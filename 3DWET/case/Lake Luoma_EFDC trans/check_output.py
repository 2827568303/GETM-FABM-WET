"""Quick validation of model output."""
import netCDF4 as nc
import numpy as np

CASE = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"

ds = nc.Dataset(f"{CASE}/LUOMA_EFDC_HYD.3d.nc")
t = ds.variables['time'][:] / 86400.0
n = len(t)
print(f"3D: {n} steps, days {t[0]:.1f} to {t[-1]:.1f}")
print(f"3D vars: {list(ds.variables.keys())}")

# Check uu/vv (3D velocity) at multiple time steps
uu = ds.variables['uu']
check_indices = [0, n // 4, n // 2, 3 * n // 4, n - 2, n - 1]
for idx in sorted(set(check_indices)):
    if idx < n:
        arr = uu[idx]
        n_nan = np.isnan(arr).sum()
        print(f"  step {idx} (day {t[idx]:.1f}): uu NaN={n_nan}/{arr.size}, min={np.nanmin(arr):.4f} max={np.nanmax(arr):.4f}")
ds.close()

ds = nc.Dataset(f"{CASE}/LUOMA_EFDC_HYD.2d.nc")
t2 = ds.variables['time'][:] / 86400.0
n2 = len(t2)
print(f"\n2D: {n2} steps, days {t2[0]:.1f} to {t2[-1]:.1f}")
elev = ds.variables['elev']
for idx in sorted(set([0, n2 // 4, n2 // 2, 3 * n2 // 4, n2 - 1])):
    if idx < n2:
        e = elev[idx]
        n_nan = np.isnan(e).sum()
        print(f"  step {idx} (day {t2[idx]:.1f}): elev NaN={n_nan}/{e.size}, min={np.nanmin(e):.4f} max={np.nanmax(e):.4f} mean={np.nanmean(e):.4f}")
ds.close()
