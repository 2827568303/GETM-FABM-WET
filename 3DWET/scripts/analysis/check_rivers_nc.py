import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\rivers.nc')
print('rivers.nc 维度:', list(f.dimensions.keys()))
for dim in f.dimensions:
    print(f'  {dim}: {f.dimensions[dim].size} (unlimited={f.dimensions[dim].isunlimited()})')

print()
print('变量:')
for v in f.variables:
    var = f.variables[v]
    print(f'  {v}: dims={var.dimensions}, shape={var.shape}, dtype={var.dtype}')
    data = var[:]
    if hasattr(data, 'mask'):
        print(f'    has_mask: {np.any(data.mask)}')
    if np.any(np.isnan(data)):
        print(f'    has NaN: True')
    if np.any(np.isinf(data)):
        print(f'    has Inf: True')
    print(f'    min={np.nanmin(data)}, max={np.nanmax(data)}')

f.close()
