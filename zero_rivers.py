import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 所有河流流量都设为 0
for river in ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    if river in f.variables:
        f.variables[river][:] = 0.0
        print(f'{river}: 0')

# 去掉所有 mask
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    data = var[:]
    if hasattr(data, 'mask'):
        var[:] = data.filled(0.0)

f.close()
print('\n所有河流流量设为 0')
