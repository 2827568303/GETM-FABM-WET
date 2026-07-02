"""Analyze reference PNG to find river positions and map to grid.

The PNG shows the EFDC grid with colored markers:
- RED arrows/text: inflow rivers
- BLUE arrows/text: outflow rivers
- GREEN: may indicate other features

Strategy:
1. Find colored marker centroids in pixel coordinates
2. Find the grid extent in the image (by detecting grid lines or lake outline)
3. Map pixel coordinates to UTM coordinates
4. Map UTM to grid (i,j)
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import os
import netCDF4 as nc

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")

# Load PNG
PNG_PATH = os.path.join(INPUTS_DIR, "骆马湖EFDC网格、出入流及底部高程示意.png")
img = Image.open(PNG_PATH)
arr = np.array(img)
print(f"Image size: {img.size} (W x H)")
print(f"Array shape: {arr.shape}")

# Check if RGBA or RGB
if arr.shape[2] == 4:
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
else:
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    a = np.ones_like(r) * 255

# Find colored regions - use more specific color thresholds
# RED: inflow (r>180, g<100, b<100)
# BLUE: outflow (r<100, g<100, b>180)
# GREEN: (r<100, g>180, b<100)
# BLACK text/labels: (r<80, g<80, b<80)
# Also look for orange/yellow which might be used for bidirectional

red_mask = (r > 180) & (g < 120) & (b < 120) & (a > 100)
blue_mask = (r < 120) & (g < 120) & (b > 180) & (a > 100)
green_mask = (r < 120) & (g > 180) & (b < 120) & (a > 100)
black_mask = (r < 80) & (g < 80) & (b < 80) & (a > 100)

print(f"\nPixel counts:")
print(f"  RED (inflow): {np.sum(red_mask)}")
print(f"  BLUE (outflow): {np.sum(blue_mask)}")
print(f"  GREEN: {np.sum(green_mask)}")
print(f"  BLACK: {np.sum(black_mask)}")

# Find connected components for each color
print("\n" + "=" * 70)
print("Colored marker regions")
print("=" * 70)

for name, mask in [("RED", red_mask), ("BLUE", blue_mask), ("GREEN", green_mask)]:
    labeled, num = ndimage.label(mask)
    if num == 0:
        print(f"\n{name}: no regions")
        continue
    print(f"\n{name}: {num} regions")
    # Find centroids and sizes
    for i in range(1, num + 1):
        region = labeled == i
        size = np.sum(region)
        if size < 5:  # skip tiny regions
            continue
        ys, xs = np.where(region)
        cx, cy = np.mean(xs), np.mean(ys)
        print(f"  Region {i}: {size} pixels, centroid pixel=({cx:.0f}, {cy:.0f}), "
              f"x range=[{xs.min()}-{xs.max()}], y range=[{ys.min()}-{ys.max()}]")

# Now find the grid extent in the image
# The grid should be visible as a pattern of lines or the lake outline
# Let's find the lake boundary (non-white, non-black pixels = colored area)
print("\n" + "=" * 70)
print("Finding lake extent in image")
print("=" * 70)

# Lake area = colored pixels (not white, not black, not transparent)
non_white = ~((r > 240) & (g > 240) & (b > 240) & (a > 200))
non_transparent = a > 100
lake_area = non_white & non_transparent
# Remove black text
lake_area = lake_area & ~black_mask

ys, xs = np.where(lake_area)
if len(ys) > 0:
    print(f"Lake area pixels: {len(ys)}")
    print(f"  X pixel range: {xs.min()} to {xs.max()}")
    print(f"  Y pixel range: {ys.min()} to {ys.max()}")
    print(f"  Image size: {img.size}")

    # The lake UTM extent
    # From bathymetry: X: 599250-621250, Y: 3762250-3789250
    # But the actual water cells are: X: 599500-621000, Y: 3763000-3789000
    utm_x_min, utm_x_max = 599250.0, 621250.0
    utm_y_min, utm_y_max = 3762250.0, 3789250.0

    # Map pixel to UTM
    px_x_min, px_x_max = xs.min(), xs.max()
    px_y_min, px_y_max = ys.min(), ys.max()

    print(f"\nMapping pixel -> UTM:")
    print(f"  X: pixel [{px_x_min}-{px_x_max}] -> UTM [{utm_x_min}-{utm_x_max}]")
    print(f"  Y: pixel [{px_y_min}-{px_y_max}] -> UTM [{utm_y_max}-{utm_y_min}] (Y flipped)")

    def pixel_to_utm(px, py):
        """Convert pixel (px, py) to UTM (X, Y). Y is flipped."""
        x = utm_x_min + (px - px_x_min) / (px_x_max - px_x_min) * (utm_x_max - utm_x_min)
        y = utm_y_max - (py - px_y_min) / (px_y_max - px_y_min) * (utm_y_max - utm_y_min)
        return x, y

    def utm_to_grid(x, y):
        """Convert UTM to grid (i, j) 1-indexed."""
        i = (x - 599250.0) / 500.0 + 0.5  # cell center
        j = (y - 3762250.0) / 500.0 + 0.5
        return int(round(i)), int(round(j))

    # Map all colored markers to grid positions
    print("\n" + "=" * 70)
    print("River markers mapped to grid positions")
    print("=" * 70)

    # Load bathymetry for depth check
    ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
    bathy = ds.variables["bathymetry"][:]
    ds.close()

    for name, mask, river_type in [
        ("RED (inflow)", red_mask, "INFLOW"),
        ("BLUE (outflow)", blue_mask, "OUTFLOW"),
        ("GREEN", green_mask, "OTHER"),
    ]:
        labeled, num = ndimage.label(mask)
        if num == 0:
            continue
        print(f"\n{name}:")
        for i in range(1, num + 1):
            region = labeled == i
            size = np.sum(region)
            if size < 20:  # skip small regions
                continue
            ys_r, xs_r = np.where(region)
            cx, cy = np.mean(xs_r), np.mean(ys_r)
            utm_x, utm_y = pixel_to_utm(cx, cy)
            gi, gj = utm_to_grid(utm_x, utm_y)
            depth = bathy[gj - 1, gi - 1] if 1 <= gi <= 44 and 1 <= gj <= 54 else "N/A"
            print(f"  Region {i}: {size} px, pixel=({cx:.0f},{cy:.0f}) -> "
                  f"UTM=({utm_x:.0f},{utm_y:.0f}) -> grid=(i={gi}, j={gj}), depth={depth}")
else:
    print("No lake area found!")
