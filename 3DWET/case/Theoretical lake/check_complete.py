#!/usr/bin/env python3
"""Check model output completeness after run."""
import netCDF4 as nc
import numpy as np
import os

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'

for f in ['THEORETICAL_LAKE.2d.nc', 'THEORETICAL_LAKE.3d.nc', 'output.nc']:
    p = os.path.join(CASE, f)
    if not os.path.exists(p):
        print(f'{f}: MISSING')
        continue
    sz = os.path.getsize(p) / (1024*1024)
    ds = nc.Dataset(p)
    t = ds.variables.get('time')
    n = len(t) if t is not None else 0
    print(f'\n=== {f} ({sz:.1f} MB) ===')
    print(f'  time dim = {n}')
    if n > 0:
        vals = np.array(t[:])
        valid = vals[vals > 0]
        print(f'  valid records = {len(valid)}')
        if len(valid) > 0:
            print(f'  first = {valid[0]/86400:.3f} days, last = {valid[-1]/86400:.3f} days')
    # Check key variables
    for v in ['elev', 'temp', 'uu', 'vv', 'w']:
        if v in ds.variables:
            arr = ds.variables[v][:]
            finite = np.isfinite(arr).sum() if arr.size > 0 else 0
            print(f'  {v}: shape={arr.shape}, finite={finite}')
    # Check FABM vars
    fabm_vars = ['diatoms_sDW', 'cyanobacteria_sDW', 'greens_sDW',
                 'cladocerans_sD', 'copepods_sD', 'macrophytes_sD',
                 'abiotic_water_sNO3W', 'abiotic_water_sPO4W',
                 'abiotic_water_sNH4W', 'abiotic_water_sO2W',
                 'POM_sDW', 'DOM_sDW', 'humus_sDS']
    for v in fabm_vars:
        if v in ds.variables:
            arr = ds.variables[v][:]
            finite = np.isfinite(arr).sum() if arr.size > 0 else 0
            vmin = np.nanmin(arr) if finite > 0 else None
            vmax = np.nanmax(arr) if finite > 0 else None
            print(f'  {v}: shape={arr.shape}, finite={finite}, range=[{vmin}, {vmax}]')
    ds.close()
