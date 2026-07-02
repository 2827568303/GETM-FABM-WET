import netCDF4 as nc
import numpy as np

print('=== 旧地形（备份）===')
try:
    f_old = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
    print(f'Variables: {list(f_old.variables.keys())}')
    for v in ['bathymetry', 'grid_type', 'x', 'y', 'lonc', 'latc']:
        if v in f_old.variables:
            var = f_old.variables[v]
            print(f'  {v}: dims={var.dimensions}, shape={var.shape}, dtype={var.dtype}')
    f_old.close()
except Exception as e:
    print(f'  Error: {e}')

print()
print('=== 测试：看看 GETM 期望的格式 ===')
# 检查原来成功的配置
# 先看看旧的输出文件中 bathymetry 的信息
try:
    f_out = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\output.nc')
    print(f'output.nc variables: {list(f_out.variables.keys())[:20]}')
    if 'bathymetry' in f_out.variables:
        b = f_out.variables['bathymetry']
        print(f'  bathymetry: dims={b.dimensions}, shape={b.shape}')
    f_out.close()
except Exception as e:
    print(f'  output.nc error: {e}')
