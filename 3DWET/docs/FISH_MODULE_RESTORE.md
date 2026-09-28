# 鱼类模块缺失排查与修复报告（2026-09-24）

## 1. 结论速览

| 检查项 | 结果 |
|---|---|
| 鱼类源码是否编译进程序 | ✅ 是。`src/wet/src/fish.F90` / `fish_pclake.F90` 在 `src/wet/src/CMakeLists.txt` 中，`wet_model_library.F90` 注册 `wet/fish`，`bin/getm_cartesian.exe` 含该模块 |
| 上游参考配置是否有鱼 | ✅ 有。`src/wet/testcases/fabm-wet.yaml` 含 JuFish / AdFish / PiscFish 三个实例 |
| 项目 4 个案例是否有鱼 | ❌ **全部没有**（Lake Dianchi 17 实例、Lake Luoma / NativeTest / Theoretical lake 各 15 实例，均无 `wet/fish`） |
| GUI 是否能开鱼类 | ❌ 之前不能（无开关）。现已新增「🐟 鱼类」引擎开关 |

## 2. 为什么会缺鱼 —— 根因链

1. **历史 bug**：`wet_fish.F90` 旧版注册了 `id_time_step` 依赖，宿主链接的是悬垂指针，
   一旦鱼模块激活就 SIGSEGV（`docs/DEBUG_HISTORY_REPORT.md` §4.4）。
2. **当时的绕行方案**：`remove_fish.py` 把 fabm.yaml 里三个鱼实例全部删掉，
   得到 `fabm_foodweb_working.yaml`（见 `scripts/data_gen/create_working_foodweb.py`、
   `create_foodweb_config.py`，两脚本都写死 `FISH_MODULES = ['JuFish','AdFish','PiscFish']` 并删除）。
3. **污染扩散**：所有案例的 fabm.yaml 都由这份"无鱼"配置派生；
   GUI 建案例用的模板是 `case/Lake Luoma/fabm.yaml`（`case_build()` 第 4 步直接 `shutil.copy2`），
   于是**新建的案例天生没有鱼**。
4. **GUI 侧**：`ENGINE_CATALOG` 只有 hydro / eco / ghg 三张卡片，`MODULE_CATEGORIES`
   也没有 JuFish / AdFish / PiscFish —— 即使 fabm.yaml 里有鱼，也只能显示为"未分类"。

> 现在 `fish.F90` 已无任何 `time_step` 依赖（补丁 `patches/fish_v2_patched.F90` 已并入源码，
> `grep -n time_step src/wet/src/fish.F90` 为空），**当年的崩溃原因已不存在**，可以安全启用。

## 3. 修复内容

### 新增文件
- `app/fish_support.py` —— 鱼类实例的读取 / 按案例食物网重映射猎物 / 增删。
- `model_builder/templates/fish_instances.yaml` —— 标准三段鱼实例（源自上游 fabm-wet.yaml，
  已按本机 `fish.F90` 校正：删除源码中不存在的 `prey_suffix1/2` 参数）。

### GUI（app/server.py + app.js + index.html）
- `ENGINE_CATALOG` 新增 `fish`（🐟 鱼类），`MODULE_SELECTION_DEFAULT` 默认 **开**；
  `MODULE_ENGINE_KEYS = (hydro, eco, fish, ghg)`。
- `/api/config/modules` GET 返回鱼开关（取自案例 fabm.yaml），POST 可一键增删三个鱼实例；
  生态引擎关闭时鱼自动关闭。
- `case_build()` 按选择注入/清除鱼实例，并把 `fish` 记入 `initial_conditions.json`。
- `MODULE_CATEGORIES` 增加 `JuFish / AdFish / PiscFish → 鱼类`。
- 术语表 `app/fabm_glossary.json` 增加三个模块说明 + fVul/sFRes/sDSiz + 46 个鱼类参数中文名。
- `app/fabm_docs.json` 重新提取（此前**漏了** `wet/fish`），现含 7 个变量 / 121 个参数英文原文与单位。
- 前端确认弹窗增加鱼类说明；静态资源版本 `app.js?v=18` / `style.css?v=10`。

### 源码小修
- `src/wet/src/fish.F90`：`sC` 状态量单位 `gN/m3` → `gC/m3`（笔误；下次重新编译时输出到 nc 的属性才更新）。

### 滇池案例（case/Lake Dianchi）
| 文件 | 改动 | 备份 |
|---|---|---|
| `fabm.yaml` | 注入 JuFish/AdFish/PiscFish（17→20 实例） | `fabm.yaml.nofish.bak` |
| `getm.inp` | `timestep 30 → 25` | `getm.inp.dt30.bak` |
| `output.yaml` | 改为 `source: *` | `output.yaml.ghglist.bak` |

## 4. 顺带查出的两个"案例根本起不来"的阻塞点

### 4.1 CFL：`timestep = 30` + `check_cfl = .true.` 必崩
```
FATAL ERROR: reduce time-step (30.0) below 28.676095620462544
```
GETM 用严格 2D 对角 CFL：`dt_max = Δx·Δy/(√2·c·√(Δx²+Δy²))`，滇池 dx=dy=500 m、H_max=7.7477 m
→ dt_max ≈ 28.68 s。全年那次成功运行用的是 `check_cfl=.false.`（日志中无 CFL 段），
之后被改成 `.true.` 却没有配套降 dt。已改为 **dt=25（Co≈0.87）**。

### 4.2 `output.yaml` 的 FABM 通配订阅：最后一条必然失败
```
collect_from_categories: No variables have been registered under output category "methane". STOP 1
```
实测规律（三次对照）：**列表里最后一条 FABM `X/*` 订阅一定 fatal**——
删掉 `methane/*` 后失败点前移到 `inorganic_carbon/*`，再删又前移到 `macrophytes/*`。
目前唯一实测可用的写法是 `source: *`（全年成功运行也是这么配的）。
若要精简输出体积，请用**显式变量名**（如 `methane_sCH4W`）而不是 `X/*`。

## 5. 实跑验证

`case/_fish_probe`（滇池输入 + 鱼 + dt=20，2020-01-01→01-03，8640 步）：

- `getm: Completed on 20260924 160340.409`，**0 FATAL / 0 SIGSEGV / 0 越界**；
- 输出 126 个鱼类变量（`JuFish_sD/sP/sN/sC/fVul/Bioturbation` …）；
- 两天内生物量平稳、无发散：
  JuFish `sD` 0.2519 → 0.2531，AdFish 0.9939 → 0.9891，PiscFish 0.0696 → 0.0693 gDW/m³。

滇池新配置（`dt=25 + source:* + 鱼`）1 小时探针同样 0 FATAL 正常收尾。

## 6. 怎么关回去 / 怎么给别的案例开

- GUI：左侧「模型模块」页 → 🐟 鱼类 卡片，一键开关（改的是案例 fabm.yaml）。
- 脚本：
  ```python
  import sys; sys.path.insert(0, "app")
  import fish_support as fs
  fs.toggle_fish_modules("case/Lake Luoma/fabm.yaml", True)   # False = 移除
  ```
- 猎物会自动按案例实际实例名重映射：JuFish→浮游动物（copepods/cladocerans）、
  AdFish→底栖动物（zoobenthos）、PiscFish→JuFish+AdFish；浮游动物不足 2 个时 `nPLAN` 自动降为 1。

## 7. 待清理

`case/_fish_probe`（259 MB）、`case/_dc_verify`（48 MB）是本次验证用的临时案例，可自行删除。
