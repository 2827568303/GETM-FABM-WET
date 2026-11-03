"""
Lake Luoma - Input data visualization and model run status report.
Generates figures following Lake Luoma case style (dpi=150, bbox_inches='tight').
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from netCDF4 import Dataset
import os
from datetime import datetime, timedelta

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

CASE_DIR = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma'
FIG_DIR = os.path.join(CASE_DIR, 'figures', 'run_check')
os.makedirs(FIG_DIR, exist_ok=True)

DPI = 150

# ========== Load data ==========
# Bathymetry
ds_bathy = Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'), 'r')
bathy = ds_bathy.variables['bathymetry'][:, :]
lonc = ds_bathy.variables['lonc'][:, :]
latc = ds_bathy.variables['latc'][:, :]
xc = ds_bathy.variables['x'][:]
yc = ds_bathy.variables['y'][:]
ds_bathy.close()

# Rivers
ds_riv = Dataset(os.path.join(CASE_DIR, 'rivers.nc'), 'r')
riv_time = ds_riv.variables['time'][:]
riv_names = ['YIHE', 'LUONAN', 'DAYUN', 'ZHANGSHAN', 'YANGHE']
riv_labels = ['Yihe', 'Luonan', 'Dayun', 'Zhangshan', 'Yanghe']
riv_data = {}
for rn in riv_names:
    riv_data[rn] = {
        'flow': ds_riv.variables[rn][:],
        'temp': ds_riv.variables[rn + '_temp'][:],
        'nh4':  ds_riv.variables[rn + '_nh4'][:],
        'no3':  ds_riv.variables[rn + '_no3'][:],
        'po4':  ds_riv.variables[rn + '_po4'][:],
    }
ds_riv.close()

# River positions from riverinfo.dat (format: j i NAME -1 -1)
riv_pos = {
    'YIHE':      [(50, 19), (50, 20), (50, 21)],
    'LUONAN':    [(2, 28)],
    'DAYUN':     [(31, 2), (32, 2), (32, 3)],
    'ZHANGSHAN': [(27, 41), (27, 42), (27, 43)],
    'YANGHE':    [(28, 35)],
}
# Note: riverinfo.dat format is "j i" (y, x), so position (j,i) -> bathy[j-1, i-1] (0-indexed)

# Meteo
ds_met = Dataset(os.path.join(CASE_DIR, 'meteo.nc'), 'r')
met_time = ds_met.variables['time'][:]
u10 = ds_met.variables['u10'][:]
v10 = ds_met.variables['v10'][:]
t2 = ds_met.variables['t2'][:]
rh = ds_met.variables['rh'][:]
tcc = ds_met.variables['tcc'][:]
precip = ds_met.variables['precip'][:]
evap = ds_met.variables['evap'][:]
ds_met.close()

# FABM init (macrophytes only)
ds_init = Dataset(os.path.join(CASE_DIR, 'fabm_init.nc'), 'r')
mac_sD = ds_init.variables['macrophytes_sD'][0, :, :]
mac_sN = ds_init.variables['macrophytes_sN'][0, :, :]
mac_sP = ds_init.variables['macrophytes_sP'][0, :, :]
ds_init.close()

# Time axes (seconds since 2020-01-01 -> convert to days)
riv_dates = [datetime(2020, 1, 1) + timedelta(days=int(t) / 86400.0) for t in riv_time]
met_dates = [datetime(2020, 1, 1) + timedelta(days=int(t) / 86400.0) for t in met_time]

# ========== FIGURE T01: Bathymetry + River Positions ==========
print('Generating T01_bathymetry_rivers.png ...')
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.pcolormesh(xc, yc, bathy, cmap='Blues_r', shading='auto')
cb = plt.colorbar(im, ax=ax, label='Depth (m)')
ax.set_xlabel('x (grid)')
ax.set_ylabel('y (grid)')
ax.set_title('Lake Luoma Bathymetry and River Positions', fontsize=13)

# Mark river positions
colors_riv = ['red', 'green', 'blue', 'purple', 'orange']
for idx, rn in enumerate(riv_names):
    for (j, i) in riv_pos[rn]:
        ax.plot(i, j, 'o', color=colors_riv[idx], markersize=8, markeredgecolor='k')
    # label at first position
    j0, i0 = riv_pos[rn][0]
    ax.annotate(riv_labels[idx], (i0, j0), textcoords='offset points',
                xytext=(8, 8), color=colors_riv[idx], fontsize=9, fontweight='bold')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T01_bathymetry_rivers.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T02: River Flow Time Series ==========
print('Generating T02_river_flow.png ...')
fig, axes = plt.subplots(5, 1, figsize=(12, 10), sharex=True)
for idx, rn in enumerate(riv_names):
    ax = axes[idx]
    flow = riv_data[rn]['flow']
    # positive = inflow, negative = outflow (GETM convention)
    colors_pos = np.where(flow >= 0, 'blue', 'red')
    ax.bar(riv_dates, flow, width=1.0, color=colors_pos, alpha=0.7)
    ax.axhline(0, color='k', linewidth=0.5)
    ax.set_ylabel(riv_labels[idx] + '\n(m3/s)')
    ax.set_title(f'{riv_labels[idx]} River Flow' if idx == 0 else '')
    ax.grid(True, alpha=0.3)
axes[-1].set_xlabel('Date')
fig.suptitle('River Inflow/Outflow Time Series (blue=inflow, red=outflow)', fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T02_river_flow.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T03: River Nutrient Concentrations ==========
print('Generating T03_river_nutrients.png ...')
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
nut_vars = ['nh4', 'no3', 'po4']
nut_labels = ['NH4-N (mg/L)', 'NO3-N (mg/L)', 'PO4-P (mg/L)']
for k, (nv, nl) in enumerate(zip(nut_vars, nut_labels)):
    ax = axes[k]
    for idx, rn in enumerate(riv_names):
        ax.plot(riv_dates, riv_data[rn][nv], label=riv_labels[idx], linewidth=0.8, alpha=0.8)
    ax.set_ylabel(nl)
    ax.grid(True, alpha=0.3)
    if k == 0:
        ax.legend(loc='upper right', fontsize=8)
axes[-1].set_xlabel('Date')
fig.suptitle('River Nutrient Concentrations (2020-2022)', fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T03_river_nutrients.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T04: River Water Temperature ==========
print('Generating T04_river_temperature.png ...')
fig, ax = plt.subplots(figsize=(12, 5))
for idx, rn in enumerate(riv_names):
    ax.plot(riv_dates, riv_data[rn]['temp'], label=riv_labels[idx], linewidth=0.8, alpha=0.8)
ax.set_ylabel('Temperature (C)')
ax.set_xlabel('Date')
ax.set_title('River Water Temperature (2020-2022)', fontsize=13)
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T04_river_temperature.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T05: Meteorological Data (spatial mean) ==========
print('Generating T05_meteo_overview.png ...')
fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
# wind speed
ws = np.sqrt(u10**2 + v10**2)
ws_mean = np.nanmean(ws, axis=(1, 2))
axes[0].plot(met_dates, ws_mean, color='steelblue', linewidth=0.8)
axes[0].set_ylabel('Wind Speed (m/s)')
axes[0].set_title('Wind Speed (spatial mean)')
axes[0].grid(True, alpha=0.3)

# air temp
t2_mean = np.nanmean(t2, axis=(1, 2))
axes[1].plot(met_dates, t2_mean, color='darkorange', linewidth=0.8)
axes[1].set_ylabel('Air Temp (C)')
axes[1].set_title('2m Air Temperature (spatial mean)')
axes[1].grid(True, alpha=0.3)

# precipitation (convert m/s to mm/day: *86400*1000)
precip_mean = np.nanmean(precip, axis=(1, 2)) * 86400.0 * 1000.0
axes[2].bar(met_dates, precip_mean, width=1.0, color='blue', alpha=0.6)
axes[2].set_ylabel('Precip (mm/day)')
axes[2].set_title('Precipitation (spatial mean)')
axes[2].grid(True, alpha=0.3)

# evaporation (convert m/s to mm/day; negative = water loss)
evap_mean = np.nanmean(evap, axis=(1, 2)) * 86400.0 * 1000.0
axes[3].bar(met_dates, evap_mean, width=1.0, color='red', alpha=0.6)
axes[3].set_ylabel('Evap (mm/day)')
axes[3].set_title('Evaporation (negative = water loss)')
axes[3].grid(True, alpha=0.3)
axes[3].set_xlabel('Date')

fig.suptitle('Meteorological Forcing (2020-2022)', fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T05_meteo_overview.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T06: Macrophyte Initial Conditions ==========
print('Generating T06_macrophyte_init.png ...')
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
vars_mac = [mac_sD, mac_sN, mac_sP]
labels_mac = ['macrophytes_sD (gDW/m2)', 'macrophytes_sN (gN/m2)', 'macrophytes_sP (gP/m2)']
cmaps = ['YlGn', 'Greens', 'Greens']
for k, (data, lab, cm) in enumerate(zip(vars_mac, labels_mac, cmaps)):
    ax = axes[k]
    im = ax.pcolormesh(xc, yc, data, cmap=cm, shading='auto')
    plt.colorbar(im, ax=ax, label=lab)
    ax.set_xlabel('x (grid)')
    ax.set_ylabel('y (grid)')
    ax.set_title(lab)
    ax.set_aspect('equal')
fig.suptitle('Macrophyte Initial Conditions (fabm_init.nc)', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T06_macrophyte_init.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T07: Water Balance Check (River inflow vs outflow) ==========
print('Generating T07_water_balance.png ...')
fig, ax = plt.subplots(figsize=(12, 5))
total_in = np.zeros(len(riv_dates))
total_out = np.zeros(len(riv_dates))
for rn in riv_names:
    flow = riv_data[rn]['flow']
    total_in += np.where(flow > 0, flow, 0)
    total_out += np.where(flow < 0, -flow, 0)
ax.plot(riv_dates, total_in, color='blue', label='Total Inflow', linewidth=0.8)
ax.plot(riv_dates, total_out, color='red', label='Total Outflow', linewidth=0.8)
ax.fill_between(riv_dates, total_in, total_out, where=total_in > total_out,
                color='blue', alpha=0.2, label='Net Inflow')
ax.fill_between(riv_dates, total_in, total_out, where=total_in < total_out,
                color='red', alpha=0.2, label='Net Outflow')
ax.set_ylabel('Flow (m3/s)')
ax.set_xlabel('Date')
ax.set_title('Water Balance: Total River Inflow vs Outflow', fontsize=13)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T07_water_balance.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T08: Nutrient Load from Rivers ==========
print('Generating T08_nutrient_loads.png ...')
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
for k, (nv, nl) in enumerate(zip(nut_vars, nut_labels)):
    ax = axes[k]
    for idx, rn in enumerate(riv_names):
        flow = riv_data[rn]['flow']
        conc = riv_data[rn][nv]
        # load = flow * conc (mg/s); convert to kg/day: *86400/1e6
        load = np.abs(flow) * conc * 86400.0 / 1e6
        ax.plot(riv_dates, load, label=riv_labels[idx], linewidth=0.8, alpha=0.8)
    ax.set_ylabel(f'{nl.split(" ")[0]} load\n(kg/d)')
    ax.grid(True, alpha=0.3)
    if k == 0:
        ax.legend(loc='upper right', fontsize=8)
axes[-1].set_xlabel('Date')
fig.suptitle('River Nutrient Loads (2020-2022)', fontsize=13, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T08_nutrient_loads.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T09: Model Run Progress ==========
print('Generating T09_run_progress.png ...')
# Parse run.log to extract n= progress
log_file = os.path.join(CASE_DIR, 'run.log')
n_values = []
t_values = []
if os.path.exists(log_file):
    with open(log_file, 'r', errors='ignore') as f:
        for line in f:
            if 'n=' in line:
                # parse lines like "10:42:45.222 n=     1114800"
                parts = line.split('n=')
                if len(parts) >= 2:
                    try:
                        n = int(parts[1].strip())
                        # parse time
                        t_str = parts[0].strip().split()[0]
                        n_values.append(n)
                        t_values.append(t_str)
                    except:
                        pass

fig, axes = plt.subplots(2, 1, figsize=(12, 8))
if n_values:
    # Plot 1: progress over log entries
    ax = axes[0]
    ax.plot(range(len(n_values)), n_values, color='steelblue', linewidth=0.8)
    ax.axhline(6301440, color='r', linestyle='--', label='Target (6,301,440)')
    ax.set_xlabel('Log entry index')
    ax.set_ylabel('Time step n')
    ax.set_title(f'Model Run Progress (current: n={n_values[-1]}/{6301440}, {n_values[-1]/6301440*100:.1f}%)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: percentage
    ax = axes[1]
    pct = [n / 6301440 * 100 for n in n_values]
    ax.plot(range(len(pct)), pct, color='green', linewidth=0.8)
    ax.axhline(100, color='r', linestyle='--', label='100%')
    ax.set_xlabel('Log entry index')
    ax.set_ylabel('Progress (%)')
    ax.set_title(f'Run Progress: {pct[-1]:.1f}% (last: {t_values[-1]})')
    ax.legend()
    ax.grid(True, alpha=0.3)
else:
    axes[0].text(0.5, 0.5, 'No progress data found in run.log', ha='center', va='center')
    axes[1].text(0.5, 0.5, 'No progress data found in run.log', ha='center', va='center')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T09_run_progress.png'), dpi=DPI, bbox_inches='tight')
plt.close()

# ========== FIGURE T10: Summary Statistics ==========
print('Generating T10_summary.png ...')
fig, axes = plt.subplots(2, 3, figsize=(15, 8))

# Bathymetry stats
ax = axes[0, 0]
ax.hist(bathy.flatten(), bins=30, color='steelblue', edgecolor='k', alpha=0.7)
ax.set_xlabel('Depth (m)')
ax.set_ylabel('Count')
ax.set_title(f'Bathymetry (min={bathy.min():.1f}, max={bathy.max():.1f}, mean={bathy.mean():.1f}m)')

# River flow stats
ax = axes[0, 1]
for idx, rn in enumerate(riv_names):
    flow = riv_data[rn]['flow']
    ax.boxplot([flow], positions=[idx + 1], widths=0.5)
ax.set_xticks(range(1, 6))
ax.set_xticklabels(riv_labels, rotation=30)
ax.set_ylabel('Flow (m3/s)')
ax.set_title('River Flow Distribution')
ax.grid(True, alpha=0.3)

# Temperature stats
ax = axes[0, 2]
for idx, rn in enumerate(riv_names):
    temp = riv_data[rn]['temp']
    ax.boxplot([temp], positions=[idx + 1], widths=0.5)
ax.set_xticks(range(1, 6))
ax.set_xticklabels(riv_labels, rotation=30)
ax.set_ylabel('Temp (C)')
ax.set_title('River Temperature Distribution')
ax.grid(True, alpha=0.3)

# NH4 stats
ax = axes[1, 0]
for idx, rn in enumerate(riv_names):
    data = riv_data[rn]['nh4']
    ax.boxplot([data], positions=[idx + 1], widths=0.5)
ax.set_xticks(range(1, 6))
ax.set_xticklabels(riv_labels, rotation=30)
ax.set_ylabel('NH4-N (mg/L)')
ax.set_title('River NH4-N Distribution')
ax.grid(True, alpha=0.3)

# NO3 stats
ax = axes[1, 1]
for idx, rn in enumerate(riv_names):
    data = riv_data[rn]['no3']
    ax.boxplot([data], positions=[idx + 1], widths=0.5)
ax.set_xticks(range(1, 6))
ax.set_xticklabels(riv_labels, rotation=30)
ax.set_ylabel('NO3-N (mg/L)')
ax.set_title('River NO3-N Distribution')
ax.grid(True, alpha=0.3)

# PO4 stats
ax = axes[1, 2]
for idx, rn in enumerate(riv_names):
    data = riv_data[rn]['po4']
    ax.boxplot([data], positions=[idx + 1], widths=0.5)
ax.set_xticks(range(1, 6))
ax.set_xticklabels(riv_labels, rotation=30)
ax.set_ylabel('PO4-P (mg/L)')
ax.set_title('River PO4-P Distribution')
ax.grid(True, alpha=0.3)

fig.suptitle('Lake Luoma Input Data Summary Statistics', fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'T10_summary.png'), dpi=DPI, bbox_inches='tight')
plt.close()

print('\nAll figures generated successfully!')
print(f'Saved to: {FIG_DIR}')

# Print summary
print('\n=== SUMMARY ===')
print(f'Bathymetry: {bathy.shape}, depth range {bathy.min():.2f}-{bathy.max():.2f} m, mean {bathy.mean():.2f} m')
print(f'Rivers: {len(riv_names)} rivers, {len(riv_time)} days')
print(f'Meteo: {len(met_time)} days, 9 variables')
print(f'Macrophyte init sD: min={mac_sD.min():.4f}, max={mac_sD.max():.4f}, mean={mac_sD.mean():.4f} gDW/m2')
if n_values:
    print(f'Run progress: n={n_values[-1]}/{6301440} ({n_values[-1]/6301440*100:.1f}%)')
