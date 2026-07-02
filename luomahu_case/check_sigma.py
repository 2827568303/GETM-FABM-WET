import netCDF4 as nc
import os
import numpy as np

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'

ds = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
sigma = ds.variables['sigma'][:]
print('Sigma layers:', len(sigma))
print('Sigma values:', sigma)
print()

# Check if there are other z-like variables
for v in ds.variables:
    if 'z' in v.lower() or 'sigma' in v.lower() or 'depth' in v.lower() or 'hcc' in v.lower() or 'layer' in v.lower():
        var = ds.variables[v]
        print(f'{v}: shape={var.shape}, dims={var.dimensions}')
        if len(var.shape) == 1:
            print(f'  values: {var[:]}')

ds.close()
