"""
Theoretical Lake - Comprehensive Visualization Suite
====================================================
Generates V01-V20 figures from GETM-FABM-WET model output.

Categories:
  V01  Bathymetry + rivers (3D view)
  V02  Water level time series
  V03  Temperature (time series + vertical profiles + depth-time heatmap)
  V04  3D lake view - bathymetry surface
  V05  3D lake view - temperature at surface (seasonal)
  V06  3D lake view - temperature at bottom (seasonal)
  V07  Velocity / circulation (surface flow field, seasonal)
  V08  Nutrients: NH4, NO3, PO4, O2, SiO2 (time series + vertical)
  V09  Algae: diatoms, cyanobacteria, greens (time series, stacked area, vertical)
  V10  TP (total phosphorus) and PO4 - vertical depth-time histograms
  V11  TN (total nitrogen) and NH4-N, NOx - vertical depth-time histograms
  V12  Zooplankton (cladocerans, copepods)
  V13  Macrophytes + zoobenthos
  V14  Organic matter (POM, DOM, humus)
  V15  2D horizontal seasonal maps - temperature (4 seasons)
  V16  2D horizontal seasonal maps - diatoms (4 seasons)
  V17  2D horizontal seasonal maps - PO4 and TP (4 seasons)
  V18  2D horizontal seasonal maps - NO3 and TN (4 seasons)
  V19  2D horizontal seasonal maps - NH4 and O2 (4 seasons)
  V20  Summary dashboard

Style: English labels, dpi=150, bbox_inches='tight'.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
import netCDF4 as nc
import os
import sys

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

CASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(CASE, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

F2D = os.path.join(CASE, "THEORETICAL_LAKE.2d.nc")
F3D = os.path.join(CASE, "THEORETICAL_LAKE.3d.nc")
FBATHY = os.path.join(CASE, "bathymetry.nc")
FRIVER = os.path.join(CASE, "riverinfo.dat")

DX = DY = 500.0

def to_np(data):
    return np.ma.filled(data, np.nan)

# ------------------------------------------------------------------
# Load bathymetry
# ------------------------------------------------------------------
print("=" * 70)
print("Loading data...")
print("=" * 70)

ds_bathy = nc.Dataset(FBATHY)
bathymetry = to_np(ds_bathy.variables['bathymetry'][:])
ds_bathy.close()

NY, NX = bathymetry.shape
mask = bathymetry > 0.0
depth = np.where(mask, bathymetry, np.nan)
max_depth = float(np.nanmax(bathymetry))

# River positions (1-indexed in file -> 0-indexed)
river_cells = {}
with open(FRIVER) as f:
    n_river = int(f.readline())
    for _ in range(n_river):
        parts = f.readline().split()
        i, j, name = int(parts[0]) - 1, int(parts[1]) - 1, parts[2]
        river_cells.setdefault(name, []).append((i, j))

x_km = (np.arange(NX) + 0.5) * DX / 1000.0
y_km = (np.arange(NY) + 0.5) * DY / 1000.0

dj_deep, di_deep = np.unravel_index(np.nanargmax(bathymetry), bathymetry.shape)

print(f"Grid: {NX} x {NY}, wet cells: {int(mask.sum())}, max depth: {max_depth:.1f} m")

# ------------------------------------------------------------------
# Load model output
# ------------------------------------------------------------------
ds2d = nc.Dataset(F2D)
ds3d = nc.Dataset(F3D)

time2d_raw = to_np(ds2d.variables['time'][:]) / 86400.0
time3d_raw = to_np(ds3d.variables['time'][:]) / 86400.0

def filter_valid(t_arr):
    valid = np.asarray(t_arr) > 0
    n = len(t_arr)
    last = -np.inf
    for i in range(n):
        if valid[i] and t_arr[i] > last:
            last = t_arr[i]
        else:
            valid[i:] = False
            break
    return valid

v2 = filter_valid(time2d_raw)
v3 = filter_valid(time3d_raw)
time2d = time2d_raw[v2]
time3d = time3d_raw[v3]
n2 = len(time2d)
n3 = len(time3d)

if n2 == 0 or n3 == 0:
    print("ERROR: No valid time records in output files.")
    print(f"  2D records: {n2}, 3D records: {n3}")
    ds2d.close(); ds3d.close()
    sys.exit(1)

print(f"2D time records: {n2} (range {time2d[0]:.1f} - {time2d[-1]:.1f} days)")
print(f"3D time records: {n3} (range {time3d[0]:.1f} - {time3d[-1]:.1f} days)")

sigma = to_np(ds3d.variables['sigma'][:])
n_sigma = len(sigma)
z_coords = -sigma * max_depth

elev = to_np(ds2d.variables['elev'][:])[v2]
temp3d = to_np(ds3d.variables['temp'][:])[v3]
uu = to_np(ds3d.variables['uu'][:])[v3]
vv = to_np(ds3d.variables['vv'][:])[v3]
ww = to_np(ds3d.variables['w'][:])[v3] if 'w' in ds3d.variables else None

def load_fabm_var(name):
    if name in ds3d.variables:
        return to_np(ds3d.variables[name][:])[v3]
    return None

# Nutrients
sNH4W = load_fabm_var("abiotic_water_sNH4W")
sNO3W = load_fabm_var("abiotic_water_sNO3W")
sPO4W = load_fabm_var("abiotic_water_sPO4W")
sO2W = load_fabm_var("abiotic_water_sO2W")
sSiO2W = load_fabm_var("abiotic_water_sSiO2W")

# Phytoplankton
diatoms_sDW = load_fabm_var("diatoms_sDW")
cyanobacteria_sDW = load_fabm_var("cyanobacteria_sDW")
greens_sDW = load_fabm_var("greens_sDW")

# Zooplankton
cladocerans_sD = load_fabm_var("cladocerans_sD")
copepods_sD = load_fabm_var("copepods_sD")

# Benthos
zoobenthos_sD = load_fabm_var("zoobenthos_sD")
macrophytes_sD = load_fabm_var("macrophytes_sD")

# Organic matter
POM_sDW = load_fabm_var("POM_sDW")
DOM_sDW = load_fabm_var("DOM_sDW")
humus_sDS = load_fabm_var("humus_sDS")

# Total N and P diagnostics
wet_totN = load_fabm_var("wet_totN")
wet_totP = load_fabm_var("wet_totP")
wet_chla = load_fabm_var("wet_chla")

print(f"FABM vars loaded: NH4={sNH4W is not None}, diatoms={diatoms_sDW is not None}, "
      f"totN={wet_totN is not None}, totP={wet_totP is not None}")

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def spatial_mean(var_3d):
    if var_3d is None:
        return None
    if var_3d.ndim == 4:
        result = np.zeros(var_3d.shape[0])
        for t in range(var_3d.shape[0]):
            vals = var_3d[t, :, mask]
            result[t] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
        return result
    elif var_3d.ndim == 3:
        result = np.zeros(var_3d.shape[0])
        for t in range(var_3d.shape[0]):
            vals = var_3d[t, mask]
            result[t] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
        return result

def get_surface(var_3d):
    if var_3d is None:
        return None
    idx = np.argmin(np.abs(sigma - 0.0))
    return var_3d[:, idx, :, :]

def get_bottom(var_3d):
    if var_3d is None:
        return None
    idx = np.argmin(np.abs(sigma - (-1.0)))
    return var_3d[:, idx, :, :]

def get_layer(var_3d, layer_idx):
    if var_3d is None:
        return None
    return var_3d[:, layer_idx, :, :]

# Season indices (Spring: Mar-May, Summer: Jun-Aug, Autumn: Sep-Nov, Winter: Dec-Feb)
def get_season_indices(time_arr):
    seasons = {}
    for i, t in enumerate(time_arr):
        month = int(t) % 12 + 1
        if month in [3, 4, 5]:
            seasons.setdefault('Spring', []).append(i)
        elif month in [6, 7, 8]:
            seasons.setdefault('Summer', []).append(i)
        elif month in [9, 10, 11]:
            seasons.setdefault('Autumn', []).append(i)
        else:
            seasons.setdefault('Winter', []).append(i)
    return seasons

seasons3d = get_season_indices(time3d)
season_labels = ['Spring', 'Summer', 'Autumn', 'Winter']
season_idx_map = {}
for s in season_labels:
    if s in seasons3d and len(seasons3d[s]) > 0:
        idxs = seasons3d[s]
        mid = idxs[len(idxs) // 2]
        season_idx_map[s] = mid

print(f"Season representative time indices: {season_idx_map}")

# Colormaps
cmap_depth = LinearSegmentedColormap.from_list(
    "lake", ["#a8d8f0", "#5fb3e0", "#2d8fd1", "#1565a8", "#0a3d6b", "#04203f"], N=256)
cmap_depth.set_bad("#d9cdb8")

def plot_rivers(ax):
    for name, cells in river_cells.items():
        is_in = name.startswith("INFL")
        color = "#1b9e3a" if is_in else "#e63946"
        for (i, j) in cells:
            ax.scatter(x_km[i], y_km[j], s=80, c=color, edgecolors="white",
                       linewidths=1.0, zorder=5, marker="o" if is_in else "s")

def save_fig(fig, name):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {name}")

# ============================================================
# V01: Bathymetry + Rivers (with 3D view)
# ============================================================
print("\n" + "=" * 70)
print("V01: Bathymetry and Rivers (3D view)")
print("=" * 70)

fig = plt.figure(figsize=(18, 7))

# 2D map
ax1 = fig.add_subplot(1, 2, 1)
Xc, Yc = np.meshgrid(x_km, y_km)
pcm = ax1.pcolormesh(Xc, Yc, depth, cmap=cmap_depth, shading="auto", vmin=0, vmax=max_depth)
levels = np.arange(1, int(max_depth) + 1, 1)
cs = ax1.contour(Xc, Yc, depth, levels=levels, colors="white", linewidths=0.5, alpha=0.5)
ax1.clabel(cs, inline=True, fontsize=6, fmt="%.0fm")
plot_rivers(ax1)
ax1.scatter(x_km[di_deep], y_km[dj_deep], marker="*", s=250, c="gold",
            edgecolors="black", linewidths=1.0, zorder=6)
ax1.set_title("Bathymetry (2D)", fontsize=13, fontweight="bold")
ax1.set_xlabel("Easting (km)")
ax1.set_ylabel("Northing (km)")
ax1.set_aspect("equal")
fig.colorbar(pcm, ax=ax1, shrink=0.7, label="Depth (m)")

# 3D view
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
X3, Y3 = np.meshgrid(x_km, y_km)
Z3 = np.where(mask, -bathymetry, np.nan)
surf = ax2.plot_surface(X3, Y3, Z3, cmap=cmap_depth, linewidth=0, antialiased=True,
                        alpha=0.9, vmin=-max_depth, vmax=0)
ax2.set_title("Bathymetry (3D)", fontsize=13, fontweight="bold")
ax2.set_xlabel("Easting (km)")
ax2.set_ylabel("Northing (km)")
ax2.set_zlabel("Depth (m)")
ax2.view_init(elev=35, azim=-60)

fig.suptitle("Theoretical Lake - Bathymetry and Rivers\n"
             f"Heart shape, 70.0 km², avg {float(np.nanmean(depth)):.1f} m, max {max_depth:.1f} m",
             fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
save_fig(fig, "V01_bathymetry_3d.png")

# ============================================================
# V02: Water Level Time Series
# ============================================================
print("\n" + "=" * 70)
print("V02: Water Level Time Series")
print("=" * 70)

elev_mean = np.array([np.nanmean(elev[t, mask]) for t in range(n2)])
elev_min = np.array([np.nanmin(elev[t, mask]) for t in range(n2)])
elev_max = np.array([np.nanmax(elev[t, mask]) for t in range(n2)])

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

ax = axes[0, 0]
ax.fill_between(time2d, elev_min, elev_max, alpha=0.3, color='blue', label='Min-Max range')
ax.plot(time2d, elev_mean, 'b-', linewidth=2, label='Mean water level')
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('Lake Water Level Time Series')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Water Level (m)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
ax.plot(time2d, elev_max, 'r-', linewidth=1, label='Max')
ax.plot(time2d, elev_mean, 'b-', linewidth=1.5, label='Mean')
ax.plot(time2d, elev_min, 'g-', linewidth=1, label='Min')
ax.set_title('Water Level Statistics')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Water Level (m)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
if n2 > 1:
    rate = np.gradient(elev_mean, time2d) * 1000
    ax.plot(time2d[1:], rate[1:], 'r-', linewidth=1.5)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('Water Level Change Rate')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Rate (mm/day)')
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
snapshots = [0, n2 // 4, n2 // 2, 3 * n2 // 4, n2 - 1]
for t_idx in snapshots:
    im = ax.pcolormesh(x_km, y_km, elev[t_idx, :, :], cmap='RdBu',
                        vmin=-0.5, vmax=0.5, shading='auto')
    ax.set_title(f'Water Level (Day {time2d[t_idx]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
plt.colorbar(im, ax=ax, label='m')

fig.suptitle("Theoretical Lake - Water Level Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V02_water_level.png")

# ============================================================
# V03: Temperature (time series + vertical profiles + depth-time heatmap)
# ============================================================
print("\n" + "=" * 70)
print("V03: Temperature Dynamics")
print("=" * 70)

temp_surf = get_surface(temp3d)
temp_bot = get_bottom(temp3d)
temp_mid = temp3d[:, n_sigma // 2, :, :]

temp_surf_mean = np.array([np.nanmean(temp_surf[t, mask]) for t in range(n3)])
temp_mid_mean = np.array([np.nanmean(temp_mid[t, mask]) for t in range(n3)])
temp_bot_mean = np.array([np.nanmean(temp_bot[t, mask]) for t in range(n3)])

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

ax = axes[0, 0]
ax.plot(time3d, temp_surf_mean, 'r-', linewidth=2, label='Surface')
ax.plot(time3d, temp_mid_mean, 'g-', linewidth=2, label='Middle')
ax.plot(time3d, temp_bot_mean, 'b-', linewidth=2, label='Bottom')
ax.set_title('Temperature Time Series (Spatial Mean)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Temperature (degC)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
temp_diff = temp_surf_mean - temp_bot_mean
ax.plot(time3d, temp_diff, 'purple', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.set_title('Surface-Bottom Temperature Difference (Stratification)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Temperature Difference (degC)')
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
n_profiles = min(8, n3)
for t_idx in np.linspace(0, n3 - 1, n_profiles, dtype=int):
    profile = temp3d[t_idx, :, dj_deep, di_deep]
    ax.plot(profile, z_coords, '-o', markersize=4, label=f'Day {time3d[t_idx]:.0f}', alpha=0.7)
ax.set_title('Temperature Vertical Profile (Deepest Point)')
ax.set_xlabel('Temperature (degC)')
ax.set_ylabel('Depth (m)')
ax.legend(fontsize=7, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(z_coords.max(), 0)

ax = axes[1, 1]
temp_profile_ts = temp3d[:, :, dj_deep, di_deep]
im = ax.pcolormesh(time3d, z_coords, temp_profile_ts.T, cmap='RdYlBu_r', shading='auto')
ax.set_title('Temperature Depth-Time Heatmap (Deepest Point)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')
ax.set_ylim(z_coords.max(), 0)
plt.colorbar(im, ax=ax, label='degC')

fig.suptitle("Theoretical Lake - Temperature Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V03_temperature.png")

# ============================================================
# V04: 3D Lake View - Bathymetry Surface
# ============================================================
print("\n" + "=" * 70)
print("V04: 3D Lake View - Bathymetry")
print("=" * 70)

fig = plt.figure(figsize=(14, 9))
ax = fig.add_subplot(111, projection='3d')
X3, Y3 = np.meshgrid(x_km, y_km)
Z3 = np.where(mask, bathymetry, 0)
surf = ax.plot_surface(X3, Y3, Z3, cmap=cmap_depth, linewidth=0, antialiased=True,
                        alpha=0.9, vmin=0, vmax=max_depth)
# Rivers
for name, cells in river_cells.items():
    is_in = name.startswith("INFL")
    color = "#1b9e3a" if is_in else "#e63946"
    for (i, j) in cells:
        ax.scatter(x_km[i], y_km[j], bathymetry[j, i], s=120, c=color,
                   edgecolors="white", linewidths=1.0, zorder=5)
ax.set_title("Theoretical Lake - 3D Bathymetry Surface", fontsize=14, fontweight="bold")
ax.set_xlabel("Easting (km)")
ax.set_ylabel("Northing (km)")
ax.set_zlabel("Depth (m)")
ax.view_init(elev=35, azim=-60)
fig.colorbar(surf, ax=ax, shrink=0.5, label="Depth (m)")
save_fig(fig, "V04_3d_bathymetry.png")

# ============================================================
# V05: 3D Lake View - Temperature at Surface (Seasonal)
# ============================================================
print("\n" + "=" * 70)
print("V05: 3D Lake View - Temperature Surface (Seasonal)")
print("=" * 70)

fig = plt.figure(figsize=(20, 5))
for col, slabel in enumerate(season_labels):
    ax = fig.add_subplot(1, 4, col + 1, projection='3d')
    if slabel in season_idx_map:
        t_idx = season_idx_map[slabel]
        surf_data = get_surface(temp3d)[t_idx].copy()
        surf_data[~mask] = np.nan
        Z3 = np.where(mask, surf_data, np.nan)
        surf = ax.plot_surface(X3, Y3, Z3, cmap='RdYlBu_r', linewidth=0,
                                antialiased=True, alpha=0.9, vmin=0, vmax=30)
        ax.set_title(f'{slabel} (Day {time3d[t_idx]:.0f})')
    else:
        ax.set_title(f'{slabel} (no data)')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('degC')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(0, 30)

fig.suptitle("Theoretical Lake - 3D Surface Temperature (Seasonal)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
save_fig(fig, "V05_3d_temp_surface_seasonal.png")

# ============================================================
# V06: 3D Lake View - Temperature at Bottom (Seasonal)
# ============================================================
print("\n" + "=" * 70)
print("V06: 3D Lake View - Temperature Bottom (Seasonal)")
print("=" * 70)

fig = plt.figure(figsize=(20, 5))
for col, slabel in enumerate(season_labels):
    ax = fig.add_subplot(1, 4, col + 1, projection='3d')
    if slabel in season_idx_map:
        t_idx = season_idx_map[slabel]
        bot_data = get_bottom(temp3d)[t_idx].copy()
        bot_data[~mask] = np.nan
        Z3 = np.where(mask, bot_data, np.nan)
        surf = ax.plot_surface(X3, Y3, Z3, cmap='RdYlBu_r', linewidth=0,
                                antialiased=True, alpha=0.9, vmin=0, vmax=30)
        ax.set_title(f'{slabel} (Day {time3d[t_idx]:.0f})')
    else:
        ax.set_title(f'{slabel} (no data)')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('degC')
    ax.view_init(elev=30, azim=-60)
    ax.set_zlim(0, 30)

fig.suptitle("Theoretical Lake - 3D Bottom Temperature (Seasonal)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
save_fig(fig, "V06_3d_temp_bottom_seasonal.png")

# ============================================================
# V07: Velocity / Circulation (Seasonal surface flow fields)
# ============================================================
print("\n" + "=" * 70)
print("V07: Circulation (Seasonal)")
print("=" * 70)

speed3d = np.sqrt(uu**2 + vv**2)
speed_surf = get_surface(speed3d)

fig, axes = plt.subplots(2, 2, figsize=(16, 13))
for i, slabel in enumerate(season_labels):
    ax = axes[i // 2, i % 2]
    if slabel in season_idx_map:
        t_idx = season_idx_map[slabel]
        u_s = get_surface(uu)[t_idx]
        v_s = get_surface(vv)[t_idx]
        spd_s = speed_surf[t_idx]
        spd_plot = np.where(mask, spd_s * 100, np.nan)
        im = ax.pcolormesh(x_km, y_km, spd_plot, cmap='YlOrRd', shading='auto', vmin=0, vmax=10)
        step = 2
        ax.quiver(x_km[::step], y_km[::step], u_s[::step, ::step], v_s[::step, ::step],
                   color='black', scale=0.05, width=0.003)
        plot_rivers(ax)
        ax.set_title(f'{slabel} Surface Flow (Day {time3d[t_idx]:.0f})')
    else:
        ax.set_title(f'{slabel} (no data)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    if 'im' in dir():
        plt.colorbar(im, ax=ax, label='cm/s')

fig.suptitle("Theoretical Lake - Seasonal Surface Circulation", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V07_circulation_seasonal.png")

# ============================================================
# V08: Nutrients (NH4, NO3, PO4, O2, SiO2)
# ============================================================
print("\n" + "=" * 70)
print("V08: Nutrients Time Series")
print("=" * 70)

nutrient_vars = [
    (sNH4W, "NH4 (g/m3)", "Ammonium", '#1b9e77'),
    (sNO3W, "NO3 (g/m3)", "Nitrate", '#7570b3'),
    (sPO4W, "PO4 (g/m3)", "Phosphate", '#d95f02'),
    (sO2W, "O2 (g/m3)", "Oxygen", '#e7298a'),
    (sSiO2W, "SiO2 (g/m3)", "Silica", '#66a61e'),
]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes_flat = axes.flatten()

for idx, (var, unit, label, color) in enumerate(nutrient_vars):
    ax = axes_flat[idx]
    if var is not None:
        mean_ts = spatial_mean(var)
        surf_ts = np.array([np.nanmean(get_surface(var)[t, mask]) for t in range(n3)])
        bot_ts = np.array([np.nanmean(get_bottom(var)[t, mask]) for t in range(n3)])
        ax.plot(time3d, surf_ts, 'r-', linewidth=1.5, label='Surface', alpha=0.8)
        ax.plot(time3d, mean_ts, 'k-', linewidth=2, label='Mean')
        ax.plot(time3d, bot_ts, 'b-', linewidth=1.5, label='Bottom', alpha=0.8)
        ax.set_title(label)
        ax.set_ylabel(unit)
    else:
        ax.set_title(f"{label} (not available)")
    ax.set_xlabel('Time (days)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

ax = axes_flat[5]
if sNO3W is not None and sPO4W is not None:
    no3_mean = spatial_mean(sNO3W)
    po4_mean = spatial_mean(sPO4W)
    ratio = (no3_mean / 14.0) / (po4_mean / 31.0 + 1e-10)
    ax.plot(time3d, ratio, 'purple', linewidth=2)
    ax.axhline(y=16, color='k', linestyle='--', alpha=0.5, label="Redfield (16:1)")
    ax.set_title('N:P Ratio (Atomic)')
    ax.set_ylabel('N:P')
    ax.legend(fontsize=8)
else:
    ax.set_title("N:P Ratio (not available)")
ax.set_xlabel('Time (days)')
ax.grid(True, alpha=0.3)

fig.suptitle("Theoretical Lake - Nutrient Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V08_nutrients.png")

# ============================================================
# V09: Algae (diatoms, cyanobacteria, greens)
# ============================================================
print("\n" + "=" * 70)
print("V09: Phytoplankton Dynamics")
print("=" * 70)

phyto_vars = [
    (diatoms_sDW, "Diatoms", '#1b9e77'),
    (cyanobacteria_sDW, "Cyanobacteria", '#7570b3'),
    (greens_sDW, "Green Algae", '#d95f02'),
]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

ax = axes[0, 0]
for var, label, color in phyto_vars:
    if var is not None:
        ax.plot(time3d, spatial_mean(var), '-', linewidth=2, label=label, color=color)
ax.set_title('Phytoplankton Biomass (Spatial Mean)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
means = []
labels_list = []
colors_list = []
for var, label, color in phyto_vars:
    if var is not None:
        means.append(spatial_mean(var))
        labels_list.append(label)
        colors_list.append(color)
if means:
    ax.stackplot(time3d, *means, labels=labels_list, colors=colors_list, alpha=0.7)
ax.set_title('Phytoplankton Composition (Stacked)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
if diatoms_sDW is not None:
    surf = np.array([np.nanmean(get_surface(diatoms_sDW)[t, mask]) for t in range(n3)])
    bot = np.array([np.nanmean(get_bottom(diatoms_sDW)[t, mask]) for t in range(n3)])
    mean_ts = spatial_mean(diatoms_sDW)
    ax.plot(time3d, surf, 'r-', linewidth=1.5, label='Surface', alpha=0.8)
    ax.plot(time3d, mean_ts, 'k-', linewidth=2, label='Mean')
    ax.plot(time3d, bot, 'b-', linewidth=1.5, label='Bottom', alpha=0.8)
ax.set_title('Diatoms - Vertical Distribution')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
if cyanobacteria_sDW is not None:
    surf = np.array([np.nanmean(get_surface(cyanobacteria_sDW)[t, mask]) for t in range(n3)])
    bot = np.array([np.nanmean(get_bottom(cyanobacteria_sDW)[t, mask]) for t in range(n3)])
    mean_ts = spatial_mean(cyanobacteria_sDW)
    ax.plot(time3d, surf, 'r-', linewidth=1.5, label='Surface', alpha=0.8)
    ax.plot(time3d, mean_ts, 'k-', linewidth=2, label='Mean')
    ax.plot(time3d, bot, 'b-', linewidth=1.5, label='Bottom', alpha=0.8)
ax.set_title('Cyanobacteria - Vertical Distribution')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

fig.suptitle("Theoretical Lake - Phytoplankton Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V09_phytoplankton.png")

# ============================================================
# V10: TP and PO4 - Vertical Depth-Time Histograms
# ============================================================
print("\n" + "=" * 70)
print("V10: TP and PO4 - Vertical Depth-Time")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# PO4 at deepest point
ax = axes[0, 0]
if sPO4W is not None:
    data = sPO4W[:, :, dj_deep, di_deep].T
    im = ax.pcolormesh(time3d, z_coords, data, cmap='Blues', shading='auto')
    ax.set_title(f'PO4 Depth-Time (Deepest Point)')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# TP at deepest point
ax = axes[0, 1]
if wet_totP is not None:
    data = wet_totP[:, :, dj_deep, di_deep].T
    im = ax.pcolormesh(time3d, z_coords, data, cmap='Blues', shading='auto')
    ax.set_title(f'Total P Depth-Time (Deepest Point)')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# PO4 spatial mean by depth
ax = axes[1, 0]
if sPO4W is not None:
    # Mean over wet cells for each (time, sigma)
    po4_depth_ts = np.zeros((n3, n_sigma))
    for t in range(n3):
        for k in range(n_sigma):
            vals = sPO4W[t, k, mask]
            po4_depth_ts[t, k] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
    im = ax.pcolormesh(time3d, z_coords, po4_depth_ts.T, cmap='Blues', shading='auto')
    ax.set_title('PO4 Spatial Mean Depth-Time')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# TP spatial mean by depth
ax = axes[1, 1]
if wet_totP is not None:
    tp_depth_ts = np.zeros((n3, n_sigma))
    for t in range(n3):
        for k in range(n_sigma):
            vals = wet_totP[t, k, mask]
            tp_depth_ts[t, k] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
    im = ax.pcolormesh(time3d, z_coords, tp_depth_ts.T, cmap='Blues', shading='auto')
    ax.set_title('Total P Spatial Mean Depth-Time')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

fig.suptitle("Theoretical Lake - Phosphorus: TP and PO4 Vertical Distribution",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V10_TP_PO4_vertical.png")

# ============================================================
# V11: TN, NH4-N, NOx - Vertical Depth-Time Histograms
# ============================================================
print("\n" + "=" * 70)
print("V11: TN, NH4, NOx - Vertical Depth-Time")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# NH4 at deepest point
ax = axes[0, 0]
if sNH4W is not None:
    data = sNH4W[:, :, dj_deep, di_deep].T
    im = ax.pcolormesh(time3d, z_coords, data, cmap='Greens', shading='auto')
    ax.set_title(f'NH4-N Depth-Time (Deepest Point)')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# NO3 at deepest point
ax = axes[0, 1]
if sNO3W is not None:
    data = sNO3W[:, :, dj_deep, di_deep].T
    im = ax.pcolormesh(time3d, z_coords, data, cmap='Purples', shading='auto')
    ax.set_title(f'NO3-N Depth-Time (Deepest Point)')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# TN at deepest point
ax = axes[0, 2]
if wet_totN is not None:
    data = wet_totN[:, :, dj_deep, di_deep].T
    im = ax.pcolormesh(time3d, z_coords, data, cmap='Oranges', shading='auto')
    ax.set_title(f'Total N Depth-Time (Deepest Point)')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# NH4 spatial mean by depth
ax = axes[1, 0]
if sNH4W is not None:
    nh4_depth_ts = np.zeros((n3, n_sigma))
    for t in range(n3):
        for k in range(n_sigma):
            vals = sNH4W[t, k, mask]
            nh4_depth_ts[t, k] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
    im = ax.pcolormesh(time3d, z_coords, nh4_depth_ts.T, cmap='Greens', shading='auto')
    ax.set_title('NH4-N Spatial Mean Depth-Time')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# NO3 spatial mean by depth
ax = axes[1, 1]
if sNO3W is not None:
    no3_depth_ts = np.zeros((n3, n_sigma))
    for t in range(n3):
        for k in range(n_sigma):
            vals = sNO3W[t, k, mask]
            no3_depth_ts[t, k] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
    im = ax.pcolormesh(time3d, z_coords, no3_depth_ts.T, cmap='Purples', shading='auto')
    ax.set_title('NO3-N Spatial Mean Depth-Time')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

# TN spatial mean by depth
ax = axes[1, 2]
if wet_totN is not None:
    tn_depth_ts = np.zeros((n3, n_sigma))
    for t in range(n3):
        for k in range(n_sigma):
            vals = wet_totN[t, k, mask]
            tn_depth_ts[t, k] = np.nanmean(vals) if np.any(np.isfinite(vals)) else np.nan
    im = ax.pcolormesh(time3d, z_coords, tn_depth_ts.T, cmap='Oranges', shading='auto')
    ax.set_title('Total N Spatial Mean Depth-Time')
    ax.set_ylim(z_coords.max(), 0)
    plt.colorbar(im, ax=ax, label='g/m3')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Depth (m)')

fig.suptitle("Theoretical Lake - Nitrogen: TN, NH4-N, NO3-N Vertical Distribution",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V11_TN_NH4_NOx_vertical.png")

# ============================================================
# V12: Zooplankton
# ============================================================
print("\n" + "=" * 70)
print("V12: Zooplankton")
print("=" * 70)

zoo_vars = [
    (cladocerans_sD, "Cladocerans", '#1b9e77'),
    (copepods_sD, "Copepods", '#7570b3'),
]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
for var, label, color in zoo_vars:
    if var is not None:
        ax.plot(time3d, spatial_mean(var), '-', linewidth=2, label=label, color=color)
ax.set_title('Zooplankton Biomass (Spatial Mean)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

ax = axes[1]
for var, label, color in zoo_vars:
    if var is not None:
        ax.plot(time3d, spatial_mean(var), '-', linewidth=2, label=label, color=color)
ax.set_title('Zooplankton (Linear Scale)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3)')
ax.legend()
ax.grid(True, alpha=0.3)

fig.suptitle("Theoretical Lake - Zooplankton Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V12_zooplankton.png")

# ============================================================
# V13: Macrophytes + Zoobenthos
# ============================================================
print("\n" + "=" * 70)
print("V13: Macrophytes + Zoobenthos")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

ax = axes[0, 0]
if macrophytes_sD is not None:
    mean_ts = spatial_mean(macrophytes_sD)
    ax.plot(time3d, mean_ts, 'g-', linewidth=2, label='Mean')
    ax.fill_between(time3d,
                     np.array([np.nanmin(macrophytes_sD[t, mask]) for t in range(n3)]),
                     np.array([np.nanmax(macrophytes_sD[t, mask]) for t in range(n3)]),
                     alpha=0.3, color='green', label='Min-Max range')
ax.set_title('Macrophytes Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m2)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
if macrophytes_sD is not None:
    mid_t = n3 // 2
    data = np.where(mask, macrophytes_sD[mid_t, :, :], np.nan)
    im = ax.pcolormesh(x_km, y_km, data, cmap='YlGn', shading='auto')
    ax.set_title(f'Macrophytes Distribution (Day {time3d[mid_t]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='gDW/m2')
else:
    ax.set_title("Macrophytes (not available)")

ax = axes[1, 0]
if zoobenthos_sD is not None:
    mean_ts = spatial_mean(zoobenthos_sD)
    ax.plot(time3d, mean_ts, 'b-', linewidth=2, label='Mean')
    ax.fill_between(time3d,
                     np.array([np.nanmin(zoobenthos_sD[t, mask]) for t in range(n3)]),
                     np.array([np.nanmax(zoobenthos_sD[t, mask]) for t in range(n3)]),
                     alpha=0.3, color='blue', label='Min-Max range')
ax.set_title('Zoobenthos Biomass')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m2)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
if zoobenthos_sD is not None:
    mid_t = n3 // 2
    data = np.where(mask, zoobenthos_sD[mid_t, :, :], np.nan)
    im = ax.pcolormesh(x_km, y_km, data, cmap='Blues', shading='auto')
    ax.set_title(f'Zoobenthos Distribution (Day {time3d[mid_t]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='gDW/m2')
else:
    ax.set_title("Zoobenthos (not available)")

fig.suptitle("Theoretical Lake - Macrophytes & Benthos", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V13_macrophytes_benthos.png")

# ============================================================
# V14: Organic Matter
# ============================================================
print("\n" + "=" * 70)
print("V14: Organic Matter")
print("=" * 70)

om_vars = [
    (POM_sDW, "POM (Particulate)", '#d95f02'),
    (DOM_sDW, "DOM (Dissolved)", '#1b9e77'),
    (humus_sDS, "Humus (Sediment)", '#7570b3'),
]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

ax = axes[0, 0]
for var, label, color in om_vars:
    if var is not None:
        ax.plot(time3d, spatial_mean(var), '-', linewidth=2, label=label, color=color)
ax.set_title('Organic Matter Pools (Spatial Mean)')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Biomass (gDW/m3 or gDW/m2)')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
if POM_sDW is not None:
    n_profiles = min(8, n3)
    for t_idx in np.linspace(0, n3 - 1, n_profiles, dtype=int):
        profile = POM_sDW[t_idx, :, dj_deep, di_deep]
        ax.plot(profile, z_coords, '-o', markersize=4, label=f'Day {time3d[t_idx]:.0f}', alpha=0.7)
ax.set_title('POM Vertical Profile (Deepest Point)')
ax.set_xlabel('POM (gDW/m3)')
ax.set_ylabel('Depth (m)')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)
ax.set_ylim(z_coords.max(), 0)

ax = axes[1, 0]
if POM_sDW is not None:
    mid_t = n3 // 2
    pom_surf = get_surface(POM_sDW)
    data = np.where(mask, pom_surf[mid_t, :, :], np.nan)
    im = ax.pcolormesh(x_km, y_km, data, cmap='YlOrBr', shading='auto')
    ax.set_title(f'POM Surface (Day {time3d[mid_t]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='gDW/m3')
else:
    ax.set_title("POM (not available)")

ax = axes[1, 1]
if DOM_sDW is not None:
    surf_ts = np.array([np.nanmean(get_surface(DOM_sDW)[t, mask]) for t in range(n3)])
    bot_ts = np.array([np.nanmean(get_bottom(DOM_sDW)[t, mask]) for t in range(n3)])
    ax.plot(time3d, surf_ts, 'r-', linewidth=1.5, label='Surface', alpha=0.8)
    ax.plot(time3d, bot_ts, 'b-', linewidth=1.5, label='Bottom', alpha=0.8)
ax.set_title('DOM Surface vs Bottom')
ax.set_xlabel('Time (days)')
ax.set_ylabel('DOM (gDW/m3)')
ax.legend()
ax.grid(True, alpha=0.3)

fig.suptitle("Theoretical Lake - Organic Matter Dynamics", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V14_organic_matter.png")

# ============================================================
# V15: 2D Horizontal Seasonal Maps - Temperature
# ============================================================
print("\n" + "=" * 70)
print("V15: Seasonal Temperature Maps")
print("=" * 70)

fig, axes = plt.subplots(2, 4, figsize=(24, 11))
for i, slabel in enumerate(season_labels):
    if slabel not in season_idx_map:
        continue
    t_idx = season_idx_map[slabel]
    # Surface
    ax = axes[0, i]
    data = get_surface(temp3d)[t_idx].copy()
    data[~mask] = np.nan
    im = ax.pcolormesh(x_km, y_km, data, cmap='RdYlBu_r', shading='auto', vmin=0, vmax=30)
    ax.set_title(f'{slabel} Surface Temp (Day {time3d[t_idx]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='degC')
    # Bottom
    ax = axes[1, i]
    data = get_bottom(temp3d)[t_idx].copy()
    data[~mask] = np.nan
    im = ax.pcolormesh(x_km, y_km, data, cmap='RdYlBu_r', shading='auto', vmin=0, vmax=30)
    ax.set_title(f'{slabel} Bottom Temp (Day {time3d[t_idx]:.0f})')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='degC')

fig.suptitle("Theoretical Lake - Seasonal Temperature (2D Horizontal)", fontsize=15, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V15_seasonal_temperature.png")

# ============================================================
# V16: 2D Horizontal Seasonal Maps - Diatoms
# ============================================================
print("\n" + "=" * 70)
print("V16: Seasonal Diatom Maps")
print("=" * 70)

fig, axes = plt.subplots(1, 4, figsize=(24, 5.5))
for i, slabel in enumerate(season_labels):
    ax = axes[i]
    if slabel in season_idx_map and diatoms_sDW is not None:
        t_idx = season_idx_map[slabel]
        data = get_surface(diatoms_sDW)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='YlGn', shading='auto')
        ax.set_title(f'{slabel} Diatoms (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='gDW/m3')
    else:
        ax.set_title(f'{slabel} (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')

fig.suptitle("Theoretical Lake - Seasonal Diatom Distribution (Surface)", fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
save_fig(fig, "V16_seasonal_diatoms.png")

# ============================================================
# V17: 2D Horizontal Seasonal Maps - PO4 and TP
# ============================================================
print("\n" + "=" * 70)
print("V17: Seasonal PO4 and TP Maps")
print("=" * 70)

fig, axes = plt.subplots(2, 4, figsize=(24, 11))
for i, slabel in enumerate(season_labels):
    if slabel not in season_idx_map:
        continue
    t_idx = season_idx_map[slabel]
    # PO4 surface
    ax = axes[0, i]
    if sPO4W is not None:
        data = get_surface(sPO4W)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='Blues', shading='auto')
        ax.set_title(f'{slabel} PO4 (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} PO4 (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    # TP surface
    ax = axes[1, i]
    if wet_totP is not None:
        data = get_surface(wet_totP)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='Blues', shading='auto')
        ax.set_title(f'{slabel} TP (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} TP (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')

fig.suptitle("Theoretical Lake - Seasonal Phosphorus: PO4 (top) and TP (bottom)",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V17_seasonal_PO4_TP.png")

# ============================================================
# V18: 2D Horizontal Seasonal Maps - NO3 and TN
# ============================================================
print("\n" + "=" * 70)
print("V18: Seasonal NO3 and TN Maps")
print("=" * 70)

fig, axes = plt.subplots(2, 4, figsize=(24, 11))
for i, slabel in enumerate(season_labels):
    if slabel not in season_idx_map:
        continue
    t_idx = season_idx_map[slabel]
    # NO3 surface
    ax = axes[0, i]
    if sNO3W is not None:
        data = get_surface(sNO3W)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='Purples', shading='auto')
        ax.set_title(f'{slabel} NO3 (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} NO3 (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    # TN surface
    ax = axes[1, i]
    if wet_totN is not None:
        data = get_surface(wet_totN)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='Oranges', shading='auto')
        ax.set_title(f'{slabel} TN (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} TN (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')

fig.suptitle("Theoretical Lake - Seasonal Nitrogen: NO3 (top) and TN (bottom)",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V18_seasonal_NO3_TN.png")

# ============================================================
# V19: 2D Horizontal Seasonal Maps - NH4 and O2
# ============================================================
print("\n" + "=" * 70)
print("V19: Seasonal NH4 and O2 Maps")
print("=" * 70)

fig, axes = plt.subplots(2, 4, figsize=(24, 11))
for i, slabel in enumerate(season_labels):
    if slabel not in season_idx_map:
        continue
    t_idx = season_idx_map[slabel]
    # NH4 surface
    ax = axes[0, i]
    if sNH4W is not None:
        data = get_surface(sNH4W)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='Greens', shading='auto')
        ax.set_title(f'{slabel} NH4 (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} NH4 (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')
    # O2 surface
    ax = axes[1, i]
    if sO2W is not None:
        data = get_surface(sO2W)[t_idx].copy()
        data[~mask] = np.nan
        im = ax.pcolormesh(x_km, y_km, data, cmap='RdYlGn', shading='auto')
        ax.set_title(f'{slabel} O2 (Day {time3d[t_idx]:.0f})')
        plt.colorbar(im, ax=ax, label='g/m3')
    else:
        ax.set_title(f'{slabel} O2 (N/A)')
    ax.set_xlabel('Easting (km)')
    ax.set_ylabel('Northing (km)')
    ax.set_aspect('equal')

fig.suptitle("Theoretical Lake - Seasonal NH4 (top) and O2 (bottom)",
             fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
save_fig(fig, "V19_seasonal_NH4_O2.png")

# ============================================================
# V20: Summary Dashboard
# ============================================================
print("\n" + "=" * 70)
print("V20: Summary Dashboard")
print("=" * 70)

speed_surf_mean = np.array([np.nanmean(speed_surf[t, mask]) for t in range(n3)])
speed_bot_mean = np.array([np.nanmean(get_bottom(speed3d)[t, mask]) for t in range(n3)])

fig = plt.figure(figsize=(22, 16))

# (a) Temperature
ax_a = fig.add_subplot(4, 3, 1)
ax_a.plot(time3d, temp_surf_mean, 'r-', linewidth=1.5, label='Surface')
ax_a.plot(time3d, temp_bot_mean, 'b-', linewidth=1.5, label='Bottom')
ax_a.set_title('(a) Temperature', fontweight='bold')
ax_a.set_xlabel('Days')
ax_a.set_ylabel('degC')
ax_a.legend(fontsize=7)
ax_a.grid(True, alpha=0.3)

# (b) Water level
ax_b = fig.add_subplot(4, 3, 2)
ax_b.plot(time2d, elev_mean, 'b-', linewidth=1.5)
ax_b.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax_b.set_title('(b) Water Level', fontweight='bold')
ax_b.set_xlabel('Days')
ax_b.set_ylabel('m')
ax_b.grid(True, alpha=0.3)

# (c) Current speed
ax_c = fig.add_subplot(4, 3, 3)
ax_c.plot(time3d, speed_surf_mean * 100, 'r-', linewidth=1.5, label='Surface')
ax_c.plot(time3d, speed_bot_mean * 100, 'b-', linewidth=1.5, label='Bottom')
ax_c.set_title('(c) Current Speed', fontweight='bold')
ax_c.set_xlabel('Days')
ax_c.set_ylabel('cm/s')
ax_c.legend(fontsize=7)
ax_c.grid(True, alpha=0.3)

# (d) Phytoplankton
ax_d = fig.add_subplot(4, 3, 4)
for var, label, color in phyto_vars:
    if var is not None:
        ax_d.plot(time3d, spatial_mean(var), '-', linewidth=1.5, label=label, color=color)
ax_d.set_title('(d) Phytoplankton', fontweight='bold')
ax_d.set_xlabel('Days')
ax_d.set_ylabel('gDW/m3')
ax_d.legend(fontsize=7)
ax_d.grid(True, alpha=0.3)

# (e) Zooplankton
ax_e = fig.add_subplot(4, 3, 5)
for var, label, color in zoo_vars:
    if var is not None:
        ax_e.plot(time3d, spatial_mean(var), '-', linewidth=1.5, label=label, color=color)
ax_e.set_title('(e) Zooplankton', fontweight='bold')
ax_e.set_xlabel('Days')
ax_e.set_ylabel('gDW/m3')
ax_e.legend(fontsize=7)
ax_e.set_yscale('log')
ax_e.grid(True, alpha=0.3)

# (f) Nutrients (NO3 + PO4)
ax_f = fig.add_subplot(4, 3, 6)
if sNO3W is not None:
    ax_f.plot(time3d, spatial_mean(sNO3W), 'b-', linewidth=1.5, label='NO3')
if sPO4W is not None:
    ax_f.plot(time3d, spatial_mean(sPO4W) * 10, 'r-', linewidth=1.5, label='PO4 x10')
ax_f.set_title('(f) Nutrients', fontweight='bold')
ax_f.set_xlabel('Days')
ax_f.set_ylabel('g/m3')
ax_f.legend(fontsize=7)
ax_f.grid(True, alpha=0.3)

# (g) NH4
ax_g = fig.add_subplot(4, 3, 7)
if sNH4W is not None:
    ax_g.plot(time3d, spatial_mean(sNH4W), 'g-', linewidth=1.5)
ax_g.set_title('(g) Ammonium (NH4)', fontweight='bold')
ax_g.set_xlabel('Days')
ax_g.set_ylabel('g/m3')
ax_g.grid(True, alpha=0.3)

# (h) Oxygen
ax_h = fig.add_subplot(4, 3, 8)
if sO2W is not None:
    ax_h.plot(time3d, spatial_mean(sO2W), 'c-', linewidth=1.5)
ax_h.set_title('(h) Dissolved Oxygen', fontweight='bold')
ax_h.set_xlabel('Days')
ax_h.set_ylabel('g/m3')
ax_h.grid(True, alpha=0.3)

# (i) TP and TN
ax_i = fig.add_subplot(4, 3, 9)
if wet_totP is not None:
    ax_i.plot(time3d, spatial_mean(wet_totP), 'r-', linewidth=1.5, label='TP')
if wet_totN is not None:
    ax_i.plot(time3d, spatial_mean(wet_totN), 'b-', linewidth=1.5, label='TN')
ax_i.set_title('(i) Total P and Total N', fontweight='bold')
ax_i.set_xlabel('Days')
ax_i.set_ylabel('g/m3')
ax_i.legend(fontsize=7)
ax_i.grid(True, alpha=0.3)

# (j) Macrophytes
ax_j = fig.add_subplot(4, 3, 10)
if macrophytes_sD is not None:
    ax_j.plot(time3d, spatial_mean(macrophytes_sD), 'g-', linewidth=1.5)
ax_j.set_title('(j) Macrophytes', fontweight='bold')
ax_j.set_xlabel('Days')
ax_j.set_ylabel('gDW/m2')
ax_j.grid(True, alpha=0.3)

# (k) Chlorophyll-a
ax_k = fig.add_subplot(4, 3, 11)
if wet_chla is not None:
    ax_k.plot(time3d, spatial_mean(wet_chla), 'g-', linewidth=1.5)
ax_k.set_title('(k) Chlorophyll-a', fontweight='bold')
ax_k.set_xlabel('Days')
ax_k.set_ylabel('ug/L')
ax_k.grid(True, alpha=0.3)

# (l) Organic matter
ax_l = fig.add_subplot(4, 3, 12)
for var, label, color in om_vars:
    if var is not None:
        ax_l.plot(time3d, spatial_mean(var), '-', linewidth=1.5, label=label, color=color)
ax_l.set_title('(l) Organic Matter', fontweight='bold')
ax_l.set_xlabel('Days')
ax_l.set_ylabel('gDW/m3')
ax_l.legend(fontsize=7)
ax_l.grid(True, alpha=0.3)

fig.suptitle("Theoretical Lake - Summary Dashboard\n"
             f"Grid {NX}x{NY}, {int(mask.sum())} wet cells, max depth {max_depth:.1f} m, "
             f"{n3} time records (Day {time3d[0]:.0f} - {time3d[-1]:.0f})",
             fontsize=15, fontweight="bold", y=1.01)
fig.tight_layout(rect=[0, 0, 1, 0.96])
save_fig(fig, "V20_summary_dashboard.png")

# ============================================================
# Done
# ============================================================
ds2d.close()
ds3d.close()

print("\n" + "=" * 70)
print(f"All figures generated in {PLOT_DIR}")
print("=" * 70)
for f in sorted(os.listdir(PLOT_DIR)):
    if f.startswith("V") and f.endswith(".png"):
        size = os.path.getsize(os.path.join(PLOT_DIR, f))
        print(f"  {f}  ({size // 1024} KB)")
