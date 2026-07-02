import netCDF4 as nc
import numpy as np

print('=== 2D 输出 ===')
f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
print(f'time size: {f2.dimensions["time"].size}')
print(f'time values: {f2.variables["time"][:]}')
if f2.dimensions["time"].size > 0:
    elev = f2.variables['elev'][:]
    print(f'elev shape: {elev.shape}')
    print(f'elev[0,27,22]: {elev[0, 27, 22]}')
f2.close()

print()
print('=== 3D 输出 ===')
f3 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')
print(f'time size: {f3.dimensions["time"].size}')
print(f'sigma: {f3.variables["sigma"][:]}')
f3.close()
