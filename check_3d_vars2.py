import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\GETM_FABM_WET_TEST.3d.nc')

print('3D 变量列表:')
for v in f.variables:
    var = f.variables[v]
    if 'sigma' in var.dimensions:
        print(f'  {v}: dims={var.dimensions}, shape={var.shape}')
        if var.ndim >= 3:
            data = var[0] if 'time' in var.dimensions else var[:]
            if hasattr(data, 'mask'):
                print(f'    masked: {np.sum(data.mask)} / {data.size}')
                # 找一个有效的 (y,x) 点
                valid_yx = ~data.mask[0] if data.shape[0] == data.mask.shape[0] else ~data.mask[0, :, :]
                for yi in range(data.shape[-2]):
                    for xi in range(data.shape[-1]):
                        if not data.mask[0, yi, xi]:
                            print(f'    点(y={yi},x={xi}) 各层值: {data[:, yi, xi]}')
                            break
                    else:
                        continue
                    break

f.close()
