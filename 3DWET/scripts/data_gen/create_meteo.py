#!/usr/bin/env python3
"""Create meteorological forcing NetCDF file for Luomahu Lake."""
import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta
import os

CASE_DIR = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"

start_date = datetime(2020, 1, 1)
end_date = datetime(2020, 12, 31)
n_days = (end_date - start_date).days + 1
n_times = n_days * 24  # hourly

time = np.arange(n_times) * 3600.0  # seconds since start

lat = 34.2
lon = 118.15

air_temp = 10 + 15 * np.sin(2 * np.pi * (np.arange(n_times) - 80*24) / 365 / 24)  # seasonal cycle
air_temp += 5 * np.sin(2 * np.pi * (np.arange(n_times) % 24 - 14) / 24)  # diurnal cycle

wind_speed = 3.0 + 2.0 * np.random.randn(n_times)
wind_speed = np.maximum(wind_speed, 0.5)

# PAR (photosynthetically active radiation) - 0 at night, peak at noon
hour_of_day = np.arange(n_times) % 24
day_of_year = np.arange(n_times) // 24
solar_elevation = np.maximum(0, np.sin(2 * np.pi * (hour_of_day - 6) / 12))  # 6am to 6pm
seasonal = 0.5 + 0.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
par = solar_elevation * seasonal * 800.0  # max ~800 W/m2

cloud = 3 + 4 * np.random.rand(n_times)
cloud = np.clip(cloud, 0, 10)

rel_hum = 70 + 10 * np.random.randn(n_times)
rel_hum = np.clip(rel_hum, 30, 100)

mslp = 1013 + 10 * np.random.randn(n_times)

outfile = os.path.join(CASE_DIR, "meteo.nc")
ds = nc.Dataset(outfile, 'w', format='NETCDF4')

ds.createDimension('time', None)
ds.createDimension('lat', 1)
ds.createDimension('lon', 1)

time_var = ds.createVariable('time', 'f8', ('time',))
time_var.units = f'seconds since {start_date.strftime("%Y-%m-%d %H:%M:%S")}'
time_var.calendar = 'standard'
time_var[:] = time

lat_var = ds.createVariable('lat', 'f4', ('lat',))
lat_var[:] = [lat]

lon_var = ds.createVariable('lon', 'f4', ('lon',))
lon_var[:] = [lon]

# Air temperature
t2m = ds.createVariable('t2m', 'f4', ('time', 'lat', 'lon'))
t2m.units = 'degrees Celsius'
t2m.long_name = 'Air temperature at 2m'
t2m[:] = air_temp.reshape(-1, 1, 1)

# Wind speed (u and v components)
u10 = ds.createVariable('u10', 'f4', ('time', 'lat', 'lon'))
u10.units = 'm s-1'
u10.long_name = 'Zonal wind at 10m'
u10[:] = wind_speed.reshape(-1, 1, 1) * 0.7

v10 = ds.createVariable('v10', 'f4', ('time', 'lat', 'lon'))
v10.units = 'm s-1'
v10.long_name = 'Meridional wind at 10m'
v10[:] = wind_speed.reshape(-1, 1, 1) * 0.3

# Relative humidity
rh = ds.createVariable('rh', 'f4', ('time', 'lat', 'lon'))
rh.units = '%'
rh.long_name = 'Relative humidity at 2m'
rh[:] = rel_hum.reshape(-1, 1, 1)

# Cloud cover
tcc = ds.createVariable('tcc', 'f4', ('time', 'lat', 'lon'))
tcc.units = 'oktas'
tcc.long_name = 'Total cloud cover'
tcc[:] = cloud.reshape(-1, 1, 1)

# Mean sea level pressure
msl = ds.createVariable('msl', 'f4', ('time', 'lat', 'lon'))
msl.units = 'hPa'
msl.long_name = 'Mean sea level pressure'
msl[:] = mslp.reshape(-1, 1, 1)

# Surface shortwave downwelling radiation (for photosynthesis)
ssrd = ds.createVariable('ssrd', 'f4', ('time', 'lat', 'lon'))
ssrd.units = 'W m-2'
ssrd.long_name = 'Surface shortwave downwelling radiation'
ssrd[:] = par.reshape(-1, 1, 1)

ds.close()

print(f"Meteo file created: {outfile}")
print(f"  Time steps: {n_times} (hourly, {n_days} days)")
print(f"  Variables: t2m, u10, v10, rh, tcc, msl, ssrd")
