import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.3d.nc')

print('3D 变量列表:')
for v in f.variables:
    var = f.variables[v]
    if 'sigma' in var.dimensions:
        data = var[0] if 'time' in var.dimensions else var[:]
        valid_count = np.sum(~data.mask) if hasattr(data, 'mask') else data.size
        print(f'  {v}: dims={var.dimensions}, shape={var.shape}, valid={valid_count}/{data.size}')
        if valid_count > 0 and hasattr(data, 'mask'):
            print(f'    valid layers: {np.where(~data.mask[:, 2, 2])[0]}')

f.close()
