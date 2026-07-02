"""
Theoretical Lake GETM-FABM-WET Model Output Visualization
Generates hydrodynamic + water quality time series visualizations.

Run with: python3 visualize_theoretical.py
Outputs:  ../../case/Theoretical lake/figures/T*.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import netCDF4 as nc

# Configure Chinese font
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# Paths (script-relative so it works under WSL)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'case', 'Theoretical lake'))
OUT_DIR = os.path.join(CASE_DIR, 'figures')
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def to_np(data):
    """Convert netCDF masked array to plain numpy with NaN for missing."""
    return np.ma.filled(data, np.nan)


def get_depth_avg(var_3d, depth, sigma):
    """Depth-average a 3D variable (time, sigma, y, x).

    depth: 2D bathymetry (y, x) broadcastable to the spatial dims.
    sigma: 1D sigma coordinate for this variable.
    """
    nz = var_3d.shape[1]
    sigma_sorted = np.sort(sigma)
    dz = np.zeros_like(var_3d)
    for k in range(nz):
        if k == 0:
            dz[:, k, :, :] = depth * (sigma_sorted[k + 1] - sigma_sorted[k])
        elif k == nz - 1:
            dz[:, k, :, :] = depth * (sigma_sorted[k] - sigma_sorted[k - 1])
        else:
            dz[:, k, :, :] = depth * 0.5 * (sigma_sorted[k + 1] - sigma_sorted[k - 1])
    total_dz = np.nansum(dz, axis=1)
    total_dz[total_dz == 0] = np.nan
    avg = np.nansum(var_3d * dz, axis=1) / total_dz
    return avg


def get_surface(var_3d, sigma):
    """Surface layer (sigma closest to 0)."""
    idx = np.argmin(np.abs(sigma - 0.0))
    return var_3d[:, idx, :, :]


def get_bottom(var_3d, sigma):
    """Bottom layer (sigma closest to -1)."""
    idx = np.argmin(np.abs(sigma - (-1.0)))
    return var_3d[:, idx, :, :]


def filter_valid(time_arr):
    """Return boolean mask of valid (monotonically increasing, >0) time records."""
    valid = time_arr > 0
    # Keep only the leading contiguous run of increasing values
    n = len(time_arr)
    last = -np.inf
    for i in range(n):
        if valid[i] and time_arr[i] > last:
            last = time_arr[i]
        else:
            valid[i:] = False
            break
    return valid


def spatial_mean(var, mask, axis=(1, 2)):
    """Spatial mean over wet cells, ignoring NaN."""
    # Broadcast mask to select wet cells only
    if var.ndim == 3:  # (time, y, x)
        masked = np.where(mask[np.newaxis, :, :], var, np.nan)
    elif var.ndim == 4:  # (time, sigma, y, x)
        masked = np.where(mask[np.newaxis, np.newaxis, :, :], var, np.nan)
    else:
        masked = var
    return np.nanmean(masked, axis=axis)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print('=' * 70)
print('Loading Theoretical Lake data...')
print('=' * 70)

ds2d = nc.Dataset(os.path.join(CASE_DIR, 'THEORETICAL_LAKE.2d.nc'))
ds3d = nc.Dataset(os.path.join(CASE_DIR, 'THEORETICAL_LAKE.3d.nc'))
dsout = nc.Dataset(os.path.join(CASE_DIR, 'output.nc'))
bathy_ds = nc.Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'))

# Bathymetry / coordinates (shared)
bathymetry = to_np(bathy_ds.variables['bathymetry'][:])
lonc = to_np(ds2d.variables['lonc'][:])
latc = to_np(ds2d.variables['latc'][:])
wet_mask = bathymetry > 0
mean_depth = float(np.nanmean(bathymetry))
max_depth = float(np.nanmax(bathymetry))

# Hydrodynamic time (seconds -> days), filter invalid trailing records
time2d_raw = to_np(ds2d.variables['time'][:])
time3d_raw = to_np(ds3d.variables['time'][:])
v2d = filter_valid(time2d_raw)
v3d = filter_valid(time3d_raw)
time2d = time2d_raw[v2d] / 86400.0
time3d = time3d_raw[v3d] / 86400.0
sigma3d = to_np(ds3d.variables['sigma'][:])  # 11 layers [-1.0 .. 0.0]

# FABM output time/sigma
time_out_raw = to_np(dsout.variables['time'][:])
vout = filter_valid(time_out_raw)
time_out = time_out_raw[vout] / 86400.0
sigma_out = to_np(dsout.variables['sigma'][:])  # 10 layers [-0.9 .. 0.0]

print(f'  2D records: {len(time2d)} (range {time2d[0]:.1f}-{time2d[-1]:.1f} days)')
print(f'  3D records: {len(time3d)} (range {time3d[0]:.1f}-{time3d[-1]:.1f} days)')
print(f'  FABM records: {len(time_out)} (range {time_out[0]:.1f}-{time_out[-1]:.1f} days)')
print(f'  3D sigma: {sigma3d} ({len(sigma3d)} layers)')
print(f'  FABM sigma: {sigma_out} ({len(sigma_out)} layers)')
print(f'  Mean depth: {mean_depth:.2f} m, Max depth: {max_depth:.2f} m')
print(f'  Grid: {bathymetry.shape[1]} x {bathymetry.shape[0]} (x y)')

# Lake geometry constants
NX, NY = 5, 7
# River cells (0-indexed x, y): j=0 is North (top), j=6 is South (bottom)
RIVERS = [
    ('INFL1', 4, 0, 'inflow', 'red'),    # NE inflow
    ('INFL2', 0, 0, 'inflow', 'red'),    # NW inflow
    ('OUTFL', 0, 6, 'outflow', 'blue'),  # SW outflow
]
# SE bay macrophyte region (0-indexed x>=2, y>=4)
MACRO_MASK = np.zeros((NY, NX), dtype=bool)
MACRO_MASK[4:, 2:] = True

# Depth-2D array broadcast for depth-averaging
DEPTH2D = bathymetry[np.newaxis, np.newaxis, :, :]


# ===========================================================================
# T01 - Bathymetry and rivers
# ===========================================================================
print()
print('=' * 70)
print('T01: Bathymetry and rivers')
print('=' * 70)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel 1: bathymetry
ax = axes[0]
im = ax.pcolormesh(lonc, latc, bathymetry, cmap='Blues_r', shading='nearest')
ax.set_title('理论湖地形水深')
ax.set_xlabel('经度 (°E)')
ax.set_ylabel('纬度 (°N)')
ax.set_aspect('equal')
cb = plt.colorbar(im, ax=ax, label='水深 (m)')

# Panel 2: bathymetry + rivers + macrophyte region
ax = axes[1]
im = ax.pcolormesh(lonc, latc, bathymetry, cmap='Blues_r', shading='nearest', alpha=0.6)
ax.set_title('理论湖河道位置与水草区')
ax.set_xlabel('经度 (°E)')
ax.set_ylabel('纬度 (°N)')
ax.set_aspect('equal')
plt.colorbar(im, ax=ax, label='水深 (m)')

# Macrophyte region hatched overlay
macro_region = np.zeros((NY, NX))
macro_region[MACRO_MASK] = 1
ax.contourf(lonc, latc, macro_region, levels=[0.5, 1.5], colors=['green'],
            alpha=0.25, hatches=['//'])

# River arrows
for name, ix, iy, rtype, color in RIVERS:
    rlon, rlat = lonc[iy, ix], latc[iy, ix]
    if rtype == 'inflow':
        # Arrow pointing into the lake (from outside toward center)
        dx, dy = 0.003, -0.003
        start = (rlon + dx, rlat + dy)
        ax.annotate('', xy=(rlon, rlat), xytext=start,
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
    else:
        # Arrow pointing out of the lake
        dx, dy = -0.003, -0.003
        ax.annotate('', xy=(rlon + dx, rlat + dy), xytext=(rlon, rlat),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
    ax.plot(rlon, rlat, 'o', color=color, markersize=9,
            markeredgecolor='black', markeredgewidth=1.2)
    ax.text(rlon + 0.002, rlat + 0.0015, name, fontsize=9, color=color,
            fontweight='bold')

# Legend
legend_elems = [
    mpatches.Patch(facecolor='green', alpha=0.25, hatch='//', label='水草区 (SE湾)'),
    plt.Line2D([0], [0], marker='o', color='red', linestyle='None', markersize=9, label='入流'),
    plt.Line2D([0], [0], marker='o', color='blue', linestyle='None', markersize=9, label='出流'),
]
ax.legend(handles=legend_elems, loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T01_bathymetry_rivers.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T01_bathymetry_rivers.png')


# ===========================================================================
# T02 - Water level time series
# ===========================================================================
print()
print('=' * 70)
print('T02: Water level time series')
print('=' * 70)

elev = to_np(ds2d.variables['elev'][:])[v2d, :, :]
elev_mean = spatial_mean(elev, wet_mask)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel 1: spatial-mean water level
ax = axes[0]
ax.plot(time2d, elev_mean, 'b-', linewidth=1.5)
ax.axhline(y=0.0, color='k', linestyle='--', alpha=0.5, label='初始水位 (0.0 m)')
net_change = elev_mean[-1] - elev_mean[0]
lvl_min, lvl_max = np.nanmin(elev_mean), np.nanmax(elev_mean)
ax.set_title(f'空间平均水位时间序列\n净变化={net_change:+.4f} m, 范围=[{lvl_min:.4f}, {lvl_max:.4f}] m')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('水位 (m)')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 2: water level at 3 river cells
ax = axes[1]
for name, ix, iy, rtype, color in RIVERS:
    ax.plot(time2d, elev[:, iy, ix], linewidth=1.5, label=f'{name} ({rtype})', color=color)
ax.axhline(y=0.0, color='k', linestyle='--', alpha=0.5)
ax.set_title('河道单元格水位时间序列')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('水位 (m)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T02_water_level_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T02_water_level_timeseries.png')


# ===========================================================================
# T03 - Temperature time series (surface vs bottom)
# ===========================================================================
print()
print('=' * 70)
print('T03: Temperature time series')
print('=' * 70)

temp3d = to_np(ds3d.variables['temp'][:])[v3d, :, :, :]
temp_surf = get_surface(temp3d, sigma3d)
temp_bot = get_bottom(temp3d, sigma3d)
temp_surf_mean = spatial_mean(temp_surf, wet_mask)
temp_bot_mean = spatial_mean(temp_bot, wet_mask)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax = axes[0]
ax.plot(time3d, temp_surf_mean, 'r-', linewidth=1.5, label='表层')
ax.plot(time3d, temp_bot_mean, 'b-', linewidth=1.5, label='底层')
ax.axhline(y=0.0, color='cyan', linestyle='--', alpha=0.5, label='0°C')
ax.axhline(y=4.0, color='gray', linestyle='--', alpha=0.5, label='4°C')
ax.set_title('空间平均水温时间序列')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('温度 (°C)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
temp_diff = temp_surf_mean - temp_bot_mean
ax.plot(time3d, temp_diff, 'purple', linewidth=1.5)
ax.axhline(y=0.0, color='k', linestyle='--', alpha=0.5)
ax.set_title('表底温差 (分层强度)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('温差 (°C)')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T03_temperature_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T03_temperature_timeseries.png')


# ===========================================================================
# T04 - Temperature vertical heatmap (spatial mean)
# ===========================================================================
print()
print('=' * 70)
print('T04: Temperature vertical heatmap')
print('=' * 70)

# Spatial mean over (y, x) -> (time, sigma), then transpose to (sigma, time)
temp_profile = spatial_mean(temp3d, wet_mask, axis=(2, 3)).T  # (sigma, time)
depth_axis = -np.sort(sigma3d) * mean_depth  # 0 at surface, mean_depth at bottom

fig, ax = plt.subplots(figsize=(14, 6))
im = ax.pcolormesh(time3d, depth_axis, temp_profile, cmap='RdYlBu_r', shading='auto')
ax.set_title('温度深度-时间热图 (空间平均)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(max_depth, 0)
cb = plt.colorbar(im, ax=ax, label='温度 (°C)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T04_temp_vertical_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T04_temp_vertical_heatmap.png')


# ===========================================================================
# T05 - Nutrients time series (surface, spatial mean)
# ===========================================================================
print()
print('=' * 70)
print('T05: Nutrients time series')
print('=' * 70)

nut_vars = [
    ('NH4W', 'abiotic_water_sNH4W', 'g/m$^3$', 'Blues'),
    ('NO3W', 'abiotic_water_sNO3W', 'g/m$^3$', 'Purples'),
    ('PO4W', 'abiotic_water_sPO4W', 'g/m$^3$', 'Reds'),
    ('O2W',  'abiotic_water_sO2W',  'g/m$^3$', 'GnBu'),
]
nut_data = {}
for label, vname, units, cmap in nut_vars:
    nut_data[label] = to_np(dsout.variables[vname][:])[vout, :, :, :]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for i, (label, vname, units, cmap) in enumerate(nut_vars):
    ax = axes[i // 2, i % 2]
    var = nut_data[label]
    surf = get_surface(var, sigma_out)
    surf_mean = spatial_mean(surf, wet_mask)
    vmean = np.nanmean(surf_mean)
    vmin, vmax = np.nanmin(surf_mean), np.nanmax(surf_mean)
    ax.plot(time_out, surf_mean, color='steelblue', linewidth=1.5)
    ax.set_title(f'{label} 表层浓度\n均值={vmean:.4f}, 范围=[{vmin:.4f}, {vmax:.4f}] {units}')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel(f'{units}')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T05_nutrients_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T05_nutrients_timeseries.png')


# ===========================================================================
# T05b - Nutrients vertical heatmaps
# ===========================================================================
print()
print('=' * 70)
print('T05b: Nutrients vertical heatmaps')
print('=' * 70)

depth_out = -np.sort(sigma_out) * mean_depth  # 0 at surface, 0.9*mean_depth at bottom

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for i, (label, vname, units, cmap) in enumerate(nut_vars):
    ax = axes[i // 2, i % 2]
    var = nut_data[label]
    profile = spatial_mean(var, wet_mask, axis=(2, 3)).T  # (sigma, time)
    im = ax.pcolormesh(time_out, depth_out, profile, cmap=cmap, shading='auto')
    ax.set_title(f'{label} 深度-时间热图')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('深度 (m)')
    ax.set_ylim(depth_out.max(), 0)
    plt.colorbar(im, ax=ax, label=units)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T05b_nutrients_vertical.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T05b_nutrients_vertical.png')


# ===========================================================================
# T06 - Phytoplankton time series (depth-averaged)
# ===========================================================================
print()
print('=' * 70)
print('T06: Phytoplankton time series')
print('=' * 70)

phyto_groups = [
    ('cyanobacteria_sDW', '蓝藻', 'teal'),
    ('diatoms_sDW',       '硅藻', 'goldenrod'),
    ('greens_sDW',        '绿藻', 'green'),
]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for i, (vname, cn_name, color) in enumerate(phyto_groups):
    ax = axes[i]
    var = to_np(dsout.variables[vname][:])[vout, :, :, :]
    avg = get_depth_avg(var, DEPTH2D, sigma_out)
    avg_mean = spatial_mean(avg, wet_mask)
    ax.plot(time_out, avg_mean, color=color, linewidth=1.5)
    ax.set_title(f'{cn_name} 生物量 (垂向平均)')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m$^3$')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T06_phytoplankton_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T06_phytoplankton_timeseries.png')


# ===========================================================================
# T07 - Zooplankton time series (depth-averaged)
# ===========================================================================
print()
print('=' * 70)
print('T07: Zooplankton time series')
print('=' * 70)

zoo_groups = [
    ('cladocerans_sD', '枝角类', 'darkred'),
    ('copepods_sD',    '桡足类', 'purple'),
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for i, (vname, cn_name, color) in enumerate(zoo_groups):
    ax = axes[i]
    var = to_np(dsout.variables[vname][:])[vout, :, :, :]
    avg = get_depth_avg(var, DEPTH2D, sigma_out)
    avg_mean = spatial_mean(avg, wet_mask)
    ax.plot(time_out, avg_mean, color=color, linewidth=1.5)
    ax.set_title(f'{cn_name} 生物量 (垂向平均)')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m$^3$')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T07_zooplankton_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T07_zooplankton_timeseries.png')


# ===========================================================================
# T08 - Fish time series (depth-averaged)
# ===========================================================================
print()
print('=' * 70)
print('T08: Fish time series')
print('=' * 70)

fish_groups = [
    ('JuFish_sD',  '幼鱼', 'darkorange'),
    ('AdFish_sD',  '成鱼', 'darkred'),
    ('PiscFish_sD','食鱼鱼', 'navy'),
]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for i, (vname, cn_name, color) in enumerate(fish_groups):
    ax = axes[i]
    var = to_np(dsout.variables[vname][:])[vout, :, :, :]
    avg = get_depth_avg(var, DEPTH2D, sigma_out)
    avg_mean = spatial_mean(avg, wet_mask)
    ax.plot(time_out, avg_mean, color=color, linewidth=1.5)
    ax.set_title(f'{cn_name} 生物量 (垂向平均)')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m$^3$')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T08_fish_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T08_fish_timeseries.png')


# ===========================================================================
# T09 - Macrophytes and benthos
# ===========================================================================
print()
print('=' * 70)
print('T09: Macrophytes and benthos')
print('=' * 70)

macro_sD = to_np(dsout.variables['macrophytes_sD'][:])[vout, :, :]
benthos_sD = to_np(dsout.variables['zoobenthos_sD'][:])[vout, :, :]
n_out = len(time_out)
snap_days = [0, min(180, n_out - 1), min(364, n_out - 1)]

fig = plt.figure(figsize=(18, 12))

# Panel 1-3: macrophyte spatial distribution at 3 time snapshots
for idx, t_idx in enumerate(snap_days):
    ax = fig.add_subplot(2, 3, idx + 1)
    im = ax.pcolormesh(lonc, latc, macro_sD[t_idx, :, :], cmap='YlGn', shading='nearest')
    ax.set_title(f'水草生物量 (第{time_out[t_idx]:.0f}天)')
    ax.set_xlabel('经度 (°E)')
    ax.set_ylabel('纬度 (°N)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='gDW/m$^2$')

# Panel 4: macrophyte time series - SE bay vs whole lake
ax = fig.add_subplot(2, 3, 4)
macro_bay = np.array([np.nanmean(macro_sD[t, MACRO_MASK]) for t in range(n_out)])
macro_all = spatial_mean(macro_sD, wet_mask)
ax.plot(time_out, macro_bay, 'g-', linewidth=1.5, label='SE湾平均')
ax.plot(time_out, macro_all, 'k--', linewidth=1.5, label='全湖平均')
ax.set_title('水草生物量时间序列')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m$^2$')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 5: zoobenthos time series (spatial mean)
ax = fig.add_subplot(2, 3, 5)
benthos_mean = spatial_mean(benthos_sD, wet_mask)
ax.plot(time_out, benthos_mean, 'saddlebrown', linewidth=1.5)
ax.set_title('底栖动物生物量 (空间平均)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m$^2$')
ax.grid(True, alpha=0.3)

# Panel 6: macrophyte coverage map (last snapshot) with bay outline
ax = fig.add_subplot(2, 3, 6)
final_t = n_out - 1
im = ax.pcolormesh(lonc, latc, macro_sD[final_t, :, :], cmap='YlGn', shading='nearest')
macro_region = np.zeros((NY, NX))
macro_region[MACRO_MASK] = 1
ax.contourf(lonc, latc, macro_region, levels=[0.5, 1.5], colors=['green'],
            alpha=0.15, hatches=['//'])
ax.set_title(f'水草分布 (第{time_out[final_t]:.0f}天) + SE湾')
ax.set_xlabel('经度 (°E)')
ax.set_ylabel('纬度 (°N)')
ax.set_aspect('equal')
plt.colorbar(im, ax=ax, label='gDW/m$^2$')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T09_macrophytes_benthic.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T09_macrophytes_benthic.png')


# ===========================================================================
# T10 - Organic matter
# ===========================================================================
print()
print('=' * 70)
print('T10: Organic matter')
print('=' * 70)

pom_dw = to_np(dsout.variables['POM_sDW'][:])[vout, :, :, :]
dom_dw = to_np(dsout.variables['DOM_sDW'][:])[vout, :, :, :]
pom_ds = to_np(dsout.variables['POM_sDS'][:])[vout, :, :]  # benthic 2D
dom_ds = to_np(dsout.variables['DOM_sDS'][:])[vout, :, :]  # benthic 2D

# Depth-average the water-column variables
pom_dw_avg = spatial_mean(get_depth_avg(pom_dw, DEPTH2D, sigma_out), wet_mask)
dom_dw_avg = spatial_mean(get_depth_avg(dom_dw, DEPTH2D, sigma_out), wet_mask)
pom_ds_mean = spatial_mean(pom_ds, wet_mask)
dom_ds_mean = spatial_mean(dom_ds, wet_mask)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax = axes[0]
ax.plot(time_out, pom_dw_avg, 'saddlebrown', linewidth=1.5, label='POM (颗粒有机物)')
ax.plot(time_out, dom_dw_avg, 'goldenrod', linewidth=1.5, label='DOM (溶解有机物)')
ax.set_title('水体有机物 (垂向平均)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m$^3$')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(time_out, pom_ds_mean, 'saddlebrown', linewidth=1.5, label='POM (底栖)')
ax.plot(time_out, dom_ds_mean, 'goldenrod', linewidth=1.5, label='DOM (底栖)')
ax.set_title('底栖有机物')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gDW/m$^2$')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'T10_organic_matter.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T10_organic_matter.png')


# ===========================================================================
# Cleanup
# ===========================================================================
ds2d.close()
ds3d.close()
dsout.close()
bathy_ds.close()

print()
print('=' * 70)
print(f'All figures saved to: {OUT_DIR}')
print('=' * 70)
