#!/usr/bin/env python3
"""Compare bathymetry files between Theoretical Lake and Lake Luoma."""
import netCDF4 as nc
import numpy as np

cases = {
    'Luoma': '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/bathymetry.nc',
    'Theoretical': '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake/bathymetry.nc',
}

for name, path in cases.items():
    print(f'\n{"="*60}')
    print(f'{name}: {path}')
    print(f'{"="*60}')
    ds = nc.Dataset(path)
    print(f'Variables: {list(ds.variables.keys())}')
    print(f'Dimensions: {list(ds.dimensions.keys())}')
    for v in ds.variables:
        var = ds.variables[v]
        print(f'\n  {v}: shape={var.shape}, dtype={var.dtype}')
        print(f'    attrs: {var.ncattrs()}')
        for a in var.ncattrs():
            print(f'      {a}: {var.getncattr(a)}')
        if v in ['bathymetry', 'convc']:
            data = var[:]
            if np.ma.isMaskedArray(data):
                data = np.ma.filled(data, np.nan)
            print(f'    min={np.nanmin(data)}, max={np.nanmax(data)}')
            print(f'    >0: {int((data>0).sum())}, ==0: {int((data==0).sum())}, <0: {int((data<0).sum())}')
            # Show fill value if present
            if hasattr(var, '_FillValue'):
                print(f'    _FillValue: {var._FillValue}')
            if hasattr(var, 'missing_value'):
                print(f'    missing_value: {var.missing_value}')
    ds.close()
