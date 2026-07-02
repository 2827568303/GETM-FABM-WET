import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')

print('=== 垂向层信息 ===')
print('sigma:', f.variables['sigma'][:])
print('sigma shape:', f.variables['sigma'].shape)

print()
print('=== 温度垂向分布 (第100个时间步，中心网格) ===')
temp = f.variables['temp'][:]
print(f'temp shape: {temp.shape}')
print(f'temp ndim: {temp.ndim}')
print(f'temp dims: {f.variables["temp"].dimensions}')

# 找一个有数据的网格点
center_j = temp.shape[2] // 2
center_i = temp.shape[3] // 2
print(f'中心网格: j={center_j}, i={center_i}')
print(f'第100步垂向温度: {temp[100, :, center_j, center_i]}')

print()
print('=== 蓝藻叶绿素垂向分布 ===')
chla = f.variables['cyanobacteria_oChla'][:]
print(f'cyanobacteria_oChla dims: {f.variables["cyanobacteria_oChla"].dimensions}')
print(f'第100步垂向分布: {chla[100, :, center_j, center_i]}')

print()
print('=== 各层温差 ===')
for t in [0, 100, 200, 479]:
    vals = temp[t, :, center_j, center_i]
    print(f'时间步{t}: 表层={vals[0]:.4f}, 底层={vals[-1]:.4f}, 差值={vals[0]-vals[-1]:.6f}')

f.close()
