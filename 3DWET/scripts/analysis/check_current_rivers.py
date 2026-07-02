#!/usr/bin/env python3
"""Check current river setup in luomahu_case."""
import netCDF4 as nc
import os

case_dir = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"

# Check riverinfo.dat
print("=== riverinfo.dat ===")
riverinfo_path = os.path.join(case_dir, "riverinfo.dat")
with open(riverinfo_path, 'r') as f:
    content = f.read()
    print(content)

# Check rivers.nc
print("\n=== rivers.nc ===")
rivers_path = os.path.join(case_dir, "rivers.nc")
ds = nc.Dataset(rivers_path, 'r')
print("Dimensions:", list(ds.dimensions.keys()))
for dim in ds.dimensions:
    print(f"  {dim}: {len(ds.dimensions[dim])}")

print("\nVariables:")
for var in ds.variables:
    v = ds.variables[var]
    print(f"  {var}: shape={v.shape}, dtype={v.dtype}")

# Print river names
if 'rivers' in ds.variables:
    print(f"\nRiver names: {ds.variables['rivers'][:]}")

# Print time
if 'time' in ds.variables:
    time_var = ds.variables['time']
    print(f"\nTime units: {time_var.units if hasattr(time_var, 'units') else 'N/A'}")
    print(f"Time values (first 10): {time_var[:10]}")
    print(f"Time values (last 5): {time_var[-5:]}")

# Check flow data
for varname in ['RiverFlow', 'discharge', 'flow']:
    if varname in ds.variables:
        flow = ds.variables[varname]
        print(f"\n{varname} shape: {flow.shape}")
        print(f"  First 5 time steps, all rivers:")
        for i in range(min(5, flow.shape[0])):
            print(f"    t={i}: {flow[i, :]}")

ds.close()
print("\nDone.")
