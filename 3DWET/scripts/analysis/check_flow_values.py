import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\rivers.nc')
print('=== 河流流量检查 ===')
for key in ['DAYUN', 'YIHE', 'LUONAN', 'ZHANGSHAN', 'YANGHE']:
    data = f.variables[key][:]
    print(f'{key}: min={data.min():.2f}, max={data.max():.2f} m³/s')
f.close()
