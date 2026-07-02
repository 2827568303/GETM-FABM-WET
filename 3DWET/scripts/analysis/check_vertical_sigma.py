import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')
print(f'时间步数: {f.dimensions["time"].size}')
print(f'sigma 层数: {f.dimensions["sigma"].size}')
print(f'sigma: {f.variables["sigma"][:]}')

temp = f.variables['temp'][:]
print(f'\ntemp shape: {temp.shape}')
cj, ci = temp.shape[2]//2, temp.shape[3]//2
print(f'中心网格: j={cj}, i={ci}')
print(f'第0步垂向温度: {temp[0, :, cj, ci]}')
print(f'第100步垂向温度: {temp[100, :, cj, ci]}')
print(f'最后步垂向温度: {temp[-1, :, cj, ci]}')

f.close()
