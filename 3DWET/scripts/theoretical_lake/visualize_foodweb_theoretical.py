"""Visualization of Theoretical Lake GETM-FABM-WET food web model output.

Generates 10 figures (FW01-FW10) showing spatial and temporal distributions
of phytoplankton, zooplankton, fish, macrophytes, benthos, organic matter,
and sediment nutrients.

Run with: python3 visualize_foodweb_theoretical.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

import netCDF4 as nc
import numpy as np
import os
from matplotlib import gridspec

# ============================================================
# Path setup (relative to this script via __file__)
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'case', 'Theoretical lake'))
FIG_DIR = os.path.join(CASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# Lake constants
# ============================================================
NX, NY = 5, 7
# River positions (0-indexed: x, y)
RIVERS = {
    'INFL1(NE)': (4, 0),
    'INFL2(NW)': (0, 0),
    'OUTFL(SW)': (0, 6),
}
# SE bay mask (macrophyte region): i>=2, j>=4 (0-indexed)
SE_BAY_MASK = np.zeros((NY, NX), dtype=bool)
SE_BAY_MASK[4:, 2:] = True


# ============================================================
# Helper functions
# ============================================================
def to_np(data):
    """Convert masked array to regular numpy array with NaN."""
    return np.ma.filled(data, np.nan)


def depth_avg(var_3d, sigma, depth_2d):
    """Depth-average: var_3d is (time, sigma, y, x), sigma is 1D, depth_2d is (y, x)."""
    nz = var_3d.shape[1]
    sigma_sorted = np.sort(sigma)[:nz]
    dz = np.zeros((nz, depth_2d.shape[0], depth_2d.shape[1]))
    for k in range(nz):
        if k == 0:
            dz[k] = depth_2d * (sigma_sorted[k + 1] - sigma_sorted[k])
        elif k == nz - 1:
            dz[k] = depth_2d * (sigma_sorted[k] - sigma_sorted[k - 1])
        else:
            dz[k] = depth_2d * 0.5 * (sigma_sorted[k + 1] - sigma_sorted[k - 1])
    total_dz = np.nansum(dz, axis=0)
    total_dz[total_dz == 0] = np.nan
    avg = np.nansum(var_3d * dz[np.newaxis, :, :, :], axis=1) / total_dz[np.newaxis, :, :]
    return avg


def mark_rivers(ax):
    """Mark river positions with red arrows pointing into the lake."""
    for name, (x, y) in RIVERS.items():
        if y == 0:
            text_x, text_y = x, -0.9
        else:
            text_x, text_y = x, NY - 0.1
        ax.annotate(name, xy=(x, y), xytext=(text_x, text_y),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    fontsize=7, color='red', ha='center', va='center')


def mark_se_bay(ax):
    """Mark SE bay region with a dashed green rectangle."""
    rect = plt.Rectangle((1.5, 3.5), 3, 3, linewidth=2, edgecolor='green',
                         facecolor='none', linestyle='--')
    ax.add_patch(rect)
    ax.text(3, 4.2, 'SE湾', color='green', fontsize=8, ha='center', va='center',
            fontweight='bold')


def setup_ax(ax, title):
    """Common axis setup for spatial plots."""
    ax.set_title(title, fontsize=11)
    ax.set_xlabel('x (网格)')
    ax.set_ylabel('y (网格)')
    ax.set_aspect('equal')
    ax.set_xlim(-0.7, NX - 0.3)
    ax.set_ylim(-1.2, NY - 0.3)


def save_fig(fig, name):
    """Save figure to FIG_DIR with FW_ prefix-less name (already starts with FW)."""
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {name}")


# ============================================================
# Data loading
# ============================================================
def load_data():
    """Load all data from NetCDF files."""
    data = {}

    # Bathymetry
    dsb = nc.Dataset(os.path.join(CASE_DIR, 'bathymetry.nc'))
    data['bathymetry'] = to_np(dsb.variables['bathymetry'][:])
    dsb.close()

    # 3D hydrodynamic (for sigma, lonc, latc)
    ds3 = nc.Dataset(os.path.join(CASE_DIR, 'THEORETICAL_LAKE.3d.nc'))
    data['sigma'] = to_np(ds3.variables['sigma'][:])
    ds3.close()

    # FABM output
    ds = nc.Dataset(os.path.join(CASE_DIR, 'output.nc'))
    data['n_time'] = len(ds.variables['time'][:])
    data['time_days'] = np.arange(data['n_time'])

    # 3D variables (time, sigma, y, x)
    vars_3d = [
        'cyanobacteria_sDW', 'diatoms_sDW', 'greens_sDW',
        'cladocerans_sD', 'copepods_sD',
        'JuFish_sD', 'AdFish_sD', 'PiscFish_sD',
        'POM_sDW', 'DOM_sDW',
        'abiotic_water_sNH4W', 'abiotic_water_sNO3W',
        'abiotic_water_sPO4W', 'abiotic_water_sO2W',
    ]
    for v in vars_3d:
        if v in ds.variables:
            data[v] = to_np(ds.variables[v][:])

    # 2D benthic variables (time, y, x)
    vars_2d = [
        'macrophytes_sD', 'zoobenthos_sD',
        'abiotic_sediment_sNH4S', 'abiotic_sediment_sNO3S',
        'abiotic_sediment_sPO4S',
        'POM_sDS', 'DOM_sDS',
        'cyanobacteria_sDS', 'diatoms_sDS', 'greens_sDS',
    ]
    for v in vars_2d:
        if v in ds.variables:
            data[v] = to_np(ds.variables[v][:])

    ds.close()
    return data


def get_surface_layer(data, varname, t):
    """Get surface layer of 3D variable at time t (last sigma index = surface)."""
    var = data[varname]
    nz = var.shape[1]
    return var[t, nz - 1, :, :]


def get_depth_avg_ts(data, varname):
    """Compute depth-averaged time series for a 3D variable."""
    return depth_avg(data[varname], data['sigma'], data['bathymetry'])


# ============================================================
# FW01: Phytoplankton 3D surface distribution
# ============================================================
def fig01_phytoplankton_3d(data):
    t = 180
    vars_plot = [
        ('cyanobacteria_sDW', '蓝藻 (gDW/m3)'),
        ('diatoms_sDW', '硅藻 (gDW/m3)'),
        ('greens_sDW', '绿藻 (gDW/m3)'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (vname, label) in zip(axes, vars_plot):
        field = get_surface_layer(data, vname, t)
        X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
        pc = ax.pcolormesh(X, Y, field, cmap='YlGn', shading='auto')
        cb = plt.colorbar(pc, ax=ax, shrink=0.8)
        cb.set_label(label)
        mark_rivers(ax)
        setup_ax(ax, f'{label.split(" ")[0]} 表层分布')
    fig.suptitle(f'浮游植物表层分布 (t={t}天)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW01_phytoplankton_3d.png')


# ============================================================
# FW02: Phytoplankton seasonal evolution
# ============================================================
def fig02_phytoplankton_seasonal(data):
    seasons = [(0, '冬季 (t=0)'), (90, '春季 (t=90)'), (180, '夏季 (t=180)'), (270, '秋季 (t=270)')]
    vars_plot = [
        ('cyanobacteria_sDW', '蓝藻'),
        ('diatoms_sDW', '硅藻'),
        ('greens_sDW', '绿藻'),
    ]
    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
    for row, (vname, label) in enumerate(vars_plot):
        # Compute shared color range across seasons for this row
        all_data = []
        for t, _ in seasons:
            all_data.append(get_surface_layer(data, vname, t))
        vmin = min(np.nanmin(d) for d in all_data)
        vmax = max(np.nanmax(d) for d in all_data)
        if vmax <= vmin:
            vmax = vmin + 1e-6
        for col, (t, season_label) in enumerate(seasons):
            ax = axes[row, col]
            field = all_data[col]
            pc = ax.pcolormesh(X, Y, field, cmap='YlGn', shading='auto',
                               vmin=vmin, vmax=vmax)
            mark_rivers(ax)
            setup_ax(ax, f'{label} {season_label}')
            if col == 3:
                cb = plt.colorbar(pc, ax=axes[row, :], shrink=0.8, pad=0.02)
                cb.set_label('gDW/m3')
    fig.suptitle('浮游植物表层季节变化', fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save_fig(fig, 'FW02_phytoplankton_seasonal.png')


# ============================================================
# FW03: Zooplankton depth-averaged
# ============================================================
def fig03_zooplankton_3d(data):
    t = 180
    vars_plot = [
        ('cladocerans_sD', '枝角类 (gDW/m3)'),
        ('copepods_sD', '桡足类 (gDW/m3)'),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
    for ax, (vname, label) in zip(axes, vars_plot):
        da = get_depth_avg_ts(data, vname)
        field = da[t, :, :]
        pc = ax.pcolormesh(X, Y, field, cmap='YlGnBu', shading='auto')
        cb = plt.colorbar(pc, ax=ax, shrink=0.8)
        cb.set_label(label)
        mark_rivers(ax)
        setup_ax(ax, f'{label.split(" ")[0]} 垂向平均')
    fig.suptitle(f'浮游动物垂向平均分布 (t={t}天)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW03_zooplankton_3d.png')


# ============================================================
# FW04: Fish surface distribution
# ============================================================
def fig04_fish_3d(data):
    t = 180
    vars_plot = [
        ('JuFish_sD', '幼鱼 (gDW/m3)'),
        ('AdFish_sD', '成鱼 (gDW/m3)'),
        ('PiscFish_sD', '食鱼性鱼 (gDW/m3)'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
    for ax, (vname, label) in zip(axes, vars_plot):
        field = get_surface_layer(data, vname, t)
        pc = ax.pcolormesh(X, Y, field, cmap='YlOrRd', shading='auto')
        cb = plt.colorbar(pc, ax=ax, shrink=0.8)
        cb.set_label(label)
        mark_rivers(ax)
        setup_ax(ax, f'{label.split(" ")[0]} 表层分布')
    fig.suptitle(f'鱼类表层分布 (t={t}天)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW04_fish_3d.png')


# ============================================================
# FW05: Fish vertical profile (depth vs time heatmap)
# ============================================================
def fig05_fish_vertical(data):
    vars_plot = [
        ('JuFish_sD', '幼鱼'),
        ('AdFish_sD', '成鱼'),
        ('PiscFish_sD', '食鱼性鱼'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    sigma = data['sigma']
    nz = data[vars_plot[0][0]].shape[1]
    sigma_layers = np.sort(sigma)[:nz]
    mean_depth = float(np.nanmean(data['bathymetry']))
    z = -sigma_layers * mean_depth  # positive downward

    for ax, (vname, label) in zip(axes, vars_plot):
        var = data[vname]
        # Spatial mean over x, y for each time and layer
        profile = np.nanmean(np.nanmean(var, axis=3), axis=2)  # (time, layer)
        T, Zg = np.meshgrid(data['time_days'], z)
        pc = ax.pcolormesh(T, Zg, profile.T, cmap='YlOrRd', shading='auto')
        cb = plt.colorbar(pc, ax=ax, shrink=0.8)
        cb.set_label('gDW/m3')
        ax.invert_yaxis()  # surface (z~0) at top
        ax.set_xlabel('时间 (天)')
        ax.set_ylabel('深度 (m)')
        ax.set_title(f'{label} 垂向剖面')
    fig.suptitle('鱼类垂向剖面 (深度-时间, 空间平均)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW05_fish_vertical.png')


# ============================================================
# FW06: Macrophytes and benthos
# ============================================================
def fig06_macrophytes_benthic(data):
    times = [(0, 't=0'), (90, 't=90'), (180, 't=180'), (270, 't=270')]
    fig = plt.figure(figsize=(16, 7))
    gs0 = gridspec.GridSpec(1, 2, width_ratios=[1.3, 1], figure=fig)

    # Left: 2x2 macrophytes spatial maps
    gs_left = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs0[0], hspace=0.4, wspace=0.3)
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
    all_data = [data['macrophytes_sD'][t, :, :] for t, _ in times]
    vmin = min(np.nanmin(d) for d in all_data)
    vmax = max(np.nanmax(d) for d in all_data)
    if vmax <= vmin:
        vmax = vmin + 1e-6
    for idx, (t, label) in enumerate(times):
        ax = fig.add_subplot(gs_left[idx])
        field = data['macrophytes_sD'][t, :, :]
        pc = ax.pcolormesh(X, Y, field, cmap='YlGn', shading='auto', vmin=vmin, vmax=vmax)
        mark_rivers(ax)
        mark_se_bay(ax)
        setup_ax(ax, f'大型水草 {label}')
    cb = plt.colorbar(pc, ax=fig.get_axes(), shrink=0.6, pad=0.02, location='left')
    cb.set_label('gDW/m2')

    # Right: time series of macrophytes and zoobenthos spatial means
    ax_ts = fig.add_subplot(gs0[1])
    macro_mean = np.nanmean(np.nanmean(data['macrophytes_sD'], axis=2), axis=1)
    bent_mean = np.nanmean(np.nanmean(data['zoobenthos_sD'], axis=2), axis=1)
    ax_ts.plot(data['time_days'], macro_mean, 'g-', linewidth=2, label='大型水草')
    ax_ts.plot(data['time_days'], bent_mean, 'b-', linewidth=2, label='底栖动物')
    ax_ts.set_xlabel('时间 (天)')
    ax_ts.set_ylabel('生物量 (gDW/m2)')
    ax_ts.set_title('大型水草与底栖动物时间序列 (空间平均)')
    ax_ts.legend(loc='best')
    ax_ts.grid(True, alpha=0.3)

    fig.suptitle('大型水草与底栖生物分布', fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_fig(fig, 'FW06_macrophytes_benthic.png')


# ============================================================
# FW07: Organic matter (water + sediment)
# ============================================================
def fig07_organic_matter(data):
    t = 180
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))

    # POM_sDW depth-avg
    ax = axes[0, 0]
    da = get_depth_avg_ts(data, 'POM_sDW')
    field = da[t, :, :]
    pc = ax.pcolormesh(X, Y, field, cmap='YlOrBr', shading='auto')
    plt.colorbar(pc, ax=ax, shrink=0.8, label='gDW/m3')
    mark_rivers(ax)
    setup_ax(ax, '颗粒有机物 (水体, 垂向平均)')

    # DOM_sDW depth-avg
    ax = axes[0, 1]
    da = get_depth_avg_ts(data, 'DOM_sDW')
    field = da[t, :, :]
    pc = ax.pcolormesh(X, Y, field, cmap='YlOrBr', shading='auto')
    plt.colorbar(pc, ax=ax, shrink=0.8, label='gDW/m3')
    mark_rivers(ax)
    setup_ax(ax, '溶解有机物 (水体, 垂向平均)')

    # POM_sDS benthic
    ax = axes[1, 0]
    field = data['POM_sDS'][t, :, :]
    pc = ax.pcolormesh(X, Y, field, cmap='YlOrBr', shading='auto')
    plt.colorbar(pc, ax=ax, shrink=0.8, label='gDW/m2')
    mark_rivers(ax)
    mark_se_bay(ax)
    setup_ax(ax, '颗粒有机物 (沉积物)')

    # DOM_sDS benthic
    ax = axes[1, 1]
    field = data['DOM_sDS'][t, :, :]
    pc = ax.pcolormesh(X, Y, field, cmap='YlOrBr', shading='auto')
    plt.colorbar(pc, ax=ax, shrink=0.8, label='gDW/m2')
    mark_rivers(ax)
    mark_se_bay(ax)
    setup_ax(ax, '溶解有机物 (沉积物)')

    fig.suptitle(f'有机物分布 (t={t}天)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW07_organic_matter.png')


# ============================================================
# FW08: Sediment nutrients
# ============================================================
def fig08_sediment_nutrients(data):
    t = 180
    vars_plot = [
        ('abiotic_sediment_sNH4S', '沉积物 NH4 (g/m2)'),
        ('abiotic_sediment_sNO3S', '沉积物 NO3 (g/m2)'),
        ('abiotic_sediment_sPO4S', '沉积物 PO4 (g/m2)'),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))
    for ax, (vname, label) in zip(axes, vars_plot):
        field = data[vname][t, :, :]
        pc = ax.pcolormesh(X, Y, field, cmap='BuPu', shading='auto')
        plt.colorbar(pc, ax=ax, shrink=0.8, label=label)
        mark_rivers(ax)
        mark_se_bay(ax)
        setup_ax(ax, label)
    fig.suptitle(f'沉积物营养盐分布 (t={t}天)', fontsize=13, fontweight='bold')
    fig.tight_layout()
    save_fig(fig, 'FW08_sediment_nutrients.png')


# ============================================================
# FW09: Trophic levels time series
# ============================================================
def fig09_trophic_levels_timeseries(data):
    # Phytoplankton: sum of 3 groups, depth-avg, spatial mean
    phyto = (get_depth_avg_ts(data, 'cyanobacteria_sDW') +
             get_depth_avg_ts(data, 'diatoms_sDW') +
             get_depth_avg_ts(data, 'greens_sDW'))
    phyto_ts = np.nanmean(np.nanmean(phyto, axis=2), axis=1)

    # Zooplankton: sum of 2 groups, depth-avg, spatial mean
    zoo = (get_depth_avg_ts(data, 'cladocerans_sD') +
           get_depth_avg_ts(data, 'copepods_sD'))
    zoo_ts = np.nanmean(np.nanmean(zoo, axis=2), axis=1)

    # Fish: sum of 3 types, depth-avg, spatial mean
    fish = (get_depth_avg_ts(data, 'JuFish_sD') +
            get_depth_avg_ts(data, 'AdFish_sD') +
            get_depth_avg_ts(data, 'PiscFish_sD'))
    fish_ts = np.nanmean(np.nanmean(fish, axis=2), axis=1)

    # Macrophytes: spatial mean (2D)
    macro_ts = np.nanmean(np.nanmean(data['macrophytes_sD'], axis=2), axis=1)

    # Benthos: spatial mean (2D)
    bent_ts = np.nanmean(np.nanmean(data['zoobenthos_sD'], axis=2), axis=1)

    fig, ax = plt.subplots(figsize=(12, 7))
    t = data['time_days']
    ax.semilogy(t, phyto_ts + 1e-10, 'g-', linewidth=2, label='浮游植物 (gDW/m3)')
    ax.semilogy(t, zoo_ts + 1e-10, 'b-', linewidth=2, label='浮游动物 (gDW/m3)')
    ax.semilogy(t, fish_ts + 1e-10, 'r-', linewidth=2, label='鱼类 (gDW/m3)')
    ax.semilogy(t, macro_ts + 1e-10, 'm-', linewidth=2, label='大型水草 (gDW/m2)')
    ax.semilogy(t, bent_ts + 1e-10, 'c-', linewidth=2, label='底栖动物 (gDW/m2)')
    ax.set_xlabel('时间 (天)', fontsize=12)
    ax.set_ylabel('生物量 (对数尺度)', fontsize=12)
    ax.set_title('各营养级生物量时间序列 (空间平均, 对数Y轴)', fontsize=13, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, which='both')
    fig.tight_layout()
    save_fig(fig, 'FW09_trophic_levels_timeseries.png')


# ============================================================
# FW10: Spatial evolution
# ============================================================
def fig10_spatial_evolution(data):
    times = [(0, 't=0'), (90, 't=90'), (180, 't=180'), (270, 't=270')]
    fig, axes = plt.subplots(4, 3, figsize=(15, 16))
    X, Y = np.meshgrid(np.arange(NX), np.arange(NY))

    # Precompute depth-avg for AdFish
    adfish_da = get_depth_avg_ts(data, 'AdFish_sD')

    # Column ranges (shared across rows)
    diatoms_all = [get_surface_layer(data, 'diatoms_sDW', t) for t, _ in times]
    adfish_all = [adfish_da[t, :, :] for t, _ in times]
    macro_all = [data['macrophytes_sD'][t, :, :] for t, _ in times]

    d_vmin, d_vmax = min(np.nanmin(d) for d in diatoms_all), max(np.nanmax(d) for d in diatoms_all)
    a_vmin, a_vmax = min(np.nanmin(d) for d in adfish_all), max(np.nanmax(d) for d in adfish_all)
    m_vmin, m_vmax = min(np.nanmin(d) for d in macro_all), max(np.nanmax(d) for d in macro_all)
    for v in [d_vmax, a_vmax, m_vmax]:
        pass
    if d_vmax <= d_vmin: d_vmax = d_vmin + 1e-6
    if a_vmax <= a_vmin: a_vmax = a_vmin + 1e-6
    if m_vmax <= m_vmin: m_vmax = m_vmin + 1e-6

    for row, (t, label) in enumerate(times):
        # Diatoms surface
        ax = axes[row, 0]
        field = diatoms_all[row]
        pc = ax.pcolormesh(X, Y, field, cmap='YlGn', shading='auto', vmin=d_vmin, vmax=d_vmax)
        mark_rivers(ax)
        setup_ax(ax, f'硅藻表层 {label}')
        if row == 0:
            ax.set_title(f'硅藻表层 (gDW/m3)\n{label}', fontsize=10)
        else:
            ax.set_title(f'{label}', fontsize=10)

        # AdFish depth-avg
        ax = axes[row, 1]
        field = adfish_all[row]
        pc = ax.pcolormesh(X, Y, field, cmap='YlOrRd', shading='auto', vmin=a_vmin, vmax=a_vmax)
        mark_rivers(ax)
        setup_ax(ax, f'成鱼垂向平均 {label}')
        if row == 0:
            ax.set_title(f'成鱼垂向平均 (gDW/m3)\n{label}', fontsize=10)
        else:
            ax.set_title(f'{label}', fontsize=10)

        # Macrophytes benthic
        ax = axes[row, 2]
        field = macro_all[row]
        pc = ax.pcolormesh(X, Y, field, cmap='YlGn', shading='auto', vmin=m_vmin, vmax=m_vmax)
        mark_rivers(ax)
        mark_se_bay(ax)
        setup_ax(ax, f'大型水草 {label}')
        if row == 0:
            ax.set_title(f'大型水草 (gDW/m2)\n{label}', fontsize=10)
        else:
            ax.set_title(f'{label}', fontsize=10)

    fig.suptitle('空间演化: 硅藻(表层) | 成鱼(垂向平均) | 大型水草(底栖)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save_fig(fig, 'FW10_spatial_evolution.png')


# ============================================================
# Main
# ============================================================
def main():
    print(f"Case dir: {CASE_DIR}")
    print(f"Figure dir: {FIG_DIR}")
    print("Loading data...")
    data = load_data()
    print(f"  Time records: {data['n_time']}")
    print(f"  Sigma values: {len(data['sigma'])}")
    print(f"  Bathymetry shape: {data['bathymetry'].shape}")
    print(f"  Mean depth: {np.nanmean(data['bathymetry']):.2f} m")

    print("\nGenerating figures...")
    fig01_phytoplankton_3d(data)
    fig02_phytoplankton_seasonal(data)
    fig03_zooplankton_3d(data)
    fig04_fish_3d(data)
    fig05_fish_vertical(data)
    fig06_macrophytes_benthic(data)
    fig07_organic_matter(data)
    fig08_sediment_nutrients(data)
    fig09_trophic_levels_timeseries(data)
    fig10_spatial_evolution(data)

    print(f"\nAll 10 figures saved to: {FIG_DIR}")


if __name__ == '__main__':
    main()
