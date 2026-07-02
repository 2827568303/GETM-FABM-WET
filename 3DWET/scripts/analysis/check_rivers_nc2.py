import netCDF4
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

nc = netCDF4.Dataset('rivers.nc')
print('Variables in rivers.nc:')
for var in nc.variables:
    print(f'  {var}')

print('\nDimensions:', dict(nc.dimensions))

# Check if ERHE exists
if 'ERHE' in nc.variables or 'ERHE_discharge' in nc.variables:
    print('\nERHE data exists')
else:
    print('\nWARNING: ERHE NOT found in rivers.nc')
    print('Need to add ERHE river to rivers.nc')

# Check rivers in nc
rivers_in_nc = [v for v in nc.variables if not v.startswith('time') and '_' not in v]
print('\nRivers in nc:', rivers_in_nc)

# What we expect
expected = ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE', 'ERHE']
print('Expected rivers:', expected)