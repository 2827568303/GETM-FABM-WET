"""
Temporal Evolution Visualization - GETM-FABM-WET
Shows complete time dynamic evolution for problem analysis.
Uses all available time records (120 days).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import netCDF4 as nc
import os

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

print(f'Time steps: {n_time} (2D: {len(time2d)})')
print(f'Sigma layers: {n_sigma}')
print(f'Time range: {time3d[0]:.0f} to {time3d[-1]:.0f} days')
print(f'Mean depth: {np.nanmean(bathymetry[mask]):.1f} m')
print(f'Max depth: {np.nanmax(bathymetry[mask]):.1f} m')

def get_surface(var_3d):
    """Get surface value (top layer, sigma closest to 0)"""
    idx_surface = np.argmin(np.abs(sigma - 0.0))
    return var_3d[:, idx_surface, :, :]

def get_bottom(var_3d):
    """Get bottom value (bottom layer, sigma closest to -1)"""
    idx_bottom = np.argmin(np.abs(sigma - (-1.0)))
    return var_3d[:, idx_bottom, :, :]

def get_depth_avg(var_3d, depth):
    """Calculate depth-averaged value from 3D variable (time, sigma, y, x)"""
    nz = var_3d.shape[1]
    dz = np.zeros_like(var_3d)
    sigma_sorted = np.sort(sigma)
    for k in range(nz):
        if k == 0:
            dz[:, k, :, :] = depth * (sigma_sorted[k+1] - sigma_sorted[k])
        elif k == nz - 1:
            dz[:, k, :, :] = depth * (sigma_sorted[k] - sigma_sorted[k-1])
        else:
            dz[:, k, :, :] = depth * 0.5 * (sigma_sorted[k+1] - sigma_sorted[k-1])
    total_dz = np.nansum(dz, axis=1)
    total_dz[total_dz == 0] = np.nan
    avg = np.nansum(var_3d * dz, axis=1) / total_dz
    return avg

# Find lake center index (deepest point)
iy, ix = np.unravel_index(np.nanargmax(bathymetry), bathymetry.shape)
depth_c = bathymetry[iy, ix]
print(f'Lake center: ({iy}, {ix}), depth={depth_c:.1f} m')

# Three monitoring stations (from previous analysis)
stations = [
    ('杨河滩', 27, 38),
    ('嶂山闸', 27, 41),
    ('皂河闸', 34, 5),
]

print()
print('=' * 70)
print('Figure T1: Water Level Time Series (Complete)')
print('=' * 70)

elev = to_np(ds2d.variables['elev'][:])
elev_mean = np.array([np.nanmean(elev[t, mask]) for t in range(len(time2d))])
elev_min = np.array([np.nanmin(elev[t, mask]) for t in range(len(time2d))])
elev_max = np.array([np.nanmax(elev[t, mask]) for t in range(len(time2d))])

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Plot 1: Mean water level with min/max band
ax = axes[0, 0]
ax.fill_between(time2d, elev_min, elev_max, alpha=0.3, color='blue', label='Min-Max范围')
ax.plot(time2d, elev_mean, 'b-', linewidth=2, label='平均水位')
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('湖面水位时间序列 (全部)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('水位 (m)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Water level spatial distribution at different times
ax = axes[0, 1]
selected_days = [0, len(time2d)//4, len(time2d)//2, 3*len(time2d)//4, len(time2d)-1]
for idx in selected_days:
    ax.plot(time2d[idx], elev_mean[idx], 'o', markersize=10, label=f'第{time2d[idx]:.0f}天')
ax.plot(time2d, elev_mean, '-', alpha=0.5)
ax.set_title('关键时间点水位')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('水位 (m)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Water level drop rate
ax = axes[1, 0]
if len(time2d) > 1:
    drop_rate = np.gradient(elev_mean, time2d) * 1000  # mm/day
    ax.plot(time2d[1:], drop_rate[1:], 'r-', linewidth=1.5)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_title('水位变化速率')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('速率 (mm/day)')
    ax.grid(True, alpha=0.3)

# Plot 4: Spatial water level maps at 4 time points
ax = axes[1, 1]
for i, t_idx in enumerate([0, len(time2d)//3, 2*len(time2d)//3, len(time2d)-1]):
    ax.plot([], [], 's', color=plt.cm.viridis(i/3), label=f'第{time2d[t_idx]:.0f}天')
ax.set_title('时间点标记')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('水位 (m)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T01_water_level_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T01_water_level_timeseries.png')

print()
print('=' * 70)
print('Figure T2: Water Level Spatial Evolution (4 time snapshots)')
print('=' * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 11))
snapshots = [0, len(time2d)//3, 2*len(time2d)//3, len(time2d)-1]

for i, t_idx in enumerate(snapshots):
    ax = axes[i // 2, i % 2]
    im = ax.pcolormesh(lon, lat, elev[t_idx, :, :], cmap='RdBu', vmin=-3, vmax=1)
    ax.set_title(f'水位 (第{time2d[t_idx]:.0f}天)')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='m')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T02_water_level_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T02_water_level_spatial.png')

print()
print('=' * 70)
print('Figure T3: Temperature Time Series (Surface/Mid/Bottom)')
print('=' * 70)

temp3d = to_np(ds3d.variables['temp'][:])
temp_surf = get_surface(temp3d)
temp_bot = get_bottom(temp3d)
temp_mid = temp3d[:, n_sigma // 2, :, :]

temp_surf_mean = np.array([np.nanmean(temp_surf[t, mask]) for t in range(n_time)])
temp_mid_mean = np.array([np.nanmean(temp_mid[t, mask]) for t in range(n_time)])
temp_bot_mean = np.array([np.nanmean(temp_bot[t, mask]) for t in range(n_time)])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
ax.plot(time3d, temp_surf_mean, 'r-', linewidth=2, label='表层')
ax.plot(time3d, temp_mid_mean, 'g-', linewidth=2, label='中层')
ax.plot(time3d, temp_bot_mean, 'b-', linewidth=2, label='底层')
ax.set_title('湖心温度时间序列 (表/中/底层)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('温度 (°C)')
ax.legend()
ax.grid(True, alpha=0.3)

# Temperature difference (stratification)
ax = axes[1]
temp_diff = temp_surf_mean - temp_bot_mean
ax.plot(time3d, temp_diff, 'purple', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('表底温差 (分层强度)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('温差 (°C)')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T03_temperature_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T03_temperature_timeseries.png')

print()
print('=' * 70)
print('Figure T4: Lake Center Vertical Profile Time Evolution')
print('=' * 70)

# Vertical profiles at lake center over time
fig, axes = plt.subplots(1, 3, figsize=(18, 8))

# Temperature
ax = axes[0]
z_c = -sigma * depth_c  # Positive depth: 0=surface, depth=bottom
for i, t_idx in enumerate(range(0, n_time, max(1, n_time // 8))):
    profile = temp3d[t_idx, :, iy, ix]
    ax.plot(profile, z_c, '-o', markersize=4, label=f'第{time3d[t_idx]:.0f}天', alpha=0.7)
ax.set_title('湖心温度垂向剖面演变')
ax.set_xlabel('温度 (°C)')
ax.set_ylabel('深度 (m)')
ax.legend(fontsize=8, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(z_c.max(), 0)

# Salinity (if available) or another variable
ax = axes[1]
try:
    salt3d = to_np(ds3d.variables['salt'][:])
    for i, t_idx in enumerate(range(0, n_time, max(1, n_time // 8))):
        profile = salt3d[t_idx, :, iy, ix]
        ax.plot(profile, z_c, '-o', markersize=4, label=f'第{time3d[t_idx]:.0f}天', alpha=0.7)
    ax.set_title('湖心盐度垂向剖面演变')
    ax.set_xlabel('盐度 (PSU)')
except KeyError:
    # Use O2 instead
    o2 = to_np(ds3d.variables['abiotic_water_sO2W'][:])
    for i, t_idx in enumerate(range(0, n_time, max(1, n_time // 8))):
        profile = o2[t_idx, :, iy, ix]
        ax.plot(profile, z_c, '-o', markersize=4, label=f'第{time3d[t_idx]:.0f}天', alpha=0.7)
    ax.set_title('湖心溶解氧垂向剖面演变')
    ax.set_xlabel('O2 (g/m³)')
ax.set_ylabel('深度 (m)')
ax.legend(fontsize=8, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(z_c.max(), 0)

# Velocity magnitude
ax = axes[2]
uu = to_np(ds3d.variables['uu'][:])
vv = to_np(ds3d.variables['vv'][:])
speed = np.sqrt(uu**2 + vv**2)
for i, t_idx in enumerate(range(0, n_time, max(1, n_time // 8))):
    profile = speed[t_idx, :, iy, ix]
    ax.plot(profile * 100, z_c, '-o', markersize=4, label=f'第{time3d[t_idx]:.0f}天', alpha=0.7)
ax.set_title('湖心流速垂向剖面演变')
ax.set_xlabel('流速 (cm/s)')
ax.set_ylabel('深度 (m)')
ax.legend(fontsize=8, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(z_c.max(), 0)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T04_vertical_profiles.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T04_vertical_profiles.png')

print()
print('=' * 70)
print('Figure T5: Depth-Time Heatmaps (Lake Center)')
print('=' * 70)

# Depth-time heatmaps at lake center
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Temperature
ax = axes[0, 0]
data = temp3d[:, :, iy, ix].T  # (sigma, time)
im = ax.pcolormesh(time3d, z_c, data, cmap='viridis', shading='auto')
ax.set_title('湖心温度深度-时间热图')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(z_c.max(), 0)
plt.colorbar(im, ax=ax, label='°C')

# O2
ax = axes[0, 1]
o2 = to_np(ds3d.variables['abiotic_water_sO2W'][:])
data = o2[:, :, iy, ix].T
im = ax.pcolormesh(time3d, z_c, data, cmap='GnBu', shading='auto')
ax.set_title('湖心溶解氧深度-时间热图')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(z_c.max(), 0)
plt.colorbar(im, ax=ax, label='gO2/m³')

# NH4
ax = axes[1, 0]
nh4 = to_np(ds3d.variables['abiotic_water_sNH4W'][:])
data = nh4[:, :, iy, ix].T
im = ax.pcolormesh(time3d, z_c, data, cmap='Blues', shading='auto')
ax.set_title('湖心氨氮深度-时间热图')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(z_c.max(), 0)
plt.colorbar(im, ax=ax, label='gN/m³')

# NO3
ax = axes[1, 1]
no3 = to_np(ds3d.variables['abiotic_water_sNO3W'][:])
data = no3[:, :, iy, ix].T
im = ax.pcolormesh(time3d, z_c, data, cmap='Purples', shading='auto')
ax.set_title('湖心硝酸盐深度-时间热图')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('深度 (m)')
ax.set_ylim(z_c.max(), 0)
plt.colorbar(im, ax=ax, label='gN/m³')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T05_depth_time_heatmaps.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T05_depth_time_heatmaps.png')

print()
print('=' * 70)
print('Figure T6: Nutrients Time Series (Surface vs Bottom)')
print('=' * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

nutrients = [
    ('NH4', nh4, 'gN/m³', 'Blues'),
    ('NO3', no3, 'gN/m³', 'Purples'),
    ('PO4', to_np(ds3d.variables['abiotic_water_sPO4W'][:]), 'gP/m³', 'Reds'),
    ('O2', o2, 'gO2/m³', 'GnBu'),
]

for i, (name, var, units, cmap) in enumerate(nutrients):
    ax = axes[i // 2, i % 2]
    surf_mean = np.array([np.nanmean(get_surface(var)[t, mask]) for t in range(n_time)])
    bot_mean = np.array([np.nanmean(get_bottom(var)[t, mask]) for t in range(n_time)])
    avg_mean = np.array([np.nanmean(get_depth_avg(var, bathymetry[np.newaxis, np.newaxis, :, :])[t, mask]) for t in range(n_time)])

    ax.plot(time3d, surf_mean, 'r-', linewidth=1.5, label='表层')
    ax.plot(time3d, avg_mean, 'g-', linewidth=1.5, label='垂向平均')
    ax.plot(time3d, bot_mean, 'b-', linewidth=1.5, label='底层')
    ax.set_title(f'{name} 时间序列')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel(units)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T06_nutrients_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T06_nutrients_timeseries.png')

print()
print('=' * 70)
print('Figure T7: Velocity Field Evolution (4 snapshots)')
print('=' * 70)

u_surf = get_surface(uu)
v_surf = get_surface(vv)
speed_surf = np.sqrt(u_surf**2 + v_surf**2)

fig, axes = plt.subplots(2, 2, figsize=(16, 13))
for i, t_idx in enumerate(snapshots):
    ax = axes[i // 2, i % 2]
    # Subsample for quiver
    step = 2
    lon_q = lon[::step, ::step]
    lat_q = lat[::step, ::step]
    u_q = u_surf[t_idx, ::step, ::step]
    v_q = v_surf[t_idx, ::step, ::step]

    im = ax.pcolormesh(lon, lat, speed_surf[t_idx, :, :] * 100, cmap='YlOrRd', vmin=0, vmax=10)
    ax.quiver(lon_q, lat_q, u_q, v_q, color='black', scale=0.5, width=0.002)
    ax.set_title(f'表层流速 (第{time3d[t_idx]:.0f}天)')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='cm/s')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T07_velocity_evolution.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T07_velocity_evolution.png')

print()
print('=' * 70)
print('Figure T8: Monitoring Stations Time Series')
print('=' * 70)

fig, axes = plt.subplots(3, 2, figsize=(16, 12))

for s_idx, (sname, sj, si) in enumerate(stations):
    # Water level
    ax = axes[s_idx, 0]
    # Note: 2D variables are (time, y, x) - note riverinfo uses (i, j) = (x, y)
    # But nc variables use (time, y, x) = (time, j, i)
    s_elev = elev[:, sj, si]
    ax.plot(time2d, s_elev, 'b-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax.set_title(f'{sname} 水位时间序列')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('水位 (m)')
    ax.grid(True, alpha=0.3)

    # Temperature (surface vs bottom)
    ax = axes[s_idx, 1]
    s_temp_surf = temp3d[:, -1, sj, si]  # surface (sigma closest to 0 is last)
    s_temp_bot = temp3d[:, 0, sj, si]    # bottom (sigma closest to -1 is first)
    ax.plot(time3d, s_temp_surf, 'r-', linewidth=1.5, label='表层')
    ax.plot(time3d, s_temp_bot, 'b-', linewidth=1.5, label='底层')
    ax.set_title(f'{sname} 温度时间序列')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('温度 (°C)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T08_stations_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T08_stations_timeseries.png')

print()
print('=' * 70)
print('Figure T9: Phytoplankton Time Series (3 groups)')
print('=' * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

phyto_groups = ['cyanobacteria', 'diatoms', 'greens']
phyto_colors = {'cyanobacteria': 'teal', 'diatoms': 'goldenrod', 'greens': 'green'}

for i, group in enumerate(phyto_groups):
    var_name = f'{group}_sDW'
    if var_name not in ds3d.variables:
        continue
    dw = to_np(ds3d.variables[var_name][:])
    surf_mean = np.array([np.nanmean(get_surface(dw)[t, mask]) for t in range(n_time)])
    bot_mean = np.array([np.nanmean(get_bottom(dw)[t, mask]) for t in range(n_time)])

    ax = axes[i]
    ax.plot(time3d, surf_mean, 'r-', linewidth=1.5, label='表层')
    ax.plot(time3d, bot_mean, 'b-', linewidth=1.5, label='底层')
    ax.set_title(f'{group.title()} 生物量时间序列')
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('gDW/m³')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T09_phytoplankton_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T09_phytoplankton_timeseries.png')

print()
print('=' * 70)
print('Figure T10: Summary - 6-panel temporal evolution overview')
print('=' * 70)

fig, axes = plt.subplots(3, 2, figsize=(16, 15))

# 1. Water level
ax = axes[0, 0]
ax.plot(time2d, elev_mean, 'b-', linewidth=2)
ax.fill_between(time2d, elev_min, elev_max, alpha=0.2, color='blue')
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('平均水位')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('m')
ax.grid(True, alpha=0.3)

# 2. Temperature
ax = axes[0, 1]
ax.plot(time3d, temp_surf_mean, 'r-', linewidth=1.5, label='表层')
ax.plot(time3d, temp_bot_mean, 'b-', linewidth=1.5, label='底层')
ax.set_title('湖心温度')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('°C')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 3. O2
ax = axes[1, 0]
o2_surf = np.array([np.nanmean(get_surface(o2)[t, mask]) for t in range(n_time)])
o2_bot = np.array([np.nanmean(get_bottom(o2)[t, mask]) for t in range(n_time)])
ax.plot(time3d, o2_surf, 'r-', linewidth=1.5, label='表层')
ax.plot(time3d, o2_bot, 'b-', linewidth=1.5, label='底层')
ax.set_title('溶解氧')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gO2/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 4. NH4
ax = axes[1, 1]
nh4_surf = np.array([np.nanmean(get_surface(nh4)[t, mask]) for t in range(n_time)])
nh4_bot = np.array([np.nanmean(get_bottom(nh4)[t, mask]) for t in range(n_time)])
ax.plot(time3d, nh4_surf, 'r-', linewidth=1.5, label='表层')
ax.plot(time3d, nh4_bot, 'b-', linewidth=1.5, label='底层')
ax.set_title('氨氮')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('gN/m³')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 5. Velocity
ax = axes[2, 0]
speed_mean = np.array([np.nanmean(speed_surf[t, mask]) for t in range(n_time)])
ax.plot(time3d, speed_mean * 100, 'purple', linewidth=1.5)
ax.set_title('平均表层流速')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('cm/s')
ax.grid(True, alpha=0.3)

# 6. Temperature difference (stratification)
ax = axes[2, 1]
ax.plot(time3d, temp_surf_mean - temp_bot_mean, 'darkorange', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('表底温差 (分层强度)')
ax.set_xlabel('时间 (天)')
ax.set_ylabel('°C')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'T10_summary_overview.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: T10_summary_overview.png')

ds3d.close()
ds2d.close()

print()
print('=' * 70)
print(f'All temporal evolution figures saved to: {out_dir}')
print('=' * 70)
