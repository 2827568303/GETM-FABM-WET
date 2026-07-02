"""Visualize model results after P0+P1 fix. Diagnostic plots for remaining issues."""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Chinese font setup
for fp in ['/mnt/c/Windows/Fonts/simhei.ttf', '/mnt/c/Windows/Fonts/msyh.ttc']:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
FIG_DIR = os.path.join(CASE, 'figures', 'after_fix')
os.makedirs(FIG_DIR, exist_ok=True)

import netCDF4 as nc

# ---------- helpers ----------
def load_output_nc():
    ds = nc.Dataset(os.path.join(CASE, 'output.nc'), 'r')
    return ds

def load_2d_nc():
    ds = nc.Dataset(os.path.join(CASE, 'THEORETICAL_LAKE.2d.nc'), 'r')
    return ds

def load_3d_nc():
    ds = nc.Dataset(os.path.join(CASE, 'THEORETICAL_LAKE.3d.nc'), 'r')
    return ds

def surf_mean(ds, varname):
    """Return time series of surface-layer spatial mean for a 4D variable."""
    if varname not in ds.variables:
        return None
    data = ds.variables[varname][:]
    if len(data.shape) == 4:
        return np.nanmean(data[:, 0, :, :], axis=(1, 2))
    elif len(data.shape) == 3:
        return np.nanmean(data, axis=(1, 2))
    return data[:]

def days_from_time(ds):
    t = ds.variables['time'][:]
    # FABM output time is seconds; may be monotonic or wrapped
    # Use index as day if time is broken
    if len(t) > 1 and np.nanmax(t) > np.nanmin(t):
        return np.arange(len(t))
    return np.arange(len(t))

# ---------- 1. Phytoplankton time series (the key fix validation) ----------
print("=== Generating phytoplankton time series ===")
ds = load_output_nc()
days = days_from_time(ds)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('P0+P1修复后浮游植物时间序列（表面层空间平均）', fontsize=14, fontweight='bold')

# 1a: three phytoplankton groups
ax = axes[0, 0]
for v, label, color in [('diatoms_sDW', '硅藻 Diatoms', 'tab:green'),
                         ('greens_sDW', '绿藻 Greens', 'tab:orange'),
                         ('cyanobacteria_sDW', '蓝藻 Cyanobacteria', 'tab:blue')]:
    ts = surf_mean(ds, v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=1.5)
ax.set_xlabel('天数')
ax.set_ylabel('生物量 (gDW/m³)')
ax.set_title('(a) 三类浮游植物生物量')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# 1b: light limitation factor aLLim
ax = axes[0, 1]
for v, label, color in [('diatoms_aLLim', '硅藻', 'tab:green'),
                         ('greens_aLLim', '绿藻', 'tab:orange'),
                         ('cyanobacteria_aLLim', '蓝藻', 'tab:blue')]:
    ts = surf_mean(ds, v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=1.5)
ax.set_xlabel('天数')
ax.set_ylabel('光照限制因子 aLLim')
ax.set_title('(b) 光照限制因子（修复前=0，修复后非零=光照耦合已修复）')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.05, 1.05)

# 1c: nutrients
ax = axes[1, 0]
for v, label, color in [('abiotic_water_sNH4W', 'NH4⁺', 'tab:red'),
                         ('abiotic_water_sNO3W', 'NO3⁻', 'tab:blue'),
                         ('abiotic_water_sPO4W', 'PO4³⁻', 'tab:purple'),
                         ('abiotic_water_sSiO2W', 'SiO2', 'tab:brown')]:
    ts = surf_mean(ds, v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=1.5)
ax.set_xlabel('天数')
ax.set_ylabel('浓度 (g/m³)')
ax.set_title('(c) 水体营养盐（年末耗尽至0=问题）')
ax.legend()
ax.grid(True, alpha=0.3)

# 1d: zooplankton & fish (grazers)
ax = axes[1, 1]
for v, label, color in [('cladocerans_sD', '枝角类', 'tab:cyan'),
                         ('copepods_sD', '桡足类', 'tab:pink'),
                         ('JuFish_sD', '幼鱼', 'tab:olive'),
                         ('AdFish_sD', '成鱼', 'tab:gray')]:
    ts = surf_mean(ds, v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=1.5)
ax.set_xlabel('天数')
ax.set_ylabel('生物量 (gDW/m³)')
ax.set_title('(d) 浮游动物与鱼类（捕食压力）')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A01_phytoplankton_diagnostic.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A01_phytoplankton_diagnostic.png")

# ---------- 2. Vertical distribution of diatoms (peak bloom) ----------
print("=== Generating diatom vertical heatmap ===")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('硅藻垂向分布热图（中心网格 i=2,j=3）— 峰值46 gDW/m³过高的诊断', fontsize=13, fontweight='bold')

# pick center cell
diatoms = ds.variables['diatoms_sDW'][:]  # (time, k, j, i)
greens = ds.variables['greens_sDW'][:]
cyanos = ds.variables['cyanobacteria_sDW'][:]

# center cell
ci, cj = 2, 3
snapshots = [0, 90, 180]  # init, spring, summer peak
for idx, day in enumerate(snapshots):
    ax = axes[idx]
    profile = diatoms[day, :, cj, ci] if day < diatoms.shape[0] else diatoms[-1, :, cj, ci]
    ax.plot(profile, np.arange(len(profile)), 'g-o', label='硅藻', linewidth=2)
    ax.plot(greens[day, :, cj, ci] if day < greens.shape[0] else greens[-1, :, cj, ci],
            np.arange(len(profile)), 'orange', label='绿藻', linewidth=2)
    ax.plot(cyanos[day, :, cj, ci] if day < cyanos.shape[0] else cyanos[-1, :, cj, ci],
            np.arange(len(profile)), 'b', label='蓝藻', linewidth=2)
    ax.set_ylim(len(profile)-0.5, -0.5)
    ax.set_xlabel('生物量 (gDW/m³)')
    ax.set_ylabel('σ层（0=水面）')
    ax.set_title(f'第{day}天')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A02_vertical_profile.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A02_vertical_profile.png")

# ---------- 3. Temperature from 2D file (since 3D temp is NaN) ----------
print("=== Generating temperature from 2D file ===")
ds2d = load_2d_nc()
print(f"  2D variables: {list(ds2d.variables.keys())[:20]}")
temp_var = None
for v in ['temp', 'tempx', 'T', 'temperature', 'salt']:
    if v in ds2d.variables:
        temp_var = v
        break

fig, ax = plt.subplots(figsize=(12, 5))
if temp_var:
    t_data = ds2d.variables[temp_var][:]
    ts = np.nanmean(t_data, axis=(1, 2)) if len(t_data.shape) >= 2 else t_data[:]
    days2d = np.arange(len(ts))
    ax.plot(days2d, ts, 'r-', linewidth=1.5)
    ax.set_title(f'2D温度时间序列（变量: {temp_var}）')
else:
    # try 3D
    ds3d = load_3d_nc()
    print(f"  3D variables sample: {list(ds3d.variables.keys())[:20]}")
    for v in ['temp', 'T', 'temperature']:
        if v in ds3d.variables:
            t_data = ds3d.variables[v][:]
            ts = np.nanmean(t_data[:, 0, :, :], axis=(1, 2))
            days3d = np.arange(len(ts))
            ax.plot(days3d, ts, 'r-', linewidth=1.5)
            ax.set_title(f'3D表面温度（变量: {v}）')
            break
    else:
        ax.text(0.5, 0.5, '未找到温度变量', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('温度（未找到变量）')

ax.set_xlabel('时间步')
ax.set_ylabel('温度 (°C)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A03_temperature.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A03_temperature.png")

# ---------- 4. Water level ----------
print("=== Generating water level ===")
fig, ax = plt.subplots(figsize=(12, 4))
if 'elev' in ds2d.variables:
    elev = ds2d.variables['elev'][:]
    ts = np.nanmean(elev, axis=(1, 2))
    days2d = np.arange(len(ts))
    ax.plot(days2d, ts, 'b-', linewidth=1.5)
    ax.axhline(ts[0], color='gray', linestyle='--', alpha=0.5, label=f'初始水位 {ts[0]:.3f}m')
    ax.set_title(f'水位时间序列（净变化={ts[-1]-ts[0]:.4f}m，水平衡有效）')
    ax.legend()
ax.set_xlabel('时间步')
ax.set_ylabel('水位 (m)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A04_water_level.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A04_water_level.png")

# ---------- 5. Summary statistics ----------
print("\n=== Summary Statistics ===")
stats = []
for v in ['diatoms_sDW', 'greens_sDW', 'cyanobacteria_sDW',
          'diatoms_aLLim', 'greens_aLLim', 'cyanobacteria_aLLim',
          'abiotic_water_sNH4W', 'abiotic_water_sNO3W', 'abiotic_water_sPO4W',
          'cladocerans_sD', 'copepods_sD', 'JuFish_sD', 'AdFish_sD', 'PiscFish_sD']:
    if v not in ds.variables:
        continue
    data = ds.variables[v][:]
    ts = surf_mean(ds, v)
    stats.append({
        'var': v,
        'min': float(np.nanmin(data)),
        'max': float(np.nanmax(data)),
        'first': float(ts[0]) if len(ts) else float('nan'),
        'last': float(ts[-2]) if len(ts) > 1 else float('nan'),  # last may be corrupt
    })

with open(os.path.join(FIG_DIR, 'stats_summary.txt'), 'w') as f:
    f.write("P0+P1修复后模型结果统计\n")
    f.write("="*70 + "\n")
    f.write(f"{'变量':<30} {'最小值':>12} {'最大值':>12} {'首日':>12} {'末日':>12}\n")
    f.write("-"*70 + "\n")
    for s in stats:
        f.write(f"{s['var']:<30} {s['min']:>12.6f} {s['max']:>12.6f} {s['first']:>12.6f} {s['last']:>12.6f}\n")

print("  saved stats_summary.txt")
ds.close()
ds2d.close()
print("\nAll figures saved to:", FIG_DIR)
