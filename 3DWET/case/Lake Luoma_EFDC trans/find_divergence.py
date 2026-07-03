"""Find exact step where NaN first appears."""
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('LUOMA_EFDC_HYD.3d.nc')
t = ds.variables['time'][:] / 86400.0
n = len(t)

# Binary search for first NaN step
lo, hi = 0, n - 1
first_nan = -1
for i in range(n):
    temp = ds.variables['temp'][i]
    if np.all(np.isnan(temp)):
        first_nan = i
        break

if first_nan >= 0:
    print(f"First all-NaN step: {first_nan} (day {t[first_nan]:.2f})")
    if first_nan > 0:
        prev = ds.variables['temp'][first_nan - 1]
        print(f"Previous step {first_nan-1} (day {t[first_nan-1]:.2f}): "
              f"temp_max={np.nanmax(prev):.3f}, uu_max={np.nanmax(np.abs(ds.variables['uu'][first_nan-1])):.5f}")

    # Check if it's really ALL NaN or just some cells
    temp_first = ds.variables['temp'][first_nan]
    n_nan = np.sum(np.isnan(temp_first))
    n_total = temp_first.size
    print(f"  NaN cells: {n_nan}/{n_total} ({100*n_nan/n_total:.1f}%)")

    # Find where NaN cells are located
    nan_mask = np.isnan(temp_first[0])  # surface layer
    if n_nan < n_total:
        nan_indices = np.argwhere(nan_mask)
        if len(nan_indices) > 0:
            print(f"  NaN locations (surface layer, first 10): {nan_indices[:10]}")
            print(f"  NaN j range: {nan_indices[:,0].min()}-{nan_indices[:,0].max()}")
            print(f"  NaN i range: {nan_indices[:,1].min()}-{nan_indices[:,1].max()}")
else:
    print("No all-NaN steps found")

ds.close()
