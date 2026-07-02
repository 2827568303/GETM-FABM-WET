import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.3d.nc')

hcc = f.variables['hcc'][:]
print('hcc shape:', hcc.shape)
print('hcc[:, 2, 2]:', hcc[:, 2, 2])

sigma = f.variables['sigma'][:]
print('sigma:', sigma)

# 看看有没有其他垂向相关的变量
print()
print('所有含 z 的变量:')
for v in f.variables:
    if 'z' in v.lower() or 'lev' in v.lower() or 'lay' in v.lower():
        print(f'  {v}')

f.close()
