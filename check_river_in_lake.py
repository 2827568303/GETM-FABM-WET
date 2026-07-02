import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
bathy = f.variables['bathymetry'][:]
print(f'bathy shape: {bathy.shape}')

rivers_0idx = {
    'DAYUN': (5, 35),
    'YIHE': (12, 49),
    'LUONAN': (23, 3),
    'ZHANGSHAN': (35, 13),
    'YANGHE': (39, 26),
}

print('\n河流位置水深检查 (0-indexed):')
for name, (i, j) in rivers_0idx.items():
    if 0 <= i < bathy.shape[1] and 0 <= j < bathy.shape[0]:
        d = bathy[j, i]
        status = 'OK' if d > 0.5 else 'TOO SHALLOW (<0.5m)'
        print(f'  {name}: i={i}, j={j}, depth={d:.2f}m - {status}')
    else:
        print(f'  {name}: i={i}, j={j} - OUT OF BOUNDS!')

# 也检查一下 1-indexed
print('\n河流位置水深检查 (1-indexed):')
rivers_1idx = {
    'DAYUN': (6, 36),
    'YIHE': (13, 50),
    'LUONAN': (24, 4),
    'ZHANGSHAN': (36, 14),
    'YANGHE': (40, 27),
}
for name, (i, j) in rivers_1idx.items():
    ii, jj = i-1, j-1  # 转为 0-indexed
    if 0 <= ii < bathy.shape[1] and 0 <= jj < bathy.shape[0]:
        d = bathy[jj, ii]
        status = 'OK' if d > 0.5 else 'TOO SHALLOW (<0.5m)'
        print(f'  {name}: i={i}, j={j}, depth={d:.2f}m - {status}')
    else:
        print(f'  {name}: i={i}, j={j} - OUT OF BOUNDS!')

f.close()
