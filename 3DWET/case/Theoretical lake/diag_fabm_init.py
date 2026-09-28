"""Diagnose fabm_init.nc structure for 4D/3D mismatch."""
import netCDF4 as nc
import sys

fpath = sys.argv[1] if len(sys.argv) > 1 else 'fabm_init.nc'
ds = nc.Dataset(fpath)

print('=== Dimensions ===')
for k, v in ds.dimensions.items():
    print(f'  {k}: {len(v)}')

print('\n=== Variables (first 30) ===')
for i, (name, var) in enumerate(ds.variables.items()):
    if i >= 30:
        break
    print(f'  {name}: dims={var.dimensions}, shape={var.shape}')

print(f'\nTotal variables: {len(ds.variables)}')

# Check specifically for 4D vs 3D
print('\n=== Dimensionality check ===')
n3d = n4d = nother = 0
for name, var in ds.variables.items():
    nd = len(var.dimensions)
    if nd == 3:
        n3d += 1
    elif nd == 4:
        n4d += 1
    else:
        nother += 1
print(f'  3D vars: {n3d}, 4D vars: {n4d}, other: {nother}')

ds.close()
