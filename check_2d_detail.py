import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.2d.nc')
print('time:', f.variables['time'][:])
print()

elev = f.variables['elev'][:]
print('elev shape:', elev.shape)
print('elev[0]:', elev[0, :, :])
print('elev[1]:', elev[1, :, :])
print('elev[2]:', elev[2, :, :])

print()
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    if 'time' in var.dimensions and len(var.dimensions) >= 2:
        data = var[:]
        if len(data) >= 2:
            d0 = np.ma.filled(data[0], np.nan)
            d1 = np.ma.filled(data[1], np.nan)
            d2 = np.ma.filled(data[-1], np.nan)
            if np.any(np.isfinite(d0)) and np.any(np.isfinite(d1)):
                print(f'{v}: t=0 max={np.nanmax(d0):.4f}, t=1 max={np.nanmax(d1):.4f}, t=last max={np.nanmax(d2):.4f}')

f.close()
