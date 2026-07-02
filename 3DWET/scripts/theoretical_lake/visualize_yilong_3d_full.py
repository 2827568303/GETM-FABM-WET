"""Complete 3D visualization for Yilong Lake theoretical model.

Output:
  Z01_bathymetry_3d.png           - 3D lake bottom topography with rivers
  Z02_lake_volume_3d.png          - 3D lake body model
  Z03_water_quality_12months.png  - 12 monthly snapshots of water quality (6 variables)
  Z04_foodweb_12months.png        - 12 monthly snapshots of food web (6 variables)
  Z05_vertical_heatmap_5points.png - vertical heatmaps at 5 representative points
  Z06_temperature_12months.png    - 12 monthly temperature 3D
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

import netCDF4 as nc
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.proj3d import proj_transform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong'
FIG_DIR = os.path.join(CASE_DIR, 'figures_3d')
os.makedirs(FIG_DIR, exist_ok=True)

NX, NY = 28, 8
DX = DY = 500.0  # m


def to_np(data):
    return np.ma.filled(data, np.nan)


def patch_numrecs(filepath, num_recs):
    import struct
    with open(filepath, 'r+b') as f:
        f.seek(4)
        f.write(struct.pack('>I', num_recs))


# Patch numrecs
patch_numrecs(os.path.join(CASE_DIR, 'YILONG.2d.nc'), 730)
patch_numrecs(os.path.join(CASE_DIR, 'YILONG.3d.nc'), 730)
patch_numrecs(os.path.join(CASE_DIR, 'output.nc'), 365)

# Load bathymetry
dsb = nc.Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'), 'r')
bathy = to_np(dsb.variables['bathymetry'][:])
lonc = to_np(dsb.variables['lonc'][:])
latc = to_np(dsb.variables['latc'][:])
dsb.close()

lake_mask = bathy > 0
print(f"Lake cells: {lake_mask.sum()}/{NX*NY}")

# Load river info
rivers = {}
with open(os.path.join(CASE_DIR, 'riverinfo.dat'), 'r') as f:
    n = int(f.readline().strip())
    for line in f:
        parts = line.split()
        if len(parts) >= 3:
            i, j, name = int(parts[0]), int(parts[1]), parts[2]
            if name not in rivers:
                rivers[name] = []
            rivers[name].append((i, j))

print(f"Rivers: {list(rivers.keys())}")

# Create coordinate grids (km scale)
x_km = np.arange(NX) * DX / 1000.0  # km
y_km = np.arange(NY) * DY / 1000.0  # km
X, Y = np.meshgrid(x_km, y_km)

# ============================================================
# Z01: 3D bathymetry with river annotations
# ============================================================
print("\n=== Z01: 3D bathymetry with rivers ===")
fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(111, projection='3d')

# Mask land as NaN for 3D plot
bathy_plot = np.where(lake_mask, bathy, np.nan)

# Plot 3D surface
surf = ax.plot_surface(X, Y, bathy_plot, cmap='Blues_r', alpha=0.85,
                       rstride=1, cstride=1, linewidth=0.2, edgecolor='lightblue',
                       antialiased=True, shade=True)

# Add wireframe for depth reference
ax.plot_wireframe(X, Y, bathy_plot, color='darkblue', linewidth=0.3, alpha=0.3,
                  rstride=1, cstride=1)

# Add water surface plane
ax.plot_surface(X, Y, np.zeros_like(bathy_plot), color='lightblue', alpha=0.2,
                rstride=1, cstride=1)

# Mark rivers (3D arrows from edges)
river_colors = {'INFL1': 'green', 'INFL2': 'blue', 'INFL3': 'purple', 'OUTFL': 'red'}
river_labels = {'INFL1': '北入流', 'INFL2': '西入流(主)', 'INFL3': '南入流', 'OUTFL': '东出流'}
for name, positions in rivers.items():
    for (i, j) in positions:
        xi, yj = x_km[i-1], y_km[j-1]
        depth = bathy[j-1, i-1] if lake_mask[j-1, i-1] else 0
        color = river_colors.get(name, 'red')
        # Draw arrow on surface
        ax.scatter([xi], [yj], [0], color=color, s=150, marker='^', edgecolors='k', zorder=10,
                   label=river_labels.get(name, name) if positions[0] == (i, j) else "")
        # Add depth annotation
        ax.text(xi, yj, depth/2, f'{depth:.1f}m', fontsize=7, ha='center', color=color)

ax.set_xlabel('X方向 (km)')
ax.set_ylabel('Y方向 (km)')
ax.set_zlabel('水深 (m)')
ax.set_title('异龙湖三维湖底地形图（标注出入湖河流）\n'
             '东西长13.8km × 南北宽1.4-3.6km | 平均水深3.5m | 最大水深4.5m',
             fontsize=13, fontweight='bold')
ax.set_zlim(0, 5.5)
ax.view_init(elev=25, azim=-55)

# Legend for rivers
handles, labels = ax.get_legend_handles_labels()
if handles:
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

cbar = plt.colorbar(surf, ax=ax, shrink=0.5, aspect=15, pad=0.1)
cbar.set_label('水深 (m)')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Z01_bathymetry_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Z01_bathymetry_3d.png")

# ============================================================
# Z02: Lake volume 3D model (isosurface style)
# ============================================================
print("\n=== Z02: Lake volume 3D model ===")
fig = plt.figure(figsize=(16, 8))

# Subplot 1: Perspective view
ax1 = fig.add_subplot(121, projection='3d')

# Create volume coordinates (layered sigma -> actual depth)
n_sigma = 11
sigma_levels = np.linspace(0, 1, n_sigma)  # 0 = surface, 1 = bottom

# Bottom surface
bottom_Z = -bathy_plot  # negative downward
bottom_Z = np.where(np.isnan(bottom_Z), 0, bottom_Z)

# Draw multiple depth layers for volume effect
cmap_vol = matplotlib.colormaps['Blues'].resampled(20)
for idx, sigma in enumerate(sigma_levels[:-1]):
    layer_Z = -bathy_plot * sigma
    alpha_val = 0.15 + 0.05 * (1 - sigma)
    ax1.plot_surface(X, Y, layer_Z, color=cmap_vol(150 + int(sigma * 100)),
                     alpha=alpha_val, rstride=1, cstride=1, linewidth=0, shade=True)

# Bottom surface (most visible)
ax1.plot_surface(X, Y, bottom_Z, cmap='YlOrBr', alpha=0.9,
                 rstride=1, cstride=1, linewidth=0.2, edgecolor='tan',
                 antialiased=True)

# Water surface
ax1.plot_surface(X, Y, np.zeros_like(X), color='deepskyblue', alpha=0.3,
                 rstride=1, cstride=1)

ax1.set_xlabel('X (km)')
ax1.set_ylabel('Y (km)')
ax1.set_zlabel('深度 (m)')
ax1.set_title('(a) 三维湖体模型 - 透视视图', fontsize=12)
ax1.set_zlim(-5.5, 0.5)
ax1.view_init(elev=25, azim=-55)

# Subplot 2: Cross-section view (east-west slice at center y)
ax2 = fig.add_subplot(122, projection='3d')

# East-west cross section at j=4 (center row)
j_slice = NY // 2
bathy_slice = bathy[j_slice, :]
x_slice = x_km[lake_mask[j_slice, :]]
bathy_slice_valid = bathy_slice[lake_mask[j_slice, :]]

# Draw the cross-section as a filled polygon
if len(x_slice) > 2:
    # Create 3D cross-section
    y_pos = y_km[j_slice]
    y_width = DY / 1000.0  # one cell width

    # Draw slice as a 3D plane
    n_points = len(x_slice)
    X_slice = np.tile(x_slice, (2, 1))
    Y_slice = np.array([[y_pos - y_width/2]*n_points, [y_pos + y_width/2]*n_points])
    Z_slice_bottom = np.tile(-bathy_slice_valid, (2, 1))
    Z_slice_top = np.zeros_like(Z_slice_bottom)

    # Bottom
    ax2.plot_surface(X_slice, Y_slice, Z_slice_bottom, cmap='YlOrBr', alpha=0.9, shade=True)
    # Top (water surface)
    ax2.plot_surface(X_slice, Y_slice, Z_slice_top, color='deepskyblue', alpha=0.5, shade=True)
    # Side walls
    for side in range(2):
        ax2.plot(x_slice, [Y_slice[side, 0]]*n_points, -bathy_slice_valid,
                 color='steelblue', linewidth=2, linestyle='-')
        ax2.plot(x_slice, [Y_slice[side, 0]]*n_points, np.zeros(n_points),
                 color='deepskyblue', linewidth=2, linestyle='-')

ax2.set_xlabel('X (km)')
ax2.set_ylabel('Y (km)')
ax2.set_zlabel('深度 (m)')
ax2.set_title('(b) 东西向剖面（中心行）', fontsize=12)
ax2.set_zlim(-5.5, 0.5)
ax2.view_init(elev=15, azim=-80)

fig.suptitle('异龙湖三维湖体模型\n'
             f'湖面积: {lake_mask.sum()*DX*DY/1e6:.1f} km² | 体积: {np.nansum(bathy)*DX*DY/1e6:.0f} 万m³ | 平均水深: {np.nanmean(bathy):.1f}m',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Z02_lake_volume_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Z02_lake_volume_3d.png")

# ============================================================
# Prepare data for 12-month snapshots
# ============================================================
print("\n=== Loading 3D data for 12-month snapshots ===")

# Monthly indices (day 1, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
month_days = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

# Load output.nc variables
ds_out = nc.Dataset(os.path.join(CASE_DIR, 'output.nc'), 'r')
ds_3d = nc.Dataset(os.path.join(CASE_DIR, 'YILONG.3d.nc'), 'r')

# Water quality variables (from output.nc)
WQ_VARS = {
    'abiotic_water_sNH4W': ('NH4+ 铵氮', 'Reds', 'g/m³'),
    'abiotic_water_sNO3W': ('NO3- 硝氮', 'Blues', 'g/m³'),
    'abiotic_water_sPO4W': ('PO4³- 磷', 'Purples', 'g/m³'),
    'abiotic_water_sO2W': ('DO 溶解氧', 'Greens', 'g/m³'),
    'POM_sDW': ('POM 颗粒有机物', 'Greys', 'g/m³'),
    'DOM_sDW': ('DOM 溶解有机物', 'Oranges', 'g/m³'),
}

# Food web variables (from output.nc)
FW_VARS = {
    'diatoms_sDW': ('硅藻', 'YlGn', 'gDW/m³'),
    'greens_sDW': ('绿藻', 'YlOrBr', 'gDW/m³'),
    'cyanobacteria_sDW': ('蓝藻', 'PuBuGn', 'gDW/m³'),
    'cladocerans_sD': ('枝角类', 'Purples', 'gDW/m³'),
    'JuFish_sD': ('幼鱼', 'Oranges', 'gDW/m³'),
    'AdFish_sD': ('成鱼', 'Reds', 'gDW/m³'),
}

# Temperature from 3d.nc (has 730 records, 2 per day)
temp_data = to_np(ds_3d.variables['temp'][:])
sigma = to_np(ds_3d.variables['sigma'][:])
print(f"Temperature shape: {temp_data.shape}, sigma layers: {len(sigma)}")

# Pre-load all needed variables into memory
wq_data = {}
for var in WQ_VARS:
    if var in ds_out.variables:
        wq_data[var] = to_np(ds_out.variables[var][:])
        print(f"  {var}: shape={wq_data[var].shape}")

fw_data = {}
for var in FW_VARS:
    if var in ds_out.variables:
        fw_data[var] = to_np(ds_out.variables[var][:])
        print(f"  {var}: shape={fw_data[var].shape}")

ds_out.close()
ds_3d.close()


# ============================================================
# Z03: Water quality - 12 months x 6 variables (surface layer)
# ============================================================
print("\n=== Z03: Water quality 12 months (surface) ===")
fig, axes = plt.subplots(6, 12, figsize=(36, 16))
fig.suptitle('异龙湖水质指标空间分布 - 12个代表性月份（表层）\n'
             '富营养化湖泊水质季节变化',
             fontsize=14, fontweight='bold')

for row, (var, (label, cmap, units)) in enumerate(WQ_VARS.items()):
    if var not in wq_data:
        continue
    data = wq_data[var]
    # Compute global max for consistent color scaling (use 95th percentile)
    surf_data = data[:, 0, :, :]
    all_vals = surf_data[:, lake_mask]
    all_vals_flat = all_vals.flatten()
    vmax = np.nanpercentile(all_vals_flat, 95)
    vmin = 0
    if vmax == 0:
        vmax = 0.01

    for col, (day_idx, month_name) in enumerate(zip(month_days, month_names)):
        ax = axes[row, col]
        if day_idx < data.shape[0]:
            surf = data[day_idx, 0, :, :].copy()
        else:
            surf = data[-1, 0, :, :].copy()
        surf[~lake_mask] = np.nan
        im = ax.pcolormesh(surf, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)
        # Mark rivers
        for rname, positions in rivers.items():
            for (i, j) in positions:
                marker = 'o' if 'INFL' in rname else 's'
                color = 'green' if 'INFL' in rname else 'red'
                ax.plot(i-1, j-1, marker=marker, color=color, markersize=6, markeredgecolor='k')

        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        if row == 0:
            ax.set_title(month_name, fontsize=10, fontweight='bold')
        if col == 0:
            ax.set_ylabel(label, fontsize=9)
        # Add max value text
        val_max = np.nanmax(surf)
        ax.text(0.95, 0.05, f'{val_max:.3f}', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=7, color='white',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

    # Colorbar for each row
    cbar_ax = fig.add_axes([0.99, 0.88 - row * (0.76/6), 0.006, 0.76/6 - 0.01])
    cbar = plt.colorbar(im, cax=cbar_ax)
    cbar.set_label(units, fontsize=7)
    cbar.ax.tick_params(labelsize=6)

plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.05, wspace=0.05, hspace=0.15)
plt.savefig(os.path.join(FIG_DIR, 'Z03_water_quality_12months.png'), dpi=120, bbox_inches='tight')
plt.close()
print("  saved Z03_water_quality_12months.png")

# ============================================================
# Z04: Food web - 12 months x 6 variables (surface layer)
# ============================================================
print("\n=== Z04: Food web 12 months (surface) ===")
fig, axes = plt.subplots(6, 12, figsize=(36, 16))
fig.suptitle('异龙湖食物网空间分布 - 12个代表性月份（表层）\n'
             '浮游植物-浮游动物-鱼类季节变化',
             fontsize=14, fontweight='bold')

for row, (var, (label, cmap, units)) in enumerate(FW_VARS.items()):
    if var not in fw_data:
        continue
    data = fw_data[var]
    surf_data = data[:, 0, :, :]
    all_vals = surf_data[:, lake_mask]
    all_vals_flat = all_vals.flatten()
    vmax = np.nanpercentile(all_vals_flat, 95)
    vmin = 0
    if vmax == 0:
        vmax = 0.01

    for col, (day_idx, month_name) in enumerate(zip(month_days, month_names)):
        ax = axes[row, col]
        if day_idx < data.shape[0]:
            surf = data[day_idx, 0, :, :].copy()
        else:
            surf = data[-1, 0, :, :].copy()
        surf[~lake_mask] = np.nan
        im = ax.pcolormesh(surf, cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)

        for rname, positions in rivers.items():
            for (i, j) in positions:
                marker = 'o' if 'INFL' in rname else 's'
                color = 'green' if 'INFL' in rname else 'red'
                ax.plot(i-1, j-1, marker=marker, color=color, markersize=6, markeredgecolor='k')

        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        if row == 0:
            ax.set_title(month_name, fontsize=10, fontweight='bold')
        if col == 0:
            ax.set_ylabel(label, fontsize=9)
        val_max = np.nanmax(surf)
        ax.text(0.95, 0.05, f'{val_max:.3f}', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=7, color='white',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

    cbar_ax = fig.add_axes([0.99, 0.88 - row * (0.76/6), 0.006, 0.76/6 - 0.01])
    cbar = plt.colorbar(im, cax=cbar_ax)
    cbar.set_label(units, fontsize=7)
    cbar.ax.tick_params(labelsize=6)

plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.05, wspace=0.05, hspace=0.15)
plt.savefig(os.path.join(FIG_DIR, 'Z04_foodweb_12months.png'), dpi=120, bbox_inches='tight')
plt.close()
print("  saved Z04_foodweb_12months.png")

# ============================================================
# Z05: Temperature 12 months (3D iso-surface style)
# ============================================================
print("\n=== Z05: Temperature 12 months (3D surface) ===")
fig, axes = plt.subplots(3, 4, figsize=(20, 14), subplot_kw={'projection': '3d'})
fig.suptitle('异龙湖水温三维分布 - 12个代表性月份\n'
             '云南高原气候：冬季最低~6°C，夏季最高~26°C',
             fontsize=14, fontweight='bold')

temp_surf = temp_data[::2, 0, :, :]  # daily surface temp
print(f"temp_surf shape: {temp_surf.shape}")

for idx, (day_idx, month_name) in enumerate(zip(month_days, month_names)):
    ax = axes[idx // 4, idx % 4]
    day_2x = day_idx * 2  # 3d.nc has 2 records per day
    if day_2x < temp_data.shape[0]:
        t_data = temp_data[day_2x, :, :, :]  # (sigma, y, x)
    else:
        t_data = temp_data[-1, :, :, :]

    # Plot surface layer temperature as 3D surface
    t_surf = t_data[0, :, :].copy()
    t_surf[~lake_mask] = np.nan
    # Use depth for Z, color for temperature
    # Use actual depth (negative) for Z coordinate
    depth_surf = -bathy_plot * 0  # surface = 0 depth
    depth_surf = np.where(lake_mask, 0, np.nan)

    vmin_t, vmax_t = 5, 28
    norm = plt.Normalize(vmin_t, vmax_t)
    colors = plt.cm.RdYlBu_r(norm(t_surf))

    surf = ax.plot_surface(X, Y, depth_surf, facecolors=colors,
                           rstride=1, cstride=1, linewidth=0, shade=False, alpha=0.9)

    # Add bottom outline
    ax.contour3D(X, Y, -bathy_plot, levels=1, colors='brown', linewidths=1, alpha=0.5)

    ax.set_title(month_name, fontsize=10, fontweight='bold')
    ax.set_zlim(-5, 0.5)
    ax.view_init(elev=25, azim=-55)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([-4, -2, 0])

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
sm = plt.cm.ScalarMappable(cmap='RdYlBu_r', norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('温度 (°C)', fontsize=10)

plt.tight_layout(rect=[0, 0, 0.9, 0.95])
plt.savefig(os.path.join(FIG_DIR, 'Z05_temperature_12months_3d.png'), dpi=120, bbox_inches='tight')
plt.close()
print("  saved Z05_temperature_12months_3d.png")

# ============================================================
# Z06: Vertical heatmaps at 5 representative points
# ============================================================
print("\n=== Z06: Vertical heatmaps at 5 points ===")

# Find 5 representative points along east-west axis (center row)
# P1: west bay
# P2: west-center
# P3: center
# P4: east-center
# P5: east end
points = []
labels = []
mid_j = NY // 2

# Find all water cells in center row
water_cols = [i for i in range(NX) if lake_mask[mid_j, i]]
print(f"Center row (j={mid_j}) water columns: {len(water_cols)} (from col {water_cols[0]} to {water_cols[-1]})")

# Pick 5 evenly spaced points along the water column
fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
label_names = ['P1 西湖湾', 'P2 西湖区', 'P3 湖心', 'P4 东湖湾', 'P5 东出流区']

for frac, lname in zip(fracs, label_names):
    idx = int(frac * (len(water_cols) - 1))
    col = water_cols[idx]
    points.append((col, mid_j, lname))
    labels.append(lname)

print(f"  5 representative points: {labels}")
for i, j, name in points:
    depth = bathy[j, i]
    print(f"    {name}: ({i},{j}), depth={depth:.2f}m")

# Variables for heatmaps
HM_VARS = [
    ('temperature', '温度', 'RdYlBu_r', '°C'),
    ('diatoms_sDW', '硅藻', 'YlGn', 'gDW/m³'),
    ('cyanobacteria_sDW', '蓝藻', 'PuBuGn', 'gDW/m³'),
    ('cladocerans_sD', '枝角类', 'Purples', 'gDW/m³'),
    ('abiotic_water_sNH4W', 'NH4+', 'Reds', 'g/m³'),
    ('abiotic_water_sPO4W', 'PO4³-', 'Purples', 'g/m³'),
]

n_vars = len(HM_VARS)
n_points = len(points)
fig, axes = plt.subplots(n_vars, n_points, figsize=(22, 16))
fig.suptitle('异龙湖5个代表性点位垂向变化热图\n'
             '横轴：时间(天数) | 纵轴：深度(σ层) | 颜色：浓度',
             fontsize=14, fontweight='bold')

days_all = np.arange(365)
n_sigma_full = 11

for col, ((pi, pj, pname), plabel) in enumerate(zip(points, labels)):
    depth_here = bathy[pj, pi]

    for row, (var, vname, cmap, units) in enumerate(HM_VARS):
        ax = axes[row, col]

        # Get data at this point (time, sigma)
        if var == 'temperature':
            # from 3d.nc (730 records, 2 per day)
            data_4d = temp_data  # (time, sigma, y, x)
            # Subsample to daily (every 2nd record)
            profile = data_4d[::2, :, pj, pi]  # (365 days, sigma)
        else:
            if var not in wq_data and var not in fw_data:
                continue
            if var in wq_data:
                data_4d = wq_data[var]
            else:
                data_4d = fw_data[var]
            profile = data_4d[:, :, pj, pi]  # (time, sigma)

        # Compute vmax from 95th percentile
        vmax = np.nanpercentile(profile, 95)
        vmin = np.nanmin(profile)
        if vmax == vmin:
            vmax = vmin + 0.01

        # Transpose for heatmap: rows=sigma, cols=time
        # Flip y so that surface (sigma=0) is at top
        profile_t = profile.T  # (sigma, time)
        profile_t = profile_t[::-1, :]  # flip vertically for surface-on-top

        im = ax.pcolormesh(days_all, np.arange(profile_t.shape[0]), profile_t,
                           cmap=cmap, shading='auto', vmin=vmin, vmax=vmax)

        ax.set_xlim(0, 365)
        ax.set_xticks([0, 90, 180, 270, 365])
        ax.set_xticklabels(['1月', '4月', '7月', '10月', '1月'], fontsize=7)

        # Y-axis: show depth (m) instead of sigma index
        sigma_vals = np.linspace(0, 1, profile_t.shape[0])
        depth_vals = sigma_vals * depth_here
        y_ticks_idx = [0, profile_t.shape[0]//2, profile_t.shape[0]-1]
        y_ticks_depth = [f'{depth_vals[i]:.1f}m' for i in y_ticks_idx]
        ax.set_yticks(y_ticks_idx)
        ax.set_yticklabels(y_ticks_depth, fontsize=7)

        if col == 0:
            ax.set_ylabel(f'{vname}\n深度', fontsize=8)
        if row == 0:
            ax.set_title(f'{plabel}\n(水深{depth_here:.1f}m)', fontsize=9, fontweight='bold')

        # Add month gridlines
        for m_day in [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]:
            ax.axvline(m_day, color='white', linewidth=0.3, alpha=0.5)

        # Colorbar for each row on right edge
        if col == n_points - 1:
            cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
            cbar.set_label(units, fontsize=7)
            cbar.ax.tick_params(labelsize=6)

plt.subplots_adjust(left=0.08, right=0.94, top=0.92, bottom=0.06, wspace=0.25, hspace=0.2)
plt.savefig(os.path.join(FIG_DIR, 'Z06_vertical_heatmap_5points.png'), dpi=130, bbox_inches='tight')
plt.close()
print("  saved Z06_vertical_heatmap_5points.png")

# ============================================================
# Z07: Food web vertical heatmaps (additional detail)
# ============================================================
print("\n=== Z07: Food web vertical 3D at 4 key dates ===")
fig, axes = plt.subplots(3, 4, figsize=(20, 14), subplot_kw={'projection': '3d'})
fig.suptitle('异龙湖食物网三维分布 - 4个关键季节（硅藻/枝角类/幼鱼）\n'
             '展示垂向分布随季节的变化',
             fontsize=14, fontweight='bold')

# 4 key dates: spring bloom (day 60), summer (day 150), autumn (day 240), winter (day 330)
key_days = [60, 150, 240, 330]
key_labels = ['春季 (3月)', '夏季 (6月)', '秋季 (9月)', '冬季 (12月)']

fw_3d_vars = [
    ('diatoms_sDW', '硅藻', 'YlGn'),
    ('cyanobacteria_sDW', '蓝藻', 'PuBuGn'),
    ('cladocerans_sD', '枝角类', 'Purples'),
]

for row, (var, vname, cmap) in enumerate(fw_3d_vars):
    if var not in fw_data:
        continue
    data = fw_data[var]
    # Global vmax
    vmax = np.nanpercentile(data.flatten(), 95)
    vmin = 0

    for col, (day_idx, label) in enumerate(zip(key_days, key_labels)):
        ax = axes[row, col]
        if day_idx >= data.shape[0]:
            day_idx = data.shape[0] - 1
        d_data = data[day_idx, :, :, :]  # (sigma, y, x)

        # Plot 3 sigma layers: surface (0), middle (5), bottom (10)
        layers_to_plot = [0, 5, 10]
        for lidx in layers_to_plot:
            if lidx >= d_data.shape[0]:
                continue
            layer_data = d_data[lidx, :, :].copy()
            layer_data[~lake_mask] = np.nan
            # Z = depth at this sigma level
            z_depth = -bathy_plot * (lidx / (d_data.shape[0] - 1))
            z_depth = np.where(lake_mask, z_depth, np.nan)

            norm = plt.Normalize(vmin, vmax)
            colors = matplotlib.colormaps[cmap](norm(layer_data))
            # Set alpha for NaN
            colors[np.isnan(layer_data), 3] = 0

            alpha_val = 0.7 - 0.15 * (lidx / 10.0)
            ax.plot_surface(X, Y, z_depth, facecolors=colors,
                            rstride=1, cstride=1, linewidth=0, shade=False, alpha=alpha_val)

        ax.set_zlim(-5, 0.5)
        ax.view_init(elev=25, azim=-55)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([-4, -2, 0])
        ax.set_zticklabels(['4m', '2m', '表层'])
        if row == 0:
            ax.set_title(label, fontsize=10, fontweight='bold')
        if col == 0:
            ax.set_ylabel(vname, fontsize=10, labelpad=20)

    # Colorbar for each row
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax))
    sm.set_array([])
    cbar_ax = fig.add_axes([0.94, 0.76 - row * 0.22, 0.015, 0.18])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label('gDW/m³', fontsize=8)

plt.tight_layout(rect=[0, 0, 0.93, 0.95])
plt.savefig(os.path.join(FIG_DIR, 'Z07_foodweb_3d_4seasons.png'), dpi=120, bbox_inches='tight')
plt.close()
print("  saved Z07_foodweb_3d_4seasons.png")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print("ALL 3D VISUALIZATIONS COMPLETE")
print("="*70)
print(f"Output directory: {FIG_DIR}")
print("Files generated:")
figs = sorted(os.listdir(FIG_DIR))
for f in figs:
    if f.endswith('.png'):
        size = os.path.getsize(os.path.join(FIG_DIR, f)) / 1024
        print(f"  {f}  ({size:.0f} KB)")
