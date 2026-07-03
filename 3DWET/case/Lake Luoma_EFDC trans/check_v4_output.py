"""Check v4 output: valid steps and temperature variable."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

# check 2D valid steps
ds = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.2d.nc'))
n = len(ds.variables['time'])
lo, hi = 0, n-1
first_nan = n
while lo <= hi:
    mid = (lo+hi)//2
    if np.isnan(ds.variables['elev'][mid]).any():
        first_nan = mid
        hi = mid-1
    else:
        lo = mid+1
print(f'2D steps: {n}, valid: {first_nan}, valid days: {first_nan*30*288/86400:.1f}')
ds.close()

# check 3D variables (especially temp)
ds = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
vars_list = list(ds.variables.keys())
print(f'3D variables: {vars_list}')
has_temp = 'temp' in ds.variables
print(f'Has temp: {has_temp}')
if has_temp:
    n3 = len(ds.variables['time'])
    temp_var = ds.variables['temp']
    dims = temp_var.dimensions
    print(f'temp dimensions: {dims}')
    temp0 = np.ma.filled(temp_var[0], np.nan)
    print(f'temp[0]: min={np.nanmin(temp0):.2f}, max={np.nanmax(temp0):.2f}, mean={np.nanmean(temp0):.2f}')
    mid = n3 // 2
    temp_mid = np.ma.filled(temp_var[mid], np.nan)
    print(f'temp[{mid}] (day {mid*30*288/86400:.1f}): min={np.nanmin(temp_mid):.2f}, max={np.nanmax(temp_mid):.2f}, mean={np.nanmean(temp_mid):.2f}')
    # vertical profile at center
    j_mid, i_mid = 23, 26  # lake center
    temp_profile = np.ma.filled(temp_var[mid, :, j_mid, i_mid], np.nan)
    print(f'temp vertical profile at center (j={j_mid}, i={i_mid}):')
    for k, t in enumerate(temp_profile):
        print(f'  k={k}: {t:.2f} C')
ds.close()
