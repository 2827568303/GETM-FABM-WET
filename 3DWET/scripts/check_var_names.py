import netCDF4 as nc

# Check output file variable names for macrophytes
ds = nc.Dataset('case/LUOMAHU_WET.3d.nc')
macro_vars = [v for v in ds.variables if 'macro' in v.lower()]
print("Macrophyte variables in output file:")
for v in macro_vars:
    var = ds.variables[v]
    print(f"  {v}: dims={var.dimensions}, shape={var.shape}")
ds.close()

# Check init file
print("\nVariables in fabm_init.nc:")
ds2 = nc.Dataset('case/fabm_init.nc')
for v in ds2.variables:
    var = ds2.variables[v]
    print(f"  {v}: dims={var.dimensions}, shape={var.shape}")
ds2.close()
