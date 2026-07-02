import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r+')

# 把所有负流量改成正的（先测试）
for river in ['DAYUN', 'LUONAN', 'YIHE', 'ZHANGSHAN', 'YANGHE']:
    if river in f.variables:
        q = f.variables[river][:]
        print(f'{river}: min={q.min():.2f}, max={q.max():.2f}')

f.close()
