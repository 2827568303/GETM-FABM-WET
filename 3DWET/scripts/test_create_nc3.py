"""Create a minimal test NC3 file with 3D variable to test Fortran reading."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
path = os.path.join(CASE_DIR, "test_nc3.nc")

nx, ny, nt = 44, 54, 31

# NETCDF3_CLASSIC with fixed time dimension (not unlimited)
ds = nc.Dataset(path, "w", format="NETCDF3_CLASSIC")
ds.createDimension("lon", nx)
ds.createDimension("lat", ny)
ds.createDimension("time", nt)  # fixed, not unlimited

lon_var = ds.createVariable("lon", "f8", ("lon",))
lon_var[:] = np.linspace(118.0, 119.0, nx)

lat_var = ds.createVariable("lat", "f8", ("lat",))
lat_var[:] = np.linspace(34.0, 34.5, ny)

time_var = ds.createVariable("time", "f8", ("time",))
time_var.units = "seconds since 2020-01-01 00:00:00"
time_var[:] = np.arange(nt) * 86400.0

# 3D variable (lon, lat, time) - float32, NO fill_value, NO chunks
u10 = ds.createVariable("u10", "f4", ("lon", "lat", "time"))
data = np.zeros((nx, ny, nt), dtype=np.float32)
for t in range(nt):
    data[:, :, t] = float(t) * 0.1
u10[:] = data

ds.close()
print(f"Created {path}")
print(f"  format: NETCDF3_CLASSIC")
print(f"  dims: lon={nx}, lat={ny}, time={nt} (fixed)")
print(f"  var: u10(lon, lat, time) float32")
