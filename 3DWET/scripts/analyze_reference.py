"""Analyze reference image to identify river positions."""
from PIL import Image
import numpy as np
import os

INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case", "inputs")

# Open the EFDC grid reference image
img_path = os.path.join(INPUTS_DIR, "骆马湖EFDC网格、出入流及底部高程示意.png")
img = Image.open(img_path)
print(f"Image size: {img.size}")
print(f"Image mode: {img.mode}")

# Convert to RGB array
arr = np.array(img.convert('RGB'))
print(f"Array shape: {arr.shape}")

# Find unique colors (downsample for speed)
small = img.resize((100, 100)).convert('RGB')
small_arr = np.array(small)
colors = {}
for y in range(small_arr.shape[0]):
    for x in range(small_arr.shape[1]):
        r, g, b = tuple(small_arr[y, x])
        # Quantize to 32 levels
        key = (r//32, g//32, b//32)
        colors[key] = colors.get(key, 0) + 1

print("\nTop 20 colors (quantized):")
for color, count in sorted(colors.items(), key=lambda x: -x[1])[:20]:
    r, g, b = color[0]*32, color[1]*32, color[2]*32
    print(f"  RGB({r},{g},{b}): {count} pixels")

# Look for text annotations - check for red pixels (often used for river labels)
full_arr = np.array(img.convert('RGB'))
red_mask = (full_arr[:,:,0] > 150) & (full_arr[:,:,1] < 100) & (full_arr[:,:,2] < 100)
print(f"\nRed pixels (potential river labels): {red_mask.sum()}")
if red_mask.sum() > 0:
    rows, cols = np.where(red_mask)
    print(f"  Red pixel locations: rows {rows.min()}-{rows.max()}, cols {cols.min()}-{cols.max()}")
    # Cluster red pixels
    from scipy.ndimage import label
    labeled, n_features = label(red_mask)
    print(f"  Red clusters: {n_features}")
    for i in range(1, min(n_features+1, 20)):
        cluster_pixels = (labeled == i)
        if cluster_pixels.sum() > 10:
            r, c = np.where(cluster_pixels)
            print(f"    Cluster {i}: {cluster_pixels.sum()} pixels, "
                  f"center=({c.mean():.0f}, {r.mean():.0f}), "
                  f"range rows {r.min()}-{r.max()}, cols {c.min()}-{c.max()}")

# Look for blue pixels (water/river lines)
blue_mask = (full_arr[:,:,2] > 150) & (full_arr[:,:,0] < 100) & (full_arr[:,:,1] < 150)
print(f"\nBlue pixels: {blue_mask.sum()}")
if blue_mask.sum() > 0:
    rows, cols = np.where(blue_mask)
    print(f"  Blue pixel locations: rows {rows.min()}-{rows.max()}, cols {cols.min()}-{cols.max()}")

# Look for green pixels (river arrows)
green_mask = (full_arr[:,:,1] > 150) & (full_arr[:,:,0] < 150) & (full_arr[:,:,2] < 150)
print(f"\nGreen pixels: {green_mask.sum()}")
if green_mask.sum() > 0:
    rows, cols = np.where(green_mask)
    print(f"  Green pixel locations: rows {rows.min()}-{rows.max()}, cols {cols.min()}-{cols.max()}")

# Save a downscaled version for reference
img.thumbnail((400, 400))
img.save(os.path.join(INPUTS_DIR, "reference_small.png"))
print(f"\nSaved small reference to reference_small.png")
