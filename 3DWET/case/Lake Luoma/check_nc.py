import sys
import netCDF4

path = sys.argv[1] if len(sys.argv) > 1 else 'output.nc'
nc = netCDF4.Dataset(path)
print(f'File: {path}')
print(f'Dimensions: {dict((k, len(v)) for k, v in nc.dimensions.items())}')
print(f'Num variables: {len(nc.variables)}')
print('\nFirst 20 variables:')
for v in list(nc.variables.keys())[:20]:
    var = nc.variables[v]
    print(f'  {v}: dims={var.dimensions}, shape={var.shape}')
print('\nLast 10 variables:')
for v in list(nc.variables.keys())[-10:]:
    var = nc.variables[v]
    print(f'  {v}: dims={var.dimensions}, shape={var.shape}')
nc.close()
