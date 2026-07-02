import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')

print('=== 基本信息 ===')
print(f'时间步数: {f.dimensions["time"].size}')
print(f'垂向层数 (sigma): {f.dimensions["sigma"].size}')
print(f'X方向: {f.dimensions["xc"].size}')
print(f'Y方向: {f.dimensions["yc"].size}')

print()
print('=== sigma 层 ===')
sigma = f.variables['sigma'][:]
print(f'sigma values: {sigma}')

print()
print('=== 变量列表（前20个）===')
vars = list(f.variables.keys())
for i, v in enumerate(vars[:30]):
    var = f.variables[v]
    dims = var.dimensions
    shape = var.shape
    print(f'  {i:2d}. {v:40s} dims={dims}, shape={shape}')

print()
print('=== 温度垂向分布 ===')
temp = f.variables['temp']
print(f'temp dimensions: {temp.dimensions}')
print(f'temp shape: {temp.shape}')

center_j = temp.shape[2] // 2
center_i = temp.shape[3] // 2
print(f'中心网格: j={center_j}, i={center_i}')

for t in [0, 10, 50, 100, 200]:
    if t < temp.shape[0]:
        vals = temp[t, :, center_j, center_i]
        valid = vals[~vals.mask] if hasattr(vals, 'mask') else vals
        print(f'  时间步{t}: 垂向分布 {vals}')

print()
print('=== 蓝藻叶绿素垂向分布 ===')
chla = f.variables['cyanobacteria_oChla']
print(f'cyanobacteria_oChla dims: {chla.dimensions}')
for t in [0, 10, 50, 100, 200]:
    if t < chla.shape[0]:
        vals = chla[t, :, center_j, center_i]
        print(f'  时间步{t}: 垂向分布 {vals}')

f.close()
