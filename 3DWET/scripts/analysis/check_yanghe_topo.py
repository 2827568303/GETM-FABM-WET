import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
bathy = np.ma.filled(f.variables['bathymetry'][:], np.nan)

# 杨河位置
ri, rj = 39, 26

print(f'杨河位置 (i={ri}, j={rj}) 周围水深:')
print('     ', end='')
for di in range(-5, 6):
    print(f'{ri+di:3d}', end='')
print()
for dj in range(-5, 6):
    jj = rj + dj
    print(f'j={jj:3d}: ', end='')
    for di in range(-5, 6):
        ii = ri + di
        if 0 <= jj < bathy.shape[0] and 0 <= ii < bathy.shape[1]:
            d = bathy[jj, ii]
            if np.isfinite(d) and d > 0.5:
                print(f'{d:3.0f}', end='')
            else:
                print('  L', end='')  # L = land
        else:
            print('  X', end='')  # X = out of bounds
    print()

f.close()
