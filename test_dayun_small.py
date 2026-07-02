import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 所有河流流量都设为 0，除了京杭大运河
for river in ['YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    if river in f.variables:
        f.variables[river][:] = 0.0

if 'DAYUN' in f.variables:
    f.variables['DAYUN'][:] = 0.001  # 非常小的正流量
    print(f'DAYUN: {f.variables["DAYUN"][0]:.4f} m3/s')

# 去掉所有 mask
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    data = var[:]
    if hasattr(data, 'mask'):
        var[:] = data.filled(0.0)

f.close()
print('\n只有京杭大运河有 0.001 m3/s 正流量')
