import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\output.nc')
print('=== output.nc 信息 ===')
print(f'Dimensions: {list(f.dimensions.keys())}')
for dim in f.dimensions:
    print(f'  {dim}: {f.dimensions[dim].size}')

print()
print('sigma:', f.variables['sigma'][:])

print()
print('temp shape:', f.variables['temp'].shape)
print('temp[0,:,10,10]:', f.variables['temp'][0, :, 10, 10])

print()
print('bathymetry shape:', f.variables['bathymetry'].shape)
b = f.variables['bathymetry'][:]
print(f'bathy min: {b.min()}, max: {b.max()}')
print(f'有效水深格点: {np.sum(b > 0)}')

f.close()
