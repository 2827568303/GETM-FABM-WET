import netCDF4 as nc
import numpy as np

# 没有河流时的输出（之前跑的）
f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f.variables['elev'][:]
print(f'有河流时 elev shape: {elev.shape}')
print(f'有河流时 t=0 elev 有效点数: {np.sum(np.isfinite(np.ma.filled(elev[0], np.nan)))}')
f.close()

# 让我看看 bathy 中 min_depth 以上的点数
f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\bathymetry.nc')
bathy = f.variables['bathymetry'][:]
b = np.ma.filled(bathy, np.nan)
print(f'bathy 有效点数: {np.sum(np.isfinite(b) & (b > 0.5))}')
f.close()
