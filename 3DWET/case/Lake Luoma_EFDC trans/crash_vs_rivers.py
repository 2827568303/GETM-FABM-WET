"""Verify crash location vs river positions and flow capacity."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

# load bathymetry
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
ds.close()

print("=" * 70)
print("  CRASH LOCATION vs RIVER POSITIONS ANALYSIS")
print("=" * 70)

# parse riverinfo.dat
print("\n[1] riverinfo.dat content (river positions):")
print(f"  {'name':6s} {'i':>3s} {'j':>3s} {'H(m)':>6s}  river_description")
river_positions = {}
river_desc = {
    'ZYH': '沂河(运南闸) - inflow/outflow',
    'ZH':  '京杭大运河 - 调水+泄洪 (正负流量)',
    'YH':  '沂河 - inflow',
    'XYH': '新沂河 - 大流量出湖',
    'YHT': '沂沭河 - outflow'
}
with open(os.path.join(CASE, 'riverinfo.dat'), 'r') as f:
    lines = [ln.strip() for ln in f if ln.strip()]
n_river = int(lines[0])
for ln in lines[1:n_river+1]:
    parts = ln.split()
    if len(parts) >= 3:
        i, j, name = int(parts[0]), int(parts[1]), parts[2]
        H = b[j-1, i-1]
        print(f"  {name:6s} {i:3d} {j:3d} {H:6.2f}  {river_desc.get(name,'')}")
        if name not in river_positions:
            river_positions[name] = []
        river_positions[name].append((i, j, H))

# crash locations
print("\n[2] Crash locations analysis:")
crash1 = (range(8, 18), range(25, 30))  # (i=8-17, j=25-29)
crash2 = (range(9, 13), range(30, 32))  # (i=9-12, j=30-31)
print(f"  Crash #1 (before fix): i=8-17, j=25-29 (sigma=0 surface)")
print(f"  Crash #2 (after fix):  i=9-12, j=30-31 (sigma=0 surface)")

# distance from each river to crash centers
crash1_center = (12.5, 27.5)
crash2_center = (10.5, 30.5)
print(f"\n[3] Distance from rivers to crash centers:")
print(f"  {'river':6s} {'i':>3s} {'j':>3s}  dist_crash1  dist_crash2")
for name, positions in river_positions.items():
    for (i, j, H) in positions:
        d1 = np.sqrt((i - crash1_center[0])**2 + (j - crash1_center[1])**2)
        d2 = np.sqrt((i - crash2_center[0])**2 + (j - crash2_center[1])**2)
        print(f"  {name:6s} {i:3d} {j:3d}  {d1:8.2f} grid  {d2:8.2f} grid")

# flow capacity analysis: single cell volume change per unit flow
print("\n[4] Flow capacity analysis (per river cell):")
print(f"  Cell size: 500m x 500m = 250000 m²")
print(f"  Time step: 30 s")
print(f"  For Q=200 m³/s (cap value):")
print(f"    Water level change per step = Q * dt / area = 200 * 30 / 250000 = {200*30/250000:.4f} m/step")
print(f"    Water level change per day = {200*30/250000 * 2880:.2f} m/day  (2880 steps/day)")
print(f"  For Q=300 m³/s (old cap):")
print(f"    Water level change per day = {300*30/250000 * 2880:.2f} m/day")

# per-river flow capacity
print(f"\n[5] Per-river flow capacity vs cell count:")
ds_r = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = np.ma.filled(ds_r.variables[name][:], 0.0)
    n_cells = len(river_positions.get(name, []))
    max_q = np.max(np.abs(q))
    # max water level change per day for this river
    if n_cells > 0:
        wl_change_per_day = max_q * 30 * 2880 / (250000 * n_cells)
        print(f"  {name:6s}: cells={n_cells}, max|Q|={max_q:.0f} m³/s, "
              f"max ΔWL/day={wl_change_per_day:.2f} m/day  "
              f"{'[HIGH!]' if wl_change_per_day > 1.0 else '[ok]'}")
ds_r.close()

# check XYH and ZH specific flow at crash times
print(f"\n[6] ZH (京杭大运河) and XYH (新沂河) flow at crash times:")
ds_r = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
for name in ['ZH', 'XYH', 'ZYH', 'YH', 'YHT']:
    q = np.ma.filled(ds_r.variables[name][:], 0.0)
    print(f"  {name:6s}: day 230={q[230]:.1f}, day 233={q[233]:.1f}, "
          f"day 380={q[380]:.1f}, day 387={q[387]:.1f}, "
          f"max around 380-390: {np.max(np.abs(q[380:390])):.1f}")
ds_r.close()

print("\n" + "=" * 70)
print("  CONCLUSION")
print("=" * 70)
print("""
Key question: Are crashes at ZH (京杭大运河) or XYH (新沂河) locations?

ZH (京杭大运河) at (i, j) with 1 cell - user's prime suspect
XYH (新沂河) at (i, j) with 3 cells - already multi-cell

If crashes are near these rivers AND single-cell ZH has high flow,
then user's recommendation applies:
  - Expand ZH from 1 cell to 3 cells (add 2 neighboring cells)
  - GETM will auto-distribute flow via flow_fraction (Q/3 per cell)
  - This reduces per-cell water level forcing by 3x
""")
