"""
3D Visualization - GETM-FABM-WET
Multi-angle 3D lake body visualization with temperature, velocity, and bathymetry.
Based on original visualize.py Figure 13, enhanced for problem analysis.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import netCDF4 as nc
import os
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Configure Chinese font
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')
out_dir = os.path.join(case_dir, 'figures')
os.makedirs(out_dir, exist_ok=True)

def to_np(data):
    return np.ma.filled(data, np.nan)

print('=' * 70)
print('Loading data...')
print('=' * 70)

ds3d = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
ds2d = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.2d.nc'))

time3d = to_np(ds3d.variables['time'][:]) / 86400.0
time2d = to_np(ds2d.variables['time'][:]) / 86400.0
sigma = to_np(ds3d.variables['sigma'][:])
lon = to_np(ds3d.variables['lonc'][:])
lat = to_np(ds3d.variables['latc'][:])

bathy_ds = nc.Dataset(os.path.join(case_dir, 'bathymetry.nc'))
bathymetry = to_np(bathy_ds.variables['bathymetry'][:])
bathy_ds.close()

mask = bathymetry > 0
n_time = len(time3d)
n_sigma = len(sigma)
ny, nx = bathymetry.shape

print(f'Time steps: {n_time}')
print(f'Sigma layers: {n_sigma}')
print(f'Grid: {nx} x {ny}')
print(f'Max depth: {np.nanmax(bathymetry[mask]):.1f} m')

# Load key 3D variables
temp3d = to_np(ds3d.variables['temp'][:])
uu = to_np(ds3d.variables['uu'][:])
vv = to_np(ds3d.variables['vv'][:])
elev = to_np(ds2d.variables['elev'][:])

# Stations and rivers
station_markers = [(37, 26, '杨河滩'), (40, 26, '嶂山闸'), (4, 33, '皂河闸')]
river_markers = [
    (49, 34, 'YIHE', 'green'),
    (1, 27, 'LUONAN', 'green'),
    (31, 1, 'DAYUN', 'orange'),
    (26, 40, 'ZHANGSHAN', 'red'),
]

max_depth = np.nanmax(bathymetry)

# ============================================================
print()
print('=' * 70)
print('Figure 3D-1: Multi-angle lake bathymetry (6 viewpoints)')
print('=' * 70)

X, Y = np.meshgrid(range(nx), range(ny))
Z_bottom = -bathymetry
Z_bottom[~mask] = np.nan
Z_surface = np.zeros_like(bathymetry)
Z_surface[~mask] = np.nan

view_angles = [
    (30, -60, '俯视视角 (30, -60)'),
    (20, -30, '侧视视角 (20, -30)'),
    (45, 45, '对角视角 (45, 45)'),
    (60, -90, '正前视角 (60, -90)'),
    (15, 0, '低角度视角 (15, 0)'),
    (90, -90, '正俯视 (90, -90)'),
]

fig = plt.figure(figsize=(24, 16))
for v_idx, (elev_angle, azim, title) in enumerate(view_angles):
    ax = fig.add_subplot(2, 3, v_idx + 1, projection='3d')

    # Water surface
    ax.plot_surface(X, Y, Z_surface, alpha=0.2, color='cyan', shade=False)
    # Lake bottom
    ax.plot_surface(X, Y, Z_bottom, alpha=0.8, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)

    # Stations
    for si, sj, sname in station_markers:
        if mask[sj, si]:
            sdepth = bathymetry[sj, si]
            ax.scatter(si, sj, 0, color='red', s=50, marker='v', zorder=5)
            ax.scatter(si, sj, -sdepth, color='red', s=50, marker='^', zorder=5)
            ax.plot([si, si], [sj, sj], [0, -sdepth], color='red', linewidth=2, zorder=5)
            ax.text(si, sj, 1, sname, color='red', fontsize=8)

    # Rivers
    for ri, rj, rname, rcolor in river_markers:
        if 0 <= ri < nx and 0 <= rj < ny and mask[rj, ri]:
            ax.scatter(ri, rj, 0, color=rcolor, s=40, marker='o', zorder=4)

    ax.set_xlabel('X (grid)')
    ax.set_ylabel('Y (grid)')
    ax.set_zlabel('深度 (m)')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.view_init(elev=elev_angle, azim=azim)
    ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D01_bathymetry_multiangle.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D01_bathymetry_multiangle.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-2: 3D temperature at surface (3 time snapshots, 3 angles)')
print('=' * 70)

t_snapshots = [0, n_time // 2, n_time - 1]
view_angles_3d = [(30, -60), (20, -30), (45, 45)]

fig = plt.figure(figsize=(20, 18))
plot_idx = 1
for t_idx in t_snapshots:
    for v_idx, (elev_angle, azim) in enumerate(view_angles_3d):
        ax = fig.add_subplot(3, 3, plot_idx, projection='3d')

        # Lake bottom
        ax.plot_surface(X, Y, Z_bottom, alpha=0.5, cmap='Blues_r',
                        vmin=-max_depth, vmax=0, shade=True)

        # Temperature at surface
        temp_surf_t = temp3d[t_idx, np.argmin(np.abs(sigma - 0.0)), :, :]
        # Normalize for colormap
        temp_min = np.nanmin(temp_surf_t[mask])
        temp_max = np.nanmax(temp_surf_t[mask])
        temp_norm = (temp_surf_t - temp_min) / max(temp_max - temp_min, 0.1)
        temp_norm[~mask] = np.nan

        ax.plot_surface(X, Y, Z_surface, alpha=0.6, cmap='viridis',
                        facecolors=plt.cm.viridis(temp_norm), shade=False)

        # Stations
        for si, sj, sname in station_markers:
            if mask[sj, si]:
                ax.scatter(si, sj, 0, color='red', s=40, marker='v', zorder=5)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('深度 (m)')
        ax.set_title(f'表层温度 (第{time3d[t_idx]:.0f}天)\n视角 ({elev_angle}, {azim})',
                     fontsize=10, fontweight='bold')
        ax.view_init(elev=elev_angle, azim=azim)
        ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)
        plot_idx += 1

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D02_temperature_surface.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D02_temperature_surface.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-3: 3D velocity field at surface (3 time snapshots)')
print('=' * 70)

fig = plt.figure(figsize=(20, 18))
plot_idx = 1
for t_idx in t_snapshots:
    for v_idx, (elev_angle, azim) in enumerate(view_angles_3d):
        ax = fig.add_subplot(3, 3, plot_idx, projection='3d')

        # Lake bottom
        ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                        vmin=-max_depth, vmax=0, shade=True)

        # Velocity vectors at surface
        u_surf = uu[t_idx, np.argmin(np.abs(sigma - 0.0)), :, :]
        v_surf = vv[t_idx, np.argmin(np.abs(sigma - 0.0)), :, :]
        speed = np.sqrt(u_surf**2 + v_surf**2)

        # Subsample for quiver
        step = 3
        for j in range(0, ny, step):
            for i in range(0, nx, step):
                if mask[j, i] and speed[j, i] > 0.001:
                    ax.quiver(i, j, 0, u_surf[j, i], v_surf[j, i], 0,
                              length=2, color='red', alpha=0.7)

        # Stations
        for si, sj, sname in station_markers:
            if mask[sj, si]:
                ax.scatter(si, sj, 0, color='blue', s=40, marker='v', zorder=5)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('深度 (m)')
        ax.set_title(f'表层流场 (第{time3d[t_idx]:.0f}天)\n视角 ({elev_angle}, {azim})',
                     fontsize=10, fontweight='bold')
        ax.view_init(elev=elev_angle, azim=azim)
        ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)
        plot_idx += 1

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D03_velocity_field.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D03_velocity_field.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-4: 3D cross-section views (XZ and YZ slices)')
print('=' * 70)

t_3d = n_time // 2  # Middle time step
fig, axes = plt.subplots(2, 2, figsize=(20, 14))

# XZ slice through station 1 (j=26)
ax = axes[0, 0]
j_slice = 26
bathy_xz = bathymetry[j_slice, :]
water_xz = mask[j_slice, :]
temp_xz = temp3d[t_3d, :, j_slice, :]
for i in range(nx):
    if water_xz[i]:
        depth_i = bathy_xz[i]
        z_layers = -sigma * depth_i  # Positive depth: 0=surface, depth=bottom
        for k in range(n_sigma):
            ax.scatter(i, z_layers[k], c=temp_xz[k, i], cmap='viridis',
                       vmin=np.nanmin(temp_xz), vmax=np.nanmax(temp_xz), s=20)
ax.fill_between(range(nx), 0, bathy_xz, where=water_xz, alpha=0.3, color='blue')
ax.set_title(f'XZ切片 (j={j_slice}, 杨河滩行) - 第{time3d[t_3d]:.0f}天')
ax.set_xlabel('X (网格)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(max_depth * 1.1, -0.5)
plt.colorbar(plt.cm.ScalarMappable(cmap='viridis',
            norm=plt.Normalize(np.nanmin(temp_xz), np.nanmax(temp_xz))), ax=ax, label='°C')

# YZ slice through station 1 (i=37)
ax = axes[0, 1]
i_slice = 37
bathy_yz = bathymetry[:, i_slice]
water_yz = mask[:, i_slice]
temp_yz = temp3d[t_3d, :, :, i_slice]
for j in range(ny):
    if water_yz[j]:
        depth_j = bathy_yz[j]
        z_layers = -sigma * depth_j
        for k in range(n_sigma):
            ax.scatter(z_layers[k], j, c=temp_yz[k, j], cmap='viridis',
                       vmin=np.nanmin(temp_yz), vmax=np.nanmax(temp_yz), s=20)
ax.fill_between(range(ny), 0, bathy_yz, where=water_yz, alpha=0.3, color='blue')
ax.set_title(f'YZ切片 (i={i_slice}, 杨河滩列) - 第{time3d[t_3d]:.0f}天')
ax.set_xlabel('深度 (m)')
ax.set_ylabel('Y (网格)')
ax.set_xlim(-0.5, max_depth * 1.1)
plt.colorbar(plt.cm.ScalarMappable(cmap='viridis',
            norm=plt.Normalize(np.nanmin(temp_yz), np.nanmax(temp_yz))), ax=ax, label='°C')

# XZ slice through station 3 (j=33)
ax = axes[1, 0]
j_slice = 33
bathy_xz = bathymetry[j_slice, :]
water_xz = mask[j_slice, :]
temp_xz = temp3d[t_3d, :, j_slice, :]
for i in range(nx):
    if water_xz[i]:
        depth_i = bathy_xz[i]
        z_layers = -sigma * depth_i
        for k in range(n_sigma):
            ax.scatter(i, z_layers[k], c=temp_xz[k, i], cmap='viridis',
                       vmin=np.nanmin(temp_xz), vmax=np.nanmax(temp_xz), s=20)
ax.fill_between(range(nx), 0, bathy_xz, where=water_xz, alpha=0.3, color='blue')
ax.set_title(f'XZ切片 (j={j_slice}, 皂河闸行) - 第{time3d[t_3d]:.0f}天')
ax.set_xlabel('X (网格)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(max_depth * 1.1, -0.5)
plt.colorbar(plt.cm.ScalarMappable(cmap='viridis',
            norm=plt.Normalize(np.nanmin(temp_xz), np.nanmax(temp_xz))), ax=ax, label='°C')

# YZ slice through station 3 (i=4)
ax = axes[1, 1]
i_slice = 4
bathy_yz = bathymetry[:, i_slice]
water_yz = mask[:, i_slice]
temp_yz = temp3d[t_3d, :, :, i_slice]
for j in range(ny):
    if water_yz[j]:
        depth_j = bathy_yz[j]
        z_layers = -sigma * depth_j
        for k in range(n_sigma):
            ax.scatter(z_layers[k], j, c=temp_yz[k, j], cmap='viridis',
                       vmin=np.nanmin(temp_yz), vmax=np.nanmax(temp_yz), s=20)
ax.fill_between(range(ny), 0, bathy_yz, where=water_yz, alpha=0.3, color='blue')
ax.set_title(f'YZ切片 (i={i_slice}, 皂河闸列) - 第{time3d[t_3d]:.0f}天')
ax.set_xlabel('深度 (m)')
ax.set_ylabel('Y (网格)')
ax.set_xlim(-0.5, max_depth * 1.1)
plt.colorbar(plt.cm.ScalarMappable(cmap='viridis',
            norm=plt.Normalize(np.nanmin(temp_yz), np.nanmax(temp_yz))), ax=ax, label='°C')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D04_cross_sections.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D04_cross_sections.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-5: 3D water level surface (4 time snapshots)')
print('=' * 70)

fig = plt.figure(figsize=(20, 12))
t_indices = [0, n_time // 3, 2 * n_time // 3, n_time - 1]

for v_idx, t_idx in enumerate(t_indices):
    ax = fig.add_subplot(2, 2, v_idx + 1, projection='3d')

    # Lake bottom
    ax.plot_surface(X, Y, Z_bottom, alpha=0.5, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)

    # Water surface with elevation
    Z_water = elev[t_idx, :, :]
    Z_water[~mask] = np.nan

    ax.plot_surface(X, Y, Z_water, alpha=0.6, cmap='RdBu',
                    vmin=-3, vmax=1, shade=False)

    # Stations
    for si, sj, sname in station_markers:
        if mask[sj, si]:
            ax.scatter(si, sj, elev[t_idx, sj, si], color='red', s=40, marker='v', zorder=5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('水位 (m)')
    ax.set_title(f'水面高程 (第{time2d[t_idx]:.0f}天)', fontsize=11, fontweight='bold')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(-max_depth * 1.1, 1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D05_water_surface.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D05_water_surface.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-6: 3D temperature volume at lake center (vertical structure)')
print('=' * 70)

# Find lake center (deepest point)
iy, ix = np.unravel_index(np.nanargmax(bathymetry), bathymetry.shape)
depth_c = bathymetry[iy, ix]

fig = plt.figure(figsize=(18, 14))

# 3D view of temperature at lake center over depth
view_angles_center = [(30, -60), (20, -30), (45, 45), (15, 0)]

for v_idx, (elev_angle, azim) in enumerate(view_angles_center):
    ax = fig.add_subplot(2, 2, v_idx + 1, projection='3d')

    # Lake bottom
    ax.plot_surface(X, Y, Z_bottom, alpha=0.3, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)

    # Plot temperature at each sigma layer as semi-transparent surfaces
    t_idx = n_time // 2
    for k in range(n_sigma):
        temp_k = temp3d[t_idx, k, :, :]
        # Depth of this layer
        z_k = -sigma[k] * bathymetry
        z_k[~mask] = np.nan

        # Only plot a few key layers to avoid clutter
        if k % 2 == 0 or k == n_sigma - 1:
            temp_norm = (temp_k - np.nanmin(temp_k)) / max(np.nanmax(temp_k) - np.nanmin(temp_k), 0.1)
            temp_norm[~mask] = np.nan
            ax.plot_surface(X, Y, z_k, alpha=0.3,
                            facecolors=plt.cm.viridis(temp_norm), shade=False)

    # Mark lake center
    ax.scatter(ix, iy, 0, color='red', s=80, marker='v', zorder=5)
    ax.scatter(ix, iy, -depth_c, color='red', s=80, marker='^', zorder=5)
    ax.plot([ix, ix], [iy, iy], [0, -depth_c], color='red', linewidth=3, zorder=5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('深度 (m)')
    ax.set_title(f'湖心温度垂向结构 (第{time3d[t_idx]:.0f}天)\n视角 ({elev_angle}, {azim})',
                 fontsize=10, fontweight='bold')
    ax.view_init(elev=elev_angle, azim=azim)
    ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D06_temp_vertical_structure.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D06_temp_vertical_structure.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-7: 3D O2 distribution at surface and bottom')
print('=' * 70)

o2 = to_np(ds3d.variables['abiotic_water_sO2W'][:])
t_idx = n_time // 2

fig = plt.figure(figsize=(18, 12))

# Surface O2
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                 vmin=-max_depth, vmax=0, shade=True)
o2_surf = o2[t_idx, np.argmin(np.abs(sigma - 0.0)), :, :]
o2_norm = (o2_surf - np.nanmin(o2_surf[mask])) / max(np.nanmax(o2_surf[mask]) - np.nanmin(o2_surf[mask]), 0.1)
o2_norm[~mask] = np.nan
ax1.plot_surface(X, Y, Z_surface, alpha=0.6, cmap='GnBu',
                 facecolors=plt.cm.GnBu(o2_norm), shade=False)
for si, sj, sname in station_markers:
    if mask[sj, si]:
        ax1.scatter(si, sj, 0, color='red', s=40, marker='v', zorder=5)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('深度 (m)')
ax1.set_title(f'表层溶解氧 (第{time3d[t_idx]:.0f}天)', fontsize=11, fontweight='bold')
ax1.view_init(elev=30, azim=-60)
ax1.set_zlim(-max_depth * 1.1, max_depth * 0.1)

# Bottom O2
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                 vmin=-max_depth, vmax=0, shade=True)
o2_bot = o2[t_idx, np.argmin(np.abs(sigma - (-1.0))), :, :]
# Use bottom depth for plotting
o2_bot_z = -bathymetry * 0.95
o2_bot_z[~mask] = np.nan
o2_bot_norm = (o2_bot - np.nanmin(o2_bot[mask])) / max(np.nanmax(o2_bot[mask]) - np.nanmin(o2_bot[mask]), 0.1)
o2_bot_norm[~mask] = np.nan
ax2.plot_surface(X, Y, o2_bot_z, alpha=0.6, cmap='GnBu',
                 facecolors=plt.cm.GnBu(o2_bot_norm), shade=False)
for si, sj, sname in station_markers:
    if mask[sj, si]:
        sdepth = bathymetry[sj, si]
        ax2.scatter(si, sj, -sdepth * 0.95, color='red', s=40, marker='^', zorder=5)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('深度 (m)')
ax2.set_title(f'底层溶解氧 (第{time3d[t_idx]:.0f}天)', fontsize=11, fontweight='bold')
ax2.view_init(elev=30, azim=-60)
ax2.set_zlim(-max_depth * 1.1, max_depth * 0.1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D07_o2_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D07_o2_distribution.png')

# ============================================================
print()
print('=' * 70)
print('Figure 3D-8: 3D nutrient distribution (NH4, NO3, PO4 at surface)')
print('=' * 70)

nh4 = to_np(ds3d.variables['abiotic_water_sNH4W'][:])
no3 = to_np(ds3d.variables['abiotic_water_sNO3W'][:])
po4 = to_np(ds3d.variables['abiotic_water_sPO4W'][:])
t_idx = n_time // 2

fig = plt.figure(figsize=(18, 14))

nutrients_3d = [
    ('NH4', nh4, 'Blues', '氨氮'),
    ('NO3', no3, 'Purples', '硝酸盐'),
    ('PO4', po4, 'Reds', '磷酸盐'),
]

for n_idx, (nname, ndata, ncmap, nlabel) in enumerate(nutrients_3d):
    ax = fig.add_subplot(2, 2, n_idx + 1, projection='3d')

    ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)

    n_surf = ndata[t_idx, np.argmin(np.abs(sigma - 0.0)), :, :]
    n_min = np.nanmin(n_surf[mask])
    n_max = np.nanmax(n_surf[mask])
    n_norm = (n_surf - n_min) / max(n_max - n_min, 0.001)
    n_norm[~mask] = np.nan

    ax.plot_surface(X, Y, Z_surface, alpha=0.6, cmap=ncmap,
                    facecolors=getattr(plt.cm, ncmap)(n_norm), shade=False)

    for si, sj, sname in station_markers:
        if mask[sj, si]:
            ax.scatter(si, sj, 0, color='red', s=40, marker='v', zorder=5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('深度 (m)')
    ax.set_title(f'表层{nlabel} (第{time3d[t_idx]:.0f}天)', fontsize=11, fontweight='bold')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

# 4th panel: combined view
ax = fig.add_subplot(2, 2, 4, projection='3d')
ax.plot_surface(X, Y, Z_bottom, alpha=0.5, cmap='Blues_r',
                vmin=-max_depth, vmax=0, shade=True)
# Show all three stations
for si, sj, sname in station_markers:
    if mask[sj, si]:
        sdepth = bathymetry[sj, si]
        ax.scatter(si, sj, 0, color='red', s=60, marker='v', zorder=5)
        ax.scatter(si, sj, -sdepth, color='red', s=60, marker='^', zorder=5)
        ax.plot([si, si], [sj, sj], [0, -sdepth], color='red', linewidth=2, zorder=5)
        ax.text(si, sj, 1, sname, color='red', fontsize=9)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('深度 (m)')
ax.set_title('监测站位置', fontsize=11, fontweight='bold')
ax.view_init(elev=30, azim=-60)
ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '3D08_nutrients.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 3D08_nutrients.png')

ds3d.close()
ds2d.close()

print()
print('=' * 70)
print(f'All 3D figures saved to: {out_dir}')
print('=' * 70)
