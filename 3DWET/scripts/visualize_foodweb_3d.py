"""
Food Web 3D Visualization - GETM-FABM-WET
Visualizes all food web components in 3D:
  - 3 Phytoplankton: cyanobacteria, diatoms, greens (3D, sDW)
  - 2 Zooplankton: cladocerans, copepods (3D, sD)
  - Zoobenthos (2D benthic, sD)
  - Macrophytes (2D benthic, sD)
  - 3 Fish: JuFish, AdFish, PiscFish (3D, sD)
  - POM, DOM (3D, sDW)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import netCDF4 as nc
import os
from mpl_toolkits.mplot3d import Axes3D

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

max_depth = np.nanmax(bathymetry)
X, Y = np.meshgrid(range(nx), range(ny))
Z_bottom = -bathymetry
Z_bottom[~mask] = np.nan
Z_surface = np.zeros_like(bathymetry)
Z_surface[~mask] = np.nan

# Find surface and bottom sigma indices
idx_surf = np.argmin(np.abs(sigma - 0.0))
idx_bot = np.argmin(np.abs(sigma - (-1.0)))

# Stations
station_markers = [(37, 26, '杨河滩'), (40, 26, '嶂山闸'), (4, 33, '皂河闸')]

def get_var_3d(name):
    """Get 3D variable (time, sigma, y, x)."""
    if name in ds3d.variables:
        return to_np(ds3d.variables[name][:])
    return None

def get_var_2d(name):
    """Get 2D benthic variable (time, y, x)."""
    if name in ds3d.variables:
        return to_np(ds3d.variables[name][:])
    return None

def safe_norm(data, mask_arr):
    """Normalize data to [0,1] for colormap, handling NaN."""
    valid = data[mask_arr]
    if len(valid) == 0 or np.all(np.isnan(valid)):
        return np.zeros_like(data)
    vmin = np.nanmin(valid)
    vmax = np.nanmax(valid)
    if vmax - vmin < 1e-10:
        return np.zeros_like(data)
    norm = (data - vmin) / (vmax - vmin)
    norm[~mask_arr] = np.nan
    return norm

def plot_3d_surface_var(ax, var_3d, t_idx, cmap, label, z_layer=None):
    """Plot 3D variable surface on a 3D axis.
    z_layer: sigma index to plot (default: surface)."""
    if z_layer is None:
        z_layer = idx_surf
    ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)
    data = var_3d[t_idx, z_layer, :, :]
    norm = safe_norm(data, mask)
    ax.plot_surface(X, Y, Z_surface, alpha=0.6, cmap=cmap,
                    facecolors=getattr(plt.cm, cmap)(norm), shade=False)
    for si, sj, sname in station_markers:
        if mask[sj, si]:
            ax.scatter(si, sj, 0, color='red', s=40, marker='v', zorder=5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('深度 (m)')
    ax.set_title(label, fontsize=11, fontweight='bold')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

def plot_3d_benthic_var(ax, var_2d, t_idx, cmap, label):
    """Plot 2D benthic variable on lake bottom surface."""
    ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                    vmin=-max_depth, vmax=0, shade=True)
    data = var_2d[t_idx, :, :]
    norm = safe_norm(data, mask)
    # Plot on bottom surface
    ax.plot_surface(X, Y, Z_bottom, alpha=0.6, cmap=cmap,
                    facecolors=getattr(plt.cm, cmap)(norm), shade=False)
    for si, sj, sname in station_markers:
        if mask[sj, si]:
            sdepth = bathymetry[sj, si]
            ax.scatter(si, sj, -sdepth, color='red', s=40, marker='^', zorder=5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('深度 (m)')
    ax.set_title(label, fontsize=11, fontweight='bold')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

# ============================================================
# Load all food web variables
print()
print('Loading food web variables...')
# Phytoplankton (3D)
cyano = get_var_3d('cyanobacteria_sDW')
diatoms = get_var_3d('diatoms_sDW')
greens = get_var_3d('greens_sDW')
# Zooplankton (3D)
cladocerans = get_var_3d('cladocerans_sD')
copepods = get_var_3d('copepods_sD')
# Fish (3D)
jufish = get_var_3d('JuFish_sD')
adfish = get_var_3d('AdFish_sD')
piscfish = get_var_3d('PiscFish_sD')
# Benthic (2D)
macro_sD = get_var_2d('macrophytes_sD')
benthos_sD = get_var_2d('zoobenthos_sD')
# Organic matter (3D)
pom = get_var_3d('POM_sDW')
dom = get_var_3d('DOM_sDW')

print(f'  cyanobacteria: {"OK" if cyano is not None else "MISSING"}')
print(f'  diatoms: {"OK" if diatoms is not None else "MISSING"}')
print(f'  greens: {"OK" if greens is not None else "MISSING"}')
print(f'  cladocerans: {"OK" if cladocerans is not None else "MISSING"}')
print(f'  copepods: {"OK" if copepods is not None else "MISSING"}')
print(f'  JuFish: {"OK" if jufish is not None else "MISSING"}')
print(f'  AdFish: {"OK" if adfish is not None else "MISSING"}')
print(f'  PiscFish: {"OK" if piscfish is not None else "MISSING"}')
print(f'  macrophytes: {"OK" if macro_sD is not None else "MISSING"}')
print(f'  zoobenthos: {"OK" if benthos_sD is not None else "MISSING"}')
print(f'  POM: {"OK" if pom is not None else "MISSING"}')
print(f'  DOM: {"OK" if dom is not None else "MISSING"}')

# Use middle time step for spatial visualization
t_mid = n_time // 2

# ============================================================
print()
print('=' * 70)
print('Figure FW-1: Phytoplankton 3D (3 groups, surface)')
print('=' * 70)

fig = plt.figure(figsize=(18, 6))

phyto_vars = [
    (cyano, 'YlGn', '蓝藻 (表层)'),
    (diatoms, 'Oranges', '硅藻 (表层)'),
    (greens, 'Greens', '绿藻 (表层)'),
]

for i, (var, cmap, label) in enumerate(phyto_vars):
    if var is None:
        continue
    ax = fig.add_subplot(1, 3, i + 1, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label}\n第{time3d[t_mid]:.0f}天')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW01_phytoplankton_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW01_phytoplankton_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-2: Zooplankton 3D (2 groups, surface + bottom)')
print('=' * 70)

fig = plt.figure(figsize=(18, 12))

zoo_vars = [
    (cladocerans, 'OrRd', '枝角类'),
    (copepods, 'BuPu', '桡足类'),
]

for i, (var, cmap, label) in enumerate(zoo_vars):
    if var is None:
        continue
    # Surface
    ax = fig.add_subplot(2, 2, i * 2 + 1, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (表层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_surf)
    # Bottom
    ax = fig.add_subplot(2, 2, i * 2 + 2, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (底层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_bot)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW02_zooplankton_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW02_zooplankton_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-3: Benthic organisms 3D (macrophytes + zoobenthos)')
print('=' * 70)

fig = plt.figure(figsize=(14, 6))

benthic_vars = [
    (macro_sD, 'YlGn', '沉水植物'),
    (benthos_sD, 'OrRd', '底栖动物'),
]

for i, (var, cmap, label) in enumerate(benthic_vars):
    if var is None:
        continue
    ax = fig.add_subplot(1, 2, i + 1, projection='3d')
    plot_3d_benthic_var(ax, var, t_mid, cmap, f'{label} (底层)\n第{time3d[t_mid]:.0f}天')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW03_benthic_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW03_benthic_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-4: Fish 3D (3 groups, surface + bottom)')
print('=' * 70)

fig = plt.figure(figsize=(18, 12))

fish_vars = [
    (jufish, 'Blues', '幼鱼 JuFish'),
    (adfish, 'Greens', '成鱼 AdFish'),
    (piscfish, 'Reds', '食鱼性鱼 PiscFish'),
]

for i, (var, cmap, label) in enumerate(fish_vars):
    if var is None:
        continue
    # Surface
    ax = fig.add_subplot(2, 3, i + 1, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (表层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_surf)
    # Bottom
    ax = fig.add_subplot(2, 3, i + 4, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (底层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_bot)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW04_fish_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW04_fish_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-5: Organic matter 3D (POM + DOM, surface + bottom)')
print('=' * 70)

fig = plt.figure(figsize=(14, 12))

om_vars = [
    (pom, 'YlOrBr', '颗粒有机物 POM'),
    (dom, 'PuOr', '溶解有机物 DOM'),
]

for i, (var, cmap, label) in enumerate(om_vars):
    if var is None:
        continue
    # Surface
    ax = fig.add_subplot(2, 2, i * 2 + 1, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (表层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_surf)
    # Bottom
    ax = fig.add_subplot(2, 2, i * 2 + 2, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label} (底层)\n第{time3d[t_mid]:.0f}天', z_layer=idx_bot)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW05_organic_matter_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW05_organic_matter_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-6: Food web overview - all 10 components (surface layer)')
print('=' * 70)

fig = plt.figure(figsize=(20, 14))

all_components = [
    (cyano, 'YlGn', '蓝藻'),
    (diatoms, 'Oranges', '硅藻'),
    (greens, 'Greens', '绿藻'),
    (cladocerans, 'OrRd', '枝角类'),
    (copepods, 'BuPu', '桡足类'),
    (jufish, 'Blues', '幼鱼'),
    (adfish, 'Greens', '成鱼'),
    (piscfish, 'Reds', '食鱼性鱼'),
    (None, None, None),  # placeholder for benthic
    (None, None, None),  # placeholder for benthic
]

plot_idx = 1
# 3D variables (8 components)
for var, cmap, label in all_components[:8]:
    if var is None:
        continue
    ax = fig.add_subplot(3, 4, plot_idx, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label}\n第{time3d[t_mid]:.0f}天')
    plot_idx += 1

# Benthic variables (2 components) - plot on bottom
for var, cmap, label in [(macro_sD, 'YlGn', '沉水植物'), (benthos_sD, 'OrRd', '底栖动物')]:
    if var is None:
        continue
    ax = fig.add_subplot(3, 4, plot_idx, projection='3d')
    plot_3d_benthic_var(ax, var, t_mid, cmap, f'{label}\n第{time3d[t_mid]:.0f}天')
    plot_idx += 1

# POM and DOM
for var, cmap, label in [(pom, 'YlOrBr', 'POM'), (dom, 'PuOr', 'DOM')]:
    if var is None:
        continue
    ax = fig.add_subplot(3, 4, plot_idx, projection='3d')
    plot_3d_surface_var(ax, var, t_mid, cmap, f'{label}\n第{time3d[t_mid]:.0f}天')
    plot_idx += 1

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW06_overview_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW06_overview_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-7: Fish vertical structure at lake center (3 angles)')
print('=' * 70)

# Find lake center (deepest point)
iy, ix = np.unravel_index(np.nanargmax(bathymetry), bathymetry.shape)
depth_c = bathymetry[iy, ix]

fig = plt.figure(figsize=(18, 14))

fish_for_vertical = [
    (jufish, 'Blues', '幼鱼'),
    (adfish, 'Greens', '成鱼'),
    (piscfish, 'Reds', '食鱼性鱼'),
]

view_angles = [(30, -60), (20, -30), (45, 45)]

for f_idx, (var, cmap, label) in enumerate(fish_for_vertical):
    if var is None:
        continue
    for v_idx, (elev_angle, azim) in enumerate(view_angles):
        ax = fig.add_subplot(3, 3, f_idx * 3 + v_idx + 1, projection='3d')

        ax.plot_surface(X, Y, Z_bottom, alpha=0.3, cmap='Blues_r',
                        vmin=-max_depth, vmax=0, shade=True)

        # Plot fish at each sigma layer
        for k in range(n_sigma):
            data_k = var[t_mid, k, :, :]
            z_k = -sigma[k] * bathymetry
            z_k[~mask] = np.nan
            norm = safe_norm(data_k, mask)
            if k % 2 == 0 or k == n_sigma - 1:
                ax.plot_surface(X, Y, z_k, alpha=0.3,
                                facecolors=getattr(plt.cm, cmap)(norm), shade=False)

        # Mark lake center
        ax.scatter(ix, iy, 0, color='red', s=60, marker='v', zorder=5)
        ax.scatter(ix, iy, -depth_c, color='red', s=60, marker='^', zorder=5)
        ax.plot([ix, ix], [iy, iy], [0, -depth_c], color='red', linewidth=2, zorder=5)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('深度 (m)')
        ax.set_title(f'{label} 垂向结构\n视角 ({elev_angle}, {azim})', fontsize=10, fontweight='bold')
        ax.view_init(elev=elev_angle, azim=azim)
        ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW07_fish_vertical_3d.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW07_fish_vertical_3d.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-8: Food web time series (all components)')
print('=' * 70)

def get_mean_ts(var_3d, layer_idx=None):
    """Get mean time series at given layer (or depth-averaged if None)."""
    if var_3d is None:
        return None
    if layer_idx is not None:
        return np.array([np.nanmean(var_3d[t, layer_idx, mask]) for t in range(n_time)])
    else:
        # Depth average
        return np.array([np.nanmean(var_3d[t, :, mask]) for t in range(n_time)])

def get_mean_ts_2d(var_2d):
    """Get mean time series for 2D variable."""
    if var_2d is None:
        return None
    return np.array([np.nanmean(var_2d[t, mask]) for t in range(n_time)])

fig, axes = plt.subplots(3, 3, figsize=(18, 12))

# Phytoplankton
for i, (var, label, color) in enumerate([
    (cyano, '蓝藻', 'teal'),
    (diatoms, '硅藻', 'goldenrod'),
    (greens, '绿藻', 'green'),
]):
    if var is None:
        continue
    ax = axes[0, i]
    surf_ts = get_mean_ts(var, idx_surf)
    bot_ts = get_mean_ts(var, idx_bot)
    avg_ts = get_mean_ts(var)
    ax.plot(time3d, surf_ts, 'r-', label='表层', linewidth=1.5)
    ax.plot(time3d, avg_ts, 'g-', label='垂向平均', linewidth=1.5)
    ax.plot(time3d, bot_ts, 'b-', label='底层', linewidth=1.5)
    ax.set_title(f'{label} 生物量')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m³')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# Zooplankton
for i, (var, label) in enumerate([
    (cladocerans, '枝角类'),
    (copepods, '桡足类'),
]):
    if var is None:
        continue
    ax = axes[1, i]
    surf_ts = get_mean_ts(var, idx_surf)
    bot_ts = get_mean_ts(var, idx_bot)
    ax.plot(time3d, surf_ts, 'r-', label='表层', linewidth=1.5)
    ax.plot(time3d, bot_ts, 'b-', label='底层', linewidth=1.5)
    ax.set_title(f'{label} 生物量')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m³')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# Benthic (2D)
ax = axes[1, 2]
if macro_sD is not None:
    ax.plot(time3d, get_mean_ts_2d(macro_sD), 'darkgreen', label='沉水植物', linewidth=1.5)
if benthos_sD is not None:
    ax.plot(time3d, get_mean_ts_2d(benthos_sD), 'darkred', label='底栖动物', linewidth=1.5)
ax.set_title('底栖生物')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m²')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Fish
for i, (var, label, color) in enumerate([
    (jufish, '幼鱼', 'blue'),
    (adfish, '成鱼', 'green'),
    (piscfish, '食鱼性鱼', 'red'),
]):
    if var is None:
        continue
    ax = axes[2, i]
    surf_ts = get_mean_ts(var, idx_surf)
    bot_ts = get_mean_ts(var, idx_bot)
    avg_ts = get_mean_ts(var)
    ax.plot(time3d, surf_ts, 'r-', label='表层', linewidth=1.5)
    ax.plot(time3d, avg_ts, 'g-', label='垂向平均', linewidth=1.5)
    ax.plot(time3d, bot_ts, 'b-', label='底层', linewidth=1.5)
    ax.set_title(f'{label} 生物量')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m³')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW08_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW08_timeseries.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-9: Food web spatial evolution (3 time snapshots)')
print('=' * 70)

fig = plt.figure(figsize=(20, 18))
t_indices = [0, n_time // 2, n_time - 1]

# Show 4 key components: phytoplankton (avg), zooplankton (avg), fish (avg), macrophytes
key_components = [
    (diatoms, 'diatoms', 'Oranges', '硅藻', True),  # 3D
    (copepods, 'copepods', 'BuPu', '桡足类', True),  # 3D
    (adfish, 'AdFish', 'Greens', '成鱼', True),  # 3D
    (macro_sD, 'macrophytes', 'YlGn', '沉水植物', False),  # 2D
]

plot_idx = 1
for comp_idx, (var, vname, cmap, label, is_3d) in enumerate(key_components):
    if var is None:
        continue
    for t_idx in t_indices:
        ax = fig.add_subplot(4, 3, plot_idx, projection='3d')
        if is_3d:
            # Depth-averaged for 3D variables
            data_t = np.nanmean(var[t_idx, :, :, :], axis=0)
            ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                            vmin=-max_depth, vmax=0, shade=True)
            norm = safe_norm(data_t, mask)
            ax.plot_surface(X, Y, Z_surface, alpha=0.6, cmap=cmap,
                            facecolors=getattr(plt.cm, cmap)(norm), shade=False)
        else:
            # Benthic variable
            data_t = var[t_idx, :, :]
            ax.plot_surface(X, Y, Z_bottom, alpha=0.4, cmap='Blues_r',
                            vmin=-max_depth, vmax=0, shade=True)
            norm = safe_norm(data_t, mask)
            ax.plot_surface(X, Y, Z_bottom, alpha=0.6, cmap=cmap,
                            facecolors=getattr(plt.cm, cmap)(norm), shade=False)

        for si, sj, sname in station_markers:
            if mask[sj, si]:
                ax.scatter(si, sj, 0, color='red', s=30, marker='v', zorder=5)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('深度 (m)')
        ax.set_title(f'{label} (第{time3d[t_idx]:.0f}天)', fontsize=10, fontweight='bold')
        ax.view_init(elev=30, azim=-60)
        ax.set_zlim(-max_depth * 1.1, max_depth * 0.1)
        plot_idx += 1

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW09_spatial_evolution.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW09_spatial_evolution.png')

# ============================================================
print()
print('=' * 70)
print('Figure FW-10: Food web summary - trophic levels comparison')
print('=' * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Trophic level 1: Phytoplankton (total)
ax = axes[0, 0]
if cyano is not None and diatoms is not None and greens is not None:
    cyano_ts = get_mean_ts(cyano)
    diatom_ts = get_mean_ts(diatoms)
    green_ts = get_mean_ts(greens)
    total_phyto = cyano_ts + diatom_ts + green_ts
    ax.plot(time3d, cyano_ts, 'teal', label='蓝藻', linewidth=1.5)
    ax.plot(time3d, diatom_ts, 'goldenrod', label='硅藻', linewidth=1.5)
    ax.plot(time3d, green_ts, 'green', label='绿藻', linewidth=1.5)
    ax.plot(time3d, total_phyto, 'black', label='总计', linewidth=2, linestyle='--')
ax.set_title('营养级1: 浮游植物')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Trophic level 2: Zooplankton (total)
ax = axes[0, 1]
if cladocerans is not None and copepods is not None:
    clad_ts = get_mean_ts(cladocerans)
    cope_ts = get_mean_ts(copepods)
    total_zoo = clad_ts + cope_ts
    ax.plot(time3d, clad_ts, 'darkred', label='枝角类', linewidth=1.5)
    ax.plot(time3d, cope_ts, 'purple', label='桡足类', linewidth=1.5)
    ax.plot(time3d, total_zoo, 'black', label='总计', linewidth=2, linestyle='--')
ax.set_title('营养级2: 浮游动物')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Trophic level 3: Fish (total)
ax = axes[1, 0]
if jufish is not None and adfish is not None and piscfish is not None:
    ju_ts = get_mean_ts(jufish)
    ad_ts = get_mean_ts(adfish)
    pisc_ts = get_mean_ts(piscfish)
    total_fish = ju_ts + ad_ts + pisc_ts
    ax.plot(time3d, ju_ts, 'blue', label='幼鱼', linewidth=1.5)
    ax.plot(time3d, ad_ts, 'green', label='成鱼', linewidth=1.5)
    ax.plot(time3d, pisc_ts, 'red', label='食鱼性鱼', linewidth=1.5)
    ax.plot(time3d, total_fish, 'black', label='总计', linewidth=2, linestyle='--')
ax.set_title('营养级3: 鱼类')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Benthic + Organic matter
ax = axes[1, 1]
if macro_sD is not None:
    ax.plot(time3d, get_mean_ts_2d(macro_sD), 'darkgreen', label='沉水植物', linewidth=1.5)
if benthos_sD is not None:
    ax.plot(time3d, get_mean_ts_2d(benthos_sD), 'darkred', label='底栖动物', linewidth=1.5)
if pom is not None:
    ax.plot(time3d, get_mean_ts(pom), 'brown', label='POM', linewidth=1.5, linestyle='--')
ax.set_title('底栖生物与有机物')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m² 或 gDW/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'FW10_trophic_levels.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: FW10_trophic_levels.png')

ds3d.close()
ds2d.close()

print()
print('=' * 70)
print(f'All food web 3D figures saved to: {out_dir}')
print('=' * 70)
