import netCDF4 as nc
import numpy as np

f = nc.Dataset(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\LUOMAHU_WET.3d.nc')

print('=== 文件信息 ===')
print(f'维度: {f.dimensions.keys()}')
print(f'时间步数: {len(f.dimensions["time"])}')
print()

print('=== cyanobacteria_oChla (蓝藻叶绿素) ===')
data = f.variables['cyanobacteria_oChla'][:]
print(f'shape: {data.shape}')
valid = data[~np.isnan(data)]
if len(valid) > 0:
    print(f'min: {np.min(valid):.6f}')
    print(f'max: {np.max(valid):.6f}')
    print(f'mean: {np.mean(valid):.6f}')
else:
    print('全是NaN')
print()

print('=== wet_chla (总叶绿素) ===')
data2 = f.variables['wet_chla'][:]
valid2 = data2[~np.isnan(data2)]
if len(valid2) > 0:
    print(f'min: {np.min(valid2):.6f}')
    print(f'max: {np.max(valid2):.6f}')
    print(f'mean: {np.mean(valid2):.6f}')
print()

print('=== abiotic_water_sPO4W (水中磷酸盐) ===')
data3 = f.variables['abiotic_water_sPO4W'][:]
valid3 = data3[~np.isnan(data3)]
if len(valid3) > 0:
    print(f'min: {np.min(valid3):.6f}')
    print(f'max: {np.max(valid3):.6f}')
    print(f'mean: {np.mean(valid3):.6f}')
print()

print('=== cyanobacteria_sDW (蓝藻生物量) ===')
data4 = f.variables['cyanobacteria_sDW'][:]
valid4 = data4[~np.isnan(data4)]
if len(valid4) > 0:
    print(f'min: {np.min(valid4):.6f}')
    print(f'max: {np.max(valid4):.6f}')
    print(f'mean: {np.mean(valid4):.6f}')
print()

print('=== 最后一个时间步的表层蓝藻叶绿素 ===')
last_surface = data[-1, 0, :, :]
valid_last = last_surface[~np.isnan(last_surface)]
if len(valid_last) > 0:
    print(f'min: {np.min(valid_last):.6f}')
    print(f'max: {np.max(valid_last):.6f}')
    print(f'mean: {np.mean(valid_last):.6f}')

f.close()
