import netCDF4 as nc
import numpy as np
from pathlib import Path

test_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

f = nc.Dataset(str(test_dir / 'rivers.nc'), 'r+')

# 确保有 TEST_RIV
if 'TEST_RIV' not in f.variables:
    f.createVariable('TEST_RIV', 'f4', ('time',))
f.variables['TEST_RIV'][:] = 1.0  # 1 m3/s 入流

# 添加一条出河
if 'OUT_RIV' not in f.variables:
    f.createVariable('OUT_RIV', 'f4', ('time',))
f.variables['OUT_RIV'][:] = -1.0  # 1 m3/s 出流

f.close()

# 修改 riverinfo.dat
with open(test_dir / 'riverinfo.dat', 'w') as f:
    f.write('2\n')
    f.write('1 3 TEST_RIV -1 -1\n')  # 西边界入流
    f.write('5 3 OUT_RIV -1 -1\n')   # 东边界出流

print('已设置入河和出河各 1 m3/s')
