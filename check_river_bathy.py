import netCDF4
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

print("=== rivers.nc ===")
nc = netCDF4.Dataset('rivers.nc')
print('Variables:', list(nc.variables.keys()))
print('Dimensions:', dict(nc.dimensions))

# Check time
if 'time' in nc.variables:
    print('Time range:', nc['time'][:5], '...')
    print('Time units:', nc['time'].units)

# Check discharge for each river
for var in nc.variables:
    if 'discharge' in var.lower() or 'flow' in var.lower() or 'river' in var.lower():
        data = nc[var][:5]
        print(f'{var}: {data}')

# Check if DAYUN has negative values (inflow)
if 'DAYUN_discharge' in nc.variables:
    d = nc['DAYUN_discharge'][:]
    print(f'DAYUN discharge: min={d.min():.2f}, max={d.max():.2f}')

print("\n=== bathymetry.nc ===")
nc2 = netCDF4.Dataset('bathymetry.nc')
print('Variables:', list(nc2.variables.keys()))
print('Dims:', dict(nc2.dimensions))

h = nc2['bathymetry'][:]
print('Height shape:', h.shape)
print('Height stats: min={:.2f}, max={:.2f}'.format(h.min(), h.max()))

# Check river locations (1-indexed in riverinfo.dat -> 0-indexed for array)
river_coords = [
    (35, 5, 'DAYUN'),
    (49, 12, 'YIHE'),
    (3, 23, 'LUONAN'),
    (13, 35, 'ZHANGSHAN'),
    (26, 39, 'YANGHE')
]

print("\n=== River location depths ===")
for j, i, name in river_coords:
    # Convert to 0-indexed
    j0, i0 = j-1, i-1
    if j0 < h.shape[0] and i0 < h.shape[1]:
        depth = h[j0, i0]
        print(f'{name} at ({j},{i}) -> [{j0},{i0}]: depth={depth:.2f}m')
    else:
        print(f'{name} at ({j},{i}) -> [{j0},{i0}]: OUT OF RANGE (h shape: {h.shape})')