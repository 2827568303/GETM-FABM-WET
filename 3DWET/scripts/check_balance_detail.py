"""Check water balance components for first 12 days."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')
lake_area = 1198 * 500 * 500  # m2

# 1. Meteo data (precip + evap)
print('=== Meteo (precip + evap) - first 12 days ===')
with nc.Dataset(os.path.join(case_dir, 'meteo.nc')) as ds:
    precip = ds.variables['precip'][:12, :, :].mean(axis=(1, 2))  # m/s, per day
    evap = ds.variables['evap'][:12, :, :].mean(axis=(1, 2))
    fwf = precip + evap
    for d in range(12):
        p_mm = precip[d] * 86400 * 1000
        e_mm = -evap[d] * 86400 * 1000  # positive = loss
        f_mm = fwf[d] * 86400 * 1000
        print(f'  Day {d+1}: precip={p_mm:.3f} mm/d, evap={e_mm:.3f} mm/d, fwf={f_mm:.3f} mm/d')
    total_fwf = fwf.sum() * 86400  # m
    print(f'  Total fwf: {total_fwf*1000:.1f} mm over 12 days = {total_fwf*1000/12:.2f} mm/d')

# 2. River flow
print('\n=== River flow - first 12 days ===')
with nc.Dataset(os.path.join(case_dir, 'rivers.nc')) as ds:
    yihe = np.ma.filled(ds.variables['YIHE'][:12], 0.0)
    luonan = np.ma.filled(ds.variables['LUONAN'][:12], 0.0)
    dayun = np.ma.filled(ds.variables['DAYUN'][:12], 0.0)
    zhangshan = np.ma.filled(ds.variables['ZHANGSHAN'][:12], 0.0)
    yanghe = np.ma.filled(ds.variables['YANGHE'][:12], 0.0)

    for d in range(12):
        inflow = yihe[d] + luonan[d] + max(dayun[d], 0)
        outflow = max(-dayun[d], 0) + (-zhangshan[d]) + (-yanghe[d])
        net = inflow - outflow
        # Convert m3/s to mm/day
        net_mm = net * 86400 / lake_area * 1000
        print(f'  Day {d+1}: YIHE={yihe[d]:.1f}, DAYUN={dayun[d]:.1f}, ZHANG={zhangshan[d]:.1f}, '
              f'net={net:.1f} m3/s = {net_mm:.2f} mm/d')

    total_net = (yihe + luonan + dayun - zhangshan - yanghe).sum() * 86400
    print(f'  Total river net: {total_net/lake_area*1000:.1f} mm over 12 days = {total_net/lake_area*1000/12:.2f} mm/d')

# 3. Total balance
print('\n=== Total water balance (first 12 days) ===')
river_total = (yihe + luonan + dayun - zhangshan - yanghe).sum() * 86400 / lake_area * 1000
meteo_total = fwf.sum() * 86400 * 1000
total = river_total + meteo_total
print(f'  River: {river_total:.1f} mm')
print(f'  Meteo: {meteo_total:.1f} mm')
print(f'  Total: {total:.1f} mm over 12 days = {total/12:.2f} mm/d')
print(f'  Model observed: -101.2 mm over 9 days = -11.24 mm/d')
