import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.3d.nc')

print('所有变量:')
for v in f.variables:
    var = f.variables[v]
    if len(var.dimensions) <= 3:
        print(f'  {v}: dims={var.dimensions}, shape={var.shape}')

print()
print('z (界面深度):')
if 'z' in f.variables:
    z = f.variables['z'][0, :, 2, 2]
    print(f'  {z}')

print()
print('zc (中心深度):')
if 'zc' in f.variables:
    zc = f.variables['zc'][0, :, 2, 2]
    print(f'  {zc}')

print()
print('hn (层厚度):')
if 'hn' in f.variables:
    hn = f.variables['hn'][0, :, 2, 2]
    print(f'  {hn}')

print()
print('D (总深度):')
if 'D' in f.variables:
    D = f.variables['D'][0, 2, 2]
    print(f'  {D}')

f.close()
