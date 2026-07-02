"""Generate Yilong vs Theoretical Lake comparison report."""
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

FIG_DIR = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong/figures'
os.makedirs(FIG_DIR, exist_ok=True)


def to_np(data):
    return np.ma.filled(data, np.nan)


def patch_numrecs(filepath, num_recs):
    import struct
    with open(filepath, 'r+b') as f:
        f.seek(4)
        f.write(struct.pack('>I', num_recs))


def load_surf_mean(path, varname):
    ds = nc.Dataset(path, 'r')
    if varname not in ds.variables:
        ds.close()
        return None
    data = to_np(ds.variables[varname][:])
    ds.close()
    if len(data.shape) == 4:
        return np.nanmean(data[:, 0, :, :], axis=(1, 2))
    elif len(data.shape) == 3:
        return np.nanmean(data, axis=(1, 2))
    return data[:]


# Patch numrecs for both cases
YILONG = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong'
THEOR = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'

patch_numrecs(YILONG + '/output.nc', 365)
patch_numrecs(THEOR + '/output.nc', 365)

# ============================================================
# Comparison: Yilong (fixed init) vs Theoretical (old init)
# ============================================================
print("=== Generating Yilong vs Theoretical comparison ===")
fig, axes = plt.subplots(3, 2, figsize=(16, 14))
fig.suptitle('异龙湖模型 vs 理论湖泊模型 对比\n'
             '异龙湖: 真实湖泊形状(28×8), 修复初值, 云南气候\n'
             '理论湖泊: 简化形状(5×7), 旧初值(级联崩溃), 骆马湖气候',
             fontsize=13, fontweight='bold')

# 1. Phytoplankton
ax = axes[0, 0]
for case_path, label_prefix, ls in [(YILONG, '异龙湖', '-'), (THEOR, '理论湖泊', '--')]:
    for v, label, color in [('diatoms_sDW', '硅藻', 'g'),
                             ('greens_sDW', '绿藻', 'orange'),
                             ('cyanobacteria_sDW', '蓝藻', 'b')]:
        ts = load_surf_mean(case_path + '/output.nc', v)
        if ts is not None:
            days = np.arange(len(ts))
            ax.plot(days, ts, ls, color=color, linewidth=1.5,
                    label=f'{label_prefix}-{label}')
ax.set_xlabel('天数')
ax.set_ylabel('生物量 (gDW/m³)')
ax.set_title('(a) 浮游植物：异龙湖3类藻都生长，理论湖泊绿藻崩溃')
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-4, 100)

# 2. Zooplankton (cascade crash fix validation)
ax = axes[0, 1]
for case_path, label_prefix, ls in [(YILONG, '异龙湖(初值0.3)', '-'), (THEOR, '理论湖泊(初值0.1)', '--')]:
    for v, label, color in [('cladocerans_sD', '枝角类', 'c'),
                             ('copepods_sD', '桡足类', 'm')]:
        ts = load_surf_mean(case_path + '/output.nc', v)
        if ts is not None:
            days = np.arange(len(ts))
            ax.plot(days, ts, ls, color=color, linewidth=1.5,
                    label=f'{label_prefix}-{label}')
ax.set_xlabel('天数')
ax.set_ylabel('生物量 (gDW/m³)')
ax.set_title('(b) 浮游动物：异龙湖稳定，理论湖泊崩溃（关键修复验证）')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-5, 1)

# 3. Fish
ax = axes[1, 0]
for case_path, label_prefix, ls in [(YILONG, '异龙湖(降50%)', '-'), (THEOR, '理论湖泊', '--')]:
    for v, label, color in [('JuFish_sD', '幼鱼', 'y'),
                             ('AdFish_sD', '成鱼', 'gray'),
                             ('PiscFish_sD', '凶猛鱼', 'r')]:
        ts = load_surf_mean(case_path + '/output.nc', v)
        if ts is not None:
            days = np.arange(len(ts))
            ax.plot(days, ts, ls, color=color, linewidth=1.5,
                    label=f'{label_prefix}-{label}')
ax.set_xlabel('天数')
ax.set_ylabel('生物量 (gDW/m³)')
ax.set_title('(c) 鱼类：异龙湖稳定，理论湖泊崩溃')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_yscale('log')
ax.set_ylim(1e-3, 1)

# 4. Nutrients
ax = axes[1, 1]
for case_path, label_prefix, ls in [(YILONG, '异龙湖', '-'), (THEOR, '理论湖泊', '--')]:
    for v, label, color in [('abiotic_water_sNH4W', 'NH4+', 'r'),
                             ('abiotic_water_sNO3W', 'NO3-', 'b'),
                             ('abiotic_water_sPO4W', 'PO4³-', 'purple')]:
        ts = load_surf_mean(case_path + '/output.nc', v)
        if ts is not None:
            days = np.arange(len(ts))
            ax.plot(days, ts, ls, color=color, linewidth=1.5,
                    label=f'{label_prefix}-{label}')
ax.set_xlabel('天数')
ax.set_ylabel('浓度 (g/m³)')
ax.set_title('(d) 营养盐：两者年末都耗尽（硅藻过度消耗）')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 5. Temperature comparison
ax = axes[2, 0]
for case_path, label_prefix, fname, ls in [(YILONG, '异龙湖(云南18°C)', 'YILONG.3d.nc', '-'),
                                            (THEOR, '理论湖泊(骆马湖10°C)', 'THEORETICAL_LAKE.3d.nc', '--')]:
    patch_numrecs(case_path + '/' + fname, 730)
    ds = nc.Dataset(case_path + '/' + fname, 'r')
    if 'temp' in ds.variables:
        temp = to_np(ds.variables['temp'][:])
        surf_t = np.nanmean(temp[:, 0, :, :], axis=(1, 2))
        ds.close()
        days3 = np.arange(len(surf_t))
        ax.plot(days3/2, surf_t, ls, label=label_prefix, linewidth=1.5)
ax.set_xlabel('天数')
ax.set_ylabel('温度 (°C)')
ax.set_title('(e) 温度：云南高原年均18°C vs 骆马湖年均10°C')
ax.legend()
ax.grid(True, alpha=0.3)

# 6. Light limitation
ax = axes[2, 1]
for case_path, label_prefix, ls in [(YILONG, '异龙湖', '-'), (THEOR, '理论湖泊', '--')]:
    for v, label, color in [('diatoms_aLLim', '硅藻', 'g'),
                             ('cyanobacteria_aLLim', '蓝藻', 'b')]:
        ts = load_surf_mean(case_path + '/output.nc', v)
        if ts is not None:
            days = np.arange(len(ts))
            ax.plot(days, ts, ls, color=color, linewidth=1.5,
                    label=f'{label_prefix}-{label}')
ax.set_xlabel('天数')
ax.set_ylabel('aLLim')
ax.set_title('(f) 光照限制因子：P0修复后两者都非零')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.05, 1.05)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'Y07_comparison_theoretical.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y07_comparison_theoretical.png")

# ============================================================
# Summary table
# ============================================================
print("\n=== Generating summary table ===")
fig, ax = plt.subplots(figsize=(15, 9))
ax.axis('off')

table_data = [
    ['湖泊形状', '简化矩形 5×7', '异龙湖形 28×8\n(东西长条状)', '真实湖泊形状'],
    ['网格数', '35 (全水域)', '224 (112水域)', '6.4倍'],
    ['面积/体积', '8.75 km² / 30.6 Mm³', '28 km² / 98 Mm³', '接近真实异龙湖(40km²/115Mm³)'],
    ['气候', '骆马湖(年均10°C)', '云南高原(年均18°C)', '低纬度高原'],
    ['降水/蒸发', '900/1000 mm', '1321/1198 mm', '云南雨季5-10月'],
    ['浮游植物初值', '0.05 (过低)', '0.2-0.3 (PCLake)', '修复级联崩溃'],
    ['浮游动物初值', '0.1 (过低)', '0.3 (避免饿死)', '关键修复'],
    ['鱼类初值', '0.3/0.8/0.1', '0.15/0.40/0.05', '降低50%减压力'],
    ['营养盐初值', 'NH4=0.4 NO3=0.5', 'NH4=0.3 NO3=1.0', '富营养化'],
    ['光照耦合(aLLim)', '✅ [0, 0.999]', '✅ [0, 0.972]', 'P0修复有效'],
    ['硅藻峰值', '46 gDW/m³ (过高)', '44 gDW/m³ (仍高)', '需进一步调参'],
    ['绿藻', '❌ 崩溃到0.0001', '✅ max=0.23 (稳定)', '级联修复有效'],
    ['蓝藻峰值', '1.4 (秋季水华)', '6.84 (秋季水华)', '云南高温更盛'],
    ['浮游动物', '❌ 崩溃到0.00001', '✅ 稳定在0.25', '关键修复成功'],
    ['鱼类', '❌ 幼鱼崩溃到0.004', '✅ 稳定(幼鱼0.16)', '关键修复成功'],
    ['营养盐年末', '全部耗尽至0', '全部耗尽至0', '硅藻过度消耗'],
    ['水位净变化', '0.0000m', '待确认', '水平衡有效'],
    ['模型运行', '22分钟(8线程)', '约90分钟(8线程)', 'grid大6.4倍'],
]

table = ax.table(cellText=table_data,
                 colLabels=['指标', '理论湖泊(旧)', '异龙湖(新)', '说明'],
                 cellLoc='center', loc='center',
                 colWidths=[0.18, 0.22, 0.25, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.0)

for j in range(4):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Color rows by success/failure
for i in range(1, len(table_data) + 1):
    status = table_data[i-1][2]
    if '✅' in status:
        color = '#C6EFCE'  # green
    elif '❌' in status:
        color = '#FFC7CE'  # red
    elif '⚠️' in status or '仍高' in status or '耗尽' in status:
        color = '#FFEB9C'  # yellow
    else:
        color = '#FFFFFF'  # white
    for j in range(4):
        table[i, j].set_facecolor(color)

ax.set_title('异龙湖模型 vs 理论湖泊模型 全面对比\n'
             '核心成果：生态级联崩溃已修复（浮游动物+鱼类稳定），光照耦合正常',
             fontsize=12, fontweight='bold', pad=20)
plt.savefig(os.path.join(FIG_DIR, 'Y08_summary_table.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  saved Y08_summary_table.png")

print(f"\nAll figures saved to: {FIG_DIR}")
