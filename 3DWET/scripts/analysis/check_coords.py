import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')

print('=== 坐标信息 ===')
print('xc:', f.variables['xc'][:])
print('yc:', f.variables['yc'][:])

print()
print('=== lonc (经度) ===')
lonc = f.variables['lonc'][:]
print(f'shape: {lonc.shape}')
valid_lon = lonc[lonc != -999.]
if len(valid_lon) > 0:
    print(f'min: {np.min(valid_lon):.4f}')
    print(f'max: {np.max(valid_lon):.4f}')
    print(f'示例值:')
    print(lonc[0, :10])
    print(lonc[:, 0])

print()
print('=== latc (纬度) ===')
latc = f.variables['latc'][:]
valid_lat = latc[latc != -999.]
if len(valid_lat) > 0:
    print(f'min: {np.min(valid_lat):.4f}')
    print(f'max: {np.max(valid_lat):.4f}')
    print(f'示例值:')
    print(latc[0, :10])
    print(latc[:, 0])

print()
print('=== sigma (垂向层) ===')
sigma = f.variables['sigma'][:]
print(f'sigma: {sigma}')

f.close()
