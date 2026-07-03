"""Check when NaN first appears in the 3D output."""
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('LUOMA_EFDC_HYD.3d.nc')
t = ds.variables['time'][:] / 86400.0
n = len(t)
print(f"Total 3D outputs: {n}")

check_steps = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, n-2]
for i in check_steps:
    if i >= n:
        continue
    temp = ds.variables['temp'][i]
    uu = ds.variables['uu'][i]
    temp_max = np.nanmax(temp) if not np.all(np.isnan(temp)) else float('nan')
    uu_max = np.nanmax(np.abs(uu)) if not np.all(np.isnan(uu)) else float('nan')
    all_nan = np.all(np.isnan(temp))
    print(f"  step {i:5d}: day {t[i]:7.1f}, temp_max={temp_max:8.3f}, uu_max={uu_max:.5f}, all_nan={all_nan}")

ds.close()
