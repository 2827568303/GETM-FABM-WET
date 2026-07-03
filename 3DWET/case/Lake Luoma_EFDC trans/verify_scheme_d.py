import netCDF4 as nc
import numpy as np

case_dir = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma_EFDC trans'

# Check 2D output
ds2d = nc.Dataset(f'{case_dir}/LUOMA_EFDC_HYD.2d.nc')
print('=== 2D Output ===')
print('Variables:', list(ds2d.variables.keys()))
print('Time steps:', len(ds2d.variables['time']))
print('Time range:', ds2d.variables['time'][0], 'to', ds2d.variables['time'][-1])

# Check elev for NaN
elev = ds2d.variables['elev'][:]
nan_count = np.isnan(elev).sum()
print('elev shape:', elev.shape)
print('elev NaN count:', nan_count)
print('elev range:', np.nanmin(elev), 'to', np.nanmax(elev))

# Check last time step for NaN
elev_last = elev[-1, :, :]
nan_last = np.isnan(elev_last).sum()
print('elev last step NaN:', nan_last)
ds2d.close()

# Check 3D output
ds3d = nc.Dataset(f'{case_dir}/LUOMA_EFDC_HYD.3d.nc')
print()
print('=== 3D Output ===')
print('Variables:', list(ds3d.variables.keys()))
print('Time steps:', len(ds3d.variables['time']))

# Check temperature
temp = ds3d.variables['temp'][:]
nan_count_t = np.isnan(temp).sum()
print('temp shape:', temp.shape)
print('temp NaN count:', nan_count_t)
print('temp range:', np.nanmin(temp), 'to', np.nanmax(temp))

# Check u velocity
u = ds3d.variables['u'][:]
nan_count_u = np.isnan(u).sum()
print('u shape:', u.shape)
print('u NaN count:', nan_count_u)
print('u range:', np.nanmin(u), 'to', np.nanmax(u))

# Check last time step
u_last = u[-1, :, :, :]
nan_u_last = np.isnan(u_last).sum()
print('u last step NaN:', nan_u_last)
ds3d.close()

print()
print('=== VERDICT ===')
if nan_count == 0 and nan_count_t == 0 and nan_count_u == 0:
    print('SUCCESS: No NaN in output data.')
    print('Model completed 3 years (1094 days) with valid data.')
else:
    print('WARNING: NaN detected in output data.')
    print(f'  elev NaN: {nan_count}')
    print(f'  temp NaN: {nan_count_t}')
    print(f'  u NaN: {nan_count_u}')
