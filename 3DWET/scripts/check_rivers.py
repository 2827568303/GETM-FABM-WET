"""Check river flow balance: inflow vs outflow."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')

# Check riverinfo.dat
print('=== riverinfo.dat ===')
with open(os.path.join(case_dir, 'riverinfo.dat')) as f:
    for line in f:
        print(f'  {line.rstrip()}')

# Check rivers.nc flow data
print('\n=== rivers.nc ===')
with nc.Dataset(os.path.join(case_dir, 'rivers.nc')) as ds:
    print(f'Variables: {list(ds.variables.keys())}')
    time = ds.variables['time'][:] / 86400.0
    print(f'Time: {len(time)} days, range {time[0]:.0f}-{time[-1]:.0f}')

    # Get all river variables
    for vname in ds.variables:
        if vname in ['time', 'lon', 'lat']:
            continue
        v = ds.variables[vname]
        if v.ndim >= 1:
            data = np.ma.filled(v[:], 0.0)
            if data.ndim == 1:
                # time series
                print(f'\n  {vname}: shape={data.shape}')
                print(f'    min={data.min():.2f}, max={data.max():.2f}, mean={data.mean():.2f}')
                print(f'    first 5: {data[:5]}')
                print(f'    last 5: {data[-5:]}')
                total = data.sum()
                print(f'    total volume: {total:.1f} m3 (sum over {len(data)} days)')

# Water balance summary
print('\n=== Water Balance Summary ===')
print('Need to check: inflow rivers vs outflow rivers')
print('Inflow (positive): YIHE, LUONAN, DAYUN (when inflowing)')
print('Outflow (negative): DAYUN (when outflowing), ZHANGSHAN, YANGHE')
