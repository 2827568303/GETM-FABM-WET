"""Generate fabm_init.nc with spatial initial conditions for macrophytes.

Macrophytes grow only in the littoral zone (~10% of lake area).
- Littoral zone = shallow water near shore (depth < threshold)
- Threshold is chosen so that ~10% of water cells have macrophytes
- Deep water cells get 0 (or minimum value)
- Other FABM variables are NOT included -> GETM uses fabm.yaml uniform values

GETM-FABM reads this when fabm_init_method=2 in getm_fabm.inp.
Variable names must match model%bottom_state_variables(n)%name (full name with prefix).
"""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

# Read bathymetry
bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
bathymetry = bathy_ds.variables['bathymetry'][:]
x = bathy_ds.variables['x'][:]
y = bathy_ds.variables['y'][:]
lonc = bathy_ds.variables['lonc'][:]
latc = bathy_ds.variables['latc'][:]
bathy_ds.close()

ny, nx = bathymetry.shape
water_mask = bathymetry > 0
n_water = np.sum(water_mask)
print(f"Grid: {nx} x {ny}, water cells: {n_water}")

# Analyze depth distribution to find threshold for ~10% littoral zone
print("\nDepth distribution of water cells:")
depths = bathymetry[water_mask]
for pct in [5, 10, 15, 20, 25, 30]:
    threshold = np.percentile(depths, pct)
    n_littoral = np.sum((bathymetry > 0) & (bathymetry <= threshold))
    print(f"  {pct}% percentile: depth <= {threshold:.2f}m -> {n_littoral} cells ({100*n_littoral/n_water:.1f}%)")

# Also check specific depth thresholds
print("\nDepth threshold analysis:")
for threshold in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]:
    n_littoral = np.sum((bathymetry > 0) & (bathymetry <= threshold))
    pct = 100 * n_littoral / n_water
    print(f"  depth <= {threshold:.1f}m: {n_littoral} cells ({pct:.1f}%)")

# Choose threshold for ~10% coverage
# Macrophytes typically grow in < 2-3m depth. Adjust threshold to get ~10%.
target_pct = 10.0
# Find threshold that gives closest to 10%
best_threshold = None
best_diff = 999
for threshold in np.arange(0.5, 6.0, 0.1):
    n_littoral = np.sum((bathymetry > 0) & (bathymetry <= threshold))
    pct = 100 * n_littoral / n_water
    diff = abs(pct - target_pct)
    if diff < best_diff:
        best_diff = diff
        best_threshold = threshold

print(f"\nChosen threshold: {best_threshold:.1f}m (gives {100*np.sum((bathymetry > 0) & (bathymetry <= best_threshold))/n_water:.1f}% coverage)")

# But macrophytes should be near the SHORE, not just shallow.
# A cell is "littoral" if it's shallow AND near the shore edge.
# Shore edge = water cell adjacent to land
land_mask = ~water_mask
# Find water cells adjacent to land
shore_edge = np.zeros_like(bathymetry, dtype=bool)
for j in range(ny):
    for i in range(nx):
        if water_mask[j, i]:
            # Check 4 neighbors
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                jj, ii = j + dj, i + di
                if 0 <= jj < ny and 0 <= ii < nx:
                    if land_mask[jj, ii]:
                        shore_edge[j, i] = True
                        break

n_shore = np.sum(shore_edge)
print(f"Shore edge cells: {n_shore} ({100*n_shore/n_water:.1f}%)")

# Macrophyte zone = shallow AND near shore (within 1-2 cells of shore)
# Use distance from shore (dilation) + depth threshold
from scipy.ndimage import binary_dilation, distance_transform_edt
# Distance from land (number of cells from shore)
dist_from_land = distance_transform_edt(water_mask)

# Macrophyte suitable: depth <= threshold AND within 2 cells of shore
macro_zone = water_mask & (bathymetry <= best_threshold) & (dist_from_land <= 3)
n_macro = np.sum(macro_zone)
pct_macro = 100 * n_macro / n_water
print(f"\nMacrophyte zone (depth<={best_threshold:.1f}m, dist<=3 cells): {n_macro} cells ({pct_macro:.1f}%)")

# If too few, relax distance constraint
if pct_macro < 8:
    macro_zone = water_mask & (bathymetry <= best_threshold) & (dist_from_land <= 5)
    n_macro = np.sum(macro_zone)
    pct_macro = 100 * n_macro / n_water
    print(f"Relaxed to dist<=5: {n_macro} cells ({pct_macro:.1f}%)")

# If still too few or too many, adjust
if pct_macro < 8:
    # Just use depth threshold alone
    macro_zone = water_mask & (bathymetry <= best_threshold)
    n_macro = np.sum(macro_zone)
    pct_macro = 100 * n_macro / n_water
    print(f"Using depth threshold only: {n_macro} cells ({pct_macro:.1f}%)")

print(f"\nFinal macrophyte zone: {n_macro} cells ({pct_macro:.1f}% of lake)")

# Create macrophyte initial fields
# sD: 30 gDW/m2 in macrophyte zone, 0 elsewhere
# (30 gDW/m2 is a reasonable biomass for established macrophyte beds)
macro_sD = np.where(macro_zone, 30.0, 0.0)
macro_sN = macro_sD * 0.02   # cNDVeg0 = 0.02
macro_sP = macro_sD * 0.002  # cPDVeg0 = 0.002
macro_sC = macro_sD * 0.4    # cCPerDW = 0.4

# Pelagic variants (same as benthic for initialization)
macro_sD_PV = macro_sD.copy()
macro_sN_PV = macro_sN.copy()
macro_sP_PV = macro_sP.copy()
macro_sC_PV = macro_sC.copy()

# Write fabm_init.nc
init_path = os.path.join(CASE_DIR, "fabm_init.nc")
print(f"\nWriting {init_path}...")

ds = nc.Dataset(init_path, "w", format="NETCDF3_CLASSIC")

# Dimensions - GETM expects (y, x) for 2D fields
ds.createDimension("x", nx)
ds.createDimension("y", ny)
ds.createDimension("time", None)  # unlimited

# Coordinate variables (GETM may need these)
x_var = ds.createVariable("x", "f8", ("x",))
x_var[:] = x
y_var = ds.createVariable("y", "f8", ("y",))
y_var[:] = y

# Grid mapping - lonc, latc
lonc_var = ds.createVariable("lonc", "f8", ("y", "x"))
lonc_var[:] = np.ma.filled(lonc, 0.0)
latc_var = ds.createVariable("latc", "f8", ("y", "x"))
latc_var[:] = np.ma.filled(latc, 0.0)

# Time variable
time_var = ds.createVariable("time", "f8", ("time",))
time_var.units = "seconds since 2020-01-01 00:00:00"
time_var[:] = [0.0]

# Macrophyte variables (2D: time, y, x) - names match FABM bottom state variable names
# FABM variable names include the instance prefix: macrophytes_sD, etc.
# Only include 2D bottom variables; _PV (3D pelagic) variants use YAML uniform values
for name, data, units, long_name in [
    ("macrophytes_sD", macro_sD, "gDW/m2", "macrophyte dry weight"),
    ("macrophytes_sN", macro_sN, "gN/m2", "macrophyte nitrogen"),
    ("macrophytes_sP", macro_sP, "gP/m2", "macrophyte phosphorus"),
    ("macrophytes_sC", macro_sC, "gC/m2", "macrophyte carbon"),
]:
    var = ds.createVariable(name, "f8", ("time", "y", "x"))
    var.units = units
    var.long_name = long_name
    var[0, :, :] = data
    print(f"  {name}: range [{data.min():.2f}, {data.max():.2f}] {units}")

ds.title = "FABM spatial initial conditions (macrophytes in littoral zone only)"
ds.source = "Generated by gen_fabm_init.py"
ds.history = f"Created {np.datetime64('now')}"
ds.close()
print("  Done!")

# Print summary
print(f"\n{'='*60}")
print("Summary:")
print(f"{'='*60}")
print(f"  Lake water cells: {n_water}")
print(f"  Macrophyte zone: {n_macro} cells ({pct_macro:.1f}%)")
print(f"  Depth threshold: {best_threshold:.1f}m")
print(f"  Macrophyte sD in zone: 30.0 gDW/m2")
print(f"  Macrophyte sD outside: 0.0 gDW/m2")
