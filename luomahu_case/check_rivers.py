import netCDF4 as nc
ds = nc.Dataset('bathymetry.nc')
bathy = ds.variables['bathymetry'][:]
print('地形 shape:', bathy.shape)
print('检查河流位置 (i, j):')
positions = [(2,22,'DAYUN'), (4,32,'YIHE'), (40,23,'LUONAN'), (40,15,'ZHANGSHAN')]
for i,j,name in positions:
    if j < bathy.shape[0] and i < bathy.shape[1]:
        depth = bathy[j,i]
        status = '✓ 水域' if depth > 0 else '✗ 陆地'
        print(f'  {name}: ({i},{j}) = {depth:.2f} m {status}')
    else:
        print(f'  {name}: ({i},{j}) - 超出范围!')
