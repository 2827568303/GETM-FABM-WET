import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 所有河流都设为小的正流量（测试）
for river in ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    if river in f.variables:
        q = f.variables[river][:]
        f.variables[river][:] = np.abs(q) * 0.01 + 0.5  # 小流量
        print(f'{river}: new min={f.variables[river][:].min():.2f}, max={f.variables[river][:].max():.2f}')

# 去掉所有 mask
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    data = var[:]
    if hasattr(data, 'mask'):
        var[:] = data.filled(0.0)

f.close()
print()
print('已修改所有河流为小正流量')
