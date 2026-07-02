"""Check water level (elev) from 2d.nc to verify water balance fix."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')
path = os.path.join(case_dir, 'LUOMAHU_WET.2d.nc')

with nc.Dataset(path) as ds:
    time = ds.variables['time'][:] / 86400.0  # days
    elev = np.ma.filled(ds.variables['elev'][:], np.nan)
    bathymetry = np.ma.filled(ds.variables['bathymetry'][:], np.nan)

    # Compute mean water level over wet cells only
    mask = bathymetry > 0
    n_wet = mask.sum()
    print(f'Wet cells: {n_wet}')
    print(f'Time records: {len(time)}')
    print(f'Time range: {time[0]:.1f} to {time[-1]:.1f} days')
    print()

    # Mean elevation over wet cells at each time
    elev_mean = np.array([np.nanmean(elev[t, mask]) for t in range(len(time))])
    # Min/max across all wet cells
    elev_min = np.array([np.nanmin(elev[t, mask]) for t in range(len(time))])
    elev_max = np.array([np.nanmax(elev[t, mask]) for t in range(len(time))])

    print('=== Water Level (elev) Statistics ===')
    print(f'{"Day":>8s} {"Mean":>10s} {"Min":>10s} {"Max":>10s} {"Delta":>10s}')
    for t in range(0, len(time), 10):
        delta = elev_mean[t] - elev_mean[0] if t > 0 else 0.0
        print(f'{time[t]:8.1f} {elev_mean[t]:10.4f} {elev_min[t]:10.4f} {elev_max[t]:10.4f} {delta:10.4f}')
    # Last record
    t = len(time) - 1
    delta = elev_mean[t] - elev_mean[0]
    print(f'{time[t]:8.1f} {elev_mean[t]:10.4f} {elev_min[t]:10.4f} {elev_max[t]:10.4f} {delta:10.4f}')

    print()
    total_delta = elev_mean[-1] - elev_mean[0]
    total_days = time[-1] - time[0]
    rate = total_delta / total_days * 1000.0  # mm/day
    print(f'Total water level change: {total_delta*1000:.1f} mm over {total_days:.0f} days')
    print(f'Rate: {rate:.2f} mm/day')
    print()

    # Check if level is stable or dropping
    if rate < -1.0:
        print('WARNING: Water level is DROPPING significantly!')
    elif rate < 0:
        print('OK: Water level slightly dropping (within evaporation range)')
    elif rate < 1.0:
        print('OK: Water level stable')
    else:
        print('OK: Water level rising (precip > evap)')
