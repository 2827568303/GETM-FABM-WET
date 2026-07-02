"""
Full Food Web 3D Visualization - Complete WET model with macrophytes, zoobenthos, 2 zooplankton, 3 phytoplankton
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

print('Loading 3D data...')
ds = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
lon = to_np(ds.variables['lonc'][:])
lat = to_np(ds.variables['latc'][:])
sigma = to_np(ds.variables['sigma'][:])
time = to_np(ds.variables['time'][:]) / 86400.0

n_sigma = len(sigma)
n_time = len(time)

# Bathymetry for mask
bathy_ds = nc.Dataset(os.path.join(case_dir, 'bathymetry.nc'))
bathymetry = to_np(bathy_ds.variables['bathymetry'][:])
bathy_ds.close()
mask = bathymetry > 0
mean_depth = np.mean(bathymetry[mask])

print(f'Time steps: {n_time}, Sigma layers: {n_sigma}')

# List all variables
all_vars = list(ds.variables.keys())

# Check what food web variables we have
foodweb_vars = {}
for v in all_vars:
    vl = v.lower()
    if any(x in vl for x in ['macrophyte', 'cladoceran', 'copepod', 'zoobenthos', 'cyanobacteria', 'diatom', 'greens', 'chla', 'zooplankton', 'fish']):
        foodweb_vars[v] = ds.variables[v].units if hasattr(ds.variables[v], 'units') else '-'

print('\nFood web variables:')
for v, u in sorted(foodweb_vars.items()):
    print(f'  {v}: {u}')

# Load key variables
print('\nLoading variables...')

# Phytoplankton
phyto = {}
for group in ['cyanobacteria', 'diatoms', 'greens']:
    phyto[group] = {
        'DW': to_np(ds.variables[f'{group}_sDW'][:]),
        'Chla': to_np(ds.variables[f'{group}_oChla'][:]),
        'NLim': to_np(ds.variables[f'{group}_aNLim'][:]),
        'PLim': to_np(ds.variables[f'{group}_aPLim'][:]),
        'LLim': to_np(ds.variables[f'{group}_aLLim'][:]),
    }

# Zooplankton
zoo = {}
for group in ['cladocerans', 'copepods']:
    zoo[group] = {
        'DW': to_np(ds.variables[f'{group}_sD'][:]),
        'N': to_np(ds.variables[f'{group}_sN'][:]),
        'P': to_np(ds.variables[f'{group}_sP'][:]),
    }

# Macrophytes (2D - sediment)
macro = {}
macro_vars = [v for v in all_vars if v.startswith('macrophytes_')]
print(f'Macrophyte variables: {macro_vars[:15]}')
for v in macro_vars[:10]:
    data = ds.variables[v][:]
    if len(data.shape) == 2:  # 2D (time, y, x)
        macro[v.replace('macrophytes_', '')] = to_np(data)

# Zoobenthos (2D - sediment)
benthos = {}
benthos_vars = [v for v in all_vars if v.startswith('zoobenthos_')]
print(f'Zoobenthos variables: {benthos_vars[:10]}')
for v in benthos_vars[:10]:
    data = ds.variables[v][:]
    if len(data.shape) == 3:  # 2D (time, y, x) or 3D (time, z, y, x)
        benthos[v.replace('zoobenthos_', '')] = to_np(data)

# Nutrients
nutrients = {
    'NH4': to_np(ds.variables['abiotic_water_sNH4W'][:]),
    'NO3': to_np(ds.variables['abiotic_water_sNO3W'][:]),
    'PO4': to_np(ds.variables['abiotic_water_sPO4W'][:]),
    'O2': to_np(ds.variables['abiotic_water_sO2W'][:]),
}

# Total chla
total_chla = to_np(ds.variables['wet_chla'][:])

ds.close()

print('\nData loaded. Creating figures...')

# ========== Figure 1: Food Web Overview - Spatial Distribution ==========
print('Figure 1: Food web spatial distribution...')
fig, axes = plt.subplots(4, 4, figsize=(20, 16))

# Row 1: Phytoplankton groups (surface, day 30)
day_idx = -1  # last day
row = 0
for col, (group, pdata) in enumerate(phyto.items()):
    ax = axes[row, col]
    d = pdata['Chla'][day_idx, -1, :, :]
    d = np.where(mask, d, np.nan)
    vmax = np.nanmax(d) if np.nanmax(d) > 0 else 1.0
    cmap = 'Blues' if 'cyano' in group else ('YlOrBr' if 'diatom' in group else 'Greens')
    im = ax.pcolormesh(lon, lat, d, cmap=cmap, vmin=0, vmax=vmax, shading='auto')
    plt.colorbar(im, ax=ax, label='Chl-a (mg/m³)')
    ax.set_title(f'Day 30 - {group}')
    ax.set_xticklabels([])
    ax.set_yticklabels([])

ax = axes[row, 3]
d = total_chla[day_idx, -1, :, :]
d = np.where(mask, d, np.nan)
im = ax.pcolormesh(lon, lat, d, cmap='YlGn', vmin=0, shading='auto')
plt.colorbar(im, ax=ax, label='Total Chl-a (mg/m³)')
ax.set_title('Day 30 - Total Chla')
ax.set_xticklabels([])
ax.set_yticklabels([])

# Row 2: Zooplankton groups (surface, day 30)
row = 1
for col, (group, zdata) in enumerate(zoo.items()):
    ax = axes[row, col]
    d = zdata['DW'][day_idx, -1, :, :]
    d = np.where(mask, d, np.nan)
    vmax = np.nanmax(d) if np.nanmax(d) > 0 else 1.0
    im = ax.pcolormesh(lon, lat, d, cmap='Oranges', vmin=0, vmax=vmax, shading='auto')
    plt.colorbar(im, ax=ax, label='DW (g/m³)')
    ax.set_title(f'Day 30 - {group}')
    ax.set_xticklabels([])
    ax.set_yticklabels([])

# Total zooplankton
ax = axes[row, 2]
zoo_total = zoo['cladocerans']['DW'][day_idx, -1, :, :] + zoo['copepods']['DW'][day_idx, -1, :, :]
zoo_total = np.where(mask, zoo_total, np.nan)
im = ax.pcolormesh(lon, lat, zoo_total, cmap='OrRd', vmin=0, shading='auto')
plt.colorbar(im, ax=ax, label='DW (g/m³)')
ax.set_title('Day 30 - Total Zooplankton')
ax.set_xticklabels([])
ax.set_yticklabels([])

# Zooplankton:phytoplankton ratio
ax = axes[row, 3]
phyto_total = np.zeros_like(phyto['cyanobacteria']['DW'][day_idx, -1, :, :])
for group, pdata in phyto.items():
    phyto_total += pdata['DW'][day_idx, -1, :, :]
ratio = np.where(phyto_total > 0.001, zoo_total / phyto_total, 0)
ratio = np.where(mask, ratio, np.nan)
im = ax.pcolormesh(lon, lat, ratio, cmap='RdYlBu', vmin=0, vmax=0.5, shading='auto')
plt.colorbar(im, ax=ax, label='Zoo/Phyto Ratio')
ax.set_title('Day 30 - Zoo/Phyto Ratio')
ax.set_xticklabels([])
ax.set_yticklabels([])

# Row 3: Macrophytes (2D) and Zoobenthos
row = 2
# Macrophyte biomass
if 'sD' in macro:
    ax = axes[row, 0]
    d = macro['sD'][day_idx, :, :]
    d = np.where(mask, d, np.nan)
    im = ax.pcolormesh(lon, lat, d, cmap='YlGn', vmin=0, shading='auto')
    plt.colorbar(im, ax=ax, label='DW (g/m²)')
    ax.set_title('Day 30 - Macrophyte Biomass')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Cover
    ax = axes[row, 1]
    if 'aCovVeg' in macro:
        d = macro['aCovVeg'][day_idx, :, :]
        d = np.where(mask, d, np.nan)
        im = ax.pcolormesh(lon, lat, d, cmap='Greens', vmin=0, vmax=1, shading='auto')
        plt.colorbar(im, ax=ax, label='Cover (-)')
        ax.set_title('Day 30 - Macrophyte Cover')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Submerged vegetation depth
    ax = axes[row, 2]
    if 'aDSubVeg' in macro:
        d = macro['aDSubVeg'][day_idx, :, :]
        d = np.where(mask, d, np.nan)
        im = ax.pcolormesh(lon, lat, d, cmap='BuGn', vmin=0, shading='auto')
        plt.colorbar(im, ax=ax, label='Depth (m)')
        ax.set_title('Day 30 - Subveg Depth')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Nutrient limitation
    ax = axes[row, 3]
    if 'aNutLimVeg' in macro:
        d = macro['aNutLimVeg'][day_idx, :, :]
        d = np.where(mask, d, np.nan)
        im = ax.pcolormesh(lon, lat, d, cmap='RdYlGn_r', vmin=0, vmax=1, shading='auto')
        plt.colorbar(im, ax=ax, label='Nut Lim (-)')
        ax.set_title('Day 30 - Macro Nutrient Lim')
    ax.set_xticklabels([])
    ax.set_yticklabels([])

# Row 4: Time series
row = 3
# Total chla time series
ax = axes[row, 0]
ts_chla = np.array([np.nanmean(total_chla[t, -1, :, :][mask]) for t in range(n_time)])
ax.plot(time, ts_chla, 'g-', linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Chl-a (mg/m³)')
ax.set_title('Total Chla - Surface')
ax.grid(True, alpha=0.3)

# Phytoplankton groups time series
ax = axes[row, 1]
for group, pdata in phyto.items():
    ts = np.array([np.nanmean(pdata['DW'][t, -1, :, :][mask]) for t in range(n_time)])
    ax.plot(time, ts, linewidth=2, label=group)
ax.set_xlabel('Day')
ax.set_ylabel('DW (g/m³)')
ax.set_title('Phytoplankton - Surface')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Zooplankton time series
ax = axes[row, 2]
for group, zdata in zoo.items():
    ts = np.array([np.nanmean(zdata['DW'][t, -1, :, :][mask]) for t in range(n_time)])
    ax.plot(time, ts, linewidth=2, label=group)
ax.set_xlabel('Day')
ax.set_ylabel('DW (g/m³)')
ax.set_title('Zooplankton - Surface')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Nutrients time series
ax = axes[row, 3]
for name, ndata in nutrients.items():
    ts = np.array([np.nanmean(ndata[t, -1, :, :][mask]) for t in range(n_time)])
    ax.plot(time, ts, linewidth=2, label=name)
ax.set_xlabel('Day')
ax.set_ylabel('Conc (g/m³)')
ax.set_title('Nutrients - Surface')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

plt.suptitle('WET Full Food Web - 3D Spatial Distribution & Time Series (30 days)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '12_full_foodweb_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 2: Vertical Profiles ==========
print('Figure 2: Vertical profiles...')
fig, axes = plt.subplots(3, 4, figsize=(20, 12))

profile_days = [0, 9, 19, 29]
profile_labels = ['Day 1', 'Day 10', 'Day 20', 'Day 30']
colors = plt.cm.viridis(np.linspace(0, 1, len(profile_days)))

def get_lake_avg(data, t_idx, mask):
    return np.array([np.nanmean(data[t_idx, k, :, :][mask]) for k in range(n_sigma)])

# Row 1: Phytoplankton
for col, (group, pdata) in enumerate(phyto.items()):
    ax = axes[0, col]
    z = sigma * mean_depth
    for i, (t_idx, lbl) in enumerate(zip(profile_days, profile_labels)):
        prof = get_lake_avg(pdata['Chla'], t_idx, mask)
        ax.plot(prof, z, '-o', color=colors[i], linewidth=2, markersize=4, label=lbl)
    ax.set_xlabel('Chl-a (mg/m³)')
    ax.set_ylabel('Depth (m)')
    ax.set_title(f'{group} Chl-a')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

# Total chla
ax = axes[0, 3]
z = sigma * mean_depth
for i, (t_idx, lbl) in enumerate(zip(profile_days, profile_labels)):
    prof = get_lake_avg(total_chla, t_idx, mask)
    ax.plot(prof, z, '-o', color=colors[i], linewidth=2, markersize=4, label=lbl)
ax.set_xlabel('Total Chl-a (mg/m³)')
ax.set_ylabel('Depth (m)')
ax.set_title('Total Chl-a')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Row 2: Zooplankton
for col, (group, zdata) in enumerate(zoo.items()):
    ax = axes[1, col]
    z = sigma * mean_depth
    for i, (t_idx, lbl) in enumerate(zip(profile_days, profile_labels)):
        prof = get_lake_avg(zdata['DW'], t_idx, mask)
        ax.plot(prof, z, '-o', color=colors[i], linewidth=2, markersize=4, label=lbl)
    ax.set_xlabel('DW (g/m³)')
    ax.set_ylabel('Depth (m)')
    ax.set_title(f'{group} Biomass')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

# Zoo/Phyto ratio
ax = axes[1, 2]
z = sigma * mean_depth
for i, (t_idx, lbl) in enumerate(zip(profile_days, profile_labels)):
    phyto_dw = np.zeros(n_sigma)
    for group, pdata in phyto.items():
        phyto_dw += get_lake_avg(pdata['DW'], t_idx, mask)
    zoo_dw = np.zeros(n_sigma)
    for group, zdata in zoo.items():
        zoo_dw += get_lake_avg(zdata['DW'], t_idx, mask)
    ratio = np.where(phyto_dw > 0.001, zoo_dw / phyto_dw, 0)
    ax.plot(ratio, z, '-o', color=colors[i], linewidth=2, markersize=4, label=lbl)
ax.set_xlabel('Zoo/Phyto Ratio')
ax.set_ylabel('Depth (m)')
ax.set_title('Zoo/Phyto Ratio')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Empty
axes[1, 3].axis('off')

# Row 3: Nutrients
for col, (name, ndata) in enumerate(nutrients.items()):
    ax = axes[2, col]
    z = sigma * mean_depth
    for i, (t_idx, lbl) in enumerate(zip(profile_days, profile_labels)):
        prof = get_lake_avg(ndata, t_idx, mask)
        ax.plot(prof, z, '-o', color=colors[i], linewidth=2, markersize=4, label=lbl)
    ax.set_xlabel(f'{name} (g/m³)')
    ax.set_ylabel('Depth (m)')
    ax.set_title(name)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

plt.suptitle('Food Web: Vertical Profiles (Lake Average)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '13_full_foodweb_vertical.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 3: Depth-Time Heatmaps ==========
print('Figure 3: Depth-time heatmaps...')
fig, axes = plt.subplots(3, 4, figsize=(20, 12))

def depth_time(data, mask):
    dt = np.zeros((n_sigma, n_time))
    for k in range(n_sigma):
        for t in range(n_time):
            vals = data[t, k, :, :]
            valid = vals[mask]
            dt[k, t] = np.nanmean(valid) if len(valid) > 0 else np.nan
    return dt

vars_dt = [
    ('Total Chla', total_chla, 'YlGn'),
    ('Cyanobacteria', phyto['cyanobacteria']['Chla'], 'Blues'),
    ('Diatoms', phyto['diatoms']['Chla'], 'YlOrBr'),
    ('Greens', phyto['greens']['Chla'], 'Greens'),
    ('Cladocerans', zoo['cladocerans']['DW'], 'Oranges'),
    ('Copepods', zoo['copepods']['DW'], 'Reds'),
    ('NH4', nutrients['NH4'], 'Reds'),
    ('NO3', nutrients['NO3'], 'Purples'),
    ('PO4', nutrients['PO4'], 'Oranges'),
    ('O2', nutrients['O2'], 'Blues'),
    ('Cyano N-Lim', phyto['cyanobacteria']['NLim'], 'RdYlGn'),
    ('Cyano L-Lim', phyto['cyanobacteria']['LLim'], 'RdYlGn'),
]

for idx, (title, data, cmap) in enumerate(vars_dt):
    row = idx // 4
    col = idx % 4
    ax = axes[row, col]
    dt = depth_time(data, mask)
    im = ax.pcolormesh(time, np.arange(n_sigma), dt, cmap=cmap, shading='auto')
    plt.colorbar(im, ax=ax)
    ax.set_xlabel('Day')
    ax.set_ylabel('Sigma layer')
    ax.set_title(title)

plt.suptitle('Food Web: Depth-Time Evolution (30 days)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '14_full_foodweb_depthtime.png'), dpi=150, bbox_inches='tight')
plt.close()

# ========== Figure 4: Macrophytes & Benthos (2D) ==========
print('Figure 4: Macrophytes and benthos...')
fig, axes = plt.subplots(2, 4, figsize=(20, 10))

# Macrophyte time series (if 2D)
if 'sD' in macro and len(macro['sD'].shape) == 3:
    # Time series of lake average
    ax = axes[0, 0]
    ts = np.array([np.nanmean(macro['sD'][t, :, :][mask]) for t in range(n_time)])
    ax.plot(time, ts, 'g-', linewidth=2)
    ax.set_xlabel('Day')
    ax.set_ylabel('Biomass (gDW/m²)')
    ax.set_title('Macrophyte Biomass')
    ax.grid(True, alpha=0.3)
    
    # Cover time series
    ax = axes[0, 1]
    if 'aCovVeg' in macro:
        ts = np.array([np.nanmean(macro['aCovVeg'][t, :, :][mask]) for t in range(n_time)])
        ax.plot(time, ts, 'g-', linewidth=2)
        ax.set_xlabel('Day')
        ax.set_ylabel('Cover (-)')
        ax.set_title('Macrophyte Cover')
        ax.grid(True, alpha=0.3)
    
    # Spatial distribution day 1
    ax = axes[0, 2]
    d = macro['sD'][0, :, :]
    d = np.where(mask, d, np.nan)
    im = ax.pcolormesh(lon, lat, d, cmap='YlGn', shading='auto')
    plt.colorbar(im, ax=ax, label='DW (g/m²)')
    ax.set_title('Day 1 - Macrophyte')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Spatial distribution day 30
    ax = axes[0, 3]
    d = macro['sD'][-1, :, :]
    d = np.where(mask, d, np.nan)
    im = ax.pcolormesh(lon, lat, d, cmap='YlGn', shading='auto')
    plt.colorbar(im, ax=ax, label='DW (g/m²)')
    ax.set_title('Day 30 - Macrophyte')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Row 2: Macrophyte limitation factors
    ax = axes[1, 0]
    if 'aNutLimVeg' in macro:
        ts = np.array([np.nanmean(macro['aNutLimVeg'][t, :, :][mask]) for t in range(n_time)])
        ax.plot(time, ts, 'r-', linewidth=2, label='Nut Lim')
    if 'aLLimVeg' in macro:
        ts = np.array([np.nanmean(macro['aLLimVeg'][t, :, :][mask]) for t in range(n_time)])
        ax.plot(time, ts, 'y-', linewidth=2, label='Light Lim')
    ax.set_xlabel('Day')
    ax.set_ylabel('Limitation (-)')
    ax.set_title('Macrophyte Limitation')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Depth distribution of macrophytes
    ax = axes[1, 1]
    if 'aDSubVeg' in macro:
        d = macro['aDSubVeg'][-1, :, :]
        d = np.where(mask, d, np.nan)
        im = ax.pcolormesh(lon, lat, d, cmap='BuGn', shading='auto')
        plt.colorbar(im, ax=ax, label='Depth (m)')
        ax.set_title('Day 30 - Subveg Depth')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Cover spatial
    ax = axes[1, 2]
    if 'aCovVeg' in macro:
        d = macro['aCovVeg'][-1, :, :]
        d = np.where(mask, d, np.nan)
        im = ax.pcolormesh(lon, lat, d, cmap='Greens', vmin=0, vmax=1, shading='auto')
        plt.colorbar(im, ax=ax, label='Cover (-)')
        ax.set_title('Day 30 - Cover')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Biomass vs depth scatter
    ax = axes[1, 3]
    if 'sD' in macro:
        depths = bathymetry[mask].flatten()
        biomass = macro['sD'][-1, :, :][mask].flatten()
        valid = ~np.isnan(biomass)
        ax.scatter(biomass[valid], depths[valid], alpha=0.5, s=10, c='g')
        ax.set_xlabel('Macrophyte DW (g/m²)')
        ax.set_ylabel('Depth (m)')
        ax.set_title('Biomass vs Depth')
        ax.grid(True, alpha=0.3)

plt.suptitle('Macrophytes & Benthos - 2D Distribution (30 days)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, '15_macrophytes_benthos.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f'\nAll figures saved to {out_dir}')
print('Figures:')
for f in sorted(os.listdir(out_dir)):
    if f.startswith('1'):
        print(f'  {f}')
