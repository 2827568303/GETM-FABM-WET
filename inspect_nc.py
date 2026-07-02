#!/usr/bin/env python3
"""Inspect NetCDF files for visualization."""
import netCDF4 as nc
import os

base = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case'
files = ['LUOMAHU_WET.3d.nc', 'LUOMAHU_WET.2d.nc', 'bathymetry.nc',
         'output.nc', 'rivers.nc', 'meteo.nc']

for f in files:
    path = os.path.join(base, f)
    if not os.path.exists(path):
        print(f'=== {f} === NOT FOUND')
        print()
        continue
    try:
        ds = nc.Dataset(path)
        print(f'=== {f} ===')
        dims = list(ds.dimensions.keys())
        print(f'  Dimensions: {dims}')
        vars_list = list(ds.variables.keys())
        print(f'  Num variables: {len(vars_list)}')
        print(f'  First 20 variables: {vars_list[:20]}')
        if 'time' in ds.dimensions:
            print(f'  Time steps: {len(ds.dimensions["time"])}')
        ds.close()
    except Exception as e:
        print(f'  ERROR: {e}')
    print()
