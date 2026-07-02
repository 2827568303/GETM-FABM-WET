"""Create test file with (time, lat, lon) variable dimension order.

The Fortran netCDF 4.5.4 library REVERSES dimension order.
So if the C variable has dims (time, lat, lon), the Fortran array
will be (lon, lat, time) - which matches GETM's start/edges convention.

GETM sets:
  start(1)=1, edges(1)=iextr (lon count)
  start(2)=1, edges(2)=jextr (lat count)
  start(3)=indx, edges(3)=1  (time index)

With Fortran reversal, this maps to C dims:
  C dim 3 (lon):  start=1, count=iextr
  C dim 2 (lat):  start=1, count=jextr
  C dim 1 (time): start=indx, count=1

So the C variable should have dims (time, lat, lon).
"""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
path = os.path.join(CASE_DIR, "test_reversed.nc")

nx, ny, nt = 44, 54, 31

ds = nc.Dataset(path, "w", format="NETCDF3_CLASSIC")
ds.createDimension("lon", nx)
ds.createDimension("lat", ny)
ds.createDimension("time", nt)

lon_var = ds.createVariable("lon", "f8", ("lon",))
lon_var[:] = np.linspace(118.0, 119.0, nx)

lat_var = ds.createVariable("lat", "f8", ("lat",))
lat_var[:] = np.linspace(34.0, 34.5, ny)

time_var = ds.createVariable("time", "f8", ("time",))
time_var.units = "seconds since 2020-01-01 00:00:00"
time_var[:] = np.arange(nt) * 86400.0

# KEY: variable dims are (time, lat, lon) - NOT (lon, lat, time)
# After Fortran reversal: (lon, lat, time) - matches GETM convention
u10 = ds.createVariable("u10", "f4", ("time", "lat", "lon"))

# Data in C order: (time, lat, lon) = (nt, ny, nx)
# Fill with known pattern: value = t * 0.1 (varies by time only)
data = np.zeros((nt, ny, nx), dtype=np.float32)
for t in range(nt):
    data[t, :, :] = float(t) * 0.1
u10[:] = data

ds.close()
print(f"Created {path}")
print(f"  format: NETCDF3_CLASSIC")
print(f"  dims: lon={nx}, lat={ny}, time={nt}")
print(f"  var: u10(time, lat, lon) float32  <-- REVERDED from GETM convention")
print(f"  After Fortran reversal: (lon, lat, time) - matches GETM")
