import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# 读取原始
f = nc.Dataset(str(case_dir / 'rivers.nc'), 'r')
data = {}
for v in f.variables:
    data[v] = f.variables[v][:]
f.close()

# 重新创建，去掉错误的 temp 属性
f = nc.Dataset(str(case_dir / 'rivers_fixed.nc'), 'w', format='NETCDF4')
f.createDimension('time', None)

time_var = f.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var[:] = data['time']

# 重新创建河流变量
for key in ['DAYUN', 'LUONAN', 'YIHE', 'ZHANGSHAN', 'YANGHE']:
    var = f.createVariable(key, 'f4', ('time',))
    var.units = 'm3 s-1'
    var[:] = data[key]

# 水质变量
for key in data:
    if key not in ['time', 'DAYUN', 'LUONAN', 'YIHE', 'ZHANGSHAN', 'YANGHE']:
        var = f.createVariable(key, 'f4', ('time',))
        if 'NH4' in key:
            var.units = 'mmol m-3'
        elif 'NO3' in key:
            var.units = 'mmol m-3'
        elif 'PO4' in key:
            var.units = 'mmol m-3'
        elif 'POM' in key:
            var.units = 'mmol m-3'
        var[:] = data[key]

f.close()
print('已创建 rivers_fixed.nc（无 temp 属性）')

# 复制为 rivers.nc
import shutil
shutil.copy(str(case_dir / 'rivers_fixed.nc'), str(case_dir / 'rivers.nc'))
print('已复制为 rivers.nc')
