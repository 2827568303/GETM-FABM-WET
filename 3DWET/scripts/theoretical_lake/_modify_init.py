"""List and modify fabm_init.nc variables."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
init_path = os.path.join(CASE_DIR, 'fabm_init.nc')

# Step 1: List ALL variables
print("=== All variables in fabm_init.nc ===")
with nc.Dataset(init_path, 'r') as ds:
    print(f"Dimensions: {[(k, len(v)) for k, v in ds.dimensions.items()]}")
    print(f"Num variables: {len(ds.variables)}")
    for v in sorted(ds.variables):
        var = ds.variables[v]
        if len(var.shape) >= 1:
            data = var[:]
            if np.issubdtype(data.dtype, np.number) and data.size > 1:
                print(f"  {v}: shape={var.shape}, min={np.nanmin(data):.6f}, max={np.nanmax(data):.6f}")
            else:
                print(f"  {v}: shape={var.shape}, value={data}")
