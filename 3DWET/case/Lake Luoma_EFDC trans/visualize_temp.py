"""Comprehensive temperature visualization for Lake Luoma (baroclinic run).

Generates temperature-specific figures:
  1. 2D surface temperature maps (4 seasons)
  2. 3D temperature body (summer, multi-view)
  3. Vertical temperature profiles (4 seasons, lake center)
  4. Temperature time series (surface/bottom/mean, stratification strength)
  5. 3D temperature cross-section (vertical slice)
  6. Hovmöller diagram (temperature evolution over time at center)
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import netCDF4 as nc
from matplotlib.colors import Normalize
import matplotlib.cm as cm

CASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(CASE, 'figures_temp')
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 110

RUN_ID = 'LUOMA_EFDC_HYD'


def to_np(data):
    return np.ma.filled(data, np.nan)


def find_valid_steps(path_2d):
    ds = nc.Dataset(path_2d)
    n = len(ds.variables['time'])
    elev = ds.variables['elev']
    lo, hi = 0, n - 1
    first_nan = n
    while lo <= hi:
        mid = (lo + hi) // 2
        if np.isnan(elev[mid]).any():
            first_nan = mid
            hi = mid - 1
        else:
            lo = mid + 1
    ds.close()
    return min(first_nan, n)


def load_bathy_and_grid():
    ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
    b = to_np(ds.variables['bathymetry'][:])
    x = to_np(ds.variables['x'][:])
    y = to_np(ds.variables['y'][:])
    ds.close()
    mask = b > 0
    return b, x, y, mask


# load data
print("Loading data...")
b, x, y, mask = load_bathy_and_grid()
X, Y = np.meshgrid(x, y)
Z_bathy = -np.where(mask, b, 0)

path_2d = os.path.join(CASE, f'{RUN_ID}.2d.nc')
n_valid = find_valid_steps(path_2d)
print(f"  Valid steps: {n_valid} ({n_valid*15*576/86400:.1f} days)")

ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
sigma = to_np(ds3.variables['sigma'][:])
print(f"  Sigma levels: {sigma}")
ds3.close()


# ------------------------------------------------------------------
# 1. 2D Surface Temperature (4 seasons)
# ------------------------------------------------------------------
def plot_surface_temp_4seasons(n_valid):
    print("[1/6] 2D surface temperature (4 seasons)...")
    # day 0 (Jan), 90 (Apr), 180 (Jul), 270 (Oct)
    season_days = [0, 90, 180, 270]
    season_names = ['Winter (Jan)', 'Spring (Apr)', 'Summer (Jul)', 'Autumn (Oct)']

    surf_i = int(np.argmin(np.abs(sigma - 0.0)))  # surface layer

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    for k, (day, name) in enumerate(zip(season_days, season_names)):
        ax = axes[k // 2][k % 2]
        step = min(int(day * 86400 / (30 * 288)), n_valid - 1)
        ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
        temp = to_np(ds3.variables['temp'][step, surf_i])
        ds3.close()
        temp_plot = np.where(mask, temp, np.nan)

        pcm = ax.pcolormesh(X, Y, temp_plot, cmap='RdYlBu_r', shading='auto',
                            vmin=0, vmax=30)
        ax.set_title(f'{name} (day {day})')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_aspect('equal')
        fig.colorbar(pcm, ax=ax, label='°C', shrink=0.8)

    fig.suptitle('Lake Luoma Surface Temperature (4 Seasons)', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temp_01_surface_4seasons.png'))
    plt.close(fig)
    print("  -> temp_01_surface_4seasons.png")


# ------------------------------------------------------------------
# 2. 3D Temperature Body (summer, multi-view)
# ------------------------------------------------------------------
def plot_temp_3d_body(n_valid):
    print("[2/6] 3D temperature body (summer)...")
    step = min(int(180 * 86400 / (30 * 288)), n_valid - 1)  # day 180 (summer)
    surf_i = int(np.argmin(np.abs(sigma - 0.0)))

    ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
    temp_s = to_np(ds3.variables['temp'][step, surf_i])
    day = ds3.variables['time'][step] / 86400
    ds3.close()
    temp_plot = np.where(mask, temp_s, np.nan)

    views = [(35, 120), (50, 210), (25, 300), (60, 60)]
    fig = plt.figure(figsize=(16, 12))
    norm = Normalize(vmin=np.nanmin(temp_plot), vmax=np.nanmax(temp_plot))
    colors = cm.RdYlBu_r(norm(np.nan_to_num(temp_plot, nan=0)))

    for k, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        ax.plot_surface(X, Y, Z_bathy, facecolors=colors,
                        linewidth=0, antialiased=True, alpha=0.85)
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
        ax.set_title(f'elev={elev} azim={azim}')
        ax.view_init(elev=elev, azim=azim)
    mappable = cm.ScalarMappable(norm=norm, cmap='RdYlBu_r')
    mappable.set_array([])
    fig.colorbar(mappable, ax=fig.get_axes(), shrink=0.4, aspect=15, label='°C')
    fig.suptitle(f'3D Temperature Body (surface, day {day:.0f}, summer)', fontsize=14)
    fig.savefig(os.path.join(FIG_DIR, 'temp_02_3d_body.png'), bbox_inches='tight')
    plt.close(fig)
    print("  -> temp_02_3d_body.png")


# ------------------------------------------------------------------
# 3. Vertical Temperature Profiles (4 seasons, lake center)
# ------------------------------------------------------------------
def plot_vertical_profiles(n_valid):
    print("[3/6] Vertical temperature profiles (4 seasons)...")
    # lake center
    j_c, i_c = 23, 26
    H_center = b[j_c, i_c]
    if H_center <= 0:
        # find deepest water cell
        j_c, i_c = np.unravel_index(np.argmax(b), b.shape)
        H_center = b[j_c, i_c]
    print(f"  Center cell: (i={i_c}, j={j_c}), H={H_center:.2f}m")

    season_days = [0, 90, 180, 270]
    season_names = ['Winter (Jan)', 'Spring (Apr)', 'Summer (Jul)', 'Autumn (Oct)']
    colors = ['blue', 'green', 'red', 'orange']

    fig, ax = plt.subplots(figsize=(8, 10))
    ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
    for k, (day, name, color) in enumerate(zip(season_days, season_names, colors)):
        step = min(int(day * 86400 / (30 * 288)), n_valid - 1)
        temp_profile = to_np(ds3.variables['temp'][step, :, j_c, i_c])
        # convert sigma to depth
        depths = sigma * H_center  # sigma: -1 (bottom) to 0 (surface)
        valid = ~np.isnan(temp_profile)
        ax.plot(temp_profile[valid], depths[valid], 'o-', color=color,
                label=name, linewidth=2, markersize=6)
    ds3.close()
    ax.set_xlabel('Temperature (°C)', fontsize=12)
    ax.set_ylabel('Depth (m)', fontsize=12)
    ax.set_title(f'Vertical Temperature Profiles at Lake Center\n'
                 f'(i={i_c}, j={j_c}, H={H_center:.1f}m)', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(H_center, 0)  # surface at top
    ax.axvline(4, color='cyan', linestyle='--', alpha=0.3, label='4°C')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temp_03_vertical_profiles.png'))
    plt.close(fig)
    print("  -> temp_03_vertical_profiles.png")


# ------------------------------------------------------------------
# 4. Temperature Time Series
# ------------------------------------------------------------------
def plot_temp_timeseries(n_valid):
    print("[4/6] Temperature time series...")
    j_c, i_c = 23, 26
    if b[j_c, i_c] <= 0:
        j_c, i_c = np.unravel_index(np.argmax(b), b.shape)

    surf_i = int(np.argmin(np.abs(sigma - 0.0)))
    bot_i = int(np.argmin(np.abs(sigma - (-1.0))))

    ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
    # load in chunks to save memory
    n = n_valid
    t_surf = np.zeros(n)
    t_bot = np.zeros(n)
    t_mean = np.zeros(n)
    days = np.zeros(n)
    for k in range(n):
        days[k] = ds3.variables['time'][k] / 86400
        temp_k = to_np(ds3.variables['temp'][k, :, j_c, i_c])
        t_surf[k] = temp_k[surf_i]
        t_bot[k] = temp_k[bot_i]
        valid = ~np.isnan(temp_k)
        t_mean[k] = np.nanmean(temp_k) if valid.any() else np.nan
    ds3.close()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9))
    ax1.plot(days, t_surf, 'r-', label='Surface', linewidth=1.5)
    ax1.plot(days, t_bot, 'b-', label='Bottom', linewidth=1.5)
    ax1.plot(days, t_mean, 'g--', label='Mean', linewidth=1.5)
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title(f'Temperature Time Series at Lake Center (i={i_c}, j={j_c})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # stratification strength
    strat = t_surf - t_bot
    ax2.fill_between(days, strat, 0, alpha=0.3, color='purple')
    ax2.plot(days, strat, 'purple', linewidth=1.5)
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Surface - Bottom (°C)')
    ax2.set_title('Stratification Strength (ΔT = T_surface - T_bottom)')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='black', linewidth=0.5)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temp_04_timeseries.png'))
    plt.close(fig)
    print("  -> temp_04_timeseries.png")


# ------------------------------------------------------------------
# 5. 3D Temperature Cross-section
# ------------------------------------------------------------------
def plot_temp_crosssection(n_valid):
    print("[5/6] 3D temperature cross-section...")
    step = min(int(180 * 86400 / (30 * 288)), n_valid - 1)  # summer
    j_c = 23  # central row

    ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
    temp_slice = to_np(ds3.variables['temp'][step, :, j_c, :])
    day = ds3.variables['time'][step] / 86400
    ds3.close()

    # build depth coordinates
    H_row = b[j_c, :]
    n_layers = len(sigma)
    n_x = len(x)
    depth_grid = np.zeros((n_layers, n_x))
    for i in range(n_x):
        if H_row[i] > 0:
            depth_grid[:, i] = sigma * H_row[i]

    fig, ax = plt.subplots(figsize=(14, 6))
    temp_plot = np.where(H_row[None, :] > 0, temp_slice, np.nan)
    pcm = ax.pcolormesh(x, depth_grid, temp_plot, cmap='RdYlBu_r',
                        shading='auto', vmin=15, vmax=30)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Depth (m)')
    ax.set_title(f'Temperature Cross-section (j={j_c}, day {day:.0f}, summer)')
    ax.invert_yaxis()  # surface at top
    fig.colorbar(pcm, ax=ax, label='°C')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temp_05_crosssection.png'))
    plt.close(fig)
    print("  -> temp_05_crosssection.png")


# ------------------------------------------------------------------
# 6. Hovmöller Diagram (temperature evolution at center)
# ------------------------------------------------------------------
def plot_hovmoller(n_valid):
    print("[6/6] Hovmöller diagram...")
    j_c, i_c = 23, 26
    if b[j_c, i_c] <= 0:
        j_c, i_c = np.unravel_index(np.argmax(b), b.shape)
    H_center = b[j_c, i_c]

    ds3 = nc.Dataset(os.path.join(CASE, f'{RUN_ID}.3d.nc'))
    n = min(n_valid, 2000)  # limit for memory
    n_layers = len(sigma)
    temp_hov = np.zeros((n_layers, n))
    days = np.zeros(n)
    for k in range(n):
        days[k] = ds3.variables['time'][k] / 86400
        temp_hov[:, k] = to_np(ds3.variables['temp'][k, :, j_c, i_c])
    ds3.close()

    depths = sigma * H_center

    fig, ax = plt.subplots(figsize=(14, 8))
    pcm = ax.pcolormesh(days, depths, temp_hov, cmap='RdYlBu_r',
                        shading='auto', vmin=0, vmax=30)
    ax.set_xlabel('Day')
    ax.set_ylabel('Depth (m)')
    ax.set_title(f'Hovmöller Diagram: Temperature Evolution at Lake Center\n'
                 f'(i={i_c}, j={j_c}, H={H_center:.1f}m)')
    ax.invert_yaxis()
    fig.colorbar(pcm, ax=ax, label='°C')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'temp_06_hovmoller.png'))
    plt.close(fig)
    print("  -> temp_06_hovmoller.png")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("=== Temperature Visualization ===")
    plot_surface_temp_4seasons(n_valid)
    plot_temp_3d_body(n_valid)
    plot_vertical_profiles(n_valid)
    plot_temp_timeseries(n_valid)
    plot_temp_crosssection(n_valid)
    plot_hovmoller(n_valid)
    print(f"\nAll temperature figures saved to {FIG_DIR}")
