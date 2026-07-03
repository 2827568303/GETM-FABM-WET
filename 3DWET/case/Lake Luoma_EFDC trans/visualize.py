"""Lake Luoma (EFDC-translated) hydrodynamic visualization.

Generates 4 figure categories:
  1. 2D spatial maps (bathymetry, elevation, velocity)
  2. 3D lake body (bathymetry surface, velocity field)
  3. Vertical profiles (velocity at selected stations over time)
  4. Time series (water level, velocity at stations)

Usage:
    python visualize.py
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

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
CASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(CASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

RUN_ID = 'LUOMA_EFDC_HYD'


def to_np(data):
    return np.ma.filled(data, np.nan)


def find_valid_steps(path_2d, path_3d):
    """Find the number of valid (non-NaN) time steps."""
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


def load_data():
    """Load model output and bathymetry (memory-efficient for large runs)."""
    bathy_path = os.path.join(CASE_DIR, 'bathymetry.nc')
    ds_b = nc.Dataset(bathy_path)
    bathymetry = to_np(ds_b.variables['bathymetry'][:])
    lonc = to_np(ds_b.variables['lonc'][:])
    latc = to_np(ds_b.variables['latc'][:])
    x = to_np(ds_b.variables['x'][:])
    y = to_np(ds_b.variables['y'][:])
    ds_b.close()

    mask = bathymetry > 0

    # Find valid steps (before any NaN)
    path_2d = os.path.join(CASE_DIR, f'{RUN_ID}.2d.nc')
    path_3d = os.path.join(CASE_DIR, f'{RUN_ID}.3d.nc')
    valid_n = find_valid_steps(path_2d, path_3d)
    print(f"  Valid steps: {valid_n}")

    # 2D output - load only valid steps
    ds2d = nc.Dataset(path_2d)
    time2d = to_np(ds2d.variables['time'][:valid_n]) / 86400.0
    n_t2d = valid_n
    elev = to_np(ds2d.variables['elev'][:valid_n])
    u2d = to_np(ds2d.variables['u'][:valid_n])
    v2d = to_np(ds2d.variables['v'][:valid_n])
    vel2d = np.sqrt(u2d**2 + v2d**2)
    ds2d.close()

    # 3D output - load selectively for memory efficiency
    ds3d = nc.Dataset(path_3d)
    time3d = to_np(ds3d.variables['time'][:valid_n]) / 86400.0
    sigma = to_np(ds3d.variables['sigma'][:])
    n_t3d = valid_n

    # Load 3D velocity snapshots (3: start, mid, end) for spatial maps
    snap_idx = [0, n_t3d // 2, n_t3d - 1]
    uu_snaps = []
    vv_snaps = []
    for idx in snap_idx:
        uu_snaps.append(to_np(ds3d.variables['uu'][idx]))
        vv_snaps.append(to_np(ds3d.variables['vv'][idx]))

    has_temp = 'temp' in ds3d.variables
    temp = None
    if has_temp:
        if n_t3d > 500:
            temp_snaps = []
            for idx in snap_idx:
                temp_snaps.append(to_np(ds3d.variables['temp'][idx]))
            temp = {'snapshots': temp_snaps, 'snap_idx': snap_idx}
        else:
            temp = {'full': to_np(ds3d.variables['temp'][:valid_n])}
    ds3d.close()

    return {
        'bathymetry': bathymetry, 'lonc': lonc, 'latc': latc,
        'x': x, 'y': y, 'mask': mask,
        'time2d': time2d, 'elev': elev, 'u2d': u2d, 'v2d': v2d, 'vel2d': vel2d,
        'time3d': time3d, 'sigma': sigma, 'n_t3d': n_t3d,
        'snap_idx': snap_idx, 'uu_snaps': uu_snaps, 'vv_snaps': vv_snaps,
        'temp': temp, 'path_3d': path_3d,
    }


def get_layer_from_snap(snap, sigma, target):
    idx = np.argmin(np.abs(sigma - target))
    return snap[idx, :, :]


# ------------------------------------------------------------------
# 1. 2D Spatial Maps
# ------------------------------------------------------------------
def plot_2d_maps(d):
    print("\n[1/4] 2D spatial maps...")
    b = d['bathymetry']
    mask = d['mask']
    lon = d['lonc']
    lat = d['latc']
    n_t = len(d['time2d'])

    # --- Bathymetry ---
    fig, ax = plt.subplots(figsize=(10, 8))
    bathy_plot = np.where(mask, b, np.nan)
    pcm = ax.pcolormesh(lon, lat, bathy_plot, shading='auto', cmap='jet')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Lake Luoma Bathymetry (from EFDC, 10-pass smoothed)')
    plt.colorbar(pcm, ax=ax, label='Depth (m)')
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '01_bathymetry_2d.png'))
    plt.close(fig)

    # --- Elevation at 4 time steps (start, 1yr, 2yr, end) ---
    t_indices = [0, n_t // 3, 2 * n_t // 3, n_t - 1]
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for k, ti in enumerate(t_indices):
        ax = axes.flat[k]
        elev_t = np.where(mask, d['elev'][ti], np.nan)
        vmax = max(abs(np.nanmin(elev_t)), abs(np.nanmax(elev_t)), 0.01)
        pcm = ax.pcolormesh(lon, lat, elev_t, shading='auto', cmap='RdYlBu_r',
                            vmin=-vmax, vmax=vmax)
        ax.set_title(f'Water Level (day {d["time2d"][ti]:.0f})')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_aspect('equal')
        plt.colorbar(pcm, ax=ax, label='m')
    fig.suptitle('Water Level Evolution (3-year run)', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '02_elevation_2d.png'))
    plt.close(fig)

    # --- Temperature at mid-time (if available) ---
    if d['temp'] is not None:
        sigma = d['sigma']
        if 'snapshots' in d['temp']:
            mid_snap = d['temp']['snapshots'][1]
            mid_day = d['time3d'][d['snap_idx'][1]]
            temp_surf = get_layer_from_snap(mid_snap, sigma, 0.0)
            temp_bot = get_layer_from_snap(mid_snap, sigma, -1.0)
        else:
            n_t3d = len(d['time3d'])
            ti = n_t3d // 2 if n_t3d > 1 else 0
            mid_day = d['time3d'][ti]
            temp_full = d['temp']['full']
            temp_surf = get_layer_from_snap(temp_full[ti], sigma, 0.0)
            temp_bot = get_layer_from_snap(temp_full[ti], sigma, -1.0)

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for ax, data_t, title in [
            (axes[0], temp_surf, 'Surface Temperature'),
            (axes[1], temp_bot, 'Bottom Temperature'),
        ]:
            plot_data = np.where(mask, data_t, np.nan)
            pcm = ax.pcolormesh(lon, lat, plot_data, shading='auto', cmap='RdYlBu_r')
            ax.set_title(f'{title} (day {mid_day:.0f})')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_aspect('equal')
            plt.colorbar(pcm, ax=ax, label='C')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, '03_temperature_2d.png'))
        plt.close(fig)

    # --- Depth-averaged velocity at 4 time steps ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for k, ti in enumerate(t_indices):
        ax = axes.flat[k]
        vel_t = np.where(mask, d['vel2d'][ti], np.nan)
        pcm = ax.pcolormesh(lon, lat, vel_t, shading='auto', cmap='YlOrRd',
                            vmin=0, vmax=max(np.nanpercentile(d['vel2d'], 95), 0.1))
        step = 4
        u_sub = np.where(mask, d['u2d'][ti], 0)
        v_sub = np.where(mask, d['v2d'][ti], 0)
        ax.quiver(lon[::step, ::step], lat[::step, ::step],
                  u_sub[::step, ::step], v_sub[::step, ::step],
                  color='black', scale=20, width=0.003)
        ax.set_title(f'Depth-Avg Velocity (day {d["time2d"][ti]:.0f})')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_aspect('equal')
        plt.colorbar(pcm, ax=ax, label='m/s')
    fig.suptitle('Depth-Averaged Velocity Evolution', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '04_velocity_2d.png'))
    plt.close(fig)

    print("  -> 01_bathymetry_2d.png, 02_elevation_2d.png, "
          + ("03_temperature_2d.png, " if d['temp'] else "")
          + "04_velocity_2d.png")


# ------------------------------------------------------------------
# 2. 3D Lake Body
# ------------------------------------------------------------------
def plot_3d_body(d):
    print("\n[2/4] 3D lake body...")
    b = d['bathymetry']
    mask = d['mask']
    x = d['x']
    y = d['y']
    X, Y = np.meshgrid(x, y)

    # --- 3D bathymetry surface ---
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    bathy_plot = np.where(mask, b, 0)
    surf = ax.plot_surface(X, Y, -bathy_plot, cmap='terrain',
                           linewidth=0, antialiased=True, alpha=0.9)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Depth (m)')
    ax.set_title('Lake Luoma 3D Bathymetry')
    fig.colorbar(surf, shrink=0.5, aspect=10, label='Depth (m)')
    ax.view_init(elev=35, azim=240)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '05_bathymetry_3d.png'))
    plt.close(fig)

    # --- 3D velocity magnitude at surface (mid-time) ---
    mid_snap_i = 1  # mid snapshot
    uu_mid = d['uu_snaps'][mid_snap_i]
    vv_mid = d['vv_snaps'][mid_snap_i]
    mid_day = d['time3d'][d['snap_idx'][mid_snap_i]]
    sigma = d['sigma']
    u_surf = get_layer_from_snap(uu_mid, sigma, 0.0)
    v_surf = get_layer_from_snap(vv_mid, sigma, 0.0)
    vel_surf = np.sqrt(u_surf**2 + v_surf**2)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    Z = -np.where(mask, b, 0)
    vel_plot = np.where(mask, vel_surf, np.nan)
    norm = Normalize(vmin=0, vmax=np.nanpercentile(vel_plot, 95))
    colors = cm.YlOrRd(norm(np.nan_to_num(vel_plot, nan=0)))
    surf = ax.plot_surface(X, Y, Z, facecolors=colors,
                           linewidth=0, antialiased=True, alpha=0.85)
    mappable = cm.ScalarMappable(norm=norm, cmap='YlOrRd')
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10, label='m/s')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Depth (m)')
    ax.set_title(f'Surface Velocity 3D (day {mid_day:.0f})')
    ax.view_init(elev=35, azim=240)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '06_velocity_3d.png'))
    plt.close(fig)

    print("  -> 05_bathymetry_3d.png, 06_velocity_3d.png")


# ------------------------------------------------------------------
# 3. Vertical Profiles (velocity at stations)
# ------------------------------------------------------------------
def plot_vertical_profiles(d):
    print("\n[3/4] Vertical profiles...")
    b = d['bathymetry']
    mask = d['mask']
    sigma = d['sigma']
    time3d = d['time3d']
    n_t3d = d['n_t3d']

    # Find 4 stations
    water_indices = np.argwhere(mask)
    depths_at_water = b[water_indices[:, 0], water_indices[:, 1]]
    i_deep = water_indices[np.argmax(depths_at_water)]
    i_shallow = water_indices[np.argmin(depths_at_water)]

    stations = [
        ('Deepest', i_deep[1] + 1, i_deep[0] + 1),
        ('Shallowest', i_shallow[1] + 1, i_shallow[0] + 1),
        ('Near ZYH inflow', 10, 20),
        ('Near YHT outflow', 50, 12),
    ]

    # Load station velocity data directly from file
    ds3d = nc.Dataset(d['path_3d'])
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, (name, i, j) in zip(axes.flat, stations):
        ix = i - 1
        jy = j - 1
        if not mask[jy, ix]:
            ax.set_title(f'{name} (land cell)')
            continue

        depth = b[jy, ix]
        z = sigma * depth

        uu_station = to_np(ds3d.variables['uu'][:n_t3d, :, jy, ix])
        vv_station = to_np(ds3d.variables['vv'][:n_t3d, :, jy, ix])
        vel_station = np.sqrt(uu_station**2 + vv_station**2)

        if n_t3d > 1000:
            step = max(1, n_t3d // 500)
            vel_station = vel_station[::step]
            t_days = time3d[::step]
        else:
            t_days = time3d

        T, Z = np.meshgrid(t_days, z, indexing='ij')
        pcm = ax.pcolormesh(T, Z, vel_station, shading='auto', cmap='YlOrRd',
                            vmin=0, vmax=max(np.nanpercentile(vel_station, 95), 0.01))
        ax.invert_yaxis()
        ax.set_xlabel('Day')
        ax.set_ylabel('Depth (m)')
        ax.set_title(f'{name} (depth={depth:.1f}m)')
        plt.colorbar(pcm, ax=ax, label='m/s')

    ds3d.close()
    fig.suptitle('Vertical Velocity Profiles', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '07_vertical_profiles.png'))
    plt.close(fig)
    print("  -> 07_vertical_profiles.png")


# ------------------------------------------------------------------
# 4. Time Series
# ------------------------------------------------------------------
def plot_time_series(d):
    print("\n[4/4] Time series...")
    mask = d['mask']
    b = d['bathymetry']
    time2d = d['time2d']
    elev = d['elev']
    vel2d = d['vel2d']
    u2d = d['u2d']
    v2d = d['v2d']

    water_indices = np.argwhere(mask)
    depths_at_water = b[water_indices[:, 0], water_indices[:, 1]]
    i_deep = water_indices[np.argmax(depths_at_water)]

    stations = [
        ('Deepest point', i_deep[1] + 1, i_deep[0] + 1),
        ('ZYH inflow', 10, 20),
        ('YHT outflow', 50, 12),
        ('Lake center', 26, 23),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

    # --- Water level ---
    ax = axes[0]
    for name, i, j in stations:
        ix = i - 1
        jy = j - 1
        if mask[jy, ix]:
            ax.plot(time2d, elev[:, jy, ix], label=name, alpha=0.8, linewidth=0.8)
    ax.set_ylabel('Water Level (m)')
    ax.set_title('Water Level Time Series')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Velocity magnitude ---
    ax = axes[1]
    for name, i, j in stations:
        ix = i - 1
        jy = j - 1
        if mask[jy, ix]:
            ax.plot(time2d, vel2d[:, jy, ix], label=name, alpha=0.8, linewidth=0.8)
    ax.set_ylabel('Velocity (m/s)')
    ax.set_title('Depth-Averaged Velocity Time Series')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Lake-wide average water level (water balance check) ---
    ax = axes[2]
    mean_elev = np.array([np.nanmean(np.where(mask, e, np.nan)) for e in elev])
    ax.plot(time2d, mean_elev, 'b-', linewidth=1, label='Mean water level')
    ax.set_xlabel('Day')
    ax.set_ylabel('Mean WL (m)')
    ax.set_title('Lake-Wide Mean Water Level (Water Balance)')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '08_time_series.png'))
    plt.close(fig)
    print("  -> 08_time_series.png")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("Loading data...")
    d = load_data()
    print(f"  2D: {len(d['time2d'])} steps, days {d['time2d'][0]:.1f} to {d['time2d'][-1]:.1f}")
    print(f"  3D: {d['n_t3d']} steps, days {d['time3d'][0]:.1f} to {d['time3d'][-1]:.1f}")
    print(f"  Temperature: {'available' if d['temp'] else 'not available (barotropic mode)'}")

    plot_2d_maps(d)
    plot_3d_body(d)
    plot_vertical_profiles(d)
    plot_time_series(d)

    print(f"\nAll figures saved to {FIG_DIR}")
