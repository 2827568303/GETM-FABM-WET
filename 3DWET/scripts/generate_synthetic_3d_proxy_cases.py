"""Build traceable, explicitly synthetic GETM 3D engineering cases for Ravn, Bryrup, and Arreskov."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import numpy as np
import shapefile
import yaml
from netCDF4 import Dataset
from pyproj import Transformer

CASE_NAMES = {
    "Lake Ravn": "Engineering Proxy - Lake Ravn - Synthetic 3D - 20261027",
    "Bryrup": "Engineering Proxy - Bryrup - Synthetic 3D - 20261027",
    "Arreskov": "Engineering Proxy - Arreskov - Synthetic 3D - 20261027",
}
HYDRO_DIR = Path("build/proxy-engineering-20261027/HydroLAKES_Europe")
OSM_XML = Path("build/proxy-engineering-20261027/source-downloads/bryrup_langso_osm_way_69314701.xml")
WET_ROOT = Path("3DWET/src/wet/testcases")
TESTLAKE = Path("3DWET/workflow/cases/TestLake")
HYDRO_URL = "https://www.hydrosheds.org/products/hydrolakes"
OSM_URL = "https://www.openstreetmap.org/way/69314701"
ACCESS_DATE = "2026-10-27"
HYDRO_LICENSE = "CC-BY-4.0"
OSM_LICENSE = "ODbL-1.0"
HYDRO_ATTRIBUTION = "HydroLAKES data product, HydroSHEDS, licensed under CC BY 4.0."
OSM_ATTRIBUTION = "© OpenStreetMap contributors, licensed under ODbL 1.0."
TEMPLATE_FILES = (
    "fabm.yaml", "getm.inp", "getm_fabm.inp", "gotm_fabm.yaml", "gotmturb.nml", "output.yaml",
)
WET_REFERENCE_FILES = {
    "Bryrup": ("lake_bryrup_denmark", ("fabm.yaml", "gotm.yaml", "hypsograph.dat", "inflow_chem.dat", "inflow.dat", "meteo_file.dat", "outflow.dat", "output.yaml")),
    "Arreskov": ("lake_arreskov_denmark", ("ERA5_meteo_file_arreskov.dat", "gotm.yaml", "hypsograph.dat", "inflow_chem_adj.dat", "inflow_chem_SiO2.dat", "inflow.dat", "manipulations.nml", "meteo_file.dat", "outflow.dat", "output.yaml", "README.md", "waterlevel.dat")),
}
HYDRO_IDS = {"Lake Ravn": 160990, "Arreskov": 162269}
GRID_SPACING_M = {"Lake Ravn": 100.0, "Bryrup": 50.0, "Arreskov": 125.0}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record_file(case: Path, relative: Path, *, role: str, purpose: str,
                 origin: Path | None = None, description: str = "",
                 url: str | None = None, license_name: str | None = None,
                 attribution: str | None = None) -> dict[str, Any]:
    path = case / relative
    item = {
        "path": relative.as_posix(), "bytes": path.stat().st_size,
        "sha256": _sha256(path), "role": role, "status": "copied_source" if origin else "generated_proxy",
        "purpose": purpose, "source_description": description or purpose,
    }
    if origin is not None:
        item["origin_path"] = origin.as_posix()
        item["origin_sha256"] = _sha256(origin)
    if url:
        item["url"] = url
        item["accessed_on"] = ACCESS_DATE
    if license_name:
        item["license"] = license_name
    if attribution:
        item["attribution"] = attribution
    return item


def _copy_source(repo: Path, case: Path, source: Path, dest: Path, *, purpose: str,
                 url: str | None = None, license_name: str | None = None,
                 attribution: str | None = None) -> dict[str, Any]:
    src = (repo / source).resolve()
    if not src.is_file() or src.is_symlink():
        raise FileNotFoundError(src)
    dst = case / dest
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    item = _record_file(case, dest, role="upstream_reference", purpose=purpose,
                        origin=source, url=url, license_name=license_name,
                        attribution=attribution)
    return item


def _hydrolakes_polygons(repo: Path, hylak_id: int):
    shp = repo / HYDRO_DIR / "HydroLAKES_Europe.shp"
    reader = shapefile.Reader(str(shp))
    fields = [field[0] for field in reader.fields[1:]]
    for shape_record in reader.iterShapeRecords():
        record = dict(zip(fields, shape_record.record))
        if int(record["Hylak_id"]) != hylak_id:
            continue
        geometry = shape_record.shape.__geo_interface__
        coords = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [coords]
        elif geometry["type"] == "MultiPolygon":
            polygons = coords
        else:
            raise ValueError(f"Unsupported HydroLAKES geometry type: {geometry['type']}")
        return polygons, record
    raise KeyError(f"HydroLAKES feature {hylak_id} was not found")


def _osm_polygon(repo: Path):
    path = repo / OSM_XML
    root = ET.parse(path).getroot()
    way = next((item for item in root.findall("way") if item.get("id") == "69314701"), None)
    if way is None:
        raise KeyError("OSM way 69314701 was not found in the downloaded XML")
    nodes = {node.get("id"): (float(node.get("lon")), float(node.get("lat")))
             for node in root.findall("node")}
    refs = [node.get("ref") for node in way.findall("nd")]
    if len(refs) < 4 or refs[0] != refs[-1] or any(ref not in nodes for ref in refs):
        raise ValueError("Bryrup OSM way is not a complete closed polygon")
    return [[ [nodes[ref] for ref in refs] ]], nodes, way.attrib


def _point_in_ring(x: float, y: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i, (xi, yi) in enumerate(ring):
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-300) + xi:
            inside = not inside
        j = i
    return inside


def _inside_polygons(x: float, y: float, polygons: list[list[list[tuple[float, float]]]]) -> bool:
    return any(_point_in_ring(x, y, polygon[0]) and
               not any(_point_in_ring(x, y, hole) for hole in polygon[1:])
               for polygon in polygons)


def _edge_distance(x: float, y: float, polygons: list[list[list[tuple[float, float]]]]) -> float:
    nearest = math.inf
    for polygon in polygons:
        for ring in polygon:
            for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                dx, dy = x2 - x1, y2 - y1
                denom = dx * dx + dy * dy
                t = 0.0 if denom == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / denom))
                nearest = min(nearest, math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)))
    return nearest


def _hypsograph_mean(path: Path) -> tuple[float, float]:
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    if len(rows) < 2:
        raise ValueError(f"Hypsograph has fewer than two depth/area rows: {path}")
    rows.sort()
    depth = np.asarray([row[0] for row in rows], dtype=float)
    area = np.asarray([row[1] for row in rows], dtype=float)
    if np.any(np.diff(depth) <= 0) or np.any(area <= 0):
        raise ValueError(f"Invalid depth/area sequence: {path}")
    volume = float(np.trapezoid(area, depth))
    return volume / float(area[-1]), float(depth[-1])


def _project_polygon(polygons_ll):
    all_coords = [point for polygon in polygons_ll for ring in polygon for point in ring]
    lon0 = float(np.mean([point[0] for point in all_coords]))
    lat0 = float(np.mean([point[1] for point in all_coords]))
    zone = int((lon0 + 180) // 6) + 1
    epsg = (32600 if lat0 >= 0 else 32700) + zone
    forward = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    inverse = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    projected = [[[(float(forward.transform(lon, lat)[0]), float(forward.transform(lon, lat)[1]))
                    for lon, lat in ring] for ring in polygon] for polygon in polygons_ll]
    return projected, forward, inverse, epsg


def _depth_exponent(normalized_distance: np.ndarray, target_mean: float, min_depth: float,
                    max_depth: float) -> float:
    target_fraction = (target_mean - min_depth) / (max_depth - min_depth)
    if not (0.0 < target_fraction < 1.0):
        raise ValueError("target mean depth must lie strictly between synthetic minimum and maximum")
    low, high = 0.02, 40.0
    for _ in range(80):
        middle = (low + high) / 2
        if float(np.mean(np.power(normalized_distance, middle))) > target_fraction:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _make_grid(polygons_ll, spacing_m: float, mean_depth: float, max_depth: float):
    polygons_xy, forward, inverse, epsg = _project_polygon(polygons_ll)
    xy = [point for polygon in polygons_xy for ring in polygon for point in ring]
    min_x, max_x = min(x for x, _ in xy), max(x for x, _ in xy)
    min_y, max_y = min(y for _, y in xy), max(y for _, y in xy)
    dx = dy = float(spacing_m)
    x = np.arange(math.floor(min_x / dx) * dx - dx + dx / 2,
                  math.ceil(max_x / dx) * dx + dx / 2 + dx * 0.1, dx)
    y = np.arange(math.floor(min_y / dy) * dy - dy + dy / 2,
                  math.ceil(max_y / dy) * dy + dy / 2 + dy * 0.1, dy)
    xx, yy = np.meshgrid(x, y)
    wet = np.zeros(xx.shape, dtype=bool)
    edge = np.full(xx.shape, np.nan, dtype=float)
    for j in range(len(y)):
        for i in range(len(x)):
            if _inside_polygons(float(xx[j, i]), float(yy[j, i]), polygons_xy):
                wet[j, i] = True
                edge[j, i] = _edge_distance(float(xx[j, i]), float(yy[j, i]), polygons_xy)
    if int(wet.sum()) < 4 or wet.all():
        raise ValueError(f"projected polygon produced unusable shoreline mask: shape={wet.shape}, water={int(wet.sum())}")
    max_distance = float(np.nanmax(edge))
    norm = np.clip(edge[wet] / max_distance, 1e-8, 1.0)
    min_depth = 0.5
    exponent = _depth_exponent(norm, mean_depth, min_depth, max_depth)
    depth = np.full(wet.shape, -9999.0, dtype=float)
    depth[wet] = min_depth + (max_depth - min_depth) * np.power(norm, exponent)
    lonc, latc = inverse.transform(xx, yy)
    return {"x": x, "y": y, "lonc": np.asarray(lonc), "latc": np.asarray(latc),
            "wet": wet, "bathymetry": depth, "spacing_m": spacing_m,
            "epsg": epsg, "mean_depth": float(np.mean(depth[wet])),
            "max_depth": float(np.max(depth[wet])), "wet_cells": int(wet.sum()),
            "shape": list(wet.shape)}


def _write_bathymetry(path: Path, grid: dict[str, Any]):
    ny, nx = grid["wet"].shape
    with Dataset(path, "w", format="NETCDF4_CLASSIC") as ds:
        ds.createDimension("x", nx); ds.createDimension("y", ny)
        ds.createDimension("xq", nx + 1); ds.createDimension("yq", ny + 1)
        var = ds.createVariable("grid_type", "i4")
        var.assignValue(1)
        x = ds.createVariable("x", "f8", ("x",)); x.units = "m"; x[:] = grid["x"]
        y = ds.createVariable("y", "f8", ("y",)); y.units = "m"; y[:] = grid["y"]
        lon = ds.createVariable("lonc", "f8", ("y", "x")); lon.units = "degrees_east"; lon[:] = grid["lonc"]
        lat = ds.createVariable("latc", "f8", ("y", "x")); lat.units = "degrees_north"; lat[:] = grid["latc"]
        bathy = ds.createVariable("bathymetry", "f8", ("y", "x"), fill_value=-9999.0)
        bathy.units = "m"; bathy.long_name = "water depth"; bathy.standard_name = "sea_floor_depth"
        bathy.coordinates = "lonc latc"; bathy[:] = grid["bathymetry"]
        ds.setncattr("grid_mapping", f"UTM zone EPSG:{grid['epsg']}")


def _write_meteo(path: Path, grid: dict[str, Any]):
    # Supply one guard hour beyond the configured stop to satisfy GOTM's final forcing read.
    times = np.arange(0.0, 25 * 3600 + 1, 1800.0)
    lon = np.linspace(float(np.min(grid["lonc"])), float(np.max(grid["lonc"])), grid["lonc"].shape[1])
    lat = np.linspace(float(np.min(grid["latc"])), float(np.max(grid["latc"])), grid["latc"].shape[0])
    shape = (len(times), len(lat), len(lon))
    phase = 2 * np.pi * times / (24 * 3600)
    fields = {
        "t2": (12.0 + 1.0 * np.sin(phase))[:, None, None],
        "u10": np.full(shape, 2.0), "v10": np.full(shape, 0.5),
        "slp": np.full(shape, 101325.0), "rh": np.full(shape, 75.0),
        "tcc": np.full(shape, 0.35), "precip": np.zeros(shape, dtype=np.float64),
        "evap": np.zeros(shape, dtype=np.float64),
    }
    units = {"t2": "degC", "u10": "m s-1", "v10": "m s-1", "slp": "Pa",
             "rh": "%", "tcc": "1", "precip": "m s-1", "evap": "m s-1"}
    with Dataset(path, "w", format="NETCDF4_CLASSIC") as ds:
        ds.createDimension("lon", len(lon)); ds.createDimension("lat", len(lat)); ds.createDimension("time", None)
        vlon = ds.createVariable("lon", "f8", ("lon",)); vlon.units = "degrees_east"; vlon[:] = lon
        vlat = ds.createVariable("lat", "f8", ("lat",)); vlat.units = "degrees_north"; vlat[:] = lat
        time = ds.createVariable("time", "f8", ("time",)); time.units = "seconds since 2020-01-01 00:00:00"; time.calendar = "gregorian"; time[:] = times
        for name, values in fields.items():
            dtype = "f8" if name in ("precip", "evap") else "f4"
            variable = ds.createVariable(name, dtype, ("time", "lat", "lon"))
            variable.units = units[name]
            if values.shape != shape:
                values = np.broadcast_to(values, shape)
            variable[:] = values
        ds.setncattr("source_description", "Uniform synthetic engineering forcing; not observed meteorology.")


def _write_fabm_init(path: Path, grid: dict[str, Any], template_path: Path):
    with Dataset(template_path) as source:
        source_var = source.variables.get("macrophytes_sD")
        if source_var is None:
            raise ValueError("generic TestLake fixture has no macrophytes_sD initialization field")
        source_values = np.asarray(source_var[:], dtype=float)
        wet_value = float(np.nanmean(source_values[source_values > 0]))
    ny, nx = grid["wet"].shape
    with Dataset(path, "w", format="NETCDF4_CLASSIC") as ds:
        ds.createDimension("lon", nx); ds.createDimension("lat", ny); ds.createDimension("z", 1)
        lon = ds.createVariable("lon", "f8", ("lon",)); lon[:] = np.mean(grid["lonc"], axis=0); lon.units = "degrees_east"
        lat = ds.createVariable("lat", "f8", ("lat",)); lat[:] = np.mean(grid["latc"], axis=1); lat.units = "degrees_north"
        z = ds.createVariable("z", "f8", ("z",)); z[:] = [0.0]; z.units = "m"
        state = ds.createVariable("macrophytes_sD", "f8", ("z", "lat", "lon"), fill_value=-9999.0)
        state.units = "gDW/m2"
        field = np.full((1, ny, nx), -9999.0, dtype=float)
        field[0, grid["wet"]] = wet_value
        state[:] = field
        ds.setncattr("initialization_description", "Uniform synthetic macrophyte state copied from generic TestLake fixture range onto proxy wet cells.")


def _patch_getm(template: str, lake: str, grid: dict[str, Any], runid: str) -> str:
    # Use a conservative shallow-water gravity-wave estimate on each raster.
    # This is a numerical engineering criterion, not lake-model validation.
    timestep = min(30.0, 0.49 * grid["spacing_m"] / math.sqrt(9.81 * grid["max_depth"]))
    replacements = {
        r"(?im)^(\s*runid\s*=\s*)'[^']*'": f"\\1'{runid}'",
        r"(?im)^(\s*title\s*=\s*)'[^']*'": f"\\1'{lake} synthetic 3D engineering proxy'",
        r"(?im)^(\s*start\s*=\s*)'[^']*'": r"\g<1>'2020-01-01 00:00:00'",
        r"(?im)^(\s*stop\s*=\s*)'[^']*'": r"\g<1>'2020-01-02 00:00:00'",
        r"(?im)^(\s*timestep\s*=\s*)[0-9.e+-]+": rf"\g<1>{timestep:.6f}",
        r"(?im)^(\s*maxdepth\s*=\s*)[0-9.e+-]+": rf"\g<1>{grid['max_depth'] + 1.0:.3f}",
        r"(?im)^(\s*ih\s*=\s*)\d+": rf"\g<1>{len(grid['x'])}",
        r"(?im)^(\s*jh\s*=\s*)\d+": rf"\g<1>{len(grid['y'])}",
        r"(?im)^(\s*river_method\s*=\s*)\d+": r"\g<1>0",
    }
    result = template
    for pattern, replacement in replacements.items():
        result, count = re.subn(pattern, replacement, result, count=1)
        if count != 1:
            raise ValueError(f"Expected exactly one setting match for {pattern!r}, found {count}")
    return result


def _append_generated_record(case: Path, records: list, relative: str, purpose: str,
                             description: str):
    records.append(_record_file(case, Path(relative), role="synthetic_proxy",
                                purpose=purpose, description=description))


def _source_catalog(repo: Path, case: Path, lake: str, polygons_ll):
    records = []
    depth_info = {}
    if lake in HYDRO_IDS:
        source_file = repo / HYDRO_DIR / "HydroLAKES_Europe.shp"
        _, record = _hydrolakes_polygons(repo, HYDRO_IDS[lake])
        depth_info = {"kind": "coarse_attribute", "source_dataset": "HydroLAKES Europe", "hylak_id": HYDRO_IDS[lake],
                      "mean_depth_m": float(record["Depth_avg"]), "attribute_role": "coarse reference only; not measured bathymetry"}
        hydro_files = [HYDRO_DIR / f"HydroLAKES_Europe.{ext}" for ext in ("shp", "shx", "dbf", "prj", "cpg")]
        for source in hydro_files:
            records.append(_copy_source(repo, case, source, Path("sources/hydrolakes") / source.name,
                                        purpose=f"HydroLAKES source component for {lake} geometry/depth reference",
                                        url=HYDRO_URL, license_name=HYDRO_LICENSE, attribution=HYDRO_ATTRIBUTION))
    else:
        osm = _copy_source(repo, case, OSM_XML, Path("sources/osm/bryrup_langso_osm_way_69314701.xml"),
                           purpose="OSM way 69314701 polygon source for Bryrup shoreline",
                           url=OSM_URL, license_name=OSM_LICENSE, attribution=OSM_ATTRIBUTION)
        records.append(osm)
        hypsograph = WET_ROOT / "lake_bryrup_denmark" / "hypsograph.dat"
        mean_depth, max_depth = _hypsograph_mean(repo / hypsograph)
        depth_info = {"kind": "hypsograph_integral", "source_dataset": "upstream Bryrup GOTM/WET hypsograph",
                      "mean_depth_m": mean_depth, "max_depth_m": max_depth,
                      "method": "trapezoidal integral of tabulated area versus depth divided by maximum-depth lake area; derived proxy, not measured bathymetry"}
    if lake == "Lake Ravn":
        source = Path("build/source-research-au-cases-20261027/testcase_Lake_Ravn.zip")
        records.append(_copy_source(repo, case, source, Path("sources/upstream/testcase_Lake_Ravn.zip"),
                                    purpose="upstream 1D GOTM reference; not a GETM 3D grid or forcing source"))
    else:
        directory, filenames = WET_REFERENCE_FILES[lake]
        for filename in filenames:
            source = WET_ROOT / directory / filename
            records.append(_copy_source(repo, case, source, Path("sources/upstream") / filename,
                                        purpose=f"{lake} upstream WET/GOTM reference; not used as converted 3D grid"))
    return records, depth_info


def _source_testlake_inputs(repo: Path, case: Path):
    records = []
    for name in TEMPLATE_FILES + ("fabm_init.nc",):
        src = TESTLAKE / name
        records.append(_copy_source(repo, case, src, Path("sources/testlake_template") / name,
                                    purpose="generic TestLake application integration fixture input used as a controlled synthetic engineering template"))
    return records


def _create_case(repo: Path, target: Path, lake: str):
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing proxy case: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=False, exist_ok=False)
    try:
        if lake in HYDRO_IDS:
            polygons_ll, hydro_record = _hydrolakes_polygons(repo, HYDRO_IDS[lake])
            avg_depth = float(hydro_record["Depth_avg"])
            max_depth = avg_depth * 2.0
            shoreline_source = f"HydroLAKES Europe Hylak_id {HYDRO_IDS[lake]} polygon; CC BY 4.0"
        else:
            polygons_ll, _, _ = _osm_polygon(repo)
            avg_depth, max_depth = _hypsograph_mean(repo / WET_ROOT / "lake_bryrup_denmark" / "hypsograph.dat")
            shoreline_source = "OpenStreetMap way 69314701 polygon; ODbL 1.0"
        grid = _make_grid(polygons_ll, GRID_SPACING_M[lake], avg_depth, max_depth)
        sources, depth_info = _source_catalog(repo, target, lake, polygons_ll)
        sources.extend(_source_testlake_inputs(repo, target))

        # Use the app's established generic TestLake ecology fixture as a fixed
        # controlled configuration, and record it separately from all lake sources.
        for name in TEMPLATE_FILES:
            shutil.copyfile(repo / TESTLAKE / name, target / name)
        output_path = target / "output.yaml"
        output_text, count = re.subn(r"(?im)^(\s*sync_interval\s*:\s*)[-+0-9.eE]+", r"\g<1>1", output_path.read_text(encoding="utf-8"), count=1)
        if count != 1:
            raise ValueError("TestLake output.yaml must contain exactly one sync_interval setting")
        output_path.write_text(output_text, encoding="utf-8", newline="")
        fabm_path = target / "fabm.yaml"
        fabm_text = fabm_path.read_text(encoding="utf-8")
        fabm_text = re.sub(r"(?im)(#.*)Yilong[^\r\n]*", "# fixed synthetic integration-fixture value; not target-lake observations", fabm_text)
        fabm_path.write_text(fabm_text, encoding="utf-8", newline="")
        runid = re.sub(r"[^A-Z0-9]+", "_", lake.upper()).strip("_") + "_SYNTH_PROXY"
        getm_path = target / "getm.inp"
        getm_path.write_text(_patch_getm(getm_path.read_text(encoding="utf-8"), lake, grid, runid), encoding="utf-8", newline="")
        _write_bathymetry(target / "bathymetry.nc", grid)
        _write_meteo(target / "meteo.nc", grid)
        _write_fabm_init(target / "fabm_init.nc", grid, repo / TESTLAKE / "fabm_init.nc")
        (target / "meteo_input.txt").write_text("meteo.nc\n", encoding="ascii")
        (target / "riverinfo.dat").write_text("0\n", encoding="ascii")
        with Dataset(target / "rivers.nc", "w", format="NETCDF4_CLASSIC") as ds:
            ds.createDimension("time", None)
            t = ds.createVariable("time", "f8", ("time",)); t.units = "seconds since 2020-01-01 00:00:00"; t[:] = [0.0]

        generated = {
            "fabm.yaml": "controlled generic TestLake application configuration, with target-lake-specific language removed",
            "getm.inp": "derived 24-hour GETM configuration with target dimensions and no river boundaries",
            "getm_fabm.inp": "generic TestLake GETM-FABM coupling settings",
            "gotm_fabm.yaml": "generic TestLake GOTM-FABM settings",
            "gotmturb.nml": "generic TestLake turbulence settings",
            "output.yaml": "generic TestLake output selection with sync_interval=1 to ensure output time records are written",
            "bathymetry.nc": "non-rectangular masked bowl derived from shoreline and coarse depth reference",
            "fabm_init.nc": "synthetic field mapped from generic template initial-state range onto wet cells",
            "meteo.nc": "uniform synthetic hourly meteorology across the projected grid; no observed forcing",
            "meteo_input.txt": "GETM meteorology file pointer",
            "riverinfo.dat": "explicit no-river boundary configuration",
            "rivers.nc": "minimal empty river time-series container; river_method=0",
        }
        for name, purpose in generated.items():
            origin = (TESTLAKE / name) if name in TEMPLATE_FILES else None
            role = "derived" if origin else "synthetic_proxy"
            item = _record_file(target, Path(name), role=role, purpose=purpose,
                                origin=origin, description=purpose)
            sources.append(item)

        manifest = {
            "schema_version": 1, "kind": "engineering_proxy", "target_lake": lake,
            "validation_status": "not_scientifically_validated", "prepared": True,
            "numerics": {
                "timestep_seconds": min(30.0, 0.49 * grid["spacing_m"] / math.sqrt(9.81 * grid["max_depth"])),
                "gravity_wave_courant_estimate": (min(30.0, 0.49 * grid["spacing_m"] / math.sqrt(9.81 * grid["max_depth"])) *
                                                  math.sqrt(9.81 * grid["max_depth"]) / grid["spacing_m"]),
                "method": "conservative engineering timestep bound: dt*sqrt(g*hmax)/min(dx,dy) <= 0.49; not scientific validation",
            },
            "geometry": {
                "status": "synthetic_proxy",
                "description": f"非矩形岸线掩膜来自{shoreline_source}；网格中心栅格化，水深为边界距离盆地形态代理。",
                "shoreline_source": shoreline_source, "shoreline_method": "projected polygon point-in-polygon cell-center rasterization",
                "grid_spacing_m": GRID_SPACING_M[lake], "grid_epsg": grid["epsg"],
                "grid_shape_yx": grid["shape"], "wet_cells": grid["wet_cells"],
                "approximate_raster_area_km2": grid["wet_cells"] * GRID_SPACING_M[lake] ** 2 / 1_000_000,
                "bathymetry_method": "shoreline_distance_bowl",
                "depth_reference": {**depth_info, "derived_mean_depth_m": grid["mean_depth"],
                                     "synthetic_max_depth_m": grid["max_depth"],
                                     "depth_warning": "All raster depths are synthetic engineering values; reference mean is not measured bathymetry."},
            },
            "forcing": {
                "status": "synthetic_proxy", "description": "24小时合成边界强迫：均匀风/气温/气压/湿度/云量；降水、蒸发与河流边界设为零/关闭。",
                "spatial_mode": "uniform_synthetic", "confirmed": False,
                "meteo_values": {"air_temperature_c": "12 + 1 sin(2 pi t / 24 h)", "u10_m_s": 2.0,
                                 "v10_m_s": 0.5, "sea_level_pressure_pa": 101325.0,
                                 "relative_humidity_percent": 75.0, "cloud_fraction": 0.35,
                                 "precipitation_m_s": 0.0, "evaporation_m_s": 0.0},
                "river_boundary": "disabled; river_method=0; no discharge observations or synthetic river inflow",
                "time_window": {"start": "2020-01-01 00:00:00", "stop": "2020-01-02 00:00:00", "meteo_interval_seconds": 1800,
                                "guard_forcing_record_through": "2020-01-02 01:00:00"},
            },
            "ecology_configuration": {
                "kind": "generic_controlled_test_fixture", "source": "3DWET/workflow/cases/TestLake",
                "description": "Fixed repository integration fixture used unchanged for all three targets except removal of target-specific source comments; values are synthetic controls, not lake ecology observations.",
                "target_specific_ecology": False,
                "validation_status": "not_scientifically_validated",
            },
            "source_attributions": ([
                {"source": "HydroLAKES Europe", "url": HYDRO_URL, "accessed_on": ACCESS_DATE,
                 "license": HYDRO_LICENSE, "attribution": HYDRO_ATTRIBUTION},
            ] if lake in HYDRO_IDS else [
                {"source": "OpenStreetMap way 69314701", "url": OSM_URL, "accessed_on": ACCESS_DATE,
                 "license": OSM_LICENSE, "attribution": OSM_ATTRIBUTION},
            ]),
            "sources": sources, "blockers": [],
        }
        manifest_path = target / "proxy_engineering.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return manifest
    except Exception:
        # The caller uses a fresh, explicitly named target directory. Leave the
        # failure inspectable instead of attempting broad cleanup.
        raise


def generate_proxy_cases(repo_root: Path, cases_root: Path) -> dict[str, dict[str, Any]]:
    repo, root = Path(repo_root).resolve(), Path(cases_root).resolve()
    targets = {lake: root / dirname for lake, dirname in CASE_NAMES.items()}
    existing = [str(path) for path in targets.values() if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite existing proxy case(s): " + ", ".join(existing))
    result = {}
    for lake, target in targets.items():
        manifest = _create_case(repo, target, lake)
        result[lake] = {"case_path": str(target), "prepared": manifest["prepared"],
                        "wet_cells": manifest["geometry"]["wet_cells"],
                        "grid_shape_yx": manifest["geometry"]["grid_shape_yx"],
                        "scientific_validation_status": manifest["validation_status"]}
    report = {"kind": "synthetic_3d_proxy_generation", "cases_root": str(root),
              "scientific_validation_status": "not_scientifically_validated", "cases": result}
    root.mkdir(parents=True, exist_ok=True)
    (root / "synthetic_proxy_generation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--cases-root", type=Path,
                        default=Path(r"D:\GETM-FABM-WET-outputs\cases"))
    args = parser.parse_args()
    result = generate_proxy_cases(args.repo_root, args.cases_root)
    for lake, record in result.items():
        print(f"{lake}: prepared={record['prepared']}, grid={record['grid_shape_yx']}, water_cells={record['wet_cells']}, path={record['case_path']}")
    print("All generated runs remain proxy engineering inputs; scientific validation is incomplete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
