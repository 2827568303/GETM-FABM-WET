"""Scheme B: Apply 15-day smoothing to ZYH only (prime suspect)."""
import os
import shutil
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
RIVERS_NC = os.path.join(CASE, 'rivers.nc')
RIVERS_ORIG = os.path.join(CASE, 'rivers_orig.nc')

print("=" * 70)
print("  SCHEME B: ZYH 15-day smoothing (other rivers unchanged)")
print("=" * 70)

# read from original backup (clean state)
ds = nc.Dataset(RIVERS_ORIG, 'r')
t = ds.variables['time'][:]
rivers = {}
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    rivers[name] = np.ma.filled(ds.variables[name][:], 0.0)
ds.close()

# current settings: cap=200, smooth=11
# new: ZYH only gets 15-day smooth (was 11), others keep 11-day

def smooth(x, win):
    if win <= 1:
        return x
    kernel = np.ones(win) / win
    pad = win // 2
    padded = np.pad(x, (pad, pad), mode='edge')
    return np.convolve(padded, kernel, mode='valid')


CAP = 200.0
SMOOTH_WIN_ZYH = 15  # increased from 11
SMOOTH_WIN_OTHER = 11

# show ZYH stats before/after
zyh_orig = rivers['ZYH']
zyh_capped = np.clip(zyh_orig, -CAP, CAP)
zyh_11d = smooth(zyh_capped, 11)
zyh_15d = smooth(zyh_capped, 15)
print(f"\n  ZYH comparison (day 385-392 around crash):")
print(f"  {'day':>4s} {'orig':>10s} {'capped':>10s} {'11d':>10s} {'15d':>10s}")
for d in range(385, 393):
    print(f"  {d:4d} {zyh_orig[d]:10.2f} {zyh_capped[d]:10.2f} {zyh_11d[d]:10.2f} {zyh_15d[d]:10.2f}")

print(f"\n  ZYH range: 11d=[{zyh_11d.min():.1f}, {zyh_11d.max():.1f}], 15d=[{zyh_15d.min():.1f}, {zyh_15d.max():.1f}]")

# write
ds = nc.Dataset(RIVERS_NC, 'w', format='NETCDF4')
ds.createDimension('time', None)
tv = ds.createVariable('time', 'f8', ('time',))
tv.units = 'seconds since 2020-01-01 00:00:00'
tv[:] = t

for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = rivers[name].copy()
    q_capped = np.clip(q, -CAP, CAP)
    win = SMOOTH_WIN_ZYH if name == 'ZYH' else SMOOTH_WIN_OTHER
    q_final = smooth(q_capped, win)
    v = ds.createVariable(name, 'f8', ('time',))
    v.units = 'm3/s'
    v[:] = q_final
    print(f"  {name}: cap={CAP}, smooth={win}d, range=[{q_final.min():.1f}, {q_final.max():.1f}]")

ds.title = f'Luoma Lake rivers (Scheme B: ZYH 15d, others 11d)'
ds.close()
print(f"\n  Wrote {RIVERS_NC}")
