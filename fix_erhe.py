import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

nc = netCDF4.Dataset('bathymetry.nc')
h = np.array(nc['bathymetry'][:])
lonc = nc['lonc'][:]
latc = nc['latc'][:]

# j=51 row only has water from i=9-21
print('Row 51 water range:')
j = 51
for i in range(9, 22):
    depth = h[j-1, i-1]
    lon = lonc[j-1, i-1]
    lat = latc[j-1, i-1]
    print(f'  i={i}: depth={depth:.2f}m, lon={lon:.3f}, lat={lat:.3f}')

# Use i=15 for ERHE
j, i = 51, 15
depth = h[j-1, i-1]
print(f'\nERHE at ({j},{i}): depth={depth:.2f}m')

# Actually j=51 row has land at i=15 (depth=-10)
# Let's check j=50 instead
print('\nRow 50:')
j = 50
for i in range(7, 23):
    depth = h[j-1, i-1]
    if depth > 0:
        lon = lonc[j-1, i-1]
        lat = latc[j-1, i-1]
        print(f'  i={i}: depth={depth:.2f}m, lon={lon:.3f}, lat={lat:.3f}')

# Row 50 has water at i=7-22
# Use i=15 for ERHE at row 50
j, i = 50, 15
depth = h[j-1, i-1]
lon = lonc[j-1, i-1]
lat = latc[j-1, i-1]
print(f'\nERHE corrected to ({j},{i}): depth={depth:.2f}m, lon={lon:.3f}, lat={lat:.3f}')

# Update riverinfo.dat
print('\n=== Writing corrected riverinfo.dat ===')
content = """6
35 15 DAYUN -1 -1
49 12 YIHE -1 -1
3 28 LUONAN -1 -1
13 30 ZHANGSHAN -1 -1
26 35 YANGHE -1 -1
50 15 ERHE -1 -1
"""
with open('riverinfo.dat', 'w') as f:
    f.write(content)
print('Written:')
print(content)