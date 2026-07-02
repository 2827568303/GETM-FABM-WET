import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 测试：只用一条河（YIHE），正流量 10 m3/s
for river in ['DAYUN', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    if river in f.variables:
        f.variables[river][:] = 0.0

if 'YIHE' in f.variables:
    f.variables['YIHE'][:] = 10.0

# 把所有水质变量的 mask 去掉（设为普通 float）
for v in f.variables:
    if v == 'time':
        continue
    var = f.variables[v]
    data = var[:]
    if hasattr(data, 'mask'):
        var[:] = data.filled(0.0)

f.close()
print('已修改 rivers.nc: 只有 YIHE=10 m3/s，其他=0')
