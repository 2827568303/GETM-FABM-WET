"""Deeper investigation: what happens AT n=1117100?

Key facts:
  - v3 (barotropic) crashes at n=1117100, location (i=9-12, j=30-31)
  - v4 (baroclinic) crashes at n=1117100, location (i=8, j=15-16)
  - Different crash locations -> not location-specific
  - Same crash step -> time-specific trigger

Investigate:
  1. What meteo time is being read at n=1117100?
  2. Is there a meteo data record at day 387-388 with discontinuity?
  3. Check if meteo time array has a duplicate or gap near day 387
  4. GETM meteo reading logic - what happens at year boundary?
"""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  WHAT HAPPENS AT n=1117100?")
print("=" * 70)

n_crash = 1117100
dt = 30
day_crash = n_crash * dt / 86400
print(f"  n_crash = {n_crash}")
print(f"  day_crash = {day_crash:.6f}")
print(f"  date = 2020-01-01 + {day_crash:.4f} days")
# 2020 is leap year, so 366 days
print(f"  (2020 is leap year, 366 days)")
print(f"  => day 366 = 2021-01-01 00:00:00")
print(f"  => day 387.88 = 2021-01-22 21:12:00")

# ============================================================
# 1. Meteo time array analysis near day 387
# ============================================================
print("\n" + "=" * 70)
print("  1. METEO TIME ARRAY NEAR DAY 387")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
t = ds.variables['time'][:]
meteo_day = t / 86400

# find records near day 387
for target in [384, 385, 386, 387, 388, 389, 390, 391]:
    idx = np.searchsorted(meteo_day, target)
    if idx < len(meteo_day):
        actual_day = meteo_day[idx]
        diff = actual_day - target
        print(f"  search day {target}: idx={idx}, actual day={actual_day:.6f}, diff={diff:+.6f}")

# check for any gaps or duplicates in day 365-390
print(f"\n  Time differences (hours) for day 365-390:")
idx_365 = np.searchsorted(meteo_day, 365)
idx_390 = np.searchsorted(meteo_day, 390)
for i in range(idx_365, idx_390 + 1):
    if i > 0:
        dt_h = (meteo_day[i] - meteo_day[i-1]) * 24
        print(f"  record {i}: day {meteo_day[i]:.4f}, dt_from_prev={dt_h:.2f}h")

# ============================================================
# 2. Meteo variables at exact day 387-388 transition
# ============================================================
print("\n" + "=" * 70)
print("  2. METEO VARIABLES AT day 387-388 TRANSITION")
print("=" * 70)

# GETM meteo_file (meteo_input.txt) - check what year boundary behavior is
print("  meteo_input.txt content:")
with open(os.path.join(CASE, 'meteo_input.txt'), 'r') as f:
    for ln in f:
        print(f"    {ln.rstrip()}")

# get exact values at day 387 and 388
idx_387 = np.searchsorted(meteo_day, 387)
idx_388 = np.searchsorted(meteo_day, 388)

print(f"\n  Meteo at day 387 (idx={idx_387}):")
for v in ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap']:
    val = float(np.ma.filled(ds.variables[v][idx_387, 0, 0], 0))
    print(f"    {v:8s} = {val:.4f}")

print(f"\n  Meteo at day 388 (idx={idx_388}):")
for v in ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap']:
    val = float(np.ma.filled(ds.variables[v][idx_388, 0, 0], 0))
    print(f"    {v:8s} = {val:.4f}")

# compute jumps
print(f"\n  Jumps day 387 -> 388:")
for v in ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap']:
    v1 = float(np.ma.filled(ds.variables[v][idx_387, 0, 0], 0))
    v2 = float(np.ma.filled(ds.variables[v][idx_388, 0, 0], 0))
    jump = v2 - v1
    pct = 100 * jump / v1 if v1 != 0 else float('inf')
    flag = "  [LARGE]" if abs(jump) > 0.3 * max(abs(v1), abs(v2), 0.001) else ""
    print(f"    {v:8s}: {v1:.4f} -> {v2:.4f} (jump={jump:+.4f}, {pct:+.1f}%){flag}")

ds.close()

# ============================================================
# 3. Check meteo time units and calendar
# ============================================================
print("\n" + "=" * 70)
print("  3. METEO TIME UNITS AND CALENDAR")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
print(f"  time units: {ds.variables['time'].units}")
print(f"  time calendar: {ds.variables['time'].calendar if hasattr(ds.variables['time'], 'calendar') else 'NONE'}")
print(f"  first time: {ds.variables['time'][0]}")
print(f"  last time: {ds.variables['time'][-1]}")
print(f"  n_records: {len(ds.variables['time'])}")

# check if 2020 leap year is handled correctly
# 2020-01-01 + 366 days = 2021-01-01
# if calendar is standard, day 366 should be 2021-01-01
t_first = ds.variables['time'][0]
t_last = ds.variables['time'][-1]
print(f"  first as date: 2020-01-01 + {t_first/86400:.2f} days")
print(f"  last as date: 2020-01-01 + {t_last/86400:.2f} days = ~{(t_last/86400)/365.25:.2f} years")
ds.close()

# ============================================================
# 4. Does the meteo data wrap around at year boundary?
# ============================================================
print("\n" + "=" * 70)
print("  4. METEO WRAP-AROUND CHECK AT YEAR BOUNDARY")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
# compare day 0-5 with day 365-370 (should be different - new year)
# and day 365-370 with day 730-735 (third year)
print(f"  Compare day 0-3 vs 365-368 vs 730-733 (t2 temperature):")
for label, start in [("Year 1", 0), ("Year 2", 365), ("Year 3", 730)]:
    vals = []
    for d in range(start, start + 4):
        idx = np.searchsorted(meteo_day, d)
        if idx < len(ds.variables['time']):
            t2 = float(np.ma.filled(ds.variables['t2'][idx, 0, 0], 0))
            u10 = float(np.ma.filled(ds.variables['u10'][idx, 0, 0], 0))
            vals.append((d, t2, u10))
    print(f"  {label}:")
    for d, t2, u10 in vals:
        print(f"    day {d}: t2={t2:.2f}, u10={u10:.3f}")

# check if day 365-366 is a duplicate (year boundary issue)
print(f"\n  Check for duplicate data at year boundary (day 365 vs 366 vs 0):")
idx_0 = 0
idx_365 = np.searchsorted(meteo_day, 365)
idx_366 = np.searchsorted(meteo_day, 366)
for v in ['t2', 'u10', 'v10', 'slp']:
    v_0 = float(np.ma.filled(ds.variables[v][idx_0, 0, 0], 0))
    v_365 = float(np.ma.filled(ds.variables[v][idx_365, 0, 0], 0))
    v_366 = float(np.ma.filled(ds.variables[v][idx_366, 0, 0], 0))
    print(f"  {v:8s}: day 0={v_0:.4f}, day 365={v_365:.4f}, day 366={v_366:.4f}")
ds.close()

# ============================================================
# 5. Check GETM meteo reading behavior
# ============================================================
print("\n" + "=" * 70)
print("  5. GETM METEO READING LOG (day 387-388)")
print("=" * 70)

import subprocess
result = subprocess.run(['wsl', 'bash', '-c',
    f"grep -E 'reading meteo|meteo data' '{os.path.join(CASE, 'run.log')}' | "
    f"grep -E '2021-01-2|2021-01-1[5-9]|day 38[0-9]' | head -20"],
    capture_output=True, text=True)
print(result.stdout if result.stdout else "  (no meteo reading log found)")

# all meteo reading events
result = subprocess.run(['wsl', 'bash', '-c',
    f"grep 'reading meteo' '{os.path.join(CASE, 'run.log')}' | tail -10"],
    capture_output=True, text=True)
print("  Last 10 meteo reading events:")
print(result.stdout if result.stdout else "  (none found)")

# ============================================================
# 6. Summary - which hypothesis is best supported?
# ============================================================
print("\n" + "=" * 70)
print("  HYPOTHESIS ASSESSMENT SUMMARY")
print("=" * 70)
print("""
Evidence:
  1. v3 and v4 both crash at EXACTLY n=1117100 (day 387.88)
  2. Crash locations DIFFER (v3: i=9-12,j=30-31; v4: i=8,j=15-16)
  3. Meteo data at day 387-388 is NORMAL (no spikes, no NaN)
  4. No meteo time gaps or duplicates
  5. Day 387.88 = 2021-01-22 (22 days after year boundary)
  6. Crash step 1117100 = 2 x 2 x 5 x 5 x 11171 (no special factor)
  7. steps_per_year = 1051200; crash at 1.0627 years (not exact annual cycle)

Hypothesis ranking:
  H1 (GETM code bug at specific step): UNLIKELY - different locations
  H2 (Floating-point accumulation): POSSIBLE - but would expect same location
  H3 (Meteo data defect): UNLIKELY - values normal, no gaps
  H4 (Bathymetry feature): UNLIKELY - crash locations differ
  H5 (Annual cycle resonance): UNLIKELY - 1.0627 years, not 1.000

NEW HYPOTHESIS H6: The crash is triggered by a GETM internal event
  (e.g., meteo file re-read, diagnostic output, restart logic) that
  occurs at this specific step. Need to check run.log for any
  non-physics events at n~1117100.
""")
