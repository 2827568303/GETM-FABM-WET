import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
print('无河流时 elev:')
print(f'  shape: {elev.shape}')
print(f'  t=0 非 mask 点: {np.sum(~elev[0].mask)}')
print(f'  t=0 有值点示例: {elev[0][10, 20]:.4f}')
print(f'  t=last 有值点示例: {elev[-1][10, 20]:.4f}')
f2.close()

# 对比有河流时的输出
f2r = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d_river.nc')
elev_r = f2r.variables['elev'][:]
print('\n有河流时 elev:')
print(f'  shape: {elev_r.shape}')
print(f'  t=0 非 mask 点: {np.sum(~elev_r[0].mask)}')
if np.sum(~elev_r[0].mask) > 0:
    valid = np.where(~elev_r[0].mask)
    print(f'  t=0 有值点示例: {elev_r[0][valid[0][0], valid[1][0]]:.4f}')
f2r.close()
