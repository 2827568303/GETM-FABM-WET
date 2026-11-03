#!/usr/bin/env python3
"""Check bathymetry file details."""
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
ds = nc.Dataset(f'{CASE}/bathymetry.nc')

print('=== Bathymetry file ===')
print('Variables:', list(ds.variables.keys()))
print('Dimensions:', list(ds.dimensions.keys()))

for v in ds.variables:
    var = ds.variables[v]
    print(f'\n{v}:')
    print(f'  shape: {var.shape}')
    print(f'  dtype: {var.dtype}')
    print(f'  attrs: {var.ncattrs()}')
    for a in var.ncattrs():
        print(f'    {a}: {var.getncattr(a)}')
    if v in ['bathymetry', 'convc']:
        data = np.ma.filled(var[:], np.nan)
        print(f'  min: {np.nanmin(data)}, max: {np.nanmax(data)}')
        print(f'  >0 count: {(data > 0).sum()}, ==0 count: {(data == 0).sum()}')
        unique = np.unique(data)
        print(f'  unique values (first 10): {unique[:10]}')

print('\n=== Global attrs ===')
for a in ds.ncattrs():
    print(f'  {a}: {ds.getncattr(a)}')

ds.close()
