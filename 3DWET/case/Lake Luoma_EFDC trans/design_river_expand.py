"""Design river cell expansion: find neighboring water cells for ZH, YH, YHT."""
import os
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))

ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
ds.close()

print("=" * 70)
print("  RIVER CELL EXPANSION DESIGN")
print("=" * 70)
print("Current single-cell rivers need expansion to 3 cells:")
print("  ZH (京杭大运河) at (21, 6): 68 m/day -> need 3 cells -> 23 m/day")
print("  YH (沂河)      at (15, 44): 65 m/day -> need 3 cells -> 22 m/day")
print("  YHT (沂沭河)   at (50, 12): 26 m/day -> need 3 cells ->  9 m/day")
print()

# For each single-cell river, find best 2 neighboring water cells
rivers_to_expand = {
    'ZH':  (21, 6),    # 京杭大运河 - 湖边
    'YH':  (15, 44),   # 沂河 - 湖边
    'YHT': (50, 12),   # 沂沭河 - 湖边
}

for name, (i0, j0) in rivers_to_expand.items():
    print(f"\n[{name}] current cell (i={i0}, j={j0}), H={b[j0-1, i0-1]:.2f}m")
    # search 3x3 neighborhood for water cells
    print(f"  3x3 neighborhood (j-1..j+1, i-1..i+1):")
    print(f"  {'j':>3s} {'i':>3s} {'H(m)':>6s} {'status':>8s}")
    candidates = []
    for dj in [-1, 0, 1]:
        for di in [-1, 0, 1]:
            i, j = i0 + di, j0 + dj
            if 1 <= i <= 52 and 1 <= j <= 46:
                H = b[j-1, i-1]
                status = 'WATER' if H > 0 else 'land'
                print(f"  {j:3d} {i:3d} {H:6.2f} {status:>8s}")
                if H > 0 and not (di == 0 and dj == 0):
                    # prefer cells along same row or column (orthogonal)
                    ortho = (di == 0) or (dj == 0)
                    candidates.append((i, j, H, ortho, abs(di) + abs(dj)))

    # prefer orthogonal neighbors first (form a line), then diagonal
    candidates.sort(key=lambda x: (not x[3], x[4]))
    print(f"  Candidates (orthogonal preferred): {[(c[0], c[1]) for c in candidates[:4]]}")

    if len(candidates) >= 2:
        chosen = candidates[:2]
        print(f"  [OK] Expand {name} to 3 cells: ({i0},{j0}) + "
              f"({chosen[0][0]},{chosen[0][1]}) + ({chosen[1][0]},{chosen[1][1]})")
    else:
        print(f"  [WARN] Only {len(candidates)} neighbor water cells - cannot expand to 3")

# Also check ZYH (3 cells) - consider expanding to 5
print(f"\n[ZYH] current 3 cells, H~12.3m (deep water)")
print(f"  Positions: (10,20), (8,18), (9,19)")
zyh_cells = [(10, 20), (8, 18), (9, 19)]
# find neighbors not already in ZYH
additional = []
for (i0, j0) in zyh_cells:
    for dj in [-1, 0, 1]:
        for di in [-1, 0, 1]:
            i, j = i0 + di, j0 + dj
            if (i, j) in zyh_cells:
                continue
            if 1 <= i <= 52 and 1 <= j <= 46 and b[j-1, i-1] > 0:
                if (i, j) not in additional:
                    additional.append((i, j, b[j-1, i-1]))
print(f"  Additional water neighbors: {additional[:6]}")
print(f"  [INFO] ZYH already has 3 cells; expansion to 5 optional")

# XYH already 3 cells - report only
print(f"\n[XYH] current 3 cells at (43,33),(44,33),(45,33), H~2.9m")
print(f"  [OK] Already 3 cells, no expansion needed")
