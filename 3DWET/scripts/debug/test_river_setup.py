import netCDF4 as nc
import numpy as np
from pathlib import Path

test_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

# 创建一个简单的河流文件
f = nc.Dataset(str(test_dir / 'test_river.nc'), 'w', format='NETCDF4')
f.createDimension('time', None)

time_var = f.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var.long_name = 'time'
time_var[:] = np.arange(25) * 3600.0

# 一条简单的河流，流量 10 m3/s
riv_var = f.createVariable('TEST_RIV', 'f4', ('time',))
riv_var.units = 'm3 s-1'
riv_var.long_name = 'test river discharge'
riv_var[:] = 10.0

f.close()
print('创建 test_river.nc 成功')

# 创建 riverinfo.dat
with open(test_dir / 'riverinfo.dat', 'w') as f:
    f.write('1\n')
    f.write('3 3 TEST_RIV -1 -1\n')
print('创建 riverinfo.dat 成功')
