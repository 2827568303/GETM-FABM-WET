import netCDF4 as nc
import numpy as np

# Check input bathymetry.nc
ds = nc.Dataset('bathymetry.nc')
bathy = np.array(ds.variables['bathymetry'][:])
print('INPUT bathymetry.nc:')
print('  shape: ' + str(bathy.shape))
print('  wet cells: ' + str(np.sum(bathy > 0)))
if np.sum(bathy > 0) > 0:
    print('  depth range: ' + str(np.min(bathy[bathy > 0])) + ' to ' + str(np.max(bathy)))
print('  variables: ' + str(list(ds.variables.keys())))
ds.close()

print()

# Check 2d.nc grid
ds2d = nc.Dataset('THEORETICAL_LAKE.2d.nc')
bathy2d = np.array(ds2d.variables['bathymetry'][:])
print('OUTPUT 2d.nc:')
print('  bathymetry shape: ' + str(bathy2d.shape))
print('  wet cells: ' + str(np.sum(bathy2d > 0)))
if np.sum(bathy2d > 0) > 0:
    print('  depth range: ' + str(np.min(bathy2d[bathy2d > 0])) + ' to ' + str(np.max(bathy2d)))
print('  variables: ' + str(list(ds2d.variables.keys())))
print('  lonc shape: ' + str(np.array(ds2d.variables['lonc'][:]).shape))
print('  latc shape: ' + str(np.array(ds2d.variables['latc'][:]).shape))

# Check dimensions
print('  dimensions:')
for dname, d in ds2d.dimensions.items():
    print('    ' + dname + ': ' + str(len(d)))
ds2d.close()

print()

# Check 3d.nc grid
ds3d = nc.Dataset('THEORETICAL_LAKE.3d.nc')
print('OUTPUT 3d.nc:')
print('  dimensions:')
for dname, d in ds3d.dimensions.items():
    print('    ' + dname + ': ' + str(len(d)))
print('  variables (first 30): ' + str(list(ds3d.variables.keys())[:30]))
ds3d.close()
