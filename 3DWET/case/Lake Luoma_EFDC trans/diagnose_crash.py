"""Diagnose the crash region (i=8-17, j=25-29, k=10 bottom layer)."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

# load bathymetry
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], np.nan)
ds.close()

print("=" * 70)
print("  CRASH REGION ANALYSIS (i=8-17, j=25-29, k=10)")
print("=" * 70)
print(f"\n  Bathymetry in crash region (i=8-17, j=25-29):")
print(f"  (note: bathymetry array is [j, i] = [y, x])")
print(f"  {'j':>3} | " + " ".join(f"i={i:2d}" for i in range(8, 18)))
for j in range(25, 30):
    print(f"  {j:3d} | " + " ".join(f"{b[j-1, i-1]:6.2f}" for i in range(8, 18)))

# depth gradient in crash region
print(f"\n  Depth gradient (dH/dx, dH/dy) in crash region:")
for j in range(26, 29):
    for i in range(10, 16):
        H = b[j-1, i-1]
        Hx_e = b[j-1, i] - H  # east neighbor
        Hx_w = H - b[j-1, i-2]  # west neighbor
        Hy_n = b[j, i-1] - H  # north neighbor
        Hy_s = H - b[j-2, i-1]  # south neighbor
        dHdx = max(abs(Hx_e), abs(Hx_w)) / 500.0
        dHdy = max(abs(Hy_n), abs(Hy_s)) / 500.0
        if H > 0:
            print(f"  i={i:2d} j={j:2d}: H={H:5.2f}m, |dH/dx|={dHdx:.4f}, |dH/dy|={dHdy:.4f}, "
                  f"max slope={max(dHdx,dHdy):.4f} ({'STEEP' if max(dHdx,dHdy)>0.005 else 'ok'})")

# load last valid 3D velocity field
print(f"\n  Velocity at last valid step (near crash):")
ds3 = nc.Dataset(os.path.join(CASE, 'LUOMA_EFDC_HYD.3d.nc'))
n = len(ds3.variables['time'])
sigma = np.ma.filled(ds3.variables['sigma'][:], np.nan)
print(f"  sigma levels: {sigma}")
print(f"  k=10 is sigma={sigma[10]:.2f} ({'surface' if sigma[10]==0 else 'bottom' if sigma[10]==-1 else 'mid'})")

# load steps 2300-2303 to see velocity evolution
for step_idx in [n-5, n-4, n-3, n-2, n-1]:
    if step_idx < 0:
        continue
    uu = np.ma.filled(ds3.variables['uu'][step_idx], np.nan)
    vv = np.ma.filled(ds3.variables['vv'][step_idx], np.nan)
    w = np.ma.filled(ds3.variables['w'][step_idx], np.nan)
    t = ds3.variables['time'][step_idx] / 86400
    # extract crash region bottom layer
    u_crash = uu[10, 24:29, 7:17]  # k=10, j=25-29, i=8-17
    v_crash = vv[10, 24:29, 7:17]
    w_crash = w[10, 24:29, 7:17]
    print(f"\n  step {step_idx} (day {t:.2f}): crash region k=10 (bottom):")
    print(f"    uu: min={np.nanmin(u_crash):.4f}, max={np.nanmax(u_crash):.4f}")
    print(f"    vv: min={np.nanmin(v_crash):.4f}, max={np.nanmax(v_crash):.4f}")
    print(f"    w:  min={np.nanmin(w_crash):.6f}, max={np.nanmax(w_crash):.6f}")
ds3.close()

# check river flow at crash time
print(f"\n  River flow at crash time (day ~233):")
ds_r = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
for v in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = np.ma.filled(ds_r.variables[v][:], np.nan)
    # day 233 is index 233
    print(f"  {v}: day 230={q[230]:.2f}, day 233={q[233]:.2f}, max around={max(abs(q[228:238].max()),abs(q[228:238].min())):.2f}")
ds_r.close()

# check CFL estimate
print(f"\n  CFL estimate at crash region:")
print(f"  dt=30s, dx=dy=500m")
for j in range(26, 29):
    for i in range(10, 16):
        H = b[j-1, i-1]
        if H <= 0:
            continue
        # wave speed ~ sqrt(g*H)
        c = np.sqrt(9.81 * H)
        cfl = c * 30 / 500
        print(f"  i={i:2d} j={j:2d}: H={H:5.2f}m, c={c:.2f}m/s, CFL={cfl:.4f}")
