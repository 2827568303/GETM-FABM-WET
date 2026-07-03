"""Diagnose bathymetry differences between EFDC trans (diverges) and Lake Luoma (stable)."""
import numpy as np
import netCDF4 as nc

CASE_DIR = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"
REF_DIR  = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma"
LAND = -10.0

def load_bathy(path):
    ds = nc.Dataset(path)
    H = ds.variables['bathymetry'][:]
    ds.close()
    return np.array(H)

# Load
H_efdc = load_bathy(CASE_DIR + r"\bathymetry.nc")
H_luoma = load_bathy(REF_DIR + r"\bathymetry.nc")

print("="*70)
print("EFDC trans bathymetry:")
print(f"  shape = {H_efdc.shape}, water cells = {(H_efdc > 0).sum()}")
print(f"  depth range: {H_efdc[H_efdc>0].min():.2f} - {H_efdc[H_efdc>0].max():.2f} m")
print("Lake Luoma bathymetry:")
print(f"  shape = {H_luoma.shape}, water cells = {(H_luoma > 0).sum()}")
print(f"  depth range: {H_luoma[H_luoma>0].min():.2f} - {H_luoma[H_luoma>0].max():.2f} m")

# Divergence region in EFDC trans: i=12-13, j=21-22 (1-based)
# In Python 0-based: i_idx = 11-12, j_idx = 20-21
print("\n" + "="*70)
print("EFDC trans - region around divergence (i=9-16, j=18-24):")
print("     ", "  ".join(f"i={i:2d}" for i in range(9, 17)))
for j in range(18, 25):
    row = []
    for i in range(9, 17):
        v = H_efdc[j-1, i-1]
        if v <= 0:
            row.append("LND ")
        else:
            row.append(f"{v:4.1f}")
    print(f"j={j:2d}: ", " ".join(row))

# Compute gradients
def grad_stats(H, label):
    Hm = H.copy().astype(float)
    land = Hm <= 0
    Hm[land] = np.nan
    # forward difference in i and j
    gx = np.diff(Hm, axis=1)
    gy = np.diff(Hm, axis=0)
    print(f"\n{label}:")
    print(f"  |grad_x|: max = {np.nanmax(np.abs(gx)):.3f}, mean = {np.nanmean(np.abs(gx)):.3f}")
    print(f"  |grad_y|: max = {np.nanmax(np.abs(gy)):.3f}, mean = {np.nanmean(np.abs(gy)):.3f}")
    # ratio of max depth to min depth in any 3x3 window
    print(f"  H range in 3x3 windows:")
    max_ratio = 0
    worst = None
    for j in range(1, Hm.shape[0]-1):
        for i in range(1, Hm.shape[1]-1):
            win = Hm[j-1:j+2, i-1:i+2]
            win_w = win[~np.isnan(win)]
            if len(win_w) >= 4:
                ratio = win_w.max() / win_w.min()
                if ratio > max_ratio:
                    max_ratio = ratio
                    worst = (i+1, j+1, win_w.min(), win_w.max())
    print(f"    max H_max/H_min in any 3x3 = {max_ratio:.2f} at (i={worst[0]},j={worst[1]}): "
          f"H_min={worst[2]:.2f} H_max={worst[3]:.2f}")

grad_stats(H_efdc, "EFDC trans")
grad_stats(H_luoma, "Lake Luoma")

# Depth distribution histogram
print("\n" + "="*70)
print("Depth distribution (water cells only):")
for label, H in [("EFDC trans", H_efdc), ("Lake Luoma", H_luoma)]:
    d = H[H > 0]
    print(f"\n{label}:")
    bins = [0, 1, 2, 3, 5, 7, 10, 12, 14, 16, 20, 100]
    for k in range(len(bins)-1):
        n = ((d >= bins[k]) & (d < bins[k+1])).sum()
        if n > 0:
            print(f"  {bins[k]:3d}-{bins[k+1]:3d} m: {n:5d}")

# Check land-water boundary patterns
print("\n" + "="*70)
print("Land-water interface analysis:")
def boundary_analysis(H, label):
    Hm = H.copy().astype(float)
    land = Hm <= 0
    # Count number of land neighbors for each water cell
    nbrs = np.zeros_like(Hm, dtype=int)
    for dj in [-1, 0, 1]:
        for di in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            shifted = np.roll(np.roll(land, -di, axis=1), -dj, axis=0)
            nbrs += shifted.astype(int)
    # only for water cells
    water_nbrs = nbrs[~land]
    print(f"\n{label}:")
    print(f"  Water cells with land neighbors: {(water_nbrs > 0).sum()} / {(~land).sum()}")
    print(f"  Land-neighbor count distribution:")
    for n in range(9):
        cnt = (water_nbrs == n).sum()
        if cnt > 0:
            print(f"    {n} land nbrs: {cnt}")
    # Cells with most land neighbors (potential issue points)
    max_nbrs = water_nbrs.max()
    worst = np.where(nbrs == max_nbrs)
    if len(worst[0]) > 0:
        print(f"  Max land nbrs = {max_nbrs} at e.g. (i={worst[1][0]+1}, j={worst[0][0]+1})")

boundary_analysis(H_efdc, "EFDC trans")
boundary_analysis(H_luoma, "Lake Luoma")
