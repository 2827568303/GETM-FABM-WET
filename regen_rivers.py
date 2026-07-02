import netCDF4
import numpy as np
import os
import shutil

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Use rivers_fixed.nc as source
nc_src = netCDF4.Dataset('rivers_fixed.nc', 'r')
print('Source: rivers_fixed.nc')
print('Variables:', list(nc_src.variables.keys()))

time_data = nc_src['time'][:]
time_units = nc_src['time'].units
n_time = len(time_data)
print(f'Time steps: {n_time}')

# Read all existing river data
rivers = {}
for var in nc_src.variables:
    if var != 'time':
        rivers[var] = nc_src[var][:]
        print(f'  Read {var}: shape={nc_src[var].shape}')

nc_src.close()

# Add ERHE (outflow, set to 0 since no data)
rivers['ERHE'] = np.zeros(n_time)
rivers['ERHE_ammonium'] = np.zeros(n_time)
rivers['ERHE_nitrate'] = np.zeros(n_time)
rivers['ERHE_phosphate'] = np.zeros(n_time)
rivers['ERHE_POM_sNW'] = np.zeros(n_time)

print(f'\nAdded ERHE river with zeros')

# Create new rivers.nc
if os.path.exists('rivers.nc'):
    os.remove('rivers.nc')

nc_new = netCDF4.Dataset('rivers.nc', 'w')

# Create time dimension
time_dim = nc_new.createDimension('time', n_time)

# Create time variable
time_var = nc_new.createVariable('time', 'f8', ('time',))
time_var.units = time_units
time_var[:] = time_data

# Create river variables
for var_name, data in rivers.items():
    var = nc_new.createVariable(var_name, 'f4', ('time',))
    var[:] = data

nc_new.close()

print('Created new rivers.nc with all 6 rivers')
print('\nRivers now in file:')
nc = netCDF4.Dataset('rivers.nc', 'r')
for var in nc.variables:
    print(f'  {var}')
nc.close()