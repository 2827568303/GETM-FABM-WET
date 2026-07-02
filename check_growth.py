import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
print('time:', f.variables['time'][:])
print(f'总时间步: {len(f.dimensions["time"])}')
print()

for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    if 'time' in var.dimensions and len(var.dimensions) >= 3:
        data = var[:]
        d0 = np.ma.filled(data[0], np.nan)
        d_mid = np.ma.filled(data[len(data)//2], np.nan)
        d_last = np.ma.filled(data[-1], np.nan)
        if np.any(np.isfinite(d0)):
            max0 = np.nanmax(np.abs(d0))
            max_mid = np.nanmax(np.abs(d_mid))
            max_last = np.nanmax(np.abs(d_last))
            print(f'{v}: t0 max={max0:.4e}, t_mid max={max_mid:.4e}, t_last max={max_last:.4e}')

f.close()
