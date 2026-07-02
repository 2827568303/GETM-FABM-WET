import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 所有河流流量都设为 0，除了杨河
for river in ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN']:
    if river in f.variables:
        f.variables[river][:] = 0.0

if 'YANGHE' in f.variables:
    f.variables['YANGHE'][:] = 0.001  # 非常小的流量
    print(f'YANGHE: {f.variables["YANGHE"][0]:.4f} m3/s')

# 去掉所有 mask
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    data = var[:]
    if hasattr(data, 'mask'):
        var[:] = data.filled(0.0)

f.close()
print('\n只有杨河有 0.001 m3/s 流量')
