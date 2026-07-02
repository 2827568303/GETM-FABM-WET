import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Try to open rivers.nc directly
try:
    nc = netCDF4.Dataset('rivers.nc', 'r')
    print('Opened rivers.nc')
    print('Variables:', list(nc.variables.keys()))
    print('Dimensions:', dict(nc.dimensions))
    
    time_data = nc['time'][:]
    time_units = nc['time'].units
    n_time = len(time_data)
    print(f'Time steps: {n_time}')
    
    # Read all existing river data
    rivers = {}
    for var in nc.variables:
        if var != 'time':
            rivers[var] = nc[var][:]
            print(f'  Read {var}: shape={nc[var].shape}')
    
    nc.close()
    
    # Add ERHE (outflow, set to 0 since no data)
    rivers['ERHE'] = np.zeros(n_time)
    rivers['ERHE_ammonium'] = np.zeros(n_time)
    rivers['ERHE_nitrate'] = np.zeros(n_time)
    rivers['ERHE_phosphate'] = np.zeros(n_time)
    rivers['ERHE_POM_sNW'] = np.zeros(n_time)
    
    print(f'\nAdded ERHE river with zeros')
    
    # Create new file
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
    
    print('Created new rivers.nc with all rivers')
    print('\nRivers now in file:')
    nc = netCDF4.Dataset('rivers.nc', 'r')
    for var in nc.variables:
        print(f'  {var}')
    nc.close()
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()