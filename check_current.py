import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
print('当前 elev (无河流配置):')
print(f'  shape: {elev.shape}')
print(f'  t=0 非 mask 点: {np.sum(~elev[0].mask)}')
if np.sum(~elev[0].mask) > 0:
    valid = np.where(~elev[0].mask)
    print(f'  t=0 有值点示例 j={valid[0][0]}, i={valid[1][0]}: {elev[0][valid[0][0], valid[1][0]]:.4f}')

# 看看是不是所有时间步都是 NaN
all_nan = True
for t in range(len(elev)):
    if np.sum(~elev[t].mask) > 0:
        all_nan = False
        break
print(f'  所有时间步都是 NaN: {all_nan}')
f2.close()
