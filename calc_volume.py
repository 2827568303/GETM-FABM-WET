import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
bathy = f.variables['bathymetry'][:]
dx = 500.0
dy = 500.0

water_cells = np.sum(bathy > 0.5)
area = water_cells * dx * dy / 1e6  # km2
print(f'水网格数: {water_cells}')
print(f'水域面积: {area:.2f} km2')
print(f'水域面积: {area*1e6:.2f} m2')

# 计算 2.5 m3/s 流量，20分钟后的水位上升
volume = 2.5 * 20 * 60  # m3
rise = volume / (area * 1e6)  # m
print(f'2.5 m3/s 流入 20 分钟，水位上升: {rise*100:.4f} cm')
f.close()
