# 骆马湖 GETM 水动力模块调试日志

**案例目录**: `3DWET/case/Lake Luoma_EFDC trans/`
**模型版本**: GETM 2.5.0 + GOTM 5.4.0 + FABM
**编译器**: GNU 13.3.0 (serial + OpenMP)
**模拟周期**: 2020-01-01 ~ 2022-12-30 (1094天)
**最终状态**: ✅ 方案D (dt=15s) 成功完成3年运行，数据完整无NaN

---

## 一、项目背景与目标

以骆马湖EFDC模型为参考，在GETM框架下构建纯水动力基线，验证EFDC→GETM数据转换路径的可行性，为后续WET生态模型耦合奠定基础。

**EFDC参考模型特征**:
- 网格: 52×46，分辨率500m
- 水域cell: 1586个（原始EFDC标记1193个'5' + 393个'9'）
- 水深: 3.5–4.1m
- 河流: 9个源汇点（ZH、YH、YHT、XYH、ZYH等5条河流）
- 气象: 1096天ERA5数据
- 仅水动力+温度输运，不含水质生态

---

## 二、调试阶段时间线

### 阶段1：EFDC数据转换 (efdc_to_getm.py)

**目标**: 将EFDC格式的bathymetry、meteorological、river数据转换为GETM所需的NetCDF文件。

**转换映射**:
| EFDC文件 | GETM文件 | 说明 |
|----------|----------|------|
| cell.inp + dxdy.inp | bathymetry.nc | 地形与水域掩膜 |
| ERA5气象数据 | meteo.nc | 风速、温度、辐射、气压 |
| 流量时间序列 | rivers.nc | 9条河流流量 |

**关键脚本**: [efdc_to_getm.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/efdc_to_getm.py)

---

### 阶段2：'9' cell水域丢失bug修复

**问题**: 初次转换后水域cell仅1193个，缺失393个（24.8%水域面积丢失）。

**根因分析**:
- EFDC的`cell.inp`用两种字符标记水域：`'5'`（正常水域，有depth数据）和`'9'`（水域但无depth数据）
- 转换脚本读取`dxdy.inp`时，`'9'` cell的depth为NaN
- `nan_to_num`将NaN转为0
- `depth <= 0`判断将`'9'` cell误设为LAND_VALUE(-10)

**修复方案** ([efdc_to_getm.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/efdc_to_getm.py) 约403行):
新增`fill_missing_depth`函数，用迭代邻居平均值填充`'9'` cell的depth：
```python
def fill_missing_depth(depth, land_mask, max_iter=50):
    """Fill missing depth values using iterative neighbor averaging."""
    for _ in range(max_iter):
        missing = np.isnan(depth) & (~land_mask)
        if not missing.any():
            break
        # 4-neighbor average for each missing cell
        ...
```

**结果**: 水域cell从1193 → 1586，完全恢复。

---

### 阶段3：河流单cell过载扩展

**问题**: 河流入流口单cell流量过大（ZH=68 m/day, YH=65 m/day, YHT=26 m/day），导致局部速度过高引发数值不稳定。

**用户诊断**:
> "崩溃的地方是在京杭大运河（正负流量）以及新沂河（流量大的出湖河道）...是否1个网格不够容纳那么大的流量会导致模型崩溃"

**修复方案**: 利用GETM的`river_split`机制（同名连续行自动分摊流量），将5条主要河流各从1 cell扩展为3 cells。

**riverinfo.dat变更** ([riverinfo.dat](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/riverinfo.dat)):
```
原始(9行):                    扩展后(15行):
9                             15
45 33 XYH -1 -1              45 33 XYH -1 -1
15 44 YH -1 -1               44 33 XYH -1 -1
50 12 YHT -1 -1              43 33 XYH -1 -1
21 6 ZH -1 -1                15 44 YH -1 -1
10 20 ZYH -1 -1              15 43 YH -1 -1
                             14 44 YH -1 -1
                             50 12 YHT -1 -1
                             50 11 YHT -1 -1
                             49 12 YHT -1 -1
                             21 6 ZH -1 -1
                             21 5 ZH -1 -1
                             20 6 ZH -1 -1
                             10 20 ZYH -1 -1
                             8 18 ZYH -1 -1
                             9 19 ZYH -1 -1
```

**流量分摊**: 每条河流的流量时间序列自动除以3，单cell负载降至原来的1/3。

---

### 阶段4：v2综合稳定性改进 (stability_fix.py)

**目标**: 在河流扩展基础上，集成多项数值稳定性改进。

**改进内容** ([stability_fix.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/stability_fix.py)):
1. **bathymetry平滑**: 20-pass全局平滑，消除地形突变
2. **内部压力梯度**: `ip_method=2`, `ip_ramp=-1`, `cord_relax=0.1`（缓解sigma坐标IPG误差）
3. **背景粘性**: `avmback=1.0E-5`, `avhback=1.0E-6`
4. **河流流量cap**: 上限200 m³/s，11天滑动平均
5. **垂向分层**: M=10层, `min_depth=1.0`

**结果**: 崩溃时间从 day 233 → day 387.9，有效数据374天。

---

### 阶段5：v4斜压（温度）运行

**配置变更**:
- `runtype=4`（3D斜压）
- `calc_temp=.true.`, `calc_salt=.false.`
- 温度初始值: 5.89°C
- 衰减系数: A=0.6, g1=0.5, g2=20.0

**结果**: 完成温度计算，生成全套温度可视化（6张图）。

---

### 阶段6：不稳定原因深度诊断

**用户质疑**:
> "为什么说'day 387.9是系统性触发点...周期性外部强迫'？"

**诊断工作**:
1. **GETM源码分析** ([check_3d_fields.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/getm/src/futils/check_3d_fields.F90), [vv_momentum_3d.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/getm/src/3d/vv_momentum_3d.F90)):
   - `check_3d_fields`检查`f(i,j,k) < minval or > maxval`，阈值默认±4.0 m/s（本案例设为±10.0）
   - `vel_check > 0`: 越界终止；`< 0`: 仅警告；`0`: 禁用
   - `mod(n, abs(vel_check))`控制检查频率

2. **崩溃位置确认** ([crash_vs_rivers.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/crash_vs_rivers.py)):
   - 崩溃点在ZYH（京杭大运河）下游约2.5网格处
   - 该区域流速局部最高，CFL数最先超限

3. **5个假说检验** ([deep_diagnosis_v2.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/deep_diagnosis_v2.py)):
   - H1 (GETM代码bug): ❌ 排除
   - H2 (浮点累积): ❌ 排除
   - H3 (meteo缺陷): ❌ day 387气象数据正常
   - H4 (bathy特征): ❌ 崩溃区地形无特殊突变
   - H5 (年度循环共振): ❌ 无证据

**修正**: 承认"周期性外部强迫"推断缺乏证据，转向多方案实验。

---

### 阶段7：4方案逐一试验

采用控制变量法，逐一试验4个改进方案。

#### 方案A: vel_check=-1（仅警告不终止）

**改动**: [getm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp) 中 `vel_check=1` → `vel_check=-1`

**备份**: [getm.inp.scheme_a](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp.scheme_a)

**结果**:
- 模型完成3年运行，无FATAL终止
- 但首次警告在 n≈19550（day ~6.8），位置(i=8-9, j=15-19)即ZH/YH区域
- 警告后NaN扩散，有效数据仍仅387.9天
- **结论**: 治标不治本，数据已损坏

#### 方案B: ZYH流量15天平滑

**改动**: [scheme_b_zyh_smooth.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/scheme_b_zyh_smooth.py)
- ZYH滑动窗口: 11天 → 15天
- 其他河流保持11天
- 流量上限cap=200 m³/s

**结果**:
- 崩溃时间: day 387.9 → day 417.7（n=1203000）
- 崩溃位置: (i=5-15, j=29-31)，ZYH下游
- 速度爆发到 1E+235
- **结论**: 延缓30天，未根本解决

#### 方案C: 崩溃区bathymetry额外平滑

**改动**: [scheme_c_bathy_smooth.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/scheme_c_bathy_smooth.py)
- 在方案B基础上，对3个崩溃区域额外30-pass平滑：
  - v3_region: (i=5-15, j=27-34)
  - v4_region: (i=4-11, j=12-19)
  - schemeB_region: (i=4-15, j=27-34)
- 深度范围: 1.02–12.36m

**结果**:
- 崩溃时间: day 417.7 → day 424.1（n=1223500）
- 崩溃位置: (i=6-17, j=24-28)，仍在ZYH下游
- 速度爆发到 1E+24
- **结论**: 仅延长7天，地形平滑效果有限

#### 方案D: 减小时间步长 dt=15s ✅ 最终方案

**改动** ([getm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp)):
- `timestep`: 30.0 → 15.0
- `step_2d`/`sync_2d`/`step_3d`/`sync_3d`: 288 → 576（保持2.4小时输出频率）
- 保留方案C的bathymetry和方案B的rivers

**运行日志** ([run.log](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/run.log)):
- 启动: 20260703 021813
- 完成: 20260703 034454
- 总时间步: 6,301,440步
- TIMERS SUM: 4538.64秒

**关键里程碑**:
| 模型时间 | 状态 | 说明 |
|----------|------|------|
| day 387.9 | ✅ 突破基线崩溃点 | 正常运行 |
| day 424.1 | ✅ 突破方案C崩溃点 | 正常运行 |
| day 1094 | ✅ 完成3年 | 正常结束 |

**数据验证** ([verify_scheme_d.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/verify_scheme_d.py)):
| 变量 | 时间步数 | NaN数 | 范围 |
|------|---------|-------|------|
| elev (2D) | 10940 | 0 | -0.002 ~ 9.67 m |
| temp (3D) | 10940 | 0 | -0.02 ~ 29.11 °C |
| u (3D) | 10940 | 0 | -0.098 ~ 0.088 m/s |

**输出文件**:
- `LUOMA_EFDC_HYD.2d.nc`: 314 MB
- `LUOMA_EFDC_HYD.3d.nc`: 9.5 GB

---

## 三、4方案结果对比汇总

| 方案 | 改进内容 | 崩溃时间 | 有效数据 | vs基线 | 结论 |
|------|---------|---------|---------|--------|------|
| **基线(v4)** | 20-pass+ip2+M10+温度 | day 387.9 | 374.4天 | — | check_3d_fields速度越界终止 |
| **方案A** | vel_check=-1 | "完成"3年* | 387.9天* | 无提升 | NaN扩散，数据损坏 |
| **方案B** | +ZYH 15天平滑 | day 417.7 | ~404天 | +30天 | 延缓未解决 |
| **方案C** | +崩溃区30-pass平滑 | day 424.1 | ~410天 | +7天 | 微弱改善 |
| **方案D** | **dt=15s** | **完成3年** | **1094天** | **+669天** | **✅ 完全成功** |

*方案A表面完成但数据无效

---

## 四、根本原因结论

**根本原因是CFL条件不满足**。

- dt=30s在ZYH（京杭大运河）下游区域（i=6-17, j=24-28）导致局部CFL数超限
- 该区域流速最高，对时间步长最敏感
- 速度在数十步内从正常值爆发到1E+24，触发`check_3d_fields`越界
- dt=15s将CFL数减半，彻底解决数值不稳定

**其他方案无效的原因**:
- vel_check=-1: 不终止运行但无法阻止NaN扩散
- 流量平滑: 降低入流峰值，但局部CFL仍超限
- 地形平滑: 减小地形突变，但对CFL影响有限

**唯一根本解决方案**: 减小时间步长，满足CFL约束。

---

## 五、当前最终配置

[getm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp) 关键参数:

```fortran
&param
    runtype      = 4          ! 3D斜压
    calc_temp    = .true.     ! 温度计算
    calc_salt    = .false.    ! 无盐度
/
&time
    timestep     = 15.0       ! ✅ 关键：15秒（原30秒）
    start        = '2020-01-01 00:00:00'
    stop         = '2022-12-30 00:00:00'
/
&domain
    vert_cord    = 1          ! sigma坐标
    maxdepth     = 25.0
    crit_depth   = 2.8
    min_depth    = 1.0
    kdum         = 10
    z0_const     = 0.001
/
&m3d
    M            = 10         ! 10层
    cnpar        = 1.0
    cord_relax   = 0.1        ! 坐标松弛
    avmback      = 1.0E-5     ! 背景动量粘性
    avhback      = 1.0E-6     ! 背景热粘性
    ip_method    = 2          ! 内部压力梯度方法
    ip_ramp      = -1
    vel_check    = 1          ! 速度检查（越界终止）
    min_vel      = -10.0
    max_vel      = 10.0
/
&io_spec
    step_2d      = 576        ! ✅ 2.4小时输出（原288）
    sync_2d      = 576
    step_3d      = 576        ! ✅ 2.4小时输出（原288）
    sync_3d      = 576
/
```

**输入文件**:
- [bathymetry.nc](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/bathymetry.nc): 20-pass全局 + 30-pass崩溃区平滑，1586水域cell
- [rivers.nc](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/rivers.nc): cap=200, ZYH 15天平滑, 其他11天
- [meteo.nc](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/meteo.nc): 1096天ERA5数据
- [riverinfo.dat](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/riverinfo.dat): 15行（5条河流×3 cells）

---

## 六、备份与版本历史

| 目录 | 说明 | 崩溃时间 |
|------|------|---------|
| `backup_before_9cell_fix/` | '9' cell修复前 | day ~233 |
| `backup_v2/` | v2综合改进 | day 233 |
| `backup_v3/` | v3河流扩展 | day 387.9 |
| `backup_v4_barotropic/` | v4正压 | day 387.9 |
| `backup_v4_vel1/` | v4斜压基线 | day 387.9 |
| `backup_scheme_a/` | 方案A (vel_check=-1) | "完成"3年* |
| `backup_scheme_b/` | 方案B (ZYH 15天平滑) | day 417.7 |
| `backup_scheme_c/` | 方案C (崩溃区平滑) | day 424.1 |
| 当前 | 方案D (dt=15s) ✅ | 完成3年 |

**配置备份**:
- [getm.inp.before_stability_fix](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp.before_stability_fix)
- [getm.inp.scheme_a](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp.scheme_a)
- [getm.inp.scheme_c_state](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/getm.inp.scheme_c_state)

---

## 七、关键经验教训

1. **CFL是第一性原理**: 时间步长必须满足全场CFL约束，河流入流口附近是敏感区域
2. **vel_check=-1不可取**: 仅警告模式会掩盖问题，NaN扩散后数据已无价值
3. **流量/地形平滑是治标**: 能延缓崩溃但无法根本解决CFL问题
4. **EFDC '9' cell陷阱**: 不同EFDC文件标记约定不一致，需仔细核对水域cell数量
5. **river_split机制有效**: 同名连续行自动分摊流量，是降低单cell负载的简洁方案
6. **源码级分析必要**: 理解check_3d_fields和vel_check的精确逻辑才能正确诊断
7. **控制变量法有效**: 逐一试验各方案，才能定位根本原因

---

## 八、可视化产出

| 目录 | 内容 | 图数 |
|------|------|------|
| `figures/` | 水动力基础图 | 8张 |
| `figures_3d/` | 3D水动力图 | 8张 |
| `figures_temp/` | 温度专题图 | 6张 |

**可视化脚本**:
- [visualize.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/visualize.py)
- [visualize_3d_full.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/visualize_3d_full.py)
- [visualize_temp.py](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma_EFDC%20trans/visualize_temp.py)

---

*日志生成时间: 2026-07-03*
*当前状态: 方案D稳定运行，纯水动力基线建立完成，可进入WET生态耦合阶段*
