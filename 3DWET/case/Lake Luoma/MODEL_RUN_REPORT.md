# Lake Luoma 模型运行检查报告

> **生成时间**：2026-07-14
> **模型路径**：`C:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma`
> **模拟周期**：2020-01-01 至 2022-12-30（1094 天，共 6,301,440 步）

---

## 一、模型运行状态

### 1.1 当前进度

| 项目 | 值 |
|------|-----|
| 进程状态 | 运行中（PID 537，CPU 100%） |
| 当前进度 | n = 1,599,200 / 6,301,440（**25.4%**） |
| 模拟时间 | 2020-10-04（已运行 277 天） |
| 推进速度 | ~4.5s / 100 步 |
| 预计剩余 | 约 58 小时（约 2.4 天） |
| 错误/警告 | 无（无 NaN、无 crash） |
| 保存事件 | 370 次（每 12 小时一次） |

### 1.2 输出文件状态

| 文件 | 大小 | time 维度 | 状态 |
|------|------|-----------|------|
| `output.nc`（FABM 生态输出） | 4.7 GB | **0** | 数据在内存缓冲 |
| `LUOMAHU_WET.3d.nc`（GETM 3D） | 3.5 GB | **0** | 数据在内存缓冲 |
| `LUOMAHU_WET.2d.nc`（GETM 2D） | 5.2 MB | **0** | 数据在内存缓冲 |

**关键问题**：所有输出文件的 `time` 维度均为 0，尽管已触发 370 次 saving 事件。

**原因**：`output.yaml` 中 `sync_interval: 0`，GETM/FABM 在运行期间不主动将数据同步到磁盘，所有数据在内存缓冲区中，只有模型正常结束（或被 kill）时才会一次性写入。

**影响**：当前无法可视化运行结果（3 年模拟的生态、水动力数据）。`output.nc` 的 4.7 GB 主要是 netCDF4/HDF5 的预分配空间，不含实际数据。

**建议**：
- 方案 A（推荐）：等待模型运行完成（约 58 小时），届时所有数据将写入磁盘
- 方案 B：修改 `output.yaml` 的 `sync_interval` 为非 0 值（如 10），需重启模型（当前进度将丢失）
- 方案 C：用 `kill -SIGUSR2` 触发 GETM 的 sync 信号（如果支持），但风险较高

### 1.3 配置确认

| 配置项 | 值 | 状态 |
|--------|-----|------|
| `getm.inp` timestep | 15.0 s | 满足 CFL |
| `getm.inp` start/stop | 2020-01-01 / 2022-12-30 | 3 年模拟 |
| `gotm_fabm.yaml` ode_method | 1（Forward Euler） | 调试用，生产建议改 10（Patankar） |
| `gotm_fabm.yaml` shade | false | 生物自遮蔽未启用 |
| `getm_fabm.inp` fabm_init_method | 1（从 fabm_init.nc 读取） | 仅含 macrophytes 初始值 |
| `output.yaml` sync_interval | 0（不同步） | 导致无法中途可视化 |

---

## 二、输入数据检查

### 2.1 湖底地形（bathymetry.nc）

| 指标 | 值 |
|------|-----|
| 网格规模 | 44 × 54 = 2,376 个网格 |
| 水域网格（bathy ≥ 0） | 1,198（50.4%） |
| 陆地网格（bathy < 0） | 1,178（49.6%） |
| 水深范围 | 0.65 – 15.86 m |
| 平均水深 | 4.15 m |
| 深水区（≥ 5 m） | 257 个网格（10.8%） |

**评价**：地形数据合理。骆马湖是浅水湖泊，平均水深 4.15 m 符合实际情况。约一半网格是陆地（湖泊边界不规则），水域网格占比 50.4%。

**可视化**：[T01_bathymetry_rivers.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T01_bathymetry_rivers.png)

### 2.2 河流边界条件（rivers.nc）

5 条河流，1096 天（3 年）日数据。每条河流包含流量（m³/s）、温度（°C）、NH4-N、NO3-N、PO4-P。

| 河流 | 网格位置(j,i) | 流向 | 流量范围(m³/s) | 均值(m³/s) | 有效天数 | 问题 |
|------|---------------|------|----------------|------------|----------|------|
| YIHE（沂河） | (50,19-21) | 纯流入 | 0 – 6,180 | 53.19 | 823/1096 | 273 天流量为 0 |
| LUONAN（骆南） | (2,28) | 纯流入 | 0 – 499 | 15.42 | 282/1096 | 814 天流量为 0 |
| DAYUN（大运河） | (31-32,2-3) | 双向 | -127 – 3,580 | 184.39 | 1096/1096 | 正常 |
| ZHANGSHAN（嶂山闸） | (27,41-43) | 纯流出 | -4,320 – 0 | -204.68 | **147/1096** | **949 天流量为 0** |
| YANGHE（仰河） | (28,35) | 纯流出 | -84.9 – 0 | -4.59 | **147/1096** | **949 天流量为 0** |

**发现问题**：

1. **ZHANGSHAN 和 YANGHE 严重数据缺失**：1096 天中仅有 147 天有流量数据（13.4%），其余 949 天流量为 0。嶂山闸是骆马湖的主要出流口，常年有出流，949 天为 0 不合理。这可能导致湖泊水位异常升高（只有流入没有流出）。

2. **YIHE 和 LUONAN 部分缺失**：沂河有 273 天流量为 0，骆南有 814 天流量为 0。沂河作为主要入湖河流，273 天无流量可能不合理。

3. **DAYUN（大运河）正常**：640 天流入 + 456 天流出，双向水流符合运河特征。

**可视化**：
- [T02_river_flow.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T02_river_flow.png)
- [T03_river_nutrients.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T03_river_nutrients.png)
- [T04_river_temperature.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T04_river_temperature.png)

### 2.3 水平衡分析

| 项目 | 3 年总量 | 日均 |
|------|----------|------|
| 河流总流入 | 25.51 km³ | 269.41 m³/s |
| 河流总流出 | 21.37 km³ | 225.68 m³/s |
| **净流入** | **4.14 km³** | **43.73 m³/s** |

**问题**：河流净流入 4.14 km³（流入 > 流出），如果降水和蒸发近似平衡，这 4.14 km³ 将导致水位持续上升。

**降水/蒸发**：
- 降水均值：2.84 mm/day（3.28×10⁻⁸ m/s）
- 蒸发均值：2.51 mm/day（2.91×10⁻⁸ m/s）
- 降水略大于蒸发，净降水约 0.33 mm/day

**水位影响估算**：
- 湖面面积 ≈ 1,198 网格 × 网格面积
- 净流入 43.73 m³/s 对应日均水位上升 ≈ 43.73 × 86400 / 湖面面积
- 如果 ZHANGSHAN/YANGHE 的 949 天零流量是数据缺失（而非真实无出流），则湖泊实际出流被低估，模型中水位可能异常偏高

**可视化**：[T07_water_balance.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T07_water_balance.png)

### 2.4 气象强迫（meteo.nc）

9 个变量，1096 天，44×54 空间网格。

| 变量 | 单位 | 均值 | 范围 | 评价 |
|------|------|------|------|------|
| u10（东西风） | m/s | -0.02 | -5.77 – 4.53 | 合理 |
| v10（南北风） | m/s | 0.43 | -4.20 – 4.92 | 合理 |
| t2（2m 气温） | °C | 15.45 | -10.01 – 34.16 | 合理（骆马湖地区气候） |
| rh（相对湿度） | - | 0.70 | 0.30 – 1.00 | 合理 |
| tcc（总云量） | - | 0.58 | 0.00 – 1.00 | 合理 |
| precip（降水） | m/s | 2.84 mm/day | 0 – 167 mm/day | 合理 |
| evap（蒸发） | m/s | -2.51 mm/day | -6.57 – -0.14 mm/day | 合理（负值=失水） |

**注意**：precip 和 evap 的单位是 m/s（米/秒），GETM 应能正确处理此单位。在可视化脚本中已转换为 mm/day 以便直观显示。

**可视化**：[T05_meteo_overview.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T05_meteo_overview.png)

### 2.5 生态初始条件（fabm_init.nc）

`fabm_init.nc` 仅包含沉水植物（macrophytes）的初始值，其他生态变量（藻类、浮游动物、营养盐等）从 `fabm.yaml` 配置中读取。

| 变量 | 单位 | 最小值 | 最大值 | 均值 | 评价 |
|------|------|--------|--------|------|------|
| macrophytes_sD | gDW/m² | 0.00 | 30.00 | 1.21 | 合理（浅水区高，深水区低） |
| macrophytes_sN | gN/m² | 0.00 | 0.84 | 0.034 | 合理（N/D ≈ 0.028） |
| macrophytes_sP | gP/m² | 0.00 | 0.30 | 0.012 | 合理（P/D ≈ 0.010） |

**可视化**：[T06_macrophyte_init.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T06_macrophyte_init.png)

### 2.6 河流营养盐负荷

| 河流 | NH4-N 均值(mg/L) | NO3-N 均值(mg/L) | PO4-P 均值(mg/L) |
|------|------------------|------------------|------------------|
| YIHE | 0.15 | 1.20 | 0.05 |
| LUONAN | 0.20 | 1.50 | 0.08 |
| DAYUN | 0.25 | 1.80 | 0.10 |
| ZHANGSHAN | 0.10 | 0.80 | 0.03 |
| YANGHE | 0.12 | 0.90 | 0.04 |

**评价**：营养盐浓度在合理范围内。入流河流（YIHE, LUONAN, DAYUN）的营养盐浓度高于出流河流（ZHANGSHAN, YANGHE），符合入流携带污染、出流较清洁的特征。

**可视化**：[T08_nutrient_loads.png](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/T08_nutrient_loads.png)

---

## 三、问题汇总与风险

### 3.1 严重问题

| 编号 | 问题 | 严重程度 | 影响 | 建议 |
|------|------|----------|------|------|
| P1 | ZHANGSHAN/YANGHE 949 天流量为 0 | **高** | 湖泊出流被低估，水位可能异常升高 | 补全河流流量数据，特别是嶂山闸的出流数据 |
| P2 | output.nc time=0，无法中途可视化 | **中** | 无法检查运行中的模型状态 | 等待完成或修改 sync_interval 重启 |
| P3 | `sealevel_check=0` 禁用 NaN 检查 | **中** | 如果出现 NaN 不会被检测 | 建议设为 1，但需重启模型 |

### 3.2 潜在风险

| 编号 | 风险 | 可能性 | 影响 |
|------|------|--------|------|
| R1 | 水平衡异常（净流入 4.14 km³） | 高 | 水位持续上升，可能淹没陆地网格 |
| R2 | ode_method=1（Euler）数值不稳定 | 中 | 生态变量可能出现负值或 NaN |
| R3 | shade=false 无生物自遮蔽 | 中 | 浅水区光照过强，藻类可能过度生长 |

### 3.3 配置建议

1. **当前运行**：保持运行至完成，不要中断（已运行 25.4%，中断将丢失进度）
2. **下次运行建议**：
   - 补全 ZHANGSHAN/YANGHE 的流量数据（最重要）
   - `output.yaml` 设置 `sync_interval: 10`（每 10 天同步一次）
   - `gotm_fabm.yaml` 改用 `ode_method: 10`（Patankar，保正性）
   - `gotm_fabm.yaml` 启用 `shade: true`（生物自遮蔽）
   - `getm.inp` 启用 `sealevel_check=1`

---

## 四、可视化图表清单

所有图表保存在 [figures/run_check/](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/figures/run_check/) 目录：

| 图表 | 文件名 | 内容 |
|------|--------|------|
| T01 | T01_bathymetry_rivers.png | 湖底地形 + 5 条河流位置 |
| T02 | T02_river_flow.png | 5 条河流流量时间序列（蓝=流入，红=流出） |
| T03 | T03_river_nutrients.png | 河流 NH4/NO3/PO4 浓度时间序列 |
| T04 | T04_river_temperature.png | 河流水温时间序列 |
| T05 | T05_meteo_overview.png | 气象数据（风速、气温、降水、蒸发） |
| T06 | T06_macrophyte_init.png | 沉水植物初始生物量（D/N/P） |
| T07 | T07_water_balance.png | 水平衡（总流入 vs 总流出） |
| T08 | T08_nutrient_loads.png | 河流营养盐负荷（kg/day） |
| T09 | T09_run_progress.png | 模型运行进度（n=1,599,200，25.4%） |
| T10 | T10_summary.png | 输入数据统计汇总（箱线图） |

---

## 五、结论

### 5.1 模型运行状态

模型运行正常，无错误，进度 25.4%（2020-10-04），预计 58 小时后完成。但由于 `sync_interval=0`，所有输出文件的 time 维度为 0，无法中途可视化运行结果。

### 5.2 输入数据质量

- **地形数据**：合理
- **气象数据**：合理
- **河流数据**：**存在严重缺失**——ZHANGSHAN（嶂山闸）和 YANGHE（仰河）949 天流量为 0（应有出流），可能导致水平衡异常
- **生态初始条件**：仅有沉水植物，其他从配置文件读取

### 5.3 建议

1. **当务之急**：让模型运行完成，获取完整 3 年输出数据
2. **数据修复**：补全嶂山闸和仰河的出流数据（这是最关键的输入数据问题）
3. **配置优化**：下次运行时启用 sync_interval、Patankar 求解器、生物自遮蔽

---

*报告基于 2026-07-14 17:03 的模型状态和输入数据检查生成。*
