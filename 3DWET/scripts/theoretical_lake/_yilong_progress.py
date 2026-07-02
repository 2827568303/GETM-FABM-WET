import netCDF4 as nc
import os

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong'

# Check progress via output.nc
try:
    ds = nc.Dataset(os.path.join(CASE, 'output.nc'), 'r')
    t = ds.variables['time'][:]
    print(f'output.nc time records: {len(t)} / 366 days')
    if len(t) > 0:
        print(f'  first time: {t[0]}, last time: {t[-1]}')
    ds.close()
except Exception as e:
    print(f'output.nc: {e}')

# Check 2D
try:
    ds = nc.Dataset(os.path.join(CASE, 'YILONG.2d.nc'), 'r')
    t = ds.variables['time'][:]
    print(f'YILONG.2d.nc time records: {len(t)} / 730')
    ds.close()
except Exception as e:
    print(f'YILONG.2d.nc: {e}')

# Check 3D
try:
    ds = nc.Dataset(os.path.join(CASE, 'YILONG.3d.nc'), 'r')
    t = ds.variables['time'][:]
    print(f'YILONG.3d.nc time records: {len(t)} / 730')
    ds.close()
except Exception as e:
    print(f'YILONG.3d.nc: {e}')
