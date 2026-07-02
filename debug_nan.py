import netCDF4 as nc
import numpy as np

f2 = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.2d.nc')
elev = f2.variables['elev'][0]
print('elev[0] 类型:', type(elev))
print('elev[0] 是 MaskedArray:', hasattr(elev, 'mask'))

if hasattr(elev, 'mask'):
    print('mask 类型:', type(elev.mask))
    print('mask shape:', elev.mask.shape)
    print('mask True 数量:', np.sum(elev.mask))
    print('mask False 数量:', np.sum(~elev.mask))
    
    # 看看非 mask 点的实际值
    data = elev.data
    print('非 mask 点 data 类型:', type(data))
    print('非 mask 点 data 中的 NaN 数量:', np.sum(np.isnan(data[~elev.mask])))
    print('非 mask 点 data 示例:', data[~elev.mask][:5])

f2.close()
