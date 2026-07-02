import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
u = f2.variables['u'][:]
v = f2.variables['v'][:]

print('=== 最终检查 ===')
for t in [0, 120, 479]:
    e = elev[t]
    uu = u[t]
    vv = v[t]
    print(f't={t}:')
    print(f'  elev: valid={np.sum(~e.mask)}, mean={np.nanmean(e.data[~e.mask]):.4f}m')
    print(f'  u: valid={np.sum(~uu.mask)}, mean={np.nanmean(uu.data[~uu.mask]):.4f}m/s')
    print(f'  v: valid={np.sum(~vv.mask)}, mean={np.nanmean(vv.data[~vv.mask]):.4f}m/s')

f2.close()

# 检查 3D 输出
f3 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')
print('\n=== 3D 输出 ===')
print(f'sigma 层数: {f3.dimensions["sigma"].size}')
sigma = f3.variables["sigma"][:]
print(f'sigma 值: {sigma}')
temp = f3.variables['temp'][0]
print(f't=0 表层温度: valid={np.sum(~temp[0].mask)}, mean={np.nanmean(temp[0].data[~temp[0].mask]):.2f} degC')
f3.close()
