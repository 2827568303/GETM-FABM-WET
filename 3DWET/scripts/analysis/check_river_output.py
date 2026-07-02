import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
print('=== 2D 输出 ===')
print(f'shape: {elev.shape}')
print(f'非 mask 点数: {np.sum(~elev[0].mask)}')
if np.sum(~elev[0].mask) > 0:
    print(f't=0 值范围: {elev[0].min():.4f} ~ {elev[0].max():.4f} m')
    print(f't=last 值范围: {elev[-1].min():.4f} ~ {elev[-1].max():.4f} m')

# 检查几个时间步
for t in [0, 120, 240, 360, 479]:
    if np.sum(~elev[t].mask) > 0:
        valid = np.where(~elev[t].mask)
        print(f't={t}: mean={np.mean(elev[t]):.4f}m, max={np.max(elev[t]):.4f}m')

f2.close()

f3 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')
print('\n=== 3D 输出 ===')
print(f'sigma 层数: {f3.dimensions["sigma"].size}')
print(f'sigma 值: {f3.variables["sigma"][:]}')
temp = f3.variables['temp'][:]
print(f'temp shape: {temp.shape}')
if np.sum(~temp[0, 0].mask) > 0:
    print(f't=0 表层温度范围: {temp[0, 0].min():.2f} ~ {temp[0, 0].max():.2f} degC')
    print(f't=0 底层温度范围: {temp[0, -1].min():.2f} ~ {temp[0, -1].max():.2f} degC')
f3.close()
