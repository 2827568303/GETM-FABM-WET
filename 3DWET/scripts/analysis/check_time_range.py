import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\rivers.nc')
time = f.variables['time'][:]
print(f'rivers time: shape={time.shape}')
print(f'rivers time: {time[:5]} ... {time[-3:]}')
print(f'rivers time range: {time[0]/3600:.1f}h ~ {time[-1]/3600:.1f}h ({time[-1]/86400:.1f} days)')

f.close()

# 检查 meteo 的时间
f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\meteo.nc')
time = f.variables['time'][:]
print(f'\nmeteo time: shape={time.shape}')
print(f'meteo time range: {time[0]/3600:.1f}h ~ {time[-1]/3600:.1f}h ({time[-1]/86400:.1f} days)')
f.close()
