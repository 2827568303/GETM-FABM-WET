"""Analyze the TIF bathymetry file to understand lake shape and river positions.

Reads the GeoTIFF and visualizes it as a text-based map to identify:
- Lake outline
- River channels (deep areas connecting to lake edges)
- Shallow/deep areas
"""
import numpy as np
import rasterio
import os

INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case", "inputs")
tif_path = os.path.join(INPUTS_DIR, "骆马湖-底部高程处理-Zhongzhao_Duan.tif")

print(f"Opening: {tif_path}")
with rasterio.open(tif_path) as src:
    data = src.read(1)
    print(f"  Shape: {data.shape}")
    print(f"  CRS: {src.crs}")
    print(f"  Bounds: {src.bounds}")
    print(f"  Transform: {src.transform}")
    print(f"  Nodata: {src.nodata}")
    if src.nodata is not None:
        data = np.where(data == src.nodata, np.nan, data)
    print(f"  Data range: {np.nanmin(data):.2f} to {np.nanmax(data):.2f}")
    print(f"  Mean: {np.nanmean(data):.2f}")
    gt = list(src.transform)
    x_size = src.width
    y_size = src.height

print(f"\nCoordinate range:")
print(f"  X: {gt[0]:.1f} to {gt[0] + gt[1]*x_size:.1f}")
print(f"  Y: {gt[3] + gt[5]*y_size:.1f} to {gt[3]:.1f}")

print(f"  Data range: {np.nanmin(data):.2f} to {np.nanmax(data):.2f}")
print(f"  Mean: {np.nanmean(data):.2f}")

# Create a text-based map
print("\n" + "=" * 80)
print("Text-based elevation map")
print("=" * 80)
print("Legend: # = NaN/land, . = high (>25m), o = mid (20-25m),")
print("        - = low (15-20m), ~ = water bottom (<15m), @ = deep (<10m)")

# Downsample
target_rows, target_cols = 50, 80
row_step = max(1, data.shape[0] // target_rows)
col_step = max(1, data.shape[1] // target_cols)
small = data[::row_step, ::col_step]

for row in range(small.shape[0]):
    line = ""
    for col in range(small.shape[1]):
        v = small[row, col]
        if np.isnan(v):
            line += "#"
        elif v < 10:
            line += "@"
        elif v < 15:
            line += "~"
        elif v < 20:
            line += "-"
        elif v < 25:
            line += "o"
        else:
            line += "."
    print(line)

# Find the lowest elevation points (deepest water)
print(f"\nLowest elevation points (deepest water):")
flat_idx = np.argsort(data.ravel())[:20]
for idx in flat_idx:
    r, c = np.unravel_index(idx, data.shape)
    x_coord = gt[0] + c * gt[1]
    y_coord = gt[3] + r * gt[5]
    print(f"  row={r}, col={c}, X={x_coord:.1f}, Y={y_coord:.1f}, elev={data[r,c]:.2f}")
