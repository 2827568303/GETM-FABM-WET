#!/usr/bin/env python3
"""Investigate masked array values."""
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
ds = nc.Dataset(f'{CASE}/THEORETICAL_LAKE.3d.nc')

t = ds.variables['temp']
print(f'temp _FillValue: {t._FillValue if hasattr(t, "_FillValue") else "N/A"}')
print(f'temp missing_value: {t.missing_value if hasattr(t, "missing_value") else "N/A"}')
print(f'temp attrs: {t.ncattrs()}')

arr = t[:]
print(f'\narr type: {type(arr)}')
print(f'arr shape: {arr.shape}')
print(f'mask count: {arr.mask.sum() if np.ma.isMaskedArray(arr) and arr.mask is not False else 0}')
print(f'total: {arr.size}')

# Get unmasked values
if np.ma.isMaskedArray(arr):
    unmasked = arr.compressed()
    print(f'\nunmasked values count: {len(unmasked)}')
    if len(unmasked) > 0:
        print(f'unmasked min: {unmasked.min()}')
        print(f'unmasked max: {unmasked.max()}')
        print(f'unmasked first 20: {unmasked[:20]}')
        print(f'unmasked dtype: {unmasked.dtype}')

# Check raw data without mask
raw = t[:].data
print(f'\nraw data type: {type(raw)}')
print(f'raw first values: {raw[0, -1, 10, 12]}')
print(f'raw min: {raw.min()}')
print(f'raw max: {raw.max()}')

# Try reading without mask
import netCDF4
ds2 = netCDF4.Dataset(f'{CASE}/THEORETICAL_LAKE.3d.nc', maskandscalenotused=True)
# Actually netCDF4 doesn't have that option. Let me try setting auto_mask False
ds3 = netCDF4.Dataset(f'{CASE}/THEORETICAL_LAKE.3d.nc')
ds3.set_auto_mask(False)
t3 = ds3.variables['temp'][0, -1, :, :]
print(f'\nNo auto mask, temp t=0 surface:')
print(t3)
print(f'finite: {np.isfinite(t3).sum()}')
print(f'min: {t3.min()}, max: {t3.max()}')
ds3.close()

# Check run.log for errors
print('\n=== Last 50 lines of run.log ===')
with open(f'{CASE}/run.log') as f:
    lines = f.readlines()
    for line in lines[-50:]:
        print(line.rstrip())

ds.close()
