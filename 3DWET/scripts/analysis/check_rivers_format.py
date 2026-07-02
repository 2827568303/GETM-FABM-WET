import netCDF4
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

print("=== rivers_fixed.nc ===")
nc = netCDF4.Dataset('rivers_fixed.nc', 'r')
print('Dimensions:', dict(nc.dimensions))
print('Variables:', list(nc.variables.keys()))
# Check first variable's dimensions
for var in ['DAYUN', 'LUONAN', 'YIHE', 'ZHANGSHAN', 'YANGHE']:
    if var in nc.variables:
        print(f'{var}: dims={nc.variables[var].dimensions}, shape={nc.variables[var].shape}')
nc.close()

print("\n=== rivers.nc (our generated) ===")
nc = netCDF4.Dataset('rivers.nc', 'r')
print('Dimensions:', dict(nc.dimensions))
print('Variables:', list(nc.variables.keys()))
for var in ['DAYUN', 'LUONAN', 'YIHE', 'ZHANGSHAN', 'YANGHE', 'ERHE']:
    if var in nc.variables:
        print(f'{var}: dims={nc.variables[var].dimensions}, shape={nc.variables[var].shape}')
nc.close()

# Check ERHE data
print("\n=== ERHE data in rivers.nc ===")
nc = netCDF4.Dataset('rivers.nc', 'r')
print('ERHE values:', nc['ERHE'][:])
nc.close()