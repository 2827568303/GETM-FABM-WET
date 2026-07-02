import netCDF4 as nc
ds = nc.Dataset('case/bathymetry.nc')
print('Vars:', list(ds.variables.keys()))
print('Dims:', list(ds.dimensions.keys()))
for v in ds.variables:
    var = ds.variables[v]
    print(f'  {v}: dims={var.dimensions}, shape={var.shape}')
ds.close()
