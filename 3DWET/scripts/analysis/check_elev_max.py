import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f.variables['elev'][:]
print(f'elev shape: {elev.shape}')

# 找到第 3 步（t=900s，15分钟）的最大值位置
t = 3
d = np.ma.filled(elev[t], np.nan)
max_val = np.nanmax(d)
max_pos = np.unravel_index(np.nanargmax(d), d.shape)
print(f't={t} (15min): max elev={max_val:.4f} m at j={max_pos[0]}, i={max_pos[1]}')

# 看看这个点周围的水位
j, i = max_pos
print(f'  周围水位:')
for dj in [-1, 0, 1]:
    for di in [-1, 0, 1]:
        jj, ii = j+dj, i+di
        if 0 <= jj < d.shape[0] and 0 <= ii < d.shape[1]:
            val = d[jj, ii]
            print(f'    j={jj}, i={ii}: {val:.4f} m')

# 河流位置
rivers = {
    'DAYUN': (5, 35),
    'YIHE': (12, 49),
    'LUONAN': (23, 3),
    'ZHANGSHAN': (35, 13),
    'YANGHE': (39, 26),
}
print()
print('河流位置的水位:')
for name, (ri, rj) in rivers.items():
    if 0 <= rj < d.shape[0] and 0 <= ri < d.shape[1]:
        print(f'  {name}: elev={d[rj, ri]:.4f} m')

f.close()
