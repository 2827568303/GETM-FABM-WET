"""
Full 3D Food Web Visualization - GETM-FABM-WET
Includes: hydrodynamics, water quality, full food web (3 fish, macrophytes, 3 phytoplankton, 2 zooplankton, zoobenthos)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import netCDF4 as nc
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'
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

print(f'Time steps: {n_time}')
print(f'Sigma layers: {n_sigma}')
print(f'Domain: {bathymetry.shape[1]} x {bathymetry.shape[0]}')
print(f'Mean depth: {np.nanmean(bathymetry[mask]):.1f} m')
print(f'Max depth: {np.nanmax(bathymetry[mask]):.1f} m')

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

def get_surface(var_3d):
    """Get surface value (top layer, sigma closest to 0)"""
    idx_surface = np.argmin(np.abs(sigma - 0.0))
    return var_3d[:, idx_surface, :, :]

def get_bottom(var_3d):
    """Get bottom value (bottom layer, sigma closest to -1)"""
    idx_bottom = np.argmin(np.abs(sigma - (-1.0)))
    return var_3d[:, idx_bottom, :, :]

print()
print('=' * 70)
print('Figure 1: Lake bathymetry and grid')
print('=' * 70)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

im0 = axes[0].pcolormesh(lon, lat, bathymetry, cmap='Blues_r')
axes[0].set_title('Lake Bathymetry (m)')
axes[0].set_xlabel('X (m)')
axes[0].set_ylabel('Y (m)')
plt.colorbar(im0, ax=axes[0])
axes[0].set_aspect('equal')

rivers_x = [13000, 5500, 3000, 15500, 17000, 18500]
rivers_y = [5500, 20500, 15500, 7000, 13500, 10500]
rivers_name = ['YIHE', 'LUONAN', 'DAYUN', 'ZHANGSHAN', 'YANGHE', 'ERHE']
im1 = axes[1].pcolormesh(lon, lat, bathymetry, cmap='Blues_r', alpha=0.5)
for rx, ry, rn in zip(rivers_x, rivers_y, rivers_name):
    axes[1].plot(rx, ry, 'ro', markersize=8)
    axes[1].text(rx+300, ry+300, rn, fontsize=9, color='red')
axes[1].set_title('Lake Grid with Rivers')
axes[1].set_xlabel('X (m)')
axes[1].set_ylabel('Y (m)')
axes[1].set_aspect('equal')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '01_lake_bathymetry_grid.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 01_lake_bathymetry_grid.png')

print()
print('=' * 70)
print('Figure 2: Hydrodynamics - surface elevation and velocity')
print('=' * 70)

elev = to_np(ds2d.variables['elev'][:])
uu = to_np(ds3d.variables['uu'][:])
vv = to_np(ds3d.variables['vv'][:])
temp3d = to_np(ds3d.variables['temp'][:])

u_surf = get_surface(uu)
v_surf = get_surface(vv)
temp_surf = get_surface(temp3d)
temp_avg = get_depth_avg(temp3d, bathymetry[np.newaxis, np.newaxis, :, :])

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

t_idx = min(15, n_time - 1)

im = axes[0,0].pcolormesh(lon, lat, elev[t_idx,:,:], cmap='RdBu')
axes[0,0].set_title(f'Surface Elevation (Day {time2d[t_idx]:.0f})')
axes[0,0].set_aspect('equal')
plt.colorbar(im, ax=axes[0,0])

im = axes[0,1].pcolormesh(lon, lat, temp_surf[t_idx,:,:], cmap='viridis')
axes[0,1].set_title(f'Surface Temperature (Day {time3d[t_idx]:.0f})')
axes[0,1].set_aspect('equal')
plt.colorbar(im, ax=axes[0,1])

im = axes[0,2].pcolormesh(lon, lat, temp_avg[t_idx,:,:], cmap='viridis')
axes[0,2].set_title(f'Depth-avg Temperature (Day {time3d[t_idx]:.0f})')
axes[0,2].set_aspect('equal')
plt.colorbar(im, ax=axes[0,2])

elev_mean = np.nanmean(elev, axis=(1,2))
temp_surf_mean = np.nanmean(temp_surf, axis=(1,2))
temp_avg_mean = np.nanmean(temp_avg, axis=(1,2))
temp_bottom_mean = np.nanmean(get_bottom(temp3d), axis=(1,2))

axes[1,0].plot(time2d, elev_mean)
axes[1,0].set_title('Mean Surface Elevation')
axes[1,0].set_xlabel('Time (days)')
axes[1,0].set_ylabel('Elevation (m)')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(time3d, temp_surf_mean, label='Surface', color='red')
axes[1,1].plot(time3d, temp_avg_mean, label='Depth-avg', color='green')
axes[1,1].plot(time3d, temp_bottom_mean, label='Bottom', color='blue')
axes[1,1].set_title('Mean Temperature')
axes[1,1].set_xlabel('Time (days)')
axes[1,1].set_ylabel('Temperature (C)')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

speed_surf = np.sqrt(u_surf**2 + v_surf**2)
speed_mean = np.nanmean(speed_surf, axis=(1,2))
axes[1,2].plot(time3d, speed_mean * 100, color='purple')
axes[1,2].set_title('Mean Surface Velocity')
axes[1,2].set_xlabel('Time (days)')
axes[1,2].set_ylabel('Velocity (cm/s)')
axes[1,2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '02_hydrodynamics.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 02_hydrodynamics.png')

print()
print('=' * 70)
print('Figure 3: Water quality - nutrients and oxygen')
print('=' * 70)

nh4 = to_np(ds3d.variables['abiotic_water_sNH4W'][:])
no3 = to_np(ds3d.variables['abiotic_water_sNO3W'][:])
po4 = to_np(ds3d.variables['abiotic_water_sPO4W'][:])
o2 = to_np(ds3d.variables['abiotic_water_sO2W'][:])

fig, axes = plt.subplots(2, 4, figsize=(20, 9))

nutrients = [
    ('NH4', nh4, 'gN/m3', 'Blues'),
    ('NO3', no3, 'gN/m3', 'Purples'),
    ('PO4', po4, 'gP/m3', 'Reds'),
    ('O2', o2, 'gO2/m3', 'GnBu'),
]

for i, (name, var, units, cmap) in enumerate(nutrients):
    surf_var = get_surface(var)
    im = axes[0,i].pcolormesh(lon, lat, surf_var[t_idx,:,:], cmap=cmap)
    axes[0,i].set_title(f'Surface {name} (Day {time3d[t_idx]:.0f})')
    axes[0,i].set_aspect('equal')
    plt.colorbar(im, ax=axes[0,i])
    
    surf_mean = np.nanmean(get_surface(var), axis=(1,2))
    bot_mean = np.nanmean(get_bottom(var), axis=(1,2))
    avg_mean = np.nanmean(get_depth_avg(var, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    axes[1,i].plot(time3d, surf_mean, label='Surface', color='red')
    axes[1,i].plot(time3d, avg_mean, label='Avg', color='green')
    axes[1,i].plot(time3d, bot_mean, label='Bottom', color='blue')
    axes[1,i].set_title(f'{name} Time Series')
    axes[1,i].set_xlabel('Time (days)')
    axes[1,i].set_ylabel(units)
    axes[1,i].legend(fontsize=8)
    axes[1,i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '03_water_quality_nutrients.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 03_water_quality_nutrients.png')

print()
print('=' * 70)
print('Figure 4: Phytoplankton spatial distribution')
print('=' * 70)

phyto_groups = ['cyanobacteria', 'diatoms', 'greens']
phyto_colors = {'cyanobacteria': 'teal', 'diatoms': 'goldenrod', 'greens': 'green'}

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for i, group in enumerate(phyto_groups):
    dw = to_np(ds3d.variables[f'{group}_sDW'][:])
    chla = to_np(ds3d.variables[f'{group}_oChla'][:])
    
    surf_dw = get_surface(dw)
    avg_dw = get_depth_avg(dw, bathymetry[np.newaxis, np.newaxis, :, :])
    
    im = axes[0,i].pcolormesh(lon, lat, surf_dw[t_idx,:,:], cmap='YlGn')
    axes[0,i].set_title(f'{group.title()} Surface Biomass\n(Day {time3d[t_idx]:.0f})')
    axes[0,i].set_aspect('equal')
    plt.colorbar(im, ax=axes[0,i])
    
    surf_mean = np.nanmean(get_surface(dw), axis=(1,2))
    avg_mean = np.nanmean(avg_dw, axis=(1,2))
    bot_mean = np.nanmean(get_bottom(dw), axis=(1,2))
    
    axes[1,i].plot(time3d, surf_mean, label='Surface', color='red')
    axes[1,i].plot(time3d, avg_mean, label='Avg', color='green')
    axes[1,i].plot(time3d, bot_mean, label='Bottom', color='blue')
    axes[1,i].set_title(f'{group.title()} Biomass')
    axes[1,i].set_xlabel('Time (days)')
    axes[1,i].set_ylabel('gDW/m3')
    axes[1,i].legend(fontsize=8)
    axes[1,i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '04_phytoplankton_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 04_phytoplankton_spatial.png')

print()
print('=' * 70)
print('Figure 5: Zooplankton spatial distribution')
print('=' * 70)

zoo_groups = ['cladocerans', 'copepods']

fig, axes = plt.subplots(2, 2, figsize=(13, 10))

for i, group in enumerate(zoo_groups):
    dw = to_np(ds3d.variables[f'{group}_sD'][:])
    
    surf_dw = get_surface(dw)
    avg_dw = get_depth_avg(dw, bathymetry[np.newaxis, np.newaxis, :, :])
    
    im = axes[0,i].pcolormesh(lon, lat, surf_dw[t_idx,:,:], cmap='OrRd')
    axes[0,i].set_title(f'{group.title()} Surface Biomass\n(Day {time3d[t_idx]:.0f})')
    axes[0,i].set_aspect('equal')
    plt.colorbar(im, ax=axes[0,i])
    
    surf_mean = np.nanmean(get_surface(dw), axis=(1,2))
    avg_mean = np.nanmean(avg_dw, axis=(1,2))
    bot_mean = np.nanmean(get_bottom(dw), axis=(1,2))
    
    axes[1,i].plot(time3d, surf_mean, label='Surface', color='red')
    axes[1,i].plot(time3d, avg_mean, label='Avg', color='green')
    axes[1,i].plot(time3d, bot_mean, label='Bottom', color='blue')
    axes[1,i].set_title(f'{group.title()} Biomass')
    axes[1,i].set_xlabel('Time (days)')
    axes[1,i].set_ylabel('gDW/m3')
    axes[1,i].legend(fontsize=8)
    axes[1,i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '05_zooplankton_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 05_zooplankton_spatial.png')

print()
print('=' * 70)
print('Figure 6: Macrophytes and benthos')
print('=' * 70)

macro_sD_3d = to_np(ds3d.variables['macrophytes_sD_PV'][:])
benthos_sD_3d = to_np(ds3d.variables['zoobenthos_sD_PV'][:])

macro_sD = get_bottom(macro_sD_3d)
benthos_sD = get_bottom(benthos_sD_3d)

macro_aCov = None

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

t_idx2 = min(15, n_time - 1)

im = axes[0,0].pcolormesh(lon, lat, macro_sD[t_idx2,:,:], cmap='YlGn')
axes[0,0].set_title(f'Macrophyte Biomass (Day {time3d[t_idx2]:.0f})')
axes[0,0].set_aspect('equal')
plt.colorbar(im, ax=axes[0,0])

if macro_aCov is not None:
    im = axes[0,1].pcolormesh(lon, lat, macro_aCov[t_idx2,:,:], cmap='Greens')
    axes[0,1].set_title(f'Macrophyte Coverage (Day {time3d[t_idx2]:.0f})')
    axes[0,1].set_aspect('equal')
    plt.colorbar(im, ax=axes[0,1])
else:
    axes[0,1].text(0.5, 0.5, 'Coverage data\nnot available', ha='center', va='center', transform=axes[0,1].transAxes)
    axes[0,1].set_title('Macrophyte Coverage')

im = axes[0,2].pcolormesh(lon, lat, benthos_sD[t_idx2,:,:], cmap='OrRd')
axes[0,2].set_title(f'Zoobenthos Biomass (Day {time3d[t_idx2]:.0f})')
axes[0,2].set_aspect('equal')
plt.colorbar(im, ax=axes[0,2])

macro_mean = np.nanmean(macro_sD, axis=(1,2))
benthos_mean = np.nanmean(benthos_sD, axis=(1,2))

axes[1,0].plot(time3d, macro_mean, color='darkgreen')
axes[1,0].set_title('Macrophyte Biomass')
axes[1,0].set_xlabel('Time (days)')
axes[1,0].set_ylabel('gDW/m2')
axes[1,0].grid(True, alpha=0.3)

if macro_aCov is not None:
    macro_cov_mean = np.nanmean(macro_aCov, axis=(1,2))
    axes[1,1].plot(time3d, macro_cov_mean, color='green')
    axes[1,1].set_title('Macrophyte Coverage')
    axes[1,1].set_xlabel('Time (days)')
    axes[1,1].set_ylabel('Coverage (-)')
    axes[1,1].grid(True, alpha=0.3)
else:
    axes[1,1].text(0.5, 0.5, 'Coverage data\nnot available', ha='center', va='center', transform=axes[1,1].transAxes)
    axes[1,1].set_title('Macrophyte Coverage')

axes[1,2].plot(time3d, benthos_mean, color='saddlebrown')
axes[1,2].set_title('Zoobenthos Biomass')
axes[1,2].set_xlabel('Time (days)')
axes[1,2].set_ylabel('gDW/m2')
axes[1,2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '06_macrophytes_benthos.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 06_macrophytes_benthos.png')

print()
print('=' * 70)
print('Figure 7: Fish spatial distribution (depth-integrated)')
print('=' * 70)

fish_groups = ['PiscFish', 'AdFish', 'JuFish']
fish_names = {'PiscFish': 'Piscivorous Fish', 'AdFish': 'Benthivorous Fish (Adult)', 'JuFish': 'Planktivorous Fish (Juvenile)'}
fish_colors = {'PiscFish': 'navy', 'AdFish': 'darkred', 'JuFish': 'darkorange'}

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

for i, group in enumerate(fish_groups):
    dw_3d = to_np(ds3d.variables[f'{group}_sD'][:])
    dw_int = get_depth_avg(dw_3d, bathymetry[np.newaxis, np.newaxis, :, :]) * bathymetry[np.newaxis, :, :]
    
    im = axes[0,i].pcolormesh(lon, lat, dw_int[t_idx,:,:], cmap='BuPu')
    axes[0,i].set_title(f'{fish_names[group]}\nDepth-integrated Biomass (Day {time3d[t_idx]:.0f})')
    axes[0,i].set_aspect('equal')
    plt.colorbar(im, ax=axes[0,i])
    
    mean_dw = np.nanmean(dw_int, axis=(1,2))
    axes[1,i].plot(time3d, mean_dw, color=fish_colors[group], linewidth=2)
    axes[1,i].set_title(f'{fish_names[group]}')
    axes[1,i].set_xlabel('Time (days)')
    axes[1,i].set_ylabel('gDW/m2')
    axes[1,i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '07_fish_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 07_fish_spatial.png')

print()
print('=' * 70)
print('Figure 8: Food web time series overview')
print('=' * 70)

fig, axes = plt.subplots(3, 3, figsize=(18, 14))

ax = axes[0,0]
for group in phyto_groups:
    dw = to_np(ds3d.variables[f'{group}_sDW'][:])
    avg_mean = np.nanmean(get_depth_avg(dw, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_mean, label=group, color=phyto_colors[group])
ax.set_title('Phytoplankton Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gDW/m3')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0,1]
zoo_colors = {'cladocerans': 'darkred', 'copepods': 'purple'}
for group in zoo_groups:
    dw = to_np(ds3d.variables[f'{group}_sD'][:])
    avg_mean = np.nanmean(get_depth_avg(dw, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_mean, label=group, color=zoo_colors[group])
ax.set_title('Zooplankton Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gDW/m3')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0,2]
for group in fish_groups:
    dw_3d = to_np(ds3d.variables[f'{group}_sD'][:])
    dw_int = get_depth_avg(dw_3d, bathymetry[np.newaxis, np.newaxis, :, :]) * bathymetry[np.newaxis, :, :]
    mean_dw = np.nanmean(dw_int, axis=(1,2))
    ax.plot(time3d, mean_dw, label=fish_names[group], color=fish_colors[group], linewidth=2)
ax.set_title('Fish Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gDW/m2')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1,0]
ax.plot(time3d, np.nanmean(macro_sD, axis=(1,2)), label='Macrophytes', color='darkgreen', linewidth=2)
ax.set_title('Macrophyte Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gDW/m2')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1,1]
ax.plot(time3d, np.nanmean(benthos_sD, axis=(1,2)), label='Zoobenthos', color='saddlebrown', linewidth=2)
ax.set_title('Zoobenthos Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gDW/m2')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1,2]
total_chla = np.zeros_like(to_np(ds3d.variables['cyanobacteria_oChla'][:]))
for group in phyto_groups:
    chla = to_np(ds3d.variables[f'{group}_oChla'][:])
    total_chla += chla
chla_surf = np.nanmean(get_surface(total_chla), axis=(1,2))
chla_avg = np.nanmean(get_depth_avg(total_chla, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
ax.plot(time3d, chla_surf, label='Surface', color='red')
ax.plot(time3d, chla_avg, label='Depth-avg', color='green')
ax.set_title('Total Chlorophyll-a')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gChla/m3')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[2,0]
for name, var, units, cmap in nutrients:
    avg_mean = np.nanmean(get_depth_avg(var, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_mean, label=name)
ax.set_title('Depth-avg Nutrients')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Concentration')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[2,1]
o2_surf = np.nanmean(get_surface(o2), axis=(1,2))
o2_avg = np.nanmean(get_depth_avg(o2, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
o2_bot = np.nanmean(get_bottom(o2), axis=(1,2))
ax.plot(time3d, o2_surf, label='Surface', color='red')
ax.plot(time3d, o2_avg, label='Avg', color='green')
ax.plot(time3d, o2_bot, label='Bottom', color='blue')
ax.set_title('Dissolved Oxygen')
ax.set_xlabel('Time (days)')
ax.set_ylabel('gO2/m3')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[2,2]
temp_surf_mean = np.nanmean(temp_surf, axis=(1,2))
temp_avg_mean = np.nanmean(temp_avg, axis=(1,2))
temp_bottom_mean = np.nanmean(get_bottom(temp3d), axis=(1,2))
ax.plot(time3d, temp_surf_mean, label='Surface', color='red')
ax.plot(time3d, temp_avg_mean, label='Avg', color='green')
ax.plot(time3d, temp_bottom_mean, label='Bottom', color='blue')
ax.set_title('Water Temperature')
ax.set_xlabel('Time (days)')
ax.set_ylabel('C')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '08_foodweb_overview.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 08_foodweb_overview.png')

print()
print('=' * 70)
print('Figure 9: Vertical profiles at lake center')
print('=' * 70)

depth_center = np.unravel_index(np.nanargmax(bathymetry), bathymetry.shape)
j_c, i_c = depth_center
print(f'  Lake center at (i={i_c}, j={j_c}), depth={bathymetry[j_c, i_c]:.1f} m')

fig, axes = plt.subplots(2, 4, figsize=(18, 10))

days_to_plot = [0, 7, 15, 29]
day_indices = []
for d in days_to_plot:
    idx = np.argmin(np.abs(time3d - d))
    day_indices.append(idx)

depth_c = bathymetry[j_c, i_c]
z = sigma * depth_c

total_chla = np.zeros_like(to_np(ds3d.variables['cyanobacteria_oChla'][:]))
for group in phyto_groups:
    chla = to_np(ds3d.variables[f'{group}_oChla'][:])
    total_chla += chla

vars_to_plot = [
    ('Temperature', temp3d, 'C', 'viridis'),
    ('Chl-a', total_chla, 'g/m3', 'YlGn'),
    ('NH4', nh4, 'gN/m3', 'Blues'),
    ('O2', o2, 'gO2/m3', 'GnBu'),
]

for i, (name, var, units, cmap) in enumerate(vars_to_plot):
    ax = axes[0,i]
    for di, d in zip(day_indices, days_to_plot):
        profile = var[di, :, j_c, i_c]
        ax.plot(profile, z, label=f'Day {d}')
    ax.set_title(f'{name} Profile')
    ax.set_xlabel(units)
    ax.set_ylabel('Depth (m)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(z[-1], z[0])

pom_dw = to_np(ds3d.variables['POM_sDW'][:])
dom_dw = to_np(ds3d.variables['DOM_sDW'][:])

axes[1,0].plot(np.nanmean(get_surface(pom_dw), axis=(1,2)), time3d, label='POM surf', color='saddlebrown')
axes[1,0].plot(np.nanmean(get_depth_avg(pom_dw, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2)), time3d, label='POM avg', color='peru')
axes[1,0].set_title('POM')
axes[1,0].set_xlabel('gDW/m3')
axes[1,0].set_ylabel('Time (days)')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(np.nanmean(get_surface(dom_dw), axis=(1,2)), time3d, label='DOM surf', color='darkgoldenrod')
axes[1,1].plot(np.nanmean(get_depth_avg(dom_dw, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2)), time3d, label='DOM avg', color='goldenrod')
axes[1,1].set_title('DOM')
axes[1,1].set_xlabel('gDW/m3')
axes[1,1].set_ylabel('Time (days)')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

ax = axes[1,2]
for group in phyto_groups:
    llim = to_np(ds3d.variables[f'{group}_aLLim'][:])
    avg_llim = np.nanmean(get_depth_avg(llim, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_llim, label=group, color=phyto_colors[group])
ax.set_title('Light Limitation')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Limitation (-)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1,3]
for group in phyto_groups:
    nlim = to_np(ds3d.variables[f'{group}_aNLim'][:])
    avg_nlim = np.nanmean(get_depth_avg(nlim, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_nlim, label=f'{group} N-lim', linestyle='-')
    plim = to_np(ds3d.variables[f'{group}_aPLim'][:])
    avg_plim = np.nanmean(get_depth_avg(plim, bathymetry[np.newaxis, np.newaxis, :, :]), axis=(1,2))
    ax.plot(time3d, avg_plim, label=f'{group} P-lim', linestyle='--')
ax.set_title('Nutrient Limitation')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Limitation (-)')
ax.legend(fontsize=7, ncol=2)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '09_vertical_profiles.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 09_vertical_profiles.png')

print()
print('=' * 70)
print('Figure 10: Depth-time heatmaps at lake center')
print('=' * 70)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

heatmap_vars = [
    ('Temperature', temp3d, 'C', 'viridis'),
    ('Chlorophyll-a', total_chla, 'g/m3', 'YlGn'),
    ('Oxygen', o2, 'gO2/m3', 'GnBu'),
    ('NH4', nh4, 'gN/m3', 'Blues'),
    ('NO3', no3, 'gN/m3', 'Purples'),
    ('PO4', po4, 'gP/m3', 'Reds'),
]

for idx, (name, var, units, cmap) in enumerate(heatmap_vars):
    i_row = idx // 3
    i_col = idx % 3
    ax = axes[i_row, i_col]
    
    profile_data = var[:, :, j_c, i_c].T
    im = ax.pcolormesh(time3d, z, profile_data, cmap=cmap)
    ax.set_aspect('auto')
    ax.set_title(f'{name} at Lake Center')
    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Depth (m)')
    plt.colorbar(im, ax=ax, label=units)
    ax.set_ylim(z[-1], z[0])

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '10_depth_time_heatmaps.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 10_depth_time_heatmaps.png')

print()
print('=' * 70)
print('Figure 11: Fish vertical distribution at lake center')
print('=' * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, group in enumerate(fish_groups):
    ax = axes[i]
    dw_3d = to_np(ds3d.variables[f'{group}_sD'][:])
    profile_data = dw_3d[:, :, j_c, i_c].T
    im = ax.pcolormesh(time3d, z, profile_data, cmap='BuPu')
    ax.set_aspect('auto')
    ax.set_title(f'{fish_names[group]}')
    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Depth (m)')
    plt.colorbar(im, ax=ax, label='gDW/m3')
    ax.set_ylim(z[-1], z[0])

plt.tight_layout()
plt.savefig(os.path.join(out_dir, '11_fish_vertical.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: 11_fish_vertical.png')

ds3d.close()
ds2d.close()

print()
print('=' * 70)
print('All figures generated successfully!')
print(f'Output directory: {out_dir}')
print('=' * 70)
