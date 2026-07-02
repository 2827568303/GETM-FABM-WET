import netCDF4 as nc
import numpy as np
from pathlib import Path

test_dir = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

f = nc.Dataset(str(test_dir / 'rivers.nc'), 'r+')
f.variables['TEST_RIV'][:] = 0.1  # 0.1 m3/s，非常小的流量
f.close()
print('流量改为 0.1 m3/s')
