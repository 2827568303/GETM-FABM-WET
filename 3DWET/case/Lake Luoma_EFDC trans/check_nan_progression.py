"""Check when NaN first appears in water cells."""
import netCDF4 as nc
import numpy as np

ds_b = nc.Dataset('bathymetry.nc')
H = ds_b.variables['bathymetry'][:]
ds_b.close()
water = H > 0

ds = nc.Dataset('LUOMA_EFDC_HYD.3d.nc')
t = ds.variables['time'][:] / 86400.0
n = len(t)

first_nan = -1
for i in range(n):
    uu = ds.variables['uu'][i]
    n_water_nan = np.sum(np.isnan(uu) & water)
    if i % 10 == 0 or n_water_nan > 0:
        print(f"  step {i:3d}: day {t[i]:5.1f}, water_nan={n_water_nan}")
    if n_water_nan > 0 and first_nan < 0:
        first_nan = i
        print(f"  >>> FIRST NaN at step {i} (day {t[i]:.2f})")

if first_nan < 0:
    print("No NaN in water cells found!")
else:
    print(f"\nFirst NaN at step {first_nan} (day {t[first_nan]:.2f})")

ds.close()
