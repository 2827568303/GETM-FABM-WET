# PCLake+Gras 模型公式导出 - 索引与对比指南

**源文件**: `PL613162PLUS_Gras_Mode_order_mass_DC_Run.xls`(PCLake+ v6.13.16, 含草鱼二次开发)
**导出时间**: 2026-07-01
**用途**: 与奥胡斯 FABM-WET 版本 (`3DWET/src/wet/src/fish_pclake.F90` 等) 逐式对比

---

## 文件清单

| 文件 | 大小 | 内容 | 用途 |
|---|---|---|---|
| `equations_by_category.md` | 634 KB | **全部 2669 条方程**,按 80+ 类别分组,含变量名/单位/描述/ACSL 原式 | 人工逐类阅读对比 |
| `equations_all.tsv` | 553 KB | 同上,扁平 TSV(`类别 lId 行号 名称 单位 描述 方程`) | Python/R 程序化 diff |
| `states.tsv` | 19 KB | 全部 136 个状态变量(初值名/状态名/导数名/单位/4 套初值/模块开关) | 状态变量映射 |
| `parameters.tsv` | 43 KB | 全部 621 个参数(名称/单位/范围/4 套值/描述/分组) | 参数映射 |
| `initialstates.tsv` | 12 KB | 全部 190 条初始值计算方程(浓度→质量转换等) | 初始化对比 |
| `gras_only.md` | 20 KB | **仅草鱼模块**:58 条 Gras 定义方程 + 19 处耦合点 | 草鱼移植核心参考 |
| `30_ACSL.txt` | 962 KB | 完整 ACSL 源码(8640 行,含 PROGRAM 结构) | 完整源码备用 |
| `17_Nom.txt` | 4 KB | PCLake 命名规范文档 | 命名查表 |
| `18_sediment_chars.txt` | <1 KB | 5 种沉积物类型参数(Janse 2005) | 沉积物校准 |

---

## PCLake ↔ WET 命名映射规则

PCLake 变量用 `_下划线_` 包裹,WET/FABM 去掉首尾下划线直接作 Fortran 变量名:

| PCLake (Excel) | WET (Fortran) | 说明 |
|---|---|---|
| `_sDGras_` | `sDGras` / `id_sDGras` | 状态变量(state_variable_id) |
| `_dDGras_` | (由 FABM 自动求导) | 导数,WET 中不显式声明 |
| `_tDGrazVegGras_` | `id_tDGrazVegGras` | 诊断变量(diagnostic_variable_id) |
| `_cDCarrGras_` | `cDCarrGras` | 参数,self%cDCarrGras |
| `_kDAssGras_` | `kDAssGras` | 参数 |
| `_aDSatGras_` | (局部变量) | 辅助量,WET 中作 local variable |
| `_uFunTmGras_` | (局部变量) | 导出输入量,WET 中作 local variable |

**鱼类命名对照**(PCLake 已有 ↔ WET 已有,可作为草鱼移植模板):
- `_sDFiJv_` ↔ `id_FiJu_D`  (注意 WET 把元素后缀放后面:D/P/N)
- `_sDFiAd_` ↔ `id_FiAd_D`
- `_sDPisc_` ↔ (PiscFish 在 WET 中)
- `_sDGras_` ↔ **需新增** `id_Gras_D` 或 `id_sDGras`

**关键差异**:WET 的 fish_pclake.F90 把 JuFish/AdFish 用数组分 size class,变量名元素后置(`FiJu_D` 而非 `sDFiJv`)。草鱼移植时需决定:沿用 WET 风格命名 `Gras_D`,还是保持 PCLake 风格 `sDGras`。建议沿用 WET 风格保持一致。

---

## ACSL ↔ Fortran 语法映射

| ACSL (PCLake) | Fortran (WET) |
|---|---|
| `_IF_ cond _THEN_ a _ELSE_ b _ENDIF_` | `merge(a, b, cond)` 或 `if/else` |
| `_IF_ cond1 _THEN_ a _ELSEIF_ cond2 _THEN_ b _ELSE_ c _ENDIF_` | 嵌套 `if/else if/else` |
| `_POW_(x, y)` | `x**y` |
| `_EXP_(x)` | `exp(x)` |
| `_MAX_(a, b, c)` | `max(a, b, c)` |
| `_MIN_(a, b, c)` | `min(a, b, c)` |
| `_COS_(x)` | `cos(x)` |
| `_SQRT_(x)` | `sqrt(x)` |
| `_LOG_(x)` | `log(x)` |
| `_EQ_` | `==` |
| `_NE_` | `/=` |
| `_GT_` / `_LT_` / `_GE_` / `_LE_` | `>` / `<` / `>=` / `<=` |
| `_AND_` / `_OR_` / `_NOT_` | `.and.` / `.or.` / `.not.` |
| `_TRUE_` / `_FALSE_` | `.true.` / `.false.` |
| `_time_` | 由 FABM 框架传入 |
| `_Pi_` | `pi`(WET 已定义) |
| `_NearZero_` | `near_zero`(WET 已定义) |

---

## 单位转换要点(关键!)

PCLake 是**0 维/垂向分层**模型,通量以**单位面积**计;WET/FABM 是 **3D** 模型,以**单位体积**计:

| 量类 | PCLake 单位 | WET 单位 | 转换 |
|---|---|---|---|
| 状态变量(浓度型) | g/m² | g/m³ | ÷ 水层深度 `_uDepthWEpi_`/`_uDepthWHyp_` |
| 面积通量 t- | g/m²/d | g/m³/s | ÷ 深度 ÷ 86400 |
| 体积通量 w- | g/m³/d | g/m³/s | ÷ 86400 |
| 速率 k- | d⁻¹ | s⁻¹ | ÷ 86400 (WET 用 `scale_factor=1.0_rk/secs_pr_day`) |

WET 的 `get_parameter` 调用中常见 `scale_factor=1.0_rk/secs_pr_day` 就是做这个 d⁻¹→s⁻¹ 转换。

**草鱼特例**:PCLake 中 `_sDGras_` 单位是 gDW/m²(底层状态变量,bottom_state)。WET 中对应应为 `type_bottom_state_variable_id`,FABM 会自动处理深度积分,无需手动除深度。

---

## 推荐对比工作流

### 第一步:状态变量映射
打开 `states.tsv`,筛选 `_InclWeb_` 列为 1 的 20 个食物网状态变量,与 WET `fish_pclake.F90` 的 `id_*` 声明逐个对应。草鱼(`_sDGras_` lId=134)在 WET 中无对应——这是移植缺口。

### 第二步:参数映射
打开 `parameters.tsv`,筛选 group 列含 "Fish" 或 "Gras" 的参数,与 WET `fish_pclake.F90` 的 `get_parameter` 调用对比。19 个 Gras 参数(见 `gras_only.md` 顶部表)在 WET 中均需新增。

### 第三步:方程逐类对比
按 `equations_by_category.md` 的类别顺序对比。建议优先级:
1. **Gras_fish_processes**(52 条)— 草鱼核心,WET 完全缺失,需移植
2. **Fish_processes_of_adult_fish / young_fish**(16+14 条)— 与 WET `fish_pclake.F90` 对比,确认基础鱼类的公式一致性
3. **Pisc_fish_processes**(62 条)— 凶猛鱼,与 WET 对比
4. **Vegetation_processes**(205 条)— 草鱼牧食耦合点 `_tDGrazVegGras_` 在此
5. **Total_fluxes_to/from_other_components**(75 条)— 草鱼对系统营养盐的耦合在此
6. **Mass_balance**(25 条)— 验证质量守恒一致性

### 第四步:程序化 diff
用 `equations_all.tsv` 加载到 pandas,按类别分组,与从 WET Fortran 源码解析出的方程做自动比对(变量名归一化后字符串匹配)。

---

## 草鱼模块移植 checklist

基于 `gras_only.md`,移植到 WET 需:
- [ ] 新增 bottom state: `Gras_D` / `Gras_P` / `Gras_N`(对应 `_sDGras_`/`_aPGras_`/`_aNGras_`)
- [ ] 新增 19 个参数(见 `gras_only.md` 参数表)
- [ ] 实现 52 条 Gras 方程(温度函数→食物限制→同化→摄食→呼吸→死亡→迁移→捕捞)
- [ ] 耦合到植被模块:`_tDGrazVegGras_` → WET 植被 DW/P/N 损失通量
- [ ] 耦合到水体碎屑:`_tDEgesGras_`/`_tDMortGrasDet_` → WET detritus 通量
- [ ] 耦合到水体营养盐:`_tPExcrGras_`/`_tPEgesGrasPO4_`/`_tPMortGrasPO4_` → PO4;`_tNExcrGras_`/`_tNEgesGrasNH4_`/`_tNMortGrasNH4_` → NH4
- [ ] 骨骼沉出:`_tDMortGrasBot_`/`_tPMortGrasBot_`/`_tNMortGrasBot_`(永久移出)
- [ ] 分层分配开关 `_fGras*Hyp_`(WET 若不分层可简化)
- [ ] 质量平衡验证:`_aDTotT_`/`_aPTotT_`/`_aNTotT_` 含 `_aDGras_`/`_aPGras_`/`_aNGras_`
