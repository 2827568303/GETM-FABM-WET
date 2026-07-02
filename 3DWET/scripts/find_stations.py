"""Find optimal grid positions for three monitoring stations."""
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case'

ds = nc.Dataset(f'{CASE}/bathymetry.nc')
bathy = np.ma.filled(ds.variables['bathymetry'][:], np.nan)
lonc = np.ma.filled(ds.variables['lonc'][:], np.nan)
latc = np.ma.filled(ds.variables['latc'][:], np.nan)
ds.close()

ny, nx = bathy.shape
water = bathy > 0

# River mouth positions (i, j) - 1-based in riverinfo, 0-based in array
# YANGHE: (35, 28) -> array [27, 34]
# ZHANGSHAN: (42, 27) -> array [26, 41]
# DAYUN: (2, 32) -> array [31, 1]
river_positions = {
    '杨河滩 (Yanghetan)': (35, 28),   # YANGHE outflow, southeast
    '嶂山闸 (Zhangshanza)': (42, 27), # ZHANGSHAN outflow, east
    '皂河闸 (Zaohezha)': (2, 32),     # DAYUN bidirectional, west
}

print(f'Lake shape: {ny}x{nx}, water cells: {water.sum()}')
print(f'Depth range: {np.nanmin(bathy[water]):.2f} - {np.nanmax(bathy[water]):.2f} m')
print()

for name, (i_1based, j_1based) in river_positions.items():
    i = i_1based - 1  # Convert to 0-based
    j = j_1based - 1

    # Check depth at river mouth
    if 0 <= i < nx and 0 <= j < ny:
        depth = bathy[j, i]
        lon = lonc[j, i]
        lat = latc[j, i]
        print(f'{name}:')
        print(f'  River mouth cell ({i_1based},{j_1based}): depth={depth:.2f}m, lon={lon:.4f}, lat={lat:.4f}')

    # Find nearby water cells with good depth (>2m) for monitoring
    best_cell = None
    best_depth = 0
    for dj in range(-3, 4):
        for di in range(-3, 4):
            ci, cj = i + di, j + dj
            if 0 <= ci < nx and 0 <= cj < ny and water[cj, ci]:
                d = bathy[cj, ci]
                if d > best_depth and d < 15:  # prefer deep but not extreme
                    best_depth = d
                    best_cell = (ci, cj)

    if best_cell:
        bi, bj = best_cell
        print(f'  Best monitoring cell: ({bi+1},{bj+1}) -> array[{bj},{bi}]')
        print(f'    depth={bathy[bj,bi]:.2f}m, lon={lonc[bj,bi]:.4f}, lat={latc[bj,bi]:.4f}')
        print(f'    offset from river mouth: di={bi-i}, dj={bj-j}')
    print()
