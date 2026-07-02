import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.3d.nc')
print(f'sigma 层数: {f.dimensions["sigma"].size}')
print(f'sigma: {f.variables["sigma"][:]}')

temp = f.variables['temp'][:]
print(f'temp shape: {temp.shape}')
print(f'temp[0,:,2,2]: {temp[0, :, 2, 2]}')

f.close()
