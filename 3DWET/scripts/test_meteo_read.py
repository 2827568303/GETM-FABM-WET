"""Simulate GETM's read_data to diagnose the NetCDF error."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
meteo_path = os.path.join(CASE_DIR, "meteo.nc")

ds = nc.Dataset(meteo_path, "r")

print("Testing GETM-style read (start=[1,1,1], count=[44,54,1]):")
print("=" * 60)

# GETM uses 1-based indexing in Fortran, but netCDF4 Python uses 0-based.
# In Fortran nf90: start=(1,1,1), edges=(44,54,1) reads var[0:44, 0:54, 0:1]
# In Python netCDF4: start=(0,0,0), count=(44,54,1)

var_names = ["u10", "v10", "slp", "t2", "rh", "tcc", "precip"]
for vname in var_names:
    var = ds.variables[vname]
    print(f"\n{vname}:")
    print(f"  dimensions: {var.dimensions}")
    print(f"  shape: {var.shape}")
    try:
        # Simulate Fortran start=(1,1,1), edges=(44,54,1)
        # Python equivalent: start=(0,0,0), count=(44,54,1)
        data = var[0:44, 0:54, 0:1]
        print(f"  read OK, shape: {data.shape}, min/max: {data.min():.4f}/{data.max():.4f}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Also try reading with explicit start/count
    try:
        data2 = var.get_value(start=(0, 0, 0), count=(44, 54, 1))
        print(f"  get_value OK, shape: {data2.shape}")
    except Exception as e:
        print(f"  get_value ERROR: {e}")

print("\n" + "=" * 60)
print("Checking variable dimension IDs:")
for vname in var_names:
    var = ds.variables[vname]
    dim_ids = var.get_dims()
    print(f"  {vname}: {[d.name for d in dim_ids]}")

ds.close()
