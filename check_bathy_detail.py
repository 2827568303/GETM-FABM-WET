import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

nc2 = netCDF4.Dataset('bathymetry.nc')
h = nc2['bathymetry'][:]
print('Bathymetry shape:', h.shape)
print('Type:', type(h))
print('Is masked:', np.ma.is_masked(h))

# Convert to masked array info
if np.ma.is_masked(h):
    print('Masked count:', h.mask.sum())

# Get actual values
h_arr = np.array(h)
print('Actual values at (34,4):', h_arr[34,4])  # DAYUN
print('Actual values at (2,22):', h_arr[2,22])  # LUONAN
print('Actual values at (48,11):', h_arr[48,11])  # YIHE

# Print the whole column/row for j=35 (0-indexed 34)
print('\nColumn i=5 (0-indexed 4) for j=1-54:')
for j in range(54):
    val = h_arr[j, 4]
    print(f'  j={j+1}, i=5: {val}')

print('\nRow j=35 (0-indexed 34) for i=1-44:')
for i in range(44):
    val = h_arr[34, i]
    print(f'  j=35, i={i+1}: {val}')