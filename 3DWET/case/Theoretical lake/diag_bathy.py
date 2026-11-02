"""Check bathymetry.nc for wet/dry cell distribution."""
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('bathymetry.nc')
bathy = ds.variables['bathymetry'][:]
bathy = np.ma.filled(bathy, 0.0)

print(f'Shape: {bathy.shape}')
print(f'Min: {bathy.min():.3f}, Max: {bathy.max():.3f}')
print(f'Cells with depth > 0: {(bathy > 0).sum()}')
print(f'Cells with depth > 0.3 (crit_depth): {(bathy > 0.3).sum()}')
print(f'Cells with depth = 0: {(bathy == 0).sum()}')
print(f'Total cells: {bathy.size}')

# Show the mask pattern
mask = bathy > 0
print('\nWet/dry pattern (W=wet, .=dry):')
for j in range(bathy.shape[0]):
    row = ''
    for i in range(bathy.shape[1]):
        row += 'W' if mask[j, i] else '.'
    print(f'  j={j:2d}: {row}')

ds.close()
