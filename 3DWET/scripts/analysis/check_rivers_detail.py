import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\rivers.nc')
print('=== rivers.nc 详细信息 ===')
for v in f.variables:
    var = f.variables[v]
    print(f'{v}:')
    print(f'  dimensions: {var.dimensions}')
    print(f'  dtype: {var.dtype}')
    print(f'  shape: {var.shape}')
    for attr in var.ncattrs():
        print(f'  {attr}: {var.getncattr(attr)}')

    data = var[:]
    if hasattr(data, 'mask'):
        print(f'  has_mask: True')
    else:
        print(f'  has_mask: False')
f.close()
