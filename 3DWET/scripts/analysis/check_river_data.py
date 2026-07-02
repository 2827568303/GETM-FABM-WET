import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\rivers.nc')
print('河流数据检查:')
for v in f.variables:
    if v == 'time':
        continue
    data = f.variables[v][:]
    print(f'  {v}:')
    print(f'    shape: {data.shape}')
    print(f'    dtype: {data.dtype}')
    if hasattr(data, 'mask'):
        print(f'    has_mask: {np.any(data.mask)}')
    print(f'    has_nan: {np.any(np.isnan(data))}')
    print(f'    has_inf: {np.any(np.isinf(data))}')
    if hasattr(data, 'filled'):
        filled = data.filled(np.nan)
        print(f'    min: {np.nanmin(filled):.4f}')
        print(f'    max: {np.nanmax(filled):.4f}')

f.close()
