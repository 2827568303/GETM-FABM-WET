import netCDF4 as nc
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'

print('=== 2D Variables ===')
ds = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.2d.nc'))
for v in sorted(ds.variables):
    var = ds.variables[v]
    dims = var.dimensions
    shape = var.shape
    units = var.units if hasattr(var, 'units') else '-'
    print(f'  {v}: shape={shape}, units={units}')
ds.close()
