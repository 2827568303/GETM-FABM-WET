"""Check output files: dimensions, time records, data validity."""
import netCDF4 as nc
import numpy as np
import os

CASE = os.path.dirname(os.path.abspath(__file__))

for fname in ["THEORETICAL_LAKE.2d.nc", "THEORETICAL_LAKE.3d.nc", "output.nc"]:
    path = os.path.join(CASE, fname)
    if not os.path.exists(path):
        print(f"{fname}: MISSING")
        continue
    print(f"=== {fname} ({os.path.getsize(path)//1024} KB) ===")
    ds = nc.Dataset(path)
    dims = {k: len(v) for k, v in ds.dimensions.items()}
    print("  dims:", dims)
    if "time" in ds.variables:
        t = np.array(ds.variables["time"][:])
        print("  time len:", len(t))
        if len(t) > 0:
            print("  time first 3:", t[:3])
            print("  time last 3:", t[-3:])
    if "bathymetry" in ds.variables:
        bathy = np.array(ds.variables["bathymetry"][:])
        print("  bathymetry shape:", bathy.shape, "wet cells:", int(np.sum(bathy > 0)))
    if "elev" in ds.variables:
        elev = np.array(ds.variables["elev"][:])
        print("  elev shape:", elev.shape, "finite:", int(np.sum(np.isfinite(elev))))
    if "temp" in ds.variables:
        temp = np.array(ds.variables["temp"][:])
        print("  temp shape:", temp.shape, "finite:", int(np.sum(np.isfinite(temp))))
    # Check a few FABM state variables
    fabm_checks = ["diatoms_sDW", "cyanobacteria_sDW", "greens_sDW",
                   "cladocerans_sD", "copepods_sD", "macrophytes_sD",
                   "abiotic_water_sNO3W", "abiotic_water_sPO4W"]
    for v in fabm_checks:
        if v in ds.variables:
            arr = np.array(ds.variables[v][:])
            finite = int(np.sum(np.isfinite(arr)))
            print(f"  {v}: shape={arr.shape} finite={finite}")
    ds.close()
    print()
