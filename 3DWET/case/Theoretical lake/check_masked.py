#!/usr/bin/env python3
"""Check if variables are masked arrays."""
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
ds = nc.Dataset(f'{CASE}/THEORETICAL_LAKE.3d.nc')

# Check temp at first time step
t = ds.variables['temp']
print(f'temp dtype: {t.dtype}')
print(f'temp shape: {t.shape}')
print(f'temp is masked: {t[0].is_masked() if hasattr(t[0], "is_masked") else "N/A"}')

arr = t[:]
print(f'arr type: {type(arr)}')
print(f'arr dtype: {arr.dtype}')
print(f'is masked array: {np.ma.isMaskedArray(arr)}')

if np.ma.isMaskedArray(arr):
    print(f'mask count: {arr.mask.sum() if arr.mask is not False else 0}')
    print(f'total elements: {arr.size}')
    filled = np.ma.filled(arr, np.nan)
    finite = np.isfinite(filled).sum()
    print(f'after fill, finite: {finite}')
    print(f'non-nan min: {np.nanmin(filled) if finite > 0 else "all nan"}')
    print(f'non-nan max: {np.nanmax(filled) if finite > 0 else "all nan"}')
    # Show first time, surface layer
    surf = filled[0, -1, :, :]
    print(f'\nSurface temp at t=0:')
    print(surf)

# Also check elev in 2d.nc
ds2 = nc.Dataset(f'{CASE}/THEORETICAL_LAKE.2d.nc')
e = ds2.variables['elev'][:]
print(f'\n2d elev type: {type(e)}')
print(f'is masked: {np.ma.isMaskedArray(e)}')
ef = np.ma.filled(e, np.nan)
print(f'elev finite: {np.isfinite(ef).sum()}')
print(f'elev t=0:')
print(ef[0])
ds2.close()

# Check bathymetry
db = nc.Dataset(f'{CASE}/bathymetry.nc')
b = db.variables['bathymetry'][:]
print(f'\nbathymetry:')
print(f'  is masked: {np.ma.isMaskedArray(b)}')
bf = np.ma.filled(b, np.nan)
print(f'  finite: {np.isfinite(bf).sum()}')
print(f'  min: {np.nanmin(bf)}, max: {np.nanmax(bf)}')
print(bf)
db.close()

ds.close()
