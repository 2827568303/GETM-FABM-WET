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


def test_generates_three_distinct_app_valid_proxy_cases_with_hashed_attribution(tmp_path):
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
