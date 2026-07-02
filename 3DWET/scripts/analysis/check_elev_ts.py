import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f.variables['elev'][:]
print('每步 elev 最大值:')
for t in range(len(elev)):
    d = np.ma.filled(elev[t], np.nan)
    if np.any(np.isfinite(d)):
        max_val = np.nanmax(d)
        min_val = np.nanmin(d)
        pos = np.unravel_index(np.nanargmax(d), d.shape)
        print(f'  t={t} ({(t+1)*5}min): max={max_val:.4f}m, min={min_val:.4f}m, max_pos=j={pos[0]}, i={pos[1]}')
    else:
        print(f'  t={t}: all nan')

f.close()
