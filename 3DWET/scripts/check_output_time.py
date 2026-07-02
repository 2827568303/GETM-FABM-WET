"""Check NetCDF output file time dimension and content."""
import netCDF4 as nc
import os
import numpy as np

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ['LUOMAHU_WET.3d.nc', 'LUOMAHU_WET.2d.nc', 'output.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        print(f"{fname}: NOT FOUND")
        continue
    ds = nc.Dataset(path)
    print(f"\n=== {fname} ===")
    print(f"  Dimensions: {dict((d, len(ds.dimensions[d])) for d in ds.dimensions)}")
    if 'time' in ds.variables:
        t = ds.variables['time'][:]
        print(f"  time var: len={len(t)}")
        if len(t) > 0:
            print(f"    min={np.min(t):.1f}, max={np.max(t):.1f}")
    else:
        print(f"  time var: NOT PRESENT")
    print(f"  Variables ({len(ds.variables)}): {list(ds.variables.keys())[:10]}...")
    ds.close()
