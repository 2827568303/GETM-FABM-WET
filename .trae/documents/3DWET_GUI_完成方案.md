# 3DWET 模型 GUI 完整开发方案

## Context（背景与目标）

用户需要为 3DWET 模型（GETM-FABM-WET 水生态耦合模型）开发一个 EFDC Explorer 级别的 Web GUI，覆盖从输入数据导入到自动率定的完整建模工作流。Lake Luoma 案例由于 `output.yaml` 中 `sync_interval: 0` 导致 3 个月模拟的全部输出数据丢失（time 维度为 0），因此本方案优先修复配置链路，并以 Theoretical lake 案例（已验证含 4 个时间步有效输出）作为可视化与率定功能的开发基线。

现状：`c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\` 下已有 Flask Web GUI 骨架（11 个导航页面、30+ 后端 API、689 行前端 JS），约 70% 架构已搭好，但多处功能为 stub。本方案的目标是补全 stub、扩展 3D 可视化与率定能力，**不重写已有可用代码**。

## 技术选型（已定）

| 维度 | 选择 | 理由 |
|---|---|---|
| 框架 | 扩展现有 Flask Web GUI | `app/` 已有 70% 骨架，复用最大化 |
| 3D 可视化 | Plotly.js（CDN 加载） | MIT 协议、纯前端、与现有 Chart.js 共存 |
| 自动率定 | pyabc（主）+ scipy.optimize（基线） | 均为 BSD/MIT、纯 Python、本地运行 |
| 部署 | 本地 Flask（`flask run`） | 数据不离本地、无云依赖 |

## 架构总览

### 复用（不改动）
- `app/server.py`（976 行）：现有 30+ API 端点，关键可复用函数：
  - `parse_getm_inp` (L116-150)：解析 GETM namelist
  - `parse_fabm_yaml` (L211-266)：解析 FABM 模块、参数、耦合关系
  - `update_fabm_parameter` (L268-279)：外科手术式 yaml 参数修改
  - `get_2d_field` (L314-347)：2D 变量场提取（支持 3D/4D 变量）
  - `get_timeseries` (L349-405)：**已支持 point/region/lake-avg 三种模式**
  - `find_output_files` (L283-292)：自动发现输出文件
  - `estimate_run_time` (L417-448)：经验式运行时间估算
  - `run_model_thread` (L450-510)：WSL 子进程 + 日志轮询
- `app/static/js/app.js`（689 行）：路由 `navigate()`、XHR 辅助 `api()`、`drawHeatmap`/`heatColor`/`drawColorbar` 全部可复用
- `app/templates/index.html`（446 行）：11 个页面容器已就位
- `app/data/calibration_points.json`、`calibration_data.json`：schema 已定义
- `scripts/visualize.py` (L53-68 `get_depth_avg`/`get_surface`/`get_bottom`)：sigma 层加权平均参考实现

### 新增文件
| 路径 | 职责 |
|---|---|
| `app/calibration.py` | `CalibrationEngine` 抽象基类 + `PyabcEngine` + `ScipyEngine` + 度量函数 + 合成观测数据生成器 |
| `app/static/js/viz3d.js` | Plotly.js 3D 表面/切片/体渲染（仅 viz3d 页加载，保持主 bundle 小） |
| `app/static/js/calibration_metrics.js` | RMSE/NSE/R²/PBIAS 计算 + 散点图绘制（纯 JS，无依赖） |

### 编辑文件
| 路径 | 改动范围 |
|---|---|
| `app/server.py` | 新增约 8 个 API 端点（不重写现有代码） |
| `app/static/js/app.js` | 替换 3 处 stub（输入数据 L139、模块开关 L172-174、自动率定 L647-676），扩展 `pollRunStatus` 加 ETA 通知 |
| `app/templates/index.html` | 新增 Plotly CDN 引用、ETA 横幅、文件上传控件、多边形选区 canvas 叠加层、状态变量小图网格 |

## 阶段划分

### Phase 1 — 配置与运行完善（让模型能正确跑起来）

**目标**：补全配置链路 stub，修复 `sync_interval=0` 数据丢失类问题。

**改动清单**：

1. **真实输入数据导入** — 替换 `app.js` L139 的 `Math.random()` stub：
   - 新增 `GET /api/case/inputs` 端点（server.py）：遍历活动案例目录，对每个输入文件返回 `{name, exists, size_bytes, mtime, n_vars (NC 文件)}`，NC 文件用 `netCDF4.Dataset` 计数变量数
   - 前端渲染真实存在性/大小/修改时间

2. **模块启用/禁用** — 替换 `app.js` L172-174 的 `alert` stub：
   - 新增 `POST /api/config/fabm/module` 端点：接收 `{module, enabled}`，禁用时将实例移至 `fabm.yaml` 顶层 `_disabled` 键（保留配置，可恢复），启用时还原
   - 修改 `parse_fabm_yaml` (L249)：从 `instances` vs `_disabled` 推导 `enabled` 字段
   - 耦合保护：禁用前检查 `has_coupling` 标志，若其他启用模块引用则警告

3. **参数编辑器打磨**（已可用，L218-231）：
   - 增加 dirty-flag（输入值与已保存值不同时高亮）
   - 增加"恢复默认值"按钮（默认值快照存于 `app/data/fabm_defaults.json`，首次加载时生成）
   - 暴露参数注释（YAML 已解析，仅需透传 `comment` 字段）

4. **冷热启动**：已工作（app.js L243-280、server.py L619-641），仅验证。

5. **运行时间提醒** — 扩展 `pollRunStatus` (app.js L300-338)：
   - 当 `s.eta_minutes` 跨越阈值（5/15/60 分钟）时触发浏览器原生 `Notification`
   - 状态翻转为 `completed`/`failed` 时同样通知
   - 后端已在 L700-710 返回 `eta_seconds`/`eta_minutes`

6. **修复 `output.yaml` sync_interval=0 类问题**：
   - 新增 `GET/POST /api/config/output` 端点
   - 保存时校验 `sync_interval > 0`，违规返回 400 + 明确错误信息
   - `load_case` (L538-564) 加入一次性 sanity check：检测到 `sync_interval: 0` 时在加载 toast 中提示并提供"一键修复"按钮

**Phase 1 验证**（无需跑模型）：
- 加载 Lake Luoma：输入页显示 `bathymetry.nc` 真实存在、67KB、2026-06-30 修改时间
- 禁用 `macrophytes` 模块 → 重新加载案例 → 确认已不在 `instances` 中
- POST `sync_interval: 0` → 期待 400 响应

### Phase 2 — 可视化完善

**目标**：让用户能完整看到模型输出（2D 场、3D 体、时间序列、状态变量），并以 Theoretical lake（4 时间步有效输出）为验证基线。

**改动清单**：

1. **2D 场视图增强** — 扩展 `updateViz2d` (app.js L389-401)：
   - 时间滑块（已存在于 index.html L262，需更新 `max`）
   - 层选择器（3D 变量时显示）：动态填充 `viz2d-level`（index.html L265），基于 `state.variables3d.find(v => v.name === currentVar).ndim === 4`
   - 点击单元格提取时间序列：canvas click → 计算 (i,j) → 调用 `extractTimeseries`

2. **3D 视图** — 新建 `app/static/js/viz3d.js`：
   - `renderSurface(varName, timestep)`：Plotly surface（湖泊表面变量场）
   - `renderSlice(varName, timestep, axis)`：xz / yz 平面切片
   - `renderVolume(varName, timestep)`：Plotly isosurface，服务端降采样至 30³ 防止浏览器 OOM
   - 用 Plotly 暗主题匹配现有 CSS

3. **时间序列三种模式**：
   - 网格点：已工作（app.js L504-529）
   - 区域：viz2d canvas 上多边形选区（用户点击 3+ 点）→ 服务端计算多边形覆盖单元格均值
   - 全湖平均：已实现于 `get_timeseries` (server.py L378, L388)
   - 新增 `POST /api/results/timeseries_polygon` 端点（或扩展现有端点加 `polygon` 参数）

4. **状态变量实时视图** — 扩展 `loadDashboardSummary` (app.js L369-381)：
   - 新增 `GET /api/results/state_vars` 端点：返回最近时间步 6 个关键变量的表面场（temp、NO3、PO4、O2、chla、POM）
   - Dashboard 渲染 6 个 mini-heatmap（每个 100×80 canvas）网格，复用 `drawHeatmap`

**新依赖**：
- Plotly.js（CDN，无安装）：`<script src="https://cdn.plotly.com/plotly-2.35.2.min.js"></script>` 加入 `index.html`

**Phase 2 验证**：
- 加载 Theoretical lake：选择 `temp` 变量，2D heatmap 显示真实场（非零）
- 点击单元格 (12,10)：时间序列图更新
- 切到 3D 页：Plotly 渲染交互式表面
- 多边形选 4 个单元格：时间序列更新
- Dashboard：6 个 mini-heatmap 显示真实 min/max/mean

### Phase 3 — 率定完善

**目标**：完整率定工作流（点位添加、实测导入、模拟-实测对比、自动/手动率定）。

**改动清单**：

1. **率定点位添加**：
   - viz2d canvas 上叠加透明层，点击存储 (i,j)，弹出对话框输入名称 + 选择率定变量
   - 替换 `index.html` L430-432 的手动 i,j 输入

2. **实测数据导入**：
   - 新增 `POST /api/calibration/upload` 端点：用 `openpyxl`（已装 3.1.5）解析 `.xlsx`，或 stdlib `csv` 解析 `.csv`
   - 期望列：`time, value`，按 `(point_id, variable)` 存入 `calibration_data.json`

3. **变量选择器** — 替换 `index.html` L433 的 comma-separated 文本为 multi-select dropdown，数据源为 `state.variables3d`

4. **实测-模拟对比** — 扩展 `updateCalComparison` (app.js L581-612)：
   - 现有双线时间序列图保留
   - 新增散点图（sim vs obs + 1:1 参考线）
   - 用 `calibration_metrics.js` 计算并显示 RMSE、NSE、R²、PBIAS（纯 JS，无依赖）

5. **手动率定**：
   - 工作流已隐式可用（Phase 1 改参 → Phase 1 重启 → Phase 3 对比）
   - 率定页加"运行模型后对比"按钮，编排此序列

6. **自动率定引擎** — 新建 `app/calibration.py`：
   ```python
   class CalibrationEngine(ABC):
       def run(self, params, prior, objective_fn, n_iterations, callback): ...
       def status(self): ...

   class ScipyEngine(CalibrationEngine):  # 基线，scipy 1.12.0 已装
       def run(self, ...): scipy.optimize.minimize(method='L-BFGS-B', bounds=...)

   class PyabcEngine(CalibrationEngine):  # 主选，需 pip install pyabc
       def run(self, ...): pyabc.ABCSMC(model, prior, distance).run(...)
   ```
   - 距离度量：所有 (point, variable) 对的加权 RMSE
   - 模型包装：复用 `update_fabm_parameter` 写参数 → 复用 `run_model_thread` 模式跑模型 → 复用 `get_timeseries` 提取模拟序列
   - pyabc 懒导入：未安装时 fallback 到 ScipyEngine + 前端 toast 提示

7. **自动率定 UI** — 替换 `app.js` L647-676 的 stub：
   - `startAutoCal` POST 到真实 `/api/calibration/auto/start`，返回 job_id
   - 新增 `GET /api/calibration/auto/status?job_id=...` 轮询端点
   - 完成时渲染最佳参数 + 收敛曲线

**新依赖**：
- `pyabc`（BSD-3-Clause）：`pip install pyabc`，主选贝叶斯 ABC-SMC 引擎
- `scipy`（BSD，已装 1.12.0）：基线优化器
- `openpyxl`（MIT，已装 3.1.5）：读 `.xlsx` 实测数据

**Phase 3 验证**：
- 在 viz2d 上点击添加率定点 → 出现在率定表中
- 上传由 Theoretical lake 输出加噪声生成的 CSV → 实测序列入库
- 加载对比：显示 RMSE/NSE/R²/PBIAS 值 + 散点图
- 在 Theoretical lake 上跑 scipy 10 次迭代（2 参数：`diatoms.cMuMax`、`POM.kDMinW`）：5 分钟内完成
- 不安装 pyabc 时：UI 显示明确"使用 scipy 替代"消息

## 关键复用函数清单（路径引用）

| 复用函数 | 路径 | 用于 |
|---|---|---|
| `parse_getm_inp` | `app/server.py` L116-150 | 任意 getm.inp 读取 |
| `parse_fabm_yaml` | `app/server.py` L211-266 | 模块/参数解析 |
| `update_fabm_parameter` | `app/server.py` L268-279 | 率定引擎写参数 |
| `get_2d_field` | `app/server.py` L314-347 | 2D 可视化、3D 切片 |
| `get_timeseries` | `app/server.py` L349-405 | 率定模拟序列提取 |
| `estimate_run_time` | `app/server.py` L417-448 | ETA 通知 |
| `run_model_thread` | `app/server.py` L450-510 | 率定引擎子进程模式 |
| `drawHeatmap` / `heatColor` / `drawColorbar` | `app/static/js/app.js` L403-451 | 所有热力图 |
| `get_depth_avg` / `get_surface` / `get_bottom` | `scripts/visualize.py` L53-68 | sigma 层加权平均（如需移植到服务端） |

## 依赖确认

| 包 | 协议 | 状态 | 用途 |
|---|---|---|---|
| `pyabc` | BSD-3-Clause | `pip install pyabc` | 主选 ABC-SMC 自动率定 |
| `scipy` | BSD | 已装 1.12.0 | 基线 L-BFGS-B 优化 + 度量函数 |
| `openpyxl` | MIT | 已装 3.1.5 | 读 `.xlsx` 实测数据 |
| `plotly.js` | MIT | CDN，无安装 | 3D 表面/isosurface 渲染 |
| `netCDF4` | MIT | 已装 1.7.1 | 服务端 NC 文件读取 |
| `numpy` | BSD | 已装 | 数值计算 |

无付费依赖。Plotly 虽从 CDN 加载，但**纯前端渲染，数据不离开浏览器**，符合"数据本地"约束。

## 风险与缓解

| 风险 | 缓解措施 |
|---|---|
| Lake Luoma 输出全丢（time=0） | Phase 2/3 验证改用 Theoretical lake（4 时间步有效输出）；`app/calibration.py` 内置合成观测数据生成器（从模拟输出加噪声），无模型也能测率定 UI |
| `fabm.yaml` 禁用模块可能破坏耦合 | 禁用前服务端检查 `has_coupling` 标志（L226 已解析），若其他启用模块引用则警告 |
| pyabc 未安装 | 懒导入 + fallback 到 `ScipyEngine` + 前端 toast 明确提示 |
| Plotly 大 3D 数组致 OOM | `/api/results/3d_volume` 端点服务端用 `np.linspace` stride 降采样至 ≤40³ 单元格 |
| 多次率定子进程并发 | 串行通过现有单 `run_process` 槽（server.py L75）；拒绝并发运行请求 |

## 验证矩阵（无需跑 Lake Luoma 模型）

| Phase | 测试项 | 方法 |
|---|---|---|
| 1 | 输入数据真实显示 | 加载 Lake Luoma，确认 `bathymetry.nc` 行显示 67KB / 2026-06-30 |
| 1 | 模块开关持久化 | 禁用 `macrophytes` → 重载 → 确认已移出 `instances` |
| 1 | output.yaml 校验 | POST `sync_interval: 0` → 期待 400 |
| 2 | 2D 热力图真实数据 | 加载 Theoretical lake，选 `temp`，看到真实场（非零） |
| 2 | Plotly 3D 渲染 | 切到 viz3d，看到交互式表面 |
| 2 | 点击单元格 → 时间序列 | 点击 (12,10)，图表更新 |
| 2 | 状态变量仪表盘 | Dashboard 显示 6 个 mini-heatmap，含真实 min/max/mean |
| 3 | 点击添加率定点 | 点击 viz2d 单元格，率定表新增一行 |
| 3 | Excel 上传 | 上传由 Inputs.xlsx 派生的 CSV，实测序列入库 |
| 3 | 度量计算 | 加载对比，看到 RMSE/NSE/R²/PBIAS 数值 |
| 3 | scipy 自动率定 | 在 Theoretical lake 跑 10 次迭代，5 分钟内完成 |
| 3 | pyabc 优雅降级 | 不装 pyabc 时，UI 显示明确"使用 scipy"消息 |

## 实施顺序

1. **Phase 1**（约 8 处编辑）：补 stub、修 sync bug、加 ETA 通知 → 用户可正确配置并启动一次完整模拟
2. **Phase 2**（约 6 处编辑/新增）：完善 2D、加 3D Plotly、扩展时间序列、加状态变量视图 → 用户能完整看到结果
3. **Phase 3**（约 7 处编辑/新增）：率定点、实测导入、对比图、scipy + pyabc 引擎 → 完整率定工作流

每个 Phase 完成后用上表对应行验证，确认无 regression 再进入下一 Phase。

## 关键改动文件

- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\server.py`（编辑：新增端点，不重写）
- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\static\js\app.js`（编辑：替换 stub）
- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\templates\index.html`（编辑：加 Plotly/控件/横幅）
- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\calibration.py`（新建）
- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\static\js\viz3d.js`（新建）
- `c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\app\static\js\calibration_metrics.js`（新建）
