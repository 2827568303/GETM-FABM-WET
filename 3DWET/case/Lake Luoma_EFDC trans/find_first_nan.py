"""Find first NaN step in both 2D and 3D output."""
import netCDF4 as nc
import numpy as np

CASE = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"

# Check 2D
ds = nc.Dataset(f"{CASE}/LUOMA_EFDC_HYD.2d.nc")
n = len(ds.variables['time'])
t = ds.variables['time'][:] / 86400.0
elev = ds.variables['elev']

lo, hi = 0, n - 1
first_nan_2d = n
while lo <= hi:
    mid = (lo + hi) // 2
    if np.isnan(elev[mid]).any():
        first_nan_2d = mid
        hi = mid - 1
    else:
        lo = mid + 1

if first_nan_2d < n:
    print(f"2D first NaN step: {first_nan_2d} (day {t[first_nan_2d]:.2f})")
else:
    print(f"2D: no NaN in {n} steps")
ds.close()

# Check 3D
ds = nc.Dataset(f"{CASE}/LUOMA_EFDC_HYD.3d.nc")
n = len(ds.variables['time'])
t = ds.variables['time'][:] / 86400.0
uu = ds.variables['uu']

lo, hi = 0, n - 1
first_nan_3d = n
while lo <= hi:
    mid = (lo + hi) // 2
    if np.isnan(uu[mid]).any():
        first_nan_3d = mid
        hi = mid - 1
    else:
        lo = mid + 1

if first_nan_3d < n:
    print(f"3D first NaN step: {first_nan_3d} (day {t[first_nan_3d]:.2f})")
else:
    print(f"3D: no NaN in {n} steps")

# Valid data range
valid_n = min(first_nan_2d, first_nan_3d)
print(f"\nValid data: steps 0 to {valid_n - 1} ({valid_n} steps)")
print(f"Valid days: {t[0]:.1f} to {t[valid_n-1]:.1f}")
ds.close()
