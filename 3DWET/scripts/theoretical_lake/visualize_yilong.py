"""Visualize Yilong Lake model results - 3D spatial + time series + vertical profiles."""
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
from matplotlib import gridspec
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'case', 'Yilong'))
FIG_DIR = os.path.join(CASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

NX, NY = 28, 8


def to_np(data):
    return np.ma.filled(data, np.nan)


def patch_numrecs(filepath, num_recs):
    """Patch NetCDF3 numrecs field at offset 4."""
    with open(filepath, 'r+b') as f:
        import struct
        f.seek(4)
        f.write(struct.pack('>I', num_recs))


# ============================================================
# Load bathymetry and lake mask
# ============================================================
print("=== Loading data ===")
dsb = nc.Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'), 'r')
bathy = to_np(dsb.variables['bathymetry'][:])
dsb.close()

lake_mask = bathy > 0
print(f"Lake cells: {lake_mask.sum()}/{NX*NY}")

# Patch numrecs if needed (GETM may exit abnormally on meteo EOF)
print("Patching numrecs...")
patch_numrecs(os.path.join(CASE_DIR, 'YILONG.2d.nc'), 730)
patch_numrecs(os.path.join(CASE_DIR, 'YILONG.3d.nc'), 730)
patch_numrecs(os.path.join(CASE_DIR, 'output.nc'), 365)

# Load output
ds = nc.Dataset(os.path.join(CASE_DIR, 'output.nc'), 'r')
ds3 = nc.Dataset(os.path.join(CASE_DIR, 'YILONG.3d.nc'), 'r')
ds2 = nc.Dataset(os.path.join(CASE_DIR, 'YILONG.2d.nc'), 'r')

n_time = len(ds.variables['time'][:])
print(f"output.nc time records: {n_time}")
sigma = to_np(ds3.variables['sigma'][:])
print(f"sigma layers: {len(sigma)}")


def surf_mean(varname):
    if varname not in ds.variables:
        return None
    data = to_np(ds.variables[varname][:])
    if len(data.shape) == 4:
        return np.nanmean(data[:, 0, :, :], axis=(1, 2))
    elif len(data.shape) == 3:
        return np.nanmean(data, axis=(1, 2))
    return data[:]


# ============================================================
# Y01: Bathymetry + Rivers overview
# ============================================================
print("\n=== Generating Y01 bathymetry overview ===")
fig, ax = plt.subplots(figsize=(12, 5))
im = ax.pcolormesh(bathy, cmap='Blues', shading='auto')
ax.set_title('Yilong Lake bathymetry (28×8 grid, 500m, avg 3.5m, max 7m)\n'
             'E-W length 13.8km, N-S width 1.4-3.6km, elongated', fontsize=12)
ax.set_xlabel('x (grid, 500m)')
ax.set_ylabel('y (grid, 500m)')
ax.set_aspect('equal')

# Mark rivers
riverinfo = os.path.join(CASE_DIR, 'riverinfo.dat')
with open(riverinfo, 'r') as f:
    lines = f.readlines()[1:]
for line in lines:
    parts = line.split()
    if len(parts) >= 3:
        i, j, name = int(parts[0]), int(parts[1]), parts[2]
        ax.plot(i-1, j-1, 'rv', markersize=15, markeredgecolor='k')
        ax.text(i-1, j-1+0.4, name, color='red', fontsize=9, ha='center', fontweight='bold')

plt.colorbar(im, ax=ax, label='Depth (m)')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y01_bathymetry.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y01_bathymetry.png")


# ============================================================
# Y02: Phytoplankton time series (key validation)
# ============================================================
print("\n=== Generating Y02 phytoplankton time series ===")
days = np.arange(n_time)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Yilong Lake Model - Phytoplankton time series (after fixing init)\n'
             'Init: Diatoms 0.3, Greens 0.2, Cyanobacteria 0.3 (gDW/m³)', fontsize=13, fontweight='bold')

# 2a: Phytoplankton biomass
ax = axes[0, 0]
for v, label, color in [('diatoms_sDW', 'Diatoms', 'tab:green'),
                         ('greens_sDW', 'Greens', 'tab:orange'),
                         ('cyanobacteria_sDW', 'Cyanobacteria', 'tab:blue')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_title('(a) Phytoplankton biomass (surface spatial mean)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# 2b: Light limitation
ax = axes[0, 1]
for v, label, color in [('diatoms_aLLim', 'Diatoms', 'tab:green'),
                         ('greens_aLLim', 'Greens', 'tab:orange'),
                         ('cyanobacteria_aLLim', 'Cyanobacteria', 'tab:blue')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Light limitation aLLim')
ax.set_title('(b) Light limitation (non-zero after P0 fix)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.05, 1.05)

# 2c: Zooplankton (validation of cascade fix)
ax = axes[1, 0]
for v, label, color in [('cladocerans_sD', 'Cladocerans', 'tab:cyan'),
                         ('copepods_sD', 'Copepods', 'tab:pink')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.axhline(0.3, color='gray', linestyle='--', alpha=0.5, label='Init 0.3')
ax.set_xlabel('Day')
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_title('(c) Zooplankton (init 0.3, verify cascade collapse fix)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# 2d: Fish
ax = axes[1, 1]
for v, label, color in [('JuFish_sD', 'Juvenile', 'tab:olive'),
                         ('AdFish_sD', 'Adult', 'tab:gray'),
                         ('PiscFish_sD', 'Piscivorous', 'tab:red')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_title('(d) Fish (init reduced 50%, verify food chain)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y02_phytoplankton_timeseries.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y02_phytoplankton_timeseries.png")


# ============================================================
# Y03: 3D Spatial distribution (Day 90, 180, 270)
# ============================================================
print("\n=== Generating Y03 spatial distribution ===")
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
fig.suptitle('Yilong Lake Model - Phytoplankton spatial distribution (surface)\n'
             '3 time snapshots showing seasonal evolution', fontsize=13, fontweight='bold')

snapshots = [0, 90, 180]
var_list = [('diatoms_sDW', 'Diatoms', 'Greens'),
            ('greens_sDW', 'Greens', 'Oranges'),
            ('cyanobacteria_sDW', 'Cyanobacteria', 'Blues')]

for col, (var, label, cmap) in enumerate(var_list):
    if var not in ds.variables:
        continue
    data = to_np(ds.variables[var][:])
    vmax = np.nanpercentile(data[:, 0, :, :], 95)
    for row, t_idx in enumerate(snapshots):
        ax = axes[row, col]
        if t_idx < data.shape[0]:
            surf = data[t_idx, 0, :, :]
        else:
            surf = data[-1, 0, :, :]
        # Mask land
        surf_masked = np.where(lake_mask, surf, np.nan)
        im = ax.pcolormesh(surf_masked, cmap=cmap, shading='auto', vmin=0, vmax=max(vmax, 0.01))
        ax.set_title(f'{label} Day{t_idx} (max={np.nanmax(surf):.2f})')
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax, shrink=0.7)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y03_phytoplankton_spatial.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y03_phytoplankton_spatial.png")


# ============================================================
# Y04: Nutrients + Temperature
# ============================================================
print("\n=== Generating Y04 nutrients+temperature ===")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Yilong Lake Model - Nutrients and Temperature\n'
             'Yunnan plateau climate (annual avg 18°C, rainy season May-Oct)', fontsize=13, fontweight='bold')

# 4a: Nutrients
ax = axes[0, 0]
for v, label, color in [('abiotic_water_sNH4W', 'NH4+', 'r'),
                         ('abiotic_water_sNO3W', 'NO3-', 'b'),
                         ('abiotic_water_sPO4W', 'PO4³-', 'purple')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Concentration (g/m³)')
ax.set_title('(a) Nutrients (init: NH4=0.3, NO3=1.0, PO4=0.06)')
ax.legend()
ax.grid(True, alpha=0.3)

# 4b: Temperature (3D file)
ax = axes[0, 1]
if 'temp' in ds3.variables:
    temp = to_np(ds3.variables['temp'][:])
    surf_t = np.nanmean(temp[:, 0, :, :], axis=(1, 2))
    bot_t = np.nanmean(temp[:, -1, :, :], axis=(1, 2))
    days3 = np.arange(len(surf_t))
    ax.plot(days3/2, surf_t, 'r-', label='Surface', linewidth=1.5)
    ax.plot(days3/2, bot_t, 'b-', label='Bottom', linewidth=1.5)
    ax.fill_between(days3/2, surf_t, bot_t, alpha=0.2, color='orange')
ax.set_xlabel('Day')
ax.set_ylabel('Temperature (°C)')
ax.set_title('(b) Temperature (Yunnan plateau annual avg 18°C)')
ax.legend()
ax.grid(True, alpha=0.3)

# 4c: Water level
ax = axes[1, 0]
if 'elev' in ds2.variables:
    elev = to_np(ds2.variables['elev'][:])
    ts = np.nanmean(elev, axis=(1, 2))
    days2 = np.arange(len(ts))
    ax.plot(days2/2, ts, 'b-', linewidth=1.5)
    ax.axhline(ts[0], color='gray', linestyle='--', alpha=0.5, label=f'Initial water level {ts[0]:.3f}m')
    ax.set_title(f'(c) Water level (net change={ts[-1]-ts[0]:.4f}m)')
    ax.legend()
ax.set_xlabel('Day')
ax.set_ylabel('Water level (m)')
ax.grid(True, alpha=0.3)

# 4d: POM and DOM
ax = axes[1, 1]
for v, label, color in [('POM_sDW', 'POM', 'k'),
                         ('DOM_sDW', 'DOM', 'brown')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_xlabel('Day')
ax.set_ylabel('Concentration (g/m³)')
ax.set_title('(d) Organic matter')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y04_nutrients_temp.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y04_nutrients_temp.png")


# ============================================================
# Y05: Vertical profile (center cell)
# ============================================================
print("\n=== Generating Y05 vertical profile ===")
fig, axes = plt.subplots(1, 3, figsize=(15, 6))
fig.suptitle('Yilong Lake Model - Vertical profile (center cell)\n'
             'Showing sigma layers (0=water surface, 10=lake bottom)', fontsize=13, fontweight='bold')

# Find center water cell
center_j, center_i = NY // 2, NX // 2
if not lake_mask[center_j, center_i]:
    # find nearest water cell
    for dj in range(NY):
        for di in range(NX):
            if lake_mask[center_j, center_j]:
                center_j += dj
                center_i += di
                break

snapshots = [0, 90, 180]
var_list = [
    ('diatoms_sDW', 'Diatoms', 'g'),
    ('abiotic_water_sNH4W', 'NH4+', 'r'),
    ('temp', 'Temperature(°C)', 'orange'),
]

for col, (var, label, color) in enumerate(var_list):
    ax = axes[col]
    if var == 'temp':
        data = to_np(ds3.variables[var][:]) if var in ds3.variables else None
    else:
        data = to_np(ds.variables[var][:]) if var in ds.variables else None
    if data is None:
        ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(label)
        continue
    for t_idx, ls in [(0, '-'), (90, '--'), (180, ':')]:
        if t_idx < data.shape[0]:
            if len(data.shape) == 4:
                profile = data[t_idx, :, center_j, center_i]
            else:
                profile = data[t_idx, :, center_j, center_i] if len(data.shape) == 3 else data[t_idx]
            ax.plot(profile, np.arange(len(profile)), ls, color=color, linewidth=2,
                    label=f'Day{t_idx}')
    ax.set_ylim(len(profile)-0.5, -0.5)
    ax.set_xlabel(label)
    ax.set_ylabel('sigma layer (0=surface)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title(label)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y05_vertical_profile.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y05_vertical_profile.png")


# ============================================================
# Y06: Cascade crash check (compare with previous fix)
# ============================================================
print("\n=== Generating Y06 cascade check ===")
fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle('Yilong Lake Model - food chain integrity check\n'
             'Compare with previous round cascade collapse (init adjust: Phytoplankton↑, Zooplankton↑, Fish↓)',
             fontsize=13, fontweight='bold')

# Phytoplankton
ax = axes[0]
for v, label, color in [('diatoms_sDW', 'Diatoms', 'tab:green'),
                         ('greens_sDW', 'Greens', 'tab:orange'),
                         ('cyanobacteria_sDW', 'Cyanobacteria', 'tab:blue')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.axhspan(0.1, 1.0, alpha=0.1, color='green', label='reasonable range')
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_title('(a) Phytoplankton: init 0.2-0.3, expected stable at 0.1-1.0')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-3, 100)

# Zooplankton
ax = axes[1]
for v, label, color in [('cladocerans_sD', 'Cladocerans', 'tab:cyan'),
                         ('copepods_sD', 'Copepods', 'tab:pink')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.axhline(0.3, color='gray', linestyle='--', alpha=0.5, label='Init 0.3')
ax.axhspan(0.05, 0.5, alpha=0.1, color='cyan', label='reasonable range')
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_title('(b) Zooplankton: init 0.3, expected stable (previous round collapse to 0.00001)')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-4, 1)

# Fish
ax = axes[2]
for v, label, color in [('JuFish_sD', 'Juvenile', 'tab:olive'),
                         ('AdFish_sD', 'Adult', 'tab:gray'),
                         ('PiscFish_sD', 'Piscivorous', 'tab:red')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_ylabel('Biomass (gDW/m³)')
ax.set_xlabel('Day')
ax.set_title('(c) Fish: init reduced 50% (Juvenile 0.15, Adult 0.40, Piscivorous 0.05)')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-3, 1)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y06_cascade_check.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y06_cascade_check.png")


# ============================================================
# Summary statistics
# ============================================================
print("\n=== Summary Statistics ===")
stats = []
for v in ['diatoms_sDW', 'greens_sDW', 'cyanobacteria_sDW',
          'diatoms_aLLim', 'greens_aLLim', 'cyanobacteria_aLLim',
          'abiotic_water_sNH4W', 'abiotic_water_sNO3W', 'abiotic_water_sPO4W',
          'cladocerans_sD', 'copepods_sD',
          'JuFish_sD', 'AdFish_sD', 'PiscFish_sD',
          'POM_sDW', 'DOM_sDW']:
    if v not in ds.variables:
        continue
    data = to_np(ds.variables[v][:])
    ts = surf_mean(v)
    stats.append({
        'var': v,
        'min': float(np.nanmin(data)),
        'max': float(np.nanmax(data)),
        'first': float(ts[0]) if len(ts) else float('nan'),
        'last': float(ts[-1]) if len(ts) else float('nan'),
    })

with open(os.path.join(FIG_DIR, 'stats_summary.txt'), 'w') as f:
    f.write("Yilong Lake Model Results Statistics\n")
    f.write("="*70 + "\n")
    f.write(f"{'Variable':<30} {'Min':>12} {'Max':>12} {'Day1':>12} {'DayN':>12}\n")
    f.write("-"*70 + "\n")
    for s in stats:
        f.write(f"{s['var']:<30} {s['min']:>12.6f} {s['max']:>12.6f} {s['first']:>12.6f} {s['last']:>12.6f}\n")

for s in stats:
    print(f"  {s['var']}: min={s['min']:.6f}, max={s['max']:.6f}, first={s['first']:.6f}, last={s['last']:.6f}")

ds.close()
ds3.close()
ds2.close()
print(f"\nAll figures saved to: {FIG_DIR}")
