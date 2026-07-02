import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
x = f.variables['x'][:]
y = f.variables['y'][:]
print(f'x: {x}')
print(f'y: {y}')
print(f'dx: {x[1] - x[0]:.1f} m')
print(f'dy: {y[1] - y[0]:.1f} m')
print(f'nx={len(x)}, ny={len(y)}')
print(f'总大小: {(x[-1]-x[0])/1000:.1f} km x {(y[-1]-y[0])/1000:.1f} km')
f.close()
