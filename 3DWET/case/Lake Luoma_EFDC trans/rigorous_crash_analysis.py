"""Rigorous analysis: is day 387.9 crash really systematic external forcing?

Re-examine evidence:
  1. Exact crash step comparison (v3 vs v4)
  2. Meteo data at day 380-395 (wind, pressure, temperature)
  3. River flow at day 380-395
  4. Velocity field evolution before crash (v3 vs v4)
  5. Check if v3/v4 crash is truly simultaneous or just close
"""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  RIGOROUS ANALYSIS: Is day 387.9 crash systematic external forcing?")
print("=" * 70)

# 1. exact crash step comparison
print("\n[1] Exact crash step comparison (v3 vs v4):")
# v3 crash: n=1117100 (from backup_v3/run.log)
# v4 crash: n=1117100 (from run.log)
# both at n=1117100 -> day = 1117100 * 30 / 86400 = 387.88 days
n_crash = 1117100
day_crash = n_crash * 30 / 86400
print(f"  v3 crash step: n=1117100, day={day_crash:.3f}")
print(f"  v4 crash step: n=1117100, day={day_crash:.3f}")
print(f"  Exact match: YES")
print(f"  Date: 2020-01-01 + {day_crash:.1f} days = ~2021-01-23")

# 2. meteo data at day 380-395
print("\n[2] Meteo data at day 380-395:")
ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
meteo_t = ds.variables['time'][:]
# meteo time is seconds since 2020-01-01
meteo_day = meteo_t / 86400
# find indices for day 380-395
idx_start = np.searchsorted(meteo_day, 380)
idx_end = np.searchsorted(meteo_day, 395)

for v in ['u10', 'v10', 'slp', 't2', 'precip', 'evap']:
    if v not in ds.variables:
        continue
    arr = np.ma.filled(ds.variables[v][idx_start:idx_end], np.nan)
    # all spatial points are the same (single station broadcast), take [0,0]
    series = arr[:, 0, 0]
    print(f"  {v:8s} day 380-395: min={np.nanmin(series):.3f}, max={np.nanmax(series):.3f}, "
          f"mean={np.nanmean(series):.3f}")
    # check for spikes around day 387
    for d in range(385, 392):
        i = np.searchsorted(meteo_day, d)
        if i < len(series):
            print(f"    day {d}: {v}={series[i]:.3f}")
ds.close()

# 3. river flow at day 380-395
print("\n[3] River flow at day 380-395:")
ds = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
for v in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = np.ma.filled(ds.variables[v][:], 0.0)
    print(f"  {v:5s} day 385-392: {[f'{q[d]:.1f}' for d in range(385, 392)]}")
ds.close()

# 4. wind speed at day 380-395 (key for mixing)
print("\n[4] Wind speed at day 380-395:")
ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
u10 = np.ma.filled(ds.variables['u10'][idx_start:idx_end, 0, 0], np.nan)
v10 = np.ma.filled(ds.variables['v10'][idx_start:idx_end, 0, 0], np.nan)
wind_spd = np.sqrt(u10**2 + v10**2)
wind_dir = np.arctan2(v10, u10) * 180 / np.pi
print(f"  Wind speed: min={wind_spd.min():.2f}, max={wind_spd.max():.2f}, mean={wind_spd.mean():.2f} m/s")
for d in range(385, 392):
    i = np.searchsorted(meteo_day, d) - idx_start
    if 0 <= i < len(wind_spd):
        print(f"    day {d}: speed={wind_spd[i]:.2f} m/s, dir={wind_dir[i]:.0f}°")
ds.close()

# 5. velocity evolution before crash in current v4 output
print("\n[5] Velocity evolution before crash (v4 output):")
ds3 = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
n3 = len(ds3.variables['time'])
# check last 10 valid steps
for step in range(max(0, n3-10), n3):
    uu = np.ma.filled(ds3.variables['uu'][step], np.nan)
    vv = np.ma.filled(ds3.variables['vv'][step], np.nan)
    t = ds3.variables['time'][step] / 86400
    vel = np.sqrt(uu**2 + vv**2)
    print(f"  step {step} (day {t:.2f}): "
          f"max|u|={np.nanmax(np.abs(uu)):.4f}, max|v|={np.nanmax(np.abs(vv)):.4f}, "
          f"max speed={np.nanmax(vel):.4f}")
ds3.close()

# 6. check if there is a pattern: annual cycle in meteo
print("\n[6] Annual cycle check - meteo at day 22-27 (early, stable) vs day 385-390:")
ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
for v in ['u10', 'v10', 't2', 'slp']:
    arr_early = np.ma.filled(ds.variables[v][22:28, 0, 0], np.nan)
    arr_crash = np.ma.filled(ds.variables[v][385:391, 0, 0], np.nan)
    print(f"  {v:8s}: day 22-27 mean={np.nanmean(arr_early):.3f}, "
          f"day 385-390 mean={np.nanmean(arr_crash):.3f}")
ds.close()
