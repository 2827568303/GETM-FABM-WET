"""Check what's special about (i=8, j=15-16) - the v4 crash location."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  WHAT'S SPECIAL ABOUT (i=8, j=15-16)?")
print("=" * 70)

# load bathymetry
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
ds.close()

# crash location i=8, j=15-16 (1-based in GETM, 0-based in array: [j-1, i-1])
print(f"\n  Bathymetry at crash region (i=6-10, j=14-17):")
print(f"  {'j':>3s} | " + " ".join(f"i={i:2d}" for i in range(6, 11)))
for j in range(14, 18):
    print(f"  {j:3d} | " + " ".join(f"{b[j-1, i-1]:6.2f}" for i in range(6, 11)))

# check if (i=8, j=15) is a river cell
print(f"\n  River positions (from riverinfo.dat):")
with open(os.path.join(CASE, 'riverinfo.dat'), 'r') as f:
    lines = [ln.strip() for ln in f if ln.strip()]
n_river = int(lines[0])
for ln in lines[1:n_river+1]:
    parts = ln.split()
    if len(parts) >= 3:
        i, j, name = int(parts[0]), int(parts[1]), parts[2]
        dist_to_crash = np.sqrt((i-8)**2 + (j-15.5)**2)
        print(f"  {name:5s} at (i={i:2d}, j={j:2d}), distance to crash (8,15.5) = {dist_to_crash:.2f}")

# check velocity at crash location in last valid output
print(f"\n  Velocity at (i=8, j=15-16) in last valid 3D output:")
ds3 = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
n3 = len(ds3.variables['time'])
# last valid step
for step in [n3-5, n3-4, n3-3, n3-2, n3-1]:
    uu = np.ma.filled(ds3.variables['uu'][step], np.nan)
    vv = np.ma.filled(ds3.variables['vv'][step], np.nan)
    t = ds3.variables['time'][step] / 86400
    # at crash location
    u_crash = uu[:, 14:16, 7]  # k, j=15-16, i=8
    v_crash = vv[:, 14:16, 7]
    print(f"  step {step} (day {t:.2f}): at (i=8, j=15-16):")
    print(f"    uu: {u_crash[:, 0]}")  # j=15
    print(f"    uu: {u_crash[:, 1]}")  # j=16
ds3.close()

# check earlier steps for trend
print(f"\n  Trend at (i=8, j=15, k=1) - surface layer:")
ds3 = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
for step in range(3700, 3750, 5):  # last few days
    uu = np.ma.filled(ds3.variables['uu'][step, 1, 14, 7], np.nan)  # k=1, j=15, i=8
    vv = np.ma.filled(ds3.variables['vv'][step, 1, 14, 7], np.nan)
    t = ds3.variables['time'][step] / 86400
    print(f"  step {step} (day {t:.2f}): uu={uu:.4f}, vv={vv:.4f}")
ds3.close()
