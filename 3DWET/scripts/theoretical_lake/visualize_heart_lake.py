"""Visualize GETM-FABM-WET output for the heart-shaped Theoretical Lake.

Adapted for the 24 x 20 cell, 500 m grid, heart-shaped (point-south) lake.
Reads THEORETICAL_LAKE.2d.nc and THEORETICAL_LAKE.3d.nc (FABM vars are in the 3d file).
Outputs PNG files to ../../case/Theoretical lake/plots/

Run:  python3 visualize_heart_lake.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import netCDF4 as nc

plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'case', 'Theoretical lake'))
OUT_DIR = os.path.join(CASE_DIR, 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# Lake geometry (must match gen_theoretical_lake.py / lake_summary.txt)
# ------------------------------------------------------------------
NX, NY = 24, 20
DX = DY = 500.0
# River cells (0-indexed i, j); j=0 north, j=NY-1 south (point)
RIVERS = [
    ('INFL_NW',  2,  5, 'inflow',  'red'),       # 2 cells, west side of NW lobe
    ('INFL_NW2', 2,  6, 'inflow',  'red'),
    ('INFL_NE', 20,  2, 'inflow',  'darkred'),   # NE side
    ('INFL_W',   2, 10, 'inflow',  'salmon'),    # west middle
    ('OUTFL_S', 12, 18, 'outflow', 'blue'),      # south point
    ('OUTFL_E', 19, 10, 'outflow', 'navy'),      # east middle (2 cells)
    ('OUTFL_E2',19, 11, 'outflow', 'navy'),
]

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def to_np(data):
    return np.ma.filled(data, np.nan) if hasattr(data, 'mask') else np.asarray(data)

def filter_valid(time_arr):
    """Keep leading contiguous run of monotonically increasing positive values."""
    valid = np.asarray(time_arr) > 0
    n = len(time_arr)
    last = -np.inf
    for i in range(n):
        if valid[i] and time_arr[i] > last:
            last = time_arr[i]
        else:
            valid[i:] = False
            break
    return valid

def spatial_mean(var, mask, axis):
    """Mean over wet cells (mask is 2D wet mask)."""
    if var.ndim == 3:      # (t, y, x)
        m = mask[np.newaxis, :, :]
    elif var.ndim == 4:    # (t, z, y, x)
        m = mask[np.newaxis, np.newaxis, :, :]
    else:
        return np.nanmean(var)
    return np.nanmean(np.where(m, var, np.nan), axis=axis)

def get_sigma_index(sigma, target):
    return int(np.argmin(np.abs(np.asarray(sigma) - target)))

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
print('=' * 70)
print('Loading Theoretical Lake (heart) model output...')

ds2d = nc.Dataset(os.path.join(CASE_DIR, 'THEORETICAL_LAKE.2d.nc'))
ds3d = nc.Dataset(os.path.join(CASE_DIR, 'THEORETICAL_LAKE.3d.nc'))

# bathymetry (read from 2D output since it contains the same grid info)
bathymetry = to_np(ds2d.variables['bathymetry'][:])
# bathymetry in (y, x) = (NY, NX); wet mask
wet_mask = bathymetry > 0

# coordinates
lonc = to_np(ds2d.variables['lonc'][:])
latc = to_np(ds2d.variables['latc'][:])

# time
t2_raw = to_np(ds2d.variables['time'][:])
t3_raw = to_np(ds3d.variables['time'][:])
v2 = filter_valid(t2_raw)
v3 = filter_valid(t3_raw)
t2 = t2_raw[v2] / 86400.0
t3 = t3_raw[v3] / 86400.0
sigma = to_np(ds3d.variables['sigma'][:])
i_surf = get_sigma_index(sigma, 0.0)
i_bot  = get_sigma_index(sigma, -1.0)

mean_depth = float(np.nanmean(bathymetry))
max_depth  = float(np.nanmax(bathymetry))
print(f'  2D records: {len(t2)}  (day {t2[0]:.1f}..{t2[-1]:.1f})')
print(f'  3D records: {len(t3)}  (day {t3[0]:.1f}..{t3[-1]:.1f})')
print(f'  sigma: {sigma}  (surf idx={i_surf}, bot idx={i_bot})')
print(f'  mean depth={mean_depth:.2f} m, max={max_depth:.2f} m')

# lake-specific colormap
lake_cmap = LinearSegmentedColormap.from_list('lake',
    ['#f0f8ff','#a8d8f0','#5aa8d0','#2070a8','#104878','#04203f'], N=256)

# ==================================================================
# V01 - Bathymetry + rivers overview
# ==================================================================
print('V01: bathymetry & rivers')
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

ax = axes[0]
im = ax.pcolormesh(lonc, latc, bathymetry, cmap=lake_cmap, shading='nearest')
ax.set_title(f'Theoretical Lake Bathymetry (heart-shaped, 70 km², mean {mean_depth:.1f} m, max {max_depth:.1f} m)')
ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)'); ax.set_aspect('equal')
plt.colorbar(im, ax=ax, label='Depth (m)')

ax = axes[1]
im = ax.pcolormesh(lonc, latc, bathymetry, cmap=lake_cmap, shading='nearest', alpha=0.7)
ax.set_title('River Locations (3 inflows / 2 outflows)')
ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)'); ax.set_aspect('equal')
plt.colorbar(im, ax=ax, label='Depth (m)')
seen = set()
for name, ix, iy, rtype, color in RIVERS:
    if name in seen:
        continue
    seen.add(name)
    rlon, rlat = lonc[iy, ix], latc[iy, ix]
    if rtype == 'inflow':
        ax.annotate('', xy=(rlon, rlat), xytext=(rlon+0.004, rlat+0.004),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
    else:
        ax.annotate('', xy=(rlon+0.004, rlat+0.004), xytext=(rlon, rlat),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
    ax.plot(rlon, rlat, 'o', color=color, markersize=10,
            markeredgecolor='black', markeredgewidth=1.2)
    ax.text(rlon+0.003, rlat+0.002, name, fontsize=8, color=color, fontweight='bold')
legend = [mpatches.Patch(color='red', label='Inflow (3 rivers)'),
          mpatches.Patch(color='blue', label='Outflow (2 rivers)')]
ax.legend(handles=legend, loc='lower left', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V01_bathymetry_rivers.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V02 - Water level time series
# ==================================================================
print('V02: water level')
elev = to_np(ds2d.variables['elev'][:])[v2, :, :]
elev_mean = spatial_mean(elev, wet_mask, axis=(1, 2))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
ax.plot(t2, elev_mean, 'b-', lw=1.3)
ax.axhline(0.0, color='k', ls='--', alpha=0.5)
net = elev_mean[-1] - elev_mean[0]
ax.set_title(f'Spatial Mean Water Level (net change {net:+.4f} m)')
ax.set_xlabel('Time (days)'); ax.set_ylabel('Water Level (m)'); ax.grid(alpha=0.3)

ax = axes[1]
for name, ix, iy, rtype, color in [('INFL_NW',2,5,'in','red'),
                                     ('INFL_NE',20,2,'in','darkred'),
                                     ('OUTFL_S',12,18,'out','blue'),
                                     ('OUTFL_E',19,10,'out','navy')]:
    ax.plot(t2, elev[:, iy, ix], lw=1.2, label=name, color=color)
ax.axhline(0.0, color='k', ls='--', alpha=0.5)
ax.set_title('Water Level at River Cells'); ax.set_xlabel('Time (days)'); ax.set_ylabel('Water Level (m)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V02_water_level.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V03 - Temperature: surface vs bottom + vertical heatmap
# ==================================================================
print('V03: temperature')
temp = to_np(ds3d.variables['temp'][:])[v3, :, :, :]
t_surf = temp[:, i_surf, :, :]
t_bot  = temp[:, i_bot,  :, :]
ts_mean = spatial_mean(t_surf, wet_mask, axis=(1, 2))
tb_mean = spatial_mean(t_bot,  wet_mask, axis=(1, 2))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
ax = axes[0]
ax.plot(t3, ts_mean, 'r-', lw=1.3, label='Surface')
ax.plot(t3, tb_mean, 'b-', lw=1.3, label='Bottom')
ax.set_title('Spatial Mean Water Temperature'); ax.set_xlabel('Time (days)'); ax.set_ylabel('Temperature (°C)')
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(t3, ts_mean - tb_mean, 'purple', lw=1.3)
ax.axhline(0.0, color='k', ls='--', alpha=0.5)
ax.set_title('Surface-Bottom Temp Difference (Stratification)'); ax.set_xlabel('Time (days)'); ax.set_ylabel('Temp Diff (°C)')
ax.grid(alpha=0.3)

# vertical heatmap (spatial mean over (y,x) -> (t, sigma) -> transpose)
ax = axes[2]
profile = spatial_mean(temp, wet_mask, axis=(2, 3)).T  # (sigma, time)
depth_axis = -np.sort(sigma) * max_depth
im = ax.pcolormesh(t3, depth_axis, profile, cmap='RdYlBu_r', shading='auto')
ax.set_title('Temperature Depth-Time Heatmap'); ax.set_xlabel('Time (days)'); ax.set_ylabel('Depth (m)')
ax.set_ylim(max_depth, 0)
plt.colorbar(im, ax=ax, label='Temperature (°C)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V03_temperature.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V04 - Nutrients (surface, spatial mean)
# ==================================================================
print('V04: nutrients')
nut_specs = [
    ('abiotic_water_sNH4W', 'NH4', 'g/m³', 'Blues'),
    ('abiotic_water_sNO3W', 'NO3', 'g/m³', 'Purples'),
    ('abiotic_water_sPO4W', 'PO4', 'g/m³', 'Reds'),
    ('abiotic_water_sO2W',  'O2',  'g/m³', 'GnBu'),
]
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
for k, (vname, label, units, cmap) in enumerate(nut_specs):
    ax = axes[k//2, k%2]
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        s = var[:, i_surf, :, :]
        sm = spatial_mean(s, wet_mask, axis=(1, 2))
        ax.plot(t3, sm, color='steelblue', lw=1.3)
        ax.set_title(f'{label} Surface (mean={np.nanmean(sm):.4f} {units})')
    else:
        ax.set_title(f'{label} (variable missing)')
    ax.set_xlabel('Time (days)'); ax.set_ylabel(units); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V04_nutrients.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V05 - Phytoplankton (depth-averaged)
# ==================================================================
print('V05: phytoplankton')
phyto = [('cyanobacteria_sDW','Cyanobacteria','teal'),
         ('diatoms_sDW','Diatoms','goldenrod'),
         ('greens_sDW','Greens','green')]
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for k, (vname, cn, color) in enumerate(phyto):
    ax = axes[k]
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        # depth-average: mean over sigma layers (simple, since sigma evenly spaced)
        da = np.nanmean(var, axis=1)
        sm = spatial_mean(da, wet_mask, axis=(1, 2))
        ax.plot(t3, sm, color=color, lw=1.3)
        ax.set_title(f'{cn} (depth-avg, peak={np.nanmax(sm):.4f})')
    else:
        ax.set_title(f'{cn} (missing)')
    ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m³'); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V05_phytoplankton.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V06 - Zooplankton
# ==================================================================
print('V06: zooplankton')
zoo = [('cladocerans_sD','Cladocerans','darkred'),
       ('copepods_sD','Copepods','purple')]
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for k, (vname, cn, color) in enumerate(zoo):
    ax = axes[k]
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        da = np.nanmean(var, axis=1)
        sm = spatial_mean(da, wet_mask, axis=(1, 2))
        ax.plot(t3, sm, color=color, lw=1.3)
        ax.set_title(f'{cn} (depth-averaged)')
    else:
        ax.set_title(f'{cn} (missing)')
    ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m³'); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V06_zooplankton.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V07 - Fish
# ==================================================================
print('V07: fish')
fish = [('JuFish_sD','Juvenile Fish','darkorange'),
        ('AdFish_sD','Adult Fish','darkred'),
        ('PiscFish_sD','Piscivorous Fish','navy')]
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for k, (vname, cn, color) in enumerate(fish):
    ax = axes[k]
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        da = np.nanmean(var, axis=1)
        sm = spatial_mean(da, wet_mask, axis=(1, 2))
        ax.plot(t3, sm, color=color, lw=1.3)
        ax.set_title(f'{cn} (depth-averaged)')
    else:
        ax.set_title(f'{cn} (missing)')
    ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m³'); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V07_fish.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V08 - Macrophytes & benthos spatial snapshots
# ==================================================================
print('V08: macrophytes & benthos')
macro_v = 'macrophytes_sD'
bent_v  = 'zoobenthos_sD'
snap_idx = [0, len(t3)//3, 2*len(t3)//3, len(t3)-1]
fig = plt.figure(figsize=(18, 10))
if macro_v in ds3d.variables:
    macro = to_np(ds3d.variables[macro_v][:])[v3, :, :]   # 2D (t, y, x) probably
    if macro.ndim == 4:  # (t, z, y, x) -> take bottom or mean
        macro = macro[:, i_bot, :, :]
    for k, ti in enumerate(snap_idx):
        ax = fig.add_subplot(2, 4, k+1)
        im = ax.pcolormesh(lonc, latc, macro[ti, :, :], cmap='YlGn', shading='nearest')
        ax.set_title(f'Macrophytes (day {t3[ti]:.0f})')
        ax.set_aspect('equal'); plt.colorbar(im, ax=ax, label='gDW/m²')
if bent_v in ds3d.variables:
    bent = to_np(ds3d.variables[bent_v][:])[v3, :, :]
    if bent.ndim == 4:
        bent = bent[:, i_bot, :, :]
    bm = spatial_mean(bent, wet_mask, axis=(1, 2))
    ax = fig.add_subplot(2, 4, 5)
    ax.plot(t3, bm, 'saddlebrown', lw=1.3)
    ax.set_title('Zoobenthos (spatial mean)'); ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m²')
    ax.grid(alpha=0.3)
    # final snapshot
    ax = fig.add_subplot(2, 4, 6)
    im = ax.pcolormesh(lonc, latc, bent[-1, :, :], cmap='YlOrBr', shading='nearest')
    ax.set_title(f'Zoobenthos (day {t3[-1]:.0f})'); ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='gDW/m²')
# macrophyte time series whole lake
if macro_v in ds3d.variables:
    mm = spatial_mean(macro, wet_mask, axis=(1, 2))
    ax = fig.add_subplot(2, 4, 7)
    ax.plot(t3, mm, 'green', lw=1.3)
    ax.set_title('Macrophytes (whole-lake mean)'); ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m²')
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V08_macrophytes_benthos.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V09 - Organic matter (POM / DOM)
# ==================================================================
print('V09: organic matter')
pom_v, dom_v = 'POM_sDW', 'DOM_sDW'
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
if pom_v in ds3d.variables:
    pom = to_np(ds3d.variables[pom_v][:])[v3, :, :, :]
    pom_da = np.nanmean(pom, axis=1)
    pom_sm = spatial_mean(pom_da, wet_mask, axis=(1, 2))
    ax.plot(t3, pom_sm, 'saddlebrown', lw=1.3, label='POM')
if dom_v in ds3d.variables:
    dom = to_np(ds3d.variables[dom_v][:])[v3, :, :, :]
    dom_da = np.nanmean(dom, axis=1)
    dom_sm = spatial_mean(dom_da, wet_mask, axis=(1, 2))
    ax.plot(t3, dom_sm, 'goldenrod', lw=1.3, label='DOM')
ax.set_title('Water Column Organic Matter (depth-averaged)'); ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m³')
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
# benthic POM/DOM (2D vars)
for vname, lbl, color in [('POM_sDS','POM benthic','saddlebrown'),
                           ('DOM_sDS','DOM benthic','goldenrod')]:
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :]
        if var.ndim == 4:
            var = var[:, i_bot, :, :]
        sm = spatial_mean(var, wet_mask, axis=(1, 2))
        ax.plot(t3, sm, color=color, lw=1.3, label=lbl)
ax.set_title('Benthic Organic Matter'); ax.set_xlabel('Time (days)'); ax.set_ylabel('gDW/m²')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V09_organic_matter.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V10 - Spatial snapshot: temperature + phyto at 3 times (surface)
# ==================================================================
print('V10: spatial snapshots')
snap = [0, len(t3)//2, len(t3)-1]
fig = plt.figure(figsize=(18, 10))
for k, ti in enumerate(snap):
    ax = fig.add_subplot(2, 3, k+1)
    im = ax.pcolormesh(lonc, latc, t_surf[ti, :, :], cmap='RdYlBu_r', shading='nearest')
    ax.set_title(f'Surface Temperature (day {t3[ti]:.0f})')
    ax.set_aspect('equal'); plt.colorbar(im, ax=ax, label='°C')
for k, ti in enumerate(snap):
    ax = fig.add_subplot(2, 3, k+4)
    if 'diatoms_sDW' in ds3d.variables:
        var = to_np(ds3d.variables['diatoms_sDW'][:])[v3, :, :, :]
        s = var[ti, i_surf, :, :]
        im = ax.pcolormesh(lonc, latc, s, cmap='YlGn', shading='nearest')
        ax.set_title(f'Diatoms Surface (day {t3[ti]:.0f})')
        ax.set_aspect('equal'); plt.colorbar(im, ax=ax, label='gDW/m³')
    else:
        ax.set_title('Diatoms (missing)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V10_spatial_snapshots.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# V11 - Summary dashboard
# ==================================================================
print('V11: summary dashboard')
fig = plt.figure(figsize=(18, 12))
# water level
ax = fig.add_subplot(2, 3, 1)
ax.plot(t2, elev_mean, 'b-', lw=1.2)
ax.set_title('Water Level'); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
# temp
ax = fig.add_subplot(2, 3, 2)
ax.plot(t3, ts_mean, 'r-', lw=1.2, label='Surf')
ax.plot(t3, tb_mean, 'b-', lw=1.2, label='Bot')
ax.set_title('Temperature'); ax.legend(); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
# NH4/NO3
ax = fig.add_subplot(2, 3, 3)
for vname, lbl, c in [('abiotic_water_sNH4W','NH4','blue'),
                       ('abiotic_water_sNO3W','NO3','purple'),
                       ('abiotic_water_sPO4W','PO4','red')]:
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        sm = spatial_mean(var[:, i_surf, :, :], wet_mask, axis=(1, 2))
        ax.plot(t3, sm, c, lw=1.2, label=lbl)
ax.set_title('Nutrients (Surface)'); ax.legend(); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
# phyto
ax = fig.add_subplot(2, 3, 4)
for vname, lbl, c in phyto:
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        sm = spatial_mean(np.nanmean(var, axis=1), wet_mask, axis=(1, 2))
        ax.plot(t3, sm, c, lw=1.2, label=lbl)
ax.set_title('Phytoplankton'); ax.legend(fontsize=8); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
# zoo
ax = fig.add_subplot(2, 3, 5)
for vname, lbl, c in zoo:
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        sm = spatial_mean(np.nanmean(var, axis=1), wet_mask, axis=(1, 2))
        ax.plot(t3, sm, c, lw=1.2, label=lbl)
ax.set_title('Zooplankton'); ax.legend(); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
# fish
ax = fig.add_subplot(2, 3, 6)
for vname, lbl, c in fish:
    if vname in ds3d.variables:
        var = to_np(ds3d.variables[vname][:])[v3, :, :, :]
        sm = spatial_mean(np.nanmean(var, axis=1), wet_mask, axis=(1, 2))
        ax.plot(t3, sm, c, lw=1.2, label=lbl)
ax.set_title('Fish'); ax.legend(fontsize=8); ax.set_xlabel('Days'); ax.grid(alpha=0.3)
plt.suptitle('Theoretical Lake (Heart) 3DWET 366-day Simulation Summary', fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'V11_summary_dashboard.png'), dpi=150, bbox_inches='tight')
plt.close()

# ==================================================================
# cleanup
# ==================================================================
ds2d.close(); ds3d.close()
print('=' * 70)
print(f'All figures saved to: {OUT_DIR}')
print('=' * 70)
