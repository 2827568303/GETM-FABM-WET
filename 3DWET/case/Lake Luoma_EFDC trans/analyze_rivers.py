"""Analyze river flow statistics and create capped + smoothed version.

The 3D model diverges at day 9.90 because ZYH jumps from +2.29 to -642.65 m3/s
in a single day. GETM applies river volume directly to water level:
    height = Q * flow_fraction * dt / area
For ZYH (3 cells, 500m x 500m each), -642.65/3 = -214 m3/s per cell gives
-74 m/day water level drop - far exceeding the 4m depth.

Strategy:
  1. Cap at +/-300 m3/s (above 95th percentile for most rivers)
  2. Apply 5-day centered moving average to remove single-day spikes
  3. This preserves seasonal dynamics while eliminating numerical shocks
"""
import netCDF4 as nc
import numpy as np
import os
import shutil

CASE_DIR = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"
RIVERS_ORIG = os.path.join(CASE_DIR, "rivers_orig.nc")
RIVERS_NC = os.path.join(CASE_DIR, "rivers.nc")

# Always work from the original backup
if not os.path.exists(RIVERS_ORIG):
    shutil.copy2(RIVERS_NC, RIVERS_ORIG)
    print(f"Backed up original rivers -> {RIVERS_ORIG}")

ds = nc.Dataset(RIVERS_ORIG, 'r')
t = ds.variables['time'][:]
rivers = {}
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    rivers[name] = q
    print(f"\n{name} statistics (original):")
    print(f"  min={q.min():.2f}, max={q.max():.2f}, mean={q.mean():.2f}")
    print(f"  |Q| > 100: {np.sum(np.abs(q) > 100)} days")
    print(f"  |Q| > 300: {np.sum(np.abs(q) > 300)} days")
    print(f"  |Q| > 500: {np.sum(np.abs(q) > 500)} days")
ds.close()

CAP = 300.0  # m3/s
SMOOTH_WIN = 5  # days, centered moving average


def smooth(x, win=SMOOTH_WIN):
    """Centered moving average with edge padding."""
    if win <= 1:
        return x
    kernel = np.ones(win) / win
    # pad edges by reflecting
    pad = win // 2
    padded = np.pad(x, (pad, pad), mode='edge')
    return np.convolve(padded, kernel, mode='valid')


print(f"\nApplying cap at +/-{CAP} m3/s then {SMOOTH_WIN}-day smoothing...")

# Show day 7-12 ZYH transformation
zyh_orig = rivers['ZYH'].copy()
zyh_capped = np.clip(zyh_orig, -CAP, CAP)
zyh_smoothed = smooth(zyh_capped)
print("\nZYH day 7-12 transformation:")
print(f"  {'day':>4}  {'orig':>10}  {'capped':>10}  {'smoothed':>10}")
for i in range(6, 13):
    print(f"  {i:4d}  {zyh_orig[i]:10.2f}  {zyh_capped[i]:10.2f}  {zyh_smoothed[i]:10.2f}")

# Write processed rivers.nc
ds = nc.Dataset(RIVERS_NC, 'w', format='NETCDF4')
ds.createDimension('time', None)

tv = ds.createVariable('time', 'f8', ('time',))
tv.units = 'seconds since 2020-01-01 00:00:00'
tv.long_name = 'time'
tv[:] = t

for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = rivers[name].copy()
    n_capped = np.sum(np.abs(q) > CAP)
    q_capped = np.clip(q, -CAP, CAP)
    q_final = smooth(q_capped)
    v = ds.createVariable(name, 'f8', ('time',))
    v.units = 'm3/s'
    v.long_name = f'{name} river discharge (cap={CAP}, smooth={SMOOTH_WIN}d)'
    v[:] = q_final
    print(f"  {name}: {n_capped} values capped, then smoothed")

ds.title = f'Luoma Lake river data (cap=+/-{CAP}, smooth={SMOOTH_WIN}d)'
ds.source = 'efdc_to_getm.py + analyze_rivers.py'
ds.close()
print(f"\nWrote processed rivers.nc")
