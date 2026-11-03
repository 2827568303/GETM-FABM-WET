"""Check fabm_init.nc structure and fix dimensions if needed."""
import netCDF4 as nc
import numpy as np
import os

CASE = os.path.dirname(os.path.abspath(__file__))
FINIT = os.path.join(CASE, "fabm_init.nc")

print("=" * 70)
print("fabm_init.nc structure")
print("=" * 70)

ds = nc.Dataset(FINIT, "r")
print(f"\nDimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}")
print(f"\nVariables ({len(ds.variables)}):")
for vname in sorted(ds.variables.keys()):
    var = ds.variables[vname]
    print(f"  {vname}: dims={var.dimensions}, shape={var.shape}, "
          f"dtype={var.dtype}")
    if hasattr(var, "_FillValue"):
        print(f"    _FillValue={var._FillValue}")
    # Print sample data for state variables
    if len(var.dimensions) >= 3 and vname not in ("lonc", "latc", "lonu", "latu", "lonv", "latv"):
        data = np.array(var[:])
        if data.size > 0:
            finite = np.sum(np.isfinite(data))
            print(f"    data: min={np.nanmin(data):.6f}, max={np.nanmax(data):.6f}, "
                  f"finite={finite}/{data.size}")
ds.close()
