import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

print('=== 检查 2D 输出 ===')
f2d = nc.Dataset(str(case_dir / 'LUOMAHU_WET.2d.nc'))
print(f'2D 时间步数: {f2d.dimensions["time"].size}')
print(f'2D 变量: {list(f2d.variables.keys())[:20]}')

for var in ['elev', 'u', 'v']:
    if var in f2d.variables:
        data = f2d.variables[var][:]
        print(f'  {var}: shape={data.shape}')
        print(f'    min={np.nanmin(data)}, max={np.nanmax(data)}')
        if np.any(np.isnan(data)):
            print(f'    has NaN: True')
        if np.any(np.isinf(data)):
            print(f'    has Inf: True')
f2d.close()

print()
print('=== 检查 3D 输出 ===')
try:
    f3d = nc.Dataset(str(case_dir / 'LUOMAHU_WET.3d.nc'))
    print(f'3D 时间步数: {f3d.dimensions["time"].size}')
    f3d.close()
except Exception as e:
    print(f'3D 文件无法打开: {e}')

print()
print('=== 检查地形 ===')
fb = nc.Dataset(str(case_dir / 'bathymetry.nc'))
bathy = fb.variables['bathymetry'][:]
print(f'bathy shape: {bathy.shape}')
print(f'bathy min: {bathy.min()}, max: {bathy.max()}')
print(f'有效格点 (>0): {np.sum(bathy > 0)}')
print(f'浅于 0.5m: {np.sum((bathy > 0) & (bathy < 0.5))}')
print(f'浅于 1m: {np.sum((bathy > 0) & (bathy < 1))}')
fb.close()

print()
print('=== 检查河流数据 ===')
fr = nc.Dataset(str(case_dir / 'rivers.nc'))
print(f'河流变量: {list(fr.variables.keys())}')
for var in fr.variables:
    if var != 'time':
        data = fr.variables[var][:]
        print(f'  {var}: shape={data.shape}, min={data.min():.4f}, max={data.max():.4f}')
        if np.any(np.isnan(data)):
            print(f'    has NaN!')
fr.close()
