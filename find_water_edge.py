import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

nc = netCDF4.Dataset('bathymetry.nc')
h = np.array(nc['bathymetry'][:])
lonc = nc['lonc'][:]
latc = nc['latc'][:]

print('Bathymetry shape:', h.shape)
print('lonc shape:', lonc.shape)
print('latc shape:', latc.shape)

# Find water cells (positive depth = actual depth, negative/masked = land)
# -10.0 appears to be the land marker
water_mask = (h > 0)  # Water cells are positive
print('\nTotal water cells:', water_mask.sum())
print('Water depth range:', h[water_mask].min(), 'to', h[water_mask].max())

# Find water cell positions
water_positions = np.where(water_mask)
print('\nWater cell ranges:')
print('  j (row):', water_positions[0].min()+1, 'to', water_positions[0].max()+1)
print('  i (col):', water_positions[1].min()+1, 'to', water_positions[1].max()+1)

# Find edges (where water meets land)
print('\n=== Water cell distribution by row (j) ===')
for j in range(54):
    row_water = (h[j, :] > 0).sum()
    if row_water > 0:
        j_water_cells = np.where(h[j, :] > 0)[0]
        print(f'j={j+1:2d}: water cells i={j_water_cells.min()+1}-{j_water_cells.max()+1} ({row_water} cells), depth range={h[j, j_water_cells].min():.1f}-{h[j, j_water_cells].max():.1f}m')

# For each river, find nearest water cell
print('\n=== Suggested river positions ===')
rivers = {
    'DAYUN': {'j': 35, 'i': 5, 'type': 'inflow'},    # Need to find correct position
    'YIHE': {'j': 49, 'i': 12, 'type': 'inflow'},
    'LUONAN': {'j': 3, 'i': 23, 'type': 'inflow'},
    'ZHANGSHAN': {'j': 13, 'i': 35, 'type': 'outflow'},
    'YANGHE': {'j': 26, 'i': 39, 'type': 'outflow'},
    'ERHE': {'j': None, 'i': None, 'type': 'outflow'}  # Need to add
}

# Find water edge near DAYUN (j=35, i=5 was land)
# Based on row 35, water starts at i=6
print('\nDAYUN: row j=35 has water from i=6-30')
print('  Suggested: j=35, i=6 (deep water entry point) or j=35, i=10 (mid-lake)')
print('  Need to check if river enters from south edge of lake')

# Check j=28-34 for potential DAYUN entry
print('\nRows 28-34 (potential DAYUN entry from west/south):')
for j in range(27, 35):
    if h[j, :].max() > 0:
        j_water_cells = np.where(h[j, :] > 0)[0]
        if len(j_water_cells) > 0:
            print(f'  j={j+1}: water from i={j_water_cells.min()+1} to i={j_water_cells.max()+1}, depth={h[j, j_water_cells].max():.1f}m')

# For YIHE at (49,12) - check row 49
print('\nRow 49 (YIHE):')
j = 48
j_water_cells = np.where(h[j, :] > 0)[0]
if len(j_water_cells) > 0:
    print(f'  Water from i={j_water_cells.min()+1} to i={j_water_cells.max()+1}')
    print(f'  At i=12 (0-indexed 11): depth={h[j,11]:.1f}m')

# For LUONAN at (3,23)
print('\nRow 3 (LUONAN):')
j = 2
j_water_cells = np.where(h[j, :] > 0)[0]
if len(j_water_cells) > 0:
    print(f'  Water from i={j_water_cells.min()+1} to i={j_water_cells.max()+1}')
    if 22 < len(h[j,:]):
        print(f'  At i=23 (0-indexed 22): depth={h[j,22]:.1f}m')

# Check longitude/latitude at each river location
print('\n=== Longitude/Latitude at suggested positions ===')
print('Lake extent from lonc/latc:')
valid_lonc = lonc[~lonc.mask] if np.ma.is_masked(lonc) else lonc.flatten()
valid_latc = latc[~latc.mask] if np.ma.is_masked(latc) else latc.flatten()
if len(valid_lonc) > 0:
    print(f'  Longitude: {valid_lonc.min():.3f} to {valid_lonc.max():.3f} deg E')
if len(valid_latc) > 0:
    print(f'  Latitude: {valid_latc.min():.3f} to {valid_latc.max():.3f} deg N')