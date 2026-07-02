"""Generate cascade crash diagnostic + corrected temperature plot."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

for fp in ['/mnt/c/Windows/Fonts/simhei.ttf', '/mnt/c/Windows/Fonts/msyh.ttc']:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
FIG_DIR = os.path.join(CASE, 'figures', 'after_fix')
os.makedirs(FIG_DIR, exist_ok=True)

import netCDF4 as nc

ds = nc.Dataset(os.path.join(CASE, 'output.nc'), 'r')
ds3d = nc.Dataset(os.path.join(CASE, 'THEORETICAL_LAKE.3d.nc'), 'r')

def surf_mean(varname):
    if varname not in ds.variables:
        return None
    data = ds.variables[varname][:]
    if len(data.shape) == 4:
        return np.nanmean(data[:, 0, :, :], axis=(1, 2))
    elif len(data.shape) == 3:
        return np.nanmean(data, axis=(1, 2))
    return data[:]

days = np.arange(365)

# ---------- Cascade crash diagnostic ----------
print("=== Generating cascade crash diagnostic ===")
fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle('生态级联崩溃诊断：浮游植物→浮游动物→鱼类\n(初始浮游植物过低引发连锁反应)',
             fontsize=14, fontweight='bold')

# Panel 1: Phytoplankton (log scale)
ax = axes[0]
for v, label, color in [('diatoms_sDW', '硅藻', 'tab:green'),
                         ('greens_sDW', '绿藻', 'tab:orange'),
                         ('cyanobacteria_sDW', '蓝藻', 'tab:blue')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_ylabel('生物量 (gDW/m3)')
ax.set_title('(a) 浮游植物：硅藻暴发(峰值46)，绿藻崩溃，蓝藻秋季水华')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-4, 100)
ax.axvspan(0, 30, alpha=0.1, color='red', label='初始调整期')

# Panel 2: Zooplankton
ax = axes[1]
for v, label, color in [('cladocerans_sD', '枝角类', 'tab:cyan'),
                         ('copepods_sD', '桡足类', 'tab:pink')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_ylabel('生物量 (gDW/m3)')
ax.set_title('(b) 浮游动物：前30天即崩溃（食物不足+捕食压力）')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-5, 1)

# Panel 3: Fish
ax = axes[2]
for v, label, color in [('JuFish_sD', '幼鱼', 'tab:olive'),
                         ('AdFish_sD', '成鱼', 'tab:gray'),
                         ('PiscFish_sD', '凶猛鱼', 'tab:red')]:
    ts = surf_mean(v)
    if ts is not None:
        ax.plot(days, ts, label=label, color=color, linewidth=2)
ax.set_ylabel('生物量 (gDW/m3)')
ax.set_xlabel('天数')
ax.set_title('(c) 鱼类：幼鱼和凶猛鱼崩溃，成鱼下降（食物链断裂）')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-3, 1)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A05_cascade_crash.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A05_cascade_crash.png")

# ---------- Corrected temperature plot (3D file) ----------
print("=== Generating corrected temperature plot ===")
temp = ds3d.variables['temp'][:]  # (730, 11, 7, 5)
print(f"  3D temp: shape={temp.shape}, range=[{np.nanmin(temp):.2f},{np.nanmax(temp):.2f}]")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('温度时间序列（3D文件，数据正常，之前NaN是numrecs patch前误报）',
             fontsize=13, fontweight='bold')

# Surface & bottom temp
ax = axes[0]
# temp dims: (time, sigma, yc, xc), sigma=0 is surface, sigma=10 is bottom
surf_t = np.nanmean(temp[:, 0, :, :], axis=(1, 2))
bot_t = np.nanmean(temp[:, -1, :, :], axis=(1, 2))
days3d = np.arange(len(surf_t))
ax.plot(days3d/2, surf_t, 'r-', label='表面', linewidth=1.5)
ax.plot(days3d/2, bot_t, 'b-', label='底层', linewidth=1.5)
ax.fill_between(days3d/2, surf_t, bot_t, alpha=0.2, color='orange')
ax.set_xlabel('天数')
ax.set_ylabel('温度 (°C)')
ax.set_title('(a) 表面与底层温度')
ax.legend()
ax.grid(True, alpha=0.3)

# Vertical profile at center, seasonal
ax = axes[1]
ci, cj = 2, 3
for day_idx, season in [(0, '冬季(Day0)'), (180, '夏季(Day90)'), (360, '秋季(Day180)'), (720, '年末(Day360)')]:
    if day_idx < temp.shape[0]:
        profile = temp[day_idx, :, cj, ci]
        ax.plot(profile, np.arange(len(profile)), '-o', label=season, linewidth=2)
ax.set_ylim(len(profile)-0.5, -0.5)
ax.set_xlabel('温度 (°C)')
ax.set_ylabel('σ层（0=水面，10=湖底）')
ax.set_title('(b) 中心网格垂向温度剖面')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'A03_temperature.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A03_temperature.png (corrected)")

# ---------- Parameter comparison table ----------
print("=== Generating parameter comparison ===")
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('off')

params = [
    ['cMuMax (最大生长率)', '1.4', '2.4', '1.0', '硅藻最高，绿藻最低'],
    ['kDResp (呼吸损失)', '0.03', '0.10', '0.075', '蓝藻最低(耐饥饿)'],
    ['净生长率 (MuMax-Resp)', '1.37', '2.30', '0.925', '绿藻最低→竞争失败'],
    ['cTmOpt (最适温度)', '25°C', '18°C', '25°C', '硅藻春季，蓝藻/绿藻夏季'],
    ['cLOptRef (最适光照)', '23 W/m2', '35 W/m2', '30 W/m2', '硅藻耐高光'],
    ['cVSet (沉降速率)', '+0.03', '-0.50', '-0.35', '硅藻/绿藻下沉，蓝藻悬浮'],
    ['cExtSp (比消光)', '0.35', '0.25', '0.25', '蓝藻自遮光强'],
    ['lSi (硅需求)', '否', '是', '否', '硅藻需硅'],
    ['cVPUptMax (P摄取)', '0.04', '0.01', '0.01', '蓝藻P摄取最强'],
]

table = ax.table(cellText=params,
                 colLabels=['参数', '蓝藻', '硅藻', '绿藻', '说明'],
                 cellLoc='center', loc='center',
                 colWidths=[0.22, 0.1, 0.1, 0.1, 0.38])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.8)

# Color header
for j in range(5):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold')
# Highlight key rows
for i in [3]:  # net growth rate row
    for j in range(5):
        table[i, j].set_facecolor('#FFE699')

ax.set_title('三类浮游植物关键参数对比\n绿藻净生长率最低(0.925)→在资源竞争中被硅藻(2.3)和蓝藻(1.37)排除',
             fontsize=12, fontweight='bold', pad=20)
plt.savefig(os.path.join(FIG_DIR, 'A06_parameter_comparison.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved A06_parameter_comparison.png")

ds.close()
ds3d.close()
print("\nAll diagnostic figures saved to:", FIG_DIR)
