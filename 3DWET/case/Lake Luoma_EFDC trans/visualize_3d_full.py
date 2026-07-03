"""Comprehensive 3D hydrodynamic visualization for Lake Luoma (EFDC-translated).

Generates a full 3D atlas (no temperature, barotropic mode):
  1. 3D bathymetry multi-view (4 perspectives)
  2. 3D water level surface (4 time snapshots)
  3. 3D surface layer velocity (4 time snapshots)
  4. 3D mid-layer velocity (1 snapshot, multi-view)
  5. 3D bottom layer velocity (1 snapshot)
  6. 3D vertical velocity w (1 snapshot, multi-view)
  7. 3D velocity vector quiver (surface, 1 snapshot)
  8. 3D composite: bathymetry + water level + velocity overlay

Memory-efficient: loads only snapshot time steps from the 7.8GB 3D file.
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

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(CASE_DIR, 'figures_3d')
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 110

RUN_ID = 'LUOMA_EFDC_HYD'


def to_np(data):
    return np.ma.filled(data, np.nan)


def find_valid_steps(path_2d):
    """Binary search for first NaN step in 2D elev field."""
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
    ds = nc.Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'))
    b = to_np(ds.variables['bathymetry'][:])
    x = to_np(ds.variables['x'][:])
    y = to_np(ds.variables['y'][:])
    ds.close()
    mask = b > 0
    return b, x, y, mask


def get_sigma():
    ds = nc.Dataset(os.path.join(CASE_DIR, f'{RUN_ID}.3d.nc'))
    sigma = to_np(ds.variables['sigma'][:])
    ds.close()
    return sigma


def get_layer_index(sigma, target):
    return int(np.argmin(np.abs(sigma - target)))


def load_2d_snapshot(idx):
    ds = nc.Dataset(os.path.join(CASE_DIR, f'{RUN_ID}.2d.nc'))
    elev = to_np(ds.variables['elev'][idx])
    u = to_np(ds.variables['u'][idx])
    v = to_np(ds.variables['v'][idx])
    t = to_np(ds.variables['time'][idx]) / 86400.0
    ds.close()
    return elev, u, v, t


def load_3d_snapshot(idx, vars=('uu', 'vv', 'w')):
    ds = nc.Dataset(os.path.join(CASE_DIR, f'{RUN_ID}.3d.nc'))
    out = {'t': to_np(ds.variables['time'][idx]) / 86400.0}
    for v in vars:
        if v in ds.variables:
            out[v] = to_np(ds.variables[v][idx])
    ds.close()
    return out


# ------------------------------------------------------------------
# 1. 3D Bathymetry Multi-View
# ------------------------------------------------------------------
def plot_bathymetry_3d_multiview(b, x, y, mask):
    print("[1/8] 3D bathymetry multi-view...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)

    views = [(30, 45), (45, 135), (60, 225), (25, 315)]
    fig = plt.figure(figsize=(16, 12))
    for k, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='terrain', linewidth=0,
                               antialiased=True, alpha=0.9)
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
        ax.set_title(f'view elev={elev} azim={azim}')
        ax.view_init(elev=elev, azim=azim)
        if k == 0:
            fig.colorbar(surf, shrink=0.5, aspect=10, label='Depth (m)')
    fig.suptitle('Lake Luoma 3D Bathymetry (10-pass smoothed, multi-view)', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_01_bathymetry_multiview.png'))
    plt.close(fig)
    print("  -> 3d_01_bathymetry_multiview.png")


# ------------------------------------------------------------------
# 2. 3D Water Level Surface (4 time snapshots)
# ------------------------------------------------------------------
def plot_water_level_3d(b, x, y, mask, n_valid):
    print("[2/8] 3D water level surface...")
    X, Y = np.meshgrid(x, y)
    snap_idx = [0, n_valid // 4, n_valid // 2, n_valid - 1]

    fig = plt.figure(figsize=(16, 12))
    for k, idx in enumerate(snap_idx):
        elev_s, _, _, day = load_2d_snapshot(idx)
        Z = np.where(mask, elev_s, np.nan)
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        # use a diverging colormap centered at 0
        vmax = max(abs(np.nanmin(Z)), abs(np.nanmax(Z)), 0.01)
        norm = Normalize(vmin=-vmax, vmax=vmax)
        colors = cm.RdYlBu_r(norm(np.nan_to_num(Z, nan=0)))
        surf = ax.plot_surface(X, Y, Z, facecolors=colors,
                               linewidth=0, antialiased=True, alpha=0.9)
        mappable = cm.ScalarMappable(norm=norm, cmap='RdYlBu_r')
        mappable.set_array([])
        fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10, label='m')
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('WL (m)')
        ax.set_title(f'day {day:.1f}')
        ax.view_init(elev=35, azim=240)
    fig.suptitle('3D Water Level Surface Evolution', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_02_water_level_surface.png'))
    plt.close(fig)
    print("  -> 3d_02_water_level_surface.png")


# ------------------------------------------------------------------
# 3. 3D Surface Layer Velocity (4 time snapshots)
# ------------------------------------------------------------------
def plot_surface_velocity_3d(b, x, y, mask, sigma, n_valid):
    print("[3/8] 3D surface velocity...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)
    snap_idx = [0, n_valid // 4, n_valid // 2, n_valid - 1]
    surf_i = get_layer_index(sigma, 0.0)

    fig = plt.figure(figsize=(16, 12))
    for k, idx in enumerate(snap_idx):
        snap = load_3d_snapshot(idx, vars=('uu', 'vv'))
        u_s = snap['uu'][surf_i]
        v_s = snap['vv'][surf_i]
        vel = np.sqrt(u_s**2 + v_s**2)
        vel_plot = np.where(mask, vel, np.nan)
        day = snap['t']
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        vmax = max(np.nanpercentile(vel_plot, 95), 0.01)
        norm = Normalize(vmin=0, vmax=vmax)
        colors = cm.YlOrRd(norm(np.nan_to_num(vel_plot, nan=0)))
        ax.plot_surface(X, Y, Z, facecolors=colors,
                        linewidth=0, antialiased=True, alpha=0.85)
        mappable = cm.ScalarMappable(norm=norm, cmap='YlOrRd')
        mappable.set_array([])
        fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10, label='m/s')
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
        ax.set_title(f'surface layer, day {day:.1f}')
        ax.view_init(elev=35, azim=240)
    fig.suptitle('3D Surface Layer Velocity (sigma=0)', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_03_surface_velocity.png'))
    plt.close(fig)
    print("  -> 3d_03_surface_velocity.png")


# ------------------------------------------------------------------
# 4. 3D Mid-Layer Velocity (multi-view)
# ------------------------------------------------------------------
def plot_midlayer_velocity_3d(b, x, y, mask, sigma, n_valid):
    print("[4/8] 3D mid-layer velocity...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)
    mid_i = get_layer_index(sigma, -0.5)
    snap = load_3d_snapshot(n_valid // 2, vars=('uu', 'vv'))
    u_m = snap['uu'][mid_i]
    v_m = snap['vv'][mid_i]
    vel = np.sqrt(u_m**2 + v_m**2)
    vel_plot = np.where(mask, vel, np.nan)
    day = snap['t']

    views = [(35, 120), (50, 210), (25, 300), (60, 60)]
    fig = plt.figure(figsize=(16, 12))
    vmax = max(np.nanpercentile(vel_plot, 95), 0.01)
    norm = Normalize(vmin=0, vmax=vmax)
    colors = cm.YlOrRd(norm(np.nan_to_num(vel_plot, nan=0)))
    for k, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        ax.plot_surface(X, Y, Z, facecolors=colors,
                        linewidth=0, antialiased=True, alpha=0.85)
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
        ax.set_title(f'elev={elev} azim={azim}')
        ax.view_init(elev=elev, azim=azim)
    mappable = cm.ScalarMappable(norm=norm, cmap='YlOrRd')
    mappable.set_array([])
    fig.colorbar(mappable, ax=fig.get_axes(), shrink=0.4, aspect=15, label='m/s')
    fig.suptitle(f'3D Mid-Layer Velocity (sigma=-0.5, day {day:.1f})', fontsize=14)
    fig.savefig(os.path.join(FIG_DIR, '3d_04_midlayer_velocity.png'), bbox_inches='tight')
    plt.close(fig)
    print("  -> 3d_04_midlayer_velocity.png")


# ------------------------------------------------------------------
# 5. 3D Bottom Layer Velocity
# ------------------------------------------------------------------
def plot_bottom_velocity_3d(b, x, y, mask, sigma, n_valid):
    print("[5/8] 3D bottom velocity...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)
    bot_i = get_layer_index(sigma, -1.0)
    snap = load_3d_snapshot(n_valid // 2, vars=('uu', 'vv'))
    u_b = snap['uu'][bot_i]
    v_b = snap['vv'][bot_i]
    vel = np.sqrt(u_b**2 + v_b**2)
    vel_plot = np.where(mask, vel, np.nan)
    day = snap['t']

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    vmax = max(np.nanpercentile(vel_plot, 95), 0.01)
    norm = Normalize(vmin=0, vmax=vmax)
    colors = cm.YlOrRd(norm(np.nan_to_num(vel_plot, nan=0)))
    ax.plot_surface(X, Y, Z, facecolors=colors,
                    linewidth=0, antialiased=True, alpha=0.85)
    mappable = cm.ScalarMappable(norm=norm, cmap='YlOrRd')
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.5, aspect=10, label='m/s')
    ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
    ax.set_title(f'3D Bottom Layer Velocity (sigma=-1.0, day {day:.1f})')
    ax.view_init(elev=40, azim=240)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_05_bottom_velocity.png'))
    plt.close(fig)
    print("  -> 3d_05_bottom_velocity.png")


# ------------------------------------------------------------------
# 6. 3D Vertical Velocity w (multi-view)
# ------------------------------------------------------------------
def plot_vertical_w_3d(b, x, y, mask, sigma, n_valid):
    print("[6/8] 3D vertical velocity w...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)
    mid_i = get_layer_index(sigma, -0.5)
    snap = load_3d_snapshot(n_valid // 2, vars=('w',))
    if 'w' not in snap:
        print("  -> skipped (no w variable)")
        return
    w = snap['w'][mid_i]
    w_plot = np.where(mask, w, np.nan)
    day = snap['t']

    views = [(35, 120), (50, 210), (25, 300), (60, 60)]
    fig = plt.figure(figsize=(16, 12))
    vmax = max(abs(np.nanmin(w_plot)), abs(np.nanmax(w_plot)), 1e-6)
    norm = Normalize(vmin=-vmax, vmax=vmax)
    colors = cm.RdBu_r(norm(np.nan_to_num(w_plot, nan=0)))
    for k, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, k + 1, projection='3d')
        ax.plot_surface(X, Y, Z, facecolors=colors,
                        linewidth=0, antialiased=True, alpha=0.85)
        ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
        ax.set_title(f'elev={elev} azim={azim}')
        ax.view_init(elev=elev, azim=azim)
    mappable = cm.ScalarMappable(norm=norm, cmap='RdBu_r')
    mappable.set_array([])
    fig.colorbar(mappable, ax=fig.get_axes(), shrink=0.4, aspect=15, label='m/s')
    fig.suptitle(f'3D Vertical Velocity w (mid-layer, day {day:.1f})', fontsize=14)
    fig.savefig(os.path.join(FIG_DIR, '3d_06_vertical_w.png'), bbox_inches='tight')
    plt.close(fig)
    print("  -> 3d_06_vertical_w.png")


# ------------------------------------------------------------------
# 7. 3D Velocity Vector Quiver (surface)
# ------------------------------------------------------------------
def plot_velocity_quiver_3d(b, x, y, mask, sigma, n_valid):
    print("[7/8] 3D velocity quiver...")
    X, Y = np.meshgrid(x, y)
    Z = -np.where(mask, b, 0)
    surf_i = get_layer_index(sigma, 0.0)
    snap = load_3d_snapshot(n_valid // 2, vars=('uu', 'vv'))
    u_s = snap['uu'][surf_i]
    v_s = snap['vv'][surf_i]
    day = snap['t']

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    # bathymetry as transparent surface
    ax.plot_surface(X, Y, Z, cmap='terrain', linewidth=0,
                    antialiased=True, alpha=0.35)
    # quiver at surface (z=0 plane)
    step = 3
    xs = x[::step]
    ys = y[::step]
    Xs, Ys = np.meshgrid(xs, ys)
    U = np.where(mask[::step, ::step], u_s[::step, ::step], 0)
    V = np.where(mask[::step, ::step], v_s[::step, ::step], 0)
    Zs = np.zeros_like(U)
    ax.quiver(Xs, Ys, Zs, U, V, np.zeros_like(U),
              color='red', length=400, normalize=False, alpha=0.8)
    ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Depth (m)')
    ax.set_title(f'3D Surface Velocity Vectors (day {day:.1f})')
    ax.view_init(elev=40, azim=240)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_07_velocity_quiver.png'))
    plt.close(fig)
    print("  -> 3d_07_velocity_quiver.png")


# ------------------------------------------------------------------
# 8. 3D Composite: bathymetry + water level + velocity overlay
# ------------------------------------------------------------------
def plot_composite_3d(b, x, y, mask, sigma, n_valid):
    print("[8/8] 3D composite...")
    X, Y = np.meshgrid(x, y)
    Z_bathy = -np.where(mask, b, 0)
    surf_i = get_layer_index(sigma, 0.0)

    snap3d = load_3d_snapshot(n_valid // 2, vars=('uu', 'vv'))
    elev_s, u2d, v2d, day = load_2d_snapshot(n_valid // 2)
    u_s = snap3d['uu'][surf_i]
    v_s = snap3d['vv'][surf_i]
    vel = np.sqrt(u_s**2 + v_s**2)

    Z_wl = np.where(mask, elev_s, np.nan)
    vel_plot = np.where(mask, vel, np.nan)

    fig = plt.figure(figsize=(16, 11))
    # Left: bathymetry + water level surface
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax1.plot_surface(X, Y, Z_bathy, cmap='terrain', linewidth=0,
                     antialiased=True, alpha=0.6)
    vmax = max(abs(np.nanmin(Z_wl)), abs(np.nanmax(Z_wl)), 0.01)
    norm_wl = Normalize(vmin=-vmax, vmax=vmax)
    colors_wl = cm.RdYlBu_r(norm_wl(np.nan_to_num(Z_wl, nan=0)))
    ax1.plot_surface(X, Y, Z_wl, facecolors=colors_wl,
                     linewidth=0, antialiased=True, alpha=0.7)
    m1 = cm.ScalarMappable(norm=norm_wl, cmap='RdYlBu_r'); m1.set_array([])
    fig.colorbar(m1, ax=ax1, shrink=0.5, aspect=10, label='WL (m)')
    ax1.set_xlabel('X (m)'); ax1.set_ylabel('Y (m)'); ax1.set_zlabel('Z (m)')
    ax1.set_title(f'Bathymetry + Water Level (day {day:.1f})')
    ax1.view_init(elev=40, azim=240)

    # Right: bathymetry colored by surface velocity + quiver
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    vmax_v = max(np.nanpercentile(vel_plot, 95), 0.01)
    norm_v = Normalize(vmin=0, vmax=vmax_v)
    colors_v = cm.YlOrRd(norm_v(np.nan_to_num(vel_plot, nan=0)))
    ax2.plot_surface(X, Y, Z_bathy, facecolors=colors_v,
                     linewidth=0, antialiased=True, alpha=0.85)
    m2 = cm.ScalarMappable(norm=norm_v, cmap='YlOrRd'); m2.set_array([])
    fig.colorbar(m2, ax=ax2, shrink=0.5, aspect=10, label='vel (m/s)')
    step = 3
    Xs, Ys = np.meshgrid(x[::step], y[::step])
    U = np.where(mask[::step, ::step], u_s[::step, ::step], 0)
    V = np.where(mask[::step, ::step], v_s[::step, ::step], 0)
    Zs = np.zeros_like(U)
    ax2.quiver(Xs, Ys, Zs, U, V, np.zeros_like(U),
               color='black', length=400, normalize=False, alpha=0.7)
    ax2.set_xlabel('X (m)'); ax2.set_ylabel('Y (m)'); ax2.set_zlabel('Depth (m)')
    ax2.set_title(f'Bathymetry + Surface Velocity (day {day:.1f})')
    ax2.view_init(elev=40, azim=240)

    fig.suptitle('3D Composite: Hydrodynamic State', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, '3d_08_composite.png'))
    plt.close(fig)
    print("  -> 3d_08_composite.png")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
if __name__ == '__main__':
    print("=== Comprehensive 3D Hydrodynamic Visualization ===")
    print("Loading bathymetry and grid...")
    b, x, y, mask = load_bathy_and_grid()
    sigma = get_sigma()
    print(f"  grid: {len(y)} x {len(x)}, water cells: {mask.sum()}")
    print(f"  sigma levels: {sigma}")

    path_2d = os.path.join(CASE_DIR, f'{RUN_ID}.2d.nc')
    n_valid = find_valid_steps(path_2d)
    print(f"  valid steps: {n_valid} (~{n_valid/86400*30:.1f} days at step_2d=288)")

    plot_bathymetry_3d_multiview(b, x, y, mask)
    plot_water_level_3d(b, x, y, mask, n_valid)
    plot_surface_velocity_3d(b, x, y, mask, sigma, n_valid)
    plot_midlayer_velocity_3d(b, x, y, mask, sigma, n_valid)
    plot_bottom_velocity_3d(b, x, y, mask, sigma, n_valid)
    plot_vertical_w_3d(b, x, y, mask, sigma, n_valid)
    plot_velocity_quiver_3d(b, x, y, mask, sigma, n_valid)
    plot_composite_3d(b, x, y, mask, sigma, n_valid)

    print(f"\nAll 3D figures saved to {FIG_DIR}")
