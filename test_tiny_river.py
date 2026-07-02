import netCDF4 as nc
import numpy as np
from pathlib import Path

test_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

f = nc.Dataset(str(test_dir / 'rivers.nc'), 'r+')
# 只有入河，非常小的流量
f.variables['TEST_RIV'][:] = 0.0001
if 'OUT_RIV' in f.variables:
    f.variables['OUT_RIV'][:] = 0.0
f.close()

with open(test_dir / 'riverinfo.dat', 'w') as f:
    f.write('1\n')
    f.write('3 3 TEST_RIV -1 -1\n')  # 中间位置

print('test_case: 只有 TEST_RIV = 0.0001 m3/s')
