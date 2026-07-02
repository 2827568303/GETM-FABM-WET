import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
bathy = f.variables['bathymetry'][:]
ny, nx = bathy.shape
print(f'网格: nx={nx}, ny={ny}')

rivers = {
    'DAYUN': (5, 35),
    'YIHE': (12, 49),
    'LUONAN': (23, 3),
    'ZHANGSHAN': (35, 13),
    'YANGHE': (39, 26),
}

print()
print('河道位置水深:')
for name, (i, j) in rivers.items():
    if 0 <= j < ny and 0 <= i < nx:
        depth = bathy[j, i]
        print(f'  {name}: i={i}, j={j}, depth={depth:.2f}m')
    else:
        print(f'  {name}: i={i}, j={j}, 超出范围!')

# 看看北部几行的水深
print()
print('北部 j=45~53 的水深:')
for j in range(45, 54):
    row = bathy[j, :]
    valid = row[row > 0]
    if len(valid) > 0:
        print(f'  j={j}: min={valid.min():.2f}, max={valid.max():.2f}, count={len(valid)}')
    else:
        print(f'  j={j}: 全部为陆地')

f.close()
