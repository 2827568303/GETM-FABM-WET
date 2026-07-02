import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')

print('=== 输出信息 ===')
print(f'时间步数: {f.dimensions["time"].size}')
print(f'垂向层数: {f.dimensions["sigma"].size}')
print(f'sigma: {f.variables["sigma"][:]}')
print(f'xc: {f.dimensions["xc"].size}')
print(f'yc: {f.dimensions["yc"].size}')

print()
print('=== 温度垂向分布（中心网格）===')
temp = f.variables['temp'][:]
cj, ci = temp.shape[2]//2, temp.shape[3]//2
print(f'中心网格: j={cj}, i={ci}')
for t in [0, 50, 100, 200, 470]:
    if t < temp.shape[0]:
        vals = temp[t, :, cj, ci]
        print(f'  时间步{t}: {vals}')

print()
print('=== 水位 ===')
elev = f.variables['elev'][:]
print(f'elev shape: {elev.shape}')
print(f'水位范围: {elev.min():.4f} ~ {elev.max():.4f} m')
print(f'第0步: {elev[0, cj, ci]:.4f} m')
print(f'最后步: {elev[-1, cj, ci]:.4f} m')

f.close()
