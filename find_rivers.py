import numpy as np
from pathlib import Path
import netCDF4 as nc

BASE_DIR = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET')
INPUT_DIR = BASE_DIR / "Luomahu_inputs"
CASE_DIR = BASE_DIR / "luomahu_case"

with nc.Dataset(str(CASE_DIR / "bathymetry.nc")) as ds:
    bathy = ds.variables["bathymetry"][:]
    lon = ds.variables["lonc"][:]
    lat = ds.variables["latc"][:]
    x = ds.variables["x"][:]
    y = ds.variables["y"][:]
    ny, nx = bathy.shape

print(f"网格: nx={nx}, ny={ny}")

bdy_points = []
with open(INPUT_DIR / "骆马湖_边界.p2d", "r") as f:
    f.readline()
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            bdy_points.append((float(parts[0]), float(parts[1])))
bdy_points = np.array(bdy_points)

print(f"\n边界范围: X={bdy_points[:,0].min():.0f}~{bdy_points[:,0].max():.0f}")
print(f"边界范围: Y={bdy_points[:,1].min():.0f}~{bdy_points[:,1].max():.0f}")

def find_bdy_extremes():
    x_min_idx = np.argmin(bdy_points[:, 0])
    x_max_idx = np.argmax(bdy_points[:, 0])
    y_min_idx = np.argmin(bdy_points[:, 1])
    y_max_idx = np.argmax(bdy_points[:, 1])

    print(f"\n边界极值点:")
    print(f"  最西点: X={bdy_points[x_min_idx,0]:.0f}, Y={bdy_points[x_min_idx,1]:.0f} (idx={x_min_idx})")
    print(f"  最东点: X={bdy_points[x_max_idx,0]:.0f}, Y={bdy_points[x_max_idx,1]:.0f} (idx={x_max_idx})")
    print(f"  最南点: X={bdy_points[y_min_idx,0]:.0f}, Y={bdy_points[y_min_idx,1]:.0f} (idx={y_min_idx})")
    print(f"  最北点: X={bdy_points[y_max_idx,0]:.0f}, Y={bdy_points[y_max_idx,1]:.0f} (idx={y_max_idx})")

    return x_min_idx, x_max_idx, y_min_idx, y_max_idx

x_min_idx, x_max_idx, y_min_idx, y_max_idx = find_bdy_extremes()

def find_nearest_water(target_x, target_y):
    X, Y = np.meshgrid(x, y)
    distances = np.sqrt((X - target_x)**2 + (Y - target_y)**2)
    mask = bathy > 0
    if not np.any(mask):
        return None, None
    dist_masked = np.where(mask, distances, np.inf)
    idx = np.unravel_index(np.argmin(dist_masked), dist_masked.shape)
    return idx[0], idx[1]

rivers_info = [
    ("京杭大运河", "西侧偏北",  bdy_points[x_min_idx, 0] + 1000,  bdy_points[x_min_idx, 1] + 2000),
    ("沂河", "北侧偏西",  bdy_points[y_max_idx, 0] - 3000,  bdy_points[y_max_idx, 1] - 500),
    ("骆南中运河", "南侧偏西",  bdy_points[y_min_idx, 0] - 2000,  bdy_points[y_min_idx, 1] + 500),
    ("嶂山闸/新沂河", "东南侧",  bdy_points[x_max_idx, 0] - 1000,  bdy_points[y_min_idx, 1] + 5000),
    ("杨河滩/总六塘河", "东侧偏北",  bdy_points[x_max_idx, 0] - 500,  bdy_points[y_max_idx, 1] - 3000),
]

print(f"\n河道位置:")
for name, desc, tx, ty in rivers_info:
    j, i = find_nearest_water(tx, ty)
    print(f"  {name} ({desc}): 目标点X={tx:.0f}, Y={ty:.0f} → 网格 i={i}, j={j}")
    if j is not None:
        print(f"    水深: {bathy[j, i]:.2f} m, lon={lon[j,i]:.3f}°, lat={lat[j,i]:.3f}°")
