import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
print('=== 2D 输出（0-indexed riverinfo）===')
print(f'shape: {elev.shape}')

# 检查几个时间步
for t in [0, 120, 240, 360, 479]:
    d = elev[t]
    if hasattr(d, 'mask'):
        valid = ~d.mask
        if np.sum(valid) > 0:
            vals = d.data[valid]
            print(f't={t}: valid={np.sum(valid)}, mean={np.nanmean(vals):.4f}m, max={np.nanmax(vals):.4f}m')
        else:
            print(f't={t}: no valid data')
    else:
        print(f't={t}: no mask, mean={np.nanmean(d):.4f}m')

f2.close()
