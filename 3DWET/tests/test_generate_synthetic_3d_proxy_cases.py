import hashlib
import importlib.util
import re
import sys
from pathlib import Path

import pytest
import numpy as np
from netCDF4 import Dataset

REPO = Path(__file__).parents[2]
SCRIPT = Path(__file__).parents[1] / "scripts" / "generate_synthetic_3d_proxy_cases.py"
APP = Path(__file__).parents[1] / "app"
sys.path.insert(0, str(APP))
import proxy_engineering

spec = importlib.util.spec_from_file_location("generate_synthetic_3d_proxy_cases", SCRIPT)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def install_geometry_sources(tmp_path, monkeypatch):
    """Stand in for the gitignored HydroLAKES extract, OSM way, and Ravn zip."""
    import zipfile

    import shapefile

    hydro = tmp_path / "HydroLAKES_Europe"
    hydro.mkdir()
    base = hydro / "HydroLAKES_Europe"
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYGON)
    writer.field("Hylak_id", "N", decimal=0)
    writer.field("Depth_avg", "F", decimal=2)
    # Irregular rings so the bounding grid keeps dry shoreline cells.
    for hylak_id, depth, origin in ((160990, 8.0, (9.50, 56.00)), (162269, 6.5, (10.20, 55.20))):
        lon, lat = origin
        # Clockwise exterior ring. Shapefile treats the opposite winding as a hole.
        ring = [
            [lon, lat],
            [lon + 0.004, lat + 0.016],
            [lon + 0.028, lat + 0.018],
            [lon + 0.03, lat + 0.002],
            [lon, lat],
        ]
        writer.poly([ring])
        writer.record(hylak_id, depth)
    writer.close()
    (hydro / "HydroLAKES_Europe.prj").write_text(
        'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]',
        encoding="utf-8")
    (hydro / "HydroLAKES_Europe.cpg").write_text("UTF-8", encoding="utf-8")
    osm = tmp_path / "bryrup_langso_osm_way_69314701.xml"
    nodes = [(1, 9.40, 56.10), (4, 9.404, 56.116), (3, 9.428, 56.118), (2, 9.43, 56.102)]
    body = ["<osm>"]
    for node_id, lon, lat in nodes:
        body.append(f'<node id="{node_id}" lon="{lon}" lat="{lat}"/>')
    body.append('<way id="69314701">')
    body.extend(f'<nd ref="{node_id}"/>' for node_id in (1, 4, 3, 2, 1))
    body.append("</way></osm>")
    osm.write_text("\n".join(body), encoding="utf-8")
    archive = tmp_path / "testcase_Lake_Ravn.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("readme.txt", "upstream ravn reference")
    monkeypatch.setattr(generator, "HYDRO_DIR", hydro)
    monkeypatch.setattr(generator, "OSM_XML", osm)
    monkeypatch.setattr(generator, "RAVN_ARCHIVE", archive)


def test_generates_three_distinct_app_valid_proxy_cases_with_hashed_attribution(tmp_path, monkeypatch):
    install_geometry_sources(tmp_path, monkeypatch)
    cases = generator.generate_proxy_cases(REPO, tmp_path / "cases")

    assert set(cases) == {"Lake Ravn", "Bryrup", "Arreskov"}
    grid_shapes = set()
    for lake, record in cases.items():
        case = Path(record["case_path"])
        manifest = __import__("json").loads((case / "proxy_engineering.json").read_text(encoding="utf-8"))
        assert manifest["target_lake"] == lake
        assert manifest["prepared"] is True
        assert manifest["validation_status"] == "not_scientifically_validated"
        assert not manifest["blockers"]
        assert proxy_engineering.validate_manifest(manifest, case).valid
        assert manifest["geometry"]["status"] == "synthetic_proxy"
        assert manifest["forcing"]["status"] == "synthetic_proxy"
        assert manifest["forcing"]["spatial_mode"] == "uniform_synthetic"
        with Dataset(case / "meteo.nc") as forcing:
            assert len(forcing.dimensions["time"]) >= 51  # include one record past the stop time for GETM EOF handling
            assert forcing.variables["rh"].units == "%"
            assert np.allclose(forcing.variables["rh"][:], 75.0)
        assert manifest["geometry"]["bathymetry_method"] == "shoreline_distance_bowl"
        assert re.search(r"(?m)^\s*sync_interval\s*:\s*([1-9]\d*(?:\.\d+)?)\s*$", (case / "output.yaml").read_text())
        timestep = float(re.search(r"(?im)^\s*timestep\s*=\s*([0-9.e+-]+)", (case / "getm.inp").read_text()).group(1))
        courant = timestep * (9.81 * manifest["geometry"]["depth_reference"]["synthetic_max_depth_m"]) ** 0.5 / manifest["geometry"]["grid_spacing_m"]
        assert courant <= 0.5
        assert manifest["numerics"]["gravity_wave_courant_estimate"] <= 0.5
        assert manifest["geometry"]["depth_reference"]["kind"] in {"coarse_attribute", "hypsograph_integral"}
        expected_license = "ODbL-1.0" if lake == "Bryrup" else "CC-BY-4.0"
        assert any(source.get("license") == expected_license for source in manifest["sources"])
        for source in manifest["sources"]:
            if source.get("role") == "missing":
                continue
            assert hashlib.sha256((case / source["path"]).read_bytes()).hexdigest() == source["sha256"]
        with Dataset(case / "bathymetry.nc") as ds:
            bathy = ds["bathymetry"][:]
            wet = np.asarray(bathy) > 0
            assert wet.any()
            assert not wet.all(), "the generated shoreline mask must retain irregular land cells"
            assert np.isfinite(np.asarray(bathy)[wet]).all()
            grid_shapes.add(bathy.shape)
    assert len(grid_shapes) == 3, "each lake must retain its own projected grid dimensions"

    arreskov = __import__("json").loads((Path(cases["Arreskov"]["case_path"]) / "proxy_engineering.json").read_text(encoding="utf-8"))
    assert any("workflow/cases/TestLake/fabm.yaml" in source.get("origin_path", "") for source in arreskov["sources"])
    assert all("lake_bryrup_denmark/fabm.yaml" not in source.get("origin_path", "") for source in arreskov["sources"])


def test_generator_refuses_to_overwrite_any_existing_target_case(tmp_path):
    root = tmp_path / "cases"
    root.mkdir()
    existing = root / generator.CASE_NAMES["Bryrup"]
    existing.mkdir()
    sentinel = existing / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError):
        generator.generate_proxy_cases(REPO, root)

    assert sentinel.read_text(encoding="utf-8") == "keep"
    assert len(list(root.iterdir())) == 1
