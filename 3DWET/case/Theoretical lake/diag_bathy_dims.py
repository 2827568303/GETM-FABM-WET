import netCDF4 as nc
import numpy as np

# Detailed check of bathymetry.nc dimensions
ds = nc.Dataset('bathymetry.nc')
print('=== INPUT bathymetry.nc ===')
print('Dimensions:')
for dname, d in ds.dimensions.items():
    print('  ' + dname + ': ' + str(len(d)))
print()
for vname in ['x', 'y', 'latc', 'lonc', 'bathymetry']:
    v = ds.variables[vname]
    print('  ' + vname + ': shape=' + str(v.shape) + ' dims=' + str(v.dimensions))
    if vname in ['x', 'y']:
        data = np.array(v[:])
        print('    range: ' + str(data[0]) + ' to ' + str(data[-1]))
        print('    len: ' + str(len(data)))
ds.close()

print()

# Check 2d.nc for ioff, joff
ds2d = nc.Dataset('THEORETICAL_LAKE.2d.nc')
print('=== OUTPUT 2d.nc ===')
for vname in ['ioff', 'joff', 'dx', 'dy', 'grid_type']:
    if vname in ds2d.variables:
        v = ds2d.variables[vname]
        print('  ' + vname + ': ' + str(np.array(v[:])))
print('  xc: ' + str(np.array(ds2d.variables['xc'][:])))
print('  yc: ' + str(np.array(ds2d.variables['yc'][:])))
ds2d.close()

print()

# Check ioff/joff meaning in GETM: they are the offset of the computed subdomain
# within the full bathymetry grid. If ioff=0, joff=0, the model starts from (0,0)
# and the grid size is limited by the compiled GRIDWI/GRIDWJ.

# Let me check the binary for compiled grid dimensions
import subprocess
result = subprocess.run(['strings', '../bin/getm_cartesian'], capture_output=True, text=True)
if result.returncode == 0:
    lines = result.stdout.split('\n')
    grid_lines = [l for l in lines if 'GRIDW' in l or 'gridwi' in l.lower() or 'gridwj' in l.lower()]
    print('=== Binary grid info ===')
    for l in grid_lines[:10]:
        print('  ' + l)
else:
    print('Could not run strings on binary')
