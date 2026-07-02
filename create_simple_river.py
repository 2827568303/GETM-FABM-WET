import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# 创建简化版河流文件
ntimes = 481
times = np.arange(ntimes) * 3600.0

f = nc.Dataset(str(case_dir / 'rivers_simple.nc'), 'w', format='NETCDF4')
f.createDimension('time', ntimes)

time_var = f.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var[:] = times

# 只有一条河，沂河，10 m³/s
Q = f.createVariable('YIHE', 'f4', ('time',))
Q.units = 'm3 s-1'
Q[:] = 10.0

f.close()
print('已创建 rivers_simple.nc: 只有 YIHE=10 m3/s')

# 修改 riverinfo.dat
with open(case_dir / 'riverinfo.dat', 'w') as f:
    f.write('1\n')
    f.write('12 49 YIHE -1 -1\n')
print('已修改 riverinfo.dat: 只有一条河 (0-indexed)')
