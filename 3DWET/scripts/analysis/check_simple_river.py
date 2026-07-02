import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][:]
time = f2.variables['time'][:]

print('=== 当前输出（简化河流 YIHE=10 m3/s）===')
print(f'shape: {elev.shape}')
print(f'time: {time[0]:.0f} ~ {time[-1]:.0f} ({time[-1]/3600:.1f} hours)')

for t in [0, 60, 120, 240, 360, 479]:
    d = elev[t]
    if hasattr(d, 'mask'):
        valid = ~d.mask
        if np.sum(valid) > 0:
            vals = d.data[valid]
            nan_count = np.sum(np.isnan(vals))
            print(f't={t} ({time[t]/3600:.1f}h): valid={np.sum(valid)}, NaN={nan_count}')
            if nan_count == 0:
                print(f'  mean={np.nanmean(vals):.4f}m, max={np.nanmax(vals):.4f}m')
        else:
            print(f't={t}: no valid data')
    else:
        print(f't={t}: no mask, mean={np.nanmean(d):.4f}m')

f2.close()
