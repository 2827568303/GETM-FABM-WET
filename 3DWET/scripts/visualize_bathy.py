"""Visualize bathymetry with river annotations and 3D lake model.

Generates:
1. 2D bathymetry map with river positions annotated
2. 3D lake body model showing underwater topography
"""
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.font_manager as fm
import os

# Configure Chinese font
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
FIG_DIR = os.path.join(CASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Read bathymetry
ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
x = ds.variables['x'][:]  # UTM easting (m)
y = ds.variables['y'][:]  # UTM northing (m)
lonc = ds.variables['lonc'][:]
latc = ds.variables['latc'][:]
bathy = ds.variables['bathymetry'][:]  # (ny, nx), water depth in m
ds.close()

# River positions from riverinfo.dat (1-based, i=col, j=row)
rivers = [
    ('YIHE',     21, 50, '沂河',         '入湖'),
    ('LUONAN',   28,  2, '骆南河',       '入湖'),
    ('DAYUN',     2, 32, '京杭大运河',    '双向流'),
    ('ZHANGSHAN',42, 27, '嶂山闸',       '出湖'),
    ('YANGHE',   35, 28, '洋河',         '出湖'),
]

# River positions in UTM and lat/lon
river_x = []
river_y = []
river_lon = []
river_lat = []
river_names = []
river_cn_names = []
river_types = []
for name, i, j, cn_name, rtype in rivers:
    i0, j0 = i-1, j-1
    river_x.append(x[i0])
    river_y.append(y[j0])
    river_lon.append(lonc[j0, i0])
    river_lat.append(latc[j0, i0])
    river_names.append(name)
    river_cn_names.append(cn_name)
    river_types.append(rtype)

# ===========================================================================
# Figure 1: 2D Bathymetry with river annotations
# ===========================================================================
print("Generating 2D bathymetry map with rivers...")

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# --- Left panel: UTM coordinates ---
ax1 = axes[0]
# Mask land cells for plotting
bathy_plot = np.ma.masked_where(bathy <= 0, bathy)

# Custom colormap:浅蓝到深蓝
colors_list = ['#a8d5e2', '#5fa8d3', '#2980b9', '#1a5490', '#0d2d5e']
cmap = LinearSegmentedColormap.from_list('lake_depth', colors_list)

im1 = ax1.pcolormesh(x, y, bathy_plot, cmap=cmap, shading='auto')
cbar1 = plt.colorbar(im1, ax=ax1, label='水深 (m)')
cbar1.set_label('水深 (m)', fontsize=12)

# Mark rivers
for rx, ry, rn, rcn, rt in zip(river_x, river_y, river_names, river_cn_names, river_types):
    # Color by type: inflow=red, outflow=green, bidirectional=orange
    if '入湖' in rt:
        marker_color = 'red'
        marker = 'v'  # triangle down (inflow into lake)
    elif '出湖' in rt:
        marker_color = 'green'
        marker = '^'  # triangle up (outflow from lake)
    else:  # bidirectional
        marker_color = 'orange'
        marker = 'D'  # diamond
    ax1.plot(rx, ry, marker=marker, color=marker_color, markersize=12,
             markeredgecolor='black', markeredgewidth=1.5, zorder=5)
    ax1.annotate(f'{rcn}\n({rn})\n[{rt}]',
                 xy=(rx, ry), xytext=(rx + 800, ry + 800),
                 fontsize=9, color=marker_color, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=marker_color, alpha=0.8),
                 arrowprops=dict(arrowstyle='->', color=marker_color, lw=1.5))

ax1.set_xlabel('UTM 东向 (m)', fontsize=12)
ax1.set_ylabel('UTM 北向 (m)', fontsize=12)
ax1.set_title('骆马湖底部高程与河道位置 (UTM坐标)', fontsize=14)
ax1.set_aspect('equal')

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='v', color='red', label='入湖河流 (inflow)',
           markerfacecolor='red', markersize=10, linestyle=''),
    Line2D([0], [0], marker='^', color='green', label='出湖河流 (outflow)',
           markerfacecolor='green', markersize=10, linestyle=''),
    Line2D([0], [0], marker='D', color='orange', label='双向流 (bidirectional)',
           markerfacecolor='orange', markersize=10, linestyle=''),
]
ax1.legend(handles=legend_elements, loc='upper left', fontsize=10)

# --- Right panel: Lat/Lon coordinates ---
ax2 = axes[1]
lonc_plot = lonc
latc_plot = latc
im2 = ax2.pcolormesh(lonc_plot, latc_plot, bathy_plot, cmap=cmap, shading='auto')
cbar2 = plt.colorbar(im2, ax=ax2, label='水深 (m)')
cbar2.set_label('水深 (m)', fontsize=12)

for rlon, rlat, rn, rcn, rt in zip(river_lon, river_lat, river_names, river_cn_names, river_types):
    if '入湖' in rt:
        marker_color = 'red'
        marker = 'v'
    elif '出湖' in rt:
        marker_color = 'green'
        marker = '^'
    else:
        marker_color = 'orange'
        marker = 'D'
    ax2.plot(rlon, rlat, marker=marker, color=marker_color, markersize=12,
             markeredgecolor='black', markeredgewidth=1.5, zorder=5)
    ax2.annotate(f'{rcn}\n({rn})\n[{rt}]',
                 xy=(rlon, rlat), xytext=(rlon + 0.015, rlat + 0.015),
                 fontsize=9, color=marker_color, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=marker_color, alpha=0.8),
                 arrowprops=dict(arrowstyle='->', color=marker_color, lw=1.5))

ax2.set_xlabel('经度 (°E)', fontsize=12)
ax2.set_ylabel('纬度 (°N)', fontsize=12)
ax2.set_title('骆马湖底部高程与河道位置 (经纬度)', fontsize=14)
ax2.set_aspect('equal')
ax2.legend(handles=legend_elements, loc='upper left', fontsize=10)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, '00_bathymetry_rivers.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {out_path}")


# ===========================================================================
# Figure 2: 3D Lake Body Model
# ===========================================================================
print("Generating 3D lake body model...")

fig = plt.figure(figsize=(16, 12))

# --- 3D view from southeast ---
ax = fig.add_subplot(111, projection='3d')

# Create meshgrid for 3D surface
X, Y = np.meshgrid(x, y)
# Bottom elevation = water_level - depth
# Water level = 21.79m (above sea level)
# bathymetry = water depth (positive for water)
# bottom_elevation = water_level - bathymetry
WATER_LEVEL = 21.79
bottom_elev = np.where(bathy > 0, WATER_LEVEL - bathy, np.nan)

# Plot lake bottom
surf = ax.plot_surface(X/1000, Y/1000, bottom_elev, cmap='terrain',
                       alpha=0.9, edgecolor='none', rstride=1, cstride=1)

# Plot water surface (transparent blue)
water_surf = np.where(bathy > 0, WATER_LEVEL, np.nan)
ax.plot_surface(X/1000, Y/1000, water_surf, color='lightblue',
                alpha=0.3, edgecolor='none', rstride=1, cstride=1)

# Mark rivers on 3D plot
for rx, ry, rn, rcn, rt in zip(river_x, river_y, river_names, river_cn_names, river_types):
    if '入湖' in rt:
        marker_color = 'red'
        marker = 'v'
    elif '出湖' in rt:
        marker_color = 'green'
        marker = '^'
    else:
        marker_color = 'orange'
        marker = 'D'
    # Place marker at water surface level
    ax.scatter(rx/1000, ry/1000, WATER_LEVEL, color=marker_color, marker=marker,
               s=100, edgecolor='black', linewidth=1.5, zorder=5)
    ax.text(rx/1000 + 0.3, ry/1000 + 0.3, WATER_LEVEL + 1,
            f'{rcn}', color=marker_color, fontsize=9, fontweight='bold')

# Labels
ax.set_xlabel('UTM 东向 (km)', fontsize=11, labelpad=10)
ax.set_ylabel('UTM 北向 (km)', fontsize=11, labelpad=10)
ax.set_zlabel('高程 (m)', fontsize=11, labelpad=10)
ax.set_title('骆马湖三维湖体模型\n(水位 21.79m, 网格 500m×500m)', fontsize=14, pad=20)

# Set viewing angle (southeast, slightly elevated)
ax.view_init(elev=35, azim=-60)

# Add colorbar
m = plt.cm.ScalarMappable(cmap='terrain')
m.set_array(bottom_elev.ravel())
cbar = plt.colorbar(m, ax=ax, shrink=0.5, pad=0.1)
cbar.set_label('湖底高程 (m)', fontsize=11)

# Set z-axis limits
ax.set_zlim(bottom_elev[np.isfinite(bottom_elev)].min() - 1, WATER_LEVEL + 2)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, '00_3d_lake_model.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {out_path}")


# ===========================================================================
# Figure 3: 3D Lake Body - top-down view with depth
# ===========================================================================
print("Generating 3D lake body (top-down depth view)...")

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot water depth as 3D surface (inverted: deeper = lower)
depth_plot = np.where(bathy > 0, -bathy, np.nan)
surf = ax.plot_surface(X/1000, Y/1000, depth_plot, cmap='Blues_r',
                       alpha=0.9, edgecolor='none', rstride=1, cstride=1)

# Mark rivers
for rx, ry, rn, rcn, rt in zip(river_x, river_y, river_names, river_cn_names, river_types):
    if '入湖' in rt:
        marker_color = 'red'
        marker = 'v'
    elif '出湖' in rt:
        marker_color = 'green'
        marker = '^'
    else:
        marker_color = 'orange'
        marker = 'D'
    # Get depth at river position
    i0 = np.argmin(np.abs(x - rx))
    j0 = np.argmin(np.abs(y - ry))
    river_depth = -bathy[j0, i0] if bathy[j0, i0] > 0 else 0
    ax.scatter(rx/1000, ry/1000, river_depth, color=marker_color, marker=marker,
               s=100, edgecolor='black', linewidth=1.5, zorder=5)
    ax.text(rx/1000 + 0.3, ry/1000 + 0.3, river_depth + 0.5,
            f'{rcn}', color=marker_color, fontsize=9, fontweight='bold')

ax.set_xlabel('UTM 东向 (km)', fontsize=11, labelpad=10)
ax.set_ylabel('UTM 北向 (km)', fontsize=11, labelpad=10)
ax.set_zlabel('水深 (m, 向下为正)', fontsize=11, labelpad=10)
ax.set_title('骆马湖三维水下地形图\n(深度视图)', fontsize=14, pad=20)

ax.view_init(elev=45, azim=-60)

m = plt.cm.ScalarMappable(cmap='Blues_r')
m.set_array(depth_plot[np.isfinite(depth_plot)].ravel())
cbar = plt.colorbar(m, ax=ax, shrink=0.5, pad=0.1)
cbar.set_label('水深 (m)', fontsize=11)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, '00_3d_lake_depth.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {out_path}")

print("\nAll bathymetry visualizations generated!")
