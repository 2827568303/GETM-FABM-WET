"""Check existing meteo.nc and rivers.nc structure."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ["meteo.nc", "rivers.nc", "fabm_fields.nc"]:
    fpath = os.path.join(CASE_DIR, fname)
    if not os.path.exists(fpath):
        print(f"\n{fname}: NOT FOUND")
        continue
    print("\n" + "=" * 70)
    print(f"{fname}")
    print("=" * 70)
    ds = nc.Dataset(fpath)
    print(f"Dimensions: {dict(ds.dimensions)}")
    for dname, d in ds.dimensions.items():
        print(f"  {dname}: {len(d)}{' (unlimited)' if d.isunlimited() else ''}")
    print(f"\nVariables:")
    for vname, v in ds.variables.items():
        print(f"  {vname}: {v.dimensions}, shape={v.shape}, dtype={v.dtype}")
        for attr in v.ncattrs():
            print(f"    @{attr} = {v.getncattr(attr)}")
    print(f"\nGlobal attrs:")
    for attr in ds.ncattrs():
        print(f"  @{attr} = {ds.getncattr(attr)}")
    ds.close()
