"""Check if existing river positions are on water cells in new bathymetry.
Find nearest water cell if not, and determine correct river positions."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
bathy = ds.variables["bathymetry"][:]
x = ds.variables["x"][:]
y = ds.variables["y"][:]
ds.close()

ny, nx = bathy.shape
water_mask = bathy > 0

# Existing river positions (i, j) - 1-indexed
rivers = {
    "YIHE":      (26, 12),  # 沂河 - inflow from north
    "LUONAN":    (12, 42),  # 骆南中运河 - inflow from west
    "DAYUN":     (7, 32),   # 京杭大运河 - bidirectional
    "ZHANGSHAN": (32, 15),  # 新沂河/嶂山闸 - outflow east
    "YANGHE":    (35, 28),  # 总六塘河/杨河滩 - outflow southeast
}

print("=" * 70)
print("Checking river positions against new bathymetry")
print("=" * 70)
print(f"Grid: {nx} x {ny}")
print(f"Water cells: {np.sum(water_mask)}")
print()

for name, (i, j) in rivers.items():
    # Convert to 0-indexed
    i0, j0 = i - 1, j - 1
    xi, yj = x[i0], y[j0]
    if 0 <= i0 < nx and 0 <= j0 < ny:
        depth = bathy[j0, i0]
        is_water = water_mask[j0, i0]
        status = "WATER" if is_water else "LAND"
        print(f"{name:12s} (i={i:2d}, j={j:2d}) x={xi:.0f} y={yj:.0f} depth={depth:.2f} -> {status}")
        if not is_water:
            # Find nearest water cell
            min_dist = float("inf")
            best = None
            for jj in range(ny):
                for ii in range(nx):
                    if water_mask[jj, ii]:
                        dist = (ii - i0) ** 2 + (jj - j0) ** 2
                        if dist < min_dist:
                            min_dist = dist
                            best = (ii + 1, jj + 1, x[ii], y[jj], bathy[jj, ii])
            if best:
                print(f"  -> Nearest water cell: i={best[0]}, j={best[1]}, x={best[2]:.0f}, y={best[3]:.0f}, depth={best[4]:.2f}")

# Print all edge water cells (water cells adjacent to land or grid boundary)
print("\n" + "=" * 70)
print("All edge water cells (water cells adjacent to land)")
print("=" * 70)
edge_cells = []
for j in range(ny):
    for i in range(nx):
        if not water_mask[j, i]:
            continue
        is_edge = False
        for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nj, ni = j + dj, i + di
            if 0 <= nj < ny and 0 <= ni < nx:
                if not water_mask[nj, ni]:
                    is_edge = True
                    break
            else:
                is_edge = True
                break
        if is_edge:
            edge_cells.append((i + 1, j + 1, x[i], y[j], bathy[j, i]))

print(f"Total: {len(edge_cells)} edge cells")
print(f"\n{'i':>4} {'j':>4} {'x':>10} {'y':>10} {'depth':>8}")
print("-" * 40)
for c in sorted(edge_cells, key=lambda c: (c[1], c[0])):
    print(f"{c[0]:>4d} {c[1]:>4d} {c[2]:>10.0f} {c[3]:>10.0f} {c[4]:>8.2f}")

# Also print which side each edge cell is on
print("\nEdge cells by side (for river placement):")
print("  North (y > 3787000):")
for c in sorted([c for c in edge_cells if c[3] > 3787000], key=lambda c: c[0]):
    print(f"    i={c[0]:2d}, j={c[1]:2d}, x={c[2]:.0f}, y={c[3]:.0f}, depth={c[4]:.2f}")
print("  South (y < 3764000):")
for c in sorted([c for c in edge_cells if c[3] < 3764000], key=lambda c: c[0]):
    print(f"    i={c[0]:2d}, j={c[1]:2d}, x={c[2]:.0f}, y={c[3]:.0f}, depth={c[4]:.2f}")
print("  West (x < 602000):")
for c in sorted([c for c in edge_cells if c[2] < 602000], key=lambda c: c[1]):
    print(f"    i={c[0]:2d}, j={c[1]:2d}, x={c[2]:.0f}, y={c[3]:.0f}, depth={c[4]:.2f}")
print("  East (x > 618000):")
for c in sorted([c for c in edge_cells if c[2] > 618000], key=lambda c: c[1]):
    print(f"    i={c[0]:2d}, j={c[1]:2d}, x={c[2]:.0f}, y={c[3]:.0f}, depth={c[4]:.2f}")
