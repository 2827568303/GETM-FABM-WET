"""Comprehensive stability improvement for Lake Luoma GETM model.

Applies 4 improvement schemes together (single change rarely sufficient):
  1. 20-pass bathymetry smoothing (was 10-pass) + extra smoothing in crash region
  2. Adjust 3D numerical parameters in getm.inp:
     - ip_method=2 (Song-Haidvogel, better for slopes)
     - cord_relax=0.1 (sigma coordinate relaxation)
     - avmback=1.0E-5, avhback=1.0E-6 (background eddy viscosity)
  3. Further river smoothing: cap +/-200 m3/s, 11-day moving average
  4. Vertical layer optimization: M=10, min_depth=1.0m
"""
import os
import shutil
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
BATHY_NC = os.path.join(CASE, 'bathymetry.nc')
RIVERS_NC = os.path.join(CASE, 'rivers.nc')
RIVERS_ORIG = os.path.join(CASE, 'rivers_orig.nc')
GETM_INP = os.path.join(CASE, 'getm.inp')

print("=" * 70)
print("  COMPREHENSIVE STABILITY IMPROVEMENT")
print("=" * 70)


# ------------------------------------------------------------------
# Scheme 1: 20-pass bathymetry smoothing + crash region enhancement
# ------------------------------------------------------------------
print("\n[1/4] Scheme 1: 20-pass bathymetry smoothing + crash region enhancement")

ds = nc.Dataset(BATHY_NC, 'r')
H = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
x = np.ma.filled(ds.variables['x'][:], 0.0)
y = np.ma.filled(ds.variables['y'][:], 0.0)
lonc = np.ma.filled(ds.variables['lonc'][:], 0.0)
latc = np.ma.filled(ds.variables['latc'][:], 0.0)
ds.close()

water_mask = H > 0
print(f"  Water cells: {int(water_mask.sum())}")
print(f"  Pre-smooth depth: {H[water_mask].min():.2f}-{H[water_mask].max():.2f} m, mean={H[water_mask].mean():.2f} m")


def smooth_bathymetry(H, water_mask, n_passes=3, extra_region=None):
    """5-point smoothing with optional extra passes in a region.

    extra_region: (i_min, i_max, j_min, j_max) for additional smoothing.
    """
    Hs = H.copy()
    for p in range(n_passes):
        Hnew = Hs.copy()
        for j in range(1, H.shape[0] - 1):
            for i in range(1, H.shape[1] - 1):
                if not water_mask[j, i]:
                    continue
                vals = [Hs[j, i]]
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if water_mask[j + dj, i + di]:
                        vals.append(Hs[j + dj, i + di])
                Hnew[j, i] = np.mean(vals)
        Hs = Hnew
        dH = np.abs(Hs[water_mask] - H[water_mask])
        if (p + 1) % 5 == 0 or p == n_passes - 1:
            print(f"  Pass {p+1}: max |dH|={dH.max():.3f} m, mean |dH|={dH.mean():.3f} m")

    # extra smoothing in crash region (i=5-20, j=22-32, 0-based)
    if extra_region:
        i_min, i_max, j_min, j_max = extra_region
        for p in range(10):
            Hnew = Hs.copy()
            for j in range(j_min, j_max):
                for i in range(i_min, i_max):
                    if not water_mask[j, i]:
                        continue
                    vals = [Hs[j, i]]
                    for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if water_mask[j + dj, i + di]:
                            vals.append(Hs[j + dj, i + di])
                    Hnew[j, i] = np.mean(vals)
            Hs = Hnew
        dH_region = np.abs(Hs[j_min:j_max, i_min:i_max][water_mask[j_min:j_max, i_min:i_max]] -
                            H[j_min:j_max, i_min:i_max][water_mask[j_min:j_max, i_min:i_max]])
        print(f"  Extra 10 passes in crash region: max |dH|={dH_region.max():.3f} m")
    return Hs


# 20-pass global + 10 extra in crash region (i=5-20, j=22-32 in 0-based)
H_smoothed = smooth_bathymetry(H, water_mask, n_passes=20,
                                extra_region=(5, 20, 22, 32))
print(f"  Post-smooth depth: {H_smoothed[water_mask].min():.2f}-{H_smoothed[water_mask].max():.2f} m, "
      f"mean={H_smoothed[water_mask].mean():.2f} m")

# write bathymetry.nc
ds = nc.Dataset(BATHY_NC, 'w', format='NETCDF4')
ds.createDimension('x', len(x))
ds.createDimension('y', len(y))
ds.createDimension('xq', len(x) + 1)
ds.createDimension('yq', len(y) + 1)

gt = ds.createVariable('grid_type', 'i4')
gt[:] = 1

xv = ds.createVariable('x', 'f8', ('x',))
yv = ds.createVariable('y', 'f8', ('y',))
xv[:] = x; yv[:] = y

lonv = ds.createVariable('lonc', 'f8', ('y', 'x'))
latv = ds.createVariable('latc', 'f8', ('y', 'x'))
lonv[:] = lonc; latv[:] = latc

bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
bv[:] = H_smoothed
bv.units = 'm'; bv.long_name = 'water depth'

ds.title = 'Luoma Lake bathymetry (20-pass + crash region enhanced)'
ds.close()
print(f"  Wrote {BATHY_NC}")


# ------------------------------------------------------------------
# Scheme 3: River flow further smoothing (cap 200, 11-day window)
# ------------------------------------------------------------------
print("\n[2/4] Scheme 3: River flow cap=200, 11-day smoothing")
if not os.path.exists(RIVERS_ORIG):
    shutil.copy2(RIVERS_NC, RIVERS_ORIG)

ds = nc.Dataset(RIVERS_ORIG, 'r')
t = ds.variables['time'][:]
rivers = {}
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    rivers[name] = np.ma.filled(ds.variables[name][:], 0.0)
ds.close()


def smooth(x, win=11):
    if win <= 1:
        return x
    kernel = np.ones(win) / win
    pad = win // 2
    padded = np.pad(x, (pad, pad), mode='edge')
    return np.convolve(padded, kernel, mode='valid')


CAP = 200.0
SMOOTH_WIN = 11
ds = nc.Dataset(RIVERS_NC, 'w', format='NETCDF4')
ds.createDimension('time', None)
tv = ds.createVariable('time', 'f8', ('time',))
tv.units = 'seconds since 2020-01-01 00:00:00'
tv[:] = t

for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = rivers[name].copy()
    n_capped = np.sum(np.abs(q) > CAP)
    q_capped = np.clip(q, -CAP, CAP)
    q_final = smooth(q_capped, SMOOTH_WIN)
    v = ds.createVariable(name, 'f8', ('time',))
    v.units = 'm3/s'
    v[:] = q_final
    print(f"  {name}: {n_capped} capped, range {q_final.min():.1f} to {q_final.max():.1f}")
ds.title = f'Luoma Lake rivers (cap=+/-{CAP}, smooth={SMOOTH_WIN}d)'
ds.close()
print(f"  Wrote {RIVERS_NC}")


# ------------------------------------------------------------------
# Scheme 2 & 4: Update getm.inp (ip_method, cord_relax, avmback, M, min_depth)
# ------------------------------------------------------------------
print("\n[3/4] Scheme 2+4: Update getm.inp numerical parameters")
shutil.copy2(GETM_INP, os.path.join(CASE, 'getm.inp.before_stability_fix'))

with open(GETM_INP, 'r') as f:
    content = f.read()

# Scheme 4: M=12 -> 10, min_depth 0.5 -> 1.0
content = content.replace('M = 12', 'M = 10')
content = content.replace('min_depth = 0.5', 'min_depth = 1.0')
content = content.replace('crit_depth = 1.5', 'crit_depth = 1.5')

# Scheme 2: ip_method 1 -> 2, cord_relax 0.0 -> 0.1, add background viscosity
content = content.replace('ip_method = 1', 'ip_method = 2')
content = content.replace('cord_relax = 0.0', 'cord_relax = 0.1')
content = content.replace('avmback = 0.0', 'avmback = 1.0E-5')
content = content.replace('avhback = 0.0', 'avhback = 1.0E-6')

with open(GETM_INP, 'w') as f:
    f.write(content)

print("  Changes applied to getm.inp:")
print("    M: 12 -> 10                    (reduce bottom sigma clustering)")
print("    min_depth: 0.5 -> 1.0          (avoid shallow numerical pathology)")
print("    ip_method: 1 -> 2              (Song-Haidvogel, better for slopes)")
print("    cord_relax: 0.0 -> 0.1         (sigma coordinate relaxation)")
print("    avmback: 0 -> 1.0E-5           (background momentum viscosity)")
print("    avhback: 0 -> 1.0E-6           (background scalar diffusivity)")

print("\n[4/4] Summary")
print("=" * 70)
print("All 4 schemes applied. Ready to rerun model.")
print("  - bathymetry: 20-pass + crash region 10 extra passes")
print("  - rivers: cap=200, 11-day smooth")
print("  - getm.inp: ip_method=2, cord_relax=0.1, M=10, min_depth=1.0, avmback/avhback")
print("=" * 70)
