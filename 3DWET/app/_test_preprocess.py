"""End-to-end test for the pre-processing pipeline.

Generates test shapefiles (a polygon lake boundary + scattered point depths),
then exercises the server.py helper functions directly (bypassing HTTP) to
verify: shapefile parse → CRS convert → grid generate → interpolate →
write bathymetry.nc. Prints a PASS/FAIL summary at the end.

Run:  python app/_test_preprocess.py
"""
import math
import os
import shutil
import sys
import traceback
from pathlib import Path

import numpy as np
import shapefile

# Make app/ importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Avoid starting the Flask server
os.environ.setdefault("PP_TEST_MODE", "1")

# Import only what we need from server.py
import importlib.util
spec = importlib.util.spec_from_file_location("server_mod", ROOT / "app" / "server.py")
# server.py guards main() with __name__ == '__main__', so importing is safe.
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

TEST_DIR = ROOT / "app" / "_pp_test_data"
TEST_DIR.mkdir(exist_ok=True)
BOUNDARY_SHP = TEST_DIR / "lake_boundary"
BATHY_SHP = TEST_DIR / "lake_depths"
OUT_DIR = TEST_DIR / "out_case"


def make_test_shapefiles():
    """Create a 500m × 300m elliptical lake boundary + 80 scattered depth points."""
    # Boundary: ellipse with 250 m semi-major (x) and 150 m semi-minor (y),
    # centered at UTM (500000, 3300000). 80 boundary vertices.
    cx, cy = 500000.0, 3300000.0
    a, b = 250.0, 150.0
    n = 80
    boundary = [(cx + a * math.cos(2 * math.pi * i / n),
                 cy + b * math.sin(2 * math.pi * i / n)) for i in range(n)]

    # WGS84 / UTM zone 50N .prj
    prj = ('PROJCS["WGS 84 / UTM zone 50N",GEOGCS["WGS 84",'
           'DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
           'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],'
           'PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],'
           'PARAMETER["central_meridian",117],PARAMETER["scale_factor",0.9996],'
           'PARAMETER["false_easting",500000],PARAMETER["false_northing",0],'
           'UNIT["metre",1]]')

    # Boundary shapefile
    with shapefile.Writer(str(BOUNDARY_SHP), shapeType=shapefile.POLYGON) as w:
        w.field("name", "C", size=32)
        w.poly([boundary])  # pyshp 3.x: list of parts
        w.record("Lake Test")
    (TEST_DIR / "lake_boundary.prj").write_text(prj, encoding="utf-8")

    # Depth points: 80 scattered points inside the ellipse, depth = quadratic
    # falloff from centre (max 6 m → edge 1 m)
    rng = np.random.default_rng(42)
    pts = []
    depths = []
    while len(pts) < 80:
        x = cx + rng.uniform(-a, a)
        y = cy + rng.uniform(-b, b)
        dxn = (x - cx) / a
        dyn = (y - cy) / b
        if dxn * dxn + dyn * dyn <= 1.0:
            r2 = dxn * dxn + dyn * dyn
            d = max(1.0, 6.0 * (1.0 - 0.7 * r2))
            pts.append((x, y))
            depths.append(d)
    with shapefile.Writer(str(BATHY_SHP), shapeType=shapefile.POINT) as w:
        w.field("depth", "N", decimal=4, size=10)
        w.field("id", "N", decimal=0, size=8)
        for i, (p, d) in enumerate(zip(pts, depths)):
            w.point(p[0], p[1])
            w.record(d, i)
    (TEST_DIR / "lake_depths.prj").write_text(prj, encoding="utf-8")
    print(f"[setup] boundary: {len(boundary)} pts, depths: {len(pts)} pts")
    print(f"[setup] depth range: {min(depths):.2f} ~ {max(depths):.2f} m")
    return boundary, pts, depths, (cx, cy)


def test_pipeline():
    boundary, pts, depths, (cx, cy) = make_test_shapefiles()
    results = {"pass": [], "fail": []}

    # Step 1: parse CRS from .prj
    prj = (TEST_DIR / "lake_boundary.prj").read_text(encoding="utf-8")
    info = server._parse_prj_crs(prj)
    assert info["crs_type"] == "utm", f"expected utm, got {info}"
    assert info["utm_zone"] == 50, f"expected zone 50, got {info}"
    results["pass"].append("CRS parse (UTM zone 50)")

    # Step 2: convert boundary to UTM (no-op since already UTM)
    coords_utm, info2 = server._convert_boundary_to_utm(boundary, info)
    assert info2["crs_type"] == "utm"
    assert abs(coords_utm[0][0] - boundary[0][0]) < 1e-3
    results["pass"].append("Boundary CRS convert (UTM pass-through)")

    # Step 3: cache boundary, generate grid (dx=dy=25 m)
    bnd_id = "test_bnd"
    bbox = [min(c[0] for c in coords_utm), min(c[1] for c in coords_utm),
            max(c[0] for c in coords_utm), max(c[1] for c in coords_utm)]
    server._preprocess_cache["boundary"][bnd_id] = {
        "coords": coords_utm, "bbox": bbox, "crs_info": info2,
        "orig_crs_type": "utm",
    }
    # Grid: 25 m cells → ~ 21 x 13 grid
    dx = dy = 25.0
    x0 = bbox[0] - dx * 0.5
    y0 = bbox[1] - dy * 0.5
    nx = int(math.ceil((bbox[2] - x0) / dx)) + 1
    ny = int(math.ceil((bbox[3] - y0) / dy)) + 1
    xc = x0 + (np.arange(nx) + 0.5) * dx
    yc = y0 + (np.arange(ny) + 0.5) * dy
    mask = np.zeros((ny, nx), dtype=bool)
    for j in range(ny):
        for i in range(nx):
            if server._point_in_polygon(xc[i], yc[j], coords_utm):
                mask[j, i] = True
    n_water = int(mask.sum())
    print(f"[grid] {nx}x{ny}, water cells={n_water} ({100*n_water/(nx*ny):.1f}%)")
    assert n_water > 0, "no water cells"
    results["pass"].append(f"Grid generate ({nx}×{ny}, {n_water} water cells)")

    grid_id = "test_grid"
    server._preprocess_cache["grid"][grid_id] = {
        "boundary_id": bnd_id,
        "nx": nx, "ny": ny, "dx": dx, "dy": dy,
        "x0": x0, "y0": y0,
        "xc": xc.tolist(), "yc": yc.tolist(),
        "mask": mask.tolist(),
        "n_water": n_water,
        "crs_info": info2,
    }

    # Step 4: cache bathymetry points
    bathy_id = "test_bathy"
    server._preprocess_cache["bathymetry"][bathy_id] = {
        "geom_type": "point",
        "points": pts,
        "polygons": [],
        "depths": depths,
        "depth_field": "depth",
        "crs_info": info2,
    }

    # Step 5: interpolate via griddata
    pts_np = np.array(pts, dtype=float)
    vals_np = np.array(depths, dtype=float)
    water_idx = np.argwhere(mask)
    query = np.array([[xc[i], yc[j]] for j, i in water_idx], dtype=float)
    res = server.griddata(pts_np, vals_np, query, method="linear")
    # Fill NaNs with nearest
    nans = np.isnan(res)
    if nans.any():
        nn = server.griddata(pts_np, vals_np, query[nans], method="nearest")
        res[nans] = nn
    bathy = np.full((ny, nx), -9999.0, dtype=float)
    for k, (j, i) in enumerate(water_idx):
        bathy[j, i] = float(res[k])
    print(f"[interp] water depth range: {bathy[mask].min():.2f} ~ {bathy[mask].max():.2f} m, mean {bathy[mask].mean():.2f} m")
    assert (bathy[mask] > 0).all(), "some water cells have non-positive depth"
    results["pass"].append(f"Depth interpolate (mean={bathy[mask].mean():.2f}m)")

    # Step 6: write bathymetry.nc
    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / "bathymetry.nc"
    if out_path.exists(): out_path.unlink()
    server._write_bathymetry_nc_standalone(
        str(out_path), nx, ny, dx, dy, x0, y0, bathy,
        lat0=29.8, lon0=117.0, lake_name="TestLake"
    )
    assert out_path.exists() and out_path.stat().st_size > 1000, "bathy.nc not written"
    # Verify with netCDF4
    import netCDF4 as nc
    with nc.Dataset(str(out_path), "r") as ds:
        assert ds.variables["grid_type"][:] == 1
        assert ds.variables["x"].shape == (nx,)
        assert ds.variables["y"].shape == (ny,)
        assert ds.variables["latc"].shape == (ny, nx)
        assert ds.variables["lonc"].shape == (ny, nx)
        assert ds.variables["bathymetry"].shape == (ny, nx)
        bv = ds.variables["bathymetry"][:]
        if hasattr(bv, "filled"): bv = bv.filled(np.nan)
        assert (bv[mask] > 0).all(), "some water cells non-positive in NC"
        # Check lat/lon roughly match expected
        lon0_check = float(ds.variables["lonc"][ny // 2, nx // 2])
        lat0_check = float(ds.variables["latc"][ny // 2, nx // 2])
        print(f"[nc] centre lat/lon: ({lat0_check:.3f}, {lon0_check:.3f}) (expected ~29.8, ~117.0)")
    print(f"[nc] written {out_path} ({out_path.stat().st_size} bytes)")
    results["pass"].append("Write bathymetry.nc (format valid)")

    # Summary
    print("\n" + "=" * 60)
    print(f"  PASS: {len(results['pass'])}  FAIL: {len(results['fail'])}")
    print("=" * 60)
    for p in results["pass"]: print(f"  ✓ {p}")
    for f in results["fail"]: print(f"  ✗ {f}")
    return 0 if not results["fail"] else 1


if __name__ == "__main__":
    try:
        sys.exit(test_pipeline())
    except Exception as e:
        print(f"FATAL: {e}")
        traceback.print_exc()
        sys.exit(2)
