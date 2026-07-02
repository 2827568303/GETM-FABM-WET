"""Diagnose 3D temperature NaN issue."""
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'

print("=== 3D file temperature variables ===")
ds = nc.Dataset(CASE + '/THEORETICAL_LAKE.3d.nc', 'r')
all_vars = list(ds.variables)
print(f"Total vars: {len(all_vars)}")
temp_like = [v for v in all_vars if 'temp' in v.lower() or v in ['T', 'salt', 'rho', 'heatc', 't']]
print(f"Temp-like vars: {temp_like}")
for v in temp_like:
    d = ds.variables[v][:]
    print(f"  {v}: shape={d.shape}, dtype={d.dtype}, "
          f"range=[{np.nanmin(d):.4f},{np.nanmax(d):.4f}], "
          f"all_nan={np.all(np.isnan(d))}, nan_frac={np.mean(np.isnan(d)):.3f}")

# check first 30 vars
print("\nFirst 30 vars:")
for i, v in enumerate(all_vars[:30]):
    print(f"  [{i}] {v}: dims={ds.variables[v].dimensions}")
ds.close()

print("\n=== 2D file variables ===")
ds2 = nc.Dataset(CASE + '/THEORETICAL_LAKE.2d.nc', 'r')
print(f"2D vars: {list(ds2.variables)}")
ds2.close()

print("\n=== Check output.nc for temperature ===")
ds3 = nc.Dataset(CASE + '/output.nc', 'r')
temp_like3 = [v for v in ds3.variables if 'temp' in v.lower()]
print(f"output.nc temp-like vars: {temp_like3}")
for v in temp_like3[:5]:
    d = ds3.variables[v][:]
    print(f"  {v}: shape={d.shape}, range=[{np.nanmin(d):.4f},{np.nanmax(d):.4f}]")
ds3.close()
