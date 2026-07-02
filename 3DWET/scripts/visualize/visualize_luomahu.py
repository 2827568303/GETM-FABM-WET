#!/usr/bin/env python3
"""骆马湖三维模型可视化脚本 - 网格、边界条件、模拟结果"""

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os

rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

BASE_DIR = r'c:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case'
FIG_DIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)


def load_bathymetry():
    ds = nc.Dataset(os.path.join(BASE_DIR, 'bathymetry.nc'))
    bathy = ds.variables['bathymetry'][:]
    lon = ds.variables['lonc'][:]
    lat = ds.variables['latc'][:]
    x = ds.variables['x'][:]
    y = ds.variables['y'][:]
    ds.close()
    return bathy, lon, lat, x, y


def load_rivers():
    ds = nc.Dataset(os.path.join(BASE_DIR, 'rivers.nc'))
    time = ds.variables['time'][:]
    river_data = {}
    for v in ds.variables:
        if v != 'time':
            river_data[v] = ds.variables[v][:]
    ds.close()
    
    riverinfo_path = os.path.join(BASE_DIR, 'riverinfo.dat')
    river_positions = {}
    if os.path.exists(riverinfo_path):
        with open(riverinfo_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    i, j, name = int(parts[0]), int(parts[1]), parts[2]
                    river_positions[name] = (i, j)
    
    return time, river_data, river_positions


def load_meteo():
    ds = nc.Dataset(os.path.join(BASE_DIR, 'meteo.nc'))
    time = ds.variables['time'][:]
    t2m = ds.variables['t2m'][:]
    u10 = ds.variables['u10'][:]
    v10 = ds.variables['v10'][:]
    ssrd = ds.variables['ssrd'][:]
    ds.close()
    return time, t2m, u10, v10, ssrd


def plot_bathymetry_2d(bathy, lon, lat):
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    bathy_masked = np.ma.masked_where(bathy <= -999, bathy)
    
    im = ax.pcolormesh(lon, lat, bathy_masked, cmap='terrain_r', shading='nearest')
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('水深 (m)')
    
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_title('骆马湖地形水深分布')
    ax.set_aspect('equal')
    
    water_cells = np.sum(bathy_masked > -999)
    ax.text(0.02, 0.02, f'有效水网格数: {water_cells}', transform=ax.transAxes,
            bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '01_bathymetry_2d.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 01_bathymetry_2d.png')


def plot_grid_3d(bathy, x, y):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    bathy_masked = np.ma.masked_where(bathy <= -999, bathy)
    
    X, Y = np.meshgrid(x, y)
    Z = bathy_masked
    
    surf = ax.plot_surface(X, Y, Z, cmap='terrain_r', alpha=0.8,
                           linewidth=0, antialiased=True)
    
    cbar = fig.colorbar(surf, ax=ax, shrink=0.6)
    cbar.set_label('水深 (m)')
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('水深 (m)')
    ax.set_title('骆马湖三维地形网格')
    
    ax.view_init(elev=30, azim=-60)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '02_bathymetry_3d.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 02_bathymetry_3d.png')


def plot_grid_structure(bathy, x, y):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    bathy_masked = np.ma.masked_where(bathy <= -999, bathy)
    
    X, Y = np.meshgrid(x, y)
    
    ax = axes[0]
    ax.pcolormesh(X, Y, bathy_masked, cmap='terrain_r', shading='nearest')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title(f'水平网格 ({len(x)} x {len(y)})')
    ax.set_aspect('equal')
    
    for i in range(0, len(x), 5):
        ax.axvline(x[i], color='gray', alpha=0.3, linewidth=0.5)
    for j in range(0, len(y), 5):
        ax.axhline(y[j], color='gray', alpha=0.3, linewidth=0.5)
    
    ax = axes[1]
    valid_bathy = bathy_masked.compressed()
    ax.hist(valid_bathy, bins=30, color='steelblue', edgecolor='white', alpha=0.8)
    ax.set_xlabel('水深 (m)')
    ax.set_ylabel('网格数')
    ax.set_title('水深分布直方图')
    ax.axvline(np.mean(valid_bathy), color='red', linestyle='--', label=f'平均: {np.mean(valid_bathy):.2f}m')
    ax.axvline(np.median(valid_bathy), color='orange', linestyle='--', label=f'中位: {np.median(valid_bathy):.2f}m')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '03_grid_structure.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 03_grid_structure.png')


def plot_river_locations(bathy, lon, lat, river_positions):
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    bathy_masked = np.ma.masked_where(bathy <= -999, bathy)
    
    im = ax.pcolormesh(lon, lat, bathy_masked, cmap='terrain_r', shading='nearest', alpha=0.7)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('水深 (m)')
    
    colors = {'YIHE': 'blue', 'LUONAN': 'green', 'DAYUN': 'orange',
              'ZHANGSHAN': 'red', 'YANGHE': 'purple', 'ERHE': 'brown'}
    markers = {'YIHE': 'v', 'LUONAN': 'v', 'DAYUN': '^',
               'ZHANGSHAN': '^', 'YANGHE': '^', 'ERHE': '^'}
    labels_cn = {'YIHE': '沂河(入)', 'LUONAN': '骆南中运河(入)', 'DAYUN': '中运河上段(出/入)',
                 'ZHANGSHAN': '嶂山闸(出)', 'YANGHE': '洋河(出)', 'ERHE': '二河(出)'}
    
    for name, (i, j) in river_positions.items():
        if 0 <= j-1 < lon.shape[0] and 0 <= i-1 < lon.shape[1]:
            lon_river = lon[j-1, i-1]
            lat_river = lat[j-1, i-1]
            color = colors.get(name.upper(), 'black')
            marker = markers.get(name.upper(), 'o')
            label = labels_cn.get(name.upper(), name)
            ax.scatter(lon_river, lat_river, c=color, s=200, marker=marker, 
                      edgecolors='black', linewidths=1.5, zorder=5, label=label)
            ax.annotate(label, (lon_river, lat_river), 
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       bbox=dict(facecolor='white', alpha=0.7, pad=2))
    
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_title('骆马湖河流边界位置')
    ax.set_aspect('equal')
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '04_river_locations.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 04_river_locations.png')


def plot_river_discharge(time, river_data):
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    days = time
    
    inflow_names = ['YIHE', 'LUONAN']
    outflow_names = ['DAYUN', 'ZHANGSHAN', 'YANGHE', 'ERHE']
    
    ax = axes[0]
    total_inflow = np.zeros_like(time, dtype=float)
    for name in inflow_names:
        if name in river_data:
            flow = np.maximum(river_data[name], 0)
            ax.plot(days, flow, label=f'{name} (入)', linewidth=1.5)
            total_inflow += flow
    
    total_outflow = np.zeros_like(time, dtype=float)
    for name in outflow_names:
        if name in river_data:
            flow = np.abs(np.minimum(river_data[name], 0))
            ax.plot(days, flow, label=f'{name} (出)', linewidth=1.5, linestyle='--')
            total_outflow += flow
    
    ax.plot(days, total_inflow, 'k-', linewidth=2.5, label='总入流')
    ax.plot(days, total_outflow, 'k--', linewidth=2.5, label='总出流')
    
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('流量 (m³/s)')
    ax.set_title('河流流量过程线')
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    
    ax = axes[1]
    nutrient_names = ['_ammonium', '_nitrate', '_phosphate']
    nutrient_labels = ['氨氮', '硝酸盐', '磷酸盐']
    nutrient_colors = ['#e41a1c', '#377eb8', '#4daf4a']
    
    for name in ['YIHE']:
        for i, (nut, label) in enumerate(zip(nutrient_names, nutrient_labels)):
            key = name + nut
            if key in river_data:
                ax.plot(days, river_data[key], color=nutrient_colors[i],
                       linewidth=1.5, label=f'{name} {label}')
    
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('浓度 (g/m³)')
    ax.set_title('沂河入流水质过程线')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '05_river_discharge.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 05_river_discharge.png')


def plot_meteo(time, t2m, u10, v10, ssrd):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    days = np.arange(len(time)) / 24.0
    
    ax = axes[0, 0]
    ax.plot(days, t2m.flatten() - 273.15, 'r-', linewidth=0.5, alpha=0.7)
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('气温 (°C)')
    ax.set_title('气温')
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    wind_speed = np.sqrt(u10.flatten()**2 + v10.flatten()**2)
    ax.plot(days, wind_speed, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('风速 (m/s)')
    ax.set_title('10m风速')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 0]
    ax.plot(days, ssrd.flatten(), 'orange', linewidth=0.5, alpha=0.7)
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('太阳辐射 (W/m²)')
    ax.set_title('地表向下短波辐射')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    daily_temp = np.mean((t2m.flatten() - 273.15).reshape(-1, 24), axis=1)
    daily_wind = np.mean(wind_speed.reshape(-1, 24), axis=1)
    daily_ssrd = np.mean(ssrd.flatten().reshape(-1, 24), axis=1)
    
    ax2 = ax.twinx()
    l1 = ax.plot(np.arange(len(daily_temp)), daily_temp, 'r-', linewidth=1.5, label='气温')
    l2 = ax2.plot(np.arange(len(daily_ssrd)), daily_ssrd, 'orange', linewidth=1.5, label='太阳辐射')
    
    ax.set_xlabel('时间 (天)')
    ax.set_ylabel('气温 (°C)', color='r')
    ax2.set_ylabel('太阳辐射 (W/m²)', color='orange')
    ax.set_title('日平均气象要素')
    ax.grid(True, alpha=0.3)
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '06_meteo.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 06_meteo.png')


def plot_sigma_layers():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    n_sigma = 5
    sigma = np.linspace(-1, 0, n_sigma + 1)
    sigma_mid = (sigma[:-1] + sigma[1:]) / 2
    
    depths = [1, 3, 5, 8, 10]
    colors = plt.cm.viridis(np.linspace(0, 1, len(depths)))
    
    for i, d in enumerate(depths):
        z = sigma * d
        ax.plot([i-0.3, i+0.3], [z[0], z[0]], color=colors[i], linewidth=2)
        for j in range(len(sigma)):
            ax.plot([i-0.2, i+0.2], [z[j], z[j]], color=colors[i], linewidth=1)
        ax.text(i, -d/2, f'H={d}m', ha='center', va='center', fontsize=10,
               bbox=dict(facecolor='white', alpha=0.8))
    
    ax.set_xticks(range(len(depths)))
    ax.set_xticklabels([f'{d}m水深' for d in depths])
    ax.set_ylabel('深度 (m)')
    ax.set_title(f'Sigma垂向分层 ({n_sigma}层)')
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(0, color='black', linewidth=1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, '07_sigma_layers.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  保存: 07_sigma_layers.png')


def main():
    print('=' * 60)
    print('骆马湖三维模型可视化')
    print('=' * 60)
    
    print('\n[1] 加载数据...')
    bathy, lon, lat, x, y = load_bathymetry()
    time_river, river_data, river_positions = load_rivers()
    time_met, t2m, u10, v10, ssrd = load_meteo()
    
    print(f'  网格: {len(x)} x {len(y)} = {len(x)*len(y)} 个')
    print(f'  bathy shape: {bathy.shape}')
    print(f'  有效水网格: {np.sum(bathy > -999)} 个')
    print(f'  河流数据时间步: {len(time_river)}')
    print(f'  气象数据时间步: {len(time_met)}')
    
    print('\n[2] 绘制地形水深分布...')
    plot_bathymetry_2d(bathy, lon, lat)
    
    print('\n[3] 绘制三维地形...')
    plot_grid_3d(bathy, x, y)
    
    print('\n[4] 绘制网格结构...')
    plot_grid_structure(bathy, x, y)
    
    print('\n[5] 绘制河流边界位置...')
    plot_river_locations(bathy, lon, lat, river_positions)
    
    print('\n[6] 绘制河流流量和水质...')
    plot_river_discharge(time_river, river_data)
    
    print('\n[7] 绘制气象数据...')
    plot_meteo(time_met, t2m, u10, v10, ssrd)
    
    print('\n[8] 绘制sigma垂向分层...')
    plot_sigma_layers()
    
    print('\n' + '=' * 60)
    print(f'可视化完成！图表保存在: {FIG_DIR}')
    print('=' * 60)


if __name__ == '__main__':
    main()
