"""Detailed river flow balance analysis - first 213 days vs full period."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')

with nc.Dataset(os.path.join(case_dir, 'rivers.nc')) as ds:
    time = ds.variables['time'][:] / 86400.0
    yihe = np.ma.filled(ds.variables['YIHE'][:], 0.0)
    luonan = np.ma.filled(ds.variables['LUONAN'][:], 0.0)
    dayun = np.ma.filled(ds.variables['DAYUN'][:], 0.0)
    zhangshan = np.ma.filled(ds.variables['ZHANGSHAN'][:], 0.0)
    yanghe = np.ma.filled(ds.variables['YANGHE'][:], 0.0)

# Lake area
lake_area = 1198 * 500 * 500  # m2
print(f'Lake area: {lake_area/1e6:.1f} km^2')
print(f'Total days: {len(time)}')
print()

# Per-period analysis
for label, n_days in [('First 30 days', 30), ('First 90 days', 90),
                       ('First 213 days', 213), ('Full 1096 days', 1096)]:
    n = min(n_days, len(time))
    inflow = yihe[:n] + luonan[:n] + np.where(dayun[:n] > 0, dayun[:n], 0)
    outflow = np.where(dayun[:n] < 0, -dayun[:n], 0) + (-zhangshan[:n]) + (-yanghe[:n])
    net = inflow - outflow

    # Volume in m3 (flow is m3/s, multiply by 86400 s/day)
    total_in = inflow.sum() * 86400
    total_out = outflow.sum() * 86400
    total_net = net.sum() * 86400
    # Water level change (m)
    dH = total_net / lake_area

    print(f'=== {label} ===')
    print(f'  YIHE:     mean={yihe[:n].mean():.1f}, sum={yihe[:n].sum():.0f} m3/s*day')
    print(f'  LUONAN:   mean={luonan[:n].mean():.1f}, sum={luonan[:n].sum():.0f}')
    print(f'  DAYUN:    mean={dayun[:n].mean():.1f}, min={dayun[:n].min():.1f}, max={dayun[:n].max():.1f}')
    print(f'  ZHANGSHAN: mean={zhangshan[:n].mean():.1f}, min={zhangshan[:n].min():.1f}')
    print(f'  YANGHE:   mean={yanghe[:n].mean():.1f}, min={yanghe[:n].min():.1f}')
    print(f'  Total inflow:  {total_in/1e9:.3f} km3 = {total_in/lake_area:.2f} m')
    print(f'  Total outflow: {total_out/1e9:.3f} km3 = {total_out/lake_area:.2f} m')
    print(f'  Net:           {total_net/1e9:.3f} km3 = {dH:.2f} m')
    print()

# Check DAYUN flow pattern in first 30 days
print('=== DAYUN flow (first 30 days) ===')
for i in range(30):
    print(f'  Day {i+1}: DAYUN={dayun[i]:.1f}, YIHE={yihe[i]:.1f}, ZHANGSHAN={zhangshan[i]:.1f}')
