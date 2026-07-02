import netCDF4 as nc
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'

print('=== 3D Variables ===')
ds = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
for v in ds.variables:
    var = ds.variables[v]
    dims = var.dimensions
    shape = var.shape
    if len(dims) >= 3:
        units = var.units if hasattr(var, 'units') else '-'
        print(f'  {v}: dims={dims}, shape={shape}, units={units}')
ds.close()

print()
print('=== 2D Variables ===')
ds2 = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.2d.nc'))
for v in ds2.variables:
    var = ds2.variables[v]
    dims = var.dimensions
    shape = var.shape
    if len(dims) >= 2:
        units = var.units if hasattr(var, 'units') else '-'
        print(f'  {v}: dims={dims}, shape={shape}, units={units}')
ds2.close()
