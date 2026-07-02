import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import netCDF4 as nc
from matplotlib import cm
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'
out_dir = os.path.join(case_dir, 'figures')
os.makedirs(out_dir, exist_ok=True)

print('Loading data...')

# 1. Load bathymetry
bathy_ds = nc.Dataset(os.path.join(case_dir, 'bathymetry.nc'))
bathymetry = bathy_ds.variables['bathymetry'][:]
lon = bathy_ds.variables['lonc'][:]
lat = bathy_ds.variables['latc'][:]
bathy_ds.close()

ny, nx = bathymetry.shape
print(f'Grid size: {nx} x {ny} = {nx*ny} cells')
print(f'Water cells: {np.sum(bathymetry > 0)}')

# 2. Load river info
rivers = []
with open(os.path.join(case_dir, 'riverinfo.dat'), 'r') as f:
    n_rivers = int(f.readline().strip())
    for _ in range(n_rivers):
        parts = f.readline().strip().split()
        rivers.append({'i': int(parts[0]), 'j': int(parts[1]), 'name': parts[2]})

# 3. Load rivers.nc for discharge time series
rivers_nc = nc.Dataset(os.path.join(case_dir, 'rivers.nc'))
river_time = rivers_nc.variables['time'][:] / 86400.0
river_data = {}
for r in rivers:
    name = r['name']
    if name in rivers_nc.variables:
        river_data[name] = rivers_nc.variables[name][:]
rivers_nc.close()

# 4. Load 2D results
ds2d = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.2d.nc'))
time2d = ds2d.variables['time'][:] / 86400.0
elev = ds2d.variables['elev'][:]
ds2d.close()

# 5. Load 3D results
ds3d = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
time3d = ds3d.variables['time'][:] / 86400.0
temp = ds3d.variables['temp'][:]
nh4 = ds3d.variables['abiotic_water_sNH4W'][:]
no3 = ds3d.variables['abiotic_water_sNO3W'][:]
po4 = ds3d.variables['abiotic_water_sPO4W'][:]
o2 = ds3d.variables['abiotic_water_sO2W'][:]
chla = ds3d.variables['wet_chla'][:]
sigma_coords = ds3d.variables['sigma'][:]
ds3d.close()

n_time = len(time3d)
n_sigma = temp.shape[1]
print(f'Time steps: {n_time}, sigma layers: {n_sigma}')

# Mask land cells
mask = bathymetry > 0

def to_np(data):
    return np.ma.filled(data, np.nan)

# ========== FIGURE 1: Lake 3D Grid (Bathymetry) ==========
print('Figure 1: 3D bathymetry...')
fig = plt.figure(figsize=(14, 10))

# 1a: 2D bathymetry map with rivers
ax1 = fig.add_subplot(2, 2, 1)
bathy_plot = np.where(mask, bathymetry, np.nan)
im = ax1.pcolormesh(lon, lat, bathy_plot, cmap='Blues_r', shading='auto')
plt.colorbar(im, ax=ax1, label='Depth (m)')
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.set_title('(a) Bathymetry Map')

# Plot rivers
for r in rivers:
    i, j, name = r['i'], r['j'], r['name']
    q = river_data.get(name, np.zeros(len(river_time)))
    color = 'red' if np.mean(q) > 0 else 'blue'
    marker = '^' if np.mean(q) > 0 else 'v'
    ax1.plot(lon[j, i], lat[j, i], marker=marker, color=color, markersize=10, 
             markeredgecolor='black', markeredgewidth=1)
    ax1.text(lon[j, i]+0.002, lat[j, i]+0.002, name, fontsize=8, 
             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

# Add grid lines
for i in range(0, nx, 5):
    ax1.axvline(lon[0, i], color='gray', alpha=0.2, linewidth=0.5)
for j in range(0, ny, 5):
    ax1.axhline(lat[j, 0], color='gray', alpha=0.2, linewidth=0.5)

# 1b: 3D surface plot
ax2 = fig.add_subplot(2, 2, 2, projection='3d')
X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
Z = np.where(mask, -bathymetry, np.nan)
surf = ax2.plot_surface(X, Y, Z, cmap='Blues_r', linewidth=0, antialiased=False, alpha=0.8)
ax2.set_xlabel('X grid')
ax2.set_ylabel('Y grid')
ax2.set_zlabel('Elevation (m)')
ax2.set_title('(b) 3D Bathymetry')
ax2.view_init(elev=30, azim=-60)

# 1c: Cross-section (middle row)
ax3 = fig.add_subplot(2, 2, 3)
mid_j = ny // 2
profile_j = mid_j
while profile_j < ny and not np.any(mask[profile_j, :]):
    profile_j += 1
depth_profile = bathymetry[profile_j, :]
x_profile = np.arange(nx)
ax3.fill_between(x_profile, -depth_profile, 0, where=mask[profile_j, :], 
                 color='steelblue', alpha=0.5)
ax3.plot(x_profile, -depth_profile, 'b-', linewidth=1.5)
ax3.set_xlabel('Grid X')
ax3.set_ylabel('Depth (m)')
ax3.set_title(f'(c) Cross-section (row {profile_j})')
ax3.grid(True, alpha=0.3)

# 1d: Vertical sigma layers at one point
ax4 = fig.add_subplot(2, 2, 4)
# Find a deep water point
max_depth_idx = np.unravel_index(np.argmax(np.where(mask, bathymetry, 0)), bathymetry.shape)
pj, pi = max_depth_idx
depth_here = bathymetry[pj, pi]
sigma_faces = np.linspace(-1, 0, n_sigma + 1)
sigma_centers = 0.5 * (sigma_faces[:-1] + sigma_faces[1:])
z_centers = sigma_centers * depth_here
z_faces = sigma_faces * depth_here

for z in z_faces:
    ax4.axhline(z, color='steelblue', linewidth=1, alpha=0.7)
ax4.fill_between([0, 1], [z_faces[0], z_faces[0]], [z_faces[-1], z_faces[-1]],
                 color='lightblue', alpha=0.3)
for i, z in enumerate(z_centers):
    ax4.plot(0.5, z, 'ro', markersize=6)
    ax4.text(0.55, z, f'k={i} z={z:.1f}m', va='center', fontsize=8)
ax4.set_xlim(0, 1)
ax4.set_xlabel('')
ax4.set_xticks([])
ax4.set_ylabel('Depth (m)')
ax4.set_title(f'(d) Sigma layers (depth={depth_here:.1f}m)')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '01_lake_3d_grid.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== FIGURE 2: River Boundary Conditions ==========
print('Figure 2: River boundary conditions...')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 2a: Discharge time series
ax = axes[0, 0]
inflow_total = np.zeros(len(river_time))
outflow_total = np.zeros(len(river_time))
for r in rivers:
    name = r['name']
    q = river_data.get(name, None)
    if q is None:
        continue
    if np.mean(q) > 0:
        ax.plot(river_time, q, '-', label=name, linewidth=1.5)
        inflow_total += q
    else:
        ax.plot(river_time, -q, '--', label=name, linewidth=1.5)
        outflow_total += -q

ax.plot(river_time, inflow_total, 'k-', linewidth=2.5, label='Total Inflow')
ax.plot(river_time, outflow_total, 'k--', linewidth=2.5, label='Total Outflow')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Discharge (m³/s)')
ax.set_title('(a) River Discharge Time Series')
ax.legend(fontsize=8, loc='upper right')
ax.grid(True, alpha=0.3)

# 2b: River locations with flow direction
ax = axes[0, 1]
bathy_plot = np.where(mask, bathymetry, np.nan)
im = ax.pcolormesh(lon, lat, bathy_plot, cmap='Blues_r', shading='auto')
plt.colorbar(im, ax=ax, label='Depth (m)')

for r in rivers:
    i, j, name = r['i'], r['j'], r['name']
    q = river_data.get(name, np.zeros(len(river_time)))
    q_mean = np.mean(q)
    color = 'red' if q_mean > 0 else 'blue'
    
    # Arrow indicating flow direction
    dx, dy = 0.008, 0
    if q_mean > 0:
        ax.arrow(lon[j, i] - dx, lat[j, i], dx*0.8, 0, head_width=0.003, 
                 head_length=0.004, fc='red', ec='red', linewidth=1.5)
    else:
        ax.arrow(lon[j, i], lat[j, i], dx*0.8, 0, head_width=0.003, 
                 head_length=0.004, fc='blue', ec='blue', linewidth=1.5)
    
    ax.text(lon[j, i], lat[j, i] + 0.006, f'{name}\n{abs(q_mean):.1f} m³/s',
            fontsize=7, ha='center',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor=color, pad=1))

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('(b) River Locations and Mean Discharge')

# 2c: Inflow river water quality
ax = axes[1, 0]
inflow_rivers = [r for r in rivers if np.mean(river_data.get(r['name'], [0])) > 0]
# Check which WQ variables are in rivers.nc
rivers_nc2 = nc.Dataset(os.path.join(case_dir, 'rivers.nc'))
wq_vars = ['abiotic_water_sNH4W', 'abiotic_water_sNO3W', 'abiotic_water_sPO4W']
wq_labels = ['NH4 (g/m³)', 'NO3 (g/m³)', 'PO4 (g/m³)']
wq_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']

for wq_var, wq_label, color in zip(wq_vars, wq_labels, wq_colors):
    if wq_var in rivers_nc2.variables:
        data = rivers_nc2.variables[wq_var][:]
        ax.plot(river_time, data, '-', color=color, label=wq_label, linewidth=1.5)

ax.set_xlabel('Time (days)')
ax.set_ylabel('Concentration')
ax.set_title('(c) Inflow Water Quality (YIHE)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
rivers_nc2.close()

# 2d: Water balance summary
ax = axes[1, 1]
river_names = [r['name'] for r in rivers]
mean_q = [np.mean(river_data.get(r['name'], [0])) for r in rivers]
colors = ['#ff6b6b' if q > 0 else '#4ecdc4' for q in mean_q]

bars = ax.barh(river_names, mean_q, color=colors, edgecolor='black', linewidth=0.5)
ax.axvline(0, color='black', linewidth=1)
ax.set_xlabel('Mean Discharge (m³/s)')
ax.set_title('(d) Mean River Discharge')
ax.grid(True, alpha=0.3, axis='x')

total_in = sum(q for q in mean_q if q > 0)
total_out = sum(-q for q in mean_q if q < 0)
ax.text(0.02, 0.02, f'Total In: {total_in:.2f} m³/s\nTotal Out: {total_out:.2f} m³/s\nNet: {total_in-total_out:.2f} m³/s',
        transform=ax.transAxes, fontsize=9,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', pad=5))

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '02_river_boundary_conditions.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== FIGURE 3: Spatial Distribution (Day 1 vs Day 365) ==========
print('Figure 3: Spatial distribution...')
variables = [
    ('temp', 'Temperature (°C)', temp, 'YlOrRd', None),
    ('abiotic_water_sNH4W', 'NH4 (g/m³)', nh4, 'Reds', None),
    ('abiotic_water_sO2W', 'DO (g/m³)', o2, 'Blues', None),
    ('wet_chla', 'Chla (mg/m³)', chla, 'Greens', None),
]

fig, axes = plt.subplots(4, 4, figsize=(20, 18))

for row, (var_name, var_label, data, cmap, vmax) in enumerate(variables):
    # Day 1 surface
    ax = axes[row, 0]
    day1_surf = to_np(data[0, -1, :, :])
    day1_surf = np.where(mask, day1_surf, np.nan)
    if vmax is None:
        vmax_val = np.nanmax(day1_surf)
    else:
        vmax_val = vmax
    im = ax.pcolormesh(lon, lat, day1_surf, cmap=cmap, vmin=0, vmax=vmax_val, shading='auto')
    plt.colorbar(im, ax=ax, label=var_label)
    ax.set_title(f'Day 1 Surface - {var_label.split(" ")[0]}')
    ax.set_ylabel('Latitude')
    
    # Day 365 surface
    ax = axes[row, 1]
    day365_surf = to_np(data[-1, -1, :, :])
    day365_surf = np.where(mask, day365_surf, np.nan)
    im = ax.pcolormesh(lon, lat, day365_surf, cmap=cmap, vmin=0, vmax=vmax_val, shading='auto')
    plt.colorbar(im, ax=ax, label=var_label)
    ax.set_title(f'Day 365 Surface - {var_label.split(" ")[0]}')
    
    # Day 365 bottom
    ax = axes[row, 2]
    day365_bot = to_np(data[-1, 0, :, :])
    day365_bot = np.where(mask, day365_bot, np.nan)
    im = ax.pcolormesh(lon, lat, day365_bot, cmap=cmap, vmin=0, vmax=vmax_val, shading='auto')
    plt.colorbar(im, ax=ax, label=var_label)
    ax.set_title(f'Day 365 Bottom - {var_label.split(" ")[0]}')
    
    # Bottom - Surface difference
    ax = axes[row, 3]
    diff = day365_bot - day365_surf
    vmax_diff = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)))
    if vmax_diff > 0:
        im = ax.pcolormesh(lon, lat, diff, cmap='RdBu_r', vmin=-vmax_diff, vmax=vmax_diff, shading='auto')
    else:
        im = ax.pcolormesh(lon, lat, diff, cmap='RdBu_r', shading='auto')
    plt.colorbar(im, ax=ax, label=var_label)
    ax.set_title(f'Day 365 Bottom - Surface')
    ax.set_xlabel('Longitude')

for ax_row in axes:
    for ax in ax_row:
        ax.set_xticklabels([])
        ax.set_yticklabels([])

plt.suptitle('Spatial Distribution: Day 1 vs Day 365 (Surface vs Bottom)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '03_spatial_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== FIGURE 4: Time Series Evolution ==========
print('Figure 4: Time series...')
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# Compute lake-averaged values for each time step
def lake_mean(data_3d, mask, k=-1):
    n_t = data_3d.shape[0]
    means = np.zeros(n_t)
    for t in range(n_t):
        vals = to_np(data_3d[t, k, :, :])
        valid = vals[mask]
        means[t] = np.nanmean(valid) if len(valid) > 0 else np.nan
    return means

nh4_mean = lake_mean(nh4, mask)
no3_mean = lake_mean(no3, mask)
po4_mean = lake_mean(po4, mask)
o2_mean = lake_mean(o2, mask)
chla_mean = lake_mean(chla, mask)
temp_mean = lake_mean(temp, mask)

# 4a: Nutrients
ax = axes[0, 0]
ax.plot(time3d, nh4_mean, 'r-', linewidth=2, label='NH4')
ax.plot(time3d, no3_mean, 'b-', linewidth=2, label='NO3')
ax.plot(time3d, po4_mean, 'g-', linewidth=2, label='PO4')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Concentration (g/m³)')
ax.set_title('(a) Nutrient Concentration (Surface)')
ax.legend()
ax.grid(True, alpha=0.3)

# 4b: Dissolved oxygen and chlorophyll
ax = axes[0, 1]
ax2 = ax.twinx()
l1 = ax.plot(time3d, o2_mean, 'b-', linewidth=2, label='DO')
l2 = ax2.plot(time3d, chla_mean, 'g-', linewidth=2, label='Chla')
ax.set_xlabel('Time (days)')
ax.set_ylabel('DO (g/m³)', color='b')
ax2.set_ylabel('Chla (mg/m³)', color='g')
ax.set_title('(b) Dissolved Oxygen and Chlorophyll (Surface)')
lines = l1 + l2
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc='upper right')
ax.grid(True, alpha=0.3)

# 4c: Water level
ax = axes[1, 0]
elev_mean = to_np([np.nanmean(to_np(elev[t, :, :])[mask]) for t in range(len(time2d))])
ax.plot(time2d, elev_mean, 'b-', linewidth=1.5)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Water Level (m)')
ax.set_title('(c) Lake Water Level')
ax.grid(True, alpha=0.3)

# 4d: Temperature
ax = axes[1, 1]
for k in [0, n_sigma//2, n_sigma-1]:
    temp_k = to_np([np.nanmean(to_np(temp[t, k, :, :])[mask]) for t in range(n_time)])
    label = 'Bottom' if k == 0 else ('Middle' if k == n_sigma//2 else 'Surface')
    ax.plot(time3d, temp_k, '-', linewidth=1.5, label=label)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Temperature (°C)')
ax.set_title('(d) Temperature at Different Depths')
ax.legend()
ax.grid(True, alpha=0.3)

# 4e: Vertical profile at day 1, 90, 180, 365
ax = axes[2, 0]
profile_days = [0, 89, 179, 364]
for t_idx, day in zip(profile_days, [1, 90, 180, 365]):
    prof = np.zeros(n_sigma)
    for k in range(n_sigma):
        vals = to_np(nh4[t_idx, k, :, :])
        valid = vals[mask]
        prof[k] = np.mean(valid)
    z_sigma = np.linspace(-1, 0, n_sigma)
    mean_depth = np.mean(bathymetry[mask])
    z = z_sigma * mean_depth
    ax.plot(prof, z, '-o', linewidth=1.5, markersize=3, label=f'Day {day}')
ax.set_xlabel('NH4 (g/m³)')
ax.set_ylabel('Sigma depth')
ax.set_title('(e) NH4 Vertical Profile')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 4f: DO vertical profile
ax = axes[2, 1]
for t_idx, day in zip(profile_days, [1, 90, 180, 365]):
    prof = np.zeros(n_sigma)
    for k in range(n_sigma):
        vals = to_np(o2[t_idx, k, :, :])
        valid = vals[mask]
        prof[k] = np.mean(valid)
    z_sigma = np.linspace(-1, 0, n_sigma)
    mean_depth = np.mean(bathymetry[mask])
    z = z_sigma * mean_depth
    ax.plot(prof, z, '-o', linewidth=1.5, markersize=3, label=f'Day {day}')
ax.set_xlabel('DO (g/m³)')
ax.set_ylabel('Sigma depth')
ax.set_title('(f) DO Vertical Profile')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '04_time_series.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== FIGURE 5: Annual cycle heatmaps ==========
print('Figure 5: Annual cycle heatmaps...')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Depth-time diagram of lake-averaged profiles
def compute_profile_timeseries(data_3d, mask):
    n_t = data_3d.shape[0]
    n_k = data_3d.shape[1]
    prof_ts = np.zeros((n_k, n_t))
    for t in range(n_t):
        for k in range(n_k):
            vals = to_np(data_3d[t, k, :, :])
            valid = vals[mask]
            prof_ts[k, t] = np.mean(valid) if len(valid) > 0 else np.nan
    return prof_ts

# 5a: DO depth-time
ax = axes[0, 0]
o2_prof = compute_profile_timeseries(o2, mask)
im = ax.pcolormesh(time3d, np.arange(n_sigma), o2_prof, cmap='Blues', shading='auto')
plt.colorbar(im, ax=ax, label='DO (g/m³)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Sigma layer (0=bottom, top=surface)')
ax.set_title('(a) DO Depth-Time Diagram')

# 5b: NH4 depth-time
ax = axes[0, 1]
nh4_prof = compute_profile_timeseries(nh4, mask)
im = ax.pcolormesh(time3d, np.arange(n_sigma), nh4_prof, cmap='Reds', shading='auto')
plt.colorbar(im, ax=ax, label='NH4 (g/m³)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Sigma layer')
ax.set_title('(b) NH4 Depth-Time Diagram')

# 5c: Chla depth-time
ax = axes[1, 0]
chla_prof = compute_profile_timeseries(chla, mask)
im = ax.pcolormesh(time3d, np.arange(n_sigma), chla_prof, cmap='Greens', shading='auto')
plt.colorbar(im, ax=ax, label='Chla (mg/m³)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Sigma layer')
ax.set_title('(c) Chla Depth-Time Diagram')

# 5d: NO3 depth-time
ax = axes[1, 1]
no3_prof = compute_profile_timeseries(no3, mask)
im = ax.pcolormesh(time3d, np.arange(n_sigma), no3_prof, cmap='Purples', shading='auto')
plt.colorbar(im, ax=ax, label='NO3 (g/m³)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Sigma layer')
ax.set_title('(d) NO3 Depth-Time Diagram')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '05_annual_cycle_heatmaps.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f'\nAll figures saved to: {out_dir}')
print('Figures generated:')
for f in sorted(os.listdir(out_dir)):
    fpath = os.path.join(out_dir, f)
    size_kb = os.path.getsize(fpath) / 1024
    print(f'  {f} ({size_kb:.0f} KB)')
