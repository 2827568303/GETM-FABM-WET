import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.2d.nc')
print('2D 变量:')
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    if 'time' in var.dimensions:
        data = var[:]
        print(f'  {v}: shape={data.shape}')
        if len(data) >= 3:
            print(f'    t=0: min={np.nanmin(data[0]):.4f}, max={np.nanmax(data[0]):.4f}')
            print(f'    t=1: min={np.nanmin(data[1]):.4f}, max={np.nanmax(data[1]):.4f}')
            print(f'    t=2: min={np.nanmin(data[2]):.4f}, max={np.nanmax(data[2]):.4f}')
            print(f'    t=3: min={np.nanmin(data[3]):.4f}, max={np.nanmax(data[3]):.4f}')

f.close()
