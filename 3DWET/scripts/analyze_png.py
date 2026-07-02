"""Find river marker centroids in reference PNG."""
import numpy as np
from PIL import Image
from scipy import ndimage
import os

PNG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "case", "inputs", "骆马湖EFDC网格、出入流及底部高程示意.png"
)

img = Image.open(PNG_PATH)
arr = np.array(img)
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# Find colored regions
red_mask = (r > 200) & (g < 100) & (b < 100)
blue_mask = (r < 100) & (g < 100) & (b > 200)
green_mask = (r < 100) & (g > 200) & (b < 100)

# Label connected components
for name, mask in [("RED (inflow)", red_mask), ("BLUE (outflow)", blue_mask), ("GREEN", green_mask)]:
    labeled, num = ndimage.label(mask)
    print(f"\n{name}: {num} regions, {np.sum(mask)} pixels total")
    if num > 0:
        for i in range(1, num + 1):
            region = (labeled == i)
            size = np.sum(region)
            if size > 20:  # Filter small noise
                ys, xs = np.where(region)
                cy, cx = ys.mean(), xs.mean()
                print(f"  Region {i}: {size} pixels, centroid=({cy:.0f}, {cx:.0f}), bbox=({ys.min()}-{ys.max()}, {xs.min()}-{xs.max()})")

# Also find black text (river names)
black_mask = (r < 50) & (g < 50) & (b < 50)
print(f"\nBlack pixels (text?): {np.sum(black_mask)}")
labeled, num = ndimage.label(black_mask)
if num > 0:
    for i in range(1, num + 1):
        region = (labeled == i)
        size = np.sum(region)
        if size > 50:
            ys, xs = np.where(region)
            cy, cx = ys.mean(), xs.mean()
            print(f"  Text region {i}: {size} pixels, centroid=({cy:.0f}, {cx:.0f})")

# Image dimensions for reference
print(f"\nImage size: {img.size} (W x H)")
print(f"Image array: {arr.shape} (H x W x C)")
