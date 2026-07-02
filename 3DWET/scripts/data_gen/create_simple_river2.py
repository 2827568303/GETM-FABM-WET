import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# 读取原始 rivers.nc 作为模板
f_orig = nc.Dataset(str(case_dir / 'rivers.nc'), 'r')
time_data = f_orig.variables['time'][:]
f_orig.close()

# 创建简化版河流文件，保持维度
f = nc.Dataset(str(case_dir / 'rivers_simple.nc'), 'w', format='NETCDF4')
f.createDimension('time', None)  # unlimited

time_var = f.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var[:] = time_data

# 只有一条河，沂河，10 m³/s
Q = f.createVariable('YIHE', 'f4', ('time',))
Q.units = 'm3 s-1'
Q[:] = 10.0

f.close()
print('已创建 rivers_simple.nc: 只有 YIHE=10 m3/s')

# 复制为 rivers.nc
import shutil
shutil.copy(str(case_dir / 'rivers_simple.nc'), str(case_dir / 'rivers.nc'))
print('已复制为 rivers.nc')
