import netCDF4 as nc

nc2d = nc.Dataset('/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/LUOMAHU_WET.2d.nc')
print('=== 2D Output ===')
print('Time steps:', len(nc2d.variables['time']))
print('Variables:', len(nc2d.variables), 'total')

fish_vars_2d = [v for v in nc2d.variables if 'Fish' in v or 'fish' in v]
print('Fish-related 2D vars:', len(fish_vars_2d))
for v in fish_vars_2d[:10]:
    print('  -', v)

macro_vars_2d = [v for v in nc2d.variables if 'macrophytes' in v]
print('Macrophyte-related 2D vars:', len(macro_vars_2d))
for v in macro_vars_2d[:10]:
    print('  -', v)

nc2d.close()

nc3d = nc.Dataset('/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/LUOMAHU_WET.3d.nc')
print()
print('=== 3D Output ===')
print('Time steps:', len(nc3d.variables['time']))
print('Variables:', len(nc3d.variables), 'total')

phyto_vars = [v for v in nc3d.variables if any(p in v for p in ['cyanobacteria', 'diatoms', 'greens'])]
print('Phytoplankton-related 3D vars:', len(phyto_vars))
for v in phyto_vars[:10]:
    print('  -', v)

nc3d.close()
print()
print('Output files verified successfully!')
