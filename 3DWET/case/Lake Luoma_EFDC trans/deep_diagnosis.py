"""Deep diagnosis: locate the true root cause of day 387.9 crash.

Investigates 5 hypotheses with concrete evidence:
  H1. GETM code-level issue at specific step (test with different timestep)
  H2. Floating-point error accumulation
  H3. Meteo data defect at day 387 (per-timestep inspection)
  H4. Hidden bathymetry feature at crash region
  H5. Sigma coordinate resonance with annual cycle
"""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  DEEP ROOT CAUSE DIAGNOSIS")
print("=" * 70)

# ============================================================
# H3. Meteo data per-timestep inspection at day 385-390
# ============================================================
print("\n" + "=" * 70)
print("  H3. METEO DATA PER-TIMESTEP AT DAY 385-390")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
meteo_t = ds.variables['time'][:]
meteo_day = meteo_t / 86400

# find exact indices for day 385-390
idx_385 = np.searchsorted(meteo_day, 385)
idx_391 = np.searchsorted(meteo_day, 391)
print(f"  Meteo records day 385-391: indices {idx_385} to {idx_391-1}")
print(f"  Total records in this range: {idx_391 - idx_385}")

# check for jumps/discontinuities in each variable
print(f"\n  Per-timestep values at day 385-391 (station values):")
print(f"  {'day':>6s} {'u10':>8s} {'v10':>8s} {'spd':>8s} {'slp':>10s} {'t2':>7s} {'rh':>6s} {'tcc':>6s}")
prev_spd = None
for i in range(idx_385, idx_391):
    u = float(np.ma.filled(ds.variables['u10'][i, 0, 0], 0))
    v = float(np.ma.filled(ds.variables['v10'][i, 0, 0], 0))
    spd = np.sqrt(u*u + v*v)
    slp = float(np.ma.filled(ds.variables['slp'][i, 0, 0], 0))
    t2 = float(np.ma.filled(ds.variables['t2'][i, 0, 0], 0))
    rh = float(np.ma.filled(ds.variables['rh'][i, 0, 0], 0))
    tcc = float(np.ma.filled(ds.variables['tcc'][i, 0, 0], 0))
    day = meteo_day[i]
    # check for jumps
    jump = ""
    if prev_spd is not None and abs(spd - prev_spd) > 3:
        jump = f"  [JUMP {spd-prev_spd:+.2f}]"
    print(f"  {day:6.2f} {u:8.3f} {v:8.3f} {spd:8.3f} {slp:10.2f} {t2:7.2f} {rh:6.3f} {tcc:6.3f}{jump}")
    prev_spd = spd

# also check day 0-5 for baseline comparison
print(f"\n  Baseline (day 0-5) for comparison:")
print(f"  {'day':>6s} {'u10':>8s} {'v10':>8s} {'spd':>8s} {'slp':>10s} {'t2':>7s} {'rh':>6s} {'tcc':>6s}")
for i in range(0, 5):
    u = float(np.ma.filled(ds.variables['u10'][i, 0, 0], 0))
    v = float(np.ma.filled(ds.variables['v10'][i, 0, 0], 0))
    spd = np.sqrt(u*u + v*v)
    slp = float(np.ma.filled(ds.variables['slp'][i, 0, 0], 0))
    t2 = float(np.ma.filled(ds.variables['t2'][i, 0, 0], 0))
    rh = float(np.ma.filled(ds.variables['rh'][i, 0, 0], 0))
    tcc = float(np.ma.filled(ds.variables['tcc'][i, 0, 0], 0))
    print(f"  {meteo_day[i]:6.2f} {u:8.3f} {v:8.3f} {spd:8.3f} {slp:10.2f} {t2:7.2f} {rh:6.3f} {tcc:6.3f}")
ds.close()

# ============================================================
# H3b. Check meteo data integrity - any NaN, gaps, duplicates?
# ============================================================
print("\n" + "=" * 70)
print("  H3b. METEO DATA INTEGRITY CHECK")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
n_meteo = len(ds.variables['time'])
print(f"  Total meteo records: {n_meteo}")
print(f"  Expected (3 years): {365*3} = 1095")

# check time array for gaps/duplicates
t = ds.variables['time'][:]
dt = np.diff(t)
print(f"  Time step: min={dt.min()/3600:.2f}h, max={dt.max()/3600:.2f}h, mean={dt.mean()/3600:.2f}h")
print(f"  Expected: 24.00h (daily)")

# check for NaN in any variable at day 385-391
for v in ['u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap']:
    arr = ds.variables[v][idx_385:idx_391]
    n_nan = np.isnan(np.ma.filled(arr, np.nan)).sum()
    n_zero = (np.ma.filled(arr, 0) == 0).sum()
    print(f"  {v:8s} day 385-391: NaN={n_nan}, zeros={n_zero}/{arr.size}")
ds.close()

# ============================================================
# H4. Bathymetry feature at v4 crash region (i=8, j=15-16)
# ============================================================
print("\n" + "=" * 70)
print("  H4. BATHYMETRY AT v4 CRASH REGION (i=8, j=15-16)")
print("=" * 70)

ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
ds.close()

# v4 crash at (i=8, j=15-16, k=9-10)
# v3 crash at (i=11-13, j=31-32, k=10)
print(f"  v4 crash region (i=8, j=15-16) bathymetry:")
print(f"  {'j':>3s} | " + " ".join(f"i={i:2d}" for i in range(6, 11)))
for j in range(14, 18):
    print(f"  {j:3d} | " + " ".join(f"{b[j-1, i-1]:6.2f}" for i in range(6, 11)))

print(f"\n  v3 crash region (i=11-13, j=31-32) bathymetry:")
print(f"  {'j':>3s} | " + " ".join(f"i={i:2d}" for i in range(9, 15)))
for j in range(30, 34):
    print(f"  {j:3d} | " + " ".join(f"{b[j-1, i-1]:6.2f}" for i in range(9, 15)))

# depth gradients at both crash regions
print(f"\n  Depth gradients (max |dH|/dx in 4 neighbors):")
for region_name, i_range, j_range in [("v4_region", range(6, 11), range(14, 18)),
                                       ("v3_region", range(9, 15), range(30, 34))]:
    max_grad = 0
    for j in j_range:
        for i in i_range:
            H = b[j-1, i-1]
            if H <= 0:
                continue
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                H_n = b[j-1+dj, i-1+di]
                if H_n > 0:
                    grad = abs(H - H_n) / 500.0
                    max_grad = max(max_grad, grad)
    print(f"  {region_name}: max gradient = {max_grad:.5f}")

# ============================================================
# H5. Check the exact model step vs output step relationship
# ============================================================
print("\n" + "=" * 70)
print("  H5. MODEL STEP vs OUTPUT STEP RELATIONSHIP")
print("=" * 70)

n_crash = 1117100
step_2d = 288  # from getm.inp
step_3d = 288
dt = 30  # seconds

# model step n=1117100 corresponds to:
day_crash = n_crash * dt / 86400
print(f"  Model crash step: n={n_crash}")
print(f"  Day: {day_crash:.4f}")
print(f"  Date: 2020-01-01 + {day_crash:.1f} days")

# how many 2D outputs have been saved by then?
n_2d_outputs = n_crash // step_2d
print(f"  2D outputs by crash: {n_2d_outputs}")
print(f"  3D outputs by crash: {n_crash // step_3d}")

# is n=1117100 a multiple of any special number?
print(f"\n  Factorization of {n_crash}:")
n = n_crash
factors = []
for p in range(2, 100):
    while n % p == 0:
        factors.append(p)
        n //= p
    if n == 1:
        break
if n > 1:
    factors.append(n)
print(f"  {n_crash} = {' x '.join(map(str, factors))}")

# is there something special about this step?
print(f"\n  Step in year cycle:")
steps_per_year = 365 * 86400 / dt
print(f"  Steps per year: {steps_per_year:.0f}")
print(f"  Crash step / steps_per_year: {n_crash / steps_per_year:.4f}")
print(f"  => Crash at year {n_crash / steps_per_year:.4f} (i.e., after 1 full annual cycle)")

# ============================================================
# H2. Floating-point error accumulation check
# ============================================================
print("\n" + "=" * 70)
print("  H2. FLOATING-POINT ERROR ACCUMULATION CHECK")
print("=" * 70)

# compare early field (day 22) vs late field (day 370) - look for precision issues
ds3 = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
sigma = np.ma.filled(ds3.variables['sigma'][:], 0.0)

# get early and late steps
step_early = 220  # day 22
step_late = 3700  # day 370
for step_name, step in [("early (day 22)", step_early), ("late (day 370)", step_late)]:
    uu = np.ma.filled(ds3.variables['uu'][step], np.nan)
    vv = np.ma.filled(ds3.variables['vv'][step], np.nan)
    elev = np.ma.filled(nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.2d.nc')).variables['elev'][step], np.nan)

    # check for denormals or extreme values
    u_min, u_max = np.nanmin(uu), np.nanmax(uu)
    v_min, v_max = np.nanmin(vv), np.nanmax(vv)
    e_min, e_max = np.nanmin(elev), np.nanmax(elev)

    print(f"  {step_name}:")
    print(f"    uu: [{u_min:.6e}, {u_max:.6e}]")
    print(f"    vv: [{v_min:.6e}, {v_max:.6e}]")
    print(f"    elev: [{e_min:.6e}, {e_max:.6e}]")

    # check for values near float64 precision limits
    eps = np.finfo(np.float64).eps
    print(f"    float64 eps: {eps:.2e}")
    print(f"    max |uu|/eps ratio: {max(abs(u_min), abs(u_max))/eps:.2e}")
ds3.close()

# ============================================================
# Compare v3 vs v4 crash: are they really at the same step?
# ============================================================
print("\n" + "=" * 70)
print("  COMPARE v3 (barotropic) vs v4 (baroclinic) CRASH DETAILS")
print("=" * 70)

import subprocess
# v3 log is in backup_v3/run.log
v3_log = os.path.join(CASE, 'backup_v3', 'run.log')
v4_log = os.path.join(CASE, 'run.log')

for name, log_path in [("v3", v3_log), ("v4", v4_log)]:
    if not os.path.exists(log_path):
        print(f"  {name}: log not found at {log_path}")
        continue
    # get last n= line and FATAL context
    result = subprocess.run(['wsl', 'bash', '-c',
        f"grep 'n=' '{log_path}' | tail -1 && echo '---' && "
        f"grep -B 8 'FATAL' '{log_path}' | tail -12"],
        capture_output=True, text=True)
    print(f"\n  {name} crash details:")
    print(result.stdout)
