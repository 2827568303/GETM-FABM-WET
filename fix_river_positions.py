import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

nc = netCDF4.Dataset('bathymetry.nc')
h = np.array(nc['bathymetry'][:])
lonc = nc['lonc'][:]
latc = nc['latc'][:]

print('=== Correcting river positions ===')
print('Original riverinfo.dat coordinates:')
print('  DAYUN: (35,5) -> land')
print('  YIHE: (49,12) -> water (depth=3.0m) - OK')
print('  LUONAN: (3,23) -> land')
print('  ZHANGSHAN: (13,35) -> water edge')
print('  YANGHE: (26,39) -> water (depth=10.0m) - OK')
print()

# Find correct positions
# DAYUN: j=35 row, water from i=6-30. Use i=15 (deep in lake)
j, i = 35, 15
depth = h[j-1, i-1]
print(f'DAYUN: ({j},{i}) -> depth={depth:.2f}m at water cell')

# YIHE: j=49 row, water from i=7-22
j, i = 49, 12
depth = h[j-1, i-1]
print(f'YIHE: ({j},{i}) -> depth={depth:.2f}m - already correct')

# LUONAN: j=3 row, water from i=26-31
j, i = 3, 28
depth = h[j-1, i-1]
print(f'LUONAN: ({j},{i}) -> depth={depth:.2f}m at water cell')

# ZHANGSHAN: j=13 row, water from i=9-35
j, i = 13, 30
depth = h[j-1, i-1]
print(f'ZHANGSHAN: ({j},{i}) -> depth={depth:.2f}m')

# YANGHE: j=26 row, water from i=7-41
j, i = 26, 35
depth = h[j-1, i-1]
print(f'YANGHE: ({j},{i}) -> depth={depth:.2f}m - already reasonable')

# ERHE: j=51 row, water from i=9-21. Use i=15
j, i = 51, 15
depth = h[j-1, i-1]
print(f'ERHE: ({j},{i}) -> depth={depth:.2f}m')

# Now get the lon/lat for each position
print('\n=== Longitude/Latitude at new positions ===')
for name, j, i in [
    ('DAYUN', 35, 15),
    ('YIHE', 49, 12),
    ('LUONAN', 3, 28),
    ('ZHANGSHAN', 13, 30),
    ('YANGHE', 26, 35),
    ('ERHE', 51, 15)
]:
    lon = lonc[j-1, i-1]
    lat = latc[j-1, i-1]
    print(f'{name} ({j},{i}): lon={lon:.3f}°E, lat={lat:.3f}°N')

# Update riverinfo.dat
print('\n=== Writing corrected riverinfo.dat ===')
content = """6
35 15 DAYUN -1 -1
49 12 YIHE -1 -1
3 28 LUONAN -1 -1
13 30 ZHANGSHAN -1 -1
26 35 YANGHE -1 -1
51 15 ERHE -1 -1
"""
with open('riverinfo.dat', 'w') as f:
    f.write(content)
print('Written 6 rivers with corrected positions')
print(content)