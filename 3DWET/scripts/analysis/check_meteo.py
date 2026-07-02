import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\meteo.nc')
print('meteo.nc:')
print(f'dimensions: {dict(f.dimensions)}')

for v in f.variables:
    data = f.variables[v][:]
    print(f'  {v}: shape={data.shape}, dtype={data.dtype}')
    if hasattr(data, 'mask'):
        print(f'    has_mask: {np.any(data.mask)}')
    print(f'    has_nan: {np.any(np.isnan(data))}')
    print(f'    has_inf: {np.any(np.isinf(data))}')
    if data.size <= 10:
        print(f'    values: {data}')
    else:
        print(f'    min: {np.nanmin(data):.4f}, max: {np.nanmax(data):.4f}')

f.close()
