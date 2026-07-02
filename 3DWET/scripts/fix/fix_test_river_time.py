import netCDF4 as nc
import numpy as np
from pathlib import Path

test_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

f = nc.Dataset(str(test_dir / 'rivers.nc'), 'r+')
f.variables['time'].units = 'seconds since 2000-01-01 00:00:00'
f.close()
print('已修改河流时间单位')
