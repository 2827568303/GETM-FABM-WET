"""Verify meteo.nc has correct precip/evap variables and check water balance."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')
meteo_path = os.path.join(case_dir, 'meteo.nc')

print(f'Reading: {meteo_path}')
with nc.Dataset(meteo_path) as ds:
    print(f'\nDimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}')
    print(f'Variables: {list(ds.variables.keys())}')

    for vname in ['precip', 'evap']:
        if vname in ds.variables:
            v = ds.variables[vname]
            data = v[:]
            print(f'\n{vname}:')
            print(f'  dtype: {data.dtype}')
            print(f'  shape: {data.shape}')
            print(f'  units: {v.units}')
            print(f'  min: {data.min():.10e}')
            print(f'  max: {data.max():.10e}')
            print(f'  mean: {data.mean():.10e}')
            # Show first 5 time steps at center
            ny, nx = data.shape[1], data.shape[2]
            cy, cx = ny // 2, nx // 2
            print(f'  first 5 days (center {cy},{cx}): {data[:5, cy, cx]}')
        else:
            print(f'\n{vname}: NOT FOUND!')

    # Water balance check
    if 'precip' in ds.variables and 'evap' in ds.variables:
        precip = ds.variables['precip'][:]
        evap = ds.variables['evap'][:]
        fwf = precip + evap
        n_days = len(precip)
        # Convert to mm/day for readability
        precip_mmd = precip.mean(axis=(1, 2)) * 86400.0 * 1000.0
        evap_mmd = -evap.mean(axis=(1, 2)) * 86400.0 * 1000.0  # -evap because evap<0 means loss
        fwf_mmd = fwf.mean(axis=(1, 2)) * 86400.0 * 1000.0
        print(f'\n=== Water Balance ({n_days} days) ===')
        print(f'  precip: mean={precip_mmd.mean():.3f} mm/d, total={precip_mmd.sum():.1f} mm')
        print(f'  evap:   mean={evap_mmd.mean():.3f} mm/d, total={evap_mmd.sum():.1f} mm')
        print(f'  fwf:    mean={fwf_mmd.mean():.3f} mm/d, total={fwf_mmd.sum()/1000.0:.3f} m')
        print(f'  net water level change: {fwf_mmd.sum():.1f} mm = {fwf_mmd.sum()/1000.0:.3f} m')
