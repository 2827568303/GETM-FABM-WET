"""Check bathymetry around river positions to determine multi-grid cell layout.

For each river that needs multi-grid (DAYUN, YIHE, ZHANGSHAN):
- Print depth at current position and neighbors
- Suggest 3 grid cells along the lake edge
"""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
bathy = ds.variables['bathymetry'][:]
# bathy shape is (y, x) = (j, i), 0-indexed
ds.close()

ny, nx = bathy.shape
print(f"Bathymetry grid: {nx} x {ny} (x: 1..{nx}, y: 1..{ny})")
print(f"Water cells: {np.sum(bathy > 0)}, land cells: {np.sum(bathy <= 0)}")
print()

# Current river positions (1-based i, j)
rivers = {
    'YIHE':      (21, 50),  # 沂河 - inflow NORTH
    'LUONAN':    (28, 2),   # 骆南中运河 - inflow SOUTH
    'DAYUN':     (2, 32),   # 京杭大运河 - bidirectional WEST
    'ZHANGSHAN': (42, 27),  # 新沂河/嶂山闸 - outflow EAST
    'YANGHE':    (35, 28),  # 洋河 - outflow SOUTHEAST
}

def show_neighbors(name, ci, cj, radius=2):
    """Show bathymetry around (ci, cj) 1-based."""
    print(f"\n{'='*60}")
    print(f"{name} at (i={ci}, j={cj}) - depth: {bathy[cj-1, ci-1]:.2f} m")
    print(f"{'='*60}")
    print("  j\\i", end="")
    for di in range(-radius, radius+1):
        print(f"{ci+di:>8}", end="")
    print()
    for dj in range(-radius, radius+1):
        j = cj + dj
        print(f"  j={j:>3}", end="")
        for di in range(-radius, radius+1):
            i = ci + di
            if 1 <= i <= nx and 1 <= j <= ny:
                d = bathy[j-1, i-1]
                if d > 0:
                    print(f"{d:>8.2f}", end="")
                else:
                    print(f"{'LAND':>8}", end="")
            else:
                print(f"{'OOR':>8}", end="")
        print()

# Show neighbors for multi-grid candidates
for name in ['YIHE', 'DAYUN', 'ZHANGSHAN']:
    ci, cj = rivers[name]
    show_neighbors(name, ci, cj, radius=3)

# Suggest multi-grid layouts
print("\n" + "=" * 60)
print("Multi-grid suggestions (along lake edge):")
print("=" * 60)

# DAYUN: west edge, spread along j (north-south)
# Current (2,32). Check (2,31),(2,32),(2,33)
print("\nDAYUN (west edge, along j):")
for j in [30, 31, 32, 33, 34]:
    i = 2
    d = bathy[j-1, i-1] if bathy[j-1, i-1] > 0 else 0
    print(f"  (i={i}, j={j}): depth={d:.2f} m {'<-- current' if j==32 else ''}")

# YIHE: north edge, spread along i (east-west)
# Current (21,50). Check (19,50),(20,50),(21,50),(22,50),(23,50)
print("\nYIHE (north edge, along i):")
for i in [18, 19, 20, 21, 22, 23, 24]:
    j = 50
    d = bathy[j-1, i-1] if bathy[j-1, i-1] > 0 else 0
    print(f"  (i={i}, j={j}): depth={d:.2f} m {'<-- current' if i==21 else ''}")

# ZHANGSHAN: east edge, spread along j
# Current (42,27). Check (42,25),(42,26),(42,27),(42,28),(42,29)
print("\nZHANGSHAN (east edge, along j):")
for j in [24, 25, 26, 27, 28, 29, 30]:
    i = 42
    d = bathy[j-1, i-1] if bathy[j-1, i-1] > 0 else 0
    print(f"  (i={i}, j={j}): depth={d:.2f} m {'<-- current' if j==27 else ''}")

# Also check east edge alternatives for ZHANGSHAN
print("\nZHANGSHAN alternatives (along i at j=27):")
for i in [39, 40, 41, 42, 43, 44]:
    j = 27
    if 1 <= i <= nx:
        d = bathy[j-1, i-1] if bathy[j-1, i-1] > 0 else 0
        print(f"  (i={i}, j={j}): depth={d:.2f} m {'<-- current' if i==42 else ''}")
