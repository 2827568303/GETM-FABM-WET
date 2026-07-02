import netCDF4 as nc
import numpy as np
from pathlib import Path

case_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# 创建只有流量的简化河流文件
ntimes = 481  # 和 meteo 一样
times = np.arange(ntimes) * 3600.0

f = nc.Dataset(str(case_dir / 'rivers_simple.nc'), 'w', format='NETCDF4')
f.createDimension('time', ntimes)

time_var = f.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var[:] = times

# 读取原始数据获取每日流量
f_orig = nc.Dataset(str(case_dir / 'rivers.nc'), 'r')
daily_flow = {}
for key in ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    daily_flow[key] = f_orig.variables[key][:21]  # 21天数据
f_orig.close()

# 插值到 hourly
from scipy.interpolate import interp1d
for key, daily in daily_flow.items():
    daily_times = np.arange(21) * 86400.0
    interp = interp1d(daily_times, daily, kind='linear', fill_value='extrapolate')
    hourly = interp(times)
    
    var = f.createVariable(key, 'f4', ('time',))
    var.units = 'm3 s-1'
    var[:] = hourly
    print(f'{key}: {hourly[0]:.2f} ~ {hourly[-1]:.2f} m3/s')

f.close()
print('\n已创建 rivers_simple.nc（只有流量，无水质变量）')

# 复制为 rivers.nc
import shutil
shutil.copy(str(case_dir / 'rivers_simple.nc'), str(case_dir / 'rivers.nc'))
print('已复制为 rivers.nc')
