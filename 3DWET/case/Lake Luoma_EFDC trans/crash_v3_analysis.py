"""Quick check crash at day 8.26 with expanded river cells."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  CRASH ANALYSIS: day 8.26 with 15 river cells (5 rivers x 3 cells)")
print("=" * 70)

# river flow at day 5-12
print("\n[1] River flow at day 5-12 (after cap=200, 11-day smooth):")
ds = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
for v in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = np.ma.filled(ds.variables[v][:], 0.0)
    print(f"  {v:5s}: day 5-12: {[f'{q[i]:7.1f}' for i in range(5, 13)]}")
ds.close()

# per-cell water level change at day 8
print("\n[2] Per-cell water level change at day 8 (Q/3 per cell):")
ds = nc.Dataset(os.path.join(CASE, 'rivers.nc'))
cell_area = 500 * 500  # m²
dt = 30  # s
steps_per_day = 86400 // dt  # 2880
for v in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = np.ma.filled(ds.variables[v][:], 0.0)
    q_day8 = q[8]
    wl_per_day = q_day8 * dt * steps_per_day / (cell_area * 3)  # /3 for 3 cells
    print(f"  {v:5s}: Q(day8)={q_day8:7.1f} m³/s, ΔWL/day={wl_per_day:+.2f} m/day (per cell, 3 cells)")
ds.close()

# read bathymetry at new river cells
print("\n[3] Bathymetry at new river cells:")
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
new_cells = {
    'YH_new':  [(15, 43), (14, 44)],
    'YHT_new': [(50, 11), (49, 12)],
    'ZH_new':  [(21, 5), (20, 6)],
}
for name, cells in new_cells.items():
    for (i, j) in cells:
        print(f"  {name}: (i={i}, j={j}) -> H={b[j-1, i-1]:.2f}m")
ds.close()

# check crash location from run.log
print("\n[4] Check 3D field values before crash:")
import subprocess
result = subprocess.run(['wsl', 'bash', '-c',
    f"grep 'check_3d_fields' '{os.path.join(CASE, 'run.log')}' | tail -10"],
    capture_output=True, text=True)
print(result.stdout)
