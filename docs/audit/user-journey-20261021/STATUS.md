# 用户流程与学术案例证据状态

更新日期：2026-10-26（Asia/Shanghai）

### 2026-10-26 Sol 高｜v140 水体显示与全量 UI 测试验收进展

- **实测（浏览器/UI）**：桌面浏览器刷新到 v140 后，Lake Dianchi 的静态水深投影可见，包含水深色标、湿网格岸线和等深线；湖底填充默认隐藏。该案例无输出文件，播放控件禁用；这是静态预览可见的验证，不能称为动态模型结果或完整工作流通过。
- **代理（显示与色标回归）**：粗湿网格边缘仅在湿单元内做显示羽化，不改变水体掩膜、原水深数据或几何；静态水深色面使用有效用户色标范围，避免色条与实际映射不一致；水深 hover 补上横向坐标。聚焦 3D 回归 **82/82**，Lake display mesh **57/57**，render 与 geometry 独立脚本通过。v140 资源 SHA-256 与本地源码一致：`3EDB4AA80A7E52945606D527644D06CFE42904815ECFFF852FDAAF57ADAA7CF3`。
- **实测（Python suite）**：复跑为 **888 passed、5 skipped、4 subtests passed**。4 个跳过项为当前 Windows symlink 权限限制，1 个跳过项为缺少 `wet_utility.mod` 编译依赖；这些项未验收。
- **代理（全量 JavaScript suite）**：Sol 高独立复跑 `3DWET/tests/run-js-tests.ps1` 退出码 0；覆盖 `3DWET/tests` + 仓库根 `tests/` 共 **109/109 个文件通过**，41 个 `node:test` 文件 **438/438 cases**，68 个 standalone 脚本全部通过。根 `tests/` 单独复跑 8/8 文件，43/43 个 node:test cases 与 standalone 脚本通过。自动化不是浏览器所有操作的实测，也不是原生 solver 科学验证。
- **未完成（地理岸线）**：湿网格约 82×41，无权威高分辨率岸线数据。v140 柔化仅改善像素阶梯，不能恢复真实地理细节或称为测绘边界。需要来源、版本、坐标系和许可明确的岸线/更细测深输入。
- **未完成（求解器/案例）**：本机缺少 gfortran/ifx/ifort/CMake/Ninja，未能将当前 Fortran 修改构建进 solver；案例没有动态输出，Erken、Lake Ravn、Bryrup、Arreskov 科学验证按既有证据仍分别保持代理/未完成状态，见各案例条目。本轮不升级其状态。
- **总体验收**：v140 静态水体显示、床面隐藏与完整 JavaScript 自动化套件已核验；Python suite 为 **888 passed / 5 skipped / 4 subtests passed**。完整端到端用户流程、动态求解器构建/运行、四湖科学验证、权威岸线仍未完成，不能交付为全部科学验收通过。参考图路径仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-26 Sol 高｜v136 水体视图同步与形态复核

- **实测（浏览器/UI）**：桌面本地应用已加载 3D 可视化页。Lake Dianchi 显示非矩形的湖区深度投影、湿网格岸线、等深线与邻岸示意；当前是静态地形，时间播放禁用，不能据此声称动态水体已经运行或完整流程已跑通。显示侧壁来自原湿网格边界，在静态高垂向倍率下为半透明显示专用几何；床面仍默认隐藏。
- **实测（岸线证据边界）**：工作目录中的 Lake Dianchi 案例数据不含配套矢量岸线；当前 82×41 bathymetry 湿网格确定的是采样边界。截图可见其非矩形地理轮廓，但边界细节受原始网格限制；平滑仅改善显示线，不能称为高精度或实测岸线。需要带出处的高分辨率岸线矢量/网格与坐标系才能进一步塑造真实细节。
- **代理（渲染回归）**：水体显示两组 Node 定向测试合计 **73/73 通过**，包含 VE=300 静态侧壁及湿网格几何约束；`node --check`、`git diff --check` 通过。该自动化结果不是湖泊科学验证。
- **代理（食性网络与模型源回归）**：PISC `pred_dummy` 消费依赖改为与生产端一致的无量纲单位，同步食性网络目录/单位校验；合法 PISC 网络与错误单位拒绝的定向验证共 21 项通过，相关浏览器端 Node 套件 2 项通过。底栖冷初始化镜像探针 10 项通过；四个 Droop 限制因子边界测试 2 项及 4 子项通过。原生 GETM 未重编译，不能将这些源级结果当作生产 solver 验证。
- **实测（全量 Python 自动化回归）**：集成后的最终源码复跑 suite 为 **878 passed / 10 failed / 5 skipped / 4 subtests passed**，日志 `C:\Users\23801\AppData\Local\Temp\GETM-FABM-WET-260928-pytest-integrated-final.log`。剩余失败包括 5 项 GETM solver 的 measured SWR opt-in/读取/时间插值/值校验契约（生产 solver 尚未实现此路径）、1 项零生物量源契约测试、2 项没有执行真实 FABM 调度的水草 probe、2 项 stub 顺序与生产 RHS 流程不符的诊断 probe；后四类未以盲改生产方程的方式消除。native fish probe 因缺少 `wet_utility.mod` 被跳过。该回归明确未全绿，不能作为全应用验收通过。
- **实测（桌面源同步）**：health 返回 `ready=true`，`model_root` 为当前工作区；HTML 使用 `viz3d.js?v=136`，HTTP 返回脚本 SHA-256 与工作区脚本一致（`1C8104729588A68FC53C592DD98711ACA994E12BB79234AB435407E5176DC2A5`）。
- **代理（启动身份修复）**：针对共享 `WET_CASE_STATE_DIR` 的已复现候选冲突，`ModelRootLease` 保持旧 `.studio-runtime` 注册兼容；若锁记录属于另一个 model root，则该新根回退到按规范化 model path 哈希隔离的 `models/<key>` registry。定向 runtime 测试 **5 passed**。这降低共享目录冲突风险，但历史用户截图的具体环境仍未取得，不能称为唯一根因已证实。运行中的服务 PID 36700 仍为补丁前进程；自动审批拒绝了停止该 idle 服务以执行重启，因此新版 launcher 运行态同步尚未验证。
- **总体验收**：水体静态预览有可见结果；完整动态用户流程、全应用测试和四湖科学验证状态不变，仍未完成。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-26 Sol 高｜恢复 temporal-memory 后全量回归及水体语义复核

- **实测（浏览器状态）**：当前页面选择 Lake Dianchi 的静态地形变量，时间播放控件禁用。屏幕上的着色面是静态水深投影，不能作为动态水体模型已显示或已运行的证据。湿网格轮廓并非矩形，但它来自 82×41 网格并且显示线经角点削切平滑；并无独立高分辨率岸线供几何验证。真实岸线细节仍**不确定**，需要可追溯矢量岸线或更精细网格。不能把插值/平滑显示线描述为实测岸线。
- **实测（隔离全量 Python 自动化回归）**：当前源码复跑 `pytest -q --tb=short` 后为 **866 passed / 26 failed / 4 skipped**，日志 `C:\Users\23801\AppData\Local\Temp\GETM-FABM-WET-260928-pytest-current.log`。先前 temporal-memory 10 个失败项在恢复对应头文件和 adapter/restart 调用后已转为通过；剩余失败来自 fish 单位/零生物量、native fish 状态、macrophyte 状态及初始化、RHS 诊断、实测短波辐射输入契约和营养限制因子边界。该结果不是全应用验收；实现方正在逐组审查根因，不能只为满足源码字符串断言而改科学逻辑。
- **代理（3D 与食性网络自动化）**：既有当前代码的 3D 定向 Node 回归 72/72、食性网络专项自动化 32/32 通过；它们覆盖特定绘图/交互契约，不是完整 UI 工作流或湖泊科学验证。
- **桌面源同步实测**：健康 API 返回 `ready=true`，当前根目录与桌面应用相同；浏览器取回 `viz3d.js?v=134` 的 SHA-256 与工作区文件一致。本轮没有改前端代码，无需因这次 Python/Fortran 回归重启前端服务。当前桌面页面仍是静态地形；没有将其当作动态模型展示验收。
- **启动注册表错误候选根因（部分代理复现）**：launcher 历史日志 21:26:47、21:27:08 的完整 traceback 表明抛错在 `ModelRootLease.existing_service()` 校验 registry 的 `model_root`。当前注册文件与 PID 86432 服务身份有效。只读临时复现证实：两个模型根共享同一 `WET_CASE_STATE_DIR` 时，第二个根会读到第一个根的 `service.json` 并抛出同一 `Registry identity does not match this model tree`。同一日志此前 21:26:20 记录了 UI smoke 要求独立 staged model tree；这使“不同模型根复用共享状态目录中的同一服务注册文件”成为有证据的候选原因，但不证明用户截图发生时环境相同，也不排除过期/并发注册等原因。区分方法：收集触发时的完整启动参数、3 个 `WET_*` 根路径、服务注册 JSON 和 PID；本轮没有改服务锁目录或改变其安全策略。
- **全量目标状态**：全用户流程、食性网络在最终 UI 中的验收、Erken/Lake Ravn/Bryrup/Arreskov 科学验证、原生 solver 编译与冷/热重启续算均仍未完成。四案例状态继续按上方表述；本记录不提升任何代理案例状态。

### 2026-10-26 Sol 高｜v134 水体画面与持续验收复核

- **代理（浏览器画面实看，不是湖泊科学验证）**：本地 3DWET 页面实际加载 `viz3d.js?v=134`。Lake Dianchi 3D 地形页显示蓝色水面深度投影、湖岸线和邻岸示意平面；水体边界来自 82×41 湿网格，轮廓不再是矩形，但仍可见网格采样形成的折线。深度颜色位于 z=0 水面，是显示投影而非湖底几何；显示值取自本案例已有 bathymetry 数据，未与独立测深真值比较。湖底网格默认隐藏，因此只能确认黑色床面当前被默认显示路径避开；黑色片根因及其是否已由根本修复解决仍**不确定**。
- **实测（当前服务身份探测）**：只读调用 `ModelRootLease.existing_service()` 成功核对注册记录、同一模型根目录、实例 ID、PID 86432 与 `http://127.0.0.1:64257` 服务。当前启动入口正常；历史截图中的 `Registry identity does not match this model tree` 未复现。错误截图附带的 `MagicMock configure_logging()` 说明该次日志路径来自 mock 上下文，但不足以证明注册表不匹配由测试造成；当时注册文件与环境的具体冲突仍**不确定**。所需证据：触发时的完整启动参数、`WET_MODEL_ROOT` / `WET_CASE_DIR` / `WET_CASE_STATE_DIR`、注册表 JSON 与完整 launcher 日志。
- **代理（自动化回归）**：3D 定向 Node 测试 72/72 通过；明确收集的全前端 JS 测试 37/37 通过；`tests/test_ecology_network.py` 与 `tests/test_wet_foodweb.py` 32/32 通过。全量 Python suite 仍为 **36 failed / 856 passed / 4 skipped**，日志在 `C:\Users\23801\AppData\Local\Temp\GETM-FABM-WET-260928-pytest-full-safe.log`；失败涉及 fish unit/zero-biomass、native fish/macrophyte state、RHS diagnostics、temporal memory、direct measured SWR 和 limitation-factor bounds。不得据此声明全应用全功能测试通过。
- **流程状态**：`build/full-workflow-20261025-attempt65/ui/ui-report.json` 当前为 `draft_incomplete`，9/10 项使用合成 Imported Random Lake；ETA/完成/失败通知仍因运行环境不支持 Notification API 而未完成原生系统通知验收。其 calibration 的 SciPy 启动终态未捕获，ABC-SMC 未运行。因此完整用户流程仍**未完成**。
- **四湖状态**：Erken 为**代理**——2017 attempt03 当前输出只覆盖 2017-06-29 至 2017-07-29（720 小时），比配置季节段少 1,536 小时，无 solver exit code，且使用混合站点/ERA5 forcing 的均匀空间广播；完整季节配对与科学验证**未完成**。Lake Ravn 的历史官方 GOTM-WET 1D replay 属**代理**（非本应用当前 GETM 3D）；当前 GETM 3D 案例与科学验证为**未完成**，仍缺经认可的连续 bathymetry、river cell mapping 和现代兼容生态配置。Bryrup 为**代理**——已存在的一天 GOTM/STIM 单列 smoke 只有两个输出时刻，归档输入测量来源未独立核验，不是当前 GETM 3D 或生态验证。Arreskov 有官方监测背景及 1990 报告汇总观测值（来源记录属**实测**），但无配对模型运行/验证，案例状态为**未完成**。四个案例均未达到科学验证通过。
- **设计参考图**仍为 `（待补充：参考图的具体路径或链接）`。Nature/科学可视化的设计方向只约束呈现，不充当模型数据来源或科学验证证据。

### 2026-10-26 Sol 高｜当前源码三角网格与食性网络复验

- **代理（自动化回归）**：在当前工作区执行 `node --test 3DWET/tests/test_lake_display_mesh.js 3DWET/tests/test_ecology_foodweb_ui.js`，命令退出码 0；三角网格测试 53/53 通过，食性网络 DOM harness 的 3 项手工汇总断言均输出 PASS（类型筛选/关系编辑/预览应用/重载拒绝；分层证据视图；完整路径总数、24 项首屏和键盘渐进展开）。该证据覆盖当前源码测试，不是桌面端视觉实测或原生通知验证。
- **代理（UI/图标回归）**：`node --test` 工作台壳、SVG 图标和学术视觉系统测试 5/5 通过；`test_ui_theme.py` 在环境缺少 pytest（`No module named pytest`）时直接执行文件内 3 个断言函数，3/3 通过。这是源码契约检查，不是桌面窗口外观验收。
- **运行案例状态**：Erken seasonal attempt03 PID 85064 在 13:56（本地）仍存活；只读反向扫描日志找到最新进度标记 `2017-08-01 17:00:00: saving 3D`。日志末段仍反复打印 Patankar `small pi=0`；三个 NetCDF 文件时间戳仍为 13:22:07/13:19:16。D 盘的 13:53 日志快照因源文件在复制期间继续增长而标作不完整，未做哈希验收。运行有进度但未完成；不读取活动 NetCDF、不把此代理运行称为案例验证。
- **其他验收状态**：黑色床面片仍**未修复**，唯一根因仍**不确定**；Erken、Lake Ravn、Bryrup、Arreskov完整科学验证与完整用户流程仍**未完成**。参考图仍为 `（待补充：参考图的具体路径或链接）`。应用服务/桌面首页版本同步仍**未完成**。

### 2026-10-26 Sol 高｜NOVANA 湖深数据源覆盖核查

- **实测（官方来源查询）**：官方 NOVANA WFS 等深线层共 1,096 条要素、78 个不同湖名；Arreskov、Bryrup、Ravn 均无等深线或声呐测深点匹配。方法及 WFS 图层/字段见[覆盖核查记录](novana-bathymetry-coverage-20261026.md)。
- **边界**：仅排除这一个数据源，不能证明其他官方或研究测深数据不存在；不把类别深度或派生表面当作实测空间地形。三个案例的 3D 输入/科学验证仍**未完成**。本次未创建、运行或删除案例，未打开 APP。

### 2026-10-26 Sol 高｜食性路径渐进展示集成复核

- **Luna 中实现**：食性路径保留完整计数，首次最多渲染 24 张三节点/两边路径卡；原生按钮按批展开余下路径。小网络仍一次显示全部。绘图复用同一份已解析路径列表来选择三层子网可用性与示例路径，避免重复全量枚举；配置边含义与保存/求解语义不变。
- **Sol 高复核（代理/界面 harness）**：`node --check 3DWET/app/static/js/ecology_network.js` 与 `node 3DWET/tests/test_ecology_foodweb_ui.js` 通过；覆盖 125 条路径的首屏限量、完整总数、渐进展开和按钮可访问性。此为自动化 DOM harness，不是桌面端实测。
- **3D 表现力代码核对（代理/自动化契约）**：当前源码包含派生三角表面网格、按显示层位区分的低饱和网格线、可选层间连接线，以及可逆的体积预设（同时开启三角显示与所有可用垂向层）；代码明确标记这些几何为 display-only，颜色不代表变量值。`test_viz3d_mesh_mode_preference.js`、`test_viz3d_volume_preset.js` 与旧模板兼容检查共 10 项通过。它们不是桌面三维渲染的视觉实测，也不能证明黑色床面已修复。
- **源码服务同步（实测/HTTP）**：端口 8770、8771、52812 的静态脚本字节与工作区一致；首页仍分别引用旧缓存键 v24、v24、v31，而工作区模板为 v32，说明服务模板未重载。端口 64257 无监听。按用户要求未打开、启动或重启桌面应用；窗口是否载入新代码**未完成验证**。
- **流程状态更正（按 attempt65 当前报告）**：`build/full-workflow-20261025-attempt65/ui/ui-report.json` 列出 9/10 项已完成、1 项未完成，因此之前记录的 8/10 已过时。重复副本扫描/移入回收区/恢复项为**代理（隐藏 Edge + 合成案例）**：恢复文件哈希与源一致且回收区清空；不能替代真实科研案例的流程验收。剩余 `eta_completion_failure_notifications` 已验证应用内阈值、状态与回退路径，但 headless Edge 不支持 Web Notification；桌面 WebView2 已有显式权限桥接实现，`tests/test_desktop_notifications.py` 的 43 项隔离测试通过。由于本轮未打开桌面 APP，原生系统通知交付仍**未完成实测**。三个 Node 通知 harness 均通过。
- **科学任务边界**：本次未创建、运行或删除科学案例。Erken、Lake Ravn、Bryrup、Arreskov 的完整科学验证仍**未完成**；完整用户流程为**代理 9/10**，尚未全部跑通。黑色床面仍**未修复**，根因仍**不确定**。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-26 Luna 中｜食性环检测性能改进与源码服务核对

- **代码实现**：`ecology_network.js` 使用稀疏出边邻接表检测三节点有向环，并在单次摘要中一起返回环数和闭环边集合；图形、证据摘要和关系表复用缓存；节点保存成功后重算缓存。复杂度为 `O(V + E + Σ_(a→b)deg⁺(b))`，稠密网络最坏仍可能达到 `O(V³)`。不改变配置边语义或求解器拓扑。资源引用从 `ecology_network.js?v=31` 提升到 `v=32`。
- **静态代码审阅**：未运行测试、语法检查或模型，也未打开 UI；状态依据是代码路径检查，运行时交互效果仍未验证。
- **源码服务同步检查**：服务 `52812` 的 idle 状态已核实，`/static/js/ecology_network.js?v=32`、`app.js`、`viz3d.js?v=128` 和学术样式表逐字节匹配工作区文件；但同一服务返回的首页仍引用旧 `viz3d.js?v=124` 和 `ecology_network.js?v=31`，可见其模板尚未重载。安全重启该 `--no-open` 服务的命令被本机策略拒绝；没有改用绕过方式，也没有启动或打开另一个窗口。端口 `64257` 无监听进程。因此产品代码已写入且静态资源服务字节可取，但当前首页/桌面窗口同步仍**未完成**。
- **任务边界**：没有运行、创建或清理科学案例；Erken、Lake Ravn、Bryrup、Arreskov 科学验证及完整用户流程保持各自原来的**未完成**状态。黑色床面仍**未修复**、根因仍**不确定**，参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-26 Sol 高｜Erken 既有 24 小时实测剖面对照

- **代理对照（有限诊断）**：只读取授权 SITES Erken 小时剖面（**实测**）与已有 WET `output.nc`（**代理模型输出**），未重跑模型。按相同时间标签在站点最近湿格 (8,36; 0.108 km) 将 10 个 sigma 层中心温度线性插值至 50 个传感器深度；24 小时 × 50 深度共 1,200 对。模型减观测 bias +0.0536°C、MAE 0.0542°C、RMSE 0.0591°C。输入哈希、算法、范围和边界见[单日对照记录](erken-one-day-measured-profile-pairing-20261026.md)。
- **误差结构（代理对照诊断）**：首六帧 bias/RMSE 为 +0.0374/0.0437°C，末六帧为 +0.0742/0.0772°C；深层 10.5–15.5 m RMSE 0.0650°C，略高于 5.25–10 m 的 0.0535°C。该日代理对照显示误差随时段增大，但不能单独确定其物理来源。
- **状态边界**：观测源为**实测**，模型输出与这组模型—观测配对及误差指标为**代理**；模型时间轴与 SITES UTC+1 标签尚无独立时区校正，时段仅一天，初始化使用同日观测剖面，气象源为 3.517 km 外且 `confirmed:false` 的 Malma 站，边界/河流配置也有限。因此 Erken 完整科学验证仍**未完成**；另三个湖泊、完整流程维持各自原标记。

### 2026-10-26 Sol 高｜丹麦湖泊已发表 1D 模型基准检索

- **文献检索（不代表本地验证）**：Aarhus University DCE Report 402 报告了以一维 GOTM-FABM-PCLake 建立的 Ravnsø、Bryrup Langsø、Arreskov Sø 等湖模型。Ravnsø 报告值为最大深度 32.6 m、平均深度 14.9 m、面积 1.8 km²、33 层；温度校准期 2004–2005，验证期 1996–2003，表中上层 0–5.2 m 验证 n=208、百分偏差 −1.8%、Spearman 0.99、R² 0.99。
- **适用边界**：这是已发表的**1D 文献结果**，不是本项目 GETM 3D 实测或代理结果，不能移植成当前验收结论。Lake Ravn 当前 3D 案例/科学验证仍**未完成**。详细来源与限制见[文献基准记录](danish-lake-published-benchmark-20261026.md)。

### 2026-10-26 Sol 高｜Lake Ravn 官方深度分区面积曲线交叉核对

- **实测（官方来源文件只读几何/表格核对）**：QWET workshop 的 33 个 `DYBDE=0..32` 分区多边形面积字段与几何面积一致，总面积 1,821,419.685 m²，与工作簿 1,821,420 m² 一致。由深到浅累加分区面积，与官方 hypsograph 最近整米阶的累计面积最大相对偏差 0.658%，支持分区顺序和总面积曲线一致性。
- **冲突与限制**：另一个 Ravn shore outline 几何面积为 1,782,658.425 m²，比深度分区总面积小约 2.13%。尚未做叠置/边界判定，`DYBDE` 是类别不是点位连续水深；任何将其代表深度栅格化的做法只能叫**派生代理**，不证明逐点实测床深。详见[hypsograph 交叉核对](ravn-hypsograph-crosscheck-20261026.md)。Ravn 3D 案例和科学验证仍**未完成**；本轮未构建模型案例、未运行求解器、未清理旧案例。

### 2026-10-23 后续：原始 CSV、播放和桌面同步复验

在新隔离副本 `user-journey-Erken-import` 中通过浏览器导入 CSV，应用解析27条记录、生成气象输入、构建2小时配置、通过预检并运行3,600步。导入基线用时44.1秒，输出有效并生成20帧；之后在同一会话先查看动态结果、把模型上下位置调到+15%，再用食性网络工作台克隆两份蓝藻 cohort，重跑3,600步（195.7秒、18.3步/秒），输出有效性检查通过，2D/3D与NetCDF归档。新输出 3D 可选 `erken_added_algae_20261023_a1_sDW`；播放20/20帧、实测4.0 fps、整帧P50/P95 50/68 ms、超预算0/20、超目标帧间隔0，播放至末帧仍保持+15%。随后从新输出提取并绘制该藻类时间序列。故“CSV导入→运行→查看动态结果→调整视角→添加藻类→再次运行→分析新增变量”的单会话工程流程已浏览器实测通过；两个克隆均为同功能群 cohort，不代表不同物种或生物学差异。食性网络原有20个实例、17条配置食性引用；添加后 UI 列出5个藻类实例（原3+新增2），总实例数据此为22，17条食性关系保持不变。新藻类没有被自动添加为猎物，已有边均可回溯到实际 YAML 端口，不代表运行时摄食验证。黑色湖底/阴影仍未解决。输入中25条为 SITES-derived Erken 数据、末尾2条为边界垫片；云量、蒸发、河流与多数生态初值为代理/默认，不能称 Erken 科学验证。详情见[后续浏览器验收记录](playback-ui-20261023-v92.md)。

源码改动后的桌面应用健康端点为 PID 78560、实例 `7630e040d730458c8a2bcf3ec1b5d054`，窗口标题为“3DWET Studio”；浏览器服务返回的 `viz3d.js` 与本地源码 SHA-256 均为 `BEDCC8128D45E7AB2DF05466410D7A36AD0A32BCC59CD6959B4B379C2C6CFE48`。

### 2026-10-23 v92 浏览器播放、视角、网络与隔离流程观察

在本机浏览器 8766、隔离副本 `build/real-use-validation-20261023/user-journey-Erken-baseline` 实际观察。2D 与 3D 各自完整推进 24/24 帧、实测 4 fps；位置控制从 −15% 到 +15% 画面可见反向位移，恢复 +15% 后从 frame 23 切到22仍保持。显示网格密度从 1 改 2 后图例计数随之变化，最后恢复为1。食性页显示21个启用实例、398个耦合端口、17条已解析配置关系，并逐条显示猎物、消费者、端口和解析证据；新增藻类没有自动增加食性边。副本完成首日模型运行，结果页提取了新增藻类全湖平均曲线。原始 CSV 上传未在同一运行流程中成功，故完整流程仍为 Partial；黑色底面仍可见并未修复。详细指标、代理输入和限制见[本次浏览器验收记录](playback-ui-20261023-v92.md)。

Erken June 2024 attempt03 的候选求解器 A/B/C 现已全部完成并通过输出结构检查。C 独立重跑报告位于 [C 重跑验证 JSON](../../../build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arm_C_rerun_20261023/validation.json)，A/B/C 的限定性解释见[attempt03记录](../../../build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/ATTEMPT03.md)。此候选二进制并非正式应用求解器；测次为机制敏感性，带显式边界垫片及云量/蒸发/河流/生态初始化代理，不能称科学验证。

### 完整用户工作流 acceptance attempt52–54（2026-10-22）

attempt52/seed 2026102201 保留为失败记录：合成气象 CSV 上传遗漏已知站点坐标，API 按现有规则返回 HTTP 200 但 `success=false`、`requires_confirmation=true`，不会写 `meteo.nc`；失败来自验收生成器未填写坐标，不应放宽应用确认逻辑。验收生成器现写入其合成源位置 (29.8°N, 117°E)，提交坐标并核对保存 JSON、NetCDF 与 provenance 哈希/坐标。

attempt53/seed 2026102202 也保留失败：当前 `/api/preprocess/help` 正确描述边界几何为 `Polygon or MultiPolygon`，而旧验收脚本只接受 `Polygon`。这是过时的 harness 断言，不是产品回归；脚本现按实际支持类型验证并拒绝 `LineString`。新增回归覆盖 meteo 保存证据、HTTP 200 确认响应拒绝以及 preprocess help 标签。

attempt54/seed 2026102203 在全新隔离目录完成 external、features、results、scipy、abc、restart 六个后端阶段，状态 `awaiting_ui`，不是完成轮次。源版本 `01b9a4edfb251d8295fcfd17b87ce5142b527a945def816b091a65c4cddc078f`，输入 identity `e2c8ea3812dee9d488898a9c14668d2f242194361112751be1635950da044566`；后端报告哈希和六阶段均记录于 [round.json](../../../build/full-workflow-20261022-attempt54/round.json)。十项 UI 清单尚无实测记录（0/10），需针对同一版本与 seed 提供各项实际观察及证据文件后方可复核；当前正式连续完成数仍为 **0/5**。本轮合成站点与 synthetic reference observations 只验证工程路径，不代表观测科学率定或科学准确性。

验收脚本和文档修改未触及应用源代码。8766 再次核验 HTTP 200、首页引用 `viz3d.js?v=79`，served 脚本 SHA-256 与工作区一致：`85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`；因此无需重启。

### 当前源码冻结包 pyABC ABC-SMC 验收（2026-10-22）

从当前源码在新隔离目录 `build/portable-abc-current-20261022/` 构建 onedir 包；首次尝试使用系统 Python 因未装 PyInstaller 而未构建，改用项目 `.venv` 后 PyInstaller 6.22.3 成功。现行 `scripts/build_app.py` 有 `--collect-all pyabc`；包内有 `pyabc` 与 `pyabc-0.12.17.dist-info`。此前关于“当前打包脚本遗漏 pyabc”的旧审计结论不适用于当前源码；历史旧安装包问题仍只代表其对应版本。

用冻结 `3DWETStudio.exe` 启动随机端口服务并执行完整 `--method pyabc` 验收；服务环境清除 `PYTHONPATH`/`VIRTUAL_ENV` 并将 `PYTHONHOME` 指向不存在目录。参考运行和固定中点 baseline 各完成 600 步（约 6.9 秒）；冻结服务报告 `pyabc-abcsmc`、任务完成，记录 14 次实际原生模型评估、两代 ABC-SMC、每代 4 个接受粒子。epsilon 从 `0.0013396773` 降到 `0.0004655425`，每代样本数为 5；两代后验权重均有限、为正且归一化。SQLite 有 14 次模拟，数据库分布与 API posterior/历史实际试验、参数范围核对通过；应用了两个参数并检查保存结果。最终加权距离 `0.0002846650` 小于独立固定中点 baseline `0.0013510493`。校准任务耗时 103.297 秒；完整证据和限制见[当前冻结包验收报告](../../../build/portable-abc-current-20261022/REPORT.md)及同目录 `acceptance-pyabc/verification.json`。

源包 `Theoretical lake/fabm.yaml` 运行前后 SHA-256 均为 `8C360E7832B2F6E8805A00EC865A26CA12DF8966730AE280F853AA483193F627`；仅 disposable work copy 被应用候选参数。该结果证明当前源码的冻结依赖与真实 ABC-SMC 工程路径可工作，不是实测率定、生态合理性、推断收敛或五个学术工作流完成的证据。隔离包没有安装到活动应用；没有应用源代码变化，8766 无需重启。

### 官方 Ravn GOTM 隔离工作副本原生运行（2026-10-21）

在 `build/ravn-official-working-copy-run-20261021-attempt01/case` 从只读官方 reference 新建工作副本，并仅运行副本内官方 `gotm_release.exe`。启动器版本为 GOTM `v5.3-679-gc0add0a2-dirty`（au branch）、FABM `v0.95.3-298-gf73ec4c`，NetCDF 3.6.1-beta1；退出码 0，墙钟 24.233 秒。新输出含 5,844 条记录，覆盖 1990-01-01 00:00 至 2005-12-31 00:00（秒，自 1990-01-01），维度 `time=5844, lon=1, lat=1, z=32, zi=33`。有限值扫描覆盖全部 273 个时间变量（38,739,876 个数值；163,731 个掩码值；未掩码非有限值为 0）。输出 SHA-256 `8edd2faf797368757b7fd12ae27d02e40f703bdcdb892c00ddc756b2295a51bf`；日志 SHA-256 `d8f3e7069ca9103dd93006fbdf8594ffb58962fca46a60245d7ddc919fe0962d`；release executable SHA-256 `9840dc304b5f1d013cbd10861ce1da14d992c3555db1ec930f32d8f95121b6e4`。报告及副本前置 provenance 在同一 build 目录；运行前先移除副本旧 output，源 reference 运行前后文件树 SHA 相同。

这是 **GOTM/FABM/WET 一维单水柱工程复现**，不是 GETM 网格运行，也不是观测率定、独立留出验证或科学有效性证明。求解日志记录 FABM interior state repaired 250,670 次，应作为数值行为审阅项。正式五轮仍为 0/5。2026-10-22 已另行完成 fresh-default 单参数训练/留出试验，详见下方报告；它不等同于正式完整率定。源码输出校验现兼容 time-z、time-zi 与无垂向维的单列时间场，并拒绝非单例水平维；该 Python 模块尚未在现存 8766 进程内重载，需宿主手动重启后才会由桌面运行版使用。


### Ravn fresh-default 单参数实验（2026-10-22）

基于官方默认 ZIP 和官方 ParSAC XML 中 `abiotic_water.kNitrW` 的 `[0.1, 0.5]` 界限，在隔离可信工作副本实际运行。1990–1995 作 warm-up，1996–2000 仅用于训练目标，2001–2005 在选值后才评分；映射为 `abiotic_water_sO2W`、mg/L、O2 basis、Ravn 柱、负向下深度，最近模型输出容差 12 h。DO.obs 11,680 行/11,622 解析记录/14 条解析诊断；训练 1,673 记录中配对 1,644，holdout 1,812 记录中配对 1,770，8,137 条落在评分时段之外。

bounded optimizer 共 18 次函数调用后达到调用上限，`success=false`，不可称为收敛。它的最好候选为 `kNitrW=0.4998694857`（训练 RMSE 2.2292591102 mg O2/L）；随后单独实跑官方精确上界 0.5，训练 RMSE 略低为 2.2292568971，并对该值做干净副本重跑；holdout RMSE 2.4380041424，默认 0.3 的 holdout RMSE 2.4510905851。由于优化未收敛且结果贴近边界，这只是被测候选中的单参数最小 RMSE 实验，不是稳健最优、完整 ParSAC 或科学验证。所有求解器返回码为 0、输出每次均验证 5,844 条记录；源副本校验有效，恢复后的 fabm 哈希匹配默认值。完整输入、过程、指标、日志及哈希见[实验报告](../../../build/real-use-validation-20261022/ravn-default-calibration/REPORT.md)、[机器可读 summary](../../../build/real-use-validation-20261022/ravn-default-calibration/summary.json)。8766 当前 v77 服务未导入此离线实验脚本；这次无需 UI 同步，也没有声称桌面应用运行了校准。

### Ravn 官方 packaged `temp_do` 重放（2026-10-22）

另以 Aarhus 官方 `calibrated_config.zip` 中的 `gotm-temp_do.yaml`/`fabm-temp_do.yaml`，配合相同官方默认 setup、输入文件和官方 GOTM-WET runner，在新隔离副本运行 fresh default 与 packaged temp_do 两次。两个 run 均退出 0，得到完整 5,844 日记录、32 层，所有时间变量均无未掩码非有限值。workshop `wet_obs.xml` 支持 TEMP→`temp`、DO→`abiotic_water_sO2W` 映射，并声明六年 spin-up；这里把 1996–2000 与 2001–2005 统一作日期窗口对比，不代表 packaged config 的训练/留出边界。

Packaged 设置的上游文件、源 ZIP、默认差异和校验哈希均可追溯；相对默认值有 7 个活动 GOTM 参数和 9 个 FABM 参数变动。TEMP RMSE 从 1.953 降到 0.800 °C（1996–2000），从 1.966 降到 0.889 °C（2001–2005）；DO RMSE 从 2.240 升到 2.291 mg O2/L，及从 2.451 降到 2.270 mg O2/L。配置文件没有记录训练日期，后期数据只能称后期诊断，**不能称 holdout validation**。Packaged native DO 达 36.33 mg O2/L，且日志记录 230,813 次 FABM interior-state repair，需要进一步物理/数值审阅。该重放是 upstream config reproduction，不是本仓库率定、ParSAC 复现、独立验证或 GETM 3D 结果。详见[packaged TEMP/DO 重放报告](../../../build/real-use-validation-20261022/ravn-temp-do-review/REPORT.md)、[配对指标](../../../build/real-use-validation-20261022/ravn-temp-do-review/pairing_metrics.json)。

后续 USGS DOTABLES Benson–Krause 大气平衡筛查在其 0–40 °C、0.5–1.1 atm 方法范围内，配对每个时间/层的温度与 DO；压力来自与 meteo forcing 一致的 `airp`，盐度输出恒为 0。Packaged 全期 186,960 个有效时间层样本中，29.00% 超过 100% 大气平衡值、1.877% 超过 150%、0.126% 超过 200%、0.00267% 超过 300%；峰值 36.33 mg/L 对应 373.71%，日期 1992-05-24、层中心 2.5 m、温度 16.76 °C。Default 相应比例为 17.50%、0.574%、0.0144%、0.00214%，峰值 30.19 mg/L / 326.30%。两组峰值都是需要物理/数值复核的红旗；过饱和不单凭表层平衡计算即可判定不可能，湖内产氧可能存在，pressure forcing 是否海平面订正也未知。深度静水压可达约 4.07 atm，超出 USGS 方法 1.1 atm 上限，因此未外推深度饱和值。峰值 chlorophyll 和前后日 DO 变化只作上下文，日输出不能归因昼夜产氧机制；缺少完整生物氧预算和独立验证。38/48 个低于 0 °C 的 default/packaged cells 按方法域排除；无 >40 °C 或气压越界。可复现脚本与结果见[氧饱和筛查脚本](../../../build/real-use-validation-20261022/ravn-temp-do-review/analyze_oxygen_saturation.py)和[机器可读结果](../../../build/real-use-validation-20261022/ravn-temp-do-review/oxygen_physical_screening.json)。

观测事件复核：`DO.obs` 在 1992-05-25 10:00 的 −2/−3/−4 m 数值为 12.6/14.5/14.6；packaged 最近日输出早 10 h，使用相邻原生层中心作线性插值后高出 8.17–9.83 mg O₂/L。时刻不完全共址且观测源没有内嵌单位，此处沿用此前显式 mg O₂/L 映射。`CHLA.obs` → WET Chl-a 模型变量映射存在，但观测单位无来源声明，因此不做 Chl-a 数值对照。详见报告事件小节和 `oxygen_physical_screening.json`。

### Ravn 数值质量后续审查：interior repair 计数与关闭修复探针

源码 `3DWET/src/gotm/src/fabm/gotm_fabm.F90` 中，`repair_interior_count` 每次内部状态检查发现至少一个越界状态时递增一次；它不是变量数、网格单元数或单个状态修复总数。`kNitrW=0.10…0.50` 的21个 profile arm 计数为250,612–250,713，区间仅101；surface/bottom 计数均为0。计数几乎不随本次参数剖面变化，但仅凭汇总数仍不能判定触发变量、事件时段或科学影响。

Sol 将 `grid_11_0.30` 复制到全新 `build/real-use-validation-20261023/ravn-repair-off-probe`，只在诊断副本中关闭 `repair_state`。副本 solver SHA-256 与源副本相同（`9840dc304b5f1d013cbd10861ce1da14d992c3555db1ec930f32d8f95121b6e4`），`fabm.yaml` SHA-256 也匹配（`4658680a444ee1da2e83422d514359e6d00d6aba0013c8ce2ccebda1697d815a`）。求解在首个 time-loop 区间的0%处停止，日志报告 time integration 后 `greens_sDW=0.9957e-4 gDW/m³` 低于 `cDMinW=1e-4`，差值`4.3e-7 gDW/m³`（0.43%）；探针记录为失败且日志含 fatal solver error，尽管被记录的进程返回码为0。repair-enabled 源输出中该状态最低约为`1e-4`。这是预期的关闭修复诊断探针失败，不是生产模型修复、操作建议或源码更改。它只确认一个靠近下限的小幅超界，不证明全部约25万次计数都由 `greens_sDW` 或同类事件造成，也未量化其对 DO profile 的影响；仍需追踪越界时段/变量并评估对轨迹和率定目标的影响。该审查不撤销已记录的 DO 过饱和筛查警示，也不解除 Ravn 官方 proxy/default forcing 与缺少独立验证的限制。详见[数值质量后续审查](../../../build/real-use-validation-20261022/ravn-knitrw-profile-20261022/REPORT.md#numerical-quality-follow-up-repair-counter-and-repair-off-probe)、[探针摘要](../../../build/real-use-validation-20261023/ravn-repair-off-probe/repair_off_probe.json)及[完整日志](../../../build/real-use-validation-20261023/ravn-repair-off-probe/model_run.log)。无源码或活动案例变更，8766/8767未重启。

同一 `grid_11_0.30` 基线的另一隔离敏感性副本 `build/real-use-validation-20261023/ravn-cdminw-sensitivity` 只将 `diatoms`、`cyanobacteria`、`greens` 三个 phytoplankton 实例的 `cDMinW` 从 Ravn 包配置的`1e-4`改为源码注释默认值`1e-5`；语义差异审计确认其余配置未变。使用同一 solver（SHA-256 `9840dc304b5f1d013cbd10861ce1da14d992c3555db1ec930f32d8f95121b6e4`）成功运行，5,844条记录，进程返回0，`output.nc` SHA-256 `ae91b6355df23a12ca482681caeccacc5b2b57301ba1dea09eac52432baf2e71`。训练DO配对数与基线相同（1,644）；训练RMSE从2.239836小幅降至2.233959 mg/L。相对基线的187,008个配对样本差值统计显示：DO RMSE/max绝对差0.303/6.258 g/m³；`cyanobacteria_sDW`为0.854/10.833 gDW/m³；`diatoms_sDW`为0.328/11.155 gDW/m³。修复计数从基线 interior/surface/bottom=250,670/0/0 变为250,830/0/571,204。该敏感性结果说明改下限会改变运行轨迹，并伴随大量bottom-state修复；它不是修复方案，没有证明科学改善或确定差异原因。实验仅属代理/默认配置敏感性，不是现场验证，也不构成推荐参数。此前DO过饱和筛查及forcing/生态代理限制仍然保留。完整探针输入和哈希摘要见[敏感性目录](../../../build/real-use-validation-20261023/ravn-cdminw-sensitivity/sensitivity.json)。

### 当前桌面版本及历史 ABC 结果复核（2026-10-21）

当前 8766 首页引用 `viz3d.js?v=79`，served 脚本 SHA-256 `85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D` 与工作区一致。2026-10-22 Sol 在新的干净 UI 会话中，以 Erken baseline 和 `cyanobacteria_sDW` 分别检查 2D、3D：2D 手动推进 frame 0→1→2 时页面显示“显示当前模型结果”，色标范围依次为 [0.2998265028,0.3017181754]、[0.2996529639,0.3024195433]、[0.2994793653,0.3026430607]；随后以 12 fps 目标连播约 1.3 秒推进至 frame 16/23，色标更新为 [0.2809491754,0.3006117344]，未停滞。3D 普通视角 frame 0→1→2 水体颜色始终可见、phase=ready、帧号递增且自动色标随帧改变。本次仅覆盖该案例/指标、新干净会话、2D 所列帧段和 3D 普通视角短帧段；没有复现用户报告的第二帧缺色，也不证明所有相机角度、变量或设备均正常。旧标签页曾出现的 Plotly axis scaling 现象仍需按相同条件独立复现，不能据本次结果宣称已解决。工作区脚本无代码变更，8766 无需重启；本轮离线校验器的后端加载状态仍需单独核验。

独立审计确认 attempt19 旧 ABC acceptance 失败由 pyabc tidy pivot 合并同 distance/weight 的不同粒子导致；harness 已修复，并使用归档数据库复验成功。attempt19 的历史结果仍记为失败；没有重跑 ABC，也没有完成正式五轮。范围是对历史结果的证据抽取复核，不是新一轮率定或科学结论。详见[attempt19 harness 诊断](abc-attempt19-harness-diagnosis.md)。

## 当前结论

**总体状态：进行中；完整用户流程尚未通过，三个学术案例均未达到科学复现/验证门槛，正式五轮为 0/5。** 证据分别覆盖后端 API、求解器输出、可见 UI 和科学有效性，不能相互替代。这里的“verified”只表示该表述范围的有限证据已被记录；不表示整项工作流已通过。

8766 当前活动案例为 `build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/mechanistic-nlimited-sensitivity-20261022/nfix_on`。首页引用 `viz3d.js?v=79`，服务端脚本字节与工作区 SHA-256 一致。新的干净 UI 会话已完成 Erken baseline `cyanobacteria_sDW` 局部播放检查：2D 手动 frame 0→1→2 与随后约 1.3 秒连播至 frame 16 均有当前结果且色标范围改变、未停滞；3D 普通视角 frame 0→1→2 水体颜色保持可见、phase=ready、色标随帧改变。用户报告的第二帧缺色在该 3D 条件下未复现。旧标签页历史 axis scaling 现象没有在本次测试中判定或宣称已解决。其他 Erken 多指标和性能记录仍按各自独立测次解释：既有 `abiotic_water_sO2W`、`cyanobacteria_sDW` 有 24/24 帧、376 有效/0 缺失；蓝藻某次 1 fps 测次整帧 P95 402 ms 且 1/24 间隔超目标，`temp` 某次 P95 81 ms、Plotly 绘制 43 ms。不同测次的性能值不合并；本次普通视角抽查不证明其他指标、相机角度、科学流程、三个学术案例或完整用户流程通过。

### 垂向平均源码状态（2026-10-21）

旧审查的“`level=0` 被当作水柱平均”是 2026-10-11 源码基线结论；当前 `updateViz3dAvg` 已请求 `aggregation=depth_mean`。专项复现还发现原生 GETM 场变量在 k=0 有有限值、而 `hn` k=0 为零厚度时，字段和 `hn` 的物理槽起点不同步，导致回退 sigma 权重并将边界槽混入平均。本轮新增回归先以 34（错）对 25（期望）失败，之后修复为按 `hn` 的物理层起点对齐字段。当前 `tests/test_result_layers.py` 为 **31/31 通过**，覆盖实际 `hn` 不等厚加权、非有限/非正厚度与缺失值、干格/mask、native 零厚度 padding、sigma 层界面/层中心回退、无权重坐标时报错、纯二维/底面变量保值及 2D 平均场 UI 请求。指南已说明有效层处理与回退规则。

此前垂向平均专项检查记录的 **v74 历史服务快照**（不是当前 8766 状态）：当时 listener PID 为 32392，`GET /` 的 `viz3d.js` 标记为 v74，served 与 workspace 脚本 SHA-256 均为 `356AF278AAAB7808A51344237054BA7D01173375A58D877EC85EC6D812FCD0AA`。当时 `GET /api/results/2d?var=temp&time=0&aggregation=depth_mean` 返回 200、`aggregation=depth_weighted_mean`、`weight_source=hn`、网格 18×44。该历史请求确认当时 API 正常走层厚平均；native 有限边界槽这一特定情况由上述 31 个专项测试覆盖，没有声称已从当前真实案例直接复现。当前运行版本见上方 v76 记录；不据此推断 PID 有变化。

正式五轮的当前计数仍按主计划为 **0/5**。2026-10-19 的五次连续通过属于旧源码指纹，不能沿用。见[用户中心验证计划](../../superpowers/plans/2026-10-21-user-centered-research-validation.md)和[五次完整流程计划](../../superpowers/plans/2026-10-11-repair-and-five-workflows.md)。

## 判定口径

- **Verified**：证据直接覆盖表述范围、数据和版本。
- **Partial**：已有真实证据，但缺关键操作、版本一致性、完整范围或科学核验。
- **Blocked**：材料、兼容求解器或必要配置缺失，无法有效继续。
- **Missing**：没有找到足以支持该项的证据。

同一个案例可能在 API 层 Verified、可见 UI 层 Partial、科学结论层 Blocked。具体结论按层分别记录。

## 完整用户流程里程碑

| 里程碑 | 状态 | 已有证据与边界 |
|---|---|---|
| 从普通用户目录启动、移机后重开 | **Partial** | 冻结便携包自检、迁移 UI smoke 和旧迁移包的真实 solver 小案例运行均已通过；仍未证明完整案例移机后能重开并恢复相同结果哈希，也未在当前 build 上复现完整迁移。见[便携包自检](../../../build/portable-user-validation-20261021-final/report.json)、[迁移后自检](../../../build/portable-user-validation-20261021-final/relocated-self-test.json)、[迁移后 UI smoke](../../../build/portable-user-validation-20261021-final/relocated-ui-smoke.json)、[便携 solver 运行审计](../../../build/portable-user-validation-20261021-final/portable-execution-20261022-final.json)。 |
| 外部数据来源、许可、映射与导入 | **Partial** | Erken 的官方岸线/等深线、SITES 气象和锚定温度剖面有来源与哈希；等深线导入、湿格生成和 API 插值已核验。温度/气象是单站广播；云量、蒸发、流量、营养盐及生态初值存在占位/代理。不能称为全套实测外部强迫。见[等深线预处理审计](erken-contour-preprocess.md)、[Erken 24 h 审计](../../../build/real-use-validation-20261021/erken-real-location-24h/evidence/erken-real-location-24h-audit.md)。 |
| 配置并运行原生模型 | **Partial** | Erken 地理位置 44×18 网格、376 湿格、10 层的 24 h 成对 GETM/FABM 运行成功，均为 17,280 步、24 个逐小时输出；另有 5 天外部气象驱动输出审计，但该运行使用合成 Imported Random Lake 几何。运行成功和有限值检查不证明 Erken 科学有效。见[Erken 24 h 审计](../../../build/real-use-validation-20261021/erken-real-location-24h/evidence/erken-real-location-24h-audit.md)、[5 天代理运行审计](../../../build/real-use-validation-20261021/erken_meteo_run_5d/ERKEN_METEO_PROXY_5D_OUTPUT_AUDIT.md)。 |
| 查看结果、仪表盘、剖面、时序和导出 | **Partial** | 新增了一次 v69 真实 Erken 2D 温度连续播放检查：24/24 帧完成，时间和自动色标首尾改变。仪表盘、剖面、时序与导出等仍未在当前固定 build 的同一完整用户流程中串联验收。较早 v68 Erken 检查只验证 served assets 和 API payload，没有可见播放。见[下方 v69 播放证据](#播放证据按案例和版本拆开)、[v68 API 检查](playback-v68-20261021.md)、[旧播放验收记录](playback-after-20261021.md)。 |
| 2D/3D 动态播放、范围、时间、值与相机 | **Partial** | 既有 `temp`、`abiotic_water_sO2W`、`cyanobacteria_sDW` 多指标测次及拖动旋转测次保持各自独立。2026-10-22 Sol 在新的干净 UI 会话中以 Erken baseline `cyanobacteria_sDW` 检查 2D、3D：2D 手动 frame 0→1→2 色标范围依次为 [0.2998265028,0.3017181754]、[0.2996529639,0.3024195433]、[0.2994793653,0.3026430607]，页面持续显示当前结果；以 12 fps 目标连播约 1.3 秒到 frame 16 后仍推进，色标为 [0.2809491754,0.3006117344]。该目标帧率不是实测 fps。3D 普通视角 frame 0→1→2 水体颜色可见、phase=ready、帧号递增且自动色标改变；该范围内未复现第二帧缺色。旧标签页历史 axis scaling 现象仍未在相同条件复现或排除。先前仰视遮挡分支 renderer 回归仅覆盖 land-network opacity。2026-10-22 v86 Lake Luoma 页面复核已覆盖播放中滚轮缩放保持，以及短范围播放中切换仰视预设并完成3/3帧；仍未覆盖平移、暂停/续播、变量切换时相机保持、其他指标/设备与完整帧范围；目标 12 fps 历史测次见[v73 UI 播放证据](playback-v73-20261021.md)，性能值不跨测次合并。最新8766 v89 Luoma `temp` 三角网格前台测次完成21/21帧且拖拽时继续推进；2D测次完成20/20帧但面板0.6 fps与约3秒推进19帧的墙钟观察不一致，不能形成稳定性能基准。两项仅限本地 Luoma 用户路径，不是外部或学术案例证据。以上不构成整体验收或科学验证。 |
| 成对生态情景及差异解释 | **Partial** | Erken baseline/treatment 与新增的三组真实网格24小时技术敏感性均有隔离运行、配置差异和逐场输出审计；新三组区分新增实例的综合效应与 `lNfix` 单因子效应，但生态初值/低DIN为代理且未有观测支持、完整质量/元素闭合或季节验证。结果证明接线、变量输出和有限响应，不证明真实物种竞争或管理效果。见[旧成对运行](../../../build/real-use-validation-20261021/erken-real-location-24h/paired_results_summary.json)、[三组敏感性报告](../../../build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/REPORT.md)。 |
| 打包、导出和迁移后复现 | **Partial** | `20261021-final` 旧迁移便携包（前端 cache key `viz3d.js?v=40`）中的打包 solver 已在迁移目录完成 Theoretical lake 可弃置副本运行；完整案例移机复现、结果哈希比对和完整交付审计仍缺，当前 build 的完整迁移复现也未完成。见[旧包便携 solver 运行审计](../../../build/portable-user-validation-20261021-final/portable-execution-20261022-final.json)及[迁移后 UI smoke](../../../build/portable-user-validation-20261021-final/relocated-ui-smoke.json)。 |
| 当前 build 五轮完整验收 | **Missing / 0/5** | 未发现与当前固定源码/求解器指纹一致的五轮证据。诊断、单案例原生运行、UI 专项和旧版本计数都不算轮次。主计划要求新数据下从创建/导入到结果、率定/对比、清理恢复和语言等阶段完整通过，失败即清零。 |

### 2026-10-22 旧迁移便携包 relocated solver 实际运行

在 `build/portable-user-validation-20261021-final/relocated/最终便携版/3DWET/case/` 下将旧包自带的 `Theoretical lake` 复制为独立的 `TheoreticalLake_PortableExec_20261022`，从该副本工作目录直接运行迁移包的 `bin/getm_cartesian.exe`，并将旧包 `bin/runtime` 加入 `PATH`。退出码为0，生成 `output.nc`（21帧、864个数值变量）及 `THEORETICAL_LAKE.2d.nc`（20帧、17个数值变量）；独立 NetCDF 扫描确认两份输出均无未掩膜 NaN/Inf。迁移包原始 Theoretical lake 的15个文件哈希及打包 solver SHA-256（`98F359433FB6646F5D597D24FE5234B43C1246CB3A9EF8F606BF2E69C5E63AAF`）运行前后不变，stdout/stderr 和模型输出均留在 disposable case。该证据仅证明旧 `20261021-final` 包（`viz3d.js?v=40`）能运行这一小型示例；不证明完整项目迁移与结果哈希复现，也不代表当前 build 的完整迁移复现。详情见[运行摘要](../../../build/portable-user-validation-20261021-final/portable-execution-20261022-final.json)、[输出有限值扫描](../../../build/portable-user-validation-20261021-final/portable-output-scan-20261022.json)。

## 真实地点 Erken 与代理限制

**已验证的工程链路**：SITES Erken 官方 GIS 边界/等深线用于 EPSG:3006 网格；SITES/Malma 气象和 Erken 温度剖面用于 2020-01-01 至 2020-01-02 的初值/强迫；24 h baseline 与 treatment 均完成原生求解，并生成真实 2D/3D GETM 输出。结果具有 24 个输出时刻且状态场通过有限/非负检查。

**必须保留的限制**：单一气象站被均匀广播到 376 个湿格；该测站靠近岛/岸线；云量与蒸发有占位值；没有实测流量（river_method=0）；没有验证过的 Erken 营养盐、生态初值或通量诊断，采用了默认/代理。干预只克隆相同藻类实例，并不代表经过参数化的不同种竞争。所以上述是“真实地点资料 + 明确代理项”的流程演示，不是完整真实数据驱动的 Erken 模拟、校准或科学验证。

另一个 Erken 气象五天运行使用的是 **合成 Imported Random Lake 网格/水深/初始条件**，只验证外部气象输入与求解链路；不能描述成 Erken 湖泊空间模型。证据见[五天输出审计](../../../build/real-use-validation-20261021/erken_meteo_run_5d/ERKEN_METEO_PROXY_5D_OUTPUT_AUDIT.md)。

### 播放证据按案例和版本拆开

- **2026-10-22 新干净 UI 会话：Erken baseline 2D/3D 蓝藻局部播放**：Sol 在 8766 页面选择 `cyanobacteria_sDW`，未重跑模型。2D 手动推进 frame 0→1→2，状态均为“显示当前模型结果”，色标分别为 [0.2998265028,0.3017181754]、[0.2996529639,0.3024195433]、[0.2994793653,0.3026430607]；另一次独立连播测次设置范围 0–23、目标 12 fps，页面计时器在第 18 个成功帧时显示实际 11.4 fps、整帧 P95 30 ms、绘制超预算 0/18、帧间隔超目标 4 次；帧游标继续推进且色标动态更新。该计时数据只描述此测次。3D 普通视角逐帧检查 frame 0→1→2，三帧水体颜色可见、`data-render-phase=ready`、帧号递增且自动色标范围随帧改变；该设置下未复现第二帧缺色。证据只覆盖该 Erken baseline、指标、新干净会话、所列短帧段及 3D 普通视角；旧标签页历史 axis scaling 未在相同旧条件下独立复测，不能据此宣称整体解决、所有动态播放或完整用户流程通过。完整用户流程、三学术案例和正式五轮仍在进行中。

- **v79 窄视口 2D→3D 首绘与播放复核**：隔离 Chromium 页面使用 8766 当前服务，新页 `innerWidth=520`、`innerHeight=709`，Plotly 容器为 490×269。2D `cyanobacteria_sDW` frame 23 后切至 3D `temp` frame 23，首次 3D 图为 `ready`、`stale=false`，存在 scene/canvas，未记录 axis-scaling 异常；最终边距 l32/r112/t60/b28。3D `temp` frame 0→1→2 均绘出水体颜色网格（每帧 1,504 个有限强度值），自动色标上限依次为 2.1806960、2.1813078、2.1819060；12 fps 目标连续播放由 frame 0 推进至 7、14、21、23 并在终帧停止，phase 一直为 ready、色标更新、未记录浏览器异常。Sol 随后在实际 8766 IAB 重新进入 Erken baseline，以 520×709 页面检查 `temp` frame 0→1→2：frame 2 湖盆蓝色水体着色可见、色标递增，页面无加载失败。两个检查均为局部视图/帧段复核，不代表所有变量/设备/镜头或完整流程通过。**版本同步边界**：工作区模板已经是 `viz3d.js?v=79`，但 `GET /` 仍返回 `viz3d.js?v=77`；`/static/js/viz3d.js?v=77` 和 `?v=79` 均返回与工作区一致的 SHA-256 `85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`，缓存头为 `no-cache, max-age=0`。IAB 已重新导航并通过局部实播，但模板 cache key 尚未同步；不据此声称所有浏览器/视角已验证。原有 v75/v78 历史测次保持独立，不合并性能读数。

- **v75 Erken 3D 多指标动态渲染复核（历史测次）**：当时服务提供 v75，`viz3d.js` served/workspace 哈希匹配。`abiotic_water_sO2W` 氧气和 `cyanobacteria_sDW` 蓝藻均完成 24/24 帧，时间与自动色标随帧更新，数据状态均为 376 有效/0 缺失。氧气在正常复位相机时水体可见；此前只见湖盆是相机仰视到水面下方造成遮挡，复位后恢复。蓝藻播放全程水体可见；目标/实际 1 fps、整帧 P95 402 ms，1/24 个帧间隔超目标。先前 `temp` 测次为 24/24、目标/实际 1 fps、P95 81 ms、绘制 43 ms。证据仅覆盖所列 Erken 指标/设置下的 3D 动态渲染，不代表其他指标、连续镜头操作、科学/整体流程或三个学术案例通过。
- **v75 Erken baseline 蓝藻播放中拖动旋转复核（历史测次）**：当时页面选择 `cyanobacteria_sDW`，播放范围 frame 0–23、目标 1 fps。播放启动后在 Plotly 主图内拖动旋转；frame 9 时仍在播放，实际 1 fps、成功 10 帧、376 有效/0 缺失，截图显示转向后的蓝色水体；继续至 frame 23 后自动停止，24/24 帧完成，整帧 P95 65 ms、超预算 0/24、慢间隔 0，最终截图保持转向镜头且水体仍可见。该结果是一次特定指标/范围/目标速度的 UI 操作复核；不声称缩放、平移、暂停/续播或切换变量时保持镜头已通过，也不覆盖其他指标、设备或科学有效性。相机仰视到水面以下时可能遮挡水面，复位可恢复常规水面视角。完整用户流程与三个学术案例状态仍按上文为 Partial/Blocked。
- **v78 3D playback patch（源码/专项测试及有限 UI 复核）**：工作区修正了 Plotly `update` payload 的 trace-array 维度；`3DWET/tests/test_viz_waterbody_patch.js` 专项 suite 21 项通过，根因证据指向快速路径为每个 trace 的数据多包一层数组，违反 Plotly trace-indexed update 语义。8766 首页仍引用 v77 cache key，但 `/static/js/viz3d.js?v=77` 的 SHA-256 `FD8D1274B1BE413A43E066496D2FCD8848B980A17211F90A75D5B4FD18D6995C` 与工作区脚本一致。Sol 随后在新干净 UI 会话中实播 Erken baseline 的 `cyanobacteria_sDW` frame 0→1→2，普通视角水体颜色持续可见、phase=ready、自动色标逐帧改变，未复现第二帧缺色。此结果仅覆盖所列条件；不证明旧标签页历史 axis scaling 现象已解决，也不覆盖所有相机、变量或完整用户流程。此前 v77 land-network 遮挡回归仅覆盖仰视 opacity 分支。

- competition_treatment 的 44×18×10、24 帧可见 UI 检查：2D greens_competitor_sDW 12.1 fps；3D 12.1 fps、P95 68 ms、1/24 帧超绘制预算、5/24 慢间隔。该案例是播放夹具，不是 Erken 科学验证。见[Erken 工作流报告中的 UI 播放记录](../../../build/real-use-validation-20261021/erken-real-location-24h/evidence/erken-real-location-24h-audit.md)。
- **当前 Erken baseline，8766 页面 v69，2D temp 可见 UI 播放**：目标 12 fps，24/24 帧完成；模型时间从 2020-DOY001 01:00 走到 DOY002 00:00。frame 0 色标为 2.180048942565918–2.1806960105895996，frame 23 为 2.180048942565918–2.1909096240997314，确认时间与当前帧自动色标改变。计时器最终显示实际 6.4 fps、整帧 P50 14 ms/P95 198 ms、超绘制预算 2/24、目标间隔慢 10/24；分段 request 89 ms、CPU assembly 2 ms、draw 9 ms。此结果验证的是 v69 的 2D 可见播放，不代表达到 12 fps，不验证 v70，也不验证 3D 或镜头交互。
- **当前 Erken baseline，8766 页面 v69，3D temp 播放中镜头操作**：范围为 frame 0–23，目标和实际均为 1.0 fps，24/24 帧完成并在 frame 23 自动停止。播放期间在视口从 [380,170] 拖到 [420,220]；可访问性状态仍显示播放开关开启，游标随后到达 frame 9（2020-DOY001 10:00），之后的截图为 frame 17（18:00）；截图中镜头方向已改变并保持，同时时间/场值继续更新。最终计时器为 P50 167 ms/P95 207 ms、超绘制预算 0/24、慢间隔 0；request 207 ms、decode 13 ms、CPU assembly 71 ms、Plotly draw 117 ms。这验证 v69 此案例、此目标速度下的动态绘制与播放中镜头保持；没有声称帧在拖动手势的每个瞬间都推进，也不验证 v70 或 12 fps 性能。
- **v71 相机俯仰修复，8766 页面同步与 UI 复核**：根因为 `plotly_relayouting` 手势期间的相机回写和 Plotly 自身旋转互相冲突。修复后手势期间只缓存相机，松开后再执行 clamp。13/13 相机相关测试通过；`GET /` 页面脚本标记为 v71，served 与 workspace `viz3d.js` SHA-256 均为 `A7EC5CFCAB205DA8D73D81203ED2CEADC0E4BD7A5935CB2966A2796EC6A1AD07`。浏览器实际拖动后能看到湖盆底面视角，验证该页面的相机俯仰 UI 修复；未测 Erken 3D 连播帧率，不改变 v69 2D 12 fps 未达标记录，也不代表完整工作流通过。
- 8766 上 Erken baseline 的 v68 复核：服务页与资产哈希匹配、结果 API 返回变化的帧值/范围，但没有可见浏览器、帧率、色标绘制、暂停续播或镜头证据。见[v68 API 检查](playback-v68-20261021.md)。
- Erken temp 的不同复测不可合并为单一承诺：既有记录包含 8.0 fps（24/24）和之后的 4.1 fps（24/24；P50 208 ms、P95 398 ms；请求约 170 ms、JSON 解码约 264 ms、组装约 61 ms、绘图约 123 ms）。这些属于不同测次/代码状态，应保留各自时间与版本；都未证明 v70。改动后的匹配 24 帧复测尚缺，不能声称性能提升。参见[较早播放验收记录](playback-after-20261021.md)；4.1 fps 测次记录为当前会话提供的测量值，待写入带页面指纹的独立浏览器证据。
- **本轮变更前 Erken baseline 目标 12 fps 播放读数**：2D 24/24 帧、实际 6.5 fps，整帧 P50 14 ms/P95 125 ms，请求约 109 ms/帧、CPU assembly 2 ms、draw 9 ms；3D 24/24 帧、实际 4.5 fps，请求 172 ms、JSON 解码 252 ms、assembly 75 ms、Plotly draw 83 ms。该组是 v73 优化前测次，独立保留，不覆盖 v69 2D 的 6.4 fps，也不合并此前 Erken 3D 的 8.0/4.1 fps 测次。优化后实测见[v73 UI 播放证据](playback-v73-20261021.md)。
- **v73 播放优化及当时的 UI 性能测次**：3D 有界未来帧预取最多 4 帧；2D 预取身份包含播放起止范围，避免修改范围后复用错帧。前端回归 36/36、服务端回归 37/37 通过。v73 页面当时的 Erken baseline 可见 UI 24 帧复测显示 2D 11.4 fps、3D 12.1 fps。边界见[v73 UI 播放证据](playback-v73-20261021.md)，缓存深度变化不单独构成性能承诺；这些是历史 12 fps 测次，不代表 v75 本次 1 fps 复核的性能。
- **只读 API 小基准，历史 8766 v72 测次**：可重复脚本[benchmark_playback_api.ps1](../../../scripts/benchmark_playback_api.ps1) 一轮记录 2D 四帧批量响应 42,526 B/61.7 ms；3D 首帧含静态几何 64,900 B/17.8 ms，后续带 `static_key` 的 frame 1–4 分别 39,015/38,983/38,978/39,025 B、27.4/18.1/16.8/17.7 ms；首帧加四个后续帧共 220,901 B。对 24 帧逐帧串行 API 请求共 961,960 B、492.8 ms 请求总时长，request-only 48.7 帧/秒，P50 18.1 ms/P95 27.4 ms；第二次请求总时长 399.0 ms、request-only 60.15 帧/秒。首次探测另曾测得 2D 57.1 ms、3D 冷首帧 142.2 ms、warm frame 139.9 ms。此测次排除浏览器调度、JSON 解码、CPU 组装和 Plotly 绘制；API 吞吐不能证明 UI 播放性能。4 帧是前端缓存帧数上界，不是总字节上界。

## 三个学术研究状态

### Lake Ravn — 官方 GOTM-WET 观测配对

**状态：Partial。** 官方 workshop 1D 水柱默认输出和 `.obs` 文件已用于配对；完整 TEMP.obs 的 11,904 行中得到 5,813 对，UI 展示源文件、哈希、显式 temp/degC 映射、排除数和配对图。Fresh-default 单参数 DO RMSE 搜索未收敛，不能称稳健最优或完整 ParSAC。官方 packaged `temp_do` 配置另已隔离重放并显示更低 TEMP 误差，但官方材料未证明拟合日期，故 2001–2005 仅为后期诊断，不是留出验证。DO 最大值 36.33 mg/L 和大量内态修复仍待物理/数值审阅。整体仍是**1D 原柱模型**，不是 GETM 湖泊网格、正式率定或独立科学验证。详见本状态文档上方的两份实验报告。

来源：[Ravn Sol 审查及 UI 复核](ravn-pairing-sol-review.md)、[观测率定实施计划](../../superpowers/plans/2026-10-16-ravn-calibration-implementation.md)。

### Lake Bryrup — 2018 热浪、分层与藻类

**状态：Blocked（2026-10-23 公开来源追溯后保持）。** 本次复查 Chen 论文及 AU/机构书目记录，只确认其公开方法与论文元数据；未找到可下载的 Chen 校准 legacy bundle、匹配 forcing 数据包或新增许可依据，未下载数据，也未运行 solver。WET 1.0 归档确实含完整的 *WET 自身* Bryrup 案例输入，时段为1990–1995，气象1979–1999、流量/水质月数据1990–1999；它不是 Chen 2020 的率定版 PCLake 案例或热浪场景。官方 WET 构建文档指定 GOTM/FABM `au` 分支、WET `master`；本次公开 refs 复查未找到 GOTM/FABM `au`，可用 GOTM `master` 是5.4.0且不匹配文档所述 WET 1.0 论文 GOTM 5.2.2-au。隔离 5.4.0 runner 在首步积分前因 `/surface/ice` schema 失败，STIM 构建另遇 GOTM/GETM host 接口不匹配。Chen 包仍缺完整率定配置/初始状态、2001–2005 循环驱动、2018 三小时 ERA-Interim 热浪序列及数据复用条款。没有 baseline/intervention 输出、输出哈希或生态指标。证据见报告新增“2026-10-22 authority and source-ref recovery follow-up”节，以及 [官方分支审计](../../../build/bryrup-wet-au-authoritative-20261022/au-source-audit.md) 和 [隔离 runner 报告](../../../build/bryrup-wet1-gotm-runner-20261022/runner-report.md)。

数值引用也须保留原文差异：Chen et al. 摘要报告 summer-average Chl-a 最多高 39%、蓝藻 biomass peaks 高 58%；结果 §3.2 和讨论 §4.2 又称 SC5 的 Chl-a peak 高 46%。这可能是平均值与峰值定义不同，也可能是作者表述不一致；文章没有明确调和，引用时须标明指标/出处，不得擅自合并或择一改写。论文方法是 1990–1995 warm-up、1996–2003 calibration、2004–2005 validation；2001–2005 loading/气象循环至 2050 作 50 年 baseline；SC1–SC3 将 May–July 2018 对应时刻的三小时气温按 5/3/1 年间隔替换，SC4/SC5 则对 2005 年后记录施加 +2.9/+5.0 °C，汇总期为 2046–2050。文章页及已检查材料没有提供可直接运行的完整 calibrated legacy bundle；完整模型/率定配置及初值、全量强迫（特别是 2001–2005 循环基线与 2018 三小时温度）和数据再利用条件仍是复现门槛。没有完成论文复现，也不以 WET 1.0 作为同版复现。来源：[Chen et al. (2020), DOI 10.3390/w12010094](https://doi.org/10.3390/w12010094)，摘要、方法 §2.4–2.5、结果 §3.2、讨论 §4.2；细节见[Bryrup 构建评估](../../../build/academic-case-validation-20261021/bryrup/report.md)新增审计节。

最小阻塞项与下一步：①带可核验版本身份且与论文匹配的 GOTM/FABM/PCLake 可执行文件/源码及依赖；②完整率定配置、117个已调整参数、初始/重启状态及1990–2005资料；③准确的2001–2005循环气象和负荷驱动；④2018年5–7月三小时气温及作者的时间匹配/替换规则；⑤每份外部数据的来源与复用条款。资料到齐后先记录来源、日期、许可、字节数和SHA-256，再在全新隔离副本检查版本/schema及未改 baseline 能否进入积分；通过后才构造 SC1–SC5、验证除目标气温记录外输入哈希相同并运行。没有这些材料不启动模型。2026-10-23 追溯详见构建评估报告末尾；只改文档，应用/solver/案例/服务未改，无需桌面同步或重启。

来源：[Bryrup 构建评估](../../../build/academic-case-validation-20261021/bryrup/report.md)、[WET 1.0 兼容性检查](../../../build/academic-case-validation-20261021/bryrup/wet-v1.0-inspection.md)。

**2026-10-25 观测来源更新：** 官方 Kemidata `Feltmåling Sø` API 已导出 Bryrup 站 21000361（`BRYRUP LANGSØ, BRY 1`）1996–2006 现场测量，包含1,676条温度观测、226个测量日期；文件、SHA-256、逐日深度覆盖及限制见[原始观测记录](bryrup-official-observation-source-note-20261025.md)。这是**实测观测数据获取**，但研究对象的站点/深度/时间匹配仍未完成；时间段也不能替代论文所需的2018三小时热浪情景强迫。Bryrup 论文复现与模型科学验证仍**未完成**，历史代理结果仍为**代理**。此新增数据不改变 Chen 校准配置、强迫或兼容模型缺口。

### Lake Arreskov — 气候/营养负荷与生态状态

**状态：Blocked。** 本地和上游支持文件含 GOTM 驱动、16层/1990–2004时间设置、ERA5气象、流量/营养输入、hypsograph、鱼类操作与输出配置，但没有案例专属 `fabm.yaml`、论文六组校准 ensemble 参数及匹配 restart/初始状态。2026-10-22 对当前官方 WET 仓库做了完整可达 refs 镜像：4个 branch、4个 tag、228个可达 commit；Arreskov 案例路径历史中没有 `fabm.yaml`，逐 commit 树检查也未找到 ensemble/restart/initial 文件。论文确称配置曾随 WET repository test case 提供，并指向历史 `WET/wet` v0.1.0 release；该旧项目 API 查询为404、release 页面跳转登录，无法恢复作者包。Pure页面仅显示CC BY论文附件，现有补充材料未含可执行配置；WET软件GPL许可不能替代强迫/观测/ensemble数据复用条款。由于生态结构与校准集合缺失，不从generic WET模板推断、不报告状态转换或负荷阈值，也未运行基线/情景。完整 refs、限制及文件哈希见报告新增的 2026-10-22 full advertised-ref history and publication-access recheck 节。

关闭缺口所需：取得有版本/哈希/许可的作者版案例 fabm.yaml、配套模型 commit/build、校准 ensemble、输入观测与驱动；如果无法取得，须改称新 exploratory 模型研究并由科学负责人先批准结构、参数化、ensemble 和情景定义，然后再独立做成对文件差异和多组结果审计。

来源：[Arreskov 源配置审计](../../../build/academic-case-validation-20261021/arreskov/REPORT.md)。

**2026-10-22 来源恢复补充：** 已在隔离目录恢复并核验 Zenodo 的 WET v0.1.0 发布包，以及官方当前公开仓库中的 Arreskov forcing/GOTM 支持文件；来源 URL、版本/commit、哈希、文件清单与逐项缺口见[恢复审计](../../../build/academic-case-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md)。恢复的两组材料不能拼成论文可执行配置：仍缺湖泊专属 `fabm.yaml`、校准 ensembles、观测数据和匹配的 GOTM/FABM 构建身份。v0.1.0 包元数据标注 CC BY 2.0，而包内 `COPYING`/`LICENSE` 为 GPL v2 文本，许可适用范围仍待澄清。没有运行模型，论文复现继续 **Blocked**；此前 API/页面不可访问的记录是当时的访问状态，不因本次恢复而删除或改写。

**2026-10-25 观测来源更新：** 官方 Kemidata `Feltmåling Sø` API 已导出 Arreskov 站 45000018（`Arreskov Sø /004`）1990–2004 温度/溶氧等现场测量，原始文件、SHA-256、行数和限制见[Arreskov 观测来源记录](arreskov-official-observation-source-note-20261025.md)。这补充了原始观测数据，但 `/004` 与论文模型列的空间对应、时间/深度/变量映射及数据许可仍**不确定**；原始数据获取为**实测**，模型配对/论文科学验证仍**未完成**。原“缺观测数据”仅描述2026-10-22恢复审计时的状态，不代表本次更新后仍未下载任何站点观测。

## 结束验收的明确剩余步骤

1. **在旧版播放记录基础上补齐交互复核。** 该历史测次的 `GET /` 引用 v75，且当时 `viz3d.js` served/workspace 哈希匹配；Erken `temp` 24 帧的 3D 动态网格显示已按本案例/设置复核。播放期间镜头保持及范围、暂停/续播等操作仍待完成。
2. **继续扩展播放性能验收。** 完整 Erken temp 24 帧目标 12 fps 历史测次为 v73：2D 11.4 fps、3D 12.1 fps；本次 v75 复核使用目标 1 fps，实际 1.0 fps，整帧 P95 81 ms、绘制 43 ms，不能与 v73 测次直接作性能对比。固定变量、实际帧、范围、绘图配置和设备；随后覆盖代表性的水动力、生态、垂向/无垂向指标，不用 API-only 吞吐或温度单指标推断全部指标。
3. **完成 2D/3D UI 播放与相机动作验收。** 对 2D 和 3D 各跑完整选定区间，实际操作起止范围、速度、暂停/续播、滑块拖动、切换指标和终帧停止；逐帧核对时间/数值/自动范围和帧序列。3D 在播放中操作旋转、缩放、平移并继续播放，确认相机和当前 toolbar/drag mode 保持；保存可复查截图/观测和服务指纹。此前暂停时的镜头操作、静态帧和 API 请求都不满足这项。
4. **完成 Erken 真实输入边界声明和科学对照。** 保留真实输入与 proxy 分栏/manifest；选择一个能由有效资料支持的目标问题。对照与干预只改声明变量，给出一项准确机制假设；补上至少一个真实湖泊观测比较、合理时窗/层位匹配、生态状态和可用通量/元素收支审计。若无法补齐河流、营养盐或生态初值，结果继续标为代理演示，不升级为 Erken 科学验证。
5. **完成 Ravn 有来源依据的率定流程。** 单参数 `kNitrW` 搜索在 18 次调用后未收敛；官方 packaged `temp_do` 配置虽已重放，但未知拟合日期使后期窗口不能当 holdout。若取得可核验的官方训练日期、算法/目标和参数阶段说明，再复现多参数过程并保留训练/留出隔离、日志和 source/rollback 哈希；否则维持 packaged config 的未知训练来源标签。完整率定与独立科学验证仍未完成；现有 RMSE 只作比较诊断。
6. **解除 Bryrup 和 Arreskov 阻塞。** 按各节列出的精确来源/兼容性门槛取得材料后，重新做隔离配置检查；没有匹配配置/驱动/版本时维持 blocked，不发起替代输入猜测。
7. **固定最终版本后跑五轮。** v71 源码/求解器/冻结包和浏览器证据固定后，从五套各自新生成、哈希留档的输入开始，按[正式五轮计划](../../superpowers/plans/2026-10-11-repair-and-five-workflows.md)跑完创建、导入、网格/配置、六个后台阶段、十组 UI、求解、结果、率定/对比、恢复/语言与交付。失败、源码变化或缺任一步即归零重跑；历史旧指纹的五轮不纳入。
8. **更新状态并做独立复审。** 为每轮和每个科学案例保留版本、服务实例、输入/输出 SHA、日志、UI 截图、实际值与残留限制。只有 Sol 核对当前源码、可见应用、模型输出及科学分级证据后，才可把对应条目升级为 Verified；总体完成仍需所有约定门槛通过。

## 本次状态整理所依据的文件

- 计划：[用户中心研究验证](../../superpowers/plans/2026-10-21-user-centered-research-validation.md)、[完整五轮](../../superpowers/plans/2026-10-11-repair-and-five-workflows.md)、[Ravn 实施](../../superpowers/plans/2026-10-16-ravn-calibration-implementation.md)。
- 外部输入/求解：[Erken 24 h 审计](../../../build/real-use-validation-20261021/erken-real-location-24h/evidence/erken-real-location-24h-audit.md)、[Erken 五天代理运行](../../../build/real-use-validation-20261021/erken_meteo_run_5d/ERKEN_METEO_PROXY_5D_OUTPUT_AUDIT.md)、[Arreskov](../../../build/academic-case-validation-20261021/arreskov/REPORT.md)、[Bryrup](../../../build/academic-case-validation-20261021/bryrup/report.md)。
- UI/API/迁移：[v68 API-only check](playback-v68-20261021.md)、[playback acceptance](playback-after-20261021.md)、[Ravn pairing/UI](ravn-pairing-sol-review.md)、[frozen package](../../../build/portable-user-validation-20261021-final/report.json)、[relocated UI smoke](../../../build/portable-user-validation-20261021-final/relocated-ui-smoke.json)。

此前垂向平均专项修复了 `3DWET/app/result_layers.py` 的原生 GETM 字段/hn 物理槽位对齐，并新增、运行了专项测试；当时核对的 v74 页面、脚本哈希及 depth_mean API 响应属于历史快照。8766 当前 HTML cache key 仍为 v77，但静态脚本 URL 返回值与工作区脚本 SHA-256 一致；该 v74 快照形成时，浏览器 hard reload 与动态播放视觉复核尚未完成；此为历史状态，已由上方 2026-10-22 新干净会话的有限 2D/3D UI 检查补充。v75 3D 多指标复核仅为历史测次。完整用户流程和科学验证仍在进行中，本状态不构成整体验收完成声明。

### 本轮 Erken 多指标 API 动态载荷检查

应用重启后，当前误选中了 pytest 临时单列案例；随后通过本地 `/api/case/open` 切换至既有 **Erken 24 h baseline**，没有重新运行模拟。对 `temp`、`abiotic_water_sO2W`、`cyanobacteria_sDW` 分别请求 2D `/api/results/2d` 与 3D `/api/results/3d_surface` 的 frame 0、1、2、23：2D 响应形状均为 `[18,44]`，每帧 376 个有限值且 min/max 随帧变化；3D 响应形状均为 `[10,18,22]`，每帧 1,850 个有限值且值域随时间变化，`static_geometry_key` 均为 `b078b205b37f44a9916562ad97c027b0ef8a4658920b3a4f8e1acbc0da902f98`。当前应用已指向 Erken baseline。上述 2D/3D 项均为 server/API 动态载荷检查，不验证可见 UI 播放或实际渲染，也未复核用户报告的播放中水体颜色消失；当时 UI 播放未验证；该历史 API-only 检查现由下方 2026-10-22 新会话的有限 UI 复核补充。API 数据本身仍不等于可见渲染证据。

### 本轮 pytest 临时案例状态污染修复

根因是服务将最后打开案例和外部案例清单写入桌面应用目录；测试曾把 `pytest-*` 临时案例路径写入该持久状态，导致重启时恢复到临时案例。现已将 pytest 进程的案例状态目录隔离到独立临时目录，并在服务恢复、注册和读取外部案例清单时排除 pytest 临时路径；失效/不存在的恢复路径不会自动替换成案例列表中的其他案例，用户需手动加载或打开有效案例。回归验证：`.venv\Scripts\python.exe -m pytest 3DWET/tests/test_case_state_isolation.py -q` 为 **4 passed**；`.venv\Scripts\python.exe -m pytest 3DWET/tests -q` 为 **46 passed**。应用案例清单 `3DWET/app/data/external_cases.json` 现为有效 JSON，保留 19 条用户案例、0 条 pytest 临时路径。用户指南已补充重启恢复说明。

8766 的 listener PID 30476 仍运行已导入旧后端模块；当前服务虽曾报告活动案例为 Erken baseline，但本次后端状态隔离代码尚未同步加载，重启核验 Pending。以上记录描述当时 API 检查后的状态，后续已有下方 2026-10-22 新会话的有限 UI 复核；API 载荷本身仍不证明渲染/交互。整体用户流程保持 **Partial**。

### 本轮 Erken 同种群拆分数值一致性检查

在独立副本中完成 Erken 2020-01-01 24 h baseline 与同种群 clone-split 配对求解；两次 solver 均 exit 0。两组共有 44×18 网格（376 湿格）、10 层和同一套水动力/气象输入；split 将 greens 的 12 个初始状态各拆半给两个相同参数的 FABM 实例，初始总量相等。基于 `hn × 250 m × 250 m` 的终帧体积积分，浮游植物总 DW/N/P/C 差异为 +0.144% 至 +0.235%，溶解氧及无机营养盐差异绝对值不超过 0.00124%。这仅是同种群拆分的数值一致性检查，不是不同物种竞争试验、观测验证或生态结论。该 1 月 24 h 窗口属于冰季代理，与春夏藻类高峰问题不匹配；参见 [Yang et al. 2016](https://limnologia.hu/publikaciok/2016/Yang_etal.pdf) 和 [Mesman et al. 2023](https://gmd.copernicus.org/articles/16/35/2023/)。可复核设计、哈希、运行状态和逐帧数值见[配对检查报告](../../../build/real-use-validation-20261021/erken-conspecific-clone-sanity/REPORT.md)及其 `paired_results.json`。原有配对结果未更改；本检查不改变 Erken 科学案例的 Partial 状态，也未同步/重启 8766 旧后端。



### 2026-10-22 启动恢复仪表盘与运行实例同步验收

新增启动恢复行为：服务重启恢复有效活动案例后，前端读取层数、FABM 模块数、湿格统计、输出帧数，并在已有结果时加载仪表盘变量摘要和迷你热图；无输出、加载中、读取失败均显示对应状态。通过隔离临时模型根目录运行新 launcher 并请求 HTTP，`/api/case/current` 返回 Erken treatment 的 10 层、21 个生态模块、24 帧及完整运行配置；之后停止隔离实例。

随后根据用户此前“你来操作”的明确指示，停止旧 8766 listener PID 30476（当时 `/api/run/status` 为 idle），从仓库 `.venv` 启动当前版本。新 listener PID 18568；首页 HTTP 200 并引用 `app.js?v=59`；当前案例仍为 Erken treatment。刷新实际浏览器后，启动落在该案例的 3D 页面；进入仪表盘可见统计为 376 湿格、10 层、21 模块、24 帧，并显示 NH4、NO3、O2、PO4、SiO2、temp 摘要及空间热图。服务端恢复接口确认 `has_results=true`。新版本 `/static/js/viz3d.js` 与磁盘 SHA-256 均为 `85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`。

启动恢复回归：`.venv\Scripts\python.exe -m pytest -q tests/test_current_case_dashboard_context.py` **1 passed**；`node 3DWET/tests/test_dashboard_restore_context.js`、`node 3DWET/tests/test_dashboard_request_order.js`、`node 3DWET/tests/test_builder_dashboard_statistics.js` 均通过。新静态 3D 脚本来自已专项验收的 v79 模板源码；本次复核未在新 listener 中重跑完整 24 帧水体播放或相机拖动，已有 32 项首绘/播放定向测试及前次 UI 帧 0→1→2 证据见前序记录。本次仅同步验收应用版本与 dashboard 恢复，不构成全部用户旅程或科学模型验收。整体状态继续为 **Partial**。

- **2026-10-22 Erken treatment 2D/3D 指标与动态镜头复核（8766 当前服务）**：活动案例为 `build/real-use-validation-20261021/erken-real-location-24h/treatment`，44×18 网格、376 湿格、10 层、21 个启用模块、24 个小时输出。UI 对 `temp`、`abiotic_water_sO2W` 和 `greens_competitor_sDW` 检查 frame 0→1→2→23；2D/3D 时间标签与逐帧自动色标均随帧改变，水域颜色数据持续可见，未复现 3D 第二帧缺色。代表性范围：temp 2D frame0 上限 2.180696、frame1 2.181308、frame2 2.181906、frame23 2.190910；O2 9.987945–9.988004 → 9.975974–9.976130 → 9.964089–9.964372 → 9.690451–9.733917；竞争藻 sDW 0.184129–0.198221 → 0.176039–0.196476 → 0.170241–0.194764 → 0.130049–0.164879。3D sDW 在目标 4 fps 下完成实际播放 24/24、实际 4.0 fps、P95 整帧 33 ms、绘制超预算 0/24；播放中向右及向下拖动，播放状态时推进到 frame17，辅助剖面显示旧时刻并明确提示暂停刷新，主图继续前进，之后完成至 frame23；最终画面仍有彩色水体且保持旋转后的视角。

  **前台复测补充**：Sol 在当前 8766 可见 IAB 前台，同案例/指标/目标速度重播 2D `greens_competitor_sDW` 的 24 帧，仍达到 24/24，但计时器为实际 11.0 fps、帧间隔慢于目标 15/24、整帧 P95 4 ms、绘制超预算 0/24。故后台窗口不能单独解释这次未达 12 fps；页面绘制耗时很低，漏掉的帧间隔发生在绘制预算之外，根因仍需结合事件调度/显示刷新调查。这是可复现的轻度 12 fps 跟随不足，尚无证据说明它导致用户报告的冻结或 3D 缺色；不宣称“完全丝滑”。

  **3D 缺色前台复核**：在同一可见会话选取 `greens_competitor_sDW`，手动定位第 0→1→2 帧；色标范围分别为 0.184129–0.198221、0.176039–0.196476、0.170241–0.194764 gDW/m³，状态栏分别报告水域有效值 376、缺测 0、几何缺失 0，截图中第 2 帧湖盆水体有蓝/青色填色。当前案例与变量下未复现“第二帧仅陆地框架”；由于用户原始出错案例、变量和镜头未知，此结果不能排除其他数据或相机状态下的问题。

  **版本/服务指纹**：首页脚本 cache key 为 `viz3d.js?v=79` 和 `app.js?v=59`；8766 的 viz3d.js、app.js、scientific_workspace.js 与 playback_performance.js SHA-256 均匹配工作区，viz3d.js=`85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`、app.js=`A991E18C92478859426E0C58C922A855001892166A6BB0DF27F28097A469DA0F`、scientific_workspace.js=`D359132E40E230F27D1B9EBCD2AD94E108DD5DFB71002ACB3096D86051D4AE16`、playback_performance.js=`25C08198633DF8AD527AB07A8905F6E3D07AB248C9B4FB129EE8731400DC7A29`。活动 PID 18568 为 `Python310/python.exe 3DWET/app/launcher.py --web --no-open`，进程创建于 2026-10-22 01:41:58 +08:00；`/api/case/current` 返回 treatment、24 帧、10 层、21 模块。当前 server.py 源码 SHA-256 为 `6D111E0A668BD02105E7D735B3FE17E0EEF80031D625B463957AFD269372720F`；这个文件哈希是磁盘源码指纹，不作为 Python 进程内存模块哈希的直接证明。以上只覆盖该案例、已存输出、当前浏览器会话和所列变量，不是科学竞争验证或全功能/全设备验收。

- **2026-10-22 累计节拍调度修复与前台复测**：根因检查发现共享播放器在每个 `setTimeout` 回调实际触发后重新锚定下一轮，因此 timer 的轻微迟到会逐帧累计；原计时器只统计结果更新 Promise 的完成间隔，不等同屏幕呈现时间。已改用单调时钟累计期限并以 requestAnimationFrame 确认前台绘制时机；轻微迟到会在下一节拍校正，严重迟到仅推进一帧并重置节拍，不跳过输出、不突发追帧。TDD 新测试已见 RED，再见 GREEN：scheduler 4/4；播放范围 47/47；性能计时 1/1；2D/3D 预取 21/21、10/10；速度选项 1/1；JS 语法检查通过。旧 `test_scientific_workspace.js` harness 已适配当前自动色标和单调时钟/RAF scheduler，新增的帧顺序、慢帧背压、暂停续播、切页停止和配置隔离断言通过；仅测试 harness 修改，生产代码未变。

  8766 已受控重启至 PID 45904；首页 `scientific_workspace.js?v=13`，服务静态脚本 SHA-256 与工作区匹配。前台 2D `greens_competitor_sDW` 目标12 fps，24/24帧、实际12.0 fps、P95整帧4 ms、绘制超预算0/24、慢间隔8/24（修复前同条件11.0 fps、慢间隔15/24）。前台 3D 同变量目标4 fps，24/24帧、实际4.0 fps、P95整帧42 ms、绘制超预算0/24、慢间隔0/24；播放中拖动相机，主图继续到终帧，色彩和转向后的视角保留。该改善只证明当前 Erken 已存输出、设备及浏览器会话；未测试的案例/设备仍应保留在总体验收边界中。


### 2026-10-22 Erken 蓝藻固氮功能敏感性配对尝试（隔离 build）

按 WET `wet/phytoplankton` 已有固氮开关，在 `build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/` 从同一无克隆三藻类输入构建 `nfix_off/on` 两分支。两边都加入第 4 个蓝藻实例，水体/沉积物营养盐、POM/DOM、O2、硅、碳和 burial 接线保持；burial/inorganic_carbon 的 `nPHYT=4` 与第四组更新/碳通量已接入；zooplankton、zoobenthos 消费者改成5个 prey 槽，原 POM 保留在 slot 5。新组的其余参数、初值都源自同一 baseline cyanobacteria；`cNFixMax` 和 `fMuNFix` 未写入新组配置，以使用模块默认值。A/B 解析 YAML 唯一差别为 `cyanobacteria_competitor.parameters.lNfix` 的 false/true；32 个其他非输出输入文件 SHA-256 完全一致。

两个求解器分支均 exit 0、无 fatal marker、43200 步完成，输出 24 个逐小时记录（+3600…+86400 s），时间网格为 21×15×6；2D/3D NetCDF 掩膜外的无效槽不计为异常。按 NetCDF mask 重新检查后，两份 `output.nc` 和 `.3d.nc` 均为0个未掩膜 NaN/Inf；有效水层时格 27,216。该技术运行仍**未通过生态功能验收**：off 新组与已有 cyanobacteria 在 sDW 上逐点一致且 `wNFix=0`，是正确的同配置关闭开关控制，不代表新增物种；on 的 `cyanobacteria_competitor_wNFix` 在全部有效格为负（−1.0816e−9…−9.5172e−10 gN/m³/s）。源码 `phytoplankton.F90` 的 `aNFix=cNFixMax*(1-aNLim)` 在初始 N/D≈0.60、大于 `cNDMax=0.15` 的代理配置下允许 `aNLim>1`，产生负固氮率。尽管文件有限、求解返回成功，此状态是机制结果不合理的证据，不得解读竞争、种群优势或现场生态响应。我们未将无效新结果载入桌面播放器。完整配置哈希、失败输出变量请求（首轮误请求未注册 `wet_chla` 后已保留日志）、两轮日志、逐值和修复门槛见[配对实验报告](../../../build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/REPORT.md)。完整 N/P/C 库存闭合尚未证明，沉积物 `sN` 与 `sN_PV` 的库存语义/边界项需先核清；此轮仅确认必要状态字段有限，并列出氮固氮率错误。


### 2026-10-22 Erken 固氮负率源码修复状态

根据负 `wNFix` 根因，WET 源码现将浮游植物 `aPLim`/`aNLim` 与大型水生植物 `aPLimVeg`/`aNLimVeg` 限制因子夹在 `[0,1]`；源级回归检查先在旧写法上对四个赋值失败，再在修改后通过（2项）。当前环境无可用 Fortran 编译器、CMake 或 Ninja，遗留 `build-win/getm` 缓存指向另一工作区和不存在的 GFortran 路径，因此没有隔离编译，也没有重跑配对。已记录并备份修复前共享 solver SHA-256 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`；共享 solver 未替换，桌面运行版仍未包含此修复。此前开启固氮分支的负 `wNFix` 结果作为修复前证据保留；修复后运行值、元素闭合和生态验收仍待隔离构建与重跑，不能宣称运行版已修复。详见[配对实验与修复报告](../../../build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/REPORT.md)及源码修复清单。


### 2026-10-22 Erken真实网格3小时隔离候选：API核验

从已有 Erken 24h baseline 复制输入，在 `build/real-use-validation-20261022/erken-external-data-real-grid/candidate/` 单独运行 3h 技术候选。原 baseline、8766 活动案例和生产 solver 均未改动。真实湖岸/等深线、SITES天气和水温 profile 来源及逐文件哈希、CRS/时间对齐、代理条件、solver 和输出哈希见[候选报告](../../../build/real-use-validation-20261022/erken-external-data-real-grid/REPORT.md)。candidate 3帧分别为 2020-01-01 01:00、02:00、03:00（UTC+1）。

隔离应用以独立模型根目录运行于 `http://127.0.0.1:8767/`，health ready；`/api/case/current` 对应 case_generation 1、candidate，路径为上述候选目录。API 在 2D depth-mean 和 3D surface 分别为 `temp`、`abiotic_water_sO2W`、`greens_sDW` 的 frame 0–2 返回带有效水域数据的 18×44 和 10×18×22 载荷，值域随帧变化；`greens_competitor_sDW` 不属于该 baseline candidate，API 返回变量不存在。Sol 随后在可见 8767 UI 以 `temp`、3D 水体立体渲染、连续网格、layer `-1`、默认斜视完成限定复核：手动 Next 逐帧到 frame 2；从 frame 0 以 1 fps 播放到 frame 2，共3帧。各帧水体色面和色标可见；UI 显示水域缺测0、几何缺失0、成功帧3、P95整帧81 ms（按 UI 指标原样记录）。随后从镜头下拉用键盘选择“仰视”，由 frame 2 返回 frame 0 再手动 Next 到 frame 1；截图中仍有水体色面和色标，UI 报水域缺测0、几何缺失0，并提示已隐藏湖底及陆地示意平面。此仰视证据仅覆盖连续网格 `temp` 的手动 frame 1，未做仰视自动连播。本候选测次未复现用户报告的第二帧缺色，但不等同于用户原始案例验收，不能外推到其他变量/图层/视角。诊断底部的“水深 hn+zc”标注垂向几何数据源（层厚和垂向中心），不是所选变量名称；结果请求和色标仍指向 `temp`。8766 活动案例未触碰。

8767 首页 cache key 为 `viz3d.js?v=79`、`app.js?v=59`、`scientific_workspace.js?v=13`、`playback_performance.js?v=7`；前两项及 performance 脚本服务内容与工作区哈希一致，scientific_workspace 服务 SHA-256 `1F377DA982CC4F415C63C5A6E91648934355D64828404ADA133D6C04399EC8B0`。API 和 NetCDF 证据仅限此案例、这3帧和列出的指标；该运行有代理生态/营养盐初值、没有流量、气象单站全域广播、云量50%及蒸发0占位，不能作为 Erken 科学验证。旧5天 synthetic Imported Random Lake 与此真实 Erken 网格严格区分；约8000 km位置差只属于 synthetic pair。



### 2026-10-22 Erken真实网格新增竞争藻三组24小时探索

在 `build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/` 从 Erken real-location baseline 复制同网格、真实湖形、SITES单站强迫和同一24小时区间，使用相同隔离修复候选 solver 完成三组原生运行：`no_extra_competitor`、新增第4个 `cyanobacteria_competitor` 且 `lNfix=false`、以及唯一改变 `lNfix=true` 的分支，三组均 exit 0。网格44×18、376湿格、10层，输出24帧（+3600…+86400 s）；全量数值输出分别扫描864/944/944个变量，没有未掩膜NaN/Inf，也没有负状态。两个新增藻分支记录到独立 `sDW/sNW/sPW/sCW/wNFix`，且消费者/碳/埋藏接线已随实例数更新。no-extra→off中现有藻与营养盐产生小幅差异，但这包括新增实例、初始生物量与C/N/P库和新增接线的综合效应，不能称为纯物种竞争系数。off→on时固氮通量从0变为均值约6.75e−10 gN/m³/s，新增藻sDW均值差约−9.96e−9 gDW/m³，24小时生物量响应可忽略。竞争藻氮磷配额因子均有限并在[0,1]，配额比在配置阈值内。

必须保留数据边界：GIS形态和气象/温度输入有Erken来源，但生态状态仍是默认/代理；NH4=0.001、NO3=0.005 gN/m³及新藻初值是人为低DIN机制初值，不是Erken观测。该冬季单日实验未做科学验证、细胞氮预算或全湖N/P/C闭合。完整哈希、全变量/状态扫描、每个所选变量的有效/掩膜数值与差异见[三组报告](../../../build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/REPORT.md)、[NetCDF审计](../../../build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/three_group_audit.json)、[运行记录](../../../build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/run_status.json)。基线43个输入文件、8766活动案例39个文件和活动指针运行前后哈希相同；8766仍HTTP 200，活动案例未打开/导入。结果结构为标准GETM/FABM NetCDF，但为保护现有活动案例，本轮没有实际UI导入验收，应用代码和生产solver均未变更。
### 2026-10-22 隔离 Nfix 副本播放缺色专项复核

在独立 8767 模型根目录检查活动 Nfix `nfix_on` 的精确副本（24 帧、6 层、189 湿单元）。3D `cyanobacteria_competitor_sDW` 以连续水体、layer `-1`（实际物理层5）、仰视相机手动检查 frame 1，并以1 fps连播至 frame 4；水体色面和色标始终可见，UI 为0缺测、0几何缺失、P95整帧51 ms。目标8 fps 播放至 frame 22，23帧成功，P50 24 ms、P95 31 ms。切 `temp` 后连续水体播放至 frame 2 仍有色面；切等值面模式到 frame 2 后，从当前镜头可见的表面变窄，但水域数据仍有效：1134有效、0缺测、0几何缺失。2D `temp` 热图逐帧播放至 2020-DOY001 05:00:00（frame4），热图可见，自动色标约从14.52–14.99变为14.35–14.92。

诊断文本中的 `hn` 表示水体垂向几何来源；`hn+zc` 表示使用实际层厚和垂向中心构造几何，不是当前科学变量名。科学变量由结果请求和色标单独标识。本轮隔离测次均未复现第二帧后缺色；它们不覆盖所有变量、渲染模式、相机和帧范围，不能称为全场景修复。8766 健康检查为 ready，首页引用 `viz3d.js?v=79`；主服务和活动案例未被触碰，未做代码修改。

### 2026-10-22 隔离 Erken 配对 24 h `nfix_on` 播放复核

在独立 8767 服务的 `nfix_on` 副本中检查 `cyanobacteria_competitor_sDW`。3D frame 0→1 水体颜色可见，随后约 1 fps 连播至 frame 7；376 个有效水值、0 缺失，自动色标随帧更新。播放记录为最新整帧 31 ms、P50 37 ms、P95 94 ms。2D 连续播放至 frame 15（约 1 fps），色标更新；最新整帧 5 ms、P50/P95 均为 32 ms。该变量/案例/浏览器测次没有复现第二帧缺色，不外推到其他变量、案例或条件。

复核后已将隔离 8767 恢复到原始 `candidate`。8766 未触碰，HTTP 200，首页引用 `viz3d.js?v=79`，served SHA-256 与工作区一致（`85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`）；8766 活动案例仍为 `build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/mechanistic-nlimited-sensitivity-20261022/nfix_on`。没有修改应用代码。该检查只支持所列 UI 行为，保留代理生态状态、科学未验证、非完整 N/P/C 闭合以及正式五轮 0/5 的限制。详细技术和科学边界见[三组报告](../../../build/real-use-validation-20261022/erken-real-shape-nfix-paired-24h/REPORT.md)。

### 2026-10-22 Sol：当前 UI 克隆藻类端到端技术验收

在当前 8766 v4 源码 UI 中，将临时副本 `build/real-use-validation-20261022/erken-nfix-playback-isolated/theoretical-phyto-clone-current-ui` 作为工作案例，通过 UI 克隆出 `cyanobacteria_ui_probe`。UI 显示新实例自动接入埋藏和无机碳；食物网连接未自动改写。API 检查确认活跃藻类数为 4，`burial`/`inorganic_carbon` 的 `nPHYT=4`，且索引 4 端口均指向克隆实例。比较测试前后 `cladocerans` coupling 一致。

从 UI 启动原生求解器后完成 600/600 步，耗时 6.98 秒，界面报告完成，输出有效性检查通过。3D `cyanobacteria_ui_probe_sDW` 的 frame 0→1 色标改变，随后播放 frame 0→4 并完成；实测 1.0 fps，整帧 P95 68 ms，绘制超预算 0/4，水域有效值 280、缺测 0、几何缺失 0。结果保留在上述 isolated build 副本。这是 Theoretical Lake 的技术流程检查，不构成科学验证；本次不声称复现用户原始报错。

检查后 8766 已恢复原 `nfix_on` 活动案例且 health 为 ready；index 引用 `viz3d.js?v=79` 与 `ecology_network.js?v=4`，served ecology script SHA-256 与源码一致。恢复后在 8766 对主案例 `cyanobacteria_competitor_sDW` 做 3D 普通视角手动 frame 0→1 检查：时间从 01:00 到 02:00，色标约从 0.04973–0.04985 变为 0.04917–0.04964，189 个有效值、0 缺测、0 几何缺失，水体色面可见。随后保持该变量、普通斜视和自动范围，设置结束帧为2，从 frame 0 连续播放至 frame 2：实际 1.0 fps，3 帧成功，整帧 P95 36 ms，绘制超预算 0/3；189 个有效值、0 缺测、0 几何缺失，水体色面持续可见且色标随时间更新。仰视角同样从 frame 0 连播至 frame 2：实际 1.0 fps，3 帧成功，整帧 P95 36 ms，绘制超预算 0/3；189 个有效值、0 缺测、0 几何缺失，界面提示已隐藏湖底与陆地示意面，水体颜色和自动色标随帧变化。上述检查仅限该案例、变量与所列视角/帧段；未复现第二帧失色，不外推到其他条件。8767 已恢复 `candidate`。本次只记录所列克隆与 UI 求解流程的技术证据，以及上述限定的主案例可见检查。

### 2026-10-22 Sol：Nfix 主案例 3D `abiotic_water_sO2W` 高速播放补充

8766 当前 `nfix_on` 主案例与先前记录的 `cyanobacteria_competitor_sDW` 仰视 frame 0–2 检查保持不变。本次对 3D `abiotic_water_sO2W` 在普通斜视下从当前 frame 2 以 8 fps 目标播放至 frame 23；新增成功帧 22，实际 8.0 fps，整帧 P95 30 ms，绘制超预算 0/22。终帧仍显示动态水体着色和更新后的色标；水域有效值189、缺测0、几何缺失0。首页引用 `viz3d.js?v=79`，8766 实际服务脚本与工作区当前源码 SHA-256 完全一致（`85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`）。本次只覆盖 `nfix_on` 下所列的 `abiotic_water_sO2W` 普通斜视播放，以及前述 `cyanobacteria_competitor_sDW` 仰视短帧段；均未复现第二帧后缺色，也不代表用户未指明案例、变量、相机或帧段的原始故障已复现或排除，不能外推至其他条件。

### 2026-10-22 Sol：Nfix 主案例蓝藻仰视 frame 0–2 独立复测

在 8766 可见 UI 中明确将 `cyanobacteria_competitor_sDW` 播放范围设为 frame 0–2、速度设为 1 fps，并使用仰视（bottom-up）相机；播放正常停止于 frame 2。此次测得3帧成功、整帧 P95 38 ms、绘制超预算 0/3；水域有效值189、缺测0、几何缺失0。frame 2 的水体色场和色标仍可见，仰视镜头正确隐藏湖底与陆地示意面。该测次是 `nfix_on` 主案例、该变量、该视角和指定短帧段的独立记录，与前述36 ms测次分开保留；仍未复现原始未明确案例/变量/镜头下的缺色报告，不据此宣称原始问题已复现或对所有条件排除。

### 2026-10-22 Sol：Nfix 主案例 2D 两指标 frame 0–2 播放交叉复核

在 8766 当前 `nfix_on` 主案例，通过 2D 播放控件分别对两个顶层指标设置 frame 0→2、1 fps，两个测次均正常停在结束帧 frame 2。`cyanobacteria_competitor_sDW` 色标由 frame 0 的 0.0497302711–0.0498522222 变为 frame 2 的 0.0487246327–0.0494342558；实际 1 fps、3帧成功、整帧 P95 18 ms、绘制超预算 0/3。`abiotic_water_sO2W`（g/m³）色标由 frame 0 的 8.522958755–8.608160973 变为 frame 2 的 8.541186333–8.694016457；实际 1 fps、3帧成功、整帧 P95 27 ms、绘制超预算 0/3。Sol 已核对服务版本为 v79、served/current 工作区哈希一致。该复核仅适用于此案例、两个顶层指标和所列短帧段，不代表其他指标或设备；不据此外推所有条件。

### 2026-10-22 Sol：Nfix 主案例 2D/3D 全区间播放与交互复核

8766 已重新加载 `nfix_on` 主案例：24帧，覆盖 2020-DOY001 01:00 至 DOY002 00:00，189个湿格、6层。2D `temp` 从 frame 0 播放至23，目标12 fps；24帧成功，实际12.1 fps，整帧 P95 4 ms，超预算0/24，慢间隔6次；自动色标由首帧14.74469–15.07436变为终帧12.00648–12.92841。3D `temp` 在斜视下以8 fps播放全区间，24/24帧成功，实际8.0 fps，P95 30 ms，超预算0/24、慢间隔0；播放到frame19时拖动旋转，播放继续至23，终帧水体可见且保持旋转后的镜头。3D `cyanobacteria_competitor_sDW` 以8 fps播放frame0–23，24/24帧成功，实际8.0 fps，P95 32 ms，超预算0/24；水域189有效、0缺测、0几何缺失，动态色标从frame2约0.04872–0.04943变至frame23约0.04446–0.04513。暂停/续播另测：该变量在frame3（04:00）暂停1.4秒，帧号未变；续播到设定的frame5（06:00）并自动停止。切换变量 `temp`→`cyanobacteria_competitor_sDW` 后实测旋转视角保持。证据限定为该 `nfix_on` 当前样例、当前小网格设备、两个指标和所列24帧区间/交互；不外推至所有变量、案例或设备。原始报告未指定的案例/变量/相机条件下的颜色消失仍未复现。总体用户流程仍为 **Partial**；三学术案例及正式五轮状态不因本次播放证据改变，正式五轮仍为 **0/5**。

### 2026-10-22 Sol：Nfix 主案例无垂向层流速变量 2D/3D 全区间播放

在 8766 当前 `nfix_on` 主案例（24帧、189个湿格、6层）对无垂向层的东西向流速 `u`（m/s）分别检查 2D 与 3D。2D 显示平面场，范围 frame 0–23、目标12 fps，24/24帧成功，实际12.1 fps，整帧耗时3 ms、P50 3 ms、P95 4 ms，绘制超预算0/24，自动停止于 DOY002 00:00。切换到3D后界面自动进入“变量高度表面”，Z 表示变量值而非水深；同为全区间，目标8 fps，24/24帧成功，实际8.1 fps，整帧耗时51 ms、P50 57 ms、P95 89 ms，绘制超预算0/24、帧间隔超过目标10%共2次。自动色标/范围逐帧变化，3D终帧范围 min −0.03119928203523159、max 0.06620388478040695，播放停止于 DOY002 00:00。以上仅限该案例、`u` 变量、当前设备和24帧播放，是技术播放验收，不是科学验证，不能外推至其他变量、案例或设备。总体仍为 **Partial**；学术案例限制和正式五轮计数不变（**0/5**）。

### 2026-10-22 Sol：UI 克隆藻类实例与初始总量限制复核

在隔离的当前 UI 克隆案例 `cyanobacteria_ui_probe` 中，克隆来源蓝藻与新实例在 t0 的 `sDW` 均为 0.1 gDW/m³，因此相同功能群的初始总生物量从 0.1 增至 0.2 gDW/m³。该输出共21帧，覆盖0–1200 s（20 min）；末帧两个实例的个体均值分别约为0.099770606和0.099898520 gDW/m³。现有捕食者/消费者食谱未自动增加对新实例的连接。由此确认当前克隆流程复制初值和已有耦合，不会自动分摊来源初始量，也不会自动改写消费者食谱；该技术流程不构成公平对照或竞争生态合理性证据。UI 来源选择提示现明确说明这些影响，并提示公平竞争试验需预先设计/分配总初始生物量、显式编辑食谱和耦合；不会自动重缩放科学参数。证据仅限此隔离 UI 案例与20分钟输出，不代表任何物种竞争结论或其他案例。总体用户流程仍为 **Partial**，三个学术案例的科学验证门槛及正式五轮 **0/5** 均不变。


### 2026-10-22 Sol：Theoretical Lake 年周期竞争设计的一日三臂试跑

在隔离 `build/real-use-validation-20261022/theoretical-lake-seasonal-competition/` 中，从同一 Theoretical Lake 源快照分别运行 A 单藻全量初值、B 两个同参实例均分 D/N/P/C 初值且均关闭固氮、C 同 B 但仅克隆实例打开 `lNfix`。三臂各完成 2020-01-01 至 2020-01-02、2 s 步长的 43,200 步，按12小时输出共3个时点，均 exit 0。A/B 聚合藻类水体、沉积物和沉积物-PV 的12个 D/N/P/C 状态在每个有效网格上与 A 精确一致；A/B/C 分别扫描864/944/944个数值变量，均无未掩膜 NaN/Inf 或负的藻类 D/N/P/C 状态。

C 出现待查的氮固定诊断异常：`cyanobacteria_competitor_wNFix` 在12h和24h两个时点的全部2,800个有效水格/垂向值均为负，单位 g/m³/s；最小值分别为−6.77008394e−10、−6.32035979e−10。其 `aNLim` 同时大于1；而 A/B 的非固氮蓝藻 `aNLim` 也在两个时点的全部有效值大于1（最大1.12466407），与工作区 WET 源码给出的[0,1]限幅不符。源码公式会把超1诊断值映射成负的 `wNFix`，并将它作为藻类氮状态方程中的加项，因此在数学上表现为氮汇；源码没有设计反向固氮/外部交换过程。该运行版与工作区诊断行为为何不一致尚未判定。当前工作树 `phytoplankton.F90` SHA-256 为 `0cb7befd44094b8c53c9d82c9d49554e5ae798feca5217915d12b591575cf56c`（修改时间 2026-10-22 02:24:46 +08:00），求解器 SHA-256 为 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`；这些只是独立文件标识/时间快照，没有构建记录证明该 exe 由当前工作树源码编译。异常可能来自二进制与工作树源码不一致，或输出诊断映射/运行链问题，具体未定。没有截断或修正异常，也没有继续长窗运行；不能把 C−B 差异作为固氮或竞争的阳性生态结论。

一日吞吐粗略线性估算约31.8小时/365天/臂，尚未计启动与输出硬件开销；本轮不做全年运行。此为 Theoretical Lake 代理机制/技术试跑，不是观测验证，也未完成全系统 C/N/P 收支闭合。原始源案例14个输入文件和 `getm_cartesian.exe` 的前后哈希均不变；运行输出、逐臂哈希、审计脚本、diet mapping、NetCDF扫描及异常坐标详见[三臂试跑报告](../../../build/real-use-validation-20261022/theoretical-lake-seasonal-competition/pilot-results.md)。总体状态继续为 **Partial**；学术案例限制及正式五轮 **0/5** 不变。

### 2026-10-22 Theoretical Lake 源链接候选求解器隔离复测

为追查此前生产 solver 的 aNLim>1/负 wNFix 现象，检查到 `3DWET/bw-nfix` 与 `3DWET/iw-nfix` 的隔离 CMake 构建：WET build.ninja 使用当前工作树 `3DWET/src/wet/src/phytoplankton.F90` 路径；源文件 mtime 02:24:46、SHA-256 `0cb7befd44094b8c53c9d82c9d49554e5ae798feca5217915d12b591575cf56c`，目标对象 mtime 02:34:35、SHA-256 `ae6f848a0b5637e70098727f260563ab8f5392f84d28e98f97e83ee7a4db417f`；GNU Fortran 16.2.0，FABM Ninja/GETM MSYS Makefiles，隔离 solver SHA-256 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672`。源码输入路径与对象后于源码的时间戳是较强 source-link 证据，但没有构建时源码摘要或可验证的对象来源记录，因此不是精确构建对应关系的加密证明。

候选第一次启动遇到 `0xC0000139 STATUS_ENTRYPOINT_NOT_FOUND`。PE 导入/导出审计定位到具体冲突：UCRT64 `libnetcdf.dll` 导入 `H5Pset_fapl_ros3`，但同目录 UCRT64 `libhdf5-320.dll` 未导出；包内 HDF5 DLL 导出该符号。将包内 runtime DLL 集复制到隔离 `runtime-packaged` 并用仅指向该副本和 Windows system directories 的进程 PATH 后，A/C 顺序运行成功；未替换二进制或修改运行服务。

隔离 candidate A/C 均为一日、2 s 步长、0/12/24 h 三条记录。A exit 0/316.874 s/864 个数值变量；C exit 0/348.13 s/944 个数值变量。两个输出均无未掩膜 NaN/Inf、无负 D/N/P/C 状态；所有 aNLim≤1。C 原藻与 competitor 的 wNFix 均为0（每组 8400 个有效样本），此前报告的 aNLim>1 和负 competitor wNFix 未由此 candidate 复现。因而 C 的 `lNfix=true` 未激活可测固氮，本次没有实际测得 C-vs-A 竞争效应。此结果支持此前异常来自不同的 solver/build/runtime 链，但未证明异常的唯一原因，也不证明 candidate 的确切编译源码字节；B 未用该 candidate 重跑。生产 solver `3DWET/bin/getm_cartesian.exe` 前后 SHA-256 均为 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`。完整 build、DLL、运行和扫描哈希见[源链接隔离复测记录](../../../build/real-use-validation-20261022/theoretical-lake-seasonal-competition/source-matched-solver/investigation.md)及更新的 [pilot integrity](../../../build/real-use-validation-20261022/theoretical-lake-seasonal-competition/pilot-integrity.json)。仍仅为 Theoretical Lake 代理技术检查，不是科学验证，未完成全系统元素收支闭合。整体状态保持 **Partial**。


### 2026-10-22 Theoretical Lake：合成低 DIN 固氮压力正控未触发

在新的隔离目录 `build/real-use-validation-20261022/theoretical-lake-seasonal-competition/low-din-positive-control-20261022/` 顺序运行已审阅的 B-off、C-on。两臂均为 2020-01-01 至 2020-01-02、2 s 步长共 43,200 步，按 6 h 输出 5 个时点。合成水体初值 `sNH4W=0.001`、`sNO3W=0.005 gN/m³`；两臂三条入流的全部有效 NH4/NO3 浓度记录均置0，流量、出流、气象、水动力和其余强迫保持不变。B 两实例均 `lNfix=false`；C 仅克隆打开 `lNfix=true`。使用 SHA-256 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672` 的隔离 source-linked candidate 与独立 runtime-packaged 副本；生产 solver 未运行，当前生产 solver SHA 与既有记录相同。

正控未触发：B 与 C 的蓝藻和克隆 `wNFix` 均在全部 14,000 个有效样本中严格为0；`aNLim` 均处于[0,1]，初始诊断帧空间均值0，之后每个6小时帧均值1。两份 NetCDF 的944个数值变量逐值完全一致；两臂各扫描24个藻类水体/沉积/沉积孔隙水 D/N/P/C 状态、每臂235,200个有效值，未发现 NaN/Inf 或负值。合计水体 NH4 均值从0.00100000升至0.00633593 gN/m³，NO3从0.00500000降至0.00379105 gN/m³；12项合计 D/N/P/C 初末均值相同于 B/C。故没有测得固氮激活或 B→C 响应；按设计停止，不继续调配方。此为可证伪的合成机制探针，不是实湖/论文复现或科学有效性证据，也没有完成全系统 C/N/P 收支。

C 的进程退出码为0（343.336 s）；B 的 GETM 日志明确显示 `Completed`（约346.59 s），但异步启动器未保留进程句柄，因此操作系统退出码未捕获。完整运行、输入、强迫字段、runtime、日志、输出和扫描哈希见[低 DIN 正控完整 integrity](../../../build/real-use-validation-20261022/theoretical-lake-seasonal-competition/low-din-positive-control-20261022/run-integrity.json)及[试跑报告](../../../build/real-use-validation-20261022/theoretical-lake-seasonal-competition/pilot-results.md#synthetic-low-din-mechanism-stress-positive-control-2026-10-22)。总体流程仍为 **Partial**；学术案例限制和正式五轮 **0/5** 不变。

### 2026-10-22 Sol：当前克隆案例 2D/3D 水温与蓝藻跨视图连续播放复核

8766 当前页面加载案例 `theoretical-phyto-clone-current-ui`，共21帧，时间为 2020-DOY001 00:00–00:20。服务 HTML/Src 引用 `viz3d.js?v=79`，health 为 ready，instance_id 为 `f687f1f82baf44718812d161e3eba618`。本次只检查该本地当前案例中的水温 `temp` 与克隆藻 `cyanobacteria_ui_probe_sDW`。水温 frame 0 色标为常量12，后端 frame 0 min=max=12；frame 1 后端范围为 11.959671–11.99599266，frame 2 为 11.94–11.99，UI frame 1 截图中可见水面着色。3D 克隆藻 UI frame 1、2 的水面均可见着色，色标随帧变化。

3D 克隆藻一次从 frame 2 播放至 frame 20 并在结束帧停止；计数为21，实际帧率12.1 fps（目标12 fps），整帧 P50/P95 为37/52 ms，超预算0/19，慢间隔0。3D 水温完整播放 frame 0–20，21帧完成；实际12.1 fps（目标12 fps），整帧 P50/P95 为36/39 ms，超预算0/21，慢间隔1。2D 水温 frame 1 色标范围与3D frame 1一致；完整播放 frame 0–20，21帧完成，实际12.1 fps（目标12 fps），整帧 P50/P95 为5/6 ms，超预算0/21，慢间隔0；末帧色标为11.75–11.95。

本次在所述当前加载案例和所列变量/视图条件下，没有复现“第二帧起无水体颜色”或动态色标锁定。原始报告所指案例、变量和条件未知，因此不能据此宣称未知原案例已修复；此证据只限上述本地案例及变量，不代表其他案例、变量、设备或完整用户流程。总体状态仍为 **Partial**，不构成科学验证。


### 2026-10-22 Sol：Erken nfix_on 窄视口水温全区间实播（独立测次）

Sol 在实际 8766/v79 页面加载 `build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/mechanistic-nlimited-sensitivity-20261022/nfix_on`，在窄视口 520×709 下检查24帧（2020-01-01 01:00–2020-01-02 00:00）、189个湿格、6层。页面画面和控件需纵向滚动才能同时查看。2D `temp` frame 0–23 全区间完成24/24帧，目标12 fps、实际12.0 fps，整帧P50/P95为3/5 ms，绘制超预算0/24，慢间隔5次；首帧色标14.74468899–15.07435703 °C，末帧12.00648022–12.92840767 °C。3D `temp` frame 0–23 全区间完成24/24帧，目标8 fps、实际8.0 fps，整帧P50/P95为27/34 ms，绘制超预算0/24，慢间隔0次；播放中进行一次向上拖动旋转，继续播放并到达frame 23，色标动态更新。2D的5次慢间隔是帧间隔超过目标，不是绘制超预算；本次两视图绘制超预算均为0/24。可视水域统计为189有效、0缺测、0几何缺失。

这是 Erken 真实湖形/气象资料基础上的24小时技术敏感性演练；营养盐和生态条件仍使用 proxy，非观测科学验证。性能读数仅适用于本机、520×709窄视口和本次水温变量；旋转证据只是一回向上拖动后的连续播放，不证明所有相机操作已验证。本次未改代码、案例或求解器，8766无需重启；页面仍停留在该活动案例和3D图。此记录与状态文档中其他日期、案例和视口的测次独立，不合并性能统计。


### 2026-10-22 Sol：Erken nfix_on 3D competitor 藻播放与仰视入口复核（独立测次）

在 8766/v79 当前 Erken `nfix_on` 活动案例（`build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/mechanistic-nlimited-sensitivity-20261022/nfix_on`；24帧、189湿格、6层）中单独检查 3D `cyanobacteria_competitor_sDW`。首帧自动色标0.04973027–0.04985222 gDW/m³，末帧0.04446157–0.04512702 gDW/m³。目标8 fps 全区间播放完成24/24帧，实际8.0 fps，整帧P50/P95 25/32 ms，绘制超预算0/24，慢间隔1；末帧水域有效189、缺测0、几何缺失0。随后将镜头下拉切换到“仰视”，UI 确认为 `viz3d-camera=仰视`，水体颜色仍可见，状态提示“水体底视：已隐藏湖底与陆地示意平面”。这是该视角入口可达并能显示场值的检查。与前一条水温播放中的单次向上拖动不同，本测次在末帧检查仰视，不据此泛化所有相机角度或所有拖动期间的连续播放行为。

该 `nfix_on` 是 Erken 真实湖形/气象资料上的短时技术敏感性案例，营养盐和生态条件仍为 proxy。播放帧及色标变化只证明此本机 UI 对该变量的动态可视化，不是藻类变化的生态科学验证。性能结论仅限本机、该案例、该变量和本次设置；本记录与其他变量/视口测次独立。Sol 将页面留在活动案例的仰视 3D 图；没有改代码、案例或求解器，8766 无需重启。

### 2026-10-22 Sol：Erken nfix_on 水柱与 DO 可视性补充（独立测次）

在 8766/v79 的 Erken `nfix_on` 案例中检查 3D 水体模式，视角为仰视，层位 `-1`（5/5），189 个湿格。手动查看 `temp` frame 0→1，色标由 14.7447–15.0744 变为 14.6224–15.0350 °C；再查看 `abiotic_water_sO2W` frame 0→2，frame 2 色标为 8.5412–8.6940 g/m³，彩色水体保持可见。DO 全 24 帧播放（目标 8 fps）完成 24/24，实际 8.1 fps，整帧 P95 30 ms，绘制超预算 0/24、慢间隔 0 次；frame 2 截图显示水体着色、189 个有效湿格、无缺测水格或缺失几何。

此测试条件下没有复现所报告的水体颜色消失；结论仅限本案例、本机、这两个指标、该视角/层位和所测试帧段，不能据此宣称所有变量或案例均已修复。随后页面恢复为 `cyanobacteria_competitor_sDW` frame 23 的仰视。仅做只读验证和文档更新，未改应用源代码、案例或求解器，未操作浏览器或切换活动案例；8766 不需重启。该状态记录与前述不同视口/指标的测次独立，不合并性能值。

### 2026-10-22 Sol：Erken 24h 包迁移后 8768 可见 UI 验收

Sol 在隔离服务 `http://127.0.0.1:8768/` 中从 `build/relocation-8768/model-root` 重开 `ErkenRealLocation24h-relocated`；Dashboard 显示24个输出时步。2D `temp` 播放实际前进并更新色标，目标/实际1.0 fps，整帧P95 32 ms，绘制超预算0/7。3D 水温从 frame 7 播放到14，湖盆显示376个湿格、缺测0、几何缺失0，水体颜色保持可见，色标范围至2.18005–2.18787 °C；目标/实际1.0 fps，整帧P95 69 ms，绘制超预算0/8。播放期间3D空间剖面有意暂停刷新：界面注明当前剖面保持frame/time 8，而主图推进到15，因此剖面静态是播放时的预期行为。迁移副本、输入/输出、app 源及来源 hash 证据见[8768 relocation handoff](../../../build/relocation-8768/evidence/relocation-handoff.md)、[逐文件哈希](../../../build/relocation-8768/evidence/relocation-hashes.json)和[服务/API核验](../../../build/relocation-8768/evidence/service-verification.json)。本次是本机迁移包的限定 UI 播放核验，不证明其他变量、视图或设备，也不构成科学验证；原始用户缺色案例仍未确定。该 package 使用 CC BY 4.0 的 SITES 地形/气象/温度资料，但包含单站气象空间广播、云量50%与蒸发0占位、无实测流量、营养/生态 proxy 及15.5m以下端点外推，具体限制见 handoff。Sol 完成 UI 检查后于 07:03:21 +08:00 仅停止本次启动的 8768 服务进程（PID 22612、51044），端口已释放；8766/8767 仍 ready，未停止。

### 2026-10-22 Sol：Erken nfix_on 3D 水温完整播放复核

在当前 8766/v79 页面，以 Erken `nfix_on` 案例的 3D `temp` 完成 frame 0–23 全区间播放：24/24 帧，目标/实际 8.0 fps，帧 P50/P95 为 26/28 ms，绘制超预算 0/24、慢间隔 0。自动色标从 frame 0 的 14.74468899–15.07435703 °C 变为 frame 23 的 12.00648022–12.92840767 °C；播放后及 frame 2、23 检查均可见有色水体。首页引用 `viz3d.js?v=79`，served JavaScript 与工作区 SHA-256 一致（`85745D4C99AD65EEA9DF1E24F3200C303685AFB3467DC5583977820F54D87F9D`）。该测次未复现报告中的颜色消失；原始案例、变量及条件仍未知，不能外推至未知原案例、其他变量/视角/设备或完整用户流程。当前代码路径已有此前记录的 Plotly trace 更新数组维度修正；本次未改应用代码、无需重启，也未运行测试。

### 2026-10-22 Arreskov 精确复现来源审计

**状态：Blocked；未运行模型。** 独立审计及下一步实验定义见[Arreskov source audit](../../../build/academic-case-validation-20261022/arreskov-source-audit/AUDIT.md)，下载/副本文件的来源 URL、日期、字节数、SHA-256 和许可/条款见同目录 `file_provenance.csv`。审计区分了两个不能混作同一个目标的研究：**Nielsen et al. (2014) 0-D PCLake** 使用 1992–2009 数据、22 个手工调整参数、350 参数敏感性筛选和 900-run 参数 ensemble，并定义了气候变暖与 N/P 负荷扰动；**Andersen et al. (2022) 1-D GOTM-WET** 使用 2 年 spin-up、1992–2005 校准、Parsac 0.5.7 与 210 个候选校准参数，约 350,000 次参数评估后按六种策略选出每组 130–141 个参数化，并将基线和 ±75% 负荷场景延展至 2024。2014 PCLake 的 900-run/变暖场景不能用 2022 GOTM-WET 案例替代复现。

本仓库 `3DWET/src/wet/testcases/lake_arreskov_denmark/` 有天气、进出流、化学负荷调整、水位、湖盆 hypsograph 和鱼类干预文件；当前 `gotm.yaml` 配置 1990–2004，气象/流量文件本身延伸到更晚年份，但这不改变已配置运行期。关键缺口是无湖泊专用 `fabm.yaml`、匹配的论文模型源码/构建身份、观测时间序列、校准/ensemble 参数成员与脚本、以及模型输出。2022 论文补充材料和两篇论文可以建立有限的图表/指标 benchmark，但没有填补可执行模型包或 member 级结果；精确复现仍需作者提供版本化配置、观测/强迫来源、ensemble 文件和许可说明。2014 KNAW PDF 仅允许私人研究使用、不得进一步分发；补充材料及 case 输入包的单独再分发许可也未确立。此审计未改模型代码、原始 case、STATUS 主结论或桌面应用；学术复现门槛仍未通过。

### 2026-10-22 N-fix 限制因子源代码与运行证据收口

时间线已核清：2026-10-21 “无可用 Fortran 编译器，因此 clamp 尚未编译/重跑”是当时状态；之后用户级 MSYS2 UCRT64 工具链可用，并已有 2026-10-22 的隔离候选运行记录。旧候选 `902a7db6…56df672` 有 CMake 源路径、时间戳和源码/二进制哈希等强链接证据，但无构建时源哈希证明，不能据此声称其精确对应某个源码字节快照。

为关闭这一来源缺口，本次在新目录 `build/nfix-build-audit-20261022/` 从当前源码干净构建并实际运行新候选。编译器为 GNU Fortran 16.2.0、CMake 4.4.4、Ninja 1.13.2。构建后当前 `phytoplankton.F90` SHA-256 为 `0cb7befd44094b8c53c9d82c9d49554e5ae798feca5217915d12b591575cf56c`，`macrophytes.F90` 为 `73f192052904f7e87cf1259a8afc2a7d6732f0c4cf1fc71d4994038a14d14619`；CMake/Ninja 图指向这两个工作区文件。新隔离 solver SHA-256 为 `863d0b4b90117a951bd8f60f797c8d0023b062739e40d120bbc7620bb48c20ff`。这是有干净 build tree、完整日志和源指纹的当前源码运行证据；编译器未把源指纹嵌入 EXE，故不是二进制内嵌或可复现构建证明。

新 solver 先通过低 DIN `nfix_off/on` 24小时成对机制检查：两臂各有27,216个水柱样本；off `wNFix` 严格为0，on 为 `5.724e−10–7.187e−10 gN/m³/s`。66个数值变量无未掩膜 NaN/Inf 或负存储状态。根据当前 Droop 公式由输出状态重算，`aNLim` 与 `aPLim` 均在[0,1]；N:D、P:D 均在配置范围内。随后新 solver 完成 Erken 真实湖形/单站气象输入的 `no_extra_competitor`、`nfix_off`、`nfix_on` 三臂24小时运行，全部 exit 0。off/on 仅有 `lNfix` 的解析模型参数差异；每臂24帧、376个湿表层格。off 的 `wNFix` 在90,240样本中全为0；on 在90,240样本中全为正，范围 `5.0646e−10–7.2546e−10 gN/m³/s`。`aNLim/aPLim` 均在[0,1]，N:D、P:D 在配置范围；扫描各臂 `output.nc`、2D和3D输出的数值变量，均无未掩膜 NaN/Inf 或负状态。新旧候选的九个生成输出文件 SHA-256 全部相同。

该结果确认限制因子修复在当前源码构建中运行，且在刻意设计的低 DIN 条件下产生有界、非负的小幅 N-fix 通量；24小时生物量变化仍可忽略。Erken 湖形、气象和温度剖面输入来自真实资料，但营养盐/生态初值为 proxy，低 DIN 和克隆群组配额是人为机制设置。这不是 Erken 生态验证、季节响应、有效竞争结论或全系统 N/P/C 收支闭合。8766 当前 UI 的独立只读检查还在 3D `nfix_on` 中观察了 `cyanobacteria_competitor_sDW` 与 `wNFix` 的 frame 0–2、189个有效湿格、0缺测值、变化色标及8 fps连续播放；它仅验证该本机案例/视图/变量的可视化。

生产 solver 未运行、覆盖或替换，`3DWET/bin/getm_cartesian.exe` SHA-256 仍为 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`；8766/8767 未用于隔离运行、未重启。桌面应用代码没有变化。完整命令、build/runtime 指纹、逐臂输入与输出哈希、数值扫描及解释边界见[N-fix 源与运行 provenance 审计](../../../build/nfix-build-audit-20261022/REPORT.md)。总体用户流程和学术验证状态保持 **Partial**；正式五轮仍为 **0/5**。

UI 证据补充：8766 `nfix_on` 案例中，3D `abiotic_water_sO2W` frame 0–2 的色标分别为 8.52296–8.60816、8.53202–8.65224、8.54119–8.69402 g/m³；水域189个有效格、缺测0。该逐帧读数和 `cyanobacteria_competitor_sDW/wNFix` 检查均为同一案例的限定 UI 呈现证据。

### 2026-10-22 Erken cohort split：隔离桌面 GUI 与镜头拖拽

在全新隔离根 `build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/ui-isolated-root` 的8769真实UI中，原始 `cyanobacteria_sDW` 与 `cyanobacteria_lowlight_cohort_sDW` 的2D/3D分别完成24/24帧，时间推进、自动色标与彩色水体均可见；仰视预设时水域376格有效、缺测0、几何缺失0。2D目标12fps实测12.1/12.2fps、P95各6ms；3D仰视实测11.7/11.6fps、P95 64/52ms；绘制超预算均0/24。Sol独立在同一8769服务以2fps对lowlight 3D播放中真实拖动画布：中途2/2、18/18均保持水色、同一向上倾斜视角与时间/色标更新；最终24/24、实际2fps、P95 40ms、超预算0/24。详细隔离路径、指标口径和各帧状态见[GUI_REPORT.md](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/GUI_REPORT.md)。

这是代理生态初值下的单一模型机制演示，不是科学验证；无A单cohort、B同参等量双cohort、C仅改性状三臂对照，不能把同次运行内两组轨迹差异归因为竞争。原始缺色报告的案例/变量/层/相机仍未确定，本测次不构成全场景修复证明。暂停续播、平移和缩放未验证；UI逐变量选择，本轮无并排对照。没有源码变化；测后由启动launcher正常停止8769，8766/8767未触碰。

### 2026-10-22 Sol：仰视下 3D 氧与蓝藻实播

在用户当前打开的 8766/v79 页面，对 Erken `nfix_on` 案例、3D 水体模式、仰视镜头、表层（layer 5/5）执行实际连续播放。`abiotic_water_sO2W` frame 0–2 播放 3/3 帧，目标8 fps、实际8.3 fps，整帧 P95 38 ms、绘制超预算0/3；色标依次为 8.52296–8.60816、8.53202–8.65224、8.54119–8.69402 g/m³。随后 `cyanobacteria_competitor_sDW` frame 0–2 播放 3/3 帧，目标8 fps、实际8.4 fps，整帧 P95 35 ms、绘制超预算0/3；frame 2 色标为 0.0487246–0.0494343 gDW/m³。两项播放都在帧 2 保持水体着色，时间标签与自动色标随帧更新，水域189个有效格、缺测0。测试后恢复原页面的 `temp` frame 23、仰视和0–23播放范围。

这次在该真实案例、两个指标、仰视和表层条件下没有复现“第二帧以后只剩陆地框架”；它不证明未知用户案例或其他变量/相机/设备均无此问题。此前查阅的代码为每帧同步更新3D网格与变量数组，结构变化/更新失败会完整重绘；对应定向 JS 回归测试由实现侧报告通过。此项实际 UI 证据由 Sol 前台确认。

补充同一用户前台页面的 2D 播放：`cyanobacteria_competitor_sDW` 在表层、frame 0–23 连播完成24/24帧，目标/实际8.0 fps，整帧 P95 4 ms，绘制超预算0/24；终帧自动色标范围为 0.0444616–0.0451270 gDW/m³。随后回到 3D `temp` frame 23、仰视。该项只验证 Erken `nfix_on` 当前数据中的 2D 显示、播放和自动范围随帧变化。

### 2026-10-22 克隆藻类初始份额分摊功能验收边界

Luna 增加了可选的等总量初始份额模式；默认克隆行为不变，严格限制 `0 < fraction < 1`，必须显式提供所有注册、有限、质量浓度状态，预览并确认后才提交，失败会回滚。专测与现有网络/事务测试报告为58 passed，`node --check` 与 `py_compile` 通过。指南已说明此操作只分摊同功能群 cohort 的初值，不构成物种/性状竞争。当前 8766 服务仍为旧进程（PID 11476）：静态脚本 SHA 与源码一致，但 Jinja 首页缓存仍引用 ecology_network.js v4，而工作区 index.html 已是 v5，因此新克隆模式尚未在当前已打开页面可见。准确服务进程的停止命令被环境策略拒绝，本轮没有尝试绕过，也没有改动活动案例。应用同步尚待由正常关闭/重启流程完成；不得将该功能说成当前 8766 已加载。

### 2026-10-22 Erken 等总量 cohort split 技术试验（非 UI 验收）

隔离副本将蓝藻12个初始注册状态等分到原 cohort 与低光最适 cohort，逐状态总量误差0；克隆只将 `cLOptRef` 从23调整到12 W/m²，并为 `burial`/`inorganic_carbon` 增加第4个 phytoplankton 端口。真实 Erken 网格上24小时求解 exit 0，24帧；两组生物量都非负且所有未屏蔽样本有限，最终均值分别0.141070/0.143105 gDW/m³。Flask test client 中 clone变量清单、2D/3D结果端点均返回200。此为模型机制运行测试，初值/营养状态为proxy，**不是生态验证、竞争结论或桌面 GUI 验收**。新案例未加载到 GUI；8766/8767 未触碰。未改源码，桌面同步不适用。详见[实验报告](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/REPORT.md)。

### 2026-10-22 Erken 三臂 cohort split 对照补充（离线）

**更正：此 A/B/C 运行无效于性状检验。** 三臂 `getm.inp` 的 `metforcing=.false.`，solver 日志也明确为 `Metforcing=F`；虽有 `meteo.nc`，实际并未启用气象强迫。全零 PAR 诊断和 B/C 零差异不能说明 `cLOptRef` 无响应。保留该运行及哈希作失败配置记录；后续须在隔离副本启用强迫并通过白天 PAR 正值 smoke gate 后再分析。

隔离目录 `build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-abcs-20261022/` 完成 A 单 cohort、B 等总初始状态的同参双 cohort、C 仅改变 clone `cLOptRef=12` 的24小时运行，三臂 exit 0。初始12状态拆分守恒误差0；A/B `sDW` 轨迹仍有最大绝对残差0.00212051 gDW/m³、最终帧相对RMSE约0.707%，且A/B实例/端口拓扑不同。B/C对比残差全为0；PAR、光限制与生长通量诊断为0，故没有测得cLOptRef响应或竞争效应。状态健康与逐帧指标、哈希和运行时间见[实验报告](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-abcs-20261022/REPORT.md)。这是proxy条件的离线机制演练，不是生态验证/校准；不是桌面GUI验收，新案例未加载到UI，8766/8767未触碰。未改源码，应用同步不适用。

### 2026-10-22 Sol：Erken A/B/C 主动气象强迫复测（离线）

新隔离副本显式启用 `metforcing=.true.`；27小时 C smoke 的日志确认 `Metforcing=T`，直接 `swr` 白天为正，24小时 temporal-mean 预热后 PAR/光限制/生长通量诊断激活。A/B/C均 exit 0，配置48小时、5秒步长，`output.nc`为三臂共同47帧（01:00至47:00，无48小时端点样本）。A/B `sDW`最大绝对残差0.00355413 gDW/m³；A为3个phyto实例、nPHYT=3，B/C为4个、nPHYT=4，存在拓扑限制。B/C同拓扑同总初值；clone `aLLim`末帧均值差0.0797205，聚合蓝藻`sDW`全帧RMSE 1.41573e-4 gDW/m³。proxy营养与空间广播气象下仅表明配置机制响应，不是校准/田野验证/生态竞争结论，也不是GUI验收。源码未改；8766/8767未触碰；桌面同步不适用。详细数据和哈希见[主动强迫报告](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-abcs-active-meteo-20261022/REPORT.md)。

### 2026-10-23 Luna：Erken A/B/C 48小时清洁构建复测（离线机制诊断）

新 attempt06 使用 clean candidate solver SHA-256 `863d0b4b90117a951bd8f60f797c8d0023b062739e40d120bbc7620bb48c20ff`，A/B/C 三个独立副本的 solver subprocess 均 exit 0，日志均记录 `Metforcing= T`；运行时间分别366.386、440.570、440.086秒。相同官方来源代理气象文件 `meteo.nc` 只覆盖2020-01-01 00:00至2020-01-03 00:00，因此未重复或外推强迫，也未声称完成72小时；求解器完整积分至48小时止点，但 hourly `output.nc` 为01:00–47:00共47帧。独立34小时 smoke 在滚动24小时窗后白昼见正 `swr`，33/34小时的 `meanparout`、`aLLim`、`wDAss` 均非零。Smoke 复用了已有日志和 NetCDF，未在该审计调用中启动求解器；原进程返回码与墙钟时间均为 unknown/null。`smoke_manifest.json` 将 solver exit code 与 wall time 记为 null，并将0.029秒仅列为已有产物/哈希审计耗时，不以 `Completed` 日志标志冒充进程退出码。

A 将12项已注册蓝藻状态维持为一个 cohort；B 对原 cohort 的12项状态按50:50拆分且保持 `cLOptRef=23`；C 与B同拓扑，仅克隆 `cLOptRef=12`。逐状态拆分误差为0。所有未屏蔽的已注册蓝藻状态样本均有限、非负，负值计数0。B/C审计指标到hour24仍相同，首个记录差异出现在hour25。解释范围只包括hour25–47的23帧：克隆 `aLLim` C−B帧均值差的均值为+0.07834（最大绝对格层差0.27809），此直接改变的诊断差异不小；source `aLLim`差异很小，聚合蓝藻`sDW`帧RMSE均方根为0.0002024 gDW/m³、均值残差约+0.000163 gDW/m³，聚合状态/水体量的差异整体较小。该结果仅说明此参数/配置下出现机制诊断响应；不能视为食性网络/消费者响应、生态合理性、物种竞争或Erken实地验证。温度输出在B/C逐臂各有266个略低于0°C的未屏蔽样本，最低−0.0128042°C；该质量提示保留，未裁剪。A/B是拓扑改变参考（3对4个phytoplankton实例、`nPHYT=3`对4），不可称等价测试；其post-warm-up `sDW`差异RMSE为0.002758 gDW/m³。无实测营养盐或生态初值；单站气象被空间广播，云量/蒸发为占位值，温度端点延伸到底；仅覆盖冬季48小时、一个窗后白昼。三臂输出 NetCDF 总量约5.46GB（A约1.73GB、B/C各约1.87GB）。输入/输出/日志SHA、逐帧指标及限制见[attempt06报告](../../../build/real-use-validation-20261023/erken-competition-luna-attempt06/REPORT.md)。源码/solver未改，未运行软件测试、未联系8766/8767、未进行GUI验收；桌面同步不适用。

### 2026-10-22 Sol：Ravn 官方默认 GOTM-WET `kNitrW` profile

完成全新隔离副本的21点确定性网格（0.10–0.50 d⁻¹，步长0.02）；21次均调用官方 runner 并 exit 0，各有5844小时输出帧。独立审计确认八项非参数输入hash一致，FABM配置语义差异仅有 `abiotic_water.kNitrW`；每次输出/日志hash匹配，27个登记状态均有限且非负。训练期DO（1996–2000）21点RMSE严格单调下降，2.280571→2.229257 mg O₂/L，最低点为0.50上界；默认0.30为2.239836，最顶端最后0.02仅降0.000730。故此前bounded optimizer贴上界与DO RMSE单调趋势相符；该目标下单参数弱可识别，0.50不可称最佳率定值。训练选择锁定后才对holdout（2001–2005）评分；0.50 RMSE为2.438004 mg O₂/L，默认0.30为2.451091，holdout只作事后比较。此实验不复现完整ParSAC，不是正式率定或独立验证；既有250,670 interior-state repairs仍需数值审查。源码与官方reference未改，8766/8767未触碰，桌面同步不适用。详见[报告](../../../build/real-use-validation-20261022/ravn-knitrw-profile-20261022/REPORT.md)及逐臂证据目录。

### 2026-10-22 Luna：UI cohort split 输出订阅修复与轨迹差异审计

在隔离 UI 克隆案例 `build/real-use-validation-20261022/erken-nfix-playback-isolated/theoretical-phyto-clone-split-ui-20261022` 中，24小时求解 exit 0、输出24帧。2D/3D 上父群和 `cyanobacteria_ui_split_clone` 的 biomass 场均有限并可见；因此这次材料没有复现“第二帧起水体着色消失”。但 `output.yaml` 当时选择的是父群/旧 `cyanobacteria_competitor` 诊断，导致汇总 `output.nc` 缺少新 clone 前缀；全量 `.3d.nc` 中仍有 clone 变量。已在克隆 API 的候选配置生成中增加：复制源实例被明确选择的 `source_*` 诊断到 clone 前缀，保留原选择/频率及其他设置，并对已存在的 clone 选择去重；直接变量的 NetCDF `name` 别名更新为克隆 source 名，发生冲突时使用确定性数字后缀，通配条目的类别名保持不变。新增测试先失败，再通过；`tests/test_wet_instance_transactions.py` 整套结果为44 passed。该回归是 Flask test-client 配置/API 检查，不是 GUI 验收或完整模型复跑。

科学分叉仍未解释：已有汇总为父/clone `sDW` 均值约0.0235867/0.0241507 gDW/m³（约4.1%），最大绝对差约0.0010262；输出 `aNLim` 约1.187，高于当前 WET 源码限幅上限1。源文件 `3DWET/src/wet/src/phytoplankton.F90` SHA256 为 `0CB7BEFD44094B8C53C9D82C9D49554E5AE798FECA5217915D12B591575CF56C`；当前 `3DWET/bin/getm_cartesian.exe` SHA256 为 `98F359433FB6646F5D597D24FE5234B43C1246CB3A9EF8F606BF2E69C5E63AAF`，修改时间为 2026-10-22 15:59:58 +08:00。该可执行文件时间戳晚于日志记录的完成时间 03:14:33，且运行日志无二进制哈希/构建来源；故不能证明这就是该次运行的可执行文件，也不能把超界诊断或轨迹差归因于生物过程。案例的营养/生态条件是 proxy，不是 Erken 场地生态验证。

8766 本轮代码同步由根代理接手：活动案例 API 路径仍为上述隔离副本，HTTP 200，页面资源 `ecology_network.js?v=5` 的服务端文件哈希与源码相同；桌面首页 reload 后显示“未加载案例”，需由根代理完成浏览器端案例恢复和最终 GUI 验收。8767 未触碰。代码改动后进行了43项聚焦事务测试；仅限此测试结果，不代表桌面端验收。

### 2026-10-22 Sol：Erken `cyanobacteria_sDW` 3D 播放中拖动旋转（8766）

活动案例 API 确认为 `build/real-use-validation-20261021/erken-exploratory-paired/nfix-functional-group-sensitivity/mechanistic-nlimited-sensitivity-20261022/nfix_on`，24帧、189个湿格。Sol 在3D `cyanobacteria_sDW` 目标1 fps播放期间拖动旋转镜头；操作后主图仍在推进，帧色标随帧变化，场值水域统计189 valid / 0 missing。交互观察中，拖动结束瞬间播放计时显示约0.4 fps；随后在frame21暂停，计数22个成功帧，快照为目标1 fps、实际0.5 fps、帧耗时P50/P95 102/163 ms、绘制超预算0/22、慢间隔15次、最后绘图71 ms。

从实现看，`PlaybackPerformance.actualFps` 是相邻成功帧完成时间间隔的倒数均值；旋转拖动及随后页面操作所花时间包含在本次会话的帧间隔内。`slowFrames`据帧间隔是否超过目标帧周期的110%计数，`overBudgetFrames`则按单帧耗时是否超过目标周期计数。因此“实际0.4–0.5 fps”准确描述了包含人工交互的这段会话平均帧节奏；它不等于纯渲染耗时或无交互时的稳定播放速度。P95帧耗时163ms且超绘制预算0/22，说明本测次的单帧渲染没有超过1秒目标预算，但15个帧间隔超容差表明交互会话的更新节奏低于目标。当前证据未证明计时器实现错误，也没有隔离测量无交互速度；因此仅更新说明，没有改源码。该次仅覆盖指定Erken案例、3D `cyanobacteria_sDW` 和一次镜头旋转，不外推到其他变量/2D/3D完整流程。8766在此任务中只读验收，无代码改动、无需同步；8767未触碰。

- **2026-10-22 无交互播放节奏与面板不一致（待定位）**：Sol 在同步后的 8766 页面选择 `nfix_on` / 3D `cyanobacteria_sDW`，设置目标4 fps，从 frame14 点击播放；3.035秒后自动停止于 frame23，成功推进9帧，色标变化，189个有效水格/0缺测。面板同刻显示实际0.8 fps、整帧P50/P95 116/131ms、绘制超预算0/9、6个慢间隔。9帧在约3秒内对应约2.6 fps，与面板值矛盾。实现检查发现调度与 `PlaybackPerformance` 使用同一单调时钟，且面板 fps 按相邻成功完成时刻计算；新增确定性遥测测试模拟9条跨约3.035秒的完成记录，得到约2.64 fps并通过。因此单元级计算没有复现该矛盾；浏览器逐帧记录的 `intervalMs` 尚未采集，无法判定是现场遥测时间戳、页面读数时序或墙钟测量边界所致。未改播放计时源代码，也未把此次数值作为稳定速度结论。此证据仅限所列案例/指标/设置，不表示其他2D/3D变量通过；8767未触碰。

- **2026-10-22 播放调度节奏修复及8766复核**：回看上面的4 fps测次，确认调度器在一帧错过目标deadline后，将下一帧deadline重置为“当前渲染完成时刻 + 一个完整播放周期”，因此慢帧后被额外插入整周期空等。实现改为deadline重置至渲染完成时刻；下一帧仍由 `requestAnimationFrame` 门控，并且每次只推进一个输出帧，不追赶、不跳帧。实现见 `3DWET/app/static/js/scientific_workspace.js:342-346`；新增的严重迟到回归断言要求下一次timer delay为0、下一帧之后恢复完整目标周期，见 `3DWET/tests/test_scientific_playback_scheduler.js:73-81`。播放调度和遥测定向测试共5项通过。

  Sol同步并加载首页引用 `scientific_workspace.js?v=14` 后，在同一 Erken `nfix_on`、目标4 fps完成新的24帧UI测次：3D `temp` 为24/24、实际4.0 fps、整帧P50/P95 48/74 ms、绘制超预算0/24、慢间隔0；2D `temp` 为24/24、实际4.0 fps、整帧P50/P95 5/7 ms、绘制超预算0/24、慢间隔0。修复前测的是 `cyanobacteria_sDW`（实际0.7 fps、P95 102 ms、18个慢间隔），修复后测的是 `temp`；案例和目标速度相同，但变量不同，因此不能视为严格的同变量A/B，也不能将性能差异全部归因于调度修复。该结果确认列出的当前案例/变量/设备会话达到目标节奏，不解释用户未知原始案例/变量/条件，也不证明其他案例、变量、设备或完整用户流程已通过。


### 2026-10-22 Sol：Erken external-data candidate 2D `temp` 可见播放（8767）

Sol 在隔离服务 8767 的可见 UI 中加载 `build/real-use-validation-20261022/erken-external-data-real-grid/candidate`。Dashboard 显示44×18网格、376个湿格、10层、3帧。2D `temp` 手动检查 frame 0/1/2 时，自动色标分别为 [2.18004894, 2.18069601]、[2.18004894, 2.18130779]、[2.18004894, 2.18190598] °C，显示范围上限逐帧增加。选择播放范围0–2、目标1 fps，从frame0播放到frame2后自动停止；重复播放的性能面板为目标1 fps、实际1.1 fps、成功帧3、整帧P50/P95 12/122 ms、绘制超预算0/3。该记录未提供缺测计数或逐帧异常指标，故不补推这些数值；暂停/续播和滑块跳帧未验证。

这只是基于真实 SITES 岸线/等深线、气象与温度剖面输入的三帧 UI 技术演示。candidate 的营养盐/生态初值仍是 proxy，天气为单站空间均匀广播，温度剖面底部存在端点外推；结果不构成 Erken 科学验证、校准或其他变量/案例的验收。8766未触碰，8767仅在隔离服务内通过案例 UI 加载目标路径；本次没有源码变更，无需桌面应用同步。服务与输入来源指纹及限制参见[候选报告](../../../build/real-use-validation-20261022/erken-external-data-real-grid/REPORT.md)。

### 2026-10-22 Sol：v80 3D 相机操作与蓝藻动态帧验收（8766）

8766 首页引用 `viz3d.js?v=80`，served JS 与工作区源码 SHA-256 一致：`36E4875D67619B574865F04DD13CBBA921F0E242C4551B32A9B67DF108795E2C`。活动 Erken `nfix_on` 案例的3D `cyanobacteria_sDW` 在 frame 0–23、目标4 fps全程播放；第二帧时切换“斜视→仰视”，截图与色标仍显示蓝色水体数据；继续播放期间切换“仰视→正面”，最终24/24帧，实测4.1 fps，整帧P50/P95 30/40 ms，绘制超预算0/24、慢间隔0。末帧范围0.04446157068014145–0.0451270155608654 gDW/m³；水域189有效/0缺测/0几何缺失。停止后静止切回斜视，彩色水体仍可见。

Sol 另外在同一案例、同一 `cyanobacteria_sDW` 指标完成2D frame 0–23可见 GUI 播放：目标4 fps、24/24帧、实际4.0 fps、整帧P50/P95 3/5 ms、绘制超预算0/24、慢间隔0；末帧范围0.04446157068014145–0.0451270155608654 gDW/m³。这是当前案例/指标及本机可见会话的2D播放证据，不外推为所有2D变量、案例或设备的验收。

本次验收对应程序化相机预设及仰视遮挡层更新与主图帧更新共用 `viz3dQueueDraw`；Plotly 内部指针旋转仍由 Plotly 即时处理。新回归先红（播放帧未释放时相机 `relayout` 提前执行），修复后绿。Sol 独立运行 `node --test 3DWET/tests/test_viz_waterbody_patch.js 3DWET/tests/test_scientific_playback_scheduler.js`，16/16通过。结论仅限上述案例、变量、设备会话和已操作视角，不外推到未明确的原始复现场景、所有变量或设备。此前未修复版本的12 fps快速相机/拖动压力测次为不同受干扰测量，实际0.6–0.9 fps，不与本次目标4 fps的全程验收混算。8766已由Sol同步并确认服务文件哈希；本次文档记录未重启服务。

### 2026-10-22 FABM 状态修复摘要面板（实现与自动回归）

运行状态接口现在仅在当前案例对应的本次任务进入完成或失败状态后，尝试读取本次新建的 `model_run.log` 中 interior/surface/bottom 三项完整统计；运行中不提供最终计数，日志缺项、格式不识别或案例路径已切换时返回“未提供”。面板说明这些是检查事件数；非零提示求解器裁剪过越界状态并建议查看完整日志与结果，不单凭计数判断结果错误或物理无效。自动回归覆盖完整/全零/缺失/旧格式/部分统计、运行未结束、旧日志、案例路径切换和任务重置；`tests/test_run_repair_summary.py` 与 `tests/test_run_lifecycle.py` 共16项通过。尚无桌面GUI验收；本轮未重启8766/8767，待根代理独立审查并同步验证。

### 2026-10-23 Ravn 官方默认时间步长敏感性

同一 Ravn 官方默认副本仅改变时间步长，3600/1800/900秒均完成5,844条输出记录；对应 FABM interior repair 计数为250,670/498,591/1,000,544，surface/bottom为0。相邻步长减半时外部步数约翻倍，按步数折算约1.78次检查事件/步，说明绝对事件数随步数增加；这不是逐格点或逐变量修复量。1800秒训练DO配对RMSE为2.182930 mg/L，3600秒为2.239836 mg/L，但单一评分指标的下降不证明更小步长更合适。三档输出对比没有证明时间步长收敛，也不足以推荐步长。证据为 [`dt=1800` 审计](../../../build/real-use-validation-20261023/ravn-dt1800-sensitivity/audit.json)、两档运行记录及 [`dt=900` 运行记录](../../../build/real-use-validation-20261023/ravn-dt900-sensitivity/sensitivity.json)。

### 2026-10-23 Sol：8766 3D 硅藻跨帧缺色复核

在当前前台 8766、Erken `nfix_on` 案例、表层 `diatoms_sDW` 下，从 frame 0 开始实际启动 3D 播放。UI 从 frame 0 到 frame 2，画面仍有着色水体；变量色标由 frame 0 的 0.0974607–0.0989025 变为 frame 2 的 0.0945244–0.0971534 gDW/m³，水域 189 格有效、缺测 0、几何缺失 0。截图确认水体彩色面仍在，并非仅有地形框架。测试后已恢复原页面为 `cyanobacteria_sDW`、表层、frame 23、斜视。

当前面板在这次受工具观察干扰的短测中报目标 4 fps、实际 0.7–0.9 fps、P95 整帧 175 ms；frame 0–2 确认帧更新和色彩连续，不代表速度达标。相邻 Sol 前台全段同变量验收曾记录 24/24 帧、4.1 fps、P95 40 ms，因此这次短测不能据此推翻全段测次；仍需把浏览器观测开销与实际前台播放分别计时。主页当前返回 HTTP 200，引用 `viz3d.js?v=80`、`scientific_workspace.js?v=14`；`app.js?v=60` 等静态脚本虽缓存版本号较旧，但以上三项服务响应 SHA-256 均与当前工作区源码一致。该复核未改应用代码、未重启服务，未能复现指定 Erken 指标和表层条件下的缺色，不构成所有变量、层、案例、视角或设备的完整验收。

## 2026-10-23 Sol：旧模板导航兼容与生态克隆隔离验收

- Luna 在 `3DWET/app/static/js/app.js` 增加旧首页模板的生态导航兼容逻辑：仅当模板缺少 `data-page="ecology"` 时，才在模型配置分组补入单个入口；正常模板不会重复。`app.js` 当前源文件 SHA256 `81509B3DA8F7EA85316E92FEF9DE914FFF95F4E6B0AFDEC728DEDC76A742038F`；8767 返回的 `/static/js/app.js?v=62` 字节数与本地一致（221302），浏览器刷新后实际看见入口并成功进入生态网络页。
- 独立测试：`node --check 3DWET/app/static/js/app.js` 通过；`node --test 3DWET/tests/test_app_ecology_nav_compat.js` 3/3 通过。
- 用户路径验收在隔离服务 8767 的临时 baseline 副本上进行，没有修改 8766 活动案例。生态网络页显示 20 个实际 FABM 实例、358 个显式端口，实例来源选择与“同功能群等总量分摊”选项均可操作。
- 尝试克隆时发现 8767 进程加载的旧后端不接受 `initial_fraction`，界面显示 `INVALID_DOCUMENT: unsupported clone fields initial_fraction`；请求在事务校验阶段被拒绝，副本未写入。随后将 8767 恢复到原候选案例并通过 `/api/ecology/network` 确认路径为 `erken-external-data-real-grid/candidate`（20 节点/358 边）。该环境不能作为当前克隆事务成功的证据，也不能据此宣称完整克隆路径已验收。
- 8766 的活动案例没有切换或编辑。首页仍返回旧模板的 `app.js?v=60`；旧模板兼容脚本在 8767 上已热加载并验收，但 8766 是否正在使用同一新脚本仍须以浏览器强制刷新后的实际 DOM 确认。服务端旧进程未重启，本次未声称新版后端已同步到桌面服务。

### 2026-10-23 Sol：8766 垂向层与 8767 外部数据 3D 连帧复核

- 8766 当前活动 `nfix_on` 未切换。蓝藻 `cyanobacteria_sDW` 在表层（`layer=-1`）0→1→2 播放，色标从 0.04973–0.04985 变化到 0.0487–0.0494 gDW/m³，189 水格有效、缺测/几何缺失为0，截图显示着色水体。随后 `layer=0` 0→1→2 播放，色标变为 0.0483–0.0493，水体仍着色；该次目标4 fps、实际0.8 fps、整帧P95 187 ms，包含首帧加载，不能当作稳定速度测值。
- 8767 隔离服务保留并加载外部数据 candidate（44×18、376水格、10层、3帧）。3D `temp` 从frame0播放到frame2，色标上限从2.180696增加到2.181906 °C；有效376、水域缺测0、几何缺失0。截图显示水体连续着色、湖岸框架仍在。目标4 fps、实测0.7 fps、整帧P95 148 ms；请求耗时包含初次帧/服务加载，该值仅为三帧短测，不能与稳态全帧播放指标混用。
- 本轮覆盖两个网格与不同输入（Erken nfix_on 和外部输入 candidate）、两个变量（藻类生物量与水温）、表层与第0层。指定条件下未复现第二帧起缺色；不推断全部变量、层、渲染方式或用户原场景均正常。3D字段更新、拓扑切换和失败回退已有自动测试，但没有找到可重现失败的 UI 输入，因此未改3D生产代码，也没有代码同步动作。
- 主服务8766仅浏览结果，无案例文件改动；8767仍为隔离 candidate。服务版本混合的限制见上一节：8767静态前端与当前源码相同，但后端旧进程不支持新克隆字段。本次仅验证已有外部候选结果的只读3D显示。

### 2026-10-23 Luna：Erken 克隆藻群输出订阅与全日播放复核（隔离副本）

- 在隔离 Erken 副本 `cyano_verified` 完成全日 43,200 步计算。克隆输出明确订阅 `sDW/sNW/sPW/sCW` 四项；诊断项不纳入订阅，存在前缀冲突的项排除。除 `fabm.yaml` 和 `output.yaml` 外，核心 forcing、grid、initial 配置哈希一致。`fabm.yaml` 的差异符合克隆设置：`nPHYT` 从4增至5，增加 CO2/POM 连接，注册克隆实例并将初始化分半。
- 输出含24帧。2D和3D播放实测均为4 fps，24帧无漏帧，水体彩色与色标正常；2D整帧P95为5 ms，3D为32 ms。这些结果只验收该隔离副本的同模型克隆分群、输出订阅和用户界面路径，不是不同物种竞争的学术验证。
- 对 baseline 比较时，cyanobacteria 与 clone 聚合后的四个水柱状态在输出第0帧已有约0.1004%差异，至末帧约2.2575%。差异原因尚未确定，不能据此宣称守恒或科学验收通过。此前 `cyanobacteria_ui_split_clone` 单独复核的约4.1%是另一案例/运行，不是本次测值。
- 输出 `aNLim` 约1.1867–1.1875，仍高于 `[0,1]`；本轮未确定越界根因。正式学术项目仍未验收，完成度维持0/5；上述工程/UI结果不改变未完成项和其他既有科学限制。
### 2026-10-22 Solver aNLim 问题修复与 8766 同步

- 根因：生产 `3DWET/bin/getm_cartesian.exe`（SHA-256 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`）和当前 WET 限值源码的运行行为不一致。来源候选 `3DWET/bw-nfix/getm/getm_cartesian.exe` SHA-256 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672`。候选 CMakeCache 记录 GETM 源目录 `3DWET/src/getm/src` 和 UCRT64 gfortran；未记录 WET 源文件内容哈希，故不能声称精确源码匹配或可重复构建证明。
- 同一隔离 `candidate_fixed` 的 YAML 与 forcing 使用旧/新 solver 对照：新 solver 完成 43,200 步，`aNLim=1` 并逐值匹配状态公式；1,027 个 3D 变量中仅 11 个 phyto `aPLim/aNLim/aNutLim` 诊断数组变化，其余状态和水动力逐值相同。证据限于该隔离案例、配置、forcing 和运行长度，不证明其他案例/时段，也不构成科学验证或完整质量守恒闭合。
- 替换前确认 8766 `run/status=idle`、root 为工作区 `3DWET`；8767 `run/status=idle`、root 为 `build/real-use-validation-20261022/erken-external-data-real-grid/ui-model-root`。旧生产文件可恢复备份位于 [`getm_cartesian.exe`](../../build/solver-backups/20261022-134037/getm_cartesian.exe)，替换清单为同目录 `replacement-manifest.json`。只替换生产 exe，没有更改案例、其他源文件或 8767/8768 服务。
- 8766 按应用同步流程重启后验证：首页 HTTP 200；`/api/system/health` ready 且 `model_root` 为本仓库 `3DWET`；`/api/run/status` idle；只读 GET `/api/run/check` 返回 HTTP 200、`ok=true`、blocking=0、warnings=0。服务 PID 59476、URL `http://127.0.0.1:8766/`；生产 exe SHA-256 为候选 SHA `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672`。8767/8768 未重启。

### 2026-10-23 Sol：克隆食谱匹配诊断与3D全区间播放复核

- 数值诊断基于隔离 Erken forcing proxy、synthetic 21×15 grid（189湿格、6层）、24帧，使用固定 solver SHA-256 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672`。比较文件为 `build/sol-aNLim-binary-probe-20261023/model-root-clean/case/{baseline,candidate_fixed,candidate_foodweb_matched}/output/ERKEN_NFIX_SENS24H.3d.nc`。
- `candidate_fixed` 未将克隆加入三类消费者食谱时，parent cyanobacteria 与 `cyano_verified` 聚合的四个水柱状态相对 baseline 全程相对RMSE约1.33%、末帧2.257%。在 `candidate_foodweb_matched` 中，cladocerans、copepods、zoobenthos 各加入 `prey_model6=cyano_verified`，相应参数照slot1配置后，四状态全程相对RMSE为0.00065–0.00070%、末帧0.00107–0.00115%；末帧aggregate mean ratio为1.000011，三个slot6摄食通量均非零。这支持差异与未匹配食谱有关，但仅是代理forcing下的工程诊断，不是不同物种竞争的学术验证或科学验收。
- 性能审计更正：此前报告的 `candidate_foodweb_matched` 对比 `candidate_fixed` 约6.1倍 `getm_fabm` timer 不可作为已验证的食谱槽位性能退化。历史两案例的 `run.stdout-stderr.log` SHA-256 相同（`0f80dbfcf4d88cce4397f10427d8be04d8a01f9ecf2fd5cabb671ce803dc8c08`），属于过期复制产物，不是逐次运行证据；保留旧目录但不将其用于该性能结论。
- 2026-10-23 以同一 solver 和逐字节相同的其他输入作四次隔离1小时重跑（每次600次FABM调用）：fixed 50.079 s、14.175 s；matched 44.207 s、12.318 s。各配置的两次墙钟时间分别相差3.533倍和3.589倍，远高于两配置配对时表面约12–13%的差异，且先后配对的表面方向相同（matched较快）但顺序不构成独立重复。故当前计时波动过大，不能推断食性匹配造成变慢或变快，也未验证 prey-slot 回归。相同配置重复运行的3D NetCDF SHA-256逐字节一致；配置间 YAML 确有差异：三种消费者的 `nPrey` 从5改为6，并增加 `prey_model6=cyano_verified` 与该槽参数。solver SHA-256 为 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672`。完整新报告与输入/输出哈希见[性能复核](../../../build/sol-foodweb-perf-audit-20261023/REPORT.md)和[机器可读清单](../../../build/sol-foodweb-perf-audit-20261023/manifest.json)。旧原始产物未改动。该测试仅为一小时合成 Imported Random Lake/Erken forcing 代理，不是 Erken 湖运行或科学验证。
- 8766 UI使用 `viz3d.js?v=80`，服务响应SHA与源码一致。Erken `nfix_on` / `cyanobacteria_sDW` 3D全区间24帧播放成功24/24；第二帧及后续帧水体着色与色标连续，189有效水格、0缺测，未复现“第二帧只剩陆地框架”。目标4 fps全区间面板实际0.5 fps、整帧P95 129 ms、绘图48 ms；短范围frame 0–3另测3.4 fps。不同测次差异明显，不足以宣称全区间流畅性已修复。播放计时在隔离模型结束后进行。
- 本轮无应用代码/运行配置改动，也无需重启桌面服务。上述结论仅覆盖列明的隔离输入、输出与一次 UI 播放；正式学术项目及正式五轮验收状态不因此改变。

### 2026-10-23 Luna：Lake Ravn 状态修复归因源码身份门槛

- 按隔离诊断要求，本次先检查了最短探针路径：Ravn 官方 `gotm_release.exe` 可复用做 repair-off 控制，但要获得状态名、检查调用位置和越界幅度的累计分布，必须改编 `fabm_check_state` 与对应 GOTM 检查调用并重建 solver。
- 本地可编译 GETM/GOTM 源码是 GOTM 5.4.0；官方 Ravn run log 记录 GOTM `v5.3-679-gc0add0a2-dirty (au branch)`、FABM `v0.95.3-298-gf73ec4c (au branch)`、WET `943d3c4 (master branch)`。可用 GOTM GitHub clone 不含日志中的 `c0add0a2` commit object；WET v1.0 archive 和当前应用源码均不能证明与该官方 binary 的 source/dependency/patch set 相同。匿名获取 WET 官方 AU 源的登录阻碍及版本差异已有隔离可行性记录。
- 因精确目标源码身份无法建立，本次按门槛停止：未写探针 instrument、未构建或运行新的 solver，模拟时长和步数均为0，没有新 NetCDF/model output；没有改 canonical Ravn case、production solver 或 app source。机器证据、哈希和下一步所需的不可变源包在[归因探针报告](../../../build/real-use-validation-20261023/ravn-repair-attribution-luna01/REPORT.md)及[清单](../../../build/real-use-validation-20261023/ravn-repair-attribution-luna01/manifest.json)。未改应用代码，桌面同步不适用。
- 旧 repair-off 对照只在首个越界时停止：`greens_sDW=0.9957e-4 gDW/m³`，下限 `cDMinW=1e-4 gDW/m³`，约低0.43%。它仍不能说明 250,670 次 repair-check 的变量、层、调用位置或事件幅度分布；不得把首个越界推断为主要来源，也不得据此建议关闭 repair 或降低下限。

### 2026-10-23 Luna：Ravn 保存输出的藻类生物量下限占据率

- 对 attempt01 官方默认运行的 `output.nc` 做只读扫描，先验证 SHA-256：NetCDF `8edd2faf797368757b7fd12ae27d02e40f703bdcdb892c00ddc756b2295a51bf`、`fabm.yaml` `74df92a7b8f9587d2b51865ddea07efc4cef67168d09cf99b48f5aab8e1bffc3`、solver `9840dc304b5f1d013cbd10861ce1da14d992c3555db1ec930f32d8f95121b6e4`；运行日志哈希和全部输入值见[机器清单](../../../build/real-use-validation-20261023/ravn-floor-occupancy-luna02/manifest.json)。Run log 记录 return code 0、5844日帧、interior repair-check 250,670次。
- `diatoms_sDW`、`cyanobacteria_sDW`、`greens_sDW` 均按各自 `fabm.yaml` 显式 `cDMinW=1e-4 gDW/m³` 检查。按 `numpy.isclose(value, floor, rtol=2e-6, atol=0)`，每个变量187,008个保存样本中分别有108,289（57.90608%）、13,164（7.03927%）、138,083（73.83802%）处于下限容差内；至少一个变量处于该下限的保存帧为4,991/5,844（85.40383%）。可用[分析脚本](../../../build/real-use-validation-20261023/ravn-floor-occupancy-luna02/analyze_floor_occupancy.py)复算。
- 这仅缩小了可能反复接触下限的已保存 `sDW` 状态候选。保存输出的触底样本不是运行中状态检查/裁剪事件计数，不能归因250,670次检查，也不能指出调用点、事件时刻/层或因果影响。`sPW/sNW/sCW` 阈值未报告，因为缺少与官方运行完全对应的注册源码，不能独立核验其实际状态下限。该只读扫描没有重跑模型，不构成生态、预算、校准或科学验证；前一节源码身份阻断与归因待办仍然有效。

### 2026-10-23 Sol：8766 3D播放相机保留修复复核

- 修复行为：Plotly `update` 帧补丁不再重复应用过期的 `scene.camera`；`Plotly.react` 回退重绘使用最近一次捕获的相机状态。相机回归测试13/13通过。8766页面重新加载脚本 `viz3d.js?v=81`，served SHA-256 与工作区源码一致。
- Sol 在 Lake Luoma 案例、21帧 `temp` 输出上做可见UI检查。目标4 fps时实际约0.5–0.9 fps；播放中切换到仰视预设后帧序列和颜色仍更新。该次 UI 手势证据限于预设切换，未实际验证滚轮缩放或鼠标拖拽旋转。
- CUA滚轮操作触发页面滚动，未形成可靠的画布滚轮事件，因此没有验证滚轮缩放或宣称该功能已通过。此结果限定于该案例、`temp`、21帧和当前工作站。
- 本轮未改应用/源代码或运行配置；8766已加载v81，无需重启。此前案例和播放测次记录保持独立，不作外推。

## 2026-10-22 Sol：Erken 外部来源运行与 algae cohort 机制演示归档

### 外部来源 Erken 技术运行

- 可复现实操入口：隔离案例 `build/real-use-validation-20261022/erken-external-data-real-grid/candidate/`；来源清单在 `candidate/Input/`，运行和完整输入/输出哈希、环境限制见 [`REPORT.md`](../../../build/real-use-validation-20261022/erken-external-data-real-grid/REPORT.md)，逐变量输出扫描见 [`candidate_outputs_summary.json`](../../../build/real-use-validation-20261022/erken-external-data-real-grid/candidate_outputs_summary.json)。本轮仅复核已有材料，未重新运行 solver 或改案例。
- 来源包括 SITES 官方 Erken outline 与 1 m bathymetry contours（CC BY 4.0，archive SHA-256 `40a4a95e5d9ec3ee0331896bc89de833b843cdfebcbe28072b2bdc19aac3c2e7`）、SITES Erken/Malma meteo（CSV SHA-256 `24b7d5f60cfb3904115bfeeb6a8b2c608b08bc791da63e29f3d552de62c29469`）及 SITES anchored temperature profile（CSV SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`）。
- 实际网格为 EPSG:3006、250 m、44×18；376/792湿格，wet area 23.50 km²，深度1–19.37338 m。GETM solver exit 0，dt=2 s，完成 2,160 步；输出 3 个逐小时帧，时间为 2020-01-01 01:00、02:00、03:00 UTC+1。自动扫描所检查 timed NetCDF 输出变量未发现未屏蔽非有限值。输出文件及 solver SHA-256 均在报告列明。
- UI 实操证据：隔离服务 8767 当时加载 `candidate`（generation 12）。可见 UI 将 2D `temp` 手动推进 frame 0/1/2 并播放 0–2，实际1.1 fps、成功3帧，自动色标上限逐帧增加；另有独立记录在3D `temp` 推进同三帧，水域376有效、缺测0、几何缺失0。当前只验证该案例/变量/短帧段；这不是对8766生产案例的写操作。当前复核确认8766在运行且当前案例为 Lake Luoma，8767在运行且指向该 Erken candidate；不要由过往UI记录推断服务后续未切换。
- 科学边界：单站气象均匀广播，云量固定50%、蒸发固定0；无实测流量；营养盐及生态状态为模型默认/代理；实测温度仅至15.5 m，以下端点保持至约19.37 m湖底。因此只验收来源输入、隔离求解和三帧结果浏览，不构成 Erken 校准、科学验证或场地生态结论。

### Erken 两 cohort 藻类机制实验及可视化

- 可复现实操入口：`build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/run_experiment.py`；运行清单 `experiment_manifest.json`，运行与解释见 [`REPORT.md`](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/REPORT.md)，逐帧数值见 [`audit_results.json`](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/audit_results.json)，可见页面步骤与性能记录见 [`GUI_REPORT.md`](../../../build/real-use-validation-20261022/erken-external-data-real-grid/cohort-split-mechanism-20261022/GUI_REPORT.md)。仅复核归档证据，未重跑实验。
- 此独立 run exit 0：24 h、17,280 个 5 s 步长，Erken 250 m、44×18、376湿格；有24个逐小时输出帧。cyanobacteria 的12项显式初始化状态按50:50分给原实例与 `cyanobacteria_lowlight_cohort`，各状态初始总量误差为0。唯一声明参数差异为 `qLightMethod=2` 下 `cLOptRef` 由23改成12 W/m²；burial 和 inorganic-carbon 多实例 consumer/multiplexer 端口扩至 `nPHYT=4`。这不是改动消费者菜谱的对照：无藻类克隆加入捕食者食谱的处理组，也没有食谱开/关对照。
- 数值：首帧（3600 s）cyanobacteria 与 lowlight cohort 空间/层均值分别为0.149598818、0.149691777 gDW/m³，差 +0.000092959；末帧（86400 s）分别为0.141070353、0.143105303 gDW/m³，差 +0.002034949，约为源群末帧均值的1.44%。报告称两组逐帧输出有限、非负。此值是同一双 cohort 模型内的轨迹差，不能作为竞争效应估计。
- UI 操作证据：2D 分别选择两个变量并各自播放24帧（实际约12.1/12.2 fps）；3D选表层并播放24帧（约11.7/11.6 fps），随后以lowlight变量在2 fps播放中拖动旋转镜头，帧继续前进至24/24。UI逐帧更新时间与色标，报告记录水格376有效、缺测0、几何缺失0。两个变量是顺序选择，未并排对照；GUI报告未测试zoom（也未测试pause/resume）。这些是特定隔离页面测次，不是通用帧率承诺。
- 归因与状态：此实验不是学术竞争验证、校准、论文复现或 Erken 现场生态验证；没有 A（原群）、B（等总量拆分且性状相同）、C（仅改指定机制）的三臂对照，缺乏独立的基线/机制归因。默认/代理营养生态状态、单站空间广播forcing、固定云量/蒸发和温度端点延伸均限制解释。**完整科学竞争分析状态：未完成。**工程运行、非负输出和2D/3D播放证据不改变正式科学验收未完成状态，也不能推出机制生态有效。
- 本次只更新用户指南与状态审计文档；未改代码、solver、案例或8766/8767服务，因此没有桌面应用同步动作。

### 2026-10-23 Sol：8766 Lake Luoma `temp` 2D/3D 可见播放与视角切换复核

- 8766 活动案例为 Lake Luoma，案例文件未改。3D `temp` 从 frame 0 播放至 frame 20（21帧）；播放中切换“仰视”后时间和色标仍逐帧更新，水域计数为1198有效值、0缺测、0几何缺失。
- 本次可见 UI 观察回合全段面板实测约0.7–0.9 fps、P95整帧约484–533 ms。期间包含多次界面读取/操作，故这些数据反映有交互的观察回合，不是无交互纯渲染基准，也不应与其他测次的稳态值直接比较。
- 切换至2D `temp` 后从 frame 0 连续推进到 frame 17；中途手动暂停，共18个成功帧，色标持续变化。面板显示约0.5 fps、P95整帧74 ms。该测量也受多次UI读取及手动暂停影响，不代表稳态连续播放性能。
- 复核后页面已恢复到3D、frame 20、斜视、暂停。操作期间未修改案例文件。此记录只确认所列案例、变量、帧范围和视角下帧更新可见，不构成通用性能验收。

### 8766 v89 Lake Luoma `temp` 三角网格播放复核

- 当前首页、`viz3d.js?v=89` 资源均为 HTTP 200；页面的脚本引用为 v89。复核结束后，8766 页面留在 3D `temp` frame 20、三角显示网格选中。
- 前台 3D 目标 0.5 fps，从 frame 0 连播到 frame 20，21/21 帧成功。播放时直接拖动画布，将湖面旋转到侧向、近乎沿边观察；帧继续推进至 frame 20。颜色范围从 frame 0 的常量 5.8899999 °C 变化为 frame 20 的 5.514081–5.868190 °C。水域为1198个有效值、0缺测、0几何缺失。面板记录实际0.5 fps、帧P50/P95为453/558 ms、绘制预算超限0/21、慢间隔3次。
- 该次实际 fps 和耗时包含 CUA/UI 观察开销；它证明本次操作中 21 帧颜色与帧序继续更新，不是无交互稳态基准，也不能外推为其他案例、指标、镜头、设备的性能结果。
- 同一案例 2D `temp` 目标4 fps，从 frame 0 到 frame 19，20/20帧成功；自动色标从常量5.8899999 °C 变为5.530694–5.869039 °C。面板显示实际0.6 fps、P95 31 ms，但墙钟观察约3秒内推进19帧；两种口径不一致，因此不报告稳定2D帧率基准。
- 8766 当前运行版本只确认本机 Lake Luoma 前台路径。该本地案例的结果不能代替外部输入或国际学术案例的验证，也不改变正式学术案例/完整工作流状态。

### 2026-10-23 Sol：8766 播放中相机保持回归与 UI 复核补充

- 定向回归 25/25 通过。测试覆盖播放帧更新时保留轨道相机状态、`Plotly.react` 回退采用最近捕获的轨道相机，以及正交 `scene.aspectratio` 上的统一缩放量跨帧保持；显式 reset 会清除缩放并回到当前帧适配尺寸。滚轮缩放保持和轨道旋转保留是代码级测试证据，不是本次 UI 手势实测。
- Sol 在 8766 的 Lake Luoma `temp` 播放期间切换到“仰视”预设，帧推进到 frame 3，色标和有效值继续更新；随后将页面恢复到 frame 20、斜视、暂停。该 UI 检查验证预设切换不会停止播放；本次未实际操作滚轮或拖拽，因此不据此宣称两种直接手势在 UI 中已验证。
- 本轮只更新用户指南和本状态文档，没有改代码、案例或运行配置；8766 无需重启。性能数据和限定条件沿用前述 Lake Luoma 观察记录，不将受界面操作影响的帧率解释为稳态基准。

### 2026-10-23 Luna：v86 真实 Plotly 播放中滚轮与跨极点拖拽复核

- 回归先红后绿：新增测试将 Plotly 真实滚轮事件形状建模为同一 relayout 同时带 `scene.camera` 和 `scene.aspectratio`，再模拟轨道事件重置 aspectratio；v85 实现无法记录该滚轮缩放而失败，v86 修复后两套定向相机/水体测试共32/32通过，`node --check` 通过。
- 根因是 Plotly 滚轮和轨道在某些交互时都同时发送相机与 aspectratio；旧判断把所有含相机的事件当成轨道事件，漏掉了滚轮比例。现有逻辑记录偏离拟合基准的缩放比例，并在轨道翻越极点、Plotly 回报基准比例时保留已有缩放；明确“复位”仍会清除用户缩放。每帧补丁继续重放事件中最新捕获的完整相机；跨极点相机不再按仰角截断。
- 在独立 headless Edge/CDP 页面通过实际 Plotly WebGL 画布操作 Lake Luoma `temp`，设定 frame 0–20、目标0.5 fps。播放中滚轮后比例为1.1；随后真实画布拖动跨越极点，`camera.up.z` 约为−0.9958；播放保持 active 并推进到 frame 1。观察到其后5次 `Plotly.update` 帧补丁继续保留基准×1.1的aspectratio和翻转后的 camera/up。该验证使用实际 Plotly 交互，不是自动化 mock；headless浏览器会话也不等同于前台桌面 UI 的人工验收或性能测量。
- 8766 已加载 v86，health ready，案例为 Lake Luoma、run idle；首页引用 `viz3d.js?v=86`，HTTP 200 的 served JS SHA-256 与源码一致：`944EDFA24D8085AC650729CA98F461FCDBCA434B2D98D99D71CCD178C81852A4`。页面及播放案例未修改。本记录只验证该服务、案例、变量和浏览器会话，不代表所有场景均已验收；播放速度仅为本次交互参数，不作为性能基准。

### 2026-10-22 8766 前台页面滚轮缩放复核

Sol 在 8766 活动页发现原标签仍显示 v82，刷新 tab6 后页面加载服务端 v86。Lake Luoma 3D `temp` 在目标1 fps播放时滚轮放大，帧序列继续推进至 frame20，放大视角保留；随后复位斜视并暂停。页面最终为 frame20/斜视/暂停，8766 run-status 为 idle。该项补充了前台页面播放中滚轮缩放保持证据。此前 v81 会话“未验收滚轮缩放”的说明仍是该次会话的真实记录；它不代表 v86 测次。前台鼠标拖拽未成功复核，跨极点拖动证据仅来自上面的独立 headless Edge 实际画布交互，不能当作前台人工验收。无需代码改动或服务重启。

### 2026-10-22 8766 仰视预设短范围播放复核

Lake Luoma 3D `temp` 固定范围0–2；播放中切换“仰视”预设后完成3/3帧，目标/实际均为1 fps，整帧P50/P95为296/341 ms，绘制超预算0/3。自动色标从frame0常量5.8899999变为frame2范围5.8473082–5.8874617；水体1198格有效、0缺测、0几何缺失，状态文字显示水体底视已隐藏湖底/陆地示意平面。该次前台复核支持播放中切换仰视预设及水体着色继续更新；坐标拖拽未形成可确认旋转，不代表前台鼠标拖拽翻越极点成功。跨极点证据仍仅来自独立 headless Edge 交互。操作后恢复frame20、斜视、暂停和范围0–20。

### 2026-10-23 Luna：Nielsen et al. (2014) PCLake 目标/附件与本地 solver 差异复核

**状态：Blocked；未运行模型。** 进一步核对论文 PDF 后明确：该研究目标是 Mooij et al. (2010) 描述的 PCLake 版本，由 Microsoft Excel 接口执行，作者扩展随机参数采样和批处理；论文没有给出不可变源码/Excel 工作簿/可执行文件版本或哈希，也没有提供可重建 Excel RAND 状态的 seed。论文说明 22 个参数由人工调整；350 个可调参数做 baseline、±25% 单参数敏感性筛查；输出敏感度最高的前 10% 参数在各自默认/调整值 ±20% 范围随机抽样，执行 900-run ensemble（作者试过 2000 次，称输出范围无显著扩展）。情景以每日温度 +0.5/+2/+6 °C 与 N、P 负荷各自 ±75% 组合。方法文字不能还原精确成员向量或可执行初态。

本地 `3DWET/src/fabm/testcases/fabm-au-pclake.yaml` 是通用测试配置；本地 `lake_arreskov_denmark` 是后来的 GOTM-WET 支持案例，不含 case-specific `fabm.yaml`。当前本地能找到的 WET/GETM solver 与论文的 Excel 版 0-D PCLake 不匹配；没有 2014 的 Excel 文件/solver 分支、ensemble/restart/initial states、完整观测与情景 forcing 包。因此 2014 论文既不要求 WET 的 `fabm.yaml`，也不能用通用 FABM YAML、当前 GETM-WET 或 2022 的 WET 配置替代。

附件/来源：论文 publisher-version PDF 取自 KNAW Pure，URL `https://pure.knaw.nl/ws/files/795592/5772_Nielsen.pdf`，SHA-256 `7371D2EE98246CB6FF3F2F890856F1EA62C315D568508562F82C7061C72883E5`。门户条款允许私人研究/学习的一份副本，禁止继续分发或商业用途；不得放入可分发案例包。仓库内已有 Elsevier mmc1 是 Andersen et al. (2022) 的 DOCX 补充材料，并非 2014 附件。未找到 2014 的 executable supplement、原始监测与 forcing 数据包、900 成员表、restart/初值、情景生成脚本或逐成员输出。完整材料来源/许可边界及恢复清单见[Arreskov 来源与复现性审计](../../../build/academic-case-validation-20261022/arreskov-source-audit/AUDIT.md)；WET v0.1.0 与 2022 支持输入的隔离恢复记录见[恢复审计](../../../build/academic-case-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md)。

最小可执行下一步：向作者或权利清晰的机构档案取得带版本/哈希的论文 Excel/PCLake build、22 个调整值、900 个留存成员向量及各自初态、日尺度气候/水文/N/P 情景输入与生成脚本（含 RNG 状态）、1992–2009 观测/插值与质量标志、输出处理脚本和逐文件复用条款；收齐哈希并确认 solver/build 与论文后再隔离运行。若无法取得，只能由科学负责人先批准一个独立 exploratory 重建并按新研究标注。

### 2026-10-23 Sol：Lake Luoma 三角显示网格前台播放和旋转记录

- 页面重载后在 Lake Luoma `temp`、3D 高视角、frame 0–20、目标 1 fps 下播放三角显示网格，完成 21/21 帧。图例为 1,198 个参与显示的湿四边形、2,396 个三角面、3,692 条去重显示边；这三角面是显示派生剖分，不是求解器原生三角拓扑。面板实际 0.6 fps，整帧 P50/P95 为 359/428 ms，末帧耗时 401 ms，慢间隔 16 次，超过 1 秒绘制预算 0/21。网络网格/线阶段 42/63 ms，Plotly 绘制 243 ms。
- 另一次前台播放中直接拖拽画布转到水下视角，帧序列仍推进至 frame 20；手势后面板实际 0.5 fps、慢间隔 7 次，无变量数据缺失或几何缺失，随后复位相机。观察到画面颜色与帧在镜头旋转时继续更新。
- 连续水体模式另作目标 1 fps 测次，观察 22 秒到 frame 18/21 后主动停止，面板实际 0.5 fps、整帧 P50/P95 230/470 ms、末次绘制 266 ms，无网格阶段。该次未完成，不是与三角模式的完整同条件对照，不能据此归因网格模式导致性能改善或下降。
- 所有计时包含前台 CUA 操作/观察开销，仅适用于本机、Lake Luoma、`temp`、frame 0–20 和所列设置；实际帧率未达到目标，不能承诺稳定目标性能。页面保持在 frame 20、三角模式、已复位的斜视相机，未更改案例或应用状态。

### 2026-10-23 Sol：8767 Erken candidate 食性网络观察

- 活动案例：`build/real-use-validation-20261022/erken-external-data-real-grid/candidate`。只读核对显示 API 与该案例 `fabm.yaml` 相符：17 条已解析食性引用、20 个实例、358 个显式耦合端口、0 个闭合三节点有向环。
- 可复核真实边：`cyanobacteria → cladocerans`（消费者端口 `cladocerans.prey_model1`）、`cladocerans → JuFish`（消费者端口 `JuFish.PLANprey2`）、`JuFish → PiscFish`（消费者端口 `PiscFish.PISCprey1`）。前两条组成 `cyanobacteria → cladocerans → JuFish` 三节点两边子链；配置继续至 `PiscFish`，完整图最长为4个关系布局层。因此这不是完整三层图，也不是三节点闭环。
- 8767 前台显示4个关系层、10个端点实例、17条边、3个鱼类实例、闭环0。已加载 foodweb filter；DOM 中摘要与全部边可读。滚动截图中图层节点可见，整张大画布需要滚动查看。
- 版本与服务边界：该页面使用旧前端 `/static/js/ecology_network.js?v=3`。同一时段 8766 首页使用 `ecology_network.js?v=21`，活动案例为 Lake Luoma（两层、无鱼类食性边）。不得把 8767 的 Erken 图形观察记为 8766 v21 的 UI 证据。
- 结论只涉及这份 candidate 的可解析配置关系、布局和本次前台可见性；不证明已成立的科学营养级、实际摄食、闭合环或求解器通量。本次无案例 YAML 或生态关系变更。

### 2026-10-23 三节点食性路径摘要实现

- `3DWET/app/static/js/ecology_network.js` 新增 `directedFoodwebPaths`：仅从 `foodwebEdges()` 返回的已解析、启用节点饮食边动态枚举长度为2的连续有向路径，并排除任意重复实例（含自环）；摘要为每条路径输出节点顺序及两段的 `reference` 与消费者端口。结果称“三节点食性路径/配置链”，明确不等于三角闭环、营养级或已验证摄食；无结果显示0条/无可验证配置链。
- 回归新增：真实有向三角的三条两边路径、自环和重复节点排除、孤立边无链；candidate 拓扑fixture应显示 `cyanobacteria → cladocerans → JuFish` 及 `cyanobacteria/sDW · prey_model1`、`cladocerans/sDW · PLANprey2`。8767 candidate此前只读配置记录为17条饮食引用、358条总耦合端口，并有上述路径；这项自动 fixture 验证不替代服务当前配置核验。Lake Luoma当前边若无连续三节点链应显示0条，不切换案例。
- 修改文件：`3DWET/app/static/js/ecology_network.js`、`3DWET/tests/test_ecology_foodweb_ui.js`、`3DWET/app/templates/index.html`（资源键v21→v22）、`3DWET/docs/USER_GUIDE.md`及本状态记录。未写案例、solver、数值配置。SHA-256：`ecology_network.js` `123AE3BA502849C6EF2E2F3AA76D5135FBBE2DFAC51E620CD9927B2F712389A2`；`test_ecology_foodweb_ui.js` `2C0132CA03862AB77B1EA3BC430339469D0F3C9F8902D1E5E8B0FDA59D20E398`；`index.html` `33CFBAB3F50DC2AAEACBD0B4B5067FAA2CBA9DF54B43B54C663D45031547CC90`；`USER_GUIDE.md` `05513003DC90F830241396980B9508EEB2F00CFCFC3175A9B33745CA10432C3F`。
- 自动测试 `node 3DWET/tests/test_ecology_foodweb_ui.js` 最终通过。过程中将过时测试断言校正为行为检查：窄视口图宽应大于可视区且可横向滚动（当前实测828px）；关系表检查六列（含闭环状态）；布局应标“配置层/未判定营养级”；宽视图允许由节点尺寸决定大于视口的画布，并以画布高度中心验证缩放；闭环中重复节点路径按要求排除。完整 DOM 回归通过，包括候选链fixture。
- 8766/8767仍运行；此时仅核对了只读网络API：8766为Lake Luoma（15节点、296边），8767为 Erken candidate（20节点、358边）。源文件服务响应、DOM摘要及服务端/浏览器版本同步需在刷新8766后复核；不能以8767旧页面作8766同步证据。完整哈希及该同步检查结果待补录。
- Sol 的最终复核：8766 run-status 为 `idle`，health `ready=true`、PID 22348、model root 指向本仓库；重载实际 IAB 页面后重新加载 Lake Luoma 并进入生态网络。页面源码 HTML 仍引用旧 cache key `ecology_network.js?v=21`（磁盘模板已更新为 v22），但 `GET /static/js/ecology_network.js?v=21` 返回 53,166 字节，其响应 SHA-256 与当前源码 `123AE3BA502849C6EF2E2F3AA76D5135FBBE2DFAC51E620CD9927B2F712389A2` 一致；浏览器中的实时 DOM 已据当前 Lake Luoma 配置显示“已解析的三节点食性路径 0 条”、12条食性引用、0个闭环，并实际绘制配置分层图。故可确认此浏览器会话执行的是当前脚本内容；HTML 版本键尚未更新。受环境进程控制策略阻挡，Sol 未停止/重启 PID 22348，不能声称已完成服务重启或 v22 HTML 模板同步。当前 UI 留在 Lake Luoma 的真实食性配置图，未修改案例/solver/数值配置。

### 2026-10-23 Luna：3D 主图与可追溯三层食性子网

- 食性视图新增“真实三层子网”开关。它先用当前已解析且启用的饮食边计算完整关系布局，再筛出层1–3端点；边仍须是原 YAML 配置的边且两端均留在筛选集。完整网络统计继续显示，不被子网过滤覆盖。Erken candidate 目标显示为完整图10端点/17边/4层，三层子网9端点/15边/3层；`JuFish → PiscFish` 和 `AdFish → PiscFish` 两条真实第4层边只在完整视图出现。橙色线与卡片突出一条三节点/两边真实路径；逐边显示 YAML 引用与消费者端口。闭环数量按完整已解析网络单独统计；路径、配置布局层和闭环的文案明确不判定科学营养级或实际摄食。空链状态单独显示0，不生成示例边。
- 3D 桌面端高级设置改为默认折叠，图例仍在侧栏可见；点“设置”可展开。播放相机的连续帧保持由既有 Plotly 相机缓存/队列实现，本次未改其相机代码。前端样式为路径卡片和紧凑侧栏增加明确层级、滚动空间和键盘可读文本。
- TDD：新增过滤视图、9节点/15边、完整网络4层/17边、突出 Erken 链两边和 Luoma 空链的断言；实现前测试因缺少路径列表及子网状态失败，随后 `node 3DWET/tests/test_ecology_foodweb_ui.js` 与 `node 3DWET/tests/test_scientific_workspace.js` 均通过。后者含播放顺序、暂停/续播和状态隔离验证；相机旋转/缩放在播放时的既有代码/UI证据见上方 2026-10-23 相机记录，本次没有声称重新实测手势。
- 本轮代码文件：`3DWET/app/static/js/ecology_network.js`、`3DWET/app/static/js/scientific_workspace.js`、`3DWET/app/static/css/scientific_workspace.css`；回归文件：`3DWET/tests/test_ecology_foodweb_ui.js`、`3DWET/tests/test_scientific_workspace.js`；文档：本节与 `3DWET/docs/USER_GUIDE.md`。实际配置复核：Python `yaml.safe_load` 只读读取 Erken candidate，得到20个启用实例、17条解析饮食边、15条三节点/两边路径、闭环0；目标路径 YAML 边为 `cyanobacteria --prey_model1→ cladocerans --PLANprey2→ JuFish`。8766 `/api/ecology/network` 仍为 Lake Luoma：15实例、12条实际食性边、三节点路径0；未切换案例。定向 Node 验证 `test_ecology_foodweb_ui.js`、`test_scientific_workspace.js`、`test_viz_waterbody_patch.js`（15项）、`test_viz_camera_axes.js`（17项）、`test_view_controls.js`、`test_viz3d_responsive_layout.js` 全通过；水体测试包含播放帧保持实拍相机、显式复位、滚轮缩放保持，camera-axis tests 包含拖动中载入下一帧时保留最新镜头。
- 同步边界：8766 PID 22348 的三个静态资源 HTTP 响应 SHA 均与工作区源码匹配（最后 `ecology_network.js`：`288F922EDF67DA6D5B2BB7D78335981693AFDE190E1E2EB1C7A114278070BE26`；`scientific_workspace.js`：`AA3D0D03C7D02F58DC03353FC3191E4B09AE8EF6B419A17E7798BA1E04726B75`；`scientific_workspace.css`：`3C06B4F1FDD8C70E7076A4772ED2D7B663F6D90D700659E3EB30E5C13562FC7D`）。但首页 Jinja 模板仍由进程缓存为 v21；磁盘模板已更新至 `ecology_network.js?v=23`、`scientific_workspace.js?v=15`、`scientific_workspace.css?v=8`，3D 设置初始 `aria-expanded=false`。本子代理调用 CUA 打开可见 IAB 收到 `IAB visibility is not supported in a subagent thread`，因此没有声称已完成人工前台点击或页面模板同步；8766 run-status 接口可读、案例为 Luoma。Sol 接管浏览器硬刷新/独立验收后，才可记录最终页面是否加载 v23 与新子网控件。没有修改案例、fabm.yaml、solver 或结果数据。

### 2026-10-23 Luna：Lake Luoma 3D 播放响应载荷收窄

- Sol 的两次带 UI 观察测次均播放 Lake Luoma `temp` frame 0–20、8 fps 目标、1198 湿格：分别 6.6/6.8 fps，整帧 P50/P95 为 125/172 与 120/153 ms。该面板观测受 CUA 操作影响，仅是探索性数据，未作为稳定帧率基准。其分阶段计时显示请求/JSON 解码约127–148/130–141 ms、绘制76–88 ms，而同步拼装约22–23 ms。
- 单层水体渲染源码只消费逐帧变量值、`water_depth`、`elevation`、`valid_geometry` 与同步警告；动态 `depth`、水面/底压水位、差值矩阵及逐格 `surface_synchronized` 不参与绘制。`waterbody_compact=1` 仅用于这个单层视图：服务端按原有效几何格汇总同步差异布尔值，然后省略未消费矩阵；其他结果 API 使用者保持原字段响应。静态几何缓存仍按原键合并，动态水深/高程、变量值与逐帧值域、湿网格和拓扑未缓存或推测。
- TDD 先红：新增 Python helper/payload 测试初始因 helper 未定义而 2 项失败，Node 播放测试初始缺少紧凑参数而失败。实现后 `node --test 3DWET/tests/test_viz3d_playback_prefetch.js` 12/12 通过，`.venv/Scripts/python.exe -m pytest -q 3DWET/tests/test_3d_surface_compact.py` 2/2 通过。回归覆盖连续播放请求带 compact 参数、有效几何格同步差异摘要、无效格不触发警告；现有播放顺序、单层/堆叠查询、预取界限和静态拓扑复用仍通过。
- 8766 同步：重启前服务端子进程 PID 22348、启动器 PID 6640；按本地 `--web --no-open --port 8766` 配置重启后，服务端 PID 41252、启动器 PID 92060，`/api/system/health` 返回 ready，实例 `ae59e6f0b5c34e9a9c1ae6caccabb67f`。重新加载原有 Lake Luoma 案例（21帧；未写案例数据）。首页已引用 `viz3d.js?v=90`；静态响应 SHA-256 `BB8922E1B1805FB7FB14D429C83677549EAD5E4FCA82637F4C6B970F297FF050` 与工作区文件一致。
- 8766 Luoma `temp`, target=96、frame1、`static_key` 相同时，旧完整响应 243,345 bytes，紧凑响应 100,122 bytes（减少143,223 bytes，58.8%）。紧凑响应仍保留 `data`、`water_depth`、`elevation`、`valid_geometry`、动态几何标志、原始 min/max 与同一静态几何键；移除项仅为 `depth`、`surface_synchronized`、`surface_elevation`、`barotropic_surface_elevation`、`surface_difference`。5 次本机 API 请求为34–39ms/帧；此端点载荷冒烟值不是浏览器播放帧率。
- Sol 随后在重启后的同一8766 instance `ae59e6f0b5c34e9a9c1ae6caccabb67f` 测试 frame20 同键响应：完整243,000 bytes、紧凑100,066 bytes（−58.8%）；`data/min/max/water_depth/elevation/valid_geometry/timestep/static_geometry_key` 一致，摘要保留。前台完整播放21/21帧，目标8 fps、实际5.9 fps、整帧P50/P95 141/185ms；相机底视操作正常。此次受前台观察开销影响，且帧率仍低于目标；载荷缩减不是达到目标帧率的证据。
- 同一Luoma页面食性网络如实显示12条已解析饮食边、0条三节点两边路径、0个闭环，且无已配置鱼类实例；没有借用 Erken 展示路径。只读解析 Erken candidate 的 `fabm.yaml` 得17条实际饮食边、15条真实三节点/两边路径、闭环0。示例路径是 `cyanobacteria --[cladocerans.prey_model1]→ cladocerans --[JuFish.PLANprey2]→ JuFish`；其后有真实边 `JuFish --[PiscFish.PISCprey1]→ PiscFish`。Erken完整网有10个饮食端点、17边、4个配置关系层；层1–3筛选为9节点/15边/3层，隐藏的两条第4层边为 `JuFish → PiscFish` 与 `AdFish → PiscFish`。这些是YAML引用及绘图布局证据，不证明实际摄食或科学营养级。
- 针对 Sol 观察到的 frame20 深色碎纹复核：当前前台 `#viz3d-mesh-mode=continuous`，按 `buildDisplayNetwork()` 实现该模式不生成 line/network overlay；三角网 overlay 若启用则使用浅青 `#74cbd8`、1.35 px（不是黑线）。8766 实际输出中 frame0 湿格1198/1198有限且温度恒为5.8899999；frame20湿格1198/1198有限，`temp`范围5.514081–5.868190，<5.7的30格分成2组、最大组24格，<5.8的73格最大相邻组71格。每帧自动色标因此会映出真实值场的空间差异；missing coverage=0，不支持把深色区域解释为缺测。颜色表低端为深蓝而非纯黑。没有充分的截图级证据区分深蓝真实色场与浏览器/栅格视觉伪影，因此保留为视觉复核限制，不改数据/颜色，不通过隐藏网格规避。
- 新增 `compact frame20-style payload preserves continuous waterbody colors and has no mesh-line overlay` 聚焦回归：对照完整字段和 compact 摘要生成的 field trace `x/y/z/i/j/k/intensity/customdata/cmin/cmax/colorscale` 逐项相同，标题同步警告相同，continuous 模式不产生 network overlay。`node --test 3DWET/tests/test_ecology_foodweb_ui.js 3DWET/tests/test_viz3d_playback_prefetch.js` 合计14/14（播放器测试本身14/14，含 frame20 compact/full mesh 等价回归）；Python compact payload 2/2 仍通过。仅新增测试，无生产渲染代码改变，故 8766 无需再次重启。

### 2026-10-23 Luna：固定只读 Erken 食性配置示例与真实空链

- 增加网络来源选择：默认仍是 Lake Luoma 活动案例；只读来源固定枚举为 `erken_reference`，服务端只解析仓库 `3DWET/case/Erken_real_20200101_24h_stage/fabm.yaml`，拒绝任意路径、未知来源、写入请求、缺失配置和未完成事务。读取跳过事务恢复；不改活动案例或示例配置。只读来源会隐藏实例、参数及食性编辑控件。
- Luoma 活动案例数据显示12条已解析饮食关系、三节点/两边路径0条、闭环0、没有已配置鱼类食性边；三层过滤禁用，关系表仍保留12条精确关系。没有借用 Erken 数据填充 Luoma。
- Erken 固定配置只读示例根据启用且解析的真实饮食端口呈现17条完整饮食边，目标路径 `cyanobacteria --[prey_model1]→ cladocerans --[PLANprey2]→ JuFish` 明确为3节点、2条边；完整配置另有 `JuFish → PiscFish`，所以网络可有4个配置层。此例仅证明配置引用和绘图布局，不证明实际摄食、科学营养级、现场或模型验证；闭环仍单独计数为0。
- TDD 红灯：添加 UI 与 API 用例后，原前端在 Luoma 两层网络上仍允许打开三层过滤；固定来源请求也退回活动案例数据。完成实现后，`node --test 3DWET/tests/test_ecology_foodweb_ui.js` 通过，DOM 断言覆盖 Luoma 空链/12条关系、三层筛选禁用、来源选择不改变活动案例、只读编辑区隐藏、Erken真实目标链及17条关系；`.venv/Scripts/pytest.exe -q tests/test_ecology_network.py -k reference_network` 2/2 通过，覆盖固定来源路径、精确两条端口引用、无事务恢复/写入、活动案例身份保持、缺失配置失败关闭及POST只读拒绝。
- 3D未改动：现有窄视口布局/滚动、主图、相机手势及播放中镜头连续性已有相关回归；本轮没有新的复现缺陷证据。
- 本轮修改仅限 `3DWET/app/lake_points_api.py`、`3DWET/app/static/js/ecology_network.js`、`3DWET/app/templates/index.html`（`ecology_network.js?v=23→24`）、`tests/test_ecology_network.py`、`3DWET/tests/test_ecology_foodweb_ui.js`、本指南和本状态记录。Node DOM 与窄屏 3D 视口联合验证3/3通过；Python `tests/test_ecology_network.py` 全文件19/19通过；`node --check`通过。\n- 8766 同步尝试：重启前 PID 41252 / launcher PID 92060，health ready、instance `ae59e6f0b5c34e9a9c1ae6caccabb67f`、活动案例 `Lake Luoma`。执行按授权的 PowerShell `Stop-Process` / `Start-Process` 重启时，命令创建被环境策略拒绝（`CreateProcess ... Rejected ... blocked by policy`）；没有绕过。原服务仍运行 PID 41252，健康状态不代表新后端已载入。磁盘 HTML 模板现引用 `ecology_network.js?v=24`，但服务首页 HTTP 200、142,497字节、SHA-256 `F92E6304EEB7864C328FC76B56CD2B2FFD85BFE5CC6A7AA8358FD0B063D05729`，仍由旧进程模板缓存为 v23。直接请求 `/static/js/ecology_network.js?v=24` HTTP 200、59,430字节，响应 SHA `75B8D419E21910244080D44A232EF6454315578A8D2D1A916B295F287400E111` 与源一致。旧进程对 `/api/ecology/network?source=erken_reference` 回 200 但仍返回 Luoma /296条全部耦合，证明新增只读 API 尚未加载；不能声称服务端到端同步或真实前台路径交互完成。子代理中的 CUA 页面控制不可用。本机用例覆盖来源切换、端口文本、活动案例不切换及空链交互；8766真实 API/前台需在进程控制可用后复核。

### 2026-10-23 Sol：不透明侧壁及浏览器最终播放复验

- 动态 `湿网格边界剖面` 侧壁从 opacity 0.12 调为 1；补充回归先因 0.12 失败，改后通过。该改动让大面积侧壁在浏览器里呈蓝灰色，但 166.5× 自动夸大下仍有黑色区域，故仅为局部改善，黑影未验收关闭。
- 实际浏览器隔离图层：关闭 Plotly 图例中的 `湖盆水深` 后，黑色区域消失，水体场与不透明蓝灰侧壁仍在；恢复湖底层后黑色重现。此观测把剩余问题指向湖底深度面在极端垂向放大下的绘制/深度交互；尚未确认更精确机制，继续调查。20×视角下黑色底面不明显。岸陆示意层在隔离后恢复为显示。
- 最新桌面实例 PID 70940 / `37ec3b2bc3174d2ab8d70f4944189072`，health ready，窗口标题 `3DWET Studio`。当前页面引用 `viz3d.js?v=92`；该 URL HTTP 200 字节 SHA `FEB259CB8A7A0DAAEFF0634C58A38EE688D63D2C463C88E8F67CC2E7BC4904A6` 与本地源码一致。
- 最终版本浏览器实播 3D frame 0→19：目标/实际 4 fps，成功帧 20/20，整帧 P50/P95 35/50 ms，超预算 0/20，帧间隔超目标10%为0；模型上下位置 +15% 在末帧保持。当前留在 frame 19、自动垂向放大、+15%、岸陆显示开启。
- 相关 Node 检查见 `test_viz_waterbody_patch.js`、`test_viz_render.js` 与 `viz3d_bathymetry_surface.test.cjs`；本节只报告运行命令的实际结果，不将光照测试单独作为黑影已修复证据。

- 2026-10-23 latest browser recheck: 3D playback 20/20 frames at actual 4.0 fps; +15% model position persisted across frames; desktop v92 source SHA matched. Black underside remains unresolved after neutral bed lighting, browser playback screenshot: erkens-3d-playback-20261023.png.

- 2026-10-23 2D browser playback on current Erken import: frame 0→19, 20/20 at actual 4.0 fps, P50/P95 3/4 ms, no over-budget draws or >10% interval misses. Screenshot erken-2d-playback-20261023.png. The black bed remains unresolved; screenshot erken-black-bed-remains-20261023.png.

### 2026-10-23 Sol：Erken A/B/C 168 h 对照运行完成状态核验

- 核对 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/ATTEMPT03.md`、C 重跑 `status.json` 和 `validation.json`。A/B/C 三组均已完成 168 h 候选求解器运行；C 独立重跑 return code 0、`getm: Completed`、无 fatal/EOF，输出验证 valid，2D/3D/NetCDF 均有 168 个预期小时帧（3600–604800 s），必需变量齐全且所检有效值有限。
- 这关闭的是候选组的求解完成与输出完整性检查。候选二进制 SHA-256 `6ac027fe4bdb851b1c7d8c08c23b3a86bcb07705c7f7510a90f64b0aa18f4344` 与生产 solver 不同；结果仍是机制敏感性实验，不是现场/科学验证。强迫包括 `swr` 实测短波和末端 held-value 计算填充；长波云量、蒸发、河流和多种生态状态仍使用已披露的代理/默认设置。
- 本次未在浏览器载入这套 168 h A/B/C 输出；长时结果的 UI 播放与科学验证仍未完成。不能把隔离 Erken 2020 浏览器工作流的 24 h 记录当成此结果集的 UI 验收。

### 2026-10-23 Sol：8766 Erken 播放、相机与黑色湖底复测

- 在 8766 已运行的 Erken 导入工作流案例中，于当前桌面应用最终源码版本实测：2D 0→19，20/20 帧；目标 4 fps、页面面板实际 4.0 fps、整帧 P50/P95 3/4 ms、0 次绘制超预算、无间隔超过目标 10%。3D 同样 0→19，20/20 帧；目标 4 fps、实际 4.2 fps、整帧 P50/P95 46/80 ms、1/20 次绘制超预算、无间隔超过目标 10%。以上是本次浏览器观察值，不外推为通用基准。
- 3D 中将“模型上下位置”设为 +15%，跨帧至 19 后仍为 +15%，视图平移保持。水深图例关掉时黑色区域消失、恢复后重现；关闭示意陆地没有消除黑色区域。受控 `flatshading=true` 浏览器试验仍出现黑面，随后已回滚；生产源码保持 `flatshading=false`。此前试验中的 `cmin/cmax` 推断系因动态 overlay 实际将 `style=null`，最终范围走默认值，已撤销，不作为修复。黑色湖底原因仍未定位，未宣称修复。
- 最新桌面服务 health ready，PID 74028，model root `3DWET`；页面资源 `viz3d.js?v=92` HTTP 200，served 与本地源码 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。此次源码版本已回滚实验性平面着色更改。
- 本记录仅更新审计文档；没有源码变化，无需重启服务。截图包括 `erken-2d-playback-20261023.png`、`erken-3d-final-playback-20261023.png`、`erken-black-bed-flatshading-20261023.png`。

### 2026-10-24 Sol：Erken June 2024 A 组 168 帧浏览器三维全程验收

- 8766 工作台通过 `/api/case/open` 载入 `arms_168h_direct_swr_padding_verified/arm_A/case`；页面 3D 视图列出 862 个变量、168 输出时步、`viz3d-time-slider` 范围 0–167，选择实际输出变量 `temp`（水温）。未重新运行模型；本次读取既有 A 组候选输出。
- 设播放范围 0–167、目标 4 fps，模型上下位置 +15%。浏览器实测 10 秒推进至第 40 帧，继续播放后到达第 167 帧，UI 时间戳为 `2024-DOY172 13:00:00`。终态面板显示目标/实际 4.0/4.0 fps、最近 60 帧统计中 0 次绘制超预算、间隔超目标 10% 为 0；+15% 控件仍在。帧序滑块和最终时间戳确认全范围到达。黑色湖底仍可见；本次不验收其修复。
- 计划复核同一 168 帧案例 2D 全程，但 CUA 对播放控件的点击动作连续超时；滑块在设为0后仍为0，没有开始播放。因此 168 帧 2D 播放仍未验收。较短 Erken 工作流已有 20 帧 2D 连续播放实测（见上文），不能替代本长时数据集验收。
- 复测后将活动案例恢复为 `build/real-use-validation-20261023/user-journey-Erken-import`，浏览器刷新后确认顶部案例名恢复。桌面 health 为 ready、PID 74028、model root `3DWET`；`viz3d.js?v=92` HTTP 200 且服务返回 UTF-8 内容与本地源 SHA-256 一致：`4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本轮只有文档更改，无源码变更。

### 2026-10-24 Sol：Erken June 2024 A 组 168 帧浏览器二维全程验收

- 在同一 8766 工作台和 A 组候选输出中，2D 页面选择 `temp`（水温），播放范围 0–167，目标 4 fps。浏览器实际播放中间检查点为 frame 61（2024-DOY168 03:00），继续播放后到 frame 167（2024-DOY172 13:00），播放控件自动回到暂停状态。终态面板为目标/实际 4/4 fps、成功帧统计最近 60、整帧 P50/P95 4/5 ms、0/60 绘制超预算、0 次超目标 10% 的帧间隔。由起始帧设置、实际中间进度和末帧/时间戳确认全范围播放。
- 此项与前一条 A 组 168 帧 3D 验收使用同一候选输出集。两者均证明当前播放器对该长时网格数据可实际推进完整输出范围；候选 solver/代理强迫/非科学验证等限制仍适用。
- 本测次在关闭临时浏览器页前将活动案例恢复到 `user-journey-Erken-import`。桌面源码和服务未改。

### 2026-10-24 Sol：Erken 导入工作流 3D 视角跨帧与播放抽查

- 当前浏览器 `user-journey-Erken-import` 3D 页：将“模型上下位置”从 0% 调至 +15%，下一帧从 0 到 1 后仍为 +15%；随后 1 fps 播放 4.2 秒到 frame 5，页面显示目标/实际 1/1.0 fps，成功帧 5，0/5 绘制超预算，帧间隔超目标 10% 为 0。实际观察确认控件在播放跨帧期间保持生效。该次是活动播放抽查，长时全范围 2D/3D 验收见前述条目。
- 切至“连续水体”后，当前 2020 导入案例的内部暗点比派生三角网画面少；此视图未复现 2024 候选案例同等程度的黑色湖底。不能据此声称黑影已修复，2024 候选结果中的黑色湖底仍待定位。
- 端口 8766 当前由 PID 74028 的 `python.exe` / `3DWET/app/launcher.py --desktop` 服务。当前页加载 `viz3d.js?v=92`；本地和 HTTP 响应 UTF-8 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。此版本没有 `/api/health` 路由（请求返回 404），因此以监听进程和服务资源哈希验证桌面同步。无代码改动，仅更新审计记录。

### 2026-10-24 Sol 补记：同一 3D 播放自然完成全范围

上条记录的 4.2 秒检查点之后，播放器在本轮浏览器检查期间继续运行并自然到达第 19 帧、自动暂停。页面终态：frame 19/19，成功帧 20，目标/实际 1/1.0 fps，整帧 P50/P95 38/46 ms，0/20 绘制超预算，帧间隔超目标 10% 为 0。“模型上下位置”在终帧仍为 +15%。因此这次实际完成了该 20 帧 3D 输出范围的完整播放；之前对 168 帧 A 组的 4 fps 全范围实测仍是更长案例的验收证据。

### 2026-10-24 Sol：浏览器实时迹线隔离黑色湖底

- 在 `user-journey-Erken-import` 的实际 3D 页面（frame 19、自动垂向放大 166.5×、镜头仰角 34°、位置 +15%）通过图例单击隐藏“湖盆水深”迹线。黑色下侧多边形消失，同时水温场、岸壁蓝灰面、岸线、等深线和岸陆示意仍可见；恢复该迹线后，黑色下侧面立即重新出现。由页面实测可将异常定位到“湖盆水深”底面迹线的渲染路径，而不是岸壁单独着色。
- 源码中该迹线使用 `geometry.floor` 深度角点、深度色带，`ambient=1 / diffuse=0 / specular=0` 且 `flatshading=false`；但浏览器画面仍出现近黑色下侧面。此前的三角形法线/退化检查未发现几何错误。根因仍未确认，因此没有再做推测性代码修改。
- 对照期间将相机角度暂设为 89°、垂向放大暂设为 20×；之后已恢复镜头仰角 34°、自动垂向放大、连续水体、床面图例打开，模型上下位置 +15%。当前浏览器回到原 20 帧 Erken 导入结果的第 19 帧。桌面源码未改，服务无需重启。

### 2026-10-24 Sol：正常俯视与底视的黑面控制变量复核

- 对当前 20 帧 Erken 导入结果，保持 frame 19、连续水体、自动放大 166.5×、位置 +15%，正常俯视 +34°下，图例关闭“湖盆水深”时近黑色下侧面消失，恢复后复现。
- 将仰角设为 −34°时，页面明确显示“水体底视：已隐藏湖底与陆地示意平面”。该底视隐藏是现有设计行为，不能视作解决了正常视角下的黑面。此项把可见异常定位在底面迹线绘制，但尚不能区分 Plotly/WebGL 着色、深度缓冲或底面自身数据/投影交互；未改代码。
- 已把镜头恢复 +34°、自动放大 166.5×，浏览器当前仍是 frame 19，模型位置 +15%，播放器暂停。页面版本 v92 的服务端与本地哈希上一轮已核验相同；本轮无源码变更，无需同步重启。

### 2026-10-24 Sol：桌面启动器最终源码下的 2D/3D 浏览器播放复验

- 在 8766 端口空闲后，由 `3DWET/app/launcher.py --desktop --port 8766` 启动桌面模式。`/api/system/health` ready，health PID 与监听端口进程均为 87684；Win32 命令行为上述 `--desktop` 启动命令。首页引用 `viz3d.js?v=92`，本地源与 HTTP 响应 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。浏览器重载后重新打开当前 `user-journey-Erken-import` 案例并进入结果页。
- 3D 实际操作：把“模型上下位置”设为 +15%，手动前进一帧（0→1）仍为 +15%；从 frame 1 播放，观察至 frame 6 和 frame 17 时帧号持续增长且位置仍 +15%；播放器自然到达 frame 19/19 并暂停。结束面板显示目标/实际 1/1.0 fps、成功帧19、绘制超预算0/19、帧间隔超目标10%为0。最终角度 +34°、位置 +15%。
- 2D 最终源码浏览器抽查：从 frame 0 开始以目标 1 fps 播放 5.5 秒，实际到 frame 5；目标/实际 1/1.0 fps、成功帧6、绘制超预算0/6、帧间隔超目标10%为0。此处是动态播放检查点，不是再次完整播放0–19；完整 2D 范围已有既往记录。
- 最终画面仍可见湖底底面黑色面片。本轮未改源码；根据已重复的迹线开关对照，隐藏“湖盆水深”会去掉该黑面，恢复则复现。异常仍定位在该底面迹线的渲染路径，根因未确认，未修复。三角网需求仍按现有 UI 明示的派生显示网格理解：视图层的连续/正交/派生三角/隐藏模式不改求解器拓扑；用户对原始需求无法确认且未提供参考图，故不扩大到求解网格编辑。
- 食性网络本轮未更换案例或重做配置检查；既有记录中的每条边均来自实际启用模型 YAML 的明确饮食引用，并且明确区分配置关系与实际摄食。参考图未提供（用户回复“没有”）。本轮只有本审计文档追加，无应用源码改动，无需重启；桌面服务仍在运行。
- 实际检查三角网可调项：在同一浏览器把模式切到“ 三角面显示网格（派生）”，页面图例实报原分辨率下376个湿四边形、752个三角面、1217条去重边；线条间隔从1改为2后图例相应变为90个湿四边形、180个三角面、669条边，透明度滑块从0.85改为0.4，网络节点开关可切换。恢复线条间隔1、透明度0.85、节点关闭、连续水体模式后，图例回到376/752/1217。页面文字和绘制结果均说明这是视图派生剖分、求解器拓扑不变；因此沿用此可视化方案，没有改求解网格。
- Erken 对照运行检查：8766 `/api/run/status` 为 `idle`（`user-journey-Erken-import`），当前没有活动 GETM/FABM 求解进程。8768 的 `/api/run/status` 为 `completed`、43200/43200步，但其 `candidate_fixed/README.txt` 明确写明这是合成 Imported Random Lake 几何、将 Erken 气象广播到距站点约8000 km 的探索性代理实验，不是 Erken 湖泊模拟或科学验证；不把它当作 Erken 实地网格对照。另找到已完成的 Erken June 2024 direct-SWR A/B/C 168小时隔离候选运行：A、B状态为returncode 0、Completed标记、无fatal/EOF，三类输出各168帧；C原始顺序运行状态文件留在“running”快照，但独立 C rerun 的 `status.json` 明确为returncode 0、Completed、无fatal/EOF，且 `validation.json` 为 valid。Sol 另用 `.venv` 中 netCDF4 直接读 A/B/C `output.nc`，确认时间轴完全相同（3600–604800 s，每小时168帧）、所需变量存在且阵列形状168×10×18×44。青蓝藻与低光 cohort 合计的未加权湿层/格均值：A 0.29863402→0.45550661、B 0.29863487→0.45555168、C 0.29863487→0.44299881 gDW/m³；A/B逐帧均值平均绝对差2.83098e-5 gDW/m³，最大相对差0.010703%；C末帧相对B低2.755531%。B→C只在 `fabm.yaml` 中观察到低光 cohort `cLOptRef` 从23改为12（同时 `getm.inp` 有文件级差异；仅配置改变并不保证科学因果解释）。这是候选求解器运行，非生产求解器；June气象直接短波有源数据依据，但固定云量、零蒸发、关闭河流、单站广播及生态初值等仍含代理/简化。该结果闭合运行与文件/时间轴检查，不构成Erken科学验证或已验证的竞争机制。

### 2026-10-24 Sol：垂向夸张与黑色湖底的同帧控制观察

- 保持 Erken 导入案例 frame19、镜头 +34°、模型位置 +15%、连续水体和其它显示设置不变，只切换垂向放大：1×、20×、50×时底面显著压扁，未见明显黑色下侧大片；100×出现窄黑色底面片；200×黑色下侧大片清晰复现；切回自动适配166.5×后异常仍明显。页面显示数据时刻和模型范围未变。该单因子浏览器对照表明黑片的可见程度随垂向放大升高而增大，但低倍率也会压扁/遮蔽侧壁，不能据此断定根因或修复。
- Luna复查确认床面 trace 按湿单元生成相互独立的四角点与两个三角面，全环境光、无漫反射；历史 `intensitymode` 试验未解决且已撤销。当前没有被证实的源码修复，生产源码保持原样。高倍率/高纵横比下的 WebGL 深度精度或床墙/其它面片相交是待验证假设；下一步需在同一高倍率下单独隔离床面与墙面绘制（若 UI 无独立墙层，则用最小源码实验另开隔离浏览器案例后由 Sol 验收），确认后才修复。桌面应用保持 PID 87684 和相同脚本哈希；无源码变更，无需重启。

### 2026-10-24 Sol：桌面同步版本下复验 3D 播放与床墙隔离

- 在临时诊断版中仅隐藏 `湿网格边界剖面` trace，浏览器 200× 垂向放大下仍看见床面下方黑色大片，故单独墙 trace 不能解释异常。该诊断行已由 Luna 精确撤销，未保留到生产源码。
- 诊断服务重启切换期间一次交互出现 `Failed to fetch`，案例重新加载、数据请求稳定后，最终版下一帧 0→1 实际成功。位置设 +15%，随后 1 fps 播放6.5秒到 frame7，位置仍 +15%；继续自然播放到 frame19/19 自动暂停。面板显示目标/实际1/1.0 fps、成功帧19、0/19绘制超预算、0次帧间隔超目标10%。桌面服务PID 68940、health ready；本地与 HTTP `/static/js/viz3d.js?v=92` SHA-256均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。
- 黑床面在 200× 墙 trace 隐藏实验中仍可见，当前根因未定、未修复。最终源码恢复原边界 trace 条件；实验和重启后再次核对服务脚本与本地哈希相同。桌面版本同步验收通过。

### 2026-10-24 Sol：黑色湖底在静态/动态地形切换下复核

- 保持 3D 页面 frame19、镜头 +34°、模型位置 +15%、垂向 200×，将“水面显示所选变量”关闭，页面切到静态 `bathymetry.nc` 地形预览。浏览器画面为蓝青水深色面与可见岸壁，没有近黑色大片；恢复动态变量叠层后，同一视角下黑色下侧大片复现。随后恢复垂向自动适配166.5×并保持动态变量叠层开启。
- 该对照把问题范围缩小为动态变量叠层路径或其与床面/水体几何的交互。静态预览与动态叠层分支使用的数据、床面 trace 属性不完全相同，因此不能由此直接归因某个字段，也不能声称修复。当前生产源码保持原样，黑床面待进一步隔离。
- 当前最终页面仍为 `user-journey-Erken-import`，3D frame19/19、+34°、位置+15%、自动垂向放大、动态变量叠层启用。桌面服务PID 68940 health ready，本地与HTTP脚本哈希一致；本次仅文档更新，无源码变更。

### 2026-10-24 Sol：食性网络当前活动案例浏览器验收

- 在桌面最终版浏览器进入 `user-journey-Erken-import` → 模型配置 → 生态网络与食物网，网络来源为“当前活动案例”。开启“食性配置分层图”后，画布显示生产者/碎屑与消费者配置分层，三节点路径卡标注实例名和各段 FABM 端口。
- 展开食性端口核对表，页面实际列出全部17条可解析猎物→消费者边，未解析引用0、声明但未配置端口0、三节点闭环0；表格逐行显示 YAML 实例名、猎物→消费者方向、消费者端口和“目标状态/单位未在此视图核验”限制。Sol 另读当前案例 `fabm.yaml` 的真实 prey 引用并与页面对应，确认该展示没有推断补画；新加的 `erken_added_algae_20261023_a1` 实例可在猎物候选中选择，但当前17条配置边里没有把它伪报为猎物。
- 选择真实 JuFish 实例后，食性编辑器回显已有 PLAN 组及两个已配置猎物（copepods、cladocerans），各自显示现存 clearance/gut 参数；没有保存任何改动。当前案例本轮浏览器食性图通过配置来源与可追溯性检查；模型端实际 state 注册、单位和求解运行时兼容性仍未被此视图验证。仅交互，无源码变更。

### 2026-10-24 Sol：动态床面深度与静态底深 API 对照

- 只读请求本地 `/api/results/3d_surface`，对 Erken 导入案例 frame 0、1、19 比较响应中的 `water_depth`（动态 hn）和 `bottom`（静态底深）；target=26采样后均有185个共同有效点。API `surface_sync_mismatch=false`、`surface_source=hn-bathymetry`、`depth_source=hn`。water_depth相对bottom差值分别为：frame0 −0.00426至+0.00685 m（平均绝对0.00131 m），frame1 −0.00803至+0.01134 m（平均绝对0.00304 m），frame19 −0.00213至+0.00342 m（平均绝对0.00053 m）。动态和静态深度确有小差异；垂向高倍放大时其投影幅度会扩大，但该相关性尚未通过床面剖分控制实验证实为黑面原因。无源码变更。

### 2026-10-24 Sol：黑床面动态/静态几何诊断与最终播放复验

- 临时诊断中将动态变量/缺测网格 traces 设为 `legendonly` 后，frame 0 高放大下黑床面仍可见；再强制动态视图床面几何使用静态 `bottom`，Erken 导入案例 frame 19、+34°、模型位置 +15%、垂向200×时黑色大片仍可见。因此单独的动态场 mesh 或动态 `water_depth` 床深几何均不足以解释黑面；异常仍关联“湖盆水深”中性床面 trace 的绘制路径。此实验未证实精确根因，也没有生产修复。
- 上述两处临时源代码改动已由 Luna 精确撤销。最终生产源码 `viz3d.js?v=92` 的本地与 HTTP SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`；桌面启动器 health ready、PID 80504，参数 `launcher.py --desktop --port 8766`。浏览器刷新并重新进入 3D 页，加载的是该最终资源版本。
- 最终版浏览器播放从 frame 0 实际播放至 frame 19 并自然暂停：目标/实际 4/4.0 fps、成功帧20、整帧P50/P95 35/52 ms、绘制超预算0/20、帧间隔超目标10%为0。播放中 frame 5 和终帧均显示模型位置 +15%；最终 position 控件值为15。当前黑色底面问题仍未修复。仅追加审计记录，无产品源码变更。

### 2026-10-24 Sol：湖底 mesh 单 trace 与纯色绘制隔离

- 进一步隔离 3D 主绘图数据：仅把原始“湖盆水深”床面 trace 送入 Plotly，并暂时禁用顶点强度、深度色带与颜色范围、指定纯绿 `#00ff00`；保留床面几何、200×垂向放大和原环境光设置。浏览器在 `user-journey-Erken-import` frame19、镜头 +34°、模型位置 +15% 下仍观察到同样黑面，而图例未出现动态变量网格 trace。HTTP HTML 引用 `viz3d.js?v=93`，该脚本与临时源码哈希一致。本结果说明原深度色带和相邻 trace 均不是黑面出现的必要条件。
- 更早的一次试验只在 `lakeTraces()` 中裁掉基础 trace；科学变量网格会在其调用返回后追加，所以那次并非真正 bed-only，已从证据中排除。后续将临时裁剪放到 Plotly 调用前，才得到上述单 trace 实测。
- 全部临时纯色、trace裁剪及 `v=93` 缓存键已撤销。生产桌面服务恢复 ready，PID 64428；页面 HTML 引用 `viz3d.js?v=92`；本地和 HTTP 返回脚本 SHA-256 同为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`；源码无临时诊断标记。黑面仍未定位或修复。仅审计文档新增记录。

### 2026-10-24 Sol：8766 最终桌面源码下 2D/3D 20 帧播放复验

- 在浏览器当前活动 `user-journey-Erken-import` 案例中，2D 水温结果从 frame 0 播放至 frame 19 并自然暂停；页面统计目标/实际 4/4.0 fps、成功帧 20、整帧 P50/P95 3/3 ms、绘制超预算 0/20、帧间隔超目标 10% 为 0。色标首尾范围改变，说明帧数据随时间更新。
- 同一案例 3D 水温结果将“模型上下位置”设为 +15%，从 frame 0 开始以 1 fps 播放。浏览器实际中间观察到 frame 11（成功帧 12），随后到达 frame 19/19 并自动暂停。终态统计目标/实际 1/1.0 fps、成功帧 20、整帧 P50/P95 36/48 ms、绘制超预算 0/20、帧间隔超目标 10% 为 0；模型位置终态仍为 +15%，色标范围随帧变化。
- 桌面服务监听 PID 64428，命令行为 `3DWET/app/launcher.py --desktop --port 8766`；浏览器脚本资源 `viz3d.js?v=92` HTTP 200，本地源码和服务返回内容 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本次仅追加审计文档，无产品源码变更。
- 此次实测只验收当前 20 帧导入工作流的 2D/3D 播放与垂向位置跨帧保持；不代表黑色湖底已修复，也不替代最新源码下完整的“导入→运行→结果→视角→添加生态组分→分析”全流程复跑或 Erken 168 帧候选输出的科学验证。


### 2026-10-24 Sol：当前验收范围与案例状态汇总

- 最新桌面源码（`viz3d.js?v=92`，SHA-256 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`）已在浏览器实测当前 Erken 导入案例 2D/3D 各20帧从首帧连续播放到末帧并自然暂停；3D 模型上下位置 +15% 跨帧保持。具体性能面板数值见本文件上一条记录。黑色底面仍可见，尚未修复。
- 六步用户流程（数据导入、运行、查看动态结果、调整视角、添加藻类 cohort、分析新增时间序列）有此前浏览器会话通过记录，但记录中的源码 SHA 是 `BEDCC8128D45E7AB2DF05466410D7A36AD0A32BCC59CD6959B4B379C2C6CFE48`；本轮只在新 SHA 下复验了播放与相机，没有重跑整个六步链。因此“六步流程”旧测次通过，“当前源码指纹下完整流程复验”仍待做；计划中的正式五轮完整验收仍为 0/5。
- 案例边界：Erken A/B/C 是候选 solver 的168小时机制敏感性运行，输出完整性已过，使用实测短波但也有 held-value 边界垫片、云量/蒸发/河流及生态代理，非科学验证；Lake Ravn 已有官方 GOTM 工作副本和代理/默认配置敏感性结果，但率定来源未确认、数值修复计数仍有风险，非独立验证；Bryrup 因官方求解器分支/模型输入不完整且现有 runner 初始化不兼容而未完成论文复现；Arreskov 缺案例专属生态配置、匹配校准集合/初态及观测，维持 blocked、未运行。详见各案例源审计与报告，不以代理结果填补缺失科学证据。
- 本轮只改审计记录，没有改产品源码。桌面应用仍由 PID 64428 的 `launcher.py --desktop --port 8766` 提供；HTTP 与本地 `viz3d.js` 哈希一致。
- 关于原“三角网等网络可自主调整”的表述，我按当前结构化 GETM 网格与已存在 UI 作 Sol 侧解释：验收显示层的连续水体/正交网格/派生三角网/隐藏模式，以及派生网格间距、线透明度和节点开关；不把它解释成修改结构化求解网格或转换成非结构三角求解器。浏览器里这些显示选项和间距变化已实测，UI 标明求解器拓扑不变。参考图没有提供，故不声称与某张参考图一致。

### 2026-10-24 Sol：最新源码下完整用户流程浏览器验收

- 在 `current-source-user-journey` 隔离案例中实际走通：上传已审计 Erken CSV → 生成 44×18、27 时步的 meteo.nc → 配置 2 小时/2 秒步长并构建 → 工作台预检与求解 → 2D/3D 查看动态结果及播放 → 调整 3D 模型上下位置 → 添加藻类实例 → 再运行 → 时间序列提取分析。输入来源的 25 条 SITES-derived 记录含已标注代理强迫，另有 2 条显式 held-terminal 边界垫片；无河流，不能称为完整观测强迫或科学验证。
- 第一次 3600 步运行由工作台启动，完成约 48.1 秒，页面日志报告结果有效性检查通过，2D/3D 结果归档到该副本的 `output/`。浏览器播放实测：2D 20/20 帧、目标/实际 4/4 fps，P50/P95 4/5 ms；3D 20/20 帧、目标/实际 1/1 fps，P50/P95 40/74 ms；两者均 0 次绘制超预算、0 次超过目标间隔10%的迟帧。3D 帧推进期间和末帧，“模型上下位置”保持 +15%，色标随帧变化。
- 通过实例管理 UI 从 `cyanobacteria` 创建 `cyanobacteria_workflow_cohort`，选择“同功能群等总量分摊”、比例0.5。UI预览列出12个明确初始状态。实际保存后对比备份：`cyanobacteria` 的 `sDW/sCW/sDS/sCS` 从 `0.3/0.04/0.003/0.0012` 各降为一半；新实例获得 `0.15/0.02/0.0015/0.0006`。这确认该次克隆正确分摊初始 biomass share。新增 cohort 不是新物种或独立性状，食性引用保持不变，未向它或其他消费者编造食性边。
- 第二次工作台运行完成3600/3600步，约68.4步/秒，日志有效性检查通过。当前副本 3D NetCDF 包含 `cyanobacteria_workflow_cohort_sDW`，形状 `(20,11,18,44)`；时间序列页实际选择该变量并提取“全湖平均”，图表成功显示。NetCDF 全域（含陆格/垂向层）均值从首样本约0.14995 gDW/m³至末样本约0.14912 gDW/m³；全域有效值范围约0.13695–0.15232 gDW/m³。这是该代理强迫的短试运行诊断，不是实测生态结果。
- 食性网络页面显示当前案例17条已解析 YAML prey→consumer 引用、0条未解析，来源为当前 `fabm.yaml`，并明确不代表运行时摄食/营养级验证。逐条引用及端口证据见前述食性网络验收记录。
- 最新桌面服务仍由 PID 64428 的 `3DWET/app/launcher.py --desktop --port 8766` 提供；页面资源 `viz3d.js?v=92` HTTP 200，本地/服务返回 SHA-256 一致，均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本次未改产品源码；只追加审计记录。
- 此次完成当前源码指纹下六步浏览器流程的实操复验。Erken 168小时 A/B/C 仍属于候选求解器的代理强迫敏感性案例，不是实测科学验证；Lake Ravn、Bryrup、Arreskov 的数据与完成边界仍按上文分别标注。黑色床面阴影未修复；参考图待补充。计划中的正式五轮验收目前只有本次一轮新源码完整流程，不能报五轮通过。

### 2026-10-24 Sol：Erken June 2024 A/B/C 运行状态与对照结果复核

- 重新读取 attempt03 状态与独立 C rerun 文件。A、B 状态文件均为 return code 0；C 独立重跑 `arm_C_rerun_20261023/status.json` 为 `Completed`、return code 0、completed marker=true、fatal/EOF=false；对应 `validation.json` 为 valid，完整输出与 168 帧时间轴齐全。旧的 `direct_swr_168h_run_status.json` 仍把已中断的原 C PID 87580 标作 running，且该 PID 当前不存在；此字段是过期状态，实际 C 结果以独立重跑与 validation 文件为准。
- Sol 再用 NetCDF4 直接读取 A/B/C 的 `output.nc`，分别得到168帧（3600–604800 s），所比较的逐帧湿层/格均值均有限。青蓝藻总 sDW 均值 A=0.29863402→0.45550661、B=0.29863487→0.45555168、C=0.29863487→0.44299881 gDW/m³；A/B 平均绝对差 2.83098e-5、最大相对差0.010703%；C相对B末帧低2.755531%。结果与已存审计值吻合。
- 这确认“等待 Erken 对照运行”已结束且 A/B/C 输出可读；仍属于 candidate solver 下的代理强迫机制敏感性运行，并非实测生态对照或科学因果验证。无模型进程仍在运行。本轮未更改产品源码。

### 2026-10-24 Sol：黑色床面在短流程与 Erken A 输出中的复现确认

- 最新短流程 `current-source-user-journey` 的浏览器 3D 图，在 temp、frame1、自动垂向放大166.4×、斜视34°、模型上下位置+15%时清楚显示蓝色水面/湖盆下方成片黑色三角面；同次从frame0点到frame1，模型位置仍显示+15%。因此该黑面并不限于June 2024候选输出；相机跨帧保持也在当前页面再次观察。
- Luna 在浏览器实际打开 June 2024 Erken A 组 `arm_A/case`，temp frame19（2024-DOY166 09:00），自动166.4×、+34°/+15%下也复现黑色湖底；200×时增大，89°俯视时不见相同大块，水平0°时出现大块黑侧/底影。只读 API与当前构造函数重算得到376湿格、1504个床面角点、752个三角形，未发现退化三角或异常绕序；此检查不能证明渲染根因。
- CUA接口没有运行时代码 evaluate/DevTools能力，无法仅靠页面可访问性层抓取 Plotly `_fullData` 或 GPU buffer dtype。当前没有基于猜测的修复。正在用 Sol 审核的临时运行时观测仪表补取 trace 属性、顶点/索引与镜头/坐标范围；仪表将立即同步到桌面应用、观察后撤销并再次同步。黑影修复保持未完成。

### 2026-10-24 Sol：床面三角绕序 A/B 与最终桌面版本复核

- 在 Erken A `arm_A/case` 的 frame 19、镜头仰角 +34°、模型位置 +15%、垂向放大 166.4×下，浏览器临时交换床面每个三角形的两条索引，再恢复原绕序。两种截图中的黑色下侧面视觉相同；结合此前隐藏岸壁后仍黑、隐藏床面后黑面消失、平滑/平面着色相同，确认异常随湖盆底面 mesh trace 绘制，但绕序不是已证实原因。无生产修复，继续标记根因未确认、未修复。
- 硬刷新并重新进入 3D 页面后，浏览器显示正式水温结果、模型上下位置控件和四种网格显示模式；无临时绕序诊断按钮。桌面服务 `/api/system/health` ready=true、PID 64428；首页引用 `viz3d.js?v=92`，脚本 HTTP 200；本地和 HTTP 响应 SHA-256 同为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。因此本次清理后桌面应用加载正式源码版本已核验。
- 本轮无产品源码修改，仅追加此审计记录。三角网需求继续由 Sol 按现有 UI 明示范围解释为视图层网格显示/间距/透明度/节点调整，不改 GETM 求解拓扑；用户回复不懂后由 Sol 继续作此判断，不再向用户追问。参考图没有提供，待补充。

### 2026-10-24 Sol：床面强制纯色 A/B 与 v94 最终恢复

- 在 Erken A frame19（2024-DOY166 09:00）、+34°、+15%、166.4× 的全屏浏览器画面中，临时把床面 trace 克隆为逐面纯洋红 `#ff00ff`，移除 intensity/vertexcolor/色标映射并用 `Plotly.react` 重绘。原先黑色的大部分下侧床面变成洋红，少量蓝灰面仍在。该受控 A/B 表明黑色呈现涉及床面颜色/着色路径；和绕序 A/B 无效的结果一起，缩小了诊断范围，但尚不能确认究竟哪项 trace 属性或 WebGL 状态导致，也没有生产修复。
- 诊断临时对象的“恢复”按钮没有即时恢复浏览器中的洋红 trace；因此清理诊断代码后通过重载正式 v94 页面并重新加载 Erken A 案例，确认画面恢复原始黑面，临时按钮数量为0。最终 `/api/system/health` ready=true、PID 62116；首页为 `viz3d.js?v=94`；脚本 HTTP 200；本地/服务 SHA-256 均为基线 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`，服务脚本不含临时诊断 marker。此次无产品源码改动，仅有临时诊断代码已清理与版本缓存号更新。

### 2026-10-24 Sol：正式浏览器完整播放与床面诊断复核

- v96 正式页面中重新加载 Erken A（`arms_168h_direct_swr_padding_verified/arm_A/case`）并在 3D 视图将位置设为 +15%、速度设为 12 fps、范围 0–167。浏览器实际播放从 0 连续推进；约5秒时达到 frame 63，页面计数目标/实际 12/12.0 fps、成功绘制60帧、绘制超预算0/60、帧间隔超目标10%为3。继续播放至 frame 167，播放器自动暂停。末态实际控件值 frame=167、仰角=34°、模型上下位置=+15%；末次性能状态成功绘制60帧、绘制超预算0/60、帧间隔超目标10%为5。确认3D全168帧自然结束并保持模型位置。
- 后续仅做 v97 临时诊断：保持 Erken A frame19、+34°、+15%、自动垂向166.4×；先记录原 intensity 色彩图，再单击“use mapped vertex colors”。全屏浏览器实际画面中的大块黑面与蓝灰片几乎未变。因此强度均一化对照和按原色带预映射顶点颜色对照都没有解决/解释黑面；纯色 override 曾改变大部分黑区，但这些证据仍不能区分 WebGL/着色、几何深度与材质交互，黑影根因未定、生产代码未修复。
- Luna 移除上述临时诊断块与按钮、缓存参数更新到 v98 并同步桌面。最终服务 ready=true，PID 7908，页面引用 `viz3d.js?v=98`，HTTP 200；本地源与服务脚本 SHA-256同为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`；服务脚本中没有 `use mapped vertex colors` 或 `uniform bed intensity` 临时标记。硬刷新后在 v98 实际完整播放 Erken A 2D 0–167：约5秒到 frame63，目标/实际12/12.0 fps、成功绘制60帧、绘制超预算0/60；继续到 frame167 后自动暂停，最终计数成功绘制60帧、绘制超预算0/60、帧间隔超目标10%为7。该诊断轮有少量间隔迟帧，但没有停帧且全范围完整结束。
- 本次完成了 2D/3D 浏览器实播验收和 v98 桌面服务源码一致性核验。黑色床面阴影仍未修复；参考图仍待补充。模型上下位置、显示网格间距/透明度/节点开关与三角网只改变显示拓扑的先前浏览器实测记录不变；全流程、食性边来源、案例数据分类详见上文。Erken A/B/C 是代理强迫下候选求解器运行，不是实测科学验证；Lake Ravn 为代理/默认敏感性，Bryrup未完成，Arreskov缺案例数据，不能合称案例验证全部通过。

### 2026-10-24 Sol：3D 视角预设对照观察补记

- 在最终 v98 浏览器页 Erken A frame19、模型位置 +15%、仰角 +34°、自动垂向放大 166.4× 下，分别切换侧视与正视预设观察床面：蓝色水体和黑色下侧床面仍可见，正视中黑色三角片仍明显；侧视投影下黑面范围变化。之后恢复斜视、+34°和+15%。这些预设同时改变投影/方位，不能单独归因具体相机轴，也未解释黑面根因。
- 之前 168 帧 3D 播放实际已从首帧连续到末帧并自然暂停，位置 +15% 跨帧保持；本次只是 UI 对照，无源码修改。桌面服务已核验 ready、v98、本地/HTTP 源码哈希一致。黑面问题仍未修复。

### 2026-10-24 Sol：3D 模型位移实际对照与跨帧保持

- 在本地浏览器 Erken A 三维温度结果 frame19 做 UI 实测：把“模型上下位置”从 +15% 调到 −15%，截图中模型在画面中的垂直位置随之改变；随后恢复 +15%，点击“三维下一输出帧”使时步从 frame19（2024-DOY166 09:00）前进到 frame20（10:00）。刷新后的无障碍树显示镜头仰角仍为34°、位置仍为+15%、垂向放大仍为166.4×，帧值为20，色标也随时间更新。因此控件的正负方向能实际移动模型，且单帧切换保持所设位置。
- 当前 Erken A 案例在166.4×斜视下仍可见床面黑色下侧面；本次没有代码改动，不能视为阴影已修复。桌面服务 PID 7908、ready=true，v98 本地源码和 HTTP 返回脚本 SHA-256仍一致。本次只追加验收记录。

### 2026-10-24 Sol：黑色床面视角/垂向比例补充观察

- 在当前 v98 浏览器页 Erken A frame20（2024-DOY166 10:00）、镜头仰角 +34°、位置 +15% 下，关闭“显示岸陆示意”后黑色床面三角仍可见；这排除了 beige 岸陆示意平面本身是黑面来源，但仍不能判定床面 trace 内的根因。切换至真实比例 1× 时该视角中黑面不可见；恢复“自动适配湖盆”166.4×后仍可见。此 A/B 与垂向放大或投影强相关，但不能区分几何遮挡与渲染着色，问题继续未修复。
- 对照时曾水平拖拽图形，导致镜头仰角也改变，该次操作不作为根因证据。之后通过镜头预设恢复斜视/+34°、垂向放大恢复自动166.4×、岸陆示意恢复开启，并将模型位置恢复到验收前+15%。浏览器 UI 最终显示 frame20、斜视、+34°、+15%、岸陆开启；无产品代码改动。
- 桌面本地服务当前 PID 7908（python），HTTP 脚本返回200；`3DWET/app/static/js/viz3d.js` 与 `/static/js/viz3d.js?v=98` 服务响应 SHA-256均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。源码和桌面服务仍一致。

### 2026-10-24 Sol：Erken June 2024 对照组 A 的浏览器全范围实播

- 当前桌面服务恢复的活动案例路径为 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`；健康端点给出 ready=true，案例输出时步数168。没有切换或改写案例目录。
- 在工作台浏览器对该 A 组真实输出执行 3D 全范围播放：起止帧0–167，12 fps；5秒观察点已经到 frame138，性能状态显示实际12.0 fps、成功帧60、整帧28 ms、P50/P95 32/42 ms、绘制超预算0/60、帧间隔超目标10%为5；随后实际到 frame167 并自动暂停。终点无障碍状态确认输出时刻2024-DOY172 13:00、播放勾选已关闭，镜头+34°、模型位置+15%。
- 在同一 A 组输出切换到 2D，起止帧0–167、12 fps；5秒观察点达到 frame139，显示实际12.0 fps、成功帧60、整帧4 ms、P50/P95 4/5 ms、绘制超预算0/60、帧间隔超目标10%为0；之后到 frame167 并自动暂停。末态实际超目标帧间隔计数为1。该轮2D/3D各完整走完168帧，无停帧。
- 该运行仍是候选求解器的机制敏感性结果：SITES实测温度/短波等部分输入外，云量固定0.5代理、蒸发为0、河流停用、生态场有模型默认/代理，末尾额外气象样本为计算边界填充。不能称作 Erken 实测科学验证；仍待将 B/C 组也在浏览器播放。
- 本轮无产品源码修改。本地服务仍需复核为 ready 且 v98 served `viz3d.js` 与当前源码 SHA-256一致；复核时服务 ready=true、PID 7908，脚本 HTTP 200；本地源与服务响应 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。

### 2026-10-24 Sol：Erken June 2024 B/C 组 2D/3D 浏览器全范围实播

- 通过工作台“案例管理 → 按路径打开案例”，只读加载已经结束的 Erken B 组 `arms_168h_direct_swr_padding_verified/arm_B/case` 和 C 独立完成重跑 `arm_C_rerun_20261023/case`。两者仪表盘都显示10个垂向层、21个生态模块、168个输出时步；未重跑、未编辑案例输入。
- B 组浏览器 3D 从0/167以12 fps播放，中途5秒观察为155/167，实际12.0 fps、成功绘制60帧、整帧38 ms（P50/P95 30/36 ms）、超预算0/60；到167/167自动暂停。B组2D同样从0到167自动暂停，中途5秒为154/167，实际12.0 fps、成功绘制60帧、整帧4 ms（P50/P95 4/5 ms）、超预算0/60。色标及日期时刻随帧变化。
- C组3D从0开始；首个样本窗口因解码较慢显示实际9.9 fps，随后约5秒到151/167，实际12.0 fps、成功绘制60帧、整帧33 ms（P50/P95 29/33 ms）、超预算0/60；到167/167自动暂停，模型上下位置保持+15%、镜头仰角34°。终态实际12.0 fps、成功帧60、整帧28 ms（P50/P95 30/38 ms）、超预算0/60。C组2D中途5秒到160/167，实际12.0 fps、成功绘制60帧、整帧4 ms（P50/P95 4/5 ms）、超预算0/60；随后到167/167自动暂停。播放窗口统计有少数间隔超过目标10%（B/C 3D终态5，B/C 2D终态分别0/2），但帧号持续前进且未观察到停帧。
- A组全168帧浏览器播放记录见上一条。至此A/B/C三组均完成2D与3D全范围浏览器播放验收（各0–167）；这只验收播放器消费这些已有 NetCDF 输出，不提升候选求解器代理强迫结果的科学证据等级。运行结果仍是部分实测强迫与代理/默认设定并存的机制敏感性案例，详见各组数据审计。
- 同一桌面浏览器中实际打开 A 组生态网络，选择“食性配置分层图”并展开关系表：读取17条可解析 YAML 猎物→消费者端口关系，0条未解析、0个未配置端口、0个已闭合三节点环；逐行展示实例、方向、消费者 FABM 端口和来源说明。关系展示来自当前案例 fabm.yaml 的真实引用，页面明确提示状态注册/单位未在此视图核验，且配置边不等于运行时摄食通量。未编造或补画边，未保存任何配置。
- 本轮没有产品源码改动；没有需要同步的代码。桌面服务 `/api/system/health` ready=true、PID 7908；HTTP `viz3d.js?v=98` 返回200，本地与服务内容 SHA-256同为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本记录补入时无源码变更。

### 2026-10-24 Sol：v98 Erken A 三维播放现场复验（0–167）

- 在当前桌面应用浏览器页，将三维时间滑块设为 frame 0，点击实际播放控件，连续采样浏览器可访问状态。帧号顺序观察到 2、7、13、18、23、29、99、126、151、167；播放控件最终自动关闭并停在 167/167。整个播放区间未出现帧号停住；早期窗口解码/绘制较慢（首个3帧窗口2帧绘制超预算），最终60帧统计目标/实际 12/11.8 fps、整帧30 ms（P50/P95 35/44 ms）、绘制超预算0/60，帧间隔超目标10%计数19。故通过“实际帧持续前进并完整到末帧”的验收，达不到每个帧间隔均符合12 fps的严格实时性；报告该性能边界，不称绝对无迟帧。
- 跨帧采样中“模型上下位置”持续为 +15%；终帧控件仍为 +15%，时间为 2024-DOY172 13:00。此处确认本次全168帧3D播放没有重置垂向位置。帧推进期间页面色标和时刻变化。
- 桌面服务核验：`/api/system/health` ready=true，PID 7908；`/static/js/viz3d.js?v=98` HTTP 200；本地文件和HTTP响应 SHA-256均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。无产品代码更改，不需重启同步。本次检查到的黑色湖底仍在实际画面中可见，问题未修复。

### 2026-10-24 Sol/Luna：湖底渲染根因审查（未形成可上线修复）

- Sol/Luna 复核当前正式源码：床面由湿单元独立四角点和两三角面构成；动态变量视图以中性灰色显示床面并关闭床深强度映射，静态水深预览才使用底深顶点值，并设置 `ambient=1, diffuse=0, specular=0`。页面禁用“湖盆水深”床面 trace 时黑片消失，启用时复现；几何采样和绕序旧检查未见退化面/异常绕序。历史受控观察表明黑片随大垂向夸张增多，纯色覆盖会改变多数黑片，但不消除全部暗片。
- 以上证据只定位到床面 trace 的绘制结果，不能区分其输入颜色/强度、屏幕深度精度、三角插值或 WebGL 着色器因素。CUA 当前可用浏览器界面不能读取 Plotly 运行时 `_fullData` 或 GPU buffer，无法完成针对实际提交给 renderer 的 trace 数组检查。Luna 因此未作源码修改；Sol 不接受再试改光照、颜色、绕序等未经定位的猜测性改动。黑影仍未修复。
- 后续可证伪路径是获得可信的 Plotly 运行时 trace 数组检查，并在保持相机/颜色/连通性不变时单独对照 Z 坐标跨度；若当前浏览器环境不能执行该项，则保留为未完成。当前无产品源代码变化，桌面服务不需同步或重启。


### 2026-10-24 Sol：活动 Erken A frame167 床面 API 几何核算

- 通过 8766 实际“案例管理”页面确认活动案例路径为 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`；服务 run-status 为 idle。只读请求实际 frame167、`target=26`、底层变量 slice API，并按当前源码 `buildLakeGeometry` 的 cell-edge/connected-wet-corner/quad-triangle 构造规则核算，未更改结果或源码。
- 响应来源为 `hn-bathymetry`，`depth_source=hn+zc`，`surface_sync_mismatch=false`；网格 shape `[1,18,22]`，185个采样湿格，对应740个床面顶点、370个三角面。所有构造顶点有限；370个三角形零面积数为0，法向 Z 符号一致为正，三角面积范围62,500–312,230.625 m²。仅两个共享格角连接了彼此不连通的对角湿组件，最大水深差6.783 m；此事实不能单独解释黑面。
- 此结果是 API 数据与源码构造规则的独立几何核算，**不是**实际提交给 Plotly 的 `_fullData` 或 GPU buffer 检查，不能据此排除运行时转换/着色器问题。CUA 页面接口未提供运行时代码执行，快捷键尝试后也未出现可访问的开发者控制台。床面黑影根因仍未确认、未修复。
- 桌面服务 `/api/system/health` ready=true、PID 7908；工作台显示当前 A 案例，run-status idle。无源码改动，桌面同步无需重启。
- 在新绑定的 IAB 工作台会话中，案例管理当前项仍标明同一 Erken A 绝对路径。三维页从 frame0（2024-DOY165 14:00）将模型上下位置设为+15%，点击实际“下一输出帧”至 frame1（15:00）；无障碍状态同步显示帧1、位置+15%。此为浏览器 UI 再次实测，未保存/改动案例。

### 2026-10-24 Sol：Erken A v98 浏览器实播与床面 Plotly 运行时诊断

- 通过桌面工作台浏览器打开 Erken June 2024 A 案例 3D 结果，frame0 上把“模型上下位置”设为 +15%，手动下一帧至 frame1；页面实际控件仍为 +15%。随后设置 8 fps 自动播放：观察 4.5 秒到 frame38，继续播放期间到 frame88，最终自然运行到 frame167/167并自动暂停。性能面板报告目标/实际约 8/8.0 fps、60个成功帧、整帧 P50/P95 32/38 ms、绘制超预算0/60、帧间隔超目标10%共2；全程未观察到帧号停住，位置控制末态仍 +15%。这是 Erken A 既有结果的 UI 播放验收，不代表重跑科学模型。
- 使用临时只读 `?bed-diagnostic=1` 仪表检查实际 Plotly bed trace。frame0 与 frame167 均报告1504个有限顶点、752个三角形；索引越界0、非有限坐标0、零面积三角0，所有三角的 normalZ 均为正；frame167垂向放大约166.3×。`_fullData` 对比显示 type/intensitymode/cmin/cmax/顶点与索引数组匹配；颜色、lighting、colorscale字段比较不匹配。可见实际画面仍有明显黑色湖底片区，运行时几何检查并未显示退化或绕序异常，但字段差异本身还不足以认定黑影根因或支持生产修复，故黑影保持未修复。
- Luna 随后精确移除本次临时只读诊断常量、面板函数与两个调用点，保留其他源码和 `v=98` 缓存版本；`node --check` 通过。Sol 独立复核桌面 `/api/system/health` ready=true、PID7908；`/static/js/viz3d.js?v=98` HTTP200；本地/HTTP SHA-256恢复一致为正式脚本 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`；服务响应无 `bed-diagnostic` 标记。随后硬刷新并在同一桌面浏览器重新进入3D，页面加载 Erken 168时步结果、临时面板不存在，确认应用已加载清理后的版本。仪表从未进入默认页面查询参数之外，不改变模型结果或求解拓扑。

### 2026-10-24 Sol：床面统一 facecolor 临时 A/B

- 在 Erken A frame167、bed trace index 0（752 triangles）触发诊断面板的“测试每面统一床色”按钮。`Plotly.restyle` 接受操作，input/source `facecolor` 为752项且全为 `#c5cdd1`；但 `_fullData.facecolor` 仍为 `undefined`，画面中的黑色床底/侧面没有可见变化。
- 下一输出帧重新绘制后临时 facecolor 状态重置。此项只是在本地浏览器中的渲染诊断，不写回或保存案例结果，不改变科学输入/求解拓扑；无法据此确认根因，黑色床面仍未修复。

### 2026-10-24 Sol：Erken A 床面黑片反方位浏览器对照

- 在本地工作台 Erken A frame19（2024-DOY166 09:00）、温度变量、自动垂向放大166.4×、模型位置+15%下先记录默认斜视画面，床面/湖盆下侧可见大片黑色三角面。水平拖动后 Plotly 同时改变仰角（34°→4°，反方向拖动到48°）；因此不把拖拽当作纯方位控制。每次均通过仰角滑块恢复到34°，并在恢复后的截图中确认黑色三角仍存在且其显示位置/轮廓随视图发生变化。
- 通过镜头预设“侧面→斜视”恢复标准斜视；因预设把模型位置复位到0%，随后将位置控件恢复+15%。最终浏览器实际状态为 frame19、仰角34°、位置+15%、诊断面板不存在。该 A/B 说明改变方位后黑片仍能复现，方位不是消除黑片的单一条件；由于拖拽也影响仰角，不能据此判定黑片是否随相机或特定几何面移动。根因仍不明、无生产修复。

### 2026-10-24 Sol：固定帧垂向比例阶梯与浏览器全程复播

- 在桌面工作台 Erken A、温度变量、frame19（2024-DOY166 09:00）、斜视仰角34°、模型位置+15%下，逐一使用页面可选的垂向比例并查看实际绘图截图：1×、20×和50×未见床面黑色下侧片；100×已见明显黑色床底/侧片；自动适配166.4×的黑片更大。可见黑影在离散样本中介于50×与100×之间出现；截图取样只支持显示现象与垂向夸张程度相关，不足以区分屏幕深度、渲染着色或其他几何/绘制原因。未改颜色、光照、相机、床面数据或默认设置。本次控件文字与图内标题一致后才记入样本。
- 随后设自动播放8 fps，从frame19实际点击播放，页面状态观察到frame21、frame53继续变化，最终到frame167并自动暂停；8 fps终态窗口报告实际8.0 fps、成功帧60、整帧41 ms（P50/P95 42/46 ms）、绘制超预算0/60、帧间隔超目标10%为1。位置控件始终为+15%，镜头34°。通过本次浏览器实播确认此段从frame19到167持续前进、没有观察到停帧；帧间隔统计仍有1次超过目标10%，所以不表述为每帧均严格达标。
- 完成后恢复自动适配166.4×、frame19、位置+15%、斜视34°，保持在3D主图供继续检查。`/api/run/status`实际为idle，服务当前指向既有 Erken A 输出目录；此次没有观察到正在执行的Erken对照运行，也没有启动新运行。桌面服务 `/api/system/health` ready=true、PID7908；`viz3d.js?v=98` HTTP200，本地源码与HTTP响应 SHA-256一致，均为`4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本轮无产品代码改动。

### 2026-10-24 Sol：X/Y 重心平移 A/B 与 v101 播放/位置浏览器验收

- 在清理前临时加载诊断版，对 Erken A `arm_A/case` 的 frame19（2024-DOY166 09:00）、自动垂向166.4×、仰角34°、模型位置+15%执行可逆的 X/Y 重心平移。Plotly运行时显示偏移量 X=699863.9880000018、Y=6639646.553000001，且 `_fullData` 与 `_fullLayout` 均可用；重心平移后黑色床底/侧面在浏览器截图中仍可见、外观未发生可辨变化。点击 Restore 后诊断状态回到原坐标，无结果/案例文件改动。此 A/B 不支持绝对X/Y坐标幅度单独造成当前黑片的假设；根因仍未确认，未作生产修复。
- 同一浏览器会话在frame19选择8 fps、播放范围19–167并实际点击播放；观察到主图帧号依次前进并到达frame167后自动暂停。过程中的性能计数到过实际7.9–8.0 fps、成功帧41–60、绘制超预算0/60；终态显示实际8.0 fps、成功帧60、绘制超预算0/60、帧间隔超目标10%为3。帧20、59、116及167附近的诊断状态均显示模型上下位置+15%，仰角34°，垂向自动166.3–166.4×。因此本轮在桌面应用网页实际完成3D播放与跨帧位置保持验收；计数窗仍记录少量超目标帧间隔，不表述为每个间隔均达标。
- 浏览器截图中的床面黑片仍在，故该项仍未修复。临时面板的全页 MutationObserver曾导致诊断页卡住；Luna修正为不监听面板自身DOM变化后完成A/B，并在验收后删除所有临时面板/查询参数/观察器代码。
- Luna将缓存键更新到v101并正常重启空闲桌面应用、保留53864端口。Sol独立核验 `/api/system/health` HTTP200、ready=true、PID73088；`/api/run/status`为idle且仍指向 Erken A 案例；首页实际引用 `viz3d.js?v=101`，脚本HTTP200，本地与响应 SHA-256同为`4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。浏览器重新加载后直接观察到script URL为v101、诊断面板不存在、Erken A仪表盘数据加载完成（376水域格、10层、20生态模块、168输出时步）。`node --check`通过。此次仅新增临时诊断后清理；科学输入和结果文件未改。

### 2026-10-24 Sol：Erken A v101 2D 浏览器实播

- 在桌面工作台当前服务 `http://127.0.0.1:53864/` 的 Erken A 案例（168个既有输出时步）切换到二维可视化，将播放范围设为frame150–167、目标速度8 fps，并在浏览器点击播放。实际观察到帧号到达167后自动暂停；性能面板报告实际8.1 fps、成功帧18、整帧5 ms（P50 5 / P95 37）、绘制超预算0/18、帧间隔超目标10%为0。该观察确认此区间的2D实际帧持续前进；不代表重跑模型，也不替代更长区间验收。
- 当前桌面应用运行版本在本轮前已由Sol核验为v101（`viz3d.js?v=101`、服务ready、PID73088、HTTP脚本与本地源码哈希一致）；本次仅操作浏览器控件，没有改代码或模型文件，无需重启。

### 2026-10-24 Sol：Erken A 食性关系配置再核验

- 对桌面服务活动案例的 `arm_A/case/fabm.yaml` 使用仓库 `.venv` 的 PyYAML 直接解析 `instances[*].coupling`，过滤全部包含 `prey` 的耦合键；实际得到17条关系引用，目标实例逐一存在，未解析目标0。配置来源可按捕食者实例、耦合字段和值追溯：浮游动物/底栖动物各4条连接 cyanobacteria、diatoms、greens、POM；JuFish连接 copepods、cladocerans；AdFish连接 zoobenthos；PiscFish连接 JuFish、AdFish。此结果来自实际运行案例配置，不推断摄食通量或运行时 ingestion。
- 浏览器中发现“生态网络与食物网”导航项，但该导航控件在当前窄面板状态下不可见，自动化点击等待超时；因此本轮没有把食性网络可视化操作冒称为浏览器验收。已有早前的实际页面验收记录仍在，但当前轮补强的是活动配置文件的17条可追溯性与目标完整性核验。
- 服务健康端点仍为ready=true、PID73088，run-status idle，活动案例路径仍为Erken A；本轮无代码、模型配置或结果文件修改，无需同步重启桌面应用。

### 2026-10-24 Sol：Erken A 食性网络浏览器实际验收

- 在桌面应用当前案例 Erken A 中通过“模型配置→生态网络与食物网”进入食性配置页，先展开侧栏模型配置分组，再点击“食性配置分层图”。浏览器状态实际显示完整食性网络、4个配置布局层、10个端点实例、17条真实猎物→消费者边；SVG可访问标签逐条列出端口引用和值，例如 `prey_model1 cyanobacteria → cladocerans`、`PLANprey1 copepods → JuFish`、`PISCprey1 JuFish → PiscFish`。页面完整关系表有17行，状态为20个FABM实例、358个显式耦合端口、17个已解析食性引用；未解析0、声明槽未配置0、闭合三节点有向环0。图页清楚提示边只来自启用且可解析 YAML 配置，不核验求解时摄食通量、目标状态注册/单位兼容，布局层不代表营养级。关系均来自当前活动案例，不补画推测关系。
- 本次导航实测纠正了先前“入口不可见”的判断：工作流侧栏最初关闭，打开后还需展开所属“模型配置”分组；完成后可正常进入。未保存任何配置，未改模型或代码。

### 2026-10-24 Sol：v101 3D 显示网格与垂向夸张浏览器 A/B

- 在当前桌面应用 Erken A、frame167、水温 temp、仰角34°、模型上下位置0%下，浏览器实际切换水体网格：连续水体→正交显示网格→三角面显示网格（派生）。三角模式的图例实际显示“376层湿四边形 / 752个三角面 / 1217条边”；正交模式图例实际显示“正交显示网格”。再将“线条间隔”控件从1改为4，DOM读回为4；恢复连续水体及间隔1后读回默认值。页面状态明确写明显示网格与求解器拓扑不变。本轮未改案例输入或求解网格；由于小视口截图中间隔1与4的线密度差别无法可靠逐条计数，不把该密度差异记作已定量验收。
- 保持同一案例、帧、变量、镜头仰角和位置，只把垂向比例从自动166.3×改为50×；浏览器截图中湖底被压扁，先前可见的黑色湖底/下侧大片未见；恢复自动166.3×后黑色下侧片重新可见。此为本次对同一帧的单变量可逆浏览器观察，进一步支持显示异常与夸张后的几何/视图条件相关，仍不能锁定根因，也不是修复。
- 最终恢复垂向比例自动、网格连续水体、间隔1、线透明度0.85、模型位置0%、仰角34°、frame167；活动结果仍为既有 Erken A。未运行模型、未写案例数据。

### 2026-10-24 Sol：湖泊案例源文件与代理/未完成状态复核

- Erken A 的活动 `meteo_provenance.json` 明确记录：169条逐小时 SITES 气象记录覆盖168小时模拟，SW_IN直接作为入射短波（源范围0–795.5 W/m²）；selected SITES站点序列广播至44×18网格。云量记录0条、固定`tcc=0.5`代理169条；蒸发设为0代理，无河流。模拟停止边界另加1条保持最后观测值的垫片，标记`is_observation=false`。profile为SITES单时刻2024-06-13的50层温度剖面，只用于初始条件。文件列明压力源元数据单位Pa与数值尺度冲突，取值按hPa×100转换；这仍是输入审查事项。结论仍为“含实测短波与温度剖面，同时含多项代理/简化”，不是完整观测强迫或科学验证。
- Lake Ravn 的当前隔离报告确认：完成的是官方 Aarhus WET/GOTM 默认单柱复跑与官方观察资料配对，不是本仓库 GETM 3D 工作台运行，也无参数拟合。运行5844个日输出、276个变量，无未屏蔽非有限值；但温度最低−0.6183°C、内部状态修复计数250670、DO饱和筛查15.87%单元时超过100%，参数校准历史与DO观测元数据未确认。故标记“官方单柱工程复跑/观察配对完成；GETM 3D与科学校准/独立验证未完成”。
- Bryrup 当前隔离attempt的实跑日志确认初始化到9m、18层后以exit1失败：`AdFish: "wet/fish" is not a valid model name`；无积分与输出。官方WET Bryrup配置需要与该生态模块兼容的solver栈；不得强行映射模块。现有案例的科学实验目标还包括N固定竞争组，而当前WET实例没有这组对照，因此论文机制复现未完成。
- Arreskov当前仓库支持目录和隔离副本均无Arreskov专属`fabm.yaml`。官方支持README标出1990–2014 forcing并建议限制到1990–2006；两次隔离启动（1990–2004与建议窗口1990–2006）均在时间/水深/网格初始化后以exit1因找不到`fabm.yaml`失败，没有积分输出。来源恢复审计亦指出缺少论文配套校准成员参数和匹配观测/初态。维持“未完成”，不以代理生态配置补齐。
- 上述结果与隔离目录日志、官方输入副本和既有审计报告一致；本轮未启动任何求解，也未修改代码、案例输入或数值结果文件。桌面服务仍ready=true、PID73088，run状态idle，活动目录为Erken A。

### 2026-10-24 Sol：v101 2D/3D 实际播放与模型位置跨帧验收补记

- 在桌面应用加载的 Erken A（既有168个输出帧）中，将3D位置控制临时设为+15%、目标8 fps，从frame0开始实际播放；连续观察到frame2、34、77，之后播放到114时手动暂停。性能状态报告8 fps目标下实际8.0 fps、成功绘制60帧、绘制超预算0/60。跨帧读取控件仍为+15%、仰角34°；播放器重返3D页时frame167自然终止并暂停。测试结束后恢复模型位置0%、速度1 fps、自动垂向166.3×、连续水体网格。
- 2D页面实际从frame150播放到frame167后自动暂停；目标8 fps、实际8.1 fps、成功帧18、绘制超预算0/18。故本轮在当前浏览器分别实测2D和3D帧推进；这是当前 Erken A 既有输出的浏览器播放验收，不是新模型运行，也不代表所有数据规模/浏览器性能。
- 活动Erken A `bathymetry.nc` 的正值有效水深为376格。按活动几何角点构造对规则网格相邻湿格共663条共享边检查，端点水深差均为0；说明没有发现共享湿边的床面高程接缝，但不能证明GPU三角面绘制没有问题。另按wet-cell平均角点做的三角坡度筛查得到752个派生三角形、网格中值间距250 m；自动垂向放大166.3×时估算最大坡角81.5°，仅1/752超过80°。该近似坡度统计不足以解释或排除黑面；实际3D图中黑色床底/侧片仍可见，根因和修复均未确认。
- 网格需求由Sol按仓库现有UI作保守解释：用户可调的是连续/正交/派生三角/隐藏显示方式，以及显示线条密度、透明度；这属于可视化网格自主调整，求解网格拓扑保持不变。浏览器已确认三角派生网格图例376个湿四边形/752个三角面/1217条边；本轮未修改任何生产网格或产品代码。
- 桌面应用服务由PID73088提供，`/api/system/health` ready=true、`/api/run/status` idle、活动路径仍为Erken A。首页实际引用`viz3d.js?v=101`，脚本HTTP200；本地源码和HTTP响应SHA-256同为`4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。本轮仅做浏览器播放验收与数据诊断，没有代码/案例输入改动，故无需重启桌面应用。

### 2026-10-24 Sol：v101 3D 连续播放复验与对照状态核验

- 在当前桌面浏览器将 Erken A 3D 模型上下位置设为 +15%、播放速度设为 8 fps，点击实际播放控件。浏览器先显示 frame2，持续约5秒后显示 frame115；性能区为目标8 fps、实际7.9 fps、成功帧60、绘制超预算0/60。跨帧后位置控件仍为 +15%。随后经页面播放控件暂停，并恢复 frame167、位置0%、速度1 fps、自动垂向放大及连续水体显示。此项是在既有 Erken A 输出上的浏览器播放实测，不是模型重跑。
- 再固定 Erken A frame167、斜视34°和自动166.3×，实际对照屏幕模型上下位置 +15%、−50%、0%：页面控件文字同步变化，3D湖盆相对视图区发生可见垂直位移；回到0%后恢复中位。播放过程跨帧仍显示+15%。因绘图区占屏高度有限，此为控件与画面可见位移验收，不报告像素级位移。
- Erken June 2024 attempt03 的 A/B/C 候选结果不是“待结束”的活动任务：隔离记录 `ATTEMPT03.md` 标记三臂均完成；C 独立重跑 `status.json` 的 returncode=0、完成标记=true、fatal/EOF=false，`validation.json` 为 valid。当前桌面 `/api/run/status` 为 idle，活动目录是 Erken A 的既有结果；不据此声称任何新的 Erken 求解正在运行。
- 黑色床底/侧片在当前浏览器画面中仍可见，且与高垂向夸张相关的既有实测仍成立；床面单 trace、隐藏墙 trace、纯色覆盖及重心平移等既有隔离并未证实精确根因。因此黑面仍标为未修复，不用改色掩盖。此次没有产品代码或模型输入更改；桌面应用 PID73088、`viz3d.js?v=101` 与本地脚本哈希保持一致，无需重启同步。

### 2026-10-24 Sol：Erken A 湖底 trace 单独显示与 Plotly 背面绘制核验

- 在桌面浏览器 Erken A 的 3D `temp` 页（frame 3，2024-DOY165 17:00），自动垂向放大约166.4×、仰角34°、模型位置+15%。图例单击隐藏“湖盆水深”后，黑色下侧片消失且水体色面仍可见；双击隔离仅显示湖盆水深后，黑片仍附着在床面下侧。固定该帧将垂向比例设为50×时截图未见明显黑片，100×时可见，恢复自动值后复现。水平视角0°时床面黑色下侧更完整；之后恢复34°。
- 这确认黑片跟随湖盆水深 mesh3d trace，且显现程度随垂向放大和相机方向变化；仍不足以确认具体GPU成因。Sol 与 Luna 核对本机 Plotly 2.35.2 bundle：gl_mesh3d 绘制关闭 `CULL_FACE`，片元着色器通过 `gl_FrontFacing` 翻转反面法线；因此“重复反向三角面以开启双面绘制”的假设不成立，本轮未改生产代码或添加补丁。
- 此前及本轮桌面浏览器实际观察 3D 播放 frame0→3、位置+15%跨帧保持；测试后已恢复自动垂向166.4×、仰角34°、frame3、位置+15%，运行状态 idle。黑片根因与修复均未确认。临时诊断面板不存在；桌面服务提供的 `viz3d.js` HTTP 200 响应 SHA-256 与磁盘源码一致（`4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`）。

### 2026-10-24 Sol：Bryrup 当前 WET/GOTM 隔离集成烟测

- 从当前仓库 `3DWET/src/gotm` 与 `3DWET/src/wet` 新建隔离 GOTM 构建；确认 FABM 注册器含 `wet` 工厂，WET `fish.F90` 与 factory 对象成功编译。GNU Fortran 16.2 下先遇到 GOTM 三个 `restart_*` 变量 namelist 声明顺序错误，以及 settings 对 `report_error` 的调用方式与 YAML 当前绑定接口不匹配。两处最小兼容调整仅施加于 `build/bryrup-current-source-candidate-20261024/gotm-source-copy` 候选副本；正式源树、正式案例与生产 EXE 均未改。隔离 runner 构建成功，候选 `gotm.exe` SHA-256 `69A13783D258F7F94799CBC73559BD730D097993A10FEB21B5CC76EBDC8541C1`。
- 在官方 Bryrup 案例隔离副本中仅将停止时间缩短至1990-01-02；其它官方输入哈希均匹配源案例。实际启动读取9m/18层配置，`wet/fish` 初始化成功；随后在首个积分前因案例参数 `BENpref1` 不属于当前 fish 模块参数而停止（return code 1）。日志 `build/bryrup-current-source-candidate-20261024/bryrup-one-day-smoke/smoke-attempt02.log` SHA-256 `BB0BDCDC16A0202D5D40714DD6B194061C1FBB5FE34E70C7EE7E82769033F6F8`。未擅自映射或补造生态参数。
- 状态：当前源码的 `wet/fish` 注册与模块初始化已通过隔离工程检查；Bryrup 首步积分烟测与论文科学机制复现仍未完成。桌面工作台和正式案例不受本次隔离构建影响，无应用同步操作。

### 2026-10-24 Sol：Erken A 床面黑片垂向阈值复验与服务版本复核

- 在桌面应用当前 Erken A 3D 温度视图（frame 3，仰角34°，位置+15%，连续水体网格）实际切换垂向放大：50×截图中未见明显黑片；100×时床面下缘出现黑色片状面；恢复自动166.4×后黑片明显复现。此为同一帧的浏览器渲染对照，支持“高垂向夸张相关”，不单独证明深度缓冲或GPU精度是根因。完成后恢复自动比例，帧/相机/位置未改。
- 截图中床面黑片仍可见；控制面板当前模型位置+15%、仰角34°、自动166.4×、frame3，run状态空闲。床面顶点顺序由源几何核对为每湿格四角按固定一致顺序拆为两三角面，代码已设置 ambient=1、diffuse=0；这些静态检查不证明每一GPU面实际法线，故黑面原因仍未确认，未作生产补丁。
- 本地首页本轮实际引用 `viz3d.js?v=102`，服务 HTTP 200；磁盘源码与服务响应 SHA-256 均为 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`。服务 health ready=true、PID44964；模型状态 idle，活动目录为 Erken A attempt03 arm A；诊断面板未显示。仅做浏览器与只读版本核对，没有代码或案例输入更改，无需桌面应用重启。

### 2026-10-24 Sol：Bryrup 仓库内 OBM 配套案例隔离烟测

- 除前述 `lake_bryrup_denmark` 配置在模块初始化前因未知参数 `BENpref1` 停止外，本轮也检查仓库随 WET 提供的 `3DWET/src/wet/testcases/lake_bryrup_obm`。其 README 描述 Chen et al. (2020) 的 Bryrup 年循环气象/营养盐强迫，并说明 WET 0.2.0 或更新版本及 OBM 试验用途；但未在此目录给出强迫数据的原始观测出处，因此这里分类为“仓库提供的案例强迫，逐项实测来源待补充”，不能称为实测验证。
- 在 `build/bryrup-current-source-candidate-20261024/bryrup-obm-one-day` 做完整隔离副本，仅把停止时间从2075-01-01改为1990-01-02；其余16个输入文件与仓库测试目录哈希无差异。用当前源码构建的 candidate GOTM runner 启动后读入25层/9m以及1990-01-01至1990-01-02的24步计划，首个 fish 实例初始化前因 `cDayAgeFish` 不是当前 `wet/fish` 可识别参数而停止，return code 1。日志 SHA-256 `9283520A6225AA287003D0FF5FE36E07A5E452ABE3158104073EA89D667DCD2F`。
- 两份仓库 Bryrup 配置分别出现当前源码不接受的 `BENpref1` 和 `cDayAgeFish`；仅为通过初始化而把这些名称猜改成当前参数，会改变或不明其生物学含义，故未这样做。当前证据确认 runner 构建成功，不能确认 Bryrup 任一配置通过首步积分；工程烟测与科学复现仍未完成。运行仅作用于 `build/` 下案例副本，未改正式源树/案例/生产 EXE；未改产品代码，无桌面应用重启。

### 2026-10-24 Sol：官方 WET 1.0 + GOTM 5.4/STIM Bryrup 单日工程烟测

- 在隔离构建副本中以公开 GOTM master（5.4.0）、FABM master、WET 1.0 官方 archive 源（build/academic-case-validation-20261021/bryrup/wet-v1.0-upstream/wet-v1.0/src）和 GOTM 自带 STIM driver 配置并串行构建。GNU Fortran 16.2 下仅在 GOTM source-copy 的 gotm.F90 移动三个 restart_* 声明到 /model_setup/ namelist 之前；正式 GOTM 源码、WET archive、生产 EXE 未改。CMake 配置和构建返回码均为0，编译了官方 WET fish.F90、macrophytes.F90 与 GOTM gotm_stim.F90，493/493 步链接成功。候选 exe SHA-256：6DD641E5EBE20A581F2848ABAAD0746E34231A78139130D5588D287D1D4E6BD4。隔离日志：build/bryrup-current-source-candidate-20261024/gotm-au-master-wet1-stim/。
- 使用归档内 lake_bryrup_denmark 案例的全新副本。除缩短 gotm.yaml 停止时间至1990-01-02，以及将整数字段 qTrans: 3.0 改写为数值等价的 qTrans: 3 外，剩余6个案例文件的 SHA-256 与归档相同；原有 surface/ice 配置保留。未经改写的第一轮启动成功初始化 STIM 与三种鱼类实例，随后因 qTrans 类型拼写停止；数值不变的格式调整后重新启动。
- 第二轮实际运行返回码0：GOTM读入18层/9m湖深、1990-01-01 12:00至1990-01-02 12:00、24个小时步；WET1鱼类、浮游植物、浮游动物、底栖和水体模块均初始化成功，STIM冰变量注册成功，模型完成运行并正常清理。生成 output.nc（286变量、time维度2），逐变量检查286个数值变量未发现 NaN/Inf；示例温度范围3.6243–4°C，AdFish_sD约0.9785–1、JuFish_sD约0.2445–0.25、PiscFish_sD约0.06853–0.07、cyanobacteria_sDW约0.0543–0.1164。日志 SHA-256：B538C0ABA29F81D2398AC0A09A84A15EDC1CB2971538BCF3FC0BEDDA9F1F6EF8。
- 分类边界：这是以仓库归档强迫与官方 WET 1.0 参数做的一日工程烟测；本地 README 未能追溯逐项强迫至原始观测，故不称“实测验证”。它不是原论文指定 GOTM 5.2.2-au 栈、未跑完整1990–1995案例、未做校准/独立验证，不能声称科学复现或用于案例性能结论。此前当前仓库 WET 源配置仍因 BENpref1、cDayAgeFish 不兼容而失败；不可把该结果归为当前 WET 源已通过 Bryrup。
- 本轮没有产品代码修改，桌面应用无需因本烟测重启。实查桌面应用 53864 端口 health ready=true、PID44964、run idle；首页引用 viz3d.js?v=102（HTTP200），服务脚本与磁盘 SHA-256 均为 4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2。8766端口拒绝连接。
### 2026-10-24 Sol：attempt55 合成湖用户流程与2D播放浏览器验收

- 工作目录 `build/full-workflow-20261025-attempt55`，seed `2026102501`。使用仓库脚本生成的随机湖形状/强迫输入（合成代理数据，不是观测案例）；六个后端阶段 external/features/results/scipy/abc/restart 均通过，实际模型 `getm_cartesian.exe` 完成600步，并生成20个输出时次。
- 在隔离的浏览器工作台实例 `http://127.0.0.1:54001/` 中从导入的 Imported Random Lake 进入模型配置，检查食性网络，再用同功能群等总量分摊把已配置 `greens` 拆分50%为 `greens_flow_acceptance`，运行模型并查看结果。运行后配置/网络刷新显示21个FABM实例、398个显式耦合端口、17条已解析猎物引用；新增实例没有自动加食性关系。不得将该克隆称为不同物种或新增食性关系。
- 模型运行由浏览器真实启动并完成600/600步；结果检查通过。NetCDF `output.nc` 有20个时间步、932个变量；新增 `greens_flow_acceptance_sDW` 在18960个样本均有限，空间/垂向全域均值从首时次0.03999691变化到末时次0.03993829 gDW/m3。浏览器实际查看3D变量、提取该变量时间序列并出现图形；3D播放观察到帧10→15→19推进，+25%模型上下位置跨帧保持。
- 2D中把输出步设为0并实际播放至19：20/20帧成功，目标/实测1/1.0 fps，整帧时间5 ms（P50/P95均5 ms），绘制超预算0/20、帧间隔超目标10%为0；终态20/20输出帧画面可见。故当前这份合成运行结果的2D全序列与3D播放/位置保持都在浏览器中观察通过。
- 本次服务 `/api/system/health` 返回HTTP200、ready=true，model_root指向attempt55隔离副本。服务实际返回 `playback_performance.js` SHA-256与源码相同：`25c08198633df8ad527ab07a8905f6e3d07ab248c9b4fb129ee8731400dc7a29`。本轮未修改产品代码；因此未触发桌面应用重启要求。该隔离浏览器实例证明当前源码已被加载，不等价于重新同步原桌面窗口。
- attempt55仍保留 `awaiting_ui`：计划要求的10项完整UI清单尚未逐项完成；ledger连续完整轮数仍为0/5。故本次只记录完成的导入→配置/添加藻类→运行→2D/3D结果查看→时间序列分析子流程，不宣称全清单或五轮验收通过。没有证据显示本次合成数据是实测案例，也没有对生物学真实性做判断。
- 另用 `workflow_acceptance.source_version(Path(...))` 重新计算当前源码/求解器版本，得到 `3eb440ec48f58e226561dac6108ac9e14fbb3fd0d71e003070f45b1e34909138`，与 attempt55 `round.json` 完全一致，证明此次 UI 操作对应其开始时锁定的源码版本。

### 2026-10-24 Sol：Erken June solver 对照完成态与 C 重跑目录复核

- 复查 `build/erken-production-compare-20261024/matched_compare_status.json`、实际 NetCDF 文件及逐变量比较结果。候选版与生产版在相同的 legacy meteorological-flux arm A 输入上都完成120960步；两侧输入37个文件哈希一致。该对照为兼容性检查，测试输入明确移除了生产求解器不接受的 `use_measured_swr=true`，因此不验证 direct-measured-SWR 模式。两份 `output.nc` 均168帧、864变量，文件 SHA-256 同为 `784b37d30e0b99ed83838369fba2a9c8bddffc1d427937b93ad36c3758d7788e`。逐变量结果864/864数值变量精确相等、缺变量0、形状差0、属性差0。生产 EXE hash `902a7db6…56df672`，候选 hash `6ac027fe…18f4344`。结论限于该输入/模式，非 direct-SWR 验收或科学验证。
- 对 attempt03 的 A/B/C direct-SWR 机制敏感性运行分别核对最终输出：A、B 位于 `arms_168h_direct_swr_padding_verified/arm_A|B/case/`；A、B 日志有完成标记，输出均168帧（3600–604800s），864与944变量。C 的 `arms_168h_direct_swr_padding_verified/arm_C/case/` 实际为原中断部分，只有31帧且没有完成标记；**C的有效完成结果在 `arm_C_rerun_20261023/case/`**。该重跑状态 return code 0、完成标记 true、fatal/EOF false，验证报告 `valid=true`；`output.nc`、`.2d.nc`、`.3d.nc` 都是168帧，验证的有效数值无非有限值，2D/3D输出时间轴完整。
- 发现并修正了 `ATTEMPT03.md` 的目录指向：原文将 C 完成结果误指向31帧的中断目录，现已明确以 `arm_C_rerun_20261023/case/` 为 C 的最终结果路径，保留中断目录但标为不可用完成结果。当前重算的 A/B/C 初末湿样本均值与文档描述一致：合并蓝藻 A 0.298634→0.455507、B 0.298635→0.455552、C 0.298635→0.442999 gDW/m3；这只是模型输出描述，不代表观测拟合、竞争机理证明或生态真实性。
- Erken forcing 分类仍为混合：SITES 实测气象中的入射短波及温度剖面保留，最后一条 forcing 边界保持值是计算垫片、不是观测；`tcc=0.5` 固定云量代理、蒸发为0、无河流流量、单站气象广播，以及多数生态/营养盐初态代理/默认值。故这两组成功运行分别是生产版兼容性对照和候选版机制敏感性运行，不得合并表述为实测验证。
- 本轮仅修正审计文档并核查隔离结果，没有改产品代码或活动案例；桌面应用无代码同步/重启动作。计划要求的10项UI清单、direct-SWR生产模式和Erken科学验证仍未完成。


### 2026-10-24 Sol：attempt55 合成湖完整子流程与3D浏览器实播

- 在隔离工作台 `http://127.0.0.1:54002/` 对 `Imported Random Lake` 实际操作。数据为工作流生成的合成随机湖与合成强迫，不是观测案例。先通过案例管理载入案例，再在浏览器启动 600/600 步模型；运行日志记录 158 个计算格、6层，输出有效性检查通过。然后进入 3D 结果页查看温度和湖盆。
- 3D播放器由第0帧实际播放至第2帧并自动停止：页面性能读数为目标1 fps、实际1.0 fps、成功帧3、超预算0/3、帧间隔超目标10%为0。之后把模型上下位置从0调到+25%，浏览器画面可见模型上移；跨帧从第2帧切至第1帧后控件仍为+25%。斜视仰角34°保留。该验收覆盖本合成结果的3D播放器和独立上下位置控制，不代替2D播放或其他数据规模验收。
- 继续完整用户主链路的后半段：从现有 `greens` 藻类实例经预览后克隆为 `greens_flow_sequence`，选择“同功能群等总量分摊”、新实例比例0.5。预览明确将12个注册状态按各50%分给原/新实例；参数与耦合完整复制。刷新后页面显示21个FABM实例、398个显式耦合端口、17条已解析食性引用，藻类实例由3增为4。克隆实例没有自动新增任何食性边，不能称作不同物种或新增关系。
- 添加后再次由浏览器启动模型，600/600步完成，用时约6秒，输出有效性检查通过。通过时间序列页选择 `greens_flow_sequence_sDW` 并提取全湖平均，页面实际出现曲线。对 `output/output.nc` 的独立读取确认3个时次、6层、12×22网格；新实例有68个输出变量；`greens_flow_sequence_sDW` 形状为(3,6,12,22)，2844个有限值，范围0.0394985–0.0401723 gDW/m³。
- 隔离服务器首页实际引用 `/static/js/viz3d.js?v=101` 与 `/static/js/app.js?v=63`；两个HTTP响应的SHA-256均与源码相符（viz3d `6ae595afb802d11ceaad57b9a915cf9afd3f74e4d8c81c3c4138e6dcbee6d9a5`；app `5b22a2cec263fffdeda351039b32895d5f3f9be70a03cad7b8eaaab9a0aa60ad`）。这证明本次隔离浏览器加载了当前源码。桌面常用端口8766和53864本轮探测超时，不能据此确认主桌面窗口正在加载；本轮没有产品代码改动，故未执行桌面重启/同步。页面与API证据来自隔离服务器54002。
- 本项浏览器流程在合成案例上走通“载入案例→运行→3D查看与调视角→增加藻类→再次运行→时间序列分析”。不代表外部观测导入、实测生态验证或全套10项/5轮UI验收已完成。未修改产品代码；本次案例改动限于 `build/full-workflow-20261025-attempt55/results/3DWET/case/Imported Random Lake`，运行前完整副本保存在同目录树的 `sequence-checkpoint-before-browser-run/Imported Random Lake`。

### 2026-10-24 Sol：原生 WebView2 桌面工作台同步核验

- 纠正前一条记录的端口判断：8766 是已退出的 headless 测试端口，53864 当前不可连接；本机桌面服务端口为8767。通过仓库 `launch_desktop.cmd` 指定的 Python WebView2 启动模式实际启动桌面应用；进程树显示 WebView2 子进程挂在 Python 主窗体下，Windows 窗口标题为 `3DWET Studio`，窗口句柄2494786。应用日志记录桌面通知桥已连接 `http://127.0.0.1:8767`。
- 8767 `/api/system/health` 返回 `ready=true`，server PID46392，model_root 为 `build/real-use-validation-20261022/erken-external-data-real-grid/ui-model-root`。从桌面窗口绑定的服务读取 `/static/js/viz3d.js?v=79` 与 `/static/js/app.js?v=59`，各自 SHA-256 与工作区源码一致（viz3d `6ae595afb802d11ceaad57b9a915cf9afd3f74e4d8c81c3c4138e6dcbee6d9a5`；app `5b22a2cec263fffdeda351039b32895d5f3f9be70a03cad7b8eaaab9a0aa60ad`）。启动后再检查时，桌面窗口仍运行且服务仍 ready。
- 本轮没有产品代码改动；该核验通过正式桌面启动器打开当前源码并验证 WebView2 窗口所连接的现有本地服务。8766/53864 的超时不代表桌面工作台未运行，后续以8767和桌面窗口进程为准。

### 2026-10-24 Sol：本轮浏览器播放复验、缓存回归用例与桌面版本核对

- 桌面浏览器实际打开当前 Erken A 三维结果页，设置模型上下位置+15%并以4 fps播放。观察帧号持续前进；性能面板到成功帧59时显示目标/实际4/4.0 fps、整帧约52 ms、P50/P95 51/60 ms、绘制超预算0/59、帧间隔超目标10%为0；跨帧后垂向位置仍为+15%。本次复验没有证明长时间或全范围播放表现，既有 A/B/C 全范围记录见前文。本轮结束将页面恢复为frame0、位置0%、1 fps、暂停。
- 修正 `tests/test_results_inventory_cache.py` 中缓存测试夹具和接口断言后，独立执行缓存、候选结果查找、伴随输出、输出选择四组用例：11 passed。此改动仅在测试文件，没有改产品源码。
- 桌面服务 `http://127.0.0.1:59302` health 为 ready=true、PID 69596、model_root 指向本仓库 `3DWET`。首页引用 `/static/js/viz3d.js?v=101`；服务响应与本地源码 SHA-256 同为 `6AE595AFB802D11CEAAD57B9A915CF9AFD3F74E4D8C81C3C4138E6DCBEE6D9A5`。因为产品源码没有改动，无需重启桌面应用；确认应用当前加载源码一致。
- 床面黑片仍待修复。历史同帧浏览器对照表明黑片附着湖盆床面 trace，随垂向夸张/视角而变化，并在关闭床面 trace 时消失；现有证据不能区分网格颜色/着色、几何精度或GPU绘制因素。没有新增生产补丁。参考图位置仍待补充；完整导入流程与四个湖泊案例的实测科学验证仍未全部完成，具体代理/失败分类见各案例记录。

### 2026-10-24 Sol：Erken A 原始与中心化 XY 浏览器 A/B

- 当前源码临时诊断模式下，在实际桌面服务 `http://127.0.0.1:8768/` 对 Erken A 同一 frame 3、层 9、温度视图、垂向放大 166.4×、镜头仰角 34°、位置 0% 做对照。`raw-xy` 保留投影坐标；`center-xy` 将所有湖区 trace 的 X/Y 与轴范围平移到湖盆中心，Z、强度、索引、相机不变。页面状态分别确认了模式；中心模式显示偏移 X=699863.988 m、Y=6639646.553 m；服务返回诊断 JS 与本地当前源哈希一致。
- 两种模式画面均复现同样明显的黑色床面片。因此“大坐标绝对值本身”不足以解释本次现象；不能排除其他精度交互，也不能据此确定唯一根因。结合既有隔离（纯色覆盖会改变多数黑片、统一 facecolor 无效、几何无退化/绕序异常、缺陷与高垂向夸张相关），候选仍包括渲染着色路径、几何遮挡/深度精度与二者交互，均未定论。
- 本次页面与案例帧浏览器实测；不构成修复，不构成四案例科学验证。临时诊断代码将在 A/B 后移除并同步桌面源。

## Sol 判断汇总：黑色床面片的已证关系与候选根因（不代表根因定论）

| 变量 | 已有浏览器对照现象 | 可确认程度 |
|---|---|---|
| 湖底图层 | 测试时禁用湖底 mesh 后黑片消失；关闭岸陆示意后黑片仍可见。说明黑片依赖湖底 trace 的绘制，但不等于已定位 trace 内部哪个属性或 GPU 路径。 | 实测：关联床面 trace；根因不确定 |
| 视角 | 镜头/视角变化时黑片显隐或面积变化。 | 实测：呈视角相关；遮挡、深度精度、着色等解释仍不确定 |
| 垂向倍率 | 1×不明显，50×未见明显黑片；100×床面下缘出现片状黑面；166.4×/200×附近明显复现。 | 实测：高垂向倍率相关；不证明深度缓冲或 GPU 精度是唯一原因 |
| 投影 XY 绝对量级 | 在临时诊断路径（强制恢复高 VE 床面填色、隐藏墙体迹线）下，Erken A 同帧/层/相机/VE 保留原 XY 或平移至局部中心都出现黑片。该模式不是默认渲染路径。 | 实测：坐标绝对量级本身不足以解释这次诊断路径对照；不能外推为默认路径根因结论，也不排除更广义精度交互 |
| 床面颜色/着色 | 禁用强度映射并指定纯色曾使多数黑区变色但仍留少量暗片；uniform intensity、预映射颜色和 facecolor 对照没有明显消除。 | 实测：颜色/着色路径参与表象；具体 Plotly/WebGL 字段或状态不确定 |
| 网格有效性 | 读回的 1504 床面顶点/752 三角形均有限，索引在界内、无零面积面，法向 Z 为正；源几何采样未见退化/反向绕序。 | 实测：已检查这些几何异常未出现；不能覆盖 GPU 深度/运行时状态 |

候选（均未证实为唯一根因）：床面 trace 的运行时着色/顶点属性差异；高 VE 与镜头变化下的面遮挡或深度精度；Plotly/WebGL 状态与几何/材质的交互。区分它们需先在默认正式渲染路径中、相同案例/帧/相机重现黑片，再单变量切换颜色来源、法线/材质、z-range/相机裁剪，并同步记录 trace 输入、Plotly `_fullData`、WebGL 绘制参数与截图。只在诊断模式覆盖材质或强制绘制所得结果不能替代默认路径的缺陷复现；目前确认默认高 VE 温度图会隐藏床面填色，这是规避而非根因修复。

状态：**未修复**。根因目前**不确定**。参考图：`（待补充：参考图的具体路径或链接）`。


### 2026-10-24 Sol：恢复正常桌面服务后核对高 VE 默认视图

- 在新载入的 8768 工作台标签页实际进入 3D，默认水温变量 frame0 的页面读数为 VE=166.5×，相机斜视34°。状态文案明确为“高垂向放大（>80×）：湖底填色已隐藏，等深线保留；异常成因尚未确认”；主图中床面填色未绘制。此为当前正式渲染路径的规避行为，不证明原黑色床面片根因已修复。
- 同一服务提供的 `viz3d.js?v=102` 哈希与移除临时模式后的本地源码一致（`FAA6DEE90EA4A929C68856BC5766527EF0A6DDAE6CC761E241B6ADC24C5E0609`）。此项仅确认隔离浏览器新页加载了当前脚本，不等同于原生 WebView 的交互式刷新确认。

### 2026-10-24 Sol：默认渲染路径 50×/自动比例复核

- 在新的 8768 页面（清洁加载当前服务脚本）进入 Erken A 水温 3D，frame0、斜视34°、模型位置0%。默认自动比例166.5×时，状态提示床面填色隐藏。用正常“垂向放大”控件选50×后，状态与图例显示真实湖底“湖盆水深” trace，完整湖形在截图中可见；此次画面未见明显黑色床面片。再用控件恢复自动166.5×，页面恢复为隐藏湖底填色。此项显示当前默认路径在50×与自动比例的行为，不推翻历史缺陷截图，也不能视作床面缺陷已修复。
- 本次未切换案例/求解器配置、未运行模型、未改结果文件。UI比例和帧恢复默认后继续使用。

### 2026-10-24 Sol/Luna：本轮集成状态

- **黑色床面片：未修复，根因不确定。** Luna 在当前 Erken A 正常渲染路径复核水温 50×、自动 166.5×及“水面显示所选变量”关闭后的静态湖盆地形路径；这些本轮检查未见明显黑片。自动 166.5×温度视图仍因现有规避逻辑隐藏床面填色。该组未复现结果是限定条件下的浏览器实测，不能推翻历史复现，也不能作为修复证据。候选根因与区分性验证仍按上方表格执行。
- **食性网络 UI：实测交互检查通过；模型运行时/科学验证未完成。** Luna 在 `ecology_network.js` 增加“编辑食性关系”快捷入口，使视图切到食性配置分层图并滚动、聚焦关系编辑器，同时遵循 reduced-motion 偏好。Sol 在浏览器选择 JuFish 后确认快捷入口可聚焦编辑区，PLAN/BEN/PISC 分组和当前 prey 关系可见；没有保存或更改案例输入。聚焦当前案例实例、保留已有端口/参数，并由模型端预览验证，改善了关系编辑入口；这不验证原生 FABM 注册状态、摄食运行或科学合理性。
- **UI 方向与实现：已落实到当前源码；原生窗口版本已同步。** 推荐的浅色科学工作台、分组导航、中心结果画布、上下文编辑区与明确科学状态已记录于 [2026-10-24-scientific-workbench-ui-design.md](../../superpowers/specs/2026-10-24-scientific-workbench-ui-design.md)。浏览器检查中当前 8768 工作台显示该布局，食性快捷操作也已加载。新启动的原生 8772 窗口标题为“3DWET Studio”，health ready、run idle；HTML 引用 `ecology_network.js?v=25`，服务脚本与本地源 SHA-256 均为 `1D8E0C10CE7A4EB264412BE104EAE981010C211BDDBE2DAF173CEE757D854C65`。该桌面实例的 `model_root` 是 `build/desktop-sync-v103`，源码由当前仓库启动器提供；完整原生 WebView 页面交互仍未单独执行。
- **实现检查：** Luna 运行 `node 3DWET/tests/test_ecology_foodweb_ui.js`（通过：食性编辑 DOM 行为、分层证据视图），以及 `node --check 3DWET/app/static/js/ecology_network.js`（通过）。Sol 在 8768 实际浏览器操作验证食性入口及 JuFish 关系编辑器可达。此 UI 检查不等于完整用户流程验收。
- **完整流程与案例：仍未全部完成。** attempt55 合成湖只覆盖导入→配置/加藻→运行→2D/3D结果查看→时间序列子流程；十项完整 UI 清单仍为 0/10，连续完整轮数 0/5（状态：**未完成**；合成输入与运行属于**代理**）。Erken 科学验证仍**未完成**（已有实测渲染/兼容性与代理配置/强迫，不可合并为实测科学验证）；Lake Ravn 官方 1D rerun 仅为**代理**，科学验证**未完成**；Bryrup 官方 WET 1.0 + GOTM 5.4/STIM 单日工程烟测为**代理**，原仓库配置及科学验证**未完成**；Arreskov 因缺少案例配置文件、运行失败，科学验证**未完成**。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：attempt56 与逐项流程/案例验收补记

- attempt56（`build/full-workflow-20261024-attempt56`，seed `2026102401`）合成湖后端 external、features、results、scipy、abc、restart 六阶段均 `passed=true`；隔离账本 `consecutive_complete=0`，状态仍为 `awaiting_ui`。输入为合成代理，不能作为任一指定湖泊的科学验证。十项 UI 清单没有本轮同源指纹的审核报告，故完整用户流程仍**未完成**。
- 十项 UI 当前可审状态：1 导入/网格保存**部分实测**（仅历史局部证据）；2 参数/初值保存重载**未完成**；3 模块/食性网络/湖点位**部分实测**（网络可达及本轮食性编辑器聚焦实测，不覆盖完整保存重载）；4 诊断/导航/修复/重跑**未完成**；5 所有结果模式**部分实测**（历史 dashboard、2D/3D、时间序列局部）；6 UI 观测导入/比较/校准**未完成**（attempt56 仅后端 SciPy/ABC 阶段通过）；7 重复结果清理恢复**未完成**；8 语言切换持久化**未完成**；9 Ctrl 缩放/窗口调整/平移/全屏/导出组合**未完成**（仅历史相机局部）；10 ETA/完成/失败通知**未完成**。不得将这些旧版局部证据合计为一次完整通过。
- Erken：SITES 导入/浏览器结果等既有环节为**实测**；attempt03 168小时候选配置和默认生态初态/部分强迫属于**代理或未完成**。科学验证**未完成**。Lake Ravn：官方 Aarhus GOTM/WET 单柱配观测复跑为**代理**；单参数优化18次触顶且 `success=false`，不是收敛率定；GETM 3D 产品流程和科学验证**未完成**。Bryrup：当前仓库配置分别因未知 `BENpref1`、`cDayAgeFish` 在积分前失败；独立官方 WET1.0/GOTM5.4/STIM 24步为工程**代理**，不是指定论文复现；科学验证**未完成**。Arreskov：缺案例专属 `fabm.yaml`，启动在积分前失败；无模型输出，状态**未完成**。不得把代理烟测称实测验证。
- 本轮最后只读确认原生桌面服务 `http://127.0.0.1:8772/api/system/health` 返回 ready=true、PID 8604、model_root=`build/desktop-sync-v103`。该进程由当前仓库 launcher 启动，HTML 使用本轮 ecology_network v25，served/source SHA-256 一致；但原生 WebView 内十项 UI 流程尚未实际操作验收。8768 浏览器仍为 ready/PID72664、run idle、活动案例 Erken A attempt03；没有更改正式案例或运行状态。

### 2026-10-24 Sol：当前源码 Erken A 黑色床面限定复查

- 8768 当前浏览器页显示 Erken A 3D `temp`，活动尝试 attempt03 arm_A、run idle；页面 `viz3d.js?v=102` 与已记录服务版本一致。当前页仅调整显示参数，未保存案例或运行模型。
- frame 19、镜头仰角34°、模型位置+15%、连续水体网格下，静态 bathymetry 路径（关闭所选变量叠层）在垂向200×绘出青蓝到蓝色床面及中性灰陆地区域；浏览器画面未见明显黑色床面片。随后恢复所选变量叠层并在50×查看同一帧，画面也未见明显黑片。高倍率默认温度叠层提示会隐藏床面填色，因此不能用它判断填色缺陷是否存在。
- 本次未复现是限定条件的当前版浏览器实测，不能推翻 frame3 / 100×与自动166.4×历史复现，更不是修复证据。候选仍包括床面、岸陆/墙面相互遮挡、颜色/深度插值、垂向跨度与视角相关的渲染交互；根因**不确定**。下一步需要当前版本同一帧默认路径可重复黑片的截图，并同步固定 view/VE/overlay 与 Plotly 实际 floor/wall/land trace 数据，才可构造有针对性的失败回归并区分候选。
- 原生桌面健康端点只读返回 ready=true、PID8604、model_root=`build/desktop-sync-v103`。本轮没有产品代码更改，故不需热重载/重启；原生 WebView 的完整流程仍未验收。

### 2026-10-24 Sol：Erken A frame3 当前版动态/静态床面复查

- 在当前 8768 实例重新打开 3D 页，加载当前运行结果：frame3 为 2024-DOY165 17:00，网格18×44、376个有效水域单元；run idle。对照统一仰角34°、位置+15%、连续水体网格，先以自动垂向166.4×（变量叠层提示床面填色已隐藏）观察，再在frame3、50×启用温度叠层。放大画布检查时水体温度色面、岸线与剖面指示可见，未发现明显黑色床面片。
- 该当前版动态50×检查为限定条件的浏览器**实测**，不推翻历史frame3在100×/自动比例下床面黑片的**实测**记录。100×动态路径按当前保护逻辑隐藏床面填色；关闭变量叠层后切到静态 bathymetry、100×、34°时，湖底是青蓝色面，灰绿色区域为无高程数据的陆地示意，画面未见明显黑片。保护逻辑与静态地形截图均不能证明黑片已修复。
- 当前回归复现仍未建立，因此本轮仍未新增测试或生产修复。根因**不确定**；候选包含床面/墙面/陆地的深度遮挡、顶点颜色/插值和垂向Z跨度与视角/深度缓冲交互。需要在当前版本复现同一默认路径黑片时同时采集截图及实际floor/wall/land运行时 trace attributes/coords，才能把回归测试对应到具体假设。
- 用户确认目前暂无当前版本复现截图；参考图位置稍后补充，当前仍保留 `（待补充：参考图的具体路径或链接）`。上述仅改文档，8768/8772应用源码未变，无需重启同步。
- Luna 对当前树与 Git 历史复核：当前床面抑制代码属于未提交工作树，`git blame` 显示为 `Not Committed Yet`；仅有的2026-09-28提交仍是没有 `lakeTraces` 的早期版本，故无法从提交历史确认这段规避逻辑何时、因何加入。最早可检索到的文字记录是本审计文件2026-10-24条目，写明高倍率抑制用于规避已观察到的黑片、成因未确认。这里是来源缺失结论，不代表代码是本轮新增或已修复。

### 2026-10-24 Sol：v102 桌面同步与强制床面诊断补记

- Luna 加入了仅由 URL 显式启用的 `viz3d-diagnostic=force-bed`、`skip-wall`、`skip-field` 调试开关，默认渲染路径未因该开关改变；并更新了 `viz3d.js` 缓存版本至 v102。Luna 报告 `node --test tests/viz3d_bathymetry_surface.test.cjs` 8/8 通过、`node --check 3DWET/app/static/js/viz3d.js` 通过；Sol 本轮未独立重跑此单测。
- 已正常关闭旧的空闲原生 WebView，并经仓库启动脚本重新打开；关闭重复启动的第二个原生窗口，保留一个。保留窗口可访问新版工作台布局，浏览器可访问的局部状态包含 3D 面板、工作流侧栏、结果图和时间控件。8768 HTTP health `ready=true`、run `idle`；首页引用 `/static/js/viz3d.js?v=102`，服务 JS 与工作区源 SHA-256 相同（`2ABD2052C56374D35883EBEACB3C21252590FB187C8F2ED51B41BC975455A0E5`）。这确认服务/当前桌面页面使用新源码，不等于完成完整工作流验收。
- 为隔离床面 trace，在 8768 `case` 标签、44×18 网格、frame 0、仰角34°、自动 VE=166.5×画面，通过诊断 URL 同时启用 `force-bed,skip-wall,skip-field`。Plotly 可访问树出现“湖盆水深”床面 trace，截图仍见黑白异常斑块。此为诊断模式人为恢复原默认高倍率下被抑制的动态床面，且活动案例身份未核实为指定 Erken；它既不是默认用户路径复现，也不是产品修复证据。三个跳过选项同时启用，现有截图不能进一步区分床面坐标/三角拓扑、插值/着色或 Z 跨度与视角的交互。黑片缺陷状态维持**未修复**，唯一根因仍**不确定**。
- 页面已离开临时诊断 URL；参考图路径继续保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：隔离合成案例结果页局部续验

- 在临时隔离服务 `http://127.0.0.1:8773/` 加载 `Imported Random Lake`，其数据由 attempt59 生成且为合成代理数据。服务 health `ready=true`，`model_root` 指向 `build/full-workflow-20261024-attempt59/ui-model-root`；该副本不是四个指定湖泊之一，以下状态均为**代理**。
- 2D 水温结果页面实际播放，帧位置从0推进至19，输出范围为0–19；状态栏显示20个输出时次。该操作只确认合成数据上2D播放到末帧，不覆盖完整 UI 验收清单或正式湖泊验证。
- 垂向热图页面对水温成功执行“生成垂向热图”；页面显示采样20点、垂向层数6、sigma坐标与结果色标。时间序列页面成功执行“提取”，并出现时间轴图表控件。之前已进入同一隔离案例3D结果页；本条是2D末帧、垂向热图与时间序列的新增浏览器局部观察。
- 本轮续看地图视图：页面显示 20×14 网格中162个水格的水深范围0–9.02 m，并呈现底图联网提示。率定分析页成功打开，并可见CSV/XLSX上传、官方观测文件选择/显式变量单位映射、预览质量诊断及只读GOTM水柱比较入口；本轮未选择/应用观测文件、未执行比较或率定。因此这些是页面可达性**代理**观察，不是观测对照或科学验证。
- 本次不改变 attempt59 原先因十项当前版本 UI 清单未完成而记录的 failed 状态，不据局部页面观察补记完整流程通过。其余 UI 清单（保存/重载、率定观测、重复结果恢复、语言持久化、缩放/窗口/导出组合、ETA/失败通知等）仍**未完成**；连续完整轮数仍为0/5。Erken、Lake Ravn、Bryrup、Arreskov 科学验证分类不变。
- 临时服务通过 API health 核对为 ready；8768 正式浏览器/桌面服务也为 ready，run idle、model_root 指向仓库 `3DWET`。没有产品源码更改；本条仅记录局部 UI 观察，无须桌面热重载。关闭/进程回收状态仍需在交付前检查。

### 2026-10-24 Sol：床面测试独立复跑与桌面同步差异核对

- 在当前工作树重新运行 `node --test tests/viz3d_bathymetry_surface.test.cjs`：10/10 通过。覆盖内容包括诊断查询过滤、显式 `force-bed`/`skip-wall`/`skip-field` 组合、静态 bathymetry 几何/着色属性与网格线叠层。该套件没有复现已报告的默认用户路径黑片，也没有 Plotly/WebGL 浏览器像素级断言；故它只验证实现契约，不代表黑片修复。
- 对照当前原生窗口/8768 服务发现多个隔离 3DWET 服务仍在运行，不能按单一端口批量重启。8768 `/api/run/status` 为 idle；其 HTML 仍引用 `ecology_network.js?v=24` / `studio.css?v=4`，工作区模板分别是 v26/v5。两个旧 query URL 返回的 JS/CSS 字节哈希分别与当前本地源一致。旧 HTML 查询版本与运行时模板状态的差异保留为**未解释**；未终止其他运行实例。
- 本轮未修改产品源码。床面片仍**未修复**、根因**不确定**；当前验证仍需默认路径可重复复现与对应 trace/相机/VE 快照。完整流程与四案科学验证状态不变，均按上方案例条目标注。

### 2026-10-24 Sol：Bryrup / Arreskov 官方 WET 配置来源复核

- **实测（来源/文件清单核验，不是模型科学验证）**：官方 Zenodo WET v0.1.0 记录 `10.5281/zenodo.4903142` 提供 `wet-v0.1.0.zip`；下载包 MD5 与记录相符（`8b16645d6625863ce6d8d8416195aa37`）。归档含 `testcases/lake_bryrup_denmark/fabm.yaml`，但未包含 Arreskov 目录或其 `fabm.yaml`。可追溯来源：[Zenodo WET v0.1.0](https://zenodo.org/records/4903142)。
- **实测（来源/文件清单核验，不是模型科学验证）**：当前公开 WET v2.3 GitLab 树中 `testcases/lake_arreskov_denmark` 有 README、GOTM、forcing、manipulations 和 output 文件，但无 `fabm.yaml`；目录：[官方 GitLab v2.3 Arreskov testcase](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tree/v2.3/testcases/lake_arreskov_denmark)。论文写明 Arreskov 配置包含在 WET repository testcase 中：[Andersen et al. (2022), paper PDF](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf)。这与当前可取得的发行包/公开目录清单不一致；缺失的原始生态配置仍**未完成**，不能以推测补造。
- **实测（源代码兼容性比较，不是模型科学验证）**：同一 WET v0.1.0 归档的 `src/fish.F90` 与当前保留的 `src/fish_pclake.F90` 都有46个 `get_parameter` 名称且集合完全相同；比较行序相似率98.91%。当前 `wet_model_library.F90` 将旧模块保留为 `fish_pclake`。Bryrup 配置里的三组 `wet/fish` 实例包含 `BENpref1`、`cDayAgeFish` 等旧参数名，因此只在隔离副本里把模型标识映射到对应兼容模块，是可验证的候选工程适配；尚未验证输出是否符合原论文。
- Luna 正在 `build/` 新隔离目录测试该三处模块标识映射，原始案例配置保持不变。任何短跑/初始化成功均只记为**代理工程烟测**；Bryrup 科学验证维持**未完成**，Arreskov 仍**未完成**。

### 2026-10-24 Sol：Bryrup v0.1 隔离启动兼容性烟测结果

- **代理（工程启动检查，非科学验证）**：Luna 在 `build/bryrup-v010-fish-pclake-20261024-luna01` 创建隔离副本。相对官方 WET v0.1.0 Bryrup 原始配置，仅 `fabm.yaml` 的三处 fish 模块标识（AdFish、JuFish、PiscFish）从 `wet/fish` 改为 `wet/fish_pclake`；其余7个输入文件 SHA-256 相同，`fabm.yaml` 仅3行变化。原始案例和产品源码未改。
- **代理（启动失败）**：使用候选 GOTM 二进制 `build/bryrup-current-source-candidate-20261024/gotm-smoke-build/gotm.exe`（SHA-256 `69A13783D258F7F94799CBC73559BD730D097993A10FEB21B5CC76EBDC8541C1`），从 `build/bryrup-v010-fish-pclake-20261024-luna01/smoke-24h` 执行，return code 1。日志 `build/bryrup-v010-fish-pclake-20261024-luna01/smoke-24h/smoke-run-smoke-build.log` 证实三个 `fish_pclake` 实例均初始化成功，随后因未修改的 `/instances/abiotic_sediment/parameters` 中 `cCPerDWS` 不识别而终止。24小时输出/耦合验证未发生。
- 按边界停止，不猜测或转换其余生态模块/参数。该候选只证明三处 fish 标识映射可初始化，不能证明整个案例可运行，更不是实测科学结果。Bryrup 科学验证状态仍**未完成**；需取得与当前 WET/FABM 实现兼容且可追溯的 abiotic_sediment 参数配置后，才能继续工程烟测和后续科学对照。Arreskov 原始生态配置仍**未完成**。
- 没有产品源码更改，因此本次不触发桌面同步/重启；产品服务此前记录的版本状态不由此烟测改变。

### 2026-10-24 Sol/Luna：黑片诊断对照可执行性复核

- **实测（服务状态）**：8768 `/api/system/health` 返回 ready=true，活动 model_root 为仓库 `3DWET`；`/api/run/status` 为 idle，case_directory 指向 Erken attempt03 的 arm_A 输出。此只证明服务可用和案例目录身份，不证明浏览器截图中的黑片状态。
- **代码复核（不是浏览器视觉实测）**：Luna 检查当前 `viz3d.js` trace 构造：`force-bed` 才会在高 VE 恢复动态床面；`skip-field` 只筛掉动态 field/missing trace；`bed-depth-colors` 必须与 `force-bed` 同时开启；`skip-bed` 移除床面 trace。VE>80 时墙体 trace 已由 `geometry.ve<=80` 条件排除，因此同一高 VE 状态下额外启用 `skip-wall` 是结构性 no-op，不能把先前同时启用的三个诊断选项解释为“墙体因素已单独排除”。
- 现有 `tests/viz3d_bathymetry_surface.test.cjs` 对合成输入覆盖 trace 选择/样式契约，但不运行真实 Plotly/WebGL 浏览器绘制，不能替代像素视觉对照。当前任务里的可操作桌面窗口未能提供稳定的窗口输入几何；未能复用浏览器标签取得同一状态的截图和 `_fullData`/运行时属性，因此本轮没有声称完成单因素视觉实验，也没有修改代码。
- 后续最小区分实验：在可访问的 Erken arm_A frame 19 页面锁定视角和 VE，依次对比基线 `force-bed`、单独附加 `skip-field`、单独附加 `bed-depth-colors`、单独附加 `skip-bed`，每步保存截图并读取床面 trace 的 x/y/z、i/j/k、intensity/color、meta 与 Plotly `_fullData`。`skip-wall` 无需在 VE>80 重复测试；若换低 VE 测墙体，则须单独固定其它变量。缺少可重复正式路径黑片、这些运行时证据前，根因继续标为**不确定**，缺陷继续标为**未修复**。
- **补充浏览器实测**：经正式桌面 WebView 打开 3D 页并把时间步控件设为19；活动页面标识 `case`，后端 run-status 指向 Erken attempt03 arm_A，状态为 idle。页面时刻为 `2024-DOY166 09:00`、相机斜视34°、自动 VE=166.4×。页面状态明确显示因高 VE 已隐藏床面填色；截图因此不能证明该倍率床面渲染正常，也未提供强制床面的默认路径缺陷复现。仅改变了显示时步，没有保存案例/模型输入。

### 2026-10-24 Sol：Erken arm_A 高倍率床面单变量 WebGL 对照

- **实测（浏览器诊断，不是科学验证）**：从本地 Edge 浏览器打开 `http://127.0.0.1:8768/?viz3d-diagnostic=...`，服务 run status 为 idle，case_directory 明确指向 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`。固定水温 `temp`、frame19（`2024-DOY166 09:00`）、斜视仰角34°、VE166.4×、连续水体网格、模型上下位置0%，376有效水格、原网格10×18×44。`Plotly` 图数据记录 floor trace 1504顶点、752三角形、z范围 `[-3074.1474,-167.4359]`；显式 URL 诊断强制床面 trace，故此结论限定于诊断渲染路径。页面引用 `viz3d.js?v=102`，服务返回 JS 与当前工作区文件 SHA-256 均为 `D97D2D79A3C59DD19CB45577E9440A16DB0AFCC16A9D2B8C30CFBF65112460DB`；HTML 的版本 query 与本地模板记录版本不同，但该床面模块文件字节一致。绘制由本地 Edge headless WebGL 完成，不代表正式用户流程或模型科学验证。
- **单变量对照观察**：

| 单一变化（其它变量固定） | 浏览器画面与 Plotly 数据 | 可确认结论 / 限制 |
|---|---|---|
| 基线 `force-bed` | 斜视下见明显黑色床面下表面；trace 元数据 `waterbodyFrame=bed`，默认床面颜色 `#c5cdd1`，未提供 `intensity`。 | 实测：在此诊断场景复现黑面；不代表默认正式路径复现。 |
| 只加 `skip-field` | 水温 field trace 从8条总 trace 中消失，床面仍是1504顶点/752三角形；黑色床面继续出现，局部黑白形态改变。 | 实测：温度场 trace 不是黑色床面的必要条件；场图会影响叠加形态。 |
| 只加 `bed-depth-colors` | 床面 geometry/camera 不变，床深 intensity 范围约1.006–18.474m并使用青蓝深度色带；黑色下表面不再明显。 | 实测：显示结果对床面颜色/强度映射路径敏感。它支持颜色/材质相关候选，但不能单独证明 Plotly 缺陷、法线/背面光照或深度精度中的唯一机制。 |
| 只加 `skip-bed` | 床面 trace 不在 Plotly `_fullData` 中，画面黑色床体消失；水温场、岸线、陆地示意与等深线仍存在。 | 实测：当前黑体与床面 trace 绘制相关；不等于某个顶点、索引或 GPU 路径已确诊。 |
| 仰角34°改为89° | 保留同一床面 trace几何、frame和VE，近顶视图中黑色下表面不可见。 | 实测：画面随视角改变；不能据此判断是遮挡、背面光照还是渲染精度。 |

- **Sol判断**：候选根因进一步收敛到“高 VE 下倾斜/可见床面与床面固定颜色/强度绘制路径的交互”，且可能受相机角度影响；更细的内部机制仍**不确定**。证据不支持将动态 field 作为唯一根因，也不支持把 XY 绝对坐标量级作为本例唯一解释。需继续用浏览器运行时记录比较顶点色/面法线与 WebGL 绘制、低倍率同颜色对照、多个角度与代表案例确认，并在正式无诊断用户路径复现/修复后重验。
- 证据截图归档于 `docs/audit/user-journey-20261021/assets/bed-diagnostic-20261024/`：`force-bed-34deg.png`、`force-bed-skip-field-34deg.png`、`force-bed-depth-colors-34deg.png`、`skip-bed-34deg.png`、`force-bed-89deg.png`。源码与案例输入未更改；本节不声称修复完成。

### 2026-10-24 Sol/Luna：高 VE 床面显示缓解与桌面同步复核

- **代理（实现契约验证，不是科学验证，也不是原缺陷已修复的证明）**：`3DWET/app/static/js/viz3d.js` 在动态叠层垂向倍率 >80× 时保留床面 trace，并使用单独的湖底深度（m）色带；状态与悬停说明区分床深和所选科学变量色阶，并保留“黑片成因尚未确认”。普通倍率配置不变。该变化基于前述诊断场景中启用床深色带后黑色下表面不再明显，但没有默认用户路径黑片可重复复现证据，故**黑片缺陷状态仍未修复/未确认**，不得以该缓解措施宣称根因已确诊或缺陷已完全修复。
- **代理（自动化回归断言）**：`node --test 3DWET/tests/test_viz_waterbody_patch.js` 21/21 通过；包括50×→166.5×切换后检查 Plotly 重建床面色带、保留变量场；`node --check 3DWET/app/static/js/viz3d.js` 通过。断言覆盖实现契约，不是科学验证或图像级缺陷验收。
- **实测（用户提供的浏览器对照）**：当前版本 frame19 的200×静态床面和50×叠层对照未复现黑片；因此继续保留缺陷未修复状态。不得由未复现推断缺陷不存在。
- **实测（本轮桌面同步）**：重启工作区8768服务后 `/` 返回200且引用 `/static/js/viz3d.js?v=104`；`/api/system/health` 返回 ready=true、model_root 为当前仓库 `3DWET`。服务 JS 与磁盘 JS SHA-256 均为 `19B5DD894EB07F8AFB170787F759383C026ADDBCA1ED4F81A7669B1612784071`。重启桌面 `3DWET Studio` 后，当前 3D 状态文字显示“床面按湖底深度（m）着色，与所选变量色阶分离；黑片成因尚未确认”，确认窗口已加载新源。该桌面窗口当前显示一般 `case` 案例与 frame0，不等同 Erken frame19 缺陷验收。
- **完整用户流程与案例状态**：仍按本记录前述条目标注；流程未完成；Erken、Lake Ravn、Bryrup、Arreskov 科学验证均未完成。任何工程代理烟测不得升格为实测科学验证。

### 2026-10-24 Sol：Arreskov 原始配置来源追溯补记

- **实测（官方发布物清单与校验）**：下载 Zenodo WET v1.0 `wet-v1.0.zip` 后，MD5 为 `04a6e996fdcd1ba9553258a831a61b3a`，与 Zenodo 记录一致；压缩包内有 `testcases/lake_bryrup_denmark/fabm.yaml`，未找到 Arreskov testcase 或 Arreskov `fabm.yaml`。来源：[WET v1.0 Zenodo 记录](https://zenodo.org/records/6482852)。
- **实测（公开 GitLab 路径历史）**：GitLab API 按 `testcases/lake_arreskov_denmark/fabm.yaml` 查询返回空提交列表；按 testcase 目录查询只返回提交 `0b1f7366`，其 diff 是添加 `.gitkeep` 空占位文件。来源：[GitLab Arreskov 路径提交记录](https://gitlab.com/api/v4/projects/50484945/repository/commits?path=testcases%2Flake_arreskov_denmark&per_page=100) 与[该提交差异](https://gitlab.com/api/v4/projects/50484945/repository/commits/0b1f736602db779b5022c316f689dc9fa6919bda/diff)。该核验限于上述公开项目和可检索历史，不排除作者另有未公开存档。
- **来源不一致（未解决）**：Arreskov 论文软件可用性段落称其模型配置 included in the WET repository as a test case；当前可取得的 WET v1.0 发布包与公开 GitLab 该目录却没有该配置。[论文全文](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf)。论文描述的是1D GOTM–WET、16水层及多模型集成；Aarhus DCE 402报告另列 Arreskov 旧五湖应用的20层与100组参数 ensemble，但该报告描述不等于缺失的论文版 `fabm.yaml` 或可执行复现包：[DCE报告条目与PDF](https://pure.au.dk/portal/en/publications/dynamiske-procesbaserede-modeller-som-forvaltningsv%C3%A6rkt%C3%B8j-for-dan/)。
- **验收状态不变**：Arreskov 原始案例配置和科学验证仍**未完成**。DCE 402是旧案例研究证据，不能升级为当前项目的 WET 原始输入或实测复现。不得根据论文概念图、参数范围或旧报告自行重建并称其原始配置。若要完成指定论文复现，仍需取得作者/维护者保存的确切 WET、GOTM、FABM 配置及相应 forcing/观测数据。

### 2026-10-24 Sol：WET v0.2.0 Arreskov 归档逐文件核验

- **实测（官方发布物校验与文件清单）**：下载 Zenodo WET v0.2.0 `wet-v0.2.0.zip`，MD5 `b31a92c9f9618893b1dd7e1b6c3d875f` 与 Zenodo 记录一致。归档 Arreskov 目录包含 ERA5/meteo、GOTM、hypsograph、inflow/chemistry、manipulations、outflow、waterlevel、output 与 README；仍只有空 `.gitkeep`，没有湖泊专属 `fabm.yaml`。来源：[WET v0.2.0 Zenodo 记录](https://zenodo.org/records/8369208)。
- **实测（本地输入来源对照）**：逐文件比较 v0.2.0 归档与工作区 `3DWET/src/wet/testcases/lake_arreskov_denmark/` 的同名文件 SHA-256，除空 `.gitkeep` 外，现有所有同名文件均不匹配。两份 forcing 内容差异原因尚未逐项解释；故仓库目录不能标为逐字节官方原件。没有覆盖仓库文件，也没有用通用 `fabm-wet.yaml` 代替湖泊生态配置。
- **验收状态不变**：发现官方 forcing 集仍不足以消除关键的生态配置缺失；Arreskov 原始论文复现与科学验证继续标记**未完成**。通用 WET 默认配置或重建配置只能另标代理，不能升格为原论文案例实测。

### 2026-10-24 Sol：原生桌面服务端口误判更正

- **实测（桌面同步）**：原生 `3DWET Studio` 进程仍运行，PID 82388，窗口标题为 `3DWET Studio` 且 Responding=True。桌面启动器检测到并附着到本工作区已有 ModelRoot 服务 `http://127.0.0.1:8768`，所以不另开 8772 端口；此前把 8772 未监听解释为桌面未同步，是端口假设错误。
- **实测（当前服务/源码）**：8768 `/api/system/health` 返回 ready=true、model_root 为当前仓库 `3DWET`；首页 HTTP 200 并引用 `viz3d.js?v=104`、`ecology_network.js?v=26`。本地 `viz3d.js` SHA-256 为 `19B5DD894EB07F8AFB170787F759383C026ADDBCA1ED4F81A7669B1612784071`。运行状态端点为 idle，目录身份是 Erken attempt03 arm_A；这不等于完整 UI 流程或案例科学验证通过。
- **范围限制**：当前 CUA 会话没有可枚举浏览器/原生 app surface，因此本次未另做 WebView 内逐页交互复查。历史记录中有桌面状态文字截图/检查，但本次证据只确认响应桌面进程、附着服务及当前源码路由。

### 2026-10-24 Sol：当前 UI 页面级实测补记（不等同完整流程）

- **实测（浏览器 UI）**：通过工作区 8768 当前页查看仪表盘、3D、食性配置和2D结果视图。仪表盘显示376个水域格、10层、20个生态模块和168个输出时步；活动服务运行目录仍指向 Erken attempt03 arm_A，模型状态 idle。3D页显示温度变量、166.5×自动垂向倍率、34°镜头、时帧控件、湖底独立深度色带提示及“黑片成因尚未确认”；此当前 frame0 页面没有复现黑片，且不是缺陷验收。
- **实测（食性 UI）**：从阶段导航进入“生态网络与食物网”，页面可见模块分类过滤、食性配置分层图、编辑关系快捷入口及按消费者筛选编辑区；当前载入的配置汇总显示已解析17条食性端口关系、三节点闭环0个。只查看和展开快捷编辑入口，没有保存/修改案例输入；这不验证求解器注册或摄食科学合理性。
- **实测（2D 结果 UI）**：成功切换到2D结果页，页面显示水温、图例/湿掩膜、输出时间与帧播放控件。本次不重新运行模型或改正式案例输入。
- **验收状态**：以上是当前源版本下的页面级 UI 可达性记录，不覆盖完整十项 UI 检查、完整用户流程、案例科学验证或连续五轮要求；这些仍为**未完成**。本轮未修改产品代码，桌面无需重新同步。

### 2026-10-24 Sol：Arreskov 论文所引 WET v0.1.0 归档可访问性核验

- **实测（论文来源）**：Arreskov 论文软件可用性段明确写明模型配置包含在 WET repository 的 test case，并将软件地址指向 `https://gitlab.com/WET/wet/-/releases/v0.1.0`。论文页面还列出 Supplementary Data DOI `10.1016/j.envsoft.2022.105501`，但当前公开元数据/论文页面没有给出可直接下载的湖泊完整配置文件。[论文 PDF](https://pure.au.dk/ws/files/333228766/1_s2.0-S1364815222002043_main.pdf)。
- **实测（当前公开仓库）**：GitLab 公共 API 项目 `wateritech-public/waterecosystemstool/wet`（ID 50484945）的 tags/release 列表为 v0.2.0、v0.2.1、v2.2、v2.3；旧论文所引 `WET/wet` 路径在当前匿名网页访问重定向到 GitLab 登录页。故此前检查 v0.2.0/v1.0 公共归档未找到 Arreskov 专属 `fabm.yaml`，不能推断 v0.1.0 归档中一定没有。
- **结论（未完成）**：这项追溯未恢复论文所称的 v0.1.0 test case，也未提供可执行原配置。Arreskov 的正式复现/科学验证继续为**未完成**；下一项可追溯证据需来自作者/维护者提供的 v0.1.0 原始归档、配置文件或无需登录的历史镜像，并核对其哈希和来源。

### 2026-10-24 Sol：官方 WET v0.1.0 Zenodo 原包核验

- **实测（官方归档及校验）**：根据 WET 论文引用 DOI `10.5281/zenodo.4903142` 下载官方 `wet-v0.1.0.zip`（2,990,542 bytes）；MD5 `8b16645d6625863ce6d8d8416195aa37` 与 Zenodo 文件记录一致，SHA-256 `B238D49CED074CA9297DC8FF2AD26A3F6E6DA4A0642138458B5D3B8B5EF17CE1`。官方 ZIP 的 testcases 目录只包含通用 GOTM/WET 配置和 `lake_bryrup_denmark` 文件，没有 `lake_arreskov_denmark` 或 Arreskov 专属 `fabm.yaml`。[WET v0.1.0 Zenodo 记录与校验和](https://zenodo.org/records/4903142)。
- **来源边界（仍不确定）**：这证明官方 v0.1.0 Zenodo 发布 ZIP 不含 Arreskov；不证明论文发表时 GitLab 工作树/其他未归档目录也没有，因为论文仅说配置在 WET repository 的 test case，旧 GitLab 路径当前匿名不可访问。论文与可取得发布包之间的差异继续未解决。[Arreskov 论文 PDF](https://pure.au.dk/ws/files/333228766/1_s2.0-S1364815222002043_main.pdf)。
- **验收状态**：未恢复 Arreskov 案例配置；正式复现与科学验证仍为**未完成**。没有把该 v0.1.0 包中的 Bryrup配置拿来代替 Arreskov，也没有从论文描述重建生态参数。

### 2026-10-24 Sol：当前版强制床面诊断视图复核

- **实测（浏览器渲染）**：在 8768 当前源服务以 `?viz3d-diagnostic=force-bed` 打开实际 Erken attempt03 arm_A 结果，切换至 `temp`、frame0、斜视34°、自动 VE=166.5×。截图显示可见的蓝色深度渐变湖底和水温场，未见明显黑色床面片；状态文案确认床底色阶独立于温度色阶，并保留原因未确认说明。
- **解释限制**：当前源码在 high-VE dynamic overlay 下自动使用 depthScale，这一路径与历史复现时的中性床面材质不同；因此本次诊断 URL 画面不能复现或排除历史黑片，也不能证明修复。床面 trace 几何、frame、视角与颜色材质仍需固定后分别对照。
- **下一诊断动作**：Sol 已请 Luna 增加仅显式诊断 URL 启用的高 VE 中性床面样式选项及断言，用于恢复历史 A/B 条件；不得改变默认路径、修改案例输入或将结果称为缺陷修复。待实现/同步后，Sol 将独立浏览器复核。

### 2026-10-24 Sol/Luna：中性床面诊断实现与桌面同步复核

- **代码实现（仅诊断能力，不是缺陷修复）**：Luna 在 `viz3d.js` 增加显式 `?viz3d-diagnostic=force-bed-neutral` allowlist，仅在高 VE 动态叠层诊断路径把床面恢复为原中性样式；默认路径未启用该覆盖。测试断言切换中性/深度床色时床面几何和科学场数据不变。`node --test 3DWET/tests/test_viz_waterbody_patch.js` 实测通过22/22，`node --check` 由 Luna 报告通过。此实现只提供隔离变量的工具，未确认唯一根因，也没有宣称修复黑片。
- **实测（桌面同步）**：关闭并重启旧桌面会话后，新原生 WebView 进程 PID 77340，窗口标题 `3DWET Studio`、Responding=True；桌面服务 `http://127.0.0.1:56162/api/system/health` 返回 ready=true，model_root 指向本仓库 `3DWET`，run status 为 idle。首页引用 `viz3d.js?v=105`；桌面服务返回该脚本的 SHA-256 `9582AB2D008F1397886D15A3E7106ACB16D115FB57B0368E53A071D4E0B955C7` 与当前源码文件哈希一致。新的 WebView 首页已加载 v105；旧独立8768服务已停止，未将旧缓存页当成当前版本。
- **实测（诊断页面）**：桌面服务3D页可达，活动后端 case_directory 仍指向 Erken attempt03 arm_A，状态 idle；当前显示 temp、frame0、斜视34°、自动 VE约166.5×、水层9。显式 neutral 样式诊断画面未见明显黑片。该状态不是用户给出的200×静态床面或50×叠层完全同条件，也没有完成 frame19 固定视角/倍率逐像素 A/B，因此不能确认缺陷消失。页面结果仅用于 UI/渲染诊断，不是科学验证。
- **结论与验收**：黑色床面缺陷仍为**未修复**；候选原因仍为多个，根因**不确定**。证据维持变量关联但不支持单一根因。完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证的状态不变，仍有**未完成**项；食性网络与 UI 的先前页面级可达性结论不等同完整验收。参考图片路径仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：neutral 诊断色彩路径浏览器 A/B

- **实测（当前桌面服务身份）**：原生 WebView PID 92992；关联服务端口60535，health ready=true、model_root为本仓库、run idle；case_directory为 Erken attempt03 arm_A。首页 v106 与 served `viz3d.js` SHA-256 `63E73666D0BD63CBB864B6BF5E3B4D1F3DB4D67925147B174A59CBBFDA17370B` 匹配本地。
- **实测（50×动态叠层）**：浏览器 URL 带显式 `force-bed-neutral` 诊断；temp、frame19（2024-DOY166 09:00）、斜视34°、VE50×、376有效格、0水域缺测。画面未见明显黑色床面片。
- **实测（静态 bathymetry、VE200×）**：同一活动 Erken 案例，静态 bathymetry 与活动输出时步无关（UI 保留/显示 frame19，但静态地形时间控制禁用），斜视34°、中性床色诊断时出现明显黑色三角/片状湖盆面；切到俯视后湖盆内部大片呈黑色。取消诊断、保持静态 bathymetry、VE200×及同一相机预设时，默认深度色带显示蓝色床面，未见同样黑片。两个页面来自同一服务/案例；截图为浏览器当前 WebGL 渲染观察，不是模型科学验证。
- **解释限制**：该 A/B 显示床色编码路径和渲染结果存在联系，令 fixed-color/material 路径成为强候选；但诊断的中性色不等于原始用户条件，黑面可能与网格面朝向、Plotly mesh3d 编码、叠层/遮挡等交互，故根因仍**不确定**，不能据此认定为唯一根因，也没有改生产默认渲染。此前“200×静态与50×叠层未复现”记录保留：本轮的黑片是在显式强制中性色静态诊断下观察到，并非宣称原始默认路径已复现/修复。
- **下一验证**：在 v106 上增加仅诊断的均匀中性色 `colorscale` 编码，对比固定 `color` 与恒定 `colorscale` trace；保持几何、强度源数组、床面显示层、相机及 VE 不变。若差异消失，可进一步定位渲染编码；若持续，则需继续隔离几何、面向和遮挡。生产缺陷仍为**未修复**。

### 2026-10-24 Sol：v107 静态床面颜色编码 A/B

- **实测（浏览器渲染观察）**：在 v107 当前服务 `http://127.0.0.1:57768`，后端健康状态 active case path 指向 Erken attempt03 arm_A，运行 idle。两浏览器标签使用同一服务与同一当前 case，均为 `bathymetry.nc` 静态地形、VE=200×、相机斜视34°、变量水面关闭、同一床面几何。显式 `force-bed-neutral` 固定 `color` 样式出现明显黑色床面片/大块黑面；显式 `force-bed-neutral-scale` 恒定中性色 `colorscale` 样式显示灰色床面，未见相同黑片。页面的静态地形时步控件禁用，故这不是 frame19 动态对照。
- **解释限制**：这是针对 Plotly trace 颜色编码分支的强诊断证据，说明中性色 `color` 与等值 `colorscale` 两条渲染路径表现不同；它尚未证明唯一底层根因（仍可能涉及 Plotly/WebGL 材质分支或其与几何/相机/遮挡的交互），也没有改变生产默认渲染。不能据此称缺陷已修复，也不推翻用户先前在其 200×静态与50×叠层对照中未复现的证据。
- **实现与检查**：Luna 新增仅由 `?viz3d-diagnostic=force-bed-neutral-scale` 显式启用且 VE>80 才生效的恒定中性色标诊断；保留 intensity、床面几何、科学场数组及默认渲染。`node --check` 通过；`node --test 3DWET/tests/test_viz_waterbody_patch.js` 实测通过24/24。桌面端正常关闭后重启，PID93236 / port57768 ready、run idle；首页引用 v107，服务返回 JS SHA256 与磁盘一致：`972FE83F7F892D494DE7FA4FEA0E6B8E8DEDC1F151CB60EB6C5A9EC21C24CC8D`。
- **状态**：黑色床面缺陷仍**未修复**；根因**不确定**，候选不止一种。完整用户流程、Erken/Lake Ravn/Bryrup/Arreskov 科学验证仍有未完成项。参考图保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：初值部分写入反馈修复与同步

- **实现（Luna）**：`saveInitConditions()` 现在检查 `/api/case/init_conditions` 的 `warnings`。若 API 在 `success:true` 同时报告部分写入失败，界面保留 dirty 标记、显示明确的部分保存警告，不更新成功状态或发成功 toast。没有修改任何案例输入。
- **代理（自动回归/隔离 fixture）**：新增 `test_initial_save_feedback.js` 对旧行为先失败、修复后通过；Sol 独立复跑初值反馈、初值 draft、实例初值 Node 检查与 JS 语法检查均通过；`.venv\Scripts\python.exe -m pytest tests/test_initial_conditions_rebuild.py -q` 18/18 通过。以上没有在页面中实际制造部分写入失败，也没有在真实 UI 里保存—重载；故完整用户流程第2项仍**未完成**，这些自动测试/fixture 按**代理**处理。
- **实测（桌面同步）**：正常关闭旧空闲窗口后运行 `launch_desktop.cmd`。新 `3DWET Studio` 窗口 PID72372，服务 port49453，health ready=true、model_root 指向当前仓库，run idle；case_directory 指向 Erken attempt03 arm_A。首页引用 `app.js?v=64` 与 `viz3d.js?v=107`，两脚本 HTTP 200 且 SHA-256 分别与磁盘匹配（app.js `149D8F612814A912E70A046CC71A01E5241B66CC564BE3224161E797B5FC7990`；viz3d.js `972FE83F7F892D494DE7FA4FEA0E6B8E8DEDC1F151CB60EB6C5A9EC21C24CC8D`）。
- **验收边界**：实现的状态反馈缺口已修复，但保存后的完整持久化流程仍须在隔离合成案例上做页面级操作和重载验收；十项完整 UI 清单及连续五轮仍未通过。四湖科学验证状态不变，代理验证不升格为实测。

### 2026-10-24 Sol：隔离合成案例运行工作流 UI 补验

- **代理（浏览器 UI 操作）**：在独立服务 `http://127.0.0.1:59730` 操作仅供流程烟测的合成案例 `Imported Random Lake`，其 model_root 为 `build/full-workflow-20261024-attempt59/ui-model-root`，162 水格、6 层，不是 Erken/Lake Ravn/Bryrup/Arreskov 的湖泊科学案例。页面先经运行前体检识别 CFL 关闭与输出订阅提醒；从诊断面板分别执行“启用 CFL 检查”和“采用当前案例的标准输出订阅”，界面确认 `getm.inp`、`output.yaml` 已修复并备份，复检显示0条提醒。随后从 UI 启动模型，页面显示600/600步、100%、状态已完成；日志含“结果有效性检查通过”及结果归档，文件面板显示日志、2D、3D、output.nc 共4项。此前记录的这一 UI 顺序作为合成案例流程代理证据，不是生产湖泊实测或科学验证。
- **定位入口补验未完成**：尝试在同一合成案例通过全量输出订阅生成告警，体检仍显示0条提醒，未出现“定位设置”链接。尝试把时间步长设为4s时页面给出超过CFL的即时提示，但未能持久保存；离开时间设置后返回值恢复2s，无法形成告警—定位入口的有效跳转验收。故“诊断→定位→修复→复检→重跑”中的定位路径尚未完整实测，清单第4项仍为**未完成**。为安全起见没有改生产案例，也未再次启动模型。
- **案例目录边界**：全量订阅的 UI 操作与此前标准输出配置所用均限于隔离合成案例，保存后界面显示标准订阅13项；随后尝试改动仅用于诊断，未改动真实湖泊案例。合成模型运行的结果不升级为实测科学证据。
- **桌面同步影响**：本次没有源代码修改，故无新增桌面代码同步动作。原生桌面会话仍按上一节记录为 PID72372 / port49453、ready、idle，引用 app.js v64、viz3d.js v107；本轮独立代理服务不替代原生桌面版本检查。
- **验收状态**：完整用户流程仍**未完成**；四个指定案例的科学验证仍**未完成**。上述 UI 烟测仅为**代理**。

### 2026-10-24 Sol：隔离合成案例初始条件保存与重载 UI 验收

- **代理（浏览器 UI 流程）**：在独立服务 `http://127.0.0.1:56158`、合成案例 `Imported Random Lake`（model_root `build/full-workflow-20261024-attempt59/ui-model-root`）中，页面读取初始水温约14.551℃。将其改为14.75℃，点击“保存到案例”；UI 回报 getm.inp 写入 `temp/temp_const=14.75℃`、fabm.yaml 更新112项水质初值、fabm_init.nc 已重新生成。随后点击“重新读取”，再刷新页面并经“案例管理→加载”重新加载该案例；初始条件页重新显示14.75℃。这确认本合成案例的初始条件保存与重载路径，不是四湖数据或科学验证。
- **范围限制**：本次仅在隔离合成案例写入了初始条件；没有触碰 Erken、Lake Ravn、Bryrup、Arreskov 或原生桌面当前案例。UI 显示112项写入，但没有模拟部分文件写入失败，故部分写入警告的页面级验收仍未完成。参数编辑页的保存与重载也未覆盖；完整用户流程第2项继续标为**未完成**，当前初始条件路径证据标为**代理**。
- **桌面同步**：没有源代码修改。本轮临时服务结束后，原生桌面版本以此前 PID72372/port49453核对结果为准；未改动桌面应用当前案例。

### 2026-10-24 Luna/Sol：参数页空模块缓存修复与代理 UI 回归

- **代码修复（Luna）**：参数编辑页进入时若当前案例已知但前端 FABM 模块缓存为空，现在按当前活动案例请求 `/api/config/fabm` 补齐模块/类别；若请求期间案例发生切换则丢弃旧响应。新回归测试 `3DWET/tests/test_parameter_module_loading.js` 覆盖空缓存补取与 option 填充。
- **代理（自动检查）**：新回归测试先失败后通过；Sol 复跑 `test_parameter_module_loading.js`、`test_parameter_autosave.js`、`test_parameter_types.js`，均通过；`node --check 3DWET/app/static/js/app.js` 通过。没有修改湖泊案例输入文件。
- **代理（隔离合成案例页面操作）**：修复后的新服务（58450）加载 `Imported Random Lake` 后，参数页显示20个模块，默认水体模块列出17个参数。UI 将 `O2PerNH4W` 从2改为2.05并显示“已保存”；刷新工作台、自动恢复案例并重新进入参数页，值仍为2.05。该页面流验证属于合成案例代理，不代表湖泊科学验证。
- **服务源版本**：隔离代理服务 health ready=true、run idle、model_root 为 attempt59 的 `ui-model-root`；首页引用 `app.js?v=65`，直接服务文件 SHA-256 `4BBE9D00A1E7D079B928E7ADDBBE3DFD0FABD199E3D4BCC8AB02E0378EACC05D` 与磁盘相符。
- **桌面同步未完成**：原生桌面 PID72372/49453 的 health 仍 ready、idle、model_root 正确，但其运行进程首页仍缓存为 `app.js?v=64`。通过 CUA 的本机 app/window 清单未能访问原生窗口；Luna 使用 `CloseMainWindow()` 的优雅重启尝试被执行策略拒绝，未强杀进程、未启动重复窗口。故按 AGENTS.md，桌面 v65 同步/加载验证仍**未完成**。源模板磁盘已是 v65；不能把新隔离服务的 v65 冒充原生桌面已加载。
- **流程状态**：本轮提高了“参数编辑保存—刷新—恢复案例—重载参数”的合成代理覆盖；完整用户流程仍**未完成**，四湖科学验证状态不变。

### 2026-10-24 Sol：用户重开后原生桌面 v65 同步验收

- **实测（桌面服务同步）**：用户确认准备重开后，旧服务 port49453 已关闭、旧原生桌面进程不在；本轮从仓库运行 `launch_desktop.cmd` 启动新原生桌面实例。新服务 `http://127.0.0.1:60336` 的 `/api/system/health` 返回 ready=true、model_root=`C:\Users\23801\Desktop\GETM-FABM-WET-260928\3DWET`、PID25832；`/api/run/status` 为 idle。首页引用 `/static/js/app.js?v=65`，该 URL 服务内容 SHA-256 与当前磁盘 `app.js` 一致：`4BBE9D00A1E7D079B928E7ADDBBE3DFD0FABD199E3D4BCC8AB02E0378EACC05D`。桌面版本同步已确认；参数页具体修复行为另由隔离合成案例 UI 代理验收，不把服务检查等同页面交互科学验证。
- **遗留测试服务**：端口8770、8771仍各自指向不同的 `%LOCALAPPDATA%\Temp\3dwet-*` model_root，首页 v63；port49858 指向20261022 Erken external weather 的隔离 model_root、首页 v59。它们不是本次原生桌面实例（60336），未对其或其案例作修改。

### 2026-10-24 Sol：桌面服务上的 Erken 参数页只读烟测

- **实测（页面可用性，不是科学验证）**：在新原生桌面后端端口60336所服务的当前活动案例 Erken attempt03 arm_A 上，以只读浏览器镜像打开“参数编辑”页。面板正常显示20个模块选项，默认水体模块17个参数项；本次没有编辑或保存 Erken 参数。该页面烟测只说明 v65 中参数页可用，不表示模型科学验证。
- **原生桌面版本**：本页由同步后的60336后端供给；health ready=true、run idle、活动路径为 Erken arm_A；首页 v65 与服务脚本/磁盘哈希匹配（详见紧邻上一节）。

### 2026-10-24 Sol：用户反馈桌面仍为旧版后的原生窗口刷新核验

- **实测（原生桌面窗口）**：通过 Windows UI 自动化找到唯一标题为 `3DWET Studio` 的原生窗口。首次截图后，该窗口文档信息可见 URL `http://127.0.0.1:60336/`；执行一次页面刷新后，WebView 文档和可访问树重新载入完整仪表盘，包含左侧工作流导航、01—05阶段导航、语言按钮和 dashboard 区块。
- **实测（源版本一致）**：窗口URL对应服务 `/api/system/health` 报告 `ready=true`、model_root 为本工作区 `3DWET`、PID 25832；首页引用 `app.js?v=65`。该服务 `/static/js/app.js?v=65` 返回内容 SHA-256 `4BBE9D00A1E7D079B928E7ADDBBE3DFD0FABD199E3D4BCC8AB02E0378EACC05D`，与当前磁盘文件一致。刷新后当前原生窗口已载入工作区当前源版本。
- **旁路旧服务**：同机仍有 port49858 的独立 Web 服务，其首页为 `app.js?v=59`，ModelRoot 属于 `build/real-use-validation/20261022/erken-external-weather-ui`。它与窗口文档当前 URL 的60336服务不同，不能用它判断当前桌面窗口版本；未关闭该服务。
- **状态边界**：该核验确认桌面 WebView 当前源版本已刷新至 v65，不证明所有设计细节已符合最终视觉期待，也不改变完整用户流程、黑色床面缺陷及四湖科学验证的未完成状态。

### 2026-10-24 Sol：独立 Erken 渲染夹具的 trace 可见性观察

- **实测（静态浏览器诊断夹具）**：打开只读夹具 `build/real-use-validation/20261023/erken-june2024-competition-luna-attempt03/bed-black-render-repro/`，已载入 API 快照 `fixture-temp-time167-target26.json`：22×18采样网格、185湿格、源网格10×18×44、温度范围11.5569–13.6808°C、自动VE约175.7×。在同一个面板中分别切换生产湖底面单独、湿网格墙面单独、湖底面+墙面组合；当前固定视角截图均未见明显黑色床面片，墙面单独视图也未出现黑色片。
- **解释限制**：夹具固定的是快照时间167、自动VE约175.7×和夹具默认相机，未复刻用户报告的frame19、200×静态 bathymetry、50×动态叠层及固定视角全组合，也简化了完整产品场景。因此该受控但不匹配条件下的**未复现**不能排除墙面 trace 在目标场景交互中的作用，更不能证明缺陷已修复。候选根因仍不唯一；生产默认未变。
- **下一验证**：要区分床面与墙面及二者交互，仍需在黑片可复现的 frame19、固定相机、200×静态床面/50×叠层条件下记录 floor-only、walls-only、floor+walls 三张对照，并保存同一视角和 trace 数据。

### 2026-10-24 Sol：合成案例参数变更后的运行与结果查看代理续测

- **代理（真实 UI + 隔离合成案例）**：在独立服务 `http://127.0.0.1:60337`（PID 47060，model_root `build/full-workflow-20261024-attempt59/ui-model-root`）中加载 `Imported Random Lake`。参数页由 `abiotic_process_in_water` 正确呈现17项；将 `O2PerNH4W` 从此前已保存的2.05改为2.06，页面提示“已保存”，且案例 `fabm.yaml` 实际值为2.06。
- **代理（前体检与求解）**：UI 运行前体检显示0条提醒：162湿格，2s步长不超过CFL估计2.65757s，预计21个输出时步，磁盘充足。随后UI启动预编译串行求解器，`/api/run/status` 从 running 到 completed；完成600/600步（约4.9s）。日志显示 `getm: Completed`、结果有效性检查通过、2D/3D/output.nc归档成功；output目录文件时间更新至2026-10-24 15:21:58。
- **代理（结果入口）**：求解结束后从 UI 打开2D可视化，再打开3D可视化；两页均加载 `Imported Random Lake` 输出，显示2020-DOY001首个输出时刻、temp变量与水域数据。该UI链路说明参数保存→运行前体检→模型运行→结果归档→2D/3D查看在该隔离合成案例中连通。
- **范围限制**：`Imported Random Lake` 是全流程烟测用合成案例，不是 Erken、Lake Ravn、Bryrup 或 Arreskov；求解器输出有效性检查不等于科学验证。此项只标为**代理**；完整用户流程仍**未完成**，四个指定案例科学验证仍**未完成**。本次合成服务已通过 Ctrl+C 正常停止；原生桌面服务及其活动案例未改动。

### 2026-10-24 Sol：合成案例单格时序与二维图导出代理

- **代理（UI 单格时序）**：在隔离服务 `http://127.0.0.1:60338` 的 `Imported Random Lake`（attempt59 合成模型树）中，结果页 2D `temp`、表层、首输出 `2020-DOY001 00:01:00`。通过“单格时序”工具点击网格 `i=9,j=7`，UI 打开单格时间序列弹窗，绘出20个输出点，x轴覆盖00:01至00:20，温度约从14.749°C下降至14.734°C；选中单格的页面读数约14.749°C，对比案例初值14.75°C。
- **代理（二维图导出）**：通过2D页面“导出二维结果图”按钮触发浏览器下载并收到 Download 事件。PNG `C:\Users\23801\Downloads\3DWET_temp_2020-DOY001_00_01_00 (5).png`，100,733 bytes，SHA-256 `7CC8E62D2ADB539D3B5D9F15F93226FDBAF63C13334FCE2100334A05764CDE4B`。人工查看导出图确认包含水温图、轴和比例尺、色标范围、案例 Imported Random Lake、变量/单位、时间、表层层号、湿掩膜说明。
- **范围限制**：以上为隔离合成案例的工程流程代理；输出曲线没有湖泊观测对照，不能作 Erken 等案例的实测科学验证。当前仅完成单格时间序列和二维图下载入口的合成 UI 操作，区域时间序列/率定点写入/完整仪表盘—剖面—时序—导出串联及用户流程其余阶段仍**未完成**。隔离服务已停止，原生桌面未改动。

### 2026-10-24 Sol：Erken attempt03 当前用户路径床面负对照

- **实测（浏览器渲染行为，不是科学验证）**：通过 60336 本地服务只读查看活动案例 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`。运行状态 idle，现有输出共168帧。选 `temp`、frame19（2024-DOY166 09:00）、斜视相机仰角34°、水体连续网格、显示岸陆示意。在当前页实际依次观察到自动 VE 166.4×叠层、200×叠层、200×静态地形（关闭“水面显示所选变量”）及50×叠层；截图中未见明确的大块纯黑床面片。静态地形显示蓝色水深色带与灰色干地示意面；50×与200×叠层显示变量场。这里的“未见”限于本次浏览器视口与场景，不排除其他视角、数据或渲染状态下复现。
- **代理（该 Erken 模型结果）**：底层输出来自命名为 `luna-attempt03` 的探索性/工程尝试；本次仅检查渲染，不作湖泊科学验证或观测拟合结论。
- **根因判断**：该正常用户渲染路径负对照与用户先前提供的 frame19/200×静态和50×叠层未复现记录一致。既有显式诊断模式曾在固定几何条件下复现黑面，隐藏床面 trace 后黑面消失、改用湖底深度色带后异常不明显；这些仅把候选因素收敛到床面 trace 的显示路径/颜色映射与视角、垂向倍率交互，仍不足以确定唯一根因。黑色床面片保持**未修复**，根因**不确定**。
- **范围限制**：当前桌面服务首页缓存仍是 v65 旧模板（缺少新版 dashboard-canvas/workbench.css）；这次 3D 浏览器观察不代表桌面 UI 已同步到最终 workbench 模板。用户参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：最终桌面工作台源码同步复核

- **实测（原生桌面同步）**：旧窗口正常关闭后，旧 port60336 服务停止。由当前仓库 `3DWET/app/launcher.py --desktop` 重启后，新 port64509 服务 health 返回 ready=true、PID90964、model_root=`C:\Users\23801\Desktop\GETM-FABM-WET-260928\3DWET`。首页 HTTP 200，引用 `app.js?v=68`、`workbench.css`、`scientific_workspace.js?v=17`，不再是旧 `app.js?v=65`。原生 WebView 可访问树和截图显示新版“湖泊模型工作台”首页、分组导航、空间结果预览和工作区检查器。用户反馈的桌面旧版本问题本轮已解决。
- **未完成（目标边界不变）**：此同步复核是 UI/版本实测，不代表床面黑片已修复。黑片仍**未修复**、根因**不确定**；完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍按本台账既有各项状态，未提升为通过。

### 2026-10-24 Sol：新版原生 3D frame19 / 200×叠层复查

- **实测（UI 渲染行为，不是科学验证）**：在新版原生窗口（service port64509，首页 v68）经工具栏正常进入3D可视化；活动结果路径由 `/api/run/status` 指向 Erken attempt03 arm_A。页面选择 `temp`，frame19（2024-DOY166 09:00），仰角34°，连续水体显示；将垂向比例设为200×后，状态栏与剖面标注均显示200×。截图中未见明显大块黑色床面片。该视角是床面与水体叠层，不是关闭变量水面后的静态 bathymetry。
- **边界**：只可说明本次 frame19/200×/34°叠层的当前画面没有明显复现；不能推翻其它视角或静态床面条件的历史黑片观察，不能证明缺陷已修复，也不能作为 Erken 科学验证。黑片仍**未修复**，根因仍**不确定**。`（待补充：frame19 静态 bathymetry 对照截图及参考图具体路径或链接）`。

### 2026-10-24 Sol：frame19 原生静态床面与50×叠层负对照

- **实测（浏览器渲染行为，不是科学验证）**：在原生服务 port64509、当前 Erken attempt03 arm_A、`temp`、frame19（2024-DOY166 09:00）、相机仰角34°的同一 3D 页中，先选 VE=200×并关闭“水面显示所选变量”；`updateViz3dIso` 按正常路径调用 `renderBathymetry3D`，显示静态湖盆床面。截图未见明显大块黑色床面片。随后打开变量水面叠层并改为 VE=50×；正常用户路径显示水温与湖盆结构，截图同样未见明显大块黑片。界面状态和相机保持 frame19/34°。
- **结论边界**：这两张截图与既有报告条件相符，但图层和 VE 在两状态间同时变化，无法从该 A/B 单独判定是哪一个变量影响现象。它们是条件性负观察，不能推翻历史复现，也不能证明修复。黑片仍**未修复**，根因仍**不确定**；Erken attempt03 模型输出仍为**代理**科学状态。
- **后续区分性证据**：需在可复现黑片的同一帧、相机、VE与变量下，分别只切换 floor/wall/land trace，并保存截图及 Plotly trace 几何、颜色/强度、索引和可见性；再在固定图层和视角下单独扫 VE。当前用户参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：原生桌面窗口现场复核（用户反馈仍像旧版后）

- **实测（原生窗口身份与页面）**：使用 Windows UI Automation 取得唯一标题为 `3DWET Studio` 的窗口（PID对应服务 port64509），其 WebView 文档 URL 为 `http://127.0.0.1:64509/`。现场截图和无障碍树显示页面为3D可视化：左侧按“案例与数据 / 模型配置 / 运行与复核”分组导航，中央3D画布、相邻播放控件、右侧“变量与视图”检查器；顶部保留项目/编辑/视图菜单及常用工具栏。页面来源由服务首页 v68 与 `viz3d.js?v=107` 提供。该结构与已批准的轻色科学工作台方案一致；这证明当前原生窗口已加载工作区源码。
- **用户感知仍待核对**：本次取得的是当前3D页截图，不能推断用户所称“旧版”具体指哪一视觉差异；不能只凭 HTTP 版本字符串宣称用户的视觉问题已解决。需要用户指出期望但未出现的改动，或提供当前对照截图。窗口当前显示3D页不代表首页仪表盘状态。
- **桌面同步状态**：原生窗口URL、端口服务健康状态和页面均已现场核实；工作区代码版本已加载。设计细节是否满足用户预期仍**不确定**，UI实施记录保留，但最终设计验收未完成。

### 2026-10-24 Sol/Luna：中性床色路径修复尝试与 v108 桌面同步

- **Luna 实现**：在 `lakeTraces()` 的普通中性床色分支，将 `mesh3d.color='#c5cdd1'` 替换为恒定灰色 `colorscale`，保留顶点水深强度、几何、深度色阶路径、tooltip、图例与灯光；仅显式诊断参数 `force-bed-neutral` 保留直接 `color` 路径作为 A/B 参照。此改动针对“固定颜色编码路径出现黑片”的强候选因素，不证明唯一根因，也不改湖泊数据/求解输入。
- **代理（定向回归）**：`node --test 3DWET/tests/test_viz_waterbody_patch.js` 通过 25/25；`node --check 3DWET/app/static/js/viz3d.js` 通过。测试断言普通低 VE 叠层的中性床色走恒定色标。它覆盖 trace 构造逻辑，不等于生产浏览器画面已消除黑片。
- **实测（桌面同步）**：正常关闭空闲旧窗口并从当前仓库重启后，原生 `3DWET Studio` WebView 位于 `http://127.0.0.1:64257/`，服务 PID 49588、health ready=true、run idle、model_root 为本仓库 `3DWET`，活动输出目录仍为 Erken attempt03 arm_A。首页引用 `viz3d.js?v=108`、`app.js?v=68`、`scientific_workspace.js?v=17`；服务提供的 v108 `viz3d.js` SHA-256 与磁盘相同：`F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`。原生截图显示新版“湖泊模型工作台”首页、3D结果入口、结果画布与检查器。
- **床面缺陷状态**：此次部署和 trace 回归已完成，但没有在稳定复现原黑片的用户条件下确认画面。生产黑片修复验收仍**未完成**；根因仍**不确定**，固定颜色材质/颜色编码路径为强候选而非唯一结论。用户提供的 frame19 静态 200×与50×叠层未复现记录继续保留。

### 2026-10-24 Sol/Luna：桌面快捷方式安装版同步

- **实测（旧版来源定位）**：Windows 桌面 `3DWET Studio.lnk` 指向 `%LOCALAPPDATA%\Programs\3DWET Studio\3DWETStudio.exe`；安装包文件时间为 2026-10-16。此前核验的 port64257 窗口由仓库 `launch_desktop` 的 Python 源码启动，不是该快捷方式安装包，因此“快捷方式打开仍是旧版”属实。
- **实现/构建（Luna）**：用当前源码构建隔离包 `build/current-desktop-package-20261024-luna01`，应用版本 1.4.4；安装器 SHA-256 `FC5EB9C44638B38387708C3211D33B14A009C68ABA295B23118515DADB1FEC03`。包自检和 EdgeChromium UI smoke 均通过；包含的页面资源版本为 `app.js?v=68`、`viz3d.js?v=108`、`scientific_workspace.js?v=17`。升级前旧安装快照保存在同目录 `rollback-installed-20261024`。
- **实测（快捷方式实际安装版）**：安装器退出码0；通过桌面快捷方式目标启动安装版进程 PID86604，服务端口62618，`/api/system/health` ready=true、model_root 为安装目录，运行 idle。首页实际引用 v68/v108/v17；Sol 独立核对三个服务资源与安装目录磁盘文件的 SHA-256 一致。原生截图显示安装版桌面窗口。
- **实测（数据保留）**：对升级前快照内 `3DWET\case` 与 `3DWET\app` 的148个文件逐一比对，均原样保留；另外新增7个已知默认文件备份（`.before-1.4.4.bak`）。模型运行未启动，当前状态 idle。
- **结论边界**：桌面快捷方式安装包已经同步至当前源码资源，旧版来源问题已处理。该同步本身不验收用户是否满意具体视觉细节；参考图仍为 `（待补充：参考图的具体路径或链接）`。黑片缺陷仍**未修复**；四湖科学验证及完整用户流程状态不变。

### 2026-10-24 Sol/Luna：桌面快捷方式安装版更新至 i18n v7

- **实现方 Luna**：基于隔离构建目录 `build/current-desktop-package-20261024-luna02` 制作并安装 3DWET Studio 1.4.5。安装器退出码 0；构建阶段包自检与 EdgeChromium UI smoke 通过（**代理**，不代替用户案例科学验证）。桌面快捷方式仍指向 `%LOCALAPPDATA%\Programs\3DWET Studio\3DWETStudio.exe`。
- **Sol 独立实测（安装运行态）**：快捷方式目标的安装版进程 PID 27356、窗口标题 `3DWET Studio`；端口 50249 `/api/system/health` ready=true，model_root=`C:\Users\23801\AppData\Local\Programs\3DWET Studio\3DWET`，run idle，当前案例 Lake Dianchi。首页脚本版本为 `app.js?v=68`、`viz3d.js?v=108`、`scientific_workspace.js?v=17`、`i18n.js?v=7`。安装目录与服务提供的 `i18n.js` SHA-256 均为 `21CD0BA196C71B6BE55F693A711C30708235E095187C04C07C9051DF54C9C3B4`；`en.json` 服务及磁盘 SHA-256 均为 `5676DDE2900571195716B443C9228A954E13AC9FE6F806A49CA2C3FFB30EB481`；安装模板 SHA-256 为 `6215C8EF9D39DFD9A0A49DFF312CA5F4E171E0275A5A265FB8CCDE4A1CEDBF70`。
- **实测（界面呈现）**：以端口 50249 页面检查安装版仪表盘。等待异步案例结果加载后，当前 Lake Dianchi 仪表盘、侧栏、主视图选择、工作区检查器和结果卡片均显示当前中文 UI；可见湖泊网格/生态模块统计和结果摘要。页面启动时的短暂加载态与最终结果页已分别观察；此项是 UI/桌面版本核对，不是 Lake Dianchi 科学验证。
- **实测（案例数据保留）**：升级前后 148 个案例树文件均保持原 SHA-256；另有 7 个安装器生成的 `.before-1.4.5.bak` 文件，其内容分别与对应升级前文件哈希一致。没有启动模型计算。
- **范围状态**：本次修复的是桌面快捷方式指向旧版的问题；床面黑片仍**未修复**且根因**不确定**。完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 的科学验证仍**未完成**，食性网络使用优化仍**未完成**；不得把 UI 实测/打包代理升级为科学验证。


### 2026-10-24 Sol：安装版食性网络入口只读复核

- **实测（界面与配置读取，未写入）**：在当前快捷方式安装版服务 `http://127.0.0.1:50249/` 的当前案例工作台中进入“生态网络与食物网”。页面资源为 `ecology_network.js?v=26`。使用“编辑食性关系”快捷入口后，分层食性视图切换为启用态并将焦点定位到编辑器；选取现有 JuFish 后，编辑器加载 PLAN 分组中两条既有 prey 配置（copepods、cladocerans），并展示已登记引用/端口数据。未点击“增加 prey”或“保存食性关系”，未更改案例 YAML。
- **说明**：这是食性编辑入口和配置读取的**实测 UI**，不能证明 native FABM 运行时注册、摄食率单位/效果或生态科学合理性。食性网络运行时与科学验证仍**未完成**。

### 2026-10-24 Sol：Erken SITES 宽表导入前置核对

- **实测（原始文件结构）**：检查仓库当前 Erken 输入目录中的 `SITES_TW-PROF_ERK_LRK_20170629-20251130_L2_daily.csv`；文件 SHA-256 为 `C068995FB263CC0B7A6660FF5759AC2080FFD5BD1156C6884A2D6E58813C36E3`。前69行是数据集元数据/列说明，第70行为 `TIMESTAMP,TW_-1.0m,TW_-1.25m,...` 表头；温度按深度分列，时间是日期字段。
- **源码核对**：`3DWET/app/observations.py` 的 CSV 读取直接以第一行初始化 `csv.DictReader`；目前映射可选时间、值、深度等列，但 UI 没有显式表头行或单值列的常量深度字段。该文件原样走当前导入器会把元数据当作 CSV 列名，因此尚未形成有效的观测预览。
- **实测（解析器只读复核）**：直接以明确列映射 `TIMESTAMP`、`TW_-1.0m`、`temp`、`°C`、-1m 向下深度读取同一原文件，当前解析器返回3,142行、0条可用记录、3,142条 `missing_time` 诊断；未写入或应用观测。实际服务预览尚未执行。
- **状态/边界**：本次仅检查源文件与实现，没有调用预览、应用观测或启动模型；案例数据没有被修改。Erken 真实观测导入流程仍**未完成**，该官方输入不得按已验证数据报告。后续需要显式、可审计的表头行、值列、深度和单位映射；不从文件名推断这些信息。

### 2026-10-24 Sol：用户反馈桌面仍显示旧版后的同步状态

- **用户报告**：用户指出桌面上显示的仍是之前的旧版本，并授权我自行重开。
- **实测（服务状态）**：重新核对时，端口64257与50249均无监听，当前没有 `pythonw`/`3DWETStudio` 桌面进程。此前关闭了一个空闲仓库源码 WebView 后，`Start-Process` 启动调用被本机策略拒绝。随后我以普通 Web 服务方式启动仓库源码，64257 health ready=true、model_root 指向本仓库；这只证明浏览器源页服务，不证明原生桌面壳已加载。
- **状态**：桌面端重新打开及用户所见版本的最终验收**未完成**。虽已有先前1.4.5安装版资源哈希实测记录，但用户的现场反馈与“用户看到正确版本”这一验收项相冲突，不能用浏览器预览或旧记录覆盖该反馈。当前参考图路径仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：按用户授权重开后完成源码桌面同步

- **实测（旧版来源确认）**：正常启动安装目录的 `3DWETStudio.exe` 后，首页仍是中文并载入 Lake Dianchi；其安装目录 `.studio-runtime/service.json` 指向 `http://127.0.0.1:51082`，`model_root` 为安装目录副本。这解释了“桌面仍是之前老版本”的反馈。随后通过窗口正常关闭该安装副本。
- **实测（仓库源码桌面）**：从仓库根目录运行 `launch_desktop.cmd` 后，原生窗口由 `.venv\Scripts\pythonw.exe 3DWET\app\launcher.py --desktop` 启动，并附着到本仓库 `3DWET` 模型树和活动服务 `http://127.0.0.1:64257`。原生 WebView 可访问树/截图显示英文工作台及当前已选 Erken 案例；该案例提示“没有输出文件”。首页 HTTP 200，引用 `i18n.js?v=7`、`app.js?v=68`、`observation_manager.js?v=5`。这次证明仓库源码原生桌面已加载当前资源；不代表安装快捷方式副本被重新打包，也不代表科学流程完成。
- **状态边界**：当前打开的是仓库源码桌面窗口。用户提供的 UI 参考图仍为 `（待补充：参考图的具体路径或链接）`；黑色床面片仍**未修复**、根因**不确定**；完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**。本轮 UI/启动链路检查不提升任何科学验证状态。

### 2026-10-24 Sol：修正桌面快捷方式指向

- **实测（旧版来源）**：桌面与开始菜单的“3DWET Studio（桌面 Desktop）”快捷方式仍指向 `%LOCALAPPDATA%\Programs\3DWET Studio\3DWETStudio.exe` 安装副本。源码 WebView 与安装快捷方式不是同一启动入口；前者已是当前源码，后者会继续启动安装副本。
- **同步处理**：在正常关闭空闲源码窗口后，将桌面图标和开始菜单“桌面 Desktop”快捷方式改为仓库 `.venv\Scripts\pythonw.exe`，参数 `"3DWET\app\launcher.py" --desktop`，工作目录为仓库根目录；保留原安装程序图标。安装副本文件未修改，开始菜单的“浏览器 Web”快捷方式未改动。
- **实测（快捷方式启动来源与资源）**：通过更新后的桌面图标重新启动，标题为 `3DWET Studio` 的 WebView 进程来源为仓库 `.venv`。服务 `http://127.0.0.1:64257` health ready，`model_root` 指向本仓库 `3DWET`；首页 HTTP 200，引用 `viz3d.js?v=108`、`i18n.js?v=7`、`app.js?v=68`。服务返回的 v108 脚本 SHA-256 与源码一致：`F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`。
- **呈现验收边界**：本轮能证明快捷方式启动来源和服务资源与仓库一致；当前计算机 UI 通道没有可读原生窗口的截图/DOM能力，因此没有用这项检查宣称用户所见的每个视觉细节都已验收。安装副本仍可通过其 EXE 启动；桌面图标与开始菜单桌面入口现转向源码。
- **状态边界**：此同步不改变黑片状态（**未修复**；根因**不确定**）、完整用户流程状态（**未完成**）或 Erken、Lake Ravn、Bryrup、Arreskov 科学验证状态（均**未完成**）。UI 参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：当前 v108 Erken frame19 床面条件复核

- **实测（浏览器渲染，非科学验证）**：在隔离 model root `build/bed-black-userjourney-probe-20261024/model-root` 上只读打开既有 `user-journey-Erken-import` 输出；后端 ready、run idle，路径仍指向 `build/real-use-validation-20261023/user-journey-Erken-import/output`。页面资源为 `viz3d.js?v=108`、`app.js?v=68`、`i18n.js?v=7`、`ecology_network.js?v=26`；服务 `viz3d.js` SHA-256 与工作区源文件一致：`F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`。
- **实测（静态床面与视角）**：固定 `temp`、frame19（2020-DOY001 02:00）、静态 `bathymetry.nc`、VE=200×、连续水体、岸陆示意开启。34°截图显示正常蓝青深度色床面；仅将相机仰角改为60°后截图仍未见明显黑色床面片。
- **实测（叠层观察）**：改为水温变量叠层且 VE=50×，frame19、34°，截图显示水温面及模型边界，未见明显黑片。此状态相对静态床面同时改变了图层与 VE，不能从这一组比较分离二者的独立效应；它也属于代理 Erken 输出的渲染观察，不是实测科学验证。
- **结论/限制**：重复负观察与用户提供的 frame19、200×静态床面及50×叠层均未复现相符；它不推翻旧条件下出现黑片的历史浏览器记录，不证明 v108 已修复。相机角度在本次静态 200×条件下的 34°/60°对照没有改变观察结果。湖底/水体图层、视角与 VE 对缺陷的独立因果关系仍**不确定**；唯一根因仍无法确认。需要一张同一 frame、同一相机、同一 VE、只切换目标图层且可复现黑片的正式用户路径截图，并同步保存 floor/wall/land trace 属性，才能形成可区分回归用例。
- **状态**：黑片**未修复**；当前 Erken 求解结果仍为**代理**；完整用户流程及四个指定案例科学验证均仍**未完成**。本轮仅改审计文档，无源码改动，无需桌面重启。

### 2026-10-24 Sol：食性网络编辑器当前源版页面复核

- **实测（代理案例 UI 操作）**：在只读隔离工作树服务 `52862` 的 `user-journey-Erken-import` 页面打开“生态网络与食物网”，选择 JuFish；面板显示消费者、食性分组、猎物目标、后缀、摄食清除率（含 `m3/gDW/d` 单位）、肠道占据率和行操作标签。此工作流实例含2条既有 PLAN prey 引用。
- **实测（撤销未保存编辑）**：点击“增加 prey”后，本地编辑器出现第3行；点击“还原此组未保存编辑”后回到原有2行，页面说明“已还原为当前案例中已保存的食性配置；尚未提交更改”。未点击保存按钮或更改 YAML。测试 `node 3DWET/tests/test_ecology_foodweb_ui.js` 通过，覆盖带单位字段标签、还原加载配置、无事务提交、层级食性路径和关系证据展示。
- **优化点**：编辑时可一眼区分消费者、猎物目标、后缀、清除率单位与肠道占据率；可按当前模型族筛选猎物、查看真实配置边和解析证据；撤销仅影响暂存表单并可恢复服务器已保存值，减少误保存风险。编辑提交仍由服务端事务预览校验。
- **状态边界**：这些是隔离 Erken 工程代理配置上的 UI/编辑行为检查，不验证 native FABM 的端口注册、参数单位、摄食量或生态合理性；食性运行时与科学验证仍**未完成**。本轮没有修改产品源码，无桌面同步动作。

### 2026-10-24 Sol：历史 Erken arm_A 当前源版床面补充对照

- **实测（浏览器 UI 渲染）**：在隔离服务 `52862` 中只读打开历史案例目录 `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`，页面资源为 `app.js?v=68`、`viz3d.js?v=108`；服务 health 为 ready、run 为 idle，model_root 指向隔离目录 `build/bed-black-userjourney-probe-20261024/model-root`。未启动求解器，未编辑或保存案例。
- **实测（同一叠层条件）**：选 `temp`、frame19（2024-DOY166 09:00）、相机仰角34°、模型位置+15%、连续网格、垂向倍率200×。当前渲染床面显示温度叠层与中性灰色床面区域；截图中未见历史描述的黑色床面片。角度、位置、帧与倍率在 UI 状态文字/控件可读；静态水底图层并未在该组中单独切换。
- **实测（代理案例来源状态）**：此 arm_A 结果目录来自既有工程回合；它是 Erken 案例输出的**代理**，截图/控件观察本身是浏览器 UI **实测**。本观察不构成 Erken 科学验证，也不能代替用户提供的稳定黑片复现条件。
- **变量—现象关系更新**：本次只支持“当前 frame19 + temp 叠层 + 34° +15% +200× 组合未复现”。此前历史记录中，床底/叠层切换、仰角变化及倍率变化均伴随黑片外观变化；本次没有仅切换一个湖底图层，也没有复现黑片，因此不能从跨回合截图归因某单一变量。床底图层、视角和垂向倍率各自的因果作用仍**不确定**。
- **候选与区分实验**：固定相同输出、相机、倍率与 viewport，只切换静态床底与水体叠层并保存 Plotly floor/wall/land trace 属性；对可复现黑片的最小条件再逐一变更角度或倍率。对 color/intensity/lighting 候选，需在相同几何/视角下比较普通用户路径和单一 trace 材质诊断，并记录 WebGL/Plotly 版本和图像；材质差异若只在诊断覆盖下出现，只能说明该渲染路径敏感，不能直接证明用户缺陷的唯一根因。
- **结论与状态**：当前 v108 在这组历史代理 Erken 叠层条件下未见黑片属于新的负观察；黑片仍**未修复**，根因仍**不确定**。Erken 科学验证、Lake Ravn、Bryrup、Arreskov 科学验证及完整用户流程仍**未完成**。本次无产品源码更改，无需桌面同步。
- **Sol/Luna 源码审查（代理）**：实现方复核 `3DWET/app/static/js/viz3d.js` 的普通静态/低 VE 中性床面色阶、高 VE 深度色阶、床面角点强度、`z=-depth×VE` 几何、三角绕序、照明与高 VE 壁面条件。直接 `mesh3d.color` 仅留在显式 `force-bed-neutral` 诊断覆盖；普通生产路径未发现可据此证明的重复生产缺陷。床面专项测试 25/25、`node --check` 通过；这些测试覆盖代码契约，不等价于正式用户渲染缺陷复现/修复验收。服务 `64257` ready、run idle、根为仓库 `3DWET`，引用 `viz3d.js?v=108`；服务与磁盘哈希一致（`F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`）。因为没有源码改动，无需重启。
- **候选因素与区分证据**：可确认的是黑片曾随床面/叠层显示条件、相机角度和垂向倍率变化；不能确认这些变量中哪一个是独立原因。待区分候选包括材质/颜色编码路径（固定颜色与色标）、动态床面与静态地形间的绘制/遮挡、相机/倍率下的深度缓冲或几何精度、Plotly/WebGL 渲染器差异。后几项目前均为**不确定**，不是根因结论。需要用户原始可复现截图/操作序列及同一浏览器环境下 trace 属性、输入几何和图形渲染日志；随后固定帧/几何/相机/倍率逐一切换图层，再分别探测材质和绘制深度候选。

### 2026-10-24 Sol：Erken SITES 宽表显式映射只读预览复核

- **代理（解析/签名预览，不是 UI 实测或科学验证）**：当前源码 `observations.py` 和 `observation_manager.js` 已支持显式 1-based 表头行、时间列/数值列、恒定深度及单位/变量映射。对 Erken 原始 SITES CSV（SHA-256 `c068995fb263cc0b7a6660ff5759ac2080ffd5bd1156c6884a2d6e58813c36e3`）按第70行表头、`TIMESTAMP`、`TW_-1.0m`、名义深度 1.0m、`temp`、`°C` 执行隔离 `ObservationStore.preview`：3077条数据行中3063条可解析，14条因非有限数值排除；时间范围2017-06-29至2025-11-30，预览签名生成。隔离汇总在 `build/real-use-validation-20261024-explicit-obs-preview/summary.json`。
- **证据解释**：这修正了较早记录中“当前解析器不支持前置元数据/只能得到0条”的过时实现描述：在明确指定第70行后，当前解析器能读取所选深度列。它未经过应用页面的文件选择、预览/应用 UI，也没有把观测写入正式案例。名义1m来自源列名/元数据，传感器实际深度随湖位变化；这项映射不证明精确传感器深度。该 CSV 只选取一个深度列；其它深度列尚未单独审核。
- **状态**：Erken SITES 显式映射解析环节为**代理**；实际 UI 导入/比较与空间代表性映射仍**未完成**，Erken 科学验证仍**未完成**。没有编辑案例输入或运行模型。黑片仍**未修复**、根因**不确定**；完整用户流程及其余三湖状态不变。此为审计文档更新，无产品代码修改，无需重启桌面服务。

### 2026-10-24 Sol：双桌面启动进程与工作区服务状态复核

- **实测（服务来源/资源）**：`3DWET/.studio-runtime/service.json` 指向 `http://127.0.0.1:64257`、本仓库 `3DWET`、PID73836；health `ready=true`、运行状态 `idle`。首页 HTTP 200，引用 `app.js?v=68`、`i18n.js?v=7`、`viz3d.js?v=108`。服务本身运行于本仓库当前源码。
- **进程状态**：本机同时存在较早的原生桌面 launcher PID75480/子进程67096（18:28启动）及较新的 launcher PID7236/子进程69432（19:04启动）；64257 服务 PID73836 于17:49启动。新 launcher 与当前 workspace service 的注册信息相符，但本次没有取得活动原生窗口的可访问树或截图，故无法确认用户眼前焦点窗口、旧窗口是否仍显示旧缓存，不能宣称现场窗口画面同步已验收。未强制结束任何进程。
- **结论**：工作区服务源码版本同步**实测确认**；桌面多实例/用户所见窗口核验仍**未完成**。这不改变黑片**未修复**、根因**不确定**、完整流程与四湖科学验证仍**未完成**的状态。仅更新文档与观察状态，没有产品代码修改。

### 2026-10-24 Sol：Arreskov 权威配置来源补充检索与桌面截图通道异常

- **实测（来源检索，不是模型验证）**：追查到 Arreskov 论文报告其 1D GOTM-WET 研究使用16层、最大深度4m、各层10cm沉积域、NOVANA hypsograph、ERA5小时气象及月平均入流/营养盐边界；论文报告12年校准（1992–2005），并指出生态状态切换时序未能良好复现。来源：[Andersen et al. 2022 论文](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf)。这些论文描述不是可直接运行的逐项配置文件或本任务结果。
- **来源核对**：追查到 DOI `10.5281/zenodo.14033888`，被 2025 年 Mar Menor 论文列为该研究 GOTM-WET 配置文件来源；它不是 Arreskov 2022 配置来源，不能用来填补 Arreskov 缺文件。官方 WET Cases 页面提供 Lake Hinge/Ravn 说明与 Ravn 完整测试包链接，没有 Arreskov 配置下载入口：[WET Cases](https://projects.au.dk/wet/cases)。当前可取得的公开 WET Arreskov testcase 仍缺 `fabm.yaml`；原始 Arreskov生态配置依旧**未完成**。未从论文叙述推造配置。
- **UI通道状态**：Computer-use 列出两个同名 `3DWET Studio` 窗口，但抓取两者时显示的是非目标应用桌面画面；画面与窗口标题/可访问树不一致。按技能流程停止交互，没有点击或改动窗口。故本机截图通道当前无法确认用户所见桌面版本；后台服务 v68 的检查仍有效，但不替代窗口画面验收。
- **总状态**：Arreskov科学验证**未完成**；本次只做来源核查与窗口只读观察，无模型运行、案例写入或产品代码修改。

### 2026-10-24 Sol：Erken SITES 观测 CSV 实际 UI 预览

- **实测（隔离工作流 UI）**：在服务 `http://127.0.0.1:52862/`（health ready；隔离 model root `build/bed-black-userjourney-probe-20261024/model-root`）加载案例 `build/real-use-validation-20261023/user-journey-Erken-import`，进入“率定分析 → 官方观测文件导入”，从案例输入目录选择 `SITES_TW-PROF_ERK_LRK_20170629-20251130_L2_daily.csv` 并执行“预览与质量诊断”。
- **实测（显式映射与预览）**：表头行70、时间列 `TIMESTAMP`、数值列 `TW_-1.0m`、无深度列、恒定名义深度1m、模型变量 `temp`、单位 `°C`、湖泊ID `Erken`；站位按源文件元数据填写为 `Erken Laboratory`。源元数据列出坐标59.84247°N, 18.630983°E与UTC+1，并说明自动水温剖面系统系泊于水下一米、实际深度随湖位变化（[SITES数据集](https://hdl.handle.net/11676.1/wGiZX7JjzAt6ZmD_V1msIID_)）。页面显示3077行、3063条有效记录、14条 `non_finite_value` 逐行诊断，SHA-256 `c068995fb263cc0b7a6660ff5759ac2080ffd5bd1156c6884a2d6e58813c36e3`。这与只读解析器检查一致。
- **范围与解释**：本次验证的是隔离代理案例的实际应用 UI 导入/预览链路；输入 CSV 是真实 SITES 温度观测文件，但预览本身未把观测应用到案例，也未做时空配对、实测模拟比较、深度代表性核验或科学验证。站位标签虽已按来源填写，但 UI 导入预览没有把坐标映射到 GETM 网格，因此页面预览不构成空间配对。名义1m取自所选源列，源文件同时说明实际深度随湖位变化；另有下列只读离线最近水格候选检查，但尚未形成观测-模型配对。未点击“应用到当前案例”。
- **状态**：Erken 导入 UI 预览工程环节为**实测**；对模型的实测比较及 Erken 科学验证仍**未完成**。它不是模型科学验证结果。黑色床面片仍**未修复**、根因**不确定**；完整用户流程及 Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**。本次无应用代码修改，无桌面重启。
- **代理（空间代表性候选检查）**：以源元数据坐标投影到该 attempt03 案例 bathymetry 的 EPSG:3006 网格，最近有效水格中心约相距102.4m，格点水深约16.47m；它只给出候选最近格，不证明仪器所在实际水体被该网格可靠代表。该代理案例3D输出覆盖2024-06-13 13:00起168小时、每小时一帧；其10层垂向坐标在该格的首个有效温度点约对应水下1.65m，不能把名义1m观测直接称为同深度匹配。后续若比较，须记录垂向插值规则、每日时间边界（源文件UTC+1）并继续标注**代理**，不能升级为实测科学验证。
- **实测（代理运行输入门槛复核）**：`arm_A/case/meteo_provenance.json` 明确记录本次短跑为候选代理：SITES 气象单站序列统一广播到44×18网格；云量固定为0.5代理、蒸发量固定为0、无河流流量；多数生态/营养盐初值是默认或代理值；50层温度剖面仅作静态初值，未持续同化；气压源元数据称Pa但数值按hPa尺度乘100，文件仍保留单位审查门槛；末端另加一条保持末值的非观测边界填充。该运行元数据自身声明“not a reproduction, calibration, or field scientific validation”。因此本轮不把它与真实温度序列计算出的误差指标包装成科学验收；需要先补齐并核验完整强迫、河流及生态初值，解决压力单位来源差异，并明确每日时间与垂向代表性配对方案。

### 2026-10-24 Sol：完整 UI 流程第8项语言切换与桌面重开

- **实测（应用 UI 偏好持久化）**：在源码服务 `http://127.0.0.1:64257/` 的“语言”对话框选择 English 并应用，实际页面切换为 `en-US`，标题和工作台文案变为英文；刷新后待语言包/偏好初始化完成，页面恢复英文。服务 `GET /api/system/language` 返回 `{"locale":"en-US","packs":[]}`，对应持久偏好位于仓库 model root 的 `.studio-runtime/language.json`。首次刷新后的短暂中文是异步初始化完成前状态，不是持久化失败。
- **实测（源码桌面同步）**：在空闲状态正常关闭源码桌面窗口并从本仓库重新启动；当前仅有一个标题 `3DWET Studio` 的源码窗口（PID78656）。服务 health ready=true、run idle、model_root 为本仓库 `3DWET`；首页资源为 `app.js?v=68`、`i18n.js?v=7`、`viz3d.js?v=108`。`app.js?v=68` 服务与磁盘 SHA-256 一致（`4df0e939931636bc38d7345e8c24429ff785340ea58ffd43d7b6e82ae3899f6e`）；`i18n.js?v=7` 一致（`21cd0ba196c71ef5e55f693a711c30708235e095187c04c07c9051df54c9c3b4`）。IAB 浏览器在同一服务实际呈现英文首页；原生 WebView 直接截图通道未提供，因此原生页面像素级检查仍未完成。
- **清单状态更新**：完整 UI 十项中的“语言切换持久化”现有当前源码/服务 UI 的**实测**证据；该单项通过不代表十项清单或完整用户流程通过。参数/初值保存重载、诊断修复重跑、结果导出组合、通知等其它未完成项目仍须逐项验收。四湖科学验证、黑色床面片状态不变。
- 本轮只改变了 UI 语言偏好并重启桌面窗口，没有修改应用代码、案例配置或运行结果。

### 2026-10-24 Sol：合成代理案例参数保存重载与桌面旧版反馈复核

- **代理（参数持久化 UI 流程）**：将 `build/full-workflow-20261024-attempt59/ui-model-root/case/Imported Random Lake` 复制到隔离路径 `build/parameter-roundtrip-proxy-20261024/Imported Random Lake`，仅在副本中打开参数编辑器，将 `abiotic_process_in_water.cVSetIM` 从 `-1.1` 改为 `-1.11`。UI 显示“已保存”；副本 `fabm.yaml` 中出现 `cVSetIM: -1.11`；刷新应用、重新打开参数页后仍显示 `-1.11`。这验证的是合成湖的参数保存/页面重载代理流程，不是 Erken、Lake Ravn、Bryrup 或 Arreskov 案例验证。
- **实测（源服务）**：`http://127.0.0.1:64257/api/system/health` 返回 ready，`model_root` 为本仓库 `3DWET`，`/api/run/status` 为 idle。首页引用 `app.js?v=68`、`i18n.js?v=7`、`viz3d.js?v=108`，与当前仓库资源版本相符。
- **桌面同步限制**：按用户“自己来”授权，向旧的空闲 WebView 窗口 PID78656 发送正常关闭请求并成功关闭。随后启动新桌面窗口的 `Start-Process` 调用被本机策略拒绝；未尝试绕过该策略。故当前源服务虽仍运行且资源最新，新的原生桌面窗口**未完成重开**，用户桌面所见版本仍未能最终复核。该项需要用户从已改指向源码的桌面快捷方式正常打开一次，再由当前窗口确认。
- **总体状态**：参数保存重载为**代理**；完整用户流程仍**未完成**。黑色床面片仍**未修复**、根因**不确定**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证均仍**未完成**。参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-24 Sol：合成代理案例初始条件保存与重载

- **代理（初值 UI 流程）**：继续使用隔离副本 `build/parameter-roundtrip-proxy-20261024/Imported Random Lake`。在“初始条件”页面将温度从14.75°C改为14.76°C，点击“保存到案例”；UI 回报已写入 `getm.inp` 水位/水温、112项 `fabm.yaml` 水质初值并重新生成 `fabm_init.nc`。再点击“重载”，页面仍显示14.76°C。
- **解释边界**：本次确认为合成案例中该 UI 字段的保存与重载工程链路；改变仅发生在隔离副本，不代表代理初值合理，也不代表任何指定湖泊的初值已科学验证。当前 build 的完整 UI 清单/五轮验收仍未完成，整条用户流程仍**未完成**。

### 2026-10-24 Sol：合成代理案例运行、2D/3D结果与剖面联动

- **代理（短程模型运行）**：在隔离副本 `build/parameter-roundtrip-proxy-20261024/Imported Random Lake` 运行前检查显示0条提醒，162湿格、2秒步长低于2.65757秒 CFL 估计上限、21个输出时步/13个变量预计约1 MB。启动后600/600步完成，用时约4.8秒，页面结果有效性检查通过；3个结果文件（2D、3D、`output.nc`）归档到该副本 `output/`。这是合成数据的工程运行代理，不是指定案例或科学验证。
- **代理（2D结果查看）**：新输出加载到2D视图，显示 Water temperature、单位 Celsius、初始时间2020-DOY001 00:01。点击“下一帧”后到00:02，页面显示色标数值范围随帧变化。
- **代理（3D结果与剖面）**：切至3D视图并推进到00:03；页面报告原始网格6×14×20、有效格162、湿格缺测0、几何缺失0，垂向剖面随同一变量/帧更新。此次未覆盖完整播放区间、导出与外部观测比较。
- **边界**：这补充了合成案例的“预检→启动→归档→2D/3D查看→剖面”片段。完整用户流程与当前build五轮验收仍**未完成**；四个指定湖泊科学验证不因此改变，均保持**未完成**。本次无产品源码更改。

### 2026-10-24 Sol：Lake Ravn 官方输入数据质量复核

- **来源与范围**：只读检查官方 QWET workshop 包的解压文件 `build/ravn-calibration-research-20261016/QWET_test_case_Lake_Ravn_workshop/`；原包清单记录下载源为 Aarhus WET 的 Lake Ravn workshop ZIP，SHA-256 `9a8767c2b5e235de268d31d1808220bcb062deb2704ef890b137827ef062a56b`。官方 WET 页面称 Ravn 长期监测自1989年开始，提供完整模型输入/校准操作示例（[Lake Ravn case](https://projects.au.dk/wet/cases)、[WET resources](https://projects.au.dk/wet/resources)）。
- **实测（气象与边界数据剖析）**：`CLIMATE/meteo_file.dat` 有359,297行、8列，无空值或重复时间戳；小时序列覆盖1979-01-01 07:00至2019-12-27 23:00。风分量范围 U10 −11.99…17.25、V10 −12.22…13.36m/s，压力948.46…1041hPa，气温−18.77…29.47°C，露点−19.71…20.56°C，云量0…1。`INFLOW/inflow.dat` 与 `inflow_chem.dat` 各696行、无空值/重复时间，覆盖1990-01-01至2018-12-31，断点成月度阶梯（每月起点和月末均列出）；流量0.1019…2.4644m³/s。化学列`sPDOMW`、`sNDOMW` 全零，其他给定列非负；全零是否为有意设定需以原配置/来源解释，不能自行改填。
- **实测（观测记录形状与异常）**：八个观测文件无解析失败，记录数范围1,420–11,904，日期从1971–2018，时间戳不带时区。`TEMP.obs` 有49个重复时间-深度键，其中19组数值冲突（53条重复行）；`DO.obs` 有40个重复键，其中14组冲突（44条重复行）；这些应按既有解析器冲突策略排除而不是平均。TEMP 中发现−0.2°C（1982-01-13、−0.2m）和72°C（2006-07-11、−14m）；磷酸盐和总磷观测含深度−99m标记。异常含义未由原 `.obs` 文件说明，保留审查诊断，不作自动修正或物理解释。
- **影响与结论**：这些数据可用于官方1D Ravn模型的来源绑定观测配对与质量审查；不自动构成当前 GETM 3D 的科学验证，也不解决校准日期、训练/独立验证划分、DO 物理红旗及大量 FABM 内态修复计数。Ravn 科学验证仍**未完成**，本次检查属于官方输入的**实测数据质量审查**，无求解器运行、无案例改写、无产品源码更改。

### 2026-10-24 Sol：桌面源码窗口重新启动与资源核验

- **实测（快捷方式与进程）**：按用户授权通过 `C:\Users\23801\Desktop\3DWET Studio.lnk` 启动。快捷方式目标为仓库 `.venv\Scripts\pythonw.exe`，参数 `3DWET\app\launcher.py --desktop`，工作目录为本仓库。当前进程窗口标题为 `3DWET Studio`，健康响应。
- **实测（桌面 WebView 服务资源）**：启动日志记载通知权限桥连接到 `http://127.0.0.1:64257`。该端点首页 HTTP 200，资源为 `app.js?v=68`、`i18n.js?v=7`、`viz3d.js?v=108`；逐项计算 HTTP 返回内容与仓库源码 SHA-256 一致（app `4DF0E939931636BC38D7345E8C24429FF785340EA58FFD43D7B6E82AE3899F6E`、i18n `21CD0BA196C71EF5E55F693A711C30708235E095187C04C07C9051DF54C9C3B4`、viz3d `F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`）。因此确认桌面快捷方式已连到当前仓库源版服务。
- **验收边界**：本机 UI 自动化未暴露原生窗口截图或 DOM；进程和 WebView 服务资源证明启动来源及服务内容，但不足以证明用户屏幕上最终绘制的所有像素或页面状态。黑色床面片仍**未修复**、根因**不确定**；用户反馈的旧版观察已记录，若重现仍需具体画面/地址来继续定位。无产品源码修改，本轮仅记录同步证据。

### 2026-10-24 Sol：Lake Ravn 当前 GETM 3D 就绪性集成复核

- **实测（来源快照完整性）**：独立对比 Luna 评估目录 `build/ravn-getm3d-candidate-20261024-luna01/source/` 中 27 个选定文件与官方解压源 `build/ravn-calibration-research-20261016/QWET_test_case_Lake_Ravn_workshop/`；逐项 SHA-256 与 manifest 相符，0 个不匹配。候选来源、清单及边界说明分别见 [assessment.md](../../../build/ravn-getm3d-candidate-20261024-luna01/assessment.md)、[source_manifest.json](../../../build/ravn-getm3d-candidate-20261024-luna01/source_manifest.json)、[readiness.json](../../../build/ravn-getm3d-candidate-20261024-luna01/readiness.json)。
- **结论（未完成）**：这证明输入快照可追溯，不证明模型案例可运行或科学有效。尚缺获批的类别水深转网格规则和 32/32.65m 配置选择、河口/出口空间映射与水量闭合、短波及降水三维强迫方案、旧版校准参数/状态迁移审查，以及观测站坐标/时区/网格映射。未生成 Ravn GETM 案例文件，未执行 preflight 或求解器。Lake Ravn 当前 GETM 3D 科学验证继续标记**未完成**；旧 1D GOTM-WET 配对仍只属工程代理。
- **后续边界**：上述空间和物理选择不能仅凭现有数据安全自动推导。等待对应的来源材料或明确方法输入期间，继续推进其他可独立完成的流程与案例；不把缺失选择写成测得事实。
- **Sol 官方来源补查**：Aarhus WET 的 [QWET 数据准备说明](https://projects.au.dk/wet/resources)明确把 `inflow.dat` 定义为整个系统的汇总流量；这解释了为何官方 1D 序列本身不含 GETM 的逐河口分配。Skanderborg Kommune 的[官方许可材料](https://www.skanderborg.dk/Files/Files/hoeringer-afgoerelser-tilladelser/2025/02-februar/Udledningstilladelse_%20udledning%20til%20Balleskov%20B%C3%A6k%20i%20udl%C3%B8b%20U123.pdf)描述了 Knudå 经 Veng Sø 流入 Ravnsø、再经 Knudå 流往 Knud Sø 的水系关系；它还提及多段上游水系，但没有提供 QWET 历史汇总流量在入湖口间的拆分、模型期流量时序配对，或可直接用于 GETM 网格的经核实边界坐标。由此能补足水系上下游背景，不能据此决定河流输入怎样映射到当前 3D 网格。

### 2026-10-24 Sol：桌面仍显示旧版后的重新绑定

- **实测（窗口重开）**：用户反馈桌面显示仍为旧版。确认桌面快捷方式目标是本仓库 `.venv\\Scripts\\pythonw.exe` + `3DWET\\app\\launcher.py --desktop`；正常关闭旧 WebView 主窗口后，通过该快捷方式目标重新启动，新窗口 PID 和启动命令均指向本仓库。
- **实测（当前服务）**：重开后 `http://127.0.0.1:64257/api/system/health` 返回 ready，model_root 为本仓库 `3DWET`；首页引用的版本化 app 脚本和静态资源与当前仓库一致。窗口资源更新核验不等同于对桌面最终像素的确认（本机 UI 通道没有原生窗口截图/DOM）。
- **同步状态**：桌面窗口已重新打开；尚未取得用户桌面的新截图确认可见画面是否已变为当前 UI。若仍显示旧版，需要用户提供当前桌面截图或窗口 URL/诊断信息，以区分另一个实例、缓存或不同安装包。

### 2026-10-24 Sol：第60轮合成完整工作流后端与当前桌面 UI 复核

- **代理（六个后端阶段）**：新鲜种子 `2026102405` 运行 `scripts/workflow_acceptance.py`，external、features、results、scipy、abc、restart 六阶段均通过，详见 `build/full-workflow-20261024-attempt60/round.json` 及各自的 `verification.json`。本轮工程数据是脚本生成的 synthetic realistic test data，不是观测数据或湖泊科学验证。
- **实测（当轮 UI 局部检查）**：在隔离 UI 根目录 `build/full-workflow-20261024-attempt60/ui-model-root` 打开当前源版服务。已通过工作台导航进入“前处理”，可见湖界、底部高程、网格生成、插值保存流程及 shapefile 上传/CRS 选择/边界预览控件；确认活动案例是 Imported Random Lake。仅检查了仪表盘与前处理边界输入页，未完成整份十项 UI 清单。
- **状态**：按验收脚本将第60轮记录为 **failed**，原因是十项 UI 证据不足；不得用后端六项通过冒充完整流程通过。`consecutive_complete` 未增加，指定四湖科学状态不变。
- **桌面同步实测**：使用 Computer Use 原生截图记录当前 `3DWET Studio` 窗口，见 `build/full-workflow-20261024-attempt60/desktop-current-render.png`。实际画面显示更新后的湖泊工作台布局、左侧分组导航、顶部工具栏、空间结果总览和右侧工作区检查器；当前案例为 Lake Dianchi。窗口已重开，画面与当前重设计方向相符。
- **缺陷状态**：此轮没有床面黑片的同帧复现/修复，不改写先前变量对照结论；黑片仍**未修复**，根因**不确定**。无产品源码修改，无桌面重启需求。

### 2026-10-24 Sol：按用户要求自行刷新桌面并完成可见画面核验

- **实测（桌面动作）**：使用 Windows UI 自动化选取唯一 `3DWET Studio` 原生窗口并执行 Ctrl+R 刷新。刷新后重新读取窗口无障碍文档与原生截图，窗口仍在 `http://127.0.0.1:64257/`，页面完整加载英文 “Lake model workbench” 首页及左侧流程导航、顶部工具栏、空间结果卡片、Workspace inspector。截图保存在 `build/full-workflow-20261024-attempt60/desktop-current-render.png`。该截图可用于与用户所说“老版本”进一步对照；本次核验所见是当前工作区重设计版本。
- **实测（服务源码一致性）**：页面包含 `i18n.js?v=7`、`app.js?v=68`、`ecology_network.js?v=26`。逐项比较 HTTP 返回文本与 `3DWET/app/static/js/` 下当前源文件 SHA-256，三项均一致：i18n `21CD0BA196C71EF5E55F693A711C30708235E095187C04C07C9051DF54C9C3B4`、app `4DF0E939931636BC38D7345E8C24429FF785340EA58FFD43D7B6E82AE3899F6E`、foodweb `674A56F24FD7076B12F20340758B70E034EACF5756BC458E7E780D4C2D5A1BAE`。
- **同步结论**：目前原生桌面显示与当前工作区源码同步，用户要求的自行刷新已完成。此前“桌面最终画面尚未确认”的状态被本次截图核验取代。没有产品源码改动。若用户口中的“老版本”指与其预期不符的某个具体控件/页面，请提供该页面截图或指出差异，以便对照其验收意图；当前屏幕本身可直接和用户桌面观察比较。
- **主任务状态**：本次只做刷新与只读验收。黑色床面片仍**未修复**、根因**不确定**；完整用户流程和四个湖泊科学验证仍**未完成**。代理输出不升级为实测科学结论。

### 2026-10-24 Sol：Erken 剖面初始化与首日垂向梯度只读诊断

- **实测（观测源）**：使用已溯源的 Erken SITES anchored temperature profile CSV 与其输入剖面快照（源 SHA-256 `c068995fb263cc0b7a6660ff5759ac2080ffd5bd1156c6884a2d6e58813c36e3`；元数据注明日均、UTC+1、50个深度样本、约1–15.5m）。湖站点坐标映射到此代理网格的最近水格 `(y=8,x=36)`，中心约102m远，案例该格深度约16.47m；此空间代表性仍属**代理**。
- **代理（模型输出）**：只读读取 `arms_168h_direct_swr_padding_verified/arm_A/case/output.nc`，变量 `temp` 为168小时×10层×18×44；首个输出记录为 2024-06-13 14:00（文件时间单位自 13:00 起一小时），最近站点格首帧水温从底至表约8.10至14.96°C；至第12帧（约12小时）垂向极差约0.25°C，第24帧（约24小时）约0.15°C。运行使用50深度观测配置文件作剖面输入，但输出为10层。该输出属于候选求解器代理运行且气象/生态输入含代理，不是现场验证。
- **实测—代理对比（非科学验收）**：将首个输出时刻的10个 `zc` 层中心按绝对水深线性插值到同一时刻输入的50点观测剖面，10点 RMSE约2.00°C、MAE约1.89°C。此仅为初始化/映射诊断：首个输出已距剖面配置时刻1小时，10层中心不等同传感器深度，源观测列实际深度可能随湖位变化；不得解释为正式日均观测配对或模型验证分数。
- **候选解释（不确定）**：早期梯度变弱与有限垂向层数、初值从50点映射到10层、动力混合或外部热强迫均相容，现有单次代理输出不能区分它们。需以相同几何和强迫建立初始化逐层对照、首个积分步前/后状态、逐时温度/混合诊断及未经代理的场地强迫，并在校正时区与传感器实际深度后按对应观测时间窗比较。未据此改参数或改源码。
- **状态**：Erken科学验证仍**未完成**；观测是**实测**，输出及对照运行是**代理**。黑色床面片仍**未修复**、根因**不确定**；全流程与其他案例状态不变。本次无产品代码修改，不需同步桌面。

### 2026-10-24 Sol：第60轮隔离案例结果视图工作流补充实测

- **实测（同一 UI 版本/数据集）**：在当前源版隔离服务 `http://127.0.0.1:61009/`，案例为 `Imported Random Lake`（脚本生成的合成工作流数据，不是观测或湖泊科学验证），从仪表盘逐步进入地图、2D、3D、垂向热图和时间序列页面；地图渲染18×14网格/150水格，2D和3D结果图正常显示，生成单点(12,10)温度垂向热图并从同一网格点提取温度时间序列。各页/操作的浏览器实际截图保存在本目录下 `ui-dashboard-current.jpg`、`ui-map-mode.jpg`、`ui-2d-mode.jpg`、`ui-3d-mode.jpg`、`ui-vertical-heatmap-generated.jpg`、`ui-timeseries-extracted.jpg`。
- **状态**：完整用户旅程结果模式分支的这六个页面环节为**实测 UI 工程交互**；本轮工作流 attempt60 的总体完整 UI 清单仍**未完成**，参数与初值保存重载、诊断修复重跑、率定 UI、重复结果处理、语言持久化、缩放/平移/全屏/导出及通知流程还未在同一轮全部验收。attempt60 的总体状态仍为 `failed`，六阶段后端代理成功不作完整流程通过。
- **科学状态**：所有图源自 Imported Random Lake 合成工作流，不作为四湖中的任何观测配对或科学验证。Erken/Lake Ravn/Bryrup/Arreskov 科学验证均**未完成**。黑片**未修复**、根因**不确定**，参考图仍 `（待补充：参考图的具体路径或链接）`。本次无应用源码更改；产品桌面服务无需同步。

### 2026-10-24 Sol：用户反馈桌面仍旧版后的源码桌面重新启动

- **实测（桌面进程）**：重新核查时，安装目录 `3DWETStudio.exe` 不在运行进程中。已从当前仓库执行 `.venv\Scripts\python.exe 3DWET\app\launcher.py --desktop`；出现窗口标题 `3DWET Studio`，窗口进程为 Python PID 55932，启动时间 2026-10-24 23:32:51（+08:00）。
- **实测（服务与源码）**：桌面启动器复用了 `http://127.0.0.1:64257`；`/api/system/health` 返回 `ready: true`，`model_root` 为本仓库 `3DWET`。桌面窗口实际指向该服务；首页引用 `i18n.js?v=7`、`app.js?v=68`，服务端 `app.js` 内容 SHA-256 `4DF0E939931636BC38D7345E8C24429FF785340EA58FFD43D7B6E82AE3899F6E` 与仓库文件完全一致。
- **状态**：源码版桌面窗口已启动并加载当前仓库页面；本轮 CUA 缺少原生窗口截图/DOM接口，因此无法核实用户可见像素是否已切换。若用户仍看到旧窗口，建议关闭旧窗后直接观察新开的 `3DWET Studio` 窗口；当前刷新截图可见的页面仍为 Lake model workbench 仪表盘。主任务仍未完成：黑片**未修复**且根因**不确定**；完整流程及四湖科学验证**未完成**，不把代理结果当作实测科学结论。

### 2026-10-25 Sol：隔离 UI 用户流程补充

- **代理（前处理 UI）**：在 `http://127.0.0.1:61009/` 的 attempt60 隔离模型根完成合成湖界 shapefile 导入（121 个点、1 个外环、UTM，约 816×602m）、测深 shapefile 导入（250 个点、显式 `depth` 字段、EPSG:32650、水深约 2.30–8.95m）、100m 网格生成（10×8、36 个湿格、0.360km²）、线性插值及保存加载。生成文件位于 `build/full-workflow-20261024-attempt60/ui-model-root/case/Imported Synthetic Boundary/bathymetry.nc`。输入来自脚本合成 `external_data`，只证明 UI 工程路径能走通，不作为任何湖泊的科学验证。
- **代理（语言、导出 UI）**：在同一隔离浏览器中用测试语言包 `ui-language-pack-fr.json` 导入并应用，将工作台首页两条消息显示为法语；页面刷新后自定义语言仍选中且翻译保留，之后恢复为 English。此验证仅针对隔离浏览器 profile。三维图导出按钮触发下载，PNG 长度 445,443 字节，副本为 `build/full-workflow-20261024-attempt60/ui-3d-export.png`。
- **未完成（总体验收）**：缩放/平移交互、导入网格/其它案例流程、诊断修复后真实重跑、率定 UI 与观测对比、结果重复项恢复/清理、ETA/完成/失败通知等仍缺同一版本/seed 的完整 UI 证据；不能将上述局部检查合并声称十项清单通过。attempt60 原始验收状态仍 `failed`。Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**；黑色床面片仍**未修复**，唯一根因**不确定**；参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：黑片 trace 运行时读取尝试

- **实测（当前浏览器状态）**：端口52862仍 ready，模型根目录为 `build/bed-black-userjourney-probe-20261024/model-root`。页面打开案例 `case`、temp frame19（2024-DOY166 09:00）、第9层、相机斜视34°；视图读数确认 376 个有效水格、10×18×44 原网格。临时对照为 200× 与相机位置+15%，随后恢复连续水体、自动倍率和位置0%。200×画面中床面主要呈浅灰/褐色，边缘可见暗色片段，但当前可访问画面没有稳定显示此前描述的成片黑色；这不能推翻历史复现。
- **实测（工具边界）**：只读读取 `#viz3d-plotly` 得到 `class="js-plotly-plot"`，但当前浏览器的只读 DOM evaluation context 中该元素 `Object.keys=[]`，`_fullData`、`_fullLayout` 均不可见；这只能说明此检查通道拿不到 Plotly 页面运行时对象，不代表 renderer 内不存在 trace 数据。未改源码、未据此作唯一根因判断。
- **状态**：动态属性、深度色带、Z 精度/投影、WebGL 深度和几何交互仍是候选解释。需在稳定重现的同帧/镜头/视角下取到页面运行时 trace 属性，并对照原始和压缩 Z 跨度；参考图仍为 `（待补充：参考图的具体路径或链接）`。黑片仍**未修复**，根因**不确定**。本次无产品代码变化。

### 2026-10-25 Luna / Sol：主变量画布与桌面英文标签同步

- **Luna 实现**：首页新增“主变量”选择器。当前选中的科学变量扩展为主空间画布，其余变量保留为次级预览；窄屏布局同步适配。新增 `en-US` 文案“Primary variable”及“Choose the dashboard primary result variable”，首页模板切换到 `i18n.js?v=8`，脚本和工作台样式分别使用 `app.js?v=69`、`workbench.css?v=3`。
- **代理（聚焦源码回归）**：`test_dashboard_primary_view.js`、`test_dashboard_primary_i18n.js`、`test_workbench_shell.js` 均通过；`app.js`、`i18n.js` 语法检查及英文 JSON 解析通过。这些检查覆盖选择器/文案和工作台结构，不证明案例科学结果或完整用户流程。
- **实测（桌面同步）**：服务 `64257` ready、run idle，`model_root` 指向本仓库 `3DWET`；原生 `3DWET Studio` 窗口重新启动并显示英文首页，实际窗口无障碍文档含 “Primary variable” 与 “Choose the dashboard primary result variable”，不再含这两个控件对应的中文原文。首页引用 `i18n.js?v=8`、`app.js?v=69`、`workbench.css?v=3`；服务端这四项（另含英文目录 `/static/i18n/en.json?v=20261025-primary-variable`）的 SHA-256 均与磁盘文件一致。截图由 Sol 在本轮窗口状态中直接检查。
- **状态边界**：UI 主变量突出显示及英文标签已落实到当前源码桌面；其余应用术语是否完全英文化未作全量验收。此 UI 工作不改变黑片结论（**未修复**、根因**不确定**），也不提升四湖科学验证或完整用户流程状态。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：总体目标证据状态重核

- **完整用户流程**：`build/full-workflow-20261025-attempt61/round.json` 记录 external、features、results、scipy、abc、restart 六个后端阶段通过，但总体状态为 `awaiting_ui`。现有隔离合成案例的页面/时间序列操作是局部 **实测 UI 工程交互**；它们不构成十项 UI 清单在同一版本、同一 seed 下全部完成。完整用户流程 **未完成**。
- **Erken**：SITES 温度记录/来源是 **实测** 数据；已存在的候选模型输出及部分比较来自代理强迫/初值的工程运行，按 **代理** 记录。完整、科学可接受的 Erken 验证仍 **未完成**。
- **Lake Ravn**：官方默认配置成功执行及初步观测配对有记录，但该比较是 **代理**，不是独立留出或已复现官方校准。科学验证 **未完成**。
- **Bryrup**：WET 1.0 与论文所述 Chen et al. 研究不是同一方案；可用的兼容性尝试在积分前失败，论文对应校准包/强迫仍缺。科学验证 **未完成**，不得用 WET 1.0 或通用 PCLake 例子替代并宣称原案例通过。
- **Arreskov**：目前为权威来源/配置可复现性审计；论文配置、匹配运行身份及成员数据仍缺，未形成目标案例的可验证模型输出。科学验证 **未完成**。
- **黑色床面片**：保留历史诊断路径的条件性复现与普通用户路径的负观察。床底图层、视角和垂向倍率与表现相关，但其独立因果、具体材质/遮挡/数值机制均仍 **不确定**；缺陷 **未修复**。参考图路径继续保留为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：用户反馈桌面仍旧版后的模板同步与导航修正

- **实现差距（Luna）**：动态“项目导入与物理设置”按钮原先插入不存在的旧式 `project` 分组，导致不在三个工作流阶段内。已改为插入“模型配置”分组；路由与页面行为不变，脚本缓存键更新到 `projects_studio.js?v=4`。对应回归用例先 RED 后 PASS。
- **实测（源码服务同步）**：发现 `64257` 原进程仍从已缓存的 Jinja 首页模板提供旧脚本引用 `projects_studio.js?v=3`，即便静态 JS 可更新读取。确认运行状态 `idle`、当前案例 Lake Dianchi、未发现求解器进程后，关闭旧空闲服务并以同一端口/同一仓库路径重启。新 health：`ready=true`、`model_root=...\\GETM-FABM-WET-260928\\3DWET`、新 PID `92916`。新首页引用 `i18n.js?v=7`、`app.js?v=68`、`projects_studio.js?v=4`；v4 服务返回 SHA-256 与源码相同：`39DEC0A3C6769D164910A4AD298EF10012E4C8C6CDEEAD354E9E8C17EE025A9E`。
- **实测（界面）**：新进程窗口标题为 `3DWET Studio`。刷新同一服务的浏览器页面后，DOM 确认项目工具按钮位于 `[data-group-items="configuration"]`，展开导航截图显示“Model configuration”下的该入口；新桌面样式首页宽屏截图 `build/ui-design-audit-20261025/dashboard-config-grouped.png`。因为本轮 CUA 不能读取原生 WebView 截图，原生窗口像素核验仍不充分；可确认的是新窗口进程已在模板重启后启动，且服务和可见浏览器页均为新模板。
- **验证**：`node 3DWET/tests/test_workbench_shell.js` PASS；`node --check 3DWET/app/static/js/projects_studio.js` PASS。仅此 UI 导航布局问题已修正；这不等于完整 UI 用户流程验收。
- **状态边界**：黑片仍**未修复**，根因仍**不确定**；完整用户流程与 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**。现有代理结果仍标为代理；参考图保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：桌面仍旧版反馈后的 WebView 强制刷新复核

- **实测（桌面服务）**：原生窗口连接 `http://127.0.0.1:64257/`；监听进程仍为仓库启动器 `3DWET\app\launcher.py --desktop --port 64257`，服务 HTML 引用 `app.js?v=70`、`i18n.js?v=9`。服务脚本字节哈希与源码一致：`app.js` `EE142CE1B6F1F0831A6C7C8AAAE0B8D2C6F48658427DC2777154633E11E084CF`，`i18n.js` `A17CFFCA2B65DF0127432643BD7E0F5B5478BA5AC84DF8DEDA71E5F980A0829C`。
- **实测（界面）**：强制刷新之前，64257 的桌面 WebView 无障碍树仍呈现旧侧栏结构；对两扇 `3DWET Studio` 桌面窗口执行强制刷新后，两者均显示英文 `Lake model workbench`、`Spatial results preview` 和 `Workspace inspector`。刷新后的画布首页截图由 Sol 在本轮原生窗口中检查；案例为现有 `Lake Dianchi`，不代表模型刚完成运行或案例科学验证。
- **状态边界**：桌面 WebView 现在已呈现当前首页源码，但这仅证明页面版本同步，不等于完整 UI 流程验收。黑片仍**未修复**且根因**不确定**；完整用户流程仍**未完成**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍各自**未完成**。参考图路径保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：attempt62 合成输入前处理 UI 实操

- **代理（真实 UI 工程交互）**：在 attempt62 隔离服务的原生窗口完成湖界上传（121 点、1 外环、0 洞、822m×611m、CRS utm）和测深 shapefile 上传（显式 `depth` 字段、250 点、EPSG:32650、水深范围 2.24–8.94m）；用 UI 默认线性插值与 100m×100m 单元生成 10×8 网格（80 格、38 湿格、0.380km²），插值完成后保存并加载 `Synthetic Workflow A62`，lake label 明确标作 `Synthetic workflow proxy`。保存路径在 attempt62 隔离模型根下的 `case/Synthetic Workflow A62/bathymetry.nc`。
- **记录**：UI 观察摘要及该检查的部分报告位于 `build/full-workflow-20261025-attempt62/ui/preprocess_upload_grid_save.txt` 和 `ui-report.json`。记录绑定 version `bc77f67b9944421470b71b059804608fdb7a19f0f6b5a2980770f94e21bee6d8`、seed `2026102503`。报告目前仅有第一项检查，尚未提交总体验收；其余九项 UI 检查仍未完成。
- **状态边界**：该回合使用脚本生成的合成湖输入，只是 UI 工程路径的**代理**，不构成实测湖泊数据，也不构成 Erken、Lake Ravn、Bryrup 或 Arreskov 的科学验证。完整用户流程**未完成**；四湖科学验证仍各自**未完成**；黑片仍**未修复**且根因**不确定**；参考图继续标记 `（待补充：参考图的具体路径或链接）`。
- **代理（参数/初值保存重载）**：同一 attempt62 合成案例 `Synthetic Workflow A62` 的“初始条件”页显示水位 0、水温 15°C；点击“保存到案例”后 UI 确认已保存，点击“重新读取”仍显示水温15°C。该路径与前处理证据已写入 `build/full-workflow-20261025-attempt62/ui/`，总检查仍只有已实际观察到的两项。

### 2026-10-25 Sol：用户重启授权后的正式桌面刷新复核

- **实测（界面）**：用户要求“自己来”后，对正式桌面服务 64257 的两个 `3DWET Studio` WebView 窗口分别执行 `Ctrl+F5`。两个窗口刷新后均显示英文 `Lake ecology · 3D modelling workbench`、`Lake model workbench`、`Spatial results preview`、`Workspace inspector` 首页内容；不再停留在旧食性网络页。
- **实测（服务）**：64257 仍由仓库 `3DWET\app\launcher.py --desktop --port 64257` 提供，HTML 引用 `app.js?v=70`、`i18n.js?v=9`。本次仅刷新页面，未更改源码。
- **状态边界**：桌面加载版本已复核；这不代表完整用户流程或四湖科学验证完成。黑色床面片仍**未修复**，根因**不确定**；四湖科学验证及完整用户流程继续按既有未完成状态记录。

### 2026-10-25 Sol：attempt62 UI 验收续测与桌面窗口复核

- **代理（校准 UI）**：在 `Imported Random Lake` 合成案例经 UI 导入 2 行合成温度 CSV，显示 2 对观测/模型值；SciPy L-BFGS-B（3 次评估）与 ABC-SMC（2 个种群、6 次评估）均完成，未应用最优参数。见 `build/full-workflow-20261025-attempt62/ui/calibration_import_compare_scipy_abc.txt`。
- **代理（结果文件与语言 UI）**：UI 扫描并识别 1 组完全相同结果副本，将副本移入可恢复回收区后恢复，最终回收区为空。自定义语言包导入、应用、重载后仍选中 `A62 Test Français`。见对应 `result_files_duplicates_cleanup_restore.txt`、`language_import_switch_persistence.txt`。
- **代理（图形控件/导出，部分完成）**：二维图放大、复位、宽高 1100×600 调整及 Fit to window、全屏进入/退出均在合成案例 UI 操作并确认；导出产生 100,932 字节 PNG：`build/full-workflow-20261025-attempt62/ui/exported-2d-temperature-a62.png`。中键平移和 Ctrl+滚轮应用缩放未核验，因此该项仍未完成。
- **代理（ETA/完成/失败通知，部分完成）**：运行前体检 0 条提醒；155 水格、2 秒步长小于 2.68459 秒重力波 CFL 估计上限、预计约 21 个输出时步。一次合成 UI 运行到 600/600（100%）并显示完成，运行时 ETA 显示 0.0 min。完成后出现系统通知权限提示；用户选择尚待回复，未点允许或拒绝；失败通知未触发。FABM 状态汇总仍为“未提供”，此运行不构成科学验证。见 `eta_completion_failure_notifications.txt`。
- **同一版本 UI 清单**：attempt62 报告绑定 version `bc77f67b9944421470b71b059804608fdb7a19f0f6b5a2980770f94e21bee6d8`、seed `2026102503`。10 项中 8 项记为已完成（全部为合成代理 UI 证据），第 9、10 项仍 `passed=false`；未运行总体验收 review，也不声称完整流程通过。详见 `build/full-workflow-20261025-attempt62/ui/ui-report.json`。
- **实测（桌面窗口）**：重新列出同名桌面窗口并逐个读取 WebView 可访问内容后，仓库桌面 64257 的两个窗口均为 `http://127.0.0.1:64257/`，展示英文 Dashboard 新首页；attempt62 独立测试窗口为 `http://127.0.0.1:57176/`。当前已将 64257 正式仓库窗口置前，前台显示 `Lake Dianchi`。首页引用 `app.js?v=70`、`i18n.js?v=9`，服务脚本哈希与源码一致。截图：`build/full-workflow-20261025-attempt62/ui/desktop-current-64257.png`。独立旧 web 服务 52862 的 `app.js?v=68`、`i18n.js?v=7` 不等同于本次核验的 64257 桌面窗口。
- **状态边界**：桌面同步已实测；完整用户流程仍**未完成**。Erken、Lake Ravn、Bryrup、Arreskov 科学验证各自仍**未完成**；代理输出没有改标为实测。黑色床面片仍**未修复**，单一根因仍**不确定**；参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：黑色床面证据矩阵整理

- 已将现有浏览器观察按湖底图层、颜色编码、视角和 VE 整理为 [证据矩阵与区分性验证](black-bed-cause-matrix.md)，并列出尚未证实的候选解释与单变量验证步骤。
- 诊断色彩 A/B 不直接等同生产路径；近期普通路径的负观察不构成修复证明。黑片仍**未修复**、根因仍**不确定**；参考图路径仍为 `（待补充：参考图的具体路径或链接）`。
- 本轮仅更新审计文档，没有修改代码或案例数据；桌面应用同步不适用。

### 2026-10-25 Sol：attempt62 UI 第9项图形交互补验

- **代理（合成 UI 流程）**：在隔离 Chromium 上打开 57176 的 `Imported Random Lake` 2D 页面。中键拖动使 `viz2d-canvas` 变换从 `translate(0px, 0px) scale(1)` 变为 `translate(68px, 42px) scale(1)`；“Restore full figure extent”恢复原位。按住 Ctrl 使用滚轮将界面比例从100%变为105%，Ctrl+0恢复100%。之后视图和平移、界面比例均回到基线。
- **版本绑定**：`round.json` 中 `app.js`、`view_controls.js`、`scientific_heatmap.js` 与 `index.html` 四项SHA-256均与当前服务页对应源文件相同。截图见 `build/full-workflow-20261025-attempt62/ui/pan-ctrlzoom-reset-final.png`。
- **验收更新**：`ui-report.json` 的 `ctrl_zoom_resize_pan_fullscreen_export` 从 `passed=false` 更新为 `passed=true`。该检查现已包含先前完成的缩放/复位、尺寸/适配、全屏和PNG导出。本轮为合成案例交互，状态仍为**代理**，不构成湖泊科学验证。
- **整体状态**：attempt62 十项中目前9项通过，`eta_completion_failure_notifications` 仍未通过；完整用户流程**未完成**，四湖科学验证均未完成。没有修改产品源码，桌面同步不适用。

### 2026-10-25 Sol：attempt62 失败状态提示隔离模拟

- **代理（客户端状态处理）**：在另一个隔离 Chromium 会话中仅拦截 `/api/run/status` 返回合成 `failed` 状态，没有调用运行/停止 API，也没有改变求解器状态。前端 `pollRunStatus()` 把页面状态切至失败，渲染模拟错误日志并显示“模型运行失败”的站内 toast；`Notification` API 在此上下文不可用，未改动原生 WebView 的通知权限选择。证据见 `build/full-workflow-20261025-attempt62/ui/failed-status-toast-simulated.txt` 及同目录截图。
- 这仅确认模拟状态下的客户端站内回退，不是实际求解器失败，也没有确认原生系统通知送达，因此十项验收第10项仍为**未完成**，完整用户流程仍**未完成**。四湖科学验证状态不变，均为**未完成**。

### 2026-10-25 Sol：Lake Ravn 官方上游率定配置长程运行复核

- **实测（上游运行执行）**：在独立目录用官方 `gotm_release.exe`、官方默认 Lake Ravn 输入包与从官方率定配置包取出的 `gotm-all_obs`/`fabm-all_obs` YAML，运行 1990-01-01 至 2005-12-31。进程退出码 0，NetCDF 有 5,844 日输出、33层；`temp`、DO、CHLA、NO23、NH4、PO4、总N、总P对应输出字段在全时空网格均为有限值。版本、输入/输出 SHA 和日志见 [Lake Ravn 上游运行审计](../lake-ravn-calibrated-upstream-run-20261025.md)。
- **未完成（科学验证）**：输出 `output.nc` 中 CHLA/TOTN/TOTP 为 `wet_*` 名称，而同目录 `wet_obs.xml` 指定的是不存在的 `pclake_*` 名称；总N和总P输出单位属性为空。未擅自更名评分，未生成新的观测误差指标。并且该执行是官方 GOTM-WET 一维上游参考二进制，不是本仓库目标 GETM 3D 应用。
- **未完成（输出质量）**：日志报告 FABM interior state repairs 249,644 次，surface/bottom 各0次。需按时间和状态变量解释修复频率并核对总量定义后，再讨论物理可信度。
- **Lake Ravn 状态**：本次属于一次可复核的**实测上游执行**，但指定案例的科学验证继续为**未完成**。Erken、Bryrup、Arreskov仍各自**未完成**；完整用户流程仍**未完成**；黑色床面片仍**未修复**且根因**不确定**；参考图仍为 `（待补充：参考图的具体路径或链接）`。此前标为代理的结果保持**代理**。

### 2026-10-25 Sol：Bryrup / Arreskov 官方版本材料追溯

- **实测（来源核对）**：WET 1.0 论文将 Lake Bryrup 设置说明为：六年 spin-up、1996–2004 校准、2004–2006 验证；比较量包括温度、溶解氧、无机营养盐、总氮/总磷和叶绿素 a，观测来自丹麦 NOVANA。论文描述的是作者已校准的一维 GOTM–WET 研究结果，不是当前 GETM 3D 项目的验证结果。来源：[Schnedler-Meyer et al. 2022, WET 1.0](https://gmd.copernicus.org/articles/15/3861/2022/)。
- **实测（官方档案目录核对）**：Zenodo WET v0.1.0 记录（DOI `10.5281/zenodo.4903142`）的公开 ZIP 预览列出 `testcases/lake_bryrup_denmark`，含 GOTM/FABM YAML、hypsograph、气象、入流/水质、出流和输出配置；预览没有该案例的 NOVANA 观测文件，也没有列出 Arreskov 目录。来源：[Zenodo WET v0.1.0 文件目录](https://zenodo.org/records/4903142)。当前本地官方 testcase 快照中的 Bryrup `gotm.yaml` 仍仅覆盖 1990–1995 热身；因此拥有强迫与配置文件不能替代论文校准/验证期的观测配对或复现校准。
- **Arreskov 版本差异（不确定）**：Andersen et al. 2022 论文写明 Arreskov 案例在 WET repository，并引用 WET v0.1.0；但 Zenodo v0.1.0 ZIP 预览只显 Bryrup testcase。当前官方 master 本地快照含 Arreskov GOTM 与强迫文件但无 `fabm.yaml`；v0.2.0/v2.3 归档的既有审计也未找到匹配配置。由此可确认各检查归档之间不一致，不能确认缺失文件是否存在于某个单独 GitLab release/supplementary 包。来源：[Andersen et al. 2022 Arreskov 论文](https://doi.org/10.1016/j.envsoft.2022.105501)。
- **状态**：Bryrup 科学验证仍**未完成**；已有官方强迫/配置与既有兼容性尝试均不得说成已验证，任何短试跑仍标**代理**。Arreskov科学验证仍**未完成**；未推造 `fabm.yaml`。Erken与Lake Ravn状态不变，完整用户流程仍**未完成**；黑片仍**未修复**、根因**不确定**；参考图继续保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：桌面仍旧版反馈后的当前源页复核

- **实测（源服务）**：从仓库桌面快捷方式重新启动后，桌面标题进程 PID 76964 提供 `http://127.0.0.1:63900/`；健康检查 `ready=true`，model root 指向本仓库 `3DWET`。首页实际引用 `i18n.js?v=10`、`app.js?v=70`、`ecology_network.js?v=28`。另一个旧 web-only 端口 52862 仍返回 i18n v7 / app v68，不能作为本次桌面源版本证据。
- **实测（用户可见页面）**：在当前 Codex 桌面会话中将 63900 源页置于可见页签，实际 DOM 显示英文 `Lake model workbench`、`Spatial results preview`、`Workspace inspector`，并显示当前 Lake Dianchi 案例；截图可见浅色画布优先首页和主变量选择器。此项只确认打开的源页 UI，不等同于科学验证或完整用户流程。
- **同步边界**：本机当前有多个同名 `3DWET Studio` 窗口进程；CUA 运行时没有原生窗口枚举/读取方法，故无法把每个原生窗口与服务端口逐一对应。本轮没有把“源服务版本正确”夸大为所有原生窗口均已核实。桌面应用仍有新版仓库窗口在运行。
- **总目标状态**：黑色床面片仍**未修复**，根因**不确定**；完整用户流程与 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍各自**未完成**。已有代理结果仍为**代理**，参考图路径保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：用户“自己来”后的桌面版本同步复核

- **实测（桌面启动与服务）**：按用户要求，从仓库桌面快捷方式正常关闭并重开 Studio。新桌面启动器 PID 86228 / 服务进程 PID 93656，服务 `http://127.0.0.1:61310/` 返回 HTTP 200；首页引用 `i18n.js?v=14`、`app.js?v=71`、`ecology_network.js?v=28`。三个在线 JS 的 SHA-256 与本仓库对应源码一致。
- **实测（当前源页）**：在 61310 页面应用 English 后，首页显示 `Lake model workbench`、`Spatial results preview`、`Workspace inspector` 与 Lake Dianchi 状态。已知桌面启动器与新服务同一启动实例；由于本机 CUA 未提供原生窗口枚举/截图，本项以实际启动的桌面服务及其可见源页核验，不声称读取了原生 WebView 截图。
- **旧服务辨别**：另有旧 web-only 进程 PID 65980 仍监听 61009，返回 `i18n.js?v=7` / `app.js?v=68` / `ecology_network.js?v=26`。这与新桌面实例不同；旧服务仍在运行，因此若切到指向 61009 的旧浏览器页，仍会看到旧版。最新桌面启动实例已指向 61310。
- **状态边界**：此次仅核对并重启桌面应用，未改源码或案例数据。完整用户流程仍**未完成**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍逐项**未完成**；黑色床面片仍**未修复**，根因**不确定**；参考图仍为 `（待补充：参考图的具体路径或链接）`。已有代理结果保持**代理**。

### 2026-10-25 Sol：四湖官方观测来源元数据续核

- **实测（来源元数据核查）**：新增 [四湖观测来源核查](target-lake-observation-sources-20261025.md)：Erken 有 SITES 2012 温度剖面与 1991–2017 GEISHA 测站数据目录；AU WET Lake Ravn 页面继续提供官方 1D 案例包入口；Bryrup WET 论文记录 NOVANA 对温度、DO、NO3、NH4、PO4、TN、TP 和 CHLA 的月度至半月度观测；Arreskov 研究记录湖内化学/生物采样及支流流量/营养盐监测。丹麦 Arealdata VanDa 湖泊水化学目录含 CSV 提取入口。
- **未完成（科学验证）**：来源目录存在不等于本地观测文件已下载、质量筛选、站点/变量/单位与模型输出配对，也不等于训练/留出期可复现。Erken、Lake Ravn、Bryrup、Arreskov 科学验证继续逐项**未完成**，代理结果继续标作**代理**。
- **其他状态**：attempt62 由于代码版本变化已按验收脚本记为 failed；attempt63（seed `2026102504`）正在执行当前源码绑定的隔离后端工作流，尚未完成 UI 验收，不能算完整流程通过。黑色床面片仍**未修复**、根因**不确定**；参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：当前 v109 同数据 Erken frame19 床面复核

- **实测（代理案例的浏览器渲染）**：从当前仓库源码启动隔离服务 `127.0.0.1:53308`，model root 独立于桌面 Lake Dianchi，并通过只读 junction 复用 `Erken 20-frame historical readonly` 案例数据；服务首页 HTTP 200，引用 `viz3d.js?v=109`、`i18n.js?v=14`、`app.js?v=71`。该案例输出为 20 帧 `USER_JOURNEY_ERKEN_IMPOR_WET`，网格 10×18×44、376 个湿格、10 层。
- **实测（基准组合，黑片未复现）**：`temp`、frame19（2020-DOY001 02:00）、连续水体、岸陆示意开启、镜头 +34°、模型位置 +15%、垂向 200×、水面动态变量叠层开启。原生浏览器画面显示蓝色温度面、灰色湖底/岸陆与蓝青侧壁；未见历史记录中的近黑色下侧大片。固定其余条件仅把镜头仰角改为 +60°，也未见黑片。
- **实测（单因子图层对照）**：返回 +34°、200×、frame19 后，仅关闭“水面显示所选变量”切到静态 `bathymetry.nc` 地形预览；床面显示蓝青地形色面与可见侧壁，未见近黑色大片。动态叠层组合与静态地形组合本轮均为负观察；这只说明当前 v109 及此代理案例条件未复现，不推翻旧版本/旧环境的浏览器记录，也不证明已修复。
- **实测（只读 trace 审计）**：动态叠层下“湖盆水深”床面为可见 `mesh3d` trace，使用 vertex intensity 和蓝青深度色标；在 200× 的床面 z 范围约 −3693.57 至 −199.60，1504 个顶点、752 个三角面，x/y/z、i/j/k、intensity/customdata 均未见非有限值。照明参数为 ambient 1、diffuse/specular 0。该审计不覆盖 GPU 深度缓冲、三角绕序在目标 GPU 上的结果、WebGL 栅格化或底面与其它图层的屏幕空间遮挡，不能据此排除这些候选。
- **结论与状态**：本轮没有生产源码修改。黑片仍**未修复**，根因仍**不确定**；材质/颜色路径、几何/绕序、深度精度/投影、图层遮挡等继续作为待区分候选，不宣称唯一根因。需用户稳定复现条件下的截图/操作记录和相同浏览器/GPU 环境，继续做固定帧/网格/镜头/倍率的单变量比较。Erken 科学验证仍**未完成**，此输出/渲染仅为**代理**；完整流程与 Lake Ravn、Bryrup、Arreskov 验证状态不变；UI 参考图路径继续保留 `（待补充：参考图的具体路径或链接）`。当前桌面 Lake Dianchi 没有切换，仓库桌面服务仍由 PID 73120 提供 v109。

### 2026-10-25 Sol：Erken 观测配对更正与当前工作流/桌面源核验

- **实测（数据来源与正式求解器输出）**：本地隔离 Erken 案例已包含 SITES 当前版 2017–2025 温度剖面 CSV；文件 SHA-256 与 provenance manifest 一致。已找到正式 GETM 求解器的既有 120,960 步、168 帧输出并对照 SITES 实测剖面，未重新运行模型。300 个深度配对的生产输出诊断为 bias +0.4767 °C、RMSE 4.0305 °C、MAE 3.7752 °C；该输出的强迫和初始生态状态仍含代理项，故对照仍标**代理**，Erken 科学验证仍**未完成**。完整方法、逐日梯度及时间限制见 [Erken 2024 配对诊断](../erken-2024-observation-pairing-feasibility-20261025.md)。温度 CSV 是日日期而非日内时刻，源数据注明 UTC+1、模型时区尚未对齐。用户已授权接受 SITES CC BY 4.0 许可并下载 2017–2024 数据；因仓库已有校验匹配的新版文件，本轮无需重复下载旧版。
- **未完成（完整用户流程）**：attempt63（seed `2026102504`）状态文件现为 `failed`，原因是 UI 观察后源码指纹变化。attempt64（seed `2026102505`）状态仍为 `awaiting_ui`，既有检查为合成代理且尚缺应用 Ctrl+滚轮缩放、原生桌面窗口尺寸变化及失败通知，因此不得算作完整用户流程通过。后续若启动新案例/工作流，先按用户要求检查并清除明确不再需要的先前生成案例；本轮没有新建案例或启动求解器，也没有删除被审计记录引用的输出。
- **实测（桌面源同步）**：复用已运行的 `http://127.0.0.1:52812/` 服务，健康检查指向本仓库 `3DWET`，PID 2980、ready。当前 HTML 加载 `app.js?v=72`、`i18n.js?v=14`、`viz3d.js?v=119`、`ecology_network.js?v=28`；四个 served asset 的 SHA-256 均与当前工作区文件一致。未另开应用窗口或切换桌面案例。该服务核验只证明源码同步，不证明完整流程或案例科学验证。
- **总目标状态**：黑色床面片仍**未修复**、唯一根因仍**不确定**；完整用户流程仍**未完成**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍逐项**未完成**；代理诊断继续标为**代理**。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：当前服务源码指纹与桌面监听核验（只读）

- **实测（服务源码同步）**：复用已有 `http://127.0.0.1:52812/`，GET 首页返回 HTTP 200，HTML 声明 `app.js?v=72`、`viz3d.js?v=119`、`ecology_network.js?v=30`、`i18n.js?v=14`、`scientific_workspace.js?v=18` 与 `academic_ui.css?v=6`。按原始响应字节下载并计算 SHA-256 后，上述六个文件均与当前工作区对应源码匹配。`/api/case/current` 返回 Lake Dianchi、generation 1、仓库案例路径且有既有结果；本轮未切换案例。
- **实测（服务类型）**：PID 2980 命令行为 `launcher.py --web --no-open --port 52812`。只读检查所有 Python 进程监听端口后，已发现的 launcher 服务均为 `--web`，未发现 `--desktop` 监听实例。CUA 仍只列出已有的 52812 IAB 页签；未刷新或打开新页签。
- **边界**：这证明 52812 当前服务在提供与源码一致的最新版资产，但不证明已有浏览器 DOM 已加载这些版本，也不证明原生桌面 WebView 已刷新。因本轮没有代码或案例更改，未启动/重启桌面应用；用户要求避免重复打开并关闭此前启动的应用，本轮遵守该约束。完整用户流程、四湖科学验证及床面缺陷状态均未因此改变。

### 2026-10-25 Sol：Erken frame19 床面代理几何统计

- **代理（API/当前源码算法的几何检查）**：复用既有只读 Erken 20 帧案例和 59467 服务，没有启动求解器。对 frame19 的抽样 `1×18×22` / 原始 `10×18×44` API 网格按当前源码床面角点算法重算：168 个采样湿格、336 个三角面、0 个退化面，所有面 z 向法向一致。具体深度和范围、版本标签与 SHA 边界见[黑片证据矩阵](black-bed-cause-matrix.md)。
- **状态边界**：这是代理输出的几何统计，不是浏览器 `_fullData`、GPU 栅格或原始问题视口的渲染复现。黑片仍**未修复**、根因**不确定**；没有生产代码更改、模型运行或新建案例，因此无需同步桌面或清理案例。

### 2026-10-25 Sol：Erken 历史温度剖面许可接受与归档

- **实测（来源/许可/文件校验）**：按用户明确授权，在 SITES 官方页面确认 CC BY 4.0 数据政策并通过许可接受入口下载旧版 Erken 日温度剖面（2017-06-29–2024-09-14）。ZIP 1,321,235 bytes，SHA-256 `498e7f45476188a4643c620f233abd63bd5fa158c7bda99d82479415a91c746e`；内部 CSV 1,245,898 bytes，SHA-256 `5f04df11af21be20e82ff4c4841098164b7dda9e3b0d71c16e7186a44c668ef7`，与 SITES 元数据一致。来源：[SITES 历史数据记录](https://meta.fieldsites.se/objects/XwTfEa8hviDoL_TEhBCYFkt9)；许可：[SITES CC BY 4.0 数据政策](https://data.fieldsites.se/licence)。
- **归档位置**：`build/source-downloads-20261025/SITES_TW-PROF_ERK_LRK_20170629-20240914_L2_daily.zip`，来源、许可和校验信息见同目录 `erken-2017-2024-provenance.json`。不重复展开为案例副本；模型配对仍使用隔离案例中已经存在且覆盖至 2025-11-30 的当前版 SITES 文件。
- **状态边界**：这确认官方实测数据来源及文件完整性，不代表模型通过科学验证。Erken 科学验证仍**未完成**；既有模型配对仍为**代理**。本轮无生产代码、无新案例/求解器运行，因此无需桌面同步或清理案例。

### 2026-10-25 Sol / Luna：食性路径聚焦交互实现与验收

- **代理（合成配置 UI harness）**：Luna 将已解析的三实例/两边路径卡片改为可键盘操作的焦点按钮；激活后高亮恰好对应的 3 个实例节点、2 条配置边和关系表行；再次激活或 Escape 清除高亮。没有修改 FABM 数据、案例或模型状态，也没有把配置连线说成运行时摄食。
- **实测（聚焦测试）**：Sol 独立逐个运行 4 个网络相关 UI 套件，4/4 通过；`node --check 3DWET/app/static/js/ecology_network.js` 通过。细节和回归断言在 [test_ecology_foodweb_ui.js](../../../3DWET/tests/test_ecology_foodweb_ui.js)。
- **同步核验**：当前 `127.0.0.1:52812` 仍是仓库 `launcher.py --web --no-open` 服务，模型状态 `idle`。服务返回旧查询串 `ecology_network.js?v=30` / `scientific_workspace.css?v=11`，但分别取回的原始响应字节与当前源码 SHA-256 匹配，且 `Cache-Control: no-cache, max-age=0`。源码模板已更新到 v31/v12；运行中的服务响应 HTML 仍是加载前缓存模板，故这只证明当前服务取用已同步的代码文件，不证明当前浏览器 DOM 或原生桌面 WebView 已加载路径聚焦交互。遵守用户不重复打开 APP 的要求，没有刷新、打开或关闭任何 APP/标签页。
- **状态边界**：交互行为在合成 UI harness **代理**通过；真实湖泊案例食性模型含义仍未据此验证。桌面可视验收、完整用户流程、Erken/Lake Ravn/Bryrup/Arreskov 科学验证仍分别**未完成**；黑色床面片仍**未修复**且根因**不确定**。参考图仍为 `（待补充：参考图的具体路径或链接）`。本轮没有创建案例或启动求解器。

### 2026-10-25 Sol / Luna：床面色标域修正与图标总审

- **实测（UI图标审计）**：现有 `StudioIcons` 提供58个 SVG 符号及58个标准路径映射；专项测试核验图标引用、统一线性绘制属性，以及 app 模板/脚本无 emoji 或旧式 Unicode pictogram 残留。修正了一处导航测试过期版本断言（`ecology_network.js?v=31`），产品图标文件未改。测试 `test_studio_icons.js` 1/1、`test_app_ecology_nav_compat.js` 3/3。
- **实测（床面显示候选修正）**：Luna 将床面深度网格的 `cmin/cmax` 固定为 `0..最大水深（米）`，科学变量 trace 保持所选变量色标范围；新增红绿测试先复现错误继承变量的 `10..25` 范围，再验证床面 `0..8 m`。`test_lake_display_mesh.js` 51/51、`test_viz3d_waterbody_patch.js` 3/3，JS语法检查通过。
- **实测（同步）**：仅复用原有 `127.0.0.1:52812` 标签刷新一次；页面恢复显示 Lake Dianchi 仪表盘。服务对 `viz3d.js?v=121` 返回字节 SHA-256 与工作区源码一致；HTML 模板响应仍带旧查询标签，因服务模板缓存，无法从版本串确认 native desktop WebView；只读窗口清单没有运行中的 native app，本轮未启动新窗口。尚未检查新色标修正的用户黑片画面。
- **结论边界**：该修正纠正床面米制色标域，但当前高 VE 常规调用传入空 style，不能据此声称它解决历史黑片。黑片仍**未修复**、根因仍**不确定**；frame19匹配视口与完整运行时 trace 仍缺。完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**。本轮未创建案例或启动求解器，也未清理审计记录引用的既有案例。
- **追加的历史渲染复核**：同一存档 06:00、9/9层、166.5× 画面中，改变温度自动色标范围前后黑色三角区域仍在，flatshading 试验截图亦仍见黑面。该观察说明这两项单独调整不足以作为修复；它不是当前源码匹配复现，也不足以指认根因。详见 [黑片证据矩阵](black-bed-cause-matrix.md)。

### 2026-10-25 Sol：三角网表达力与学术 UI 复核

- **设计参考复核**：重新核对官方 [ParaView 显示属性文档](https://docs.paraview.org/en/latest/UsersGuide/displayingData.html)、[napari 图层文档](https://napari.org/stable/getting_started/layers.html)、[QGIS 3D 地图文档](https://docs.qgis.org/3.44/en/docs/user_manual/map_views/3d_map_view.html) 与 [Matplotlib 色图指南](https://matplotlib.org/stable/tutorials/colors/colormaps.html)。采用理由与产品取舍见[设计方案](../../superpowers/specs/2026-10-25-restrained-scientific-3d-design.md)：控件保持低彩度，模型场颜色与定量图例保持独立；图层/表示、相机/倍率分组显式可控。
- **代理（代码结构审查）**：Luna 检查当前 3D 渲染代码后未发现可由现有渲染证据支持的安全改动，因此未改生产代码。当前渲染已有派生三角网边、分层线色、层间显示连接和可选节点，节点默认关闭；UI 明示三角拓扑和显示偏移不属于求解器原生几何/物理量。
- **代理（回归测试）**：Luna 的网格专项 `test_lake_display_mesh.js` 为 51/51 通过；Sol 独立运行 `test_lake_display_mesh.js`、`test_ecology_foodweb_ui.js`、`test_academic_visual_system.js`、`test_studio_icons.js`、`test_app_ecology_nav_compat.js` 与 `test_viz3d_waterbody_patch.js`，共 62/62 通过。测试验证网格构造、图层分离、字段值不变、食性路径聚焦、主题色和图标结构；不能证明实时 GPU 画面中的三角线视觉清晰度。
- **未完成（视觉验收）**：本轮未刷新/打开桌面应用或新标签，遵守用户“不要重复打开 APP”的要求。存档桌面截图不是当前 3D 三角网视口，因此不能代替当前桌面应用中的视效核验。下一步需要在现有可见工作台中审看 3D 三角网，不另起窗口。
- **状态边界**：无生产代码、案例数据或求解器运行变化，桌面同步无需触发。黑色床面片仍**未修复**，唯一根因**不确定**；完整用户流程仍**未完成**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍分别**未完成**；已有代理结果保持**代理**。参考图继续保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Luna：三角网首次默认与属性栏结构回归

- **实现**：将三角网显示偏好键从 v1 升至 v2；首次进入按模板默认显示三角剖分，旧 v1 的连续曲面/隐藏网格偏好不再覆盖该默认；用户在 v2 主动切换后仍跨页面保存。`index.html` 中偏好脚本查询串由 v2 升至 v3。求解器数据、变量值和网格拓扑未改。
- **测试与纠正**：新增旧偏好迁移回归；将 `test_viz3d_responsive_layout.js` 中已过时的“设置控件 DOM 顺序必须早于绘图区”断言，改为检查已批准的相邻属性栏结构（画布与设置栏同处 `.sw-main`，网格/岸陆控件唯一且位于设置栏）。Luna 报告三项 59/59；Sol 独立运行偏好、网格、响应式、食性网络、学术 UI、图标、导航兼容及水体播放套件，共 70/70；脚本语法检查通过。
- **实测（服务同步边界）**：现有 52812 服务 HTTP 200、`ready=true`、model root 指向本仓库，活动案例仍为 Lake Dianchi。`viz3d_mesh_mode_preference.js?v=3` 响应 SHA-256 与源码一致（`0f0d1710c157dad0fd8be3944910256fc31379e6449c70edbec2f048cdf5b3e7`）；但该进程缓存的首页模板仍引用 v2。遵守用户不重复打开/刷新 APP 的要求，未重启服务或刷新现有页面；因此静态资产同步已核实，页面模板与可见 DOM 的升级尚未核实。
- **状态边界**：没有新建/删除案例，没有启动求解器。黑色床面片仍**未修复**、根因**不确定**；三角网当前桌面视效尚**未完成视觉验收**；完整用户流程与 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍分别**未完成**；代理输出继续标为**代理**。参考图仍保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：Erken SITES 当前观测源与许可核验

- **实测（许可与来源）**：按用户明确授权，通过 SITES 官方页面的许可接受入口接受 CC BY 4.0 数据使用说明，并下载当前版 Erken 日温度剖面数据（2017-06-29–2025-11-30）。数据集引用为 Erken Laboratory (2026), PID `11676.1/wGiZX7JjzAt6ZmD_V1msIID_`；记录注明日频、UTC+1，51列（日期加50个深度温度变量）、3,077条记录。文件 SHA-256 `c068995fb263cc0b7a6660ff5759ac2080ffd5bd1156c6884a2d6e58813c36e3` 与官方元数据一致。来源：[SITES 当前数据记录](https://meta.fieldsites.se/objects/wGiZX7JjzAt6ZmD_V1msIID_)；[CC BY 4.0 数据政策](https://data.fieldsites.se/licence)。
- **实测（已有案例输入一致性）**：下载文件与隔离案例 `Erken_real_20200101_24h_stage/Input` 中已存在的同名观测文件字节相同，SHA-256 一致；本轮下载的临时重复归档及解压副本已清理，没有改动案例输入。
- **状态边界**：该来源核验不等于独立模型科学验证。既有正式 GETM 输出的配对结果仍为**代理**，受代理强迫/生态初值及模型时区未对齐等限制；Erken 科学验证仍**未完成**。本轮未创建或删除案例、未运行求解器，也未打开或刷新桌面应用。

### 2026-10-25 Sol：桌面服务与丹麦公开站点 API 复核

- **实测（服务同步）**：复用中的 `127.0.0.1:52812` 服务 HTTP 200，`/api/run/status` 为 idle，活动案例 Lake Dianchi；进程以 `launcher.py --web --no-open --port 52812` 运行。工作区模板为 `viz3d_mesh_mode_preference.js?v=3`，服务根页仍返回 `v=2`。同端口重启命令被本机策略在创建 PowerShell 进程前拒绝，命令未执行、现有服务未改变；没有另起服务、窗口或标签。桌面页尚未同步到 v3。
- **实测（官方 API 访问范围）**：Kemidata 官方 SPA 配置将水文查询指向 `https://vandah.miljoeportal.dk/api`。匿名 `/stations` 返回3,015条站点目录记录；其中当前 `Arreskov Sø` 记录为站点 `70001300`，其测点目录显示水位/高程类检查。用旧 VanDa 站号 `21000361` 请求测量结果时，API 返回400并称找不到该站。该接口结果不能替代 VanDa 水化学数据，也没有取得 Bryrup/Ravn/Arreskov 的样品结果行；相关案例科学验证仍**未完成**。数据目录与旧站点线索继续见[四湖观测来源核查](../target-lake-observation-sources-20261025.md)及[Bryrup 观测来源记录](bryrup-official-observation-source-note-20261025.md)。
- **状态边界**：未创建/删除案例、未运行求解器、未修改产品代码或刷新桌面页。黑色床面片仍**未修复**且根因**不确定**；完整用户流程及四湖科学验证仍**未完成**；代理结果保持**代理**。

### 2026-10-25 Sol：DCE 历史湖泊报告目录核查

- **实测（来源目录）**：DCE 官方湖泊报告页列有 Arreskov Sø 的 1987–1997、1989–2003 等报告，Bryrup Langsø 的年度报告至 2003 年，以及 Ravn Sø 1993–2002 年报告。该目录可证明存在官方历史监测报告，但不是原始观测行或目标模型验证证据。来源：[DCE 历史湖泊报告目录](https://dce.au.dk/udgivelser/tidligere-udgivelser/amtsrapporter)。
- **访问结果**：尝试读取 Bryrup 2003、Arreskov 2003、Ravn 2002 PDF；网页抓取因大小/超时失败。Bryrup PDF 可下载但为扫描影像、没有可提取文本；临时下载已删除，未留报告数据副本，也未转录任何数值。原始观测行取得、变量/单位核对、时间深度配对和科学验证仍**未完成**。
- **状态边界**：本轮未创建/删除案例、未运行求解器、未修改产品代码或刷新桌面页。所有代理输出仍标为**代理**；黑色床面片仍**未修复**且根因**不确定**；完整用户流程与四湖科学验证仍**未完成**。

### 2026-10-25 Sol：NOVANA 沉积实测汇总值

- **实测（官方报告统计）**：DCE/NOVANA 2023/2024 表层沉积物表（SR683 表2.11）报告每湖3个站点的简单均值。总磷单位为 mg P/g 干重；0–2 cm / 0–10 cm 分别为 Arreskov Sø **1.33 / 1.11**、Bryrup Langsø **4.13 / 4.20**、Ravn Sø **7.20 / 5.07**。来源：[DCE SR683 表2.11](https://dce.au.dk/fileadmin/dce.au.dk/Udgivelser/Videnskabelige_rapporter_600-699/SR683.pdf)。
- **状态边界**：这些是**实测的沉积物汇总值**，不是原始样本行，也不是模型水柱浓度；采样位置和聚合方式与目标模型输出尚未配对。因此只能作为沉积物观测来源证据，不能替代三湖的模型科学验证，相关验证仍**未完成**。ODA 无登录访问仍跳转至登录页；VanDa CSV 下载仍未取得。
- **当前湖泊状态**：Erken：观测源**实测**、模型配对**代理**、科学验证**未完成**；Lake Ravn：上游模型/数据比较**代理**、目标3D验证**未完成**；Bryrup：新增沉积物汇总**实测**、水柱观测配对和验证**未完成**；Arreskov：新增沉积物汇总**实测**、水柱观测配对和验证**未完成**。

### 2026-10-25 Sol：VanDa WFS 湖泊图层字段核查

- **实测（公开 WFS 目录/响应）**：匿名 WFS GetCapabilities 可列出 `vanda:vandkemi-soe`、`vanda:feltmaaling-soe`、`vanda:sediment-soe`、`vanda:mfs-vandkemi-soe` 等湖泊层。DescribeFeatureType 显示这些图层记录的是站号、站名、所有者、位置、首末调查日期和详情链接；GetFeature 只读样例同样返回站点元数据与 Kemidata 页面链接，没有水温/水化学/沉积物测量结果行。故该匿名 WFS 层是站点索引，不能作为四湖实测配对数据。
- **限制与状态**：这项检查只说明所查 WFS 图层公开字段不含观测值，不推断其它受权限保护的接口不存在数据。结合先前 CSV/API/ODA 访问结果，Erken 模型配对仍**代理**、科学验证**未完成**；Lake Ravn 上游比较仍**代理**、目标3D验证**未完成**；Bryrup 与 Arreskov 的沉积物汇总为**实测**、目标水柱配对和科学验证**未完成**。没有创建/删除案例、运行求解器、修改产品代码或打开/刷新桌面应用。

### 2026-10-25 Sol：续查现有桌面服务模板版本（只读）

- **实测（复用既有服务）**：`http://127.0.0.1:52812/` 返回 HTTP 200，服务仍是 PID 2980 的 `launcher.py --web --no-open --port 52812`。未打开新应用、未创建新标签、未刷新桌面页。
- **同步差异**：当前 HTTP 首页仍引用 `viz3d.js?v=119`、`ecology_network.js?v=30`、`viz3d_mesh_mode_preference.js?v=2`；工作区模板现引用 `viz3d.js?v=121`、`ecology_network.js?v=31`、`viz3d_mesh_mode_preference.js?v=2`。因此 3D/食性网络工作区已比运行服务模板新，尚不能对其最终桌面表现做验收。本轮只读哈希对照命令被本机策略拒绝，未执行任何命令或改动服务；不尝试规避该限制。依 AGENTS.md，任何后续产品代码修改前需先解决现有服务的同步/验收方式。
- **状态**：未新建或删除案例、未运行求解器、未修改产品代码。黑片仍**未修复**且根因**不确定**；完整流程与四湖科学验证仍**未完成**。参考图保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol/Luna：黑片根因与测试覆盖复核

- **Sol 高判断 / Luna 中源码复核**：没有改生产源码。现有颜色域修正锁定的是“床面不继承科学变量色标范围”这一独立正确性要求，但缺乏黑片历史条件下的匹配复现，不能作为黑片修复；材质/颜色、网格/绕序、深度/视角和多 trace 遮挡仍是候选，唯一根因**不确定**。frame19 原条件截图、Plotly 全 trace `_fullData` 和 GPU/浏览器信息缺失。
- **代理（已有针对性测试）**：`node --test 3DWET/tests/test_lake_display_mesh.js` 54/54 通过；`node --test 3DWET/tests/test_viz3d_waterbody_patch.js` 3/3 通过。覆盖湖底几何/色标数据和 playback trace 更新，未覆盖历史像素黑片，不能据此标记缺陷已修复。
- **实测（静态资源只读核验）**：现有服务首页为旧 cache-bust 标签（viz3d v119、ecology_network v30），而工作区模板为 v121/v31。GET `/static/js/viz3d.js?v=119` 的响应 SHA-256 与当前工作区 viz3d.js 相同；这只证明服务静态文件体相同，不证明当前页面 DOM 已重载最新模板。启动器当前用 Waitress，未发现安全模板热加载接口；没有刷新/重启或另开 APP。
- **下一步区分证据**：需获得原问题场景/参考图（继续保留 `（待补充：参考图的具体路径或链接）`），匹配帧、镜头、VE、图层、窗口大小复现；捕获 Plotly 全 trace arrays/顺序/可见性、颜色域与浏览器/GPU，再对 bed、wall、land、shoreline 组合及颜色、视角、VE逐项单因素切换。
- **总状态**：黑片**未修复**、根因**不确定**；本轮未新建/删除案例、未运行求解器、未改产品源码。完整用户流程和 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**，既有代理结果仍标**代理**。

### 2026-10-25 Sol：技术图标家族静态覆盖检查

- **实测（源码静态审计）**：当前模板定义58个 `studio-icon-*` SVG symbol，静态模板实际引用48个，未发现引用缺失；对 `app.js`、`gridstudio.js`、`preprocess.js`、`scientific_workspace.js`、`variable_guide.js` 中可静态识别的 `StudioIcons` 动态调用，共检查11个名称，均有对应 symbol。图标源码采用同一内联线稿 sprite 与动态路径表。
- **验收边界**：这是静态引用完整性检查，不能证明每个应用页面的运行时状态图标都被覆盖，也不能替代浏览器/桌面视觉验收；当前旧模板标签仍未同步重载。整体学术配色、图标笔画质量与响应式界面仍需当前版本桌面视觉验收，完整 UI 交付不可仅据此判定完成。

### 2026-10-25 Sol：52812 静态资源字节复核（内存只读）

- **实测（HTTP/source SHA-256）**：复用 52812 现有服务，在内存中读取并散列 `viz3d.js?v=119`、`ecology_network.js?v=30`、`app.js?v=72`、`viz3d_mesh_mode_preference.js?v=2` 与 `academic_ui.css?v=6`，五个响应体均与各自当前工作区文件逐字节一致。由此修正前条“3D/食性网络资源体尚不同步”的过度推断：目前确认的是 HTML cache-bust 标签比工作区模板落后，但该旧标签返回的静态内容与当前源码相同。
- **未证实项**：这不证明桌面 WebView 当前已重新请求这些资源，或已显示最新 HTML 模板；没有刷新页面、打开窗口或重启服务。黑片、科学验证、完整流程的状态未变化。

### 2026-10-25 Sol：attempt64 可补验状态检查

- **实测（现存记录）**：attempt64 `display_controls_followup.txt` 记载 1280×900 浏览器视口调整、3D 拖拽相机仰角 34°→49°、图表全屏进出和既有 2D/3D PNG 导出。上述行为均发生在合成 WorkflowPreprocessProxy64，属于**代理**，不是湖泊科学验证；浏览器视口覆盖也不等同原生桌面窗口 resize。
- **未完成**：应用 Ctrl+滚轮缩放、原生桌面窗口尺寸改变、失败状态通知仍缺实测记录。此前测试服务端口61007当前无监听进程，attempt64 原浏览器/服务已不在线，故不能在原运行中补验。未重启或另开 APP，也未重新创建案例。
- **状态**：attempt64 仍不能通过完整 UI 验收；完整用户流程**未完成**。Erken、Lake Ravn、Bryrup、Arreskov 科学验证状态不变；黑片仍**未修复**且根因**不确定**。

### 2026-10-25 Sol：食性网络路径聚焦回归检查

- **代理（合成 DOM/源码回归测试）**：执行 `node --test 3DWET/tests/test_ecology_foodweb_ui.js 3DWET/tests/test_ecology_network_ui.js 3DWET/tests/test_ecology_network_filter.js 3DWET/tests/test_ecology_network_i18n.js`，4/4通过。食性路径卡可点击/键盘 Enter 聚焦；确切的三节点和两条边在网络与对应关系表行同步高亮；再次激活或 Escape 清除聚焦；边和节点保留可访问标签；家族筛选与语言标签回归通过。
- **使用优化判断**：减少了从路径说明定位到网络和关系表的手动查找，且只聚焦 YAML 中已配置的关系，不会推断实测摄食或新增营养关系。此回归使用合成网络数据，不是湖泊科学验证，也未在当前桌面页面做视觉验收；Lake Ravn 等科学状态不因此改变。

### 2026-10-25 Sol：存档黑片图像的空间位置复核

- **实测（历史截图视觉复核）**：`erkens-black-bed-remains-20261023.png` 中近黑/蓝灰面主要位于浅灰色示意平面下方的近侧湖盆边缘，呈相邻的垂向/斜向三角面；湖内蓝色场面本身没有同样的黑片。该图标题记录 2020-DOY001 02:00、层9/9、VE166.5×。这是存档截图观察，不是当前版本匹配复现。
- **对候选顺序的影响（推断）**：空间位置使“床面边界附近的 wall/rim/land trace 组合、遮挡/深度顺序”更适合作为下一组优先隔离对象；但截图没有 trace 索引和对应网格，不能确认这些黑面属于哪条 trace，floor 几何、投影和 z-buffer 等仍未排除，根因仍**不确定**。下一次匹配渲染应先固定完整视口与 `_fullData`，对 wall/rim/land/bed 逐 trace 隐藏和恢复，再单独对照视角及 VE。

### 2026-10-25 Sol：丹麦公开水化学数据集与匿名导出限制复核

- **实测（官方元数据）**：Arealdata `Vandkemi Sø` 数据集说明其收录 VanDa 湖泊水化学的全部结果，字段覆盖地点、时间、测点、参数和值；许可标注 CC0 1.0，列出的 CSV 出口为 `https://arealdata-api.miljoeportal.dk/data/vanda-ue-26/file`。来源：[官方数据集页](https://arealdata.miljoeportal.dk/datasets/urn%3Admp%3Ads%3Avandkemi-soe)。
- **实测（当前访问）**：该 CSV 出口 HEAD 返回405，匿名 GET（Range 请求）返回401，未取得 CSV 内容。Danmarks Miljøportal 的 Arealdata 官方帮助说明需先登录后打开 CSV 下载；KemiData 帮助说明可筛选化学测量结果并下载 CSV。[Arealdata 使用说明](https://support.miljoeportal.dk/hc/da/articles/360016780777-Arealdata-Udstilling-af-data)、[Kemidata 页面说明](https://kemidata.miljoeportal.dk/)。这表示数据集和授权许可公开，但本轮匿名文件直链没有授权可读；没有尝试绕过登录。仍不能确定以用户身份登录的 KemiData UI 是否可对目标湖导出样品行。
- **状态边界**：未取得 Erken/Lake Ravn/Bryrup/Arreskov 的新观测行，科学验证状态不变；Erken现有配对仍**代理**，三湖目标配对仍**未完成**。本轮未创建/删除案例、运行模型或打开 APP。

### 2026-10-25 Sol：Kemidata 站点原始现场测量导出后续

- **Bryrup — 实测（原始观测获取）**：绕过此前未响应的搜索条件后，官方 API 对站点 21000361、`Datamart Feltmåling Sø`、1996–2006 返回并导出 5,005 行；其中温度 1,676 行、226 个测量日期，深度 0–10 m、温度 0.8–24.5°C。CSV 与 SHA-256 见[Bryrup 原始观测记录](bryrup-official-observation-source-note-20261025.md)。这不是 2018 三小时热浪强迫，也尚未与论文模型配对；数据集许可需单独核对。
- **Arreskov — 实测（原始观测获取）**：官方 API 对站点 45000018（`Arreskov Sø /004`）、1990–2004 返回并导出 4,627 行；其中温度 1,565 行、294 个测量日期，深度 0.2–3.5 m、温度 0.4–25.0°C。CSV 与 SHA-256 见[Arreskov 原始观测记录](arreskov-official-observation-source-note-20261025.md)。与模型列的空间、时间和变量映射及适用许可仍**不确定**。
- **Lake Ravn — 实测（官方目录搜索）**：站点 21000355（`RAVNSØ, MIDT -- RAV1 - vandkemi`）的 1990–2006 目录结果显示 `Feltmåling Sø` 18,679 条结果、342 个测次；此处未另行导出该 CSV。项目中既有官方 workshop `.obs` 配对仍为历史上游 1D 比较，结果只作**代理**，目标 GETM 3D 科学验证仍**未完成**。
- **状态边界**：新增两份湖泊 CSV 是实测监测数据来源，不是模型配对或科学验证。Erken 现有 GETM 配对仍**代理**；Lake Ravn、Bryrup、Arreskov 的目标科学验证仍**未完成**；完整用户流程仍**未完成**。黑色床面片仍**未修复**且根因**不确定**。本轮没有新建/删除案例、运行求解器或打开/刷新桌面 APP。

### 2026-10-25 Sol：Lake Ravn 官方现场观测 CSV 后续导出

- **实测（原始观测获取）**：官方 Kemidata `Feltmåling Sø` 对 Ravn 中点站 21000355（`RAVNSØ, MIDT -- RAV1 - vandkemi`）的 1990–2006 查询返回18,679行；原始 CSV 哈希、6,397条温度行、采样时刻与深度覆盖见[Ravn观测来源记录](ravn-official-observation-source-note-20261025.md)。原始记录含 `+01:00`/`+02:00` 等偏移，需先确认时区语义与模型输出时钟。
- **未完成 / 不确定**：站点 `RAV1` 与既有模型代表柱的精确空间映射、观测深度/变量映射和许可尚未核定；没有用此 CSV 生成新的模型配对或评分。官方 workshop `.obs` 上游一维比较仍属**代理**，目标 GETM 3D 科学验证仍**未完成**。
- **状态边界**：本次只增加原始观测审计材料；没有新建/删除案例、启动求解器或打开/刷新桌面 APP。食性网络和 UI 代码未变；黑色床面片仍**未修复**、根因**不确定**，完整用户流程及四湖科学验证仍**未完成**。

### 2026-10-25 Sol：Ravn 官方观测来源交叉核对与温度留出诊断

- **实测（观测来源交叉核对）**：Ravn CSV 与官方 workshop `TEMP.obs` 在6,382组日期/深度上重合，6,369条温度完全相同、6,378条差值≤0.1°C；与 `DO.obs` 有6,255组日期/深度重合，6,253条溶氧完全相同、全部差值≤0.1 mg/L。唯一精确值样本的原始本地采样时钟均在12小时内（中位差0小时）。这强力支持 station 21000355 是 workshop Ravn 观测流所对应的官方测站；空间采样位置到模型垂向柱的完整映射仍待核。
- **代理（现有官方 1D 参考输出温度诊断）**：未运行新案例，复用 21 点 `kNitrW` profile 的既有 `grid_11_0.30/output.nc`，以官方 `TEMP.obs` 对2001–2005做应用原生时深插值。1,852条候选中配对1,810条，42条因观测深度超出模型层中心范围而排除；bias −1.239°C、RMSE 1.966°C、MAE 1.571°C。源文件 SHA-256、模型输出 SHA-256 和算法上下文见[Ravn观测来源记录](ravn-official-observation-source-note-20261025.md)。这是历史 **1D** GOTM-WET 输出的代理诊断，不能声称完成目标 GETM 3D 科学验证或独立验证。
- **状态边界**：本次仅分析已存在的官方观测文件与模型输出，没有新建/删除案例、启动求解器或打开/刷新桌面 APP。Ravn 目标科学验证仍**未完成**；其他三湖、完整用户流程和黑片状态不变。

### 2026-10-25 Sol：Bryrup 旧版沉积物模块参数兼容性源码对照

- **实测（源码差异，非模型科学验证）**：官方 WET v0.1.0 的 `abiotic_sediment.F90` 将 `cCPerDWS` 作为活动参数，单位 `gC/gDW`，并用于沉积耗氧、氧化分解和反硝化通量；当前 `3DWET/src/wet/src/abiotic_sediment.F90` 中该参数已从类型移除、`get_parameter` 调用被注释，相关通量改由 `tCTrans_POM` / `tCTrans_DOM` 等变量表达。两个文件 SHA-256 分别为 `25859E763B9BBF50BEB0E8F7E584B84137BBA2774A74231650AD52BE82C9068D`（v0.1.0）与 `AA564FACC6D324F7BFB3AAF9E9C1510EACD56493E4D76172E513CAE5FE572CA6`（当前源码）。
- **结论**：此前 smoke 的 `cCPerDWS` 未识别不是单纯拼写差异；没有证据支持把它映射到当前其他参数或静默删掉。当前 smoke 仍只证明模块不兼容，完整运行与 Bryrup 科学验证仍**未完成**。需要可追溯的旧版兼容构建，或由科学负责人批准有明确守恒/语义依据的移植方案后，才能继续运行；本轮没有改源码或启动新案例。

### 2026-10-25 Sol：Feltmåling Sø 公开许可元数据核验

- **实测（官方元数据）**：检索 [Datavejviser JSON-LD](https://datavejviser.dk/katalog/danmarks-miljoportal/2ba457fb-a819-4e9c-8d4a-0d2de28c5197.jsonld) 的 `dcat:Dataset` 及 CSV `dcat:Distribution` 项，`Feltmåling Sø` 均声明 CC0，且访问级别为 PUBLIC。此项核验解除先前对 Ravn、Bryrup、Arreskov 三份 `Feltmåling Sø` CSV 再利用许可的**不确定**；数据来源与单湖原始文件哈希见各湖观测来源记录。
- **状态边界**：许可只决定数据再利用条件，不证明站点与模型的空间、时间或变量映射。Ravn目标 GETM 3D、Bryrup 2018 情景、Arreskov 论文案例配对与科学验证仍**未完成**；Erken目标模型科学验证仍**未完成**。未启动求解器或打开桌面 APP。

### 2026-10-25 Sol：Bryrup 候选旧版执行器排除

- **实测（版本/源码兼容性检查，非模型运行）**：复核了 Ravn 官方 GOTM 5.3/FABM au 执行器（WET `943d3c4`）。它保留旧沉积 `cCPerDWS`，但其 WET model library 未注册 Bryrup 配置中的 `wet/fish`，并且鱼类、浮游植物和浮游动物参数集仍不匹配；历史预检也明确报 `wet/fish is not a valid model name`。证据与 SHA-256 见[Bryrup 执行器兼容性记录](bryrup-legacy-binary-compatibility-note-20261025.md)。
- **结论**：不删参数、不猜测模型别名；此执行器不兼容原配置。当前环境未找到 Fortran 编译器或 CMake/Ninja，无法构建版本匹配的 WET v0.1.0 执行器。本轮无新案例/solver 运行，Bryrup 及四湖目标科学验证状态继续**未完成**。

### 2026-10-25 Sol：Kemidata 官方搜索 API 路径核实

- **实测（官方前端静态配置）**：Miljødata/Kemidata 首页公开配置 `connection.api=https://kemidata.miljoeportal.dk/api`；官方前端包使用 `POST /search` 搜索化学结果，并在 UI 中提供导出搜索结果的功能。该路径来自实际服务的首页设置和 JavaScript 调用，不是推测 endpoint。公开官方说明亦称 Kemidata 可按化学物质、地点、调查类型筛选并下载 CSV。[Kemidata](https://kemidata.miljoeportal.dk/)；[官方使用说明](https://support.miljoeportal.dk/hc/da/article_attachments/24503935676189)。
- **访问实测**：只发起针对 Bryrup、限定2001–2006日期窗口的位置搜索，不请求全库；该 `POST /api/search` 在20秒后无响应数据超时（HTTP 000）。因此目前找到的是官方结果搜索接口，但本轮未能取回结果；不能据此断言 endpoint 不含目标观测，也不把目录或汇总值当成原始观测。
- **状态边界**：四湖科学配对状态不变：Erken既有配对**代理**、科学验证**未完成**；Lake Ravn上游比较**代理**、目标3D验证**未完成**；Bryrup与Arreskov有部分沉积物汇总**实测**，目标原始水柱观测配对和验证**未完成**。没有模型、案例或 APP 操作。

### 2026-10-25 Sol：Bryrup 官方版本路线复查

- **实测（官方版本文档）**：现行 WET 官方文档记载 v0.1.0 于 2021-06-05 发布，说明该版包含 PCLake 式兼容鱼类模块，并指向历史 `WET/wet` release；现维护仓库已迁移且 tags 页面列出 v0.2.x。来源：[WET 官方文档](https://gitlab.com/wateritech-public/waterecosystemstool/wet)、[官方 tags](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tags)。这确认存在版本化源码路线，但没有核实到匹配 Windows 执行器，也未证明现有二进制适用 Bryrup 归档。
- **不确定**：可下载的精确时代执行器/构建包是否公开可得；本次没有构建或运行新案例。
- **未完成**：Bryrup 全案例执行与论文复现仍未完成；四湖科学验证和完整用户流程状态不变。无桌面 APP 操作。

### 2026-10-25 Sol：科研软件交互与 3D 表现参考复核

- **实测（官方文档检索）**：ParaView 官方文档说明 pipeline browser、properties panel、3D view 与 camera toolbar 的职责分区；napari 官方 viewer 文档展示 layer list、canvas、layer controls、status bar 及 2D/3D、home、axes、scale bar 控件；QGIS 3D 文档明确提供 terrain vertical scale、triangle/wireframe、shading 与灯光/深度效果。逐条来源与采用理由见[科研 UI 参考审阅](../../superpowers/specs/2026-10-25-scientific-ui-reference-review.md)。
- **Sol 高设计结论**：采用暖纸色基底与低饱和湖蓝、鼠尾草绿、赭石形成层级；高彩度只用于定量场色带和语义告警。采用三角面轻度明暗、克制边线、湖盆轮廓、直接视角预设和清楚标单位的垂向倍率。避免强环境遮蔽/阴影默认值，以免与尚未修复的黑色床面片混淆。图标延续单一技术制图线稿家族。来源提供的是科研交互模式，不构成“全球最佳”排名或对产品配色的客观背书。
- **状态**：设计方案已有用户确认；既有 UI/图标改动仍需结合本轮 3D 实现和桌面同步状态验收。黑片仍**未修复**且根因**不确定**；四湖目标科学验证与完整用户流程仍**未完成**。

### 2026-10-25 Luna：三角网络空间表现实现与 Sol 验收

- **Luna 中实现**：三角变量面使用固定方向、低调的面片明暗，显式标记为显示照明；字段原值、色标范围、湿网格几何、悬停数据不变。保持细而克制的三角边线、湖盆边界、连续曲面替代模式及默认隐藏节点；仅在已支持的多层 sigma 数据时增加显示用途的层间连线。图层关系/显示提升仍不是求解器原生拓扑或物理位移。
- **Sol 高独立验收（代理）**：运行 `node --test 3DWET/tests/test_lake_display_mesh.js 3DWET/tests/test_viz3d_mesh_mode_preference.js 3DWET/tests/test_viz_metadata.js`，73/73 通过。元数据测试的旧断言误把床面 trace 当变量层，已改用 `meta.scientificField` 并核对合并堆叠 trace 的 `layerOrdinals=[0,4]`；没有改生产 trace 排序来迁就测试。
- **实测（资源服务）**：52812 首页 HTTP 200，但仍渲染 `viz3d.js?v=119`；新 URL `viz3d.js?v=122` HTTP 200，SHA-256 与工作区脚本相同（`ED3C9E85552FA233E9BE08939031D6C3AFD2759D09F7296C844712D6D5F4158B`）。本地模板已从 v121 更新为 v122。现有进程缓存着旧 Jinja 模板；本机策略拒绝了服务重启调用，且应用没有热重载接口。没有重开窗口。故桌面 WebView 最终模板/视觉状态仍**未验证**，自动同步尚未完整完成。
- **状态边界**：此项只验证视图渲染/代码，不是黑片修复或湖泊科学验证。黑色床面片仍**未修复**、根因**不确定**；Erken、Lake Ravn、Bryrup、Arreskov 目标科学验证及完整用户流程仍**未完成**；参考图保留 `（待补充：参考图的具体路径或链接）`。本轮未启动/删除求解案例。

### 2026-10-25 Sol：食性网络路径交互复核

- **代理（合成数据回归）**：本轮重新运行食性网络四组测试，4/4通过。路径聚焦同步标识配置节点、边和关系表行；键盘 Enter/Escape、类别过滤、语言标签及单实例编辑器均通过。
- **边界**：测试不验证湖泊中的真实摄食或运行时通量，不改变四湖科学验证状态。

### 2026-10-25 Sol：复用已存在的 52812 浏览器标签复核

- **实测（现有页面）**：只选取并刷新了原有 52812 标签，没有新开窗口/标签。刷新后页面仍显示 Lake Dianchi 仪表盘，暖纸色和低饱和绿/蓝界面可见；页面脚本直接资源响应（`v=119`）与工作区 viz3d.js 字节匹配。此处只核实了仪表盘截图和资源请求，不是 3D 工作区视觉验收。
- **未完成同步**：Flask 首页仍返回缓存的模板标签 `v=119`，工作区模板为 `v=122`；重启进程的调用被本机策略拒绝，无热重载接口。未关闭用户原有标签。故当前活动页面是否使用最新 HTML/CSS和完整 shell 仍**不确定**。

### 2026-10-25 Sol：Erken 2017–2024 小时温度实测配对诊断

- **实测（数据获取与校验）**：按用户已授权的 SITES CC BY 4.0 数据使用告知接受流程，取得 PID `11676.1/Kq6E7t69ZyKJejMcANJQVoHP` 的 2017-06-28–2024-09-14 60分钟剖面。解压 CSV 为 29,452,645 bytes，SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`，与官方元数据一致；文件和 provenance 位于 `build/source-downloads-20261025/erken-hourly-2017-2024/`。核对发现此前留存的 PID `XwTfEa8hviDoL_TEhBCYFkt9` 是另一个日频产品，不能称为该小时数据。
- **代理（已有输出逐小时配对）**：只读复用既有 `build/erken-production-compare-20261024/case-production-legacy/output.nc`（SHA-256 `784b37d30e0b99ed83838369fba2a9c8bddffc1d427937b93ad36c3758d7788e`），未启动求解器。用站点最近湿格 `(yc=8,xc=36)`（0.1023 km），按时变 sigma 中心深度对 49 个实测深度线性插值；168个小时、8,232个深度配对。原时间标签、减1小时、加1小时的 RMSE 分别 4.1839、4.1879、4.1799 °C，说明这三种钟差下总体结果相近。
- **未完成 / 不确定**：源文件注明 UTC+1，而 NetCDF 时间轴没有时区；观测为小时平均，模型为小时输出帧，时间支持是否等价未知；最近格点也不是测站空间平均。既有实验的云量、蒸发、流量和生态初始/营养条件含代理或缺失，因此分数只能是**代理**，不得称为 Erken 科学实测验证。报告见 `docs/audit/erken-hourly-profile-pairing-proxy-20261025.md`。Erken 科学验证仍**未完成**；未创建/删除案例或运行求解器。
- **官方版本说明**：该历史 60分钟产品现标记为 deprecated。SITES 当前产品 PID `11676.1/gVQYm0aNPryFRtn2CpeuzzwF` 已更新至 2025-12-01，仍为60分钟数据；本次按用户授权下载的限定时段历史源，没有额外下载该更长版本。
- **界面操作约束**：没有新开或刷新 APP/浏览器窗口。52812 进程仍 idle；服务没有模板热重载路由，安全同步还需通过其所有者正常关闭/重新启动。完整桌面同步验收仍**未完成**。

### 2026-10-25 Sol：黑床材质路径与回归测试复核

- **实测（源码静态审计）**：湖底 bed trace 使用独立 bathymetric intensity/cmin/cmax/color 路径，照明设为 ambient=1、diffuse=0、specular=0、roughness=1；wall 使用相近的中性照明。科学变量三角网格 trace 单独使用 ambient=0.68、diffuse=0.32、specular=0。该结构降低了“新三角网格科学场照明直接把床面染黑”的可能性，但多 trace 遮挡、几何/绕序、深度缓冲精度、材质或数据更新仍未排除。根因继续标记**不确定**；缺陷**未修复**。
- **代理（自动回归）**：修正过期的 cache-bust 版本断言后，`node --test 3DWET/tests/test_viz3d_waterbody_patch.js 3DWET/tests/test_waterbody_patch.js 3DWET/tests/test_lake_display_mesh.js` 54/54 通过。覆盖静态代码/几何行为，不包含历史条件的黑像素复现，不能作为黑片修复证据。
- **桌面同步**：本轮未打开或刷新 APP。52812 仍需通过原启动器所有者控制台正常重启才能加载最新模板；该控制台当前不可访问，且旧版本服务与工作区标签不一致。桌面最终同步验收仍**未完成**。
- **案例与流程**：本轮没有创建或运行求解器案例，因此无需清理既有生成案例；四湖科学验证与完整用户流程状态不变，仍**未完成**。

### 2026-10-25 Sol/Luna：历史床面/侧壁对照复核

- **实测（历史浏览器记录）**：回查 2026-10-23 图层隔离记录，床面 trace 隐藏时黑区消失，恢复床面后重现；侧壁仍显示，关闭示意陆地也未消除黑区。这优先支持床面绘制路径或其渲染交互，但历史记录不是当前版本、匹配 viewport 的复现，不能确认唯一机制。
- **实测（当前源码 trace 构成）**：高 VE 动态叠层与静态地形预览均省略独立 wet-grid wall；静态路径额外显示验证过的岸边 rim/显示网格，动态路径包含科学变量场。现有 frame167 简化夹具没有复现，且其 trace 集不同于正式完整场景。
- **结论**：没有满足因果门槛的当前路径复现，因此未改生产渲染代码、未新增回归测试。黑片仍**未修复**，唯一根因仍**不确定**。下一步需在匹配的历史条件下捕获完整 `_fullData`，依次隐藏床面、rim、陆地、岸线、等深线及科学场；参考图路径保持 `（待补充：参考图的具体路径或链接）`。
- **流程边界**：未创建/启动/删除案例，未打开、刷新或重启桌面 APP；四湖科学验证及完整用户流程仍**未完成**。

### 2026-10-25 Sol：frame19 当前渲染构造无头对照

- **代理（渲染诊断）**：复用已有 frame19 Erken proxy API 快照，在独立 headless Edge/SwiftShader 页面调用当前湖盆几何/trace 构造函数，对照 200×静态床面与50×动态 `temp` 叠层。Viewport 1800×900，固定正交相机；页面不连接桌面服务、不读写案例、不运行求解器。
- **实测（无头像素观察及 `_fullData`）**：两条路径均未复现明显黑片；床面 mesh 672 顶点/336面，所有检查到的 trace x/y/z 有限。结果与限制、输入和源文件哈希见[诊断记录](../../../build/bed-black-frame19-current-render-audit-20261025/README.md)。
- **验收边界**：这是当前渲染函数在代理数据、SwiftShader 和固定相机下的负复现，不代表用户设备复现或缺陷修复。黑片仍**未修复**、根因仍**不确定**；未改生产代码。完整用户流程与四湖科学验证仍**未完成**，参考图继续待补充。本轮无新建/运行案例、无桌面 APP 操作。

### 2026-10-25 Sol：frame19 床面颜色编码单变量复现

- **代理（渲染诊断）**：在同一已存在的 frame19 proxy 快照、200×静态几何、相机和当前 `lakeTraces` 上，对照深度色标、显式 diagnostic direct-color、恒定中性色标三路；50×动态叠层作为参考。没有求解器或用户案例操作。
- **实测（无头像素和 `_fullData`）**：三种静态床面 x/y/z/i/j/k 哈希相同，672顶点/336面；显式单色 `color` 图框中 `RGB max<40` 像素8.8036%，而深度色标、恒定中性色标图框均为0。direct-color路径不含床面 intensity，另两路各保留672个 intensity 值。Screenshot、源哈希和方法见[颜色编码诊断](../../../build/bed-black-frame19-color-encoding-audit-20261025/README.md)。
- **Sol判断**：证据增强了“床面颜色编码分支与黑面相关”的候选，仍不能区分 Plotly/WebGL材质分支、面向/照明和相机/遮挡交互；且直接单色只由显式诊断选项进入，不证明默认用户路径已修复。黑片仍**未修复**，根因仍**不确定**。Luna 正在为床面 mesh3d 加最小防护并补回归，桌面状态须在实现后独立同步验收。
- **桌面只读状态**：52812 ready/idle，指向当前仓库；HTML引用 `viz3d.js?v=119`，该URL实际返回字节与当前工作区 renderer 相同。页面实际视觉状态未刷新/检查。本轮未打开、刷新或重启桌面 APP，也未启动/删除案例。

### 2026-10-25 Luna：三维体网格预设与工作区英文标签

- **实现（界面代码）**：新增可逆“体网格预设”按钮，一次启用派生三角显示剖分及所有可用垂向层；再次点击恢复之前的网格/叠层/选层设置。用户手动更改相关控制时退出预设并保留手动选择。模型变量值、求解器拓扑、湖底渲染不变；文案明确这是显示层辅助，不代表模型拓扑或物理位移。此改动针对“单层虽有三角线，但不易读成三维体”的界面使用问题。
- **实现（国际化）**：补齐“检查器”“变量与图层”“变量与视图”、镜头手势说明及两个 inspector 切换标题等6个英文标签；英文目录共覆盖242个工作区静态标签/无障碍文本。
- **代理（独立回归）**：三角网格、偏好、体网格预设、静态工作区语言、waterbody trace/playback 测试合计 **63/63通过**；JS 语法检查与英文 JSON 解析通过。测试证明控件切换、恢复、英文目录及渲染 trace 属性，不证明实际桌面页面中的纵深感受，也不证明黑片修复或湖泊科学验证。
- **实测（服务同步核对）**：52812/PID 2980 健康、指向当前仓库且模型 idle；修改过的静态资源响应与磁盘一致。但 HTTP 首页仍使用模板缓存的 i18n v14、mesh preference v2，且无体网格预设脚本；磁盘模板已为 i18n v16、mesh preference v3，并包含预设脚本 v1。现有服务无受支持的模板热重载接口，所有者启动器控制台不可访问。本轮未强制终止进程、未打开/刷新/重启 APP，故桌面同步和可视验收**未完成**。
- **案例**：未创建或启动模型案例；按用户要求未清理/删除既有案例。
- **状态边界**：黑片仍**未修复**且根因**不确定**；完整用户流程及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍各自**未完成**。参考图保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：Bryrup 兼容性阻塞复核与工具链纠正

- **实测（工具链）**：当前用户工具链中存在 UCRT64 `gfortran 16.2.0`、`cmake 4.4.4`、`ninja 1.13.2`，位置在 `C:\Users\23801\.codex\toolchains\msys64\ucrt64\bin`；它们不在 PATH。此前“环境没有编译器/CMake/Ninja”的概括不准确，真正限制不是找不到通用工具链。
- **实测（上游分支）**：官方 Aarhus 开发页要求 GOTM `au`、FABM `au` 与 WET `master` 组合；来源：[AU WET developer instructions](https://projects.au.dk/wet/for-developers)。本轮对三个官方 GitLab remote 的 `git ls-remote --heads` 检查仅返回 master：GOTM `2b107b1fddd3ba4a17746cc2b4f31e431f8d35fd`、FABM `e42ba6dd57a710afaac33f4de6d15fe0bc8727e9`、WET `d2eee4419ab6762c092e07dc79316feff9efec5c`；未观察到所需 GOTM/FABM `au` 分支。
- **科学边界**：官方 WET GitLab 发布说明区分 v0.1.0 与 v0.2.0 的模型机制变化；用当前 master 或当前 GETM 二进制替代论文所述历史 runner，无法证明和 Bryrup/Chen 校准情景等价。既有 v1.0 smoke 在首个积分步前因主机配置不兼容而终止，无科学模拟输出。来源：[官方 WET repository/version description](https://gitlab.com/wateritech-public/waterecosystemstool/wet)。
- **状态**：没有删除或新建案例、没有运行求解器。Bryrup 科学验证继续**未完成**；要继续须获得可追溯的匹配 GOTM/FABM 源码/二进制与论文案例驱动包，或由科学负责人批准有物理语义依据的兼容方案。不能只靠通用编译器补齐该缺口。

### 2026-10-25 Sol：Bryrup Zenodo 源码包核验

- **实测（公开记录元数据）**：读取 Zenodo DOI `10.5281/zenodo.6482852` 的官方 API 元数据，v1.0 仅列出 `wet-v1.0.zip`（3,043,858 bytes）；记录描述为 WET 软件发布。该包不列 GOTM/FABM `au` 依赖或完整 Bryrup 案例驱动，因此不能单独解除历史版本兼容阻塞。官方记录：[WET v1.0 on Zenodo](https://zenodo.org/records/6482852)。
- **版本边界**：同一 Zenodo 记录的 latest 指向 v2.3（DOI `10.5281/zenodo.17453175`），文件包括 WET 源码与 executables；较新版本不能仅凭发布时间/打包形式认定等价于论文 Bryrup 配置，本轮未替换模型或启动求解。
- **状态**：Bryrup 目标科学验证仍**未完成**。未创建/删除案例，未运行求解器，也未打开/刷新桌面 APP。

### 2026-10-25 Sol/Luna：科研 UI 方向、源码检查与同步状态

- **Sol 高（设计参考与方案）**：读取 QGIS GUI/3D Map View 和 ParaView GUI/Displaying Data 官方手册，依据其画布优先、可收纳面板、上下文工具、明确 2D/3D 相机操作的交互结构，制定整体科研工作台艺术指导，见[设计方案](sol-scientific-ui-art-direction-20261025.md)。方案明确采用暖纸白/石灰灰、低饱和灰绿与雾蓝灰的多层次结构色；科学图层色带保留；统一技术线性图标；禁止纯黑白方案和装饰性艳色。
- **Luna 中（源码审查）**：确认当前工作区 `academic_ui.css` 覆盖 shell、导航、表单、表格、弹窗、工作流、食性网络、2D/3D 工作区；模板 58 个 SVG 符号各有独立线稿，统一 24 格与约 1.7px 视觉笔画；静态/动态控件共享 icon helper。没有发现需增加产品样式代码的明确缺口。该检查基于源码，不等同于桌面视觉验收。
- **代理（前端回归）**：Luna 报告 `test_studio_icons.js`、`test_academic_visual_system.js`、`test_workbench_shell.js`、`test_scientific_workspace_language.js` 共 **6/6** 通过；为修正测试期望，将 `test_workbench_shell.js` 中旧的 i18n/workspace CSS 版本断言更新为当前模板版本。
- **实测（服务响应）**：52812 首页 HTTP 200 且模型 idle；页面引用 `academic_ui.css?v=6`、`studio_icons.js?v=2`，其资源响应哈希与磁盘相同。首页模板仍引用 `i18n.js?v=14`、`viz3d.js?v=119`，并未包含 `viz3d_volume_preset.js`，而工作区模板为 i18n v16、viz3d v122 并含体网格预设。整体样式已由该旧模板引用，但最新语言/三维工作区 shell 功能没有完整同步。没有刷新/重启 APP，未另开窗口；桌面最终视觉验收仍**未完成**。
- **案例**：未新建、删除或启动任何模型案例，因此未触碰用户已有案例与证据。

### 2026-10-25 Luna/Sol：旧模板下三维体网格预设可用性

- **Luna 中（实现）**：为修复“当前 Flask 进程模板缓存仍没有新脚本标签”的功能缺口，在仍由旧模板引用的 `app.js` 加入兼容引导。只在旧模板已有网格、垂向堆叠、层选择控件时注入预设按钮并加载已有体网格预设模块；如果新版模板已有该按钮，改为复用并绑定，避免重复元素或脚本。
- **代理（回归）**：Sol 检查并执行旧模板兼容、预设状态恢复、shell、图标、UI 色彩、工作区静态语言相关 6 个测试文件，**12/12通过**；`app.js` 语法检查通过。
- **实测（同步/资源）**：52812/PID 2980 HTTP ready，模型 idle。缓存首页仍引用 `app.js?v=72` 且未含预设脚本；同一旧 URL 返回更新后的 `app.js`，SHA-256 `5EB8A1E9BF24D8F6CAD7B5F9FE2522D5C10291E65EF30F304E0BD4AC24485A36`，与磁盘一致，`Cache-Control: no-cache, max-age=0`。新版磁盘模板 app.js cache key 已升至 v73；服务模板本身仍未更新。代码路径保证旧页在下一次加载时获得预设，但现有桌面 DOM 是否已加载兼容逻辑仍未检查。
- **边界与操作**：遵守用户“不重复打开 APP”的要求，没有刷新/重启/另开窗口或关闭用户页面。服务正在提供更新后的 JS 源，但实际桌面窗口是否执行它仍**未验证**；后续最终桌面同步须复用既有窗口正常载入，不能以另开窗口替代。未启动/清理任何案例。

### 2026-10-25 Sol：复用现有页面的一次性同步与体网格显示检查

- **实测（既有浏览器页面）**：复用标签 127（`http://127.0.0.1:52812/`），未创建标签或窗口，单次重新载入后进入原有 Lake Dianchi 三维工作区。可访问树显示“体网格预设”按钮及说明，证明旧缓存模板下的 app.js 兼容层在当前页面已执行。模型运行仍 idle。
- **实测（可逆显示操作）**：启用体网格预设后，页面显示选层 `0–9/9`，状态栏记为 10 层、三角显示剖分及辅助层间连线；再次点击恢复原先第9层单层状态。没有运行求解器或写入案例。当前狭窄页面截图显示三角线与湖盆层次可见，但视觉感受只属该窗口/该 Lake Dianchi 案例的浏览器展示，不能证明所有分辨率或用户目标案例下的三维观感。
- **实测（界面视觉）**：复载的当前页面呈暖纸白、石灰灰、灰绿与蓝灰工具状态层级；SVG 线性图标在导航和工具中统一。没有把结构层改成纯黑白，模型变量使用独立定量色带。实际界面观测已完成，但参考图仍未提供；对目标参考图的对照仍**未完成**。
- **黑片边界**：当前检查使用 Lake Dianchi、2020-DOY002、垂向 300×，不是历史 Erken 黑片的匹配帧/视角/设备。该画面未见明显黑片不构成修复证据。黑色床面片仍**未修复**，根因**不确定**。

### 2026-10-25 Sol：床面颜色分支实现复核、数据取回与同步状态

- **代理（代码回归）**：独立复跑床面测试 **11/11**、湖盆叠层测试 **26/26**、3D 网格显示测试 **51/51**；`viz3d.js` 语法检查通过。中性色床面保持深度 intensity 与几何/hover 数据，诊断 direct `color` 分支改为固定中性色 colorscale。回归通过不能证明用户原报告的生产场景已修复。
- **代理（受控渲染）**：同 frame19 proxy 的后改动 headless 重渲染中，depth、force-bed-neutral、force-bed-neutral-scale、动态温度四个面板的近黑像素均为 **0.0000%**。输入与限制见 [`post-Luna render`](../../../build/bed-black-frame19-post-luna-audit-20261025/README.md)。此前 direct-color A/B 支持颜色编码分支敏感性，但没有新证据确定 Plotly/WebGL 内部唯一机制，也没有匹配用户默认渲染路径的复验。
- **实测（服务/既有页面）**：复用现有 52812 标签一次刷新，没有新建窗口/标签。当前服务 PID 2980 报告 model root 为本仓库、run idle；服务返回 `viz3d.js?v=123` 的内容与磁盘 JS SHA-256 一致（`06FCCA575190F05AB85F6E80130B42518E1C619504DFF96AC2381B2B1EAB0CB7`）。但缓存首页仍引用 `viz3d.js?v=119`，与磁盘模板 v123 不一致；尝试对该用户服务做正常重启被本机策略拒绝，因此模板同步和桌面最终验收**未完成**。没有以另开窗口替代同步。
- **实测（观测数据取得与完整性）**：按用户明确授权，在 SITES 数据许可页确认使用 CC BY 4.0 后下载 Erken 2017-06-28 至 2024-09-14 hourly anchored profile。CSV SHA-256 与门户公布值完全一致：`2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`；解析为 62,959 条记录、50 个测温深度列、无空值，温度范围 −0.1509183–25.55556 °C。原文件、ZIP、许可证与来源/引用记录位于 `build/erken-observed-2017-2024/`。文件校验是观测数据**实测**，并非模型配对验证。
- **未完成**：Erken 完整科学验证、Ravn/Bryrup/Arreskov科学验证、完整用户流程、食性网络运行验证、原用户床面黑片修复及根因确认仍按原状态保留。数据集截止 2024-09-14，不覆盖完整 2024 年。
- **案例边界**：本轮没有创建、删除、清理或启动模型案例；当前 Lake Dianchi 服务 run 状态为空闲。
- **Erken 配对更新**：对已有 2020-01-01 24 h 输出进行了只读温度配对，得到 1,200 对（24 时刻 × 50 深度），RMSE 0.05912 °C、MAE 0.05422 °C、模型减观测偏差 +0.05356 °C。使用 sigma 界面中点映射，配对复现脚本、逐点 CSV 和限制说明见 [`Erken one-day pairing`](../../../build/erken-2020-observation-pairing-20261025/README.md)。由于初值来自同一观测源、仅一天且其他输入含代理/默认，分类为**代理**；这更新了“尚无模型与观测配对”这一点，但 Erken 完整科学验证仍**未完成**。时区标签在模型 NetCDF 中缺失，日期标签相配仍属假设。
- **代理（食性网络回归）**：本轮复跑关系图层、类别筛选、语言标签及可访问路径聚焦测试，**4/4** 通过。路径焦点可关联网络节点/边与关系行，筛选和键盘操作通过；这不构成求解器运行时的摄食机制验证，完整流程仍**未完成**。

### 2026-10-25 Sol：黑色床面颜色假设的历史反证复核

- **实测（历史浏览器诊断记录）**：同案例高倍率对照曾显示：隐藏床面 trace 时黑面消失；只保留床面 mesh、关闭 intensity 与色带并将其强制为纯绿后，黑面仍在。静态 bathymetry 预览与动态叠层也曾表现不同，但其床面数据/trace 属性并非完全一致。说明床面绘制是相关路径，直色编码并非已证实必要条件。
- **代理（颜色分支诊断）**：另一个 frame19 代理无头对照中 direct `mesh3d.color` 出现 8.8036% 近黑像素，恒定中性色标与深度色标为0%。该结果只说明特定代理渲染对编码分支敏感，不能解释历史真实浏览器的纯绿床面黑片，更不支持单独改色即修复。
- **Sol 决策**：撤回无生产失败证据支持的高 VE 中性色方案；当前生产代码未因该假设改变。已更新[黑片证据矩阵](black-bed-cause-matrix.md)，将床面几何/网格与视角、VE及动态/静态绘制交互列为优先候选；全部仍**不确定**。下一次有区分力的证据必须在原场景正复现下采集 `_fullData`、几何和完整视口，再做单变量 A/B。
- **代理（Sol 独立回归）**：3D bathymetry/waterbody tests **37/37** 通过；食性网络、学术 UI、图标和 shell tests **10/10** 通过。这些结果覆盖 trace/控件和样式结构，不等于黑片 GPU 复现、求解器摄食验证或桌面整体验收。
- **实测（仓库服务同步检查）**：52812 health ready，model root 指向本仓库，HTTP 首页200并引用 `academic_ui.css?v=7`、`scientific_workspace.css?v=12`、`scientific_workspace.js?v=18`、`viz3d.js?v=123`、`i18n.js?v=16`、`app.js?v=73`、`ecology_network.js?v=31`；HTTP `viz3d.js?v=123` 与当前磁盘资源 SHA-256 同为 `06FCCA575190F05AB85F6E80130B42518E1C619504DFF96AC2381B2B1EAB0CB7`。遵守用户避免重复开应用的要求，本轮没有刷新或打开页面，因此服务资源同步已核、页面实际执行版本和桌面最终视觉仍**未验证**。
- **状态**：用户桌面黑色床面片的最终验收仍**未完成**，唯一根因仍**不确定**；参考图保留 `（待补充：参考图的具体路径或链接）`。本轮没有创建、删除或运行模型案例，没有打开、刷新或重启桌面应用；无产品代码变更，无桌面同步操作。

### 2026-10-25 Sol：历史正复现载荷的 v86/v123 源码重放

- **代理（受控源码重放）**：使用保存的 Erken frame19 `temp` 代理载荷，在同一 Plotly 2.35.2/headless Edge/1440×1000/正交相机下分别载入历史 `viz3d.js` v86 和当前源码 v123。床面 `x/y/z/i/j/k` 几何哈希完全一致；ROI 572,400 像素中，旧版全场 75,471 个像素低于 RGB 40、床面单 trace 245,173 个；当前 v123 两种条件均为0。旧版床面强制纯绿且使用 ambient-only 光照仍有245,173个近黑像素。该证据支持当前组合渲染路径消除这份历史代理载荷的黑片复现。
- **根因限制**：v86 与 v123 的颜色编码（直接色 vs 深度 intensity/colorscale）和 lighting 属性同时改变；因此不能确认单个属性或 WebGL 内部唯一根因。像素阈值只作图像筛查，不是湖床分割。
- **实测/未完成边界**：这是代理渲染诊断，不是用户当前桌面/目标 GPU 实测。按用户不重复打开 APP 的要求，没有刷新或另开应用；服务当前版本先前已核对，但真实窗口执行版本及最终视觉仍未验证。因此用户桌面缺陷最终状态为**未完成验收**，不能写作全面修复。详见 [重放报告](../../../build/bed-black-v86-replay-20261025/README.md) 与[黑片证据矩阵](black-bed-cause-matrix.md)。
- 本轮仅新增诊断记录，无应用代码变化；未创建、删除或运行模型案例。

### 2026-10-25 Sol/Luna：黑片单属性对照、工作区配色修正与相机测试 fixture

- **代理（历史床面属性 A/B）**：同一 v86 bed trace、几何、相机、Plotly 2.35.2 与 headless Edge/ANGLE RTX 4070 下，仅添加 intensity 数组将 ROI 近黑像素从245,173降到0；单独改 direct color、colorscale、ambient/diffuse lighting 均仍为245,173。Plotly 在 intensity 条件因 `autocolorscale=true` 自动选择 colorscale，因此结论仅为“强度/自动着色分支有区分性”，不能拆成唯一属性根因。报告见 [单属性对照](../../../build/bed-black-v86-attribute-ab-20261025/single-property-controls/README.md)。黑片仍**未修复**，唯一根因**不确定**。
- **Luna（实现）**：修正学术工作区主题覆盖缺口，将表单文字/边框、次级 hover 与成功按钮接入共同 ink、矿物灰、湖蓝和 sage token；模型色带与语义状态色未受改动。CSS cache key 为 `academic_ui.css?v=8`。修改位于 `3DWET/app/static/css/academic_ui.css`，对应断言在 `3DWET/tests/test_academic_visual_system.js`。
- **Luna（测试 fixture）**：相机事件测试失败根因是 VM fixture 未注入浏览器全局 `URLSearchParams`，造成 render audit 在 listeners 与 last-plot case key 初始化前异常退出；跨案例相机值错误是连带结果，不是生产回归。只在 `test_viz_camera_axes.js` fixture 注入该全局，没有改生产 JS。
- **代理（Sol 独立回归）**：运行学术 UI、图标、食性网络、工作区语言/播放、3D 网格/体网格预设及相机轴测试共 **93/93 通过**。该套测试证明代码/合成 DOM 行为，不证明目标桌面视觉或用户 GPU 黑片验收。
- **桌面同步**：52812 旧服务 PID 15680 起初仍提供首页 `academic_ui.css?v=7`，但 `?v=8` 静态资源已与磁盘哈希一致。按仓库要求尝试安全地重启 `launcher.py --web --no-open --port 52812` 以载入新模板时，本机命令策略拒绝了进程停止/重启调用，故没有启动替代进程；新首页模板与 UI 修改的服务级同步、桌面窗口实际视觉仍**未验证**。没有打开、刷新或另开 APP。
- **案例与目标边界**：本轮没有创建、删除、清理或运行模型案例。Erken、Lake Ravn、Bryrup、Arreskov科学验证、完整用户流程仍逐项**未完成**；食性网络运行时机制验证仍**未完成**。参考图保留 `（待补充：参考图的具体路径或链接）`。


### 2026-10-25 Sol：Bryrup 官方 WET v0.1.0 案例包存在性校正

- **实测（官方归档文件核验）**：官方 WET v0.1.0 Zenodo 归档 `10.5281/zenodo.4903142` 已在本机恢复，其中确实含 `testcases/lake_bryrup_denmark/`，包括专属 `fabm.yaml`、`gotm.yaml`、forcing 与输出配置。两个 YAML SHA-256：`fabm.yaml` `CA2B3F18D2E76797BD049BE9F35C670200246C27725E1B69B41A50A4B4081E78`；`gotm.yaml` `FE310E46548DF2407B45973886D116BE427129C942B0D3B925D0364F7F7E8AFE`。官方来源：[WET v0.1.0 Zenodo 记录](https://zenodo.org/records/4903142)，整包 SHA-256 `B238D49CED074CA9297DC8FF2AD26A3F6E6DA4A0642138458B5D3B8B5EF17CE1`。
- **校正边界**：此前阻塞不应描述为“没有 Bryrup 配置/forcing”。已找到版本化 case 包；现有 Ravn runner 与该配置的模块名/参数不兼容，当前环境 PATH 也没有 CMake、Ninja 或 Fortran/MSVC 编译器。该包是否等同论文最终校准配置、是否能以可追溯历史 runner 执行仍**不确定**，本轮没有启动 solver。
- **状态**：Bryrup 归档配置存在为**实测**；Bryrup 全案执行与科学验证**未完成**。完整用户流程、Erken、Lake Ravn、Arreskov科学验证状态不变；黑片仍**未修复**且根因**不确定**。未创建/删除案例或操作桌面 APP。

### 2026-10-25 Sol：Bryrup WSL 工具链与历史 GOTM 来源复核

- **实测（本机工具链）**：Ubuntu 22.04 WSL 可用，含 CMake 3.22.1、GNU Fortran/GCC 11.4.0、Make 与 Git。此前“当前没有编译器”的说法仅适用于 Windows PATH，应以此条修正；本轮未编译或运行模型。
- **实测（官方历史源码元数据）**：公开迁移仓库最后的 GOTM 开发提交 `2895ac9449a2d2bfc31ba9f23406c6d841910d36`（2021-11-25）同时出现源码子目录版本 5.3.0 与外层 CMake 5.4.0 标识，都不是论文所述 5.2.2-au。可见 FABM 历史包含 `39101776e36f166380d62c452c4dabd64b174e40`（2021-04-27），但当前公开迁移项目没有 `au` 分支引用及可核验的论文匹配依赖固定点。
- **判断/状态**：Bryrup 精确执行器来源仍**不确定**。阻塞已由“缺工具链”收敛为“未恢复 5.2.2-au/FABM 精确源码与递归依赖固定点”；换用 5.3/5.4 仅能得到版本代理，不能称为论文等价或科学实测。Bryrup 执行与科学验证**未完成**。无案例创建/删除、无 APP 操作。

### 2026-10-25 Sol：Bryrup 1996–1999 观测与驱动时间窗对照

- **实测（观测/驱动文件检查）**：官方 Bryrup 原始 field-measurement CSV 在 1996-01-25 至 1999-12-08 有温度 622 行/83 个日期、氧含量 620 行/82 个日期。官方 WET v0.1.0 归档中的气象、入流和入流化学文件覆盖到 1999-12-31；原 `gotm.yaml` 仍于 1995-12-31 停止。存在可研究的四年时间重叠，但要另做显式扩展案例，不能改写原归档/论文设置。采样当地时区、深度配对、插值和质量标记仍需处理。
- **设计判断**：WET 1.0 论文的 Bryrup 案例采用 1D GOTM lake branch；产品目标是 GETM 3D。论文复现与产品 3D 应用是两个验证命题，不能相互冒充。来源：[WET 1.0 论文](https://gmd.copernicus.org/articles/15/3861/2022/)。
- **状态**：观测行与驱动时间窗检查为**实测**；重叠期模型运行、模型观测配对、Bryrup科学验证均**未完成**。没有启动/清理案例。

### 2026-10-25 Sol：52812 服务静态资源同步复核

- **实测（只读 HTTP/进程检查）**：52812 仍由 PID 15680 的仓库 `launcher.py --web --no-open` 进程提供，根页面 HTTP 200，run 状态 idle。根 HTML 仍写 `academic_ui.css?v=7`，但 CSS URL v7 与 v8 返回字节哈希均等于磁盘文件 `855f0c6122cc726d5924646fdbf59ccc3aedf9783f9f6add589256cf2236d996`，并带 `Cache-Control: no-cache, max-age=0`；页面脚本版本为 viz3d123/i18n16/app73，且包含体网格预设脚本。服务已提供当前 CSS 内容，版本查询串落后；这不证明用户已打开页面当前 DOM 或完整桌面视觉已更新。
- **限制**：CUA 当前未列出可复用浏览器标签，本轮没有新开或刷新 APP。用户桌面实际显示状态仍**未验证**。没有代码改动或案例操作。

### 2026-10-25 Sol：Bryrup 观测配对输入规范化

- **实测（观测文件整理与质控）**：由原始站点 CSV（SHA-256 `D5014A821E0D5F9B6BB0FEC33A1F6B1B7D0303997E5CD460A39118EEA3E81841`）生成 1996–1999 温度/氧记录，共1,242行。保留原始行号、记录 URL、原始 qualifier、质量标记、采样本地时间及显式 UTC offset；另生成 UTC 时间列和数值小数点列，不做插值或质量过滤。必填字段空值0，时区转换不一致0，本地日期不一致0，候选键重复组0。派生文件及方法见[`Bryrup observation extract`](../../../build/bryrup-observations-1996-1999-normalized-20261025/README.md)；CSV SHA-256 `B89EE6D96FEB0C737B8104FD69429566F630267A3281EF25F9D3707A0406BD8F`。
- **状态边界**：此表仅为观测来源的规范化与质量检查，属**实测观测数据整理**；尚未与模型时间/深度配对，也未计算技能分数。Bryrup模型运行和科学验证仍**未完成**。无案例启动/删除，无桌面 APP 操作。

### 2026-10-25 Sol：GOTM 5.2.2-au 精确发布路径复核

- **实测（官方来源指针）**：WET 1.0 论文的软件可用性栏给出 GOTM `v5.2.2-au` 精确 release 路径；AU 开发页仍列出 GOTM `au`、FABM `au`、WET `master` 的构建要求，并说明 GitLab 下载需要免费账户。当前匿名打开 release 会跳至 GitLab 登录页。来源：[论文软件可用性](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf)、[AU 开发页](https://projects.au.dk/wet/for-developers/)、[版本发布 URL](https://gitlab.com/WET/gotm/-/releases/v5.2.2-au)。
- **不确定/未完成**：精确版本有出版物指向，但当前是否能登录后下载、对应源代码 commit 与递归子模块固定点均**不确定**；本次没有访问账户、下载旧 release 或运行模型。Bryrup scientific validation 仍**未完成**。

### 2026-10-25 Sol：Lake Ravn 官方测站空间锚点复核

- **实测（源记录与GIS交叉检查）**：21000355/RAV1 原始官方 CSV 给出唯一测点 `GeoZone=32, X=552519, Y=6218243`。VanDa 官方数据录入清单默认坐标为 UTM / ETRS89 / 32N；丹麦测绘机构列明 EPSG:25832。按该坐标解释转换为 `(9.844418°E, 56.106400°N)`，并通过官方 Ravn `EPSG:25832` 岸线 polygon 与 `DYBDE=31` 深度带 polygon 的包含检查。后一字段仍为深度带类别 ID，不能当连续实测水深。观测 CSV 与 workshop `TEMP.obs`/`DO.obs` 的既有日期/深度/数值对应关系见[Ravn观测来源记录](ravn-official-observation-source-note-20261025.md)。
- **不确定/未完成**：原始 CSV 行没有显式 EPSG/datum 字段；VanDa 清单支持默认解释，几何交叉检查提供一致性证据，但不等于该行自身明确记载了 CRS。测站空间锚点已找到；目标 GETM 网格尚未审定/生成，故 `(i,j,k)` 映射、时间/深度支持和 GETM 3D 科学评分仍**未完成**。本轮未启动/清理案例，也未打开应用。
- **版本化 readiness 校正**：更新了 [`Ravn GETM 3D candidate assessment`](../../../build/ravn-getm3d-candidate-20261024-luna01/assessment.md) 与 `readiness.json`，撤回“官方观测没有测站位置”的过时阻塞描述；其余 bathymetry、river forcing、3D气象、生态配置迁移阻塞保持不变。

### 2026-10-25 Sol/Luna：床面播放补丁色标残留假设复核

- **源码检查（非黑片复现）**：检查 `viz3dWaterbodyRestyleGroups()` 时发现 bed 补丁属性表未列 `colorscale`，遂核对它是否能在生产播放条件下留下 VE 切换前的床面色标。`playbackTopologyKey` 包含 `ve`，而使用 `Plotly.update` 的补丁路径要求拓扑键相同；床面颜色分支恰在 `VE<=80` 与 `VE>80` 间变化，跨分支会回退 `Plotly.react`。同一 VE/诊断设置的帧播放中该色标分支固定，水深范围变化时 bed 的 `cmax` 已经更新。
- **结论**：否定“遗漏的 bed `colorscale` 播放补丁导致 VE 切换后残留旧色标”这一特定假设。未证明其他候选根因；没有代码修改或测试改动。
- **状态**：黑片仍**未修复**，唯一根因**不确定**；参考图保留 `（待补充：参考图的具体路径或链接）`。本轮没有启动/删除案例或打开桌面 APP，无桌面同步操作。

### 2026-10-25 Sol/Luna：frame19 三角显示模式匹配度对照

- **代理（headless 渲染，非科学验证）**：对同一 Erken frame19 / target26 温度层9只读帧，固定水深、VE=166.5×、生产默认相机、轴范围、宽高比、896×760视口和其他 trace，只将连续网格切到生产三角显示网络。连续模式 `_fullData` 为7条 trace，三角模式为8条并出现一条三角剖分显示 trace；两组阈值 `max(R,G,B)<40` 的 ROI 与全图近黑像素计数均为0。报告显式记录相机/轴构造输入，与 trace 审计和像素筛查分别列出。
- **来源与限制**：比较报告及图像位于[`frame19 triangle-mode comparison`](../../../build/bed-black-frame19-triangle-mode-compare-20261025-02/README.md)。引用的历史存档图能确认三角显示网可见，但未记录 UI 网格选择与相机坐标。当前 headless fixture 是代理证据，不是用户目标桌面复现；负结果不能证明修复或排除历史情况。
- **同步检查**：52812 首页 HTTP 200，引用 `viz3d.js?v=123`；该 URL 的响应 SHA-256 与工作区 renderer 相同（`06FCCA575190F05AB85F6E80130B42518E1C619504DFF96AC2381B2B1EAB0CB7`）。只读检查未打开/刷新桌面 APP；产品源未修改。
- **状态**：黑片仍**未修复**，根因仍**不确定**；完整用户流程、Erken/Lake Ravn/Bryrup/Arreskov 科学验证和桌面最终视觉验收仍**未完成**。本轮只生成渲染诊断材料，没有启动或删除模型案例。参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol/Luna：frame19 三角模式对照的控制条件纠正

- **证据更正**：既有 target26 三角/连续对照及其后补的精确输入元数据继续保留为历史记录，但此前“相机、轴范围、宽高比和视口匹配”的控制条件声明现标记为**无效/已被后续有效对照取代**。诊断 helper 的 JSON replacer 错误地把所有嵌套对象和数组（含 camera、轴范围、aspect、margin）替换为 `null`；Plotly 因而使用回退场景值。对应截图及 0 近黑像素计数不能支撑此前声称的匹配条件像素结论。初次 target96 默认视角尝试具有相同缺陷，图像保留但不进入有效对照结论。
- **有效补充（代理渲染，非用户设备复现）**：target96 有效对照从保存输入哈希 `85b2932d4149ff0e4b8e48667b374c072bf807dc2d46a879fafdf33c6e320a26` 重绘，历史回放审计哈希 `a433507f06b90694f5407cddff620b3157c432272eec010ccca8cd3fe8bf361c`。输入字段与 `_fullData` 捕获明确分列；两种模式的相机、轴、aspect 和 1410×905 视口输入均为非空且一致。连续/三角模式 `_fullData` trace 数为 7/8（后者含一条三角显示网络）；ROI 及整图 near-black (`max(R,G,B)<40`) 均为 0。target96 输入是 2020-DOY001 02:00，归档黑床截图为 06:00，仍有四小时差异；仅日期/网格/层/VE相同。结果和哈希见 [triangle-mode report](../../../build/bed-black-frame19-triangle-mode-compare-20261025-02/README.md)。
- **结论边界**：新结果仍是 SwiftShader headless 代理渲染，不能认作用户设备复现或证明历史截图条件。黑床仍未修复，唯一根因仍不确定。无应用源改动、案例运行或桌面 UI 操作。
- **精确产物指纹**：target96 输入 SHA-256 `85b2932d4149ff0e4b8e48667b374c072bf807dc2d46a879fafdf33c6e320a26`；回放审计 `a433507f06b90694f5407cddff620b3157c432272eec010ccca8cd3fe8bf361c`；序列化 viewport `{width:1410,height:905}` 哈希 `3bb89073abe82160994cfb07535c145a943c9177b005067b11eaae0352573fa9`；连续 PNG `f2fca12850620a928bec726831c48c3268d7403a1d9bb6ed7f5746b00dec57a4`；三角 PNG `6a4e28091de85d8179a19cb172c804bbf2f395d8c09c9780141877be6d937357`；并排 PNG `b0b7cf219a4bfafdcbcc95b5290cd5c7332e122a538033daf7a5fb223b271662`。

## 2026-10-25 Sol/Luna：服务同步、食性网络回归与床面生产路径复核

- **服务同步（本机 HTTP 实测）**：重启已确认的 `launcher.py --web --no-open --port 52812` 服务后，首页 HTTP 200 并引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`app.js?v=73`、`i18n.js?v=16`、`viz3d.js?v=123`。五个静态资源的服务响应 SHA-256 与工作区文件一致。没有打开或刷新浏览器窗口，因此实际窗口视觉仍未验收。
- **食性网络（代理回归）**：`node --test 3DWET/tests/test_ecology_foodweb_ui.js` 通过；合成 DOM 断言覆盖分类筛选、编辑器入口、关系行编辑、预览/应用、重载与拒绝状态，以及以鼠标/键盘聚焦三节点配置路径并同步高亮图中的节点、边和关系表行、清除焦点、显示相应端口标签。输出报告显示示例图包含12条已配置边（含POM），没有三节点闭环。`pytest -q tests/test_wet_foodweb.py` 13/13通过，覆盖食性映射编译与无效状态/单位拒绝。这些均为代理测试，不验证原生 FABM 实际注册、模型运行摄食通量或生态科学合理性。
- **床面生产路径（Luna 源码审计）**：唯一生产 bed `mesh3d` 构造在 `viz3d.js` 的 `lakeTraces()`；静态及动态水体路径都复用它，床面带顶点 intensity、显式色标/范围与床面角色播放更新，未找到一个可证实遗漏这些属性的第二生产分支。历史 v86 intensity 对照与 v123 02:00 target96 对照都仍为代理，不能确认当前黑片根因。无猜测性代码补丁；黑片仍**未修复**，根因**不确定**。下一项有区分力的证据是从原始06:00黑片场景获取实际 `_fullData`、几何、相机/坐标轴/VE并在相同目标浏览器与输入做控制对照。
- **案例清理检查**：`Erken_real_20200101_24h_stage/Input` 含原始观测、气象与GIS资料且被审计引用；`output` 和 `analysis` 仅有说明文件，没有模型输出。因此没有删除该案例，也没有启动新案例。
- **仍未完成**：完整用户流程；Erken、Lake Ravn、Bryrup、Arreskov完整科学验证；食性网络模型运行时验证；原始用户床面参考图位置与当前桌面窗口视觉验收。参考图保持 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 Sol：床面播放路径回归复核

- **代理（现有测试）**：`node --test 3DWET/tests/test_viz_waterbody_patch.js` 通过 **26/26**。覆盖高 VE 床面独立深度色标、跨高 VE 阈值重建床面、低 VE 中性色标、显示/隐藏床面诊断、播放帧更新与相机保留，以及拓扑/trace 形状变化时回退完整渲染。
- **范围限制**：这是合成 DOM / Plotly patch 行为测试，不会绘制用户 GPU 黑片场景，不等价桌面实测，也不能确认唯一根因或证明用户报告缺陷已修复。黑片状态仍**未修复**，根因**不确定**；本轮没有启动模型案例、修改案例或打开应用。

## 2026-10-25 Sol：06:00床面输入可恢复性检查

- **未完成（只读文件盘点）**：历史只读 Erken 20-frame 案例目录只含 `bathymetry.nc`、`fabm_init.nc`、`meteo.nc` 等输入，没有 GETM 历史结果 NetCDF。黑片诊断目录仅保存 `target26` 与 `target96` payload；target96 明确为02:00，未发现可重取06:00的本地模型结果文件。因此无法从现存历史输出中只读重建与存档黑片截图完全同一时刻的数据帧。
- **下一步证据**：需从用户原始场景或其导出的结果中取得06:00床面数据、完整 `_fullData`、几何及相机/坐标轴/VE。缺少该组输入前，不以邻近时刻代替，不启动新案例来声称复现。黑片仍**未修复**，根因仍**不确定**；本轮没有运行或删除案例。

### 2026-10-25 Sol：Erken小时观测源复核（用户授权后）

- **实测（本地源复核）**：无需重复下载；复核既有 SITES 小时剖面 CSV 与 provenance，文件 SHA-256 为 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`，与 SITES 元数据一致。CSV 包含 `2020-01-01 06:00` 小时记录；该时间标签及 UTC+1 解释仍需和模型时间轴确认。
- **授权/来源**：用户已明确授权接受 SITES CC BY 4.0 数据说明并下载。来源为 Erken Laboratory (2024), PID `11676.1/Kq6E7t69ZyKJejMcANJQVoHP`，原始记录 https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP 。
- **边界**：该记录只确认观测侧有对应小时，不补足同次运行的 GETM 输出、渲染状态或床面三角形数据；黑片仍**未修复**，根因仍**不确定**。本轮没有重跑案例，也没有打开/刷新桌面应用。

### 2026-10-25 Sol：历史床面网格与现存 Erken 输出交叉核对

- **实测（只读文件比对）**：发现并读取现存 Erken real-location baseline `build/real-use-validation-20261021/erken-real-location-24h/baseline/output/output.nc`。其中 24 个逐小时输出覆盖 2020-01-01 01:00–2020-01-02 00:00；API 只读查询在索引 1/5 返回 02:00/06:00，网格为 10×18×44、376 湿格。
- **几何匹配**：与历史 frame19 诊断载荷的投影坐标完全一致；376 个湿格的 `bottom` 与该 NetCDF `bathymetry` 最大差值小于 `1e-6 m`。因此现存 baseline 可复用同一平面网格和床面深度做几何侧核验。
- **不匹配项/限制**：历史 frame19 载荷的温度范围为 8.3006–14.8710 °C；现存 Erken baseline 在 02:00/06:00 的第9层为 2.1800–2.1813 / 2.1800–2.1836 °C。它不是历史截图相同的动态场状态，不能代替原始阳性复现。截图相机/完整 `_fullData` 仍未记录。
- **结论**：新增可复用的实测底形与坐标对照，但它没有证明黑片修复，也不能锁定根因。黑片仍**未修复**、根因**不确定**；Erken科学验证仍**未完成**（既有配对保持**代理**）。本轮只读复用结果，没有创建、删除或运行案例，没有打开/刷新桌面应用，也没有源码更改。

### 2026-10-25 Sol：52812 仓库服务静态资源同步核验

- **实测（HTTP）**：复用已有 52812 服务，首页 HTTP 200，模板版本串与工作区一致：`academic_ui.css?v=8`、`studio_icons.js?v=2`、`app.js?v=73`、`i18n.js?v=16`、`viz3d.js?v=123`。逐字节 SHA-256 核对上述五个已服务资源，均与当前工作区对应文件一致。
- **边界**：没有打开、刷新或新建 APP/浏览器标签；这核实服务返回的 HTML 和静态文件，不证明原生 WebView/用户现有页面 DOM 已重新加载，也不构成桌面视觉验收。黑片仍**未修复**，根因**不确定**；其他案例与完整流程状态不变。

### 2026-10-25 Sol：退化面法线候选核对

- **代理（静态几何核算）**：对历史 frame19 18×44 payload 按现行 `lakeCellEdges()`/`buildLakeGeometry()` 结构计算，网格 dx/dy 均为250m；376个湿格组成752个床面三角形，每片水平投影面积均为31,250m²，不存在零面积面。Plotly Mesh3d 文档将 `facenormalsepsilon`（默认1e-6）描述为避免退化几何下的法线计算问题；该候选对这份规则网格载荷不受支持。参考：[Plotly Mesh3d属性](https://plotly.com/python/reference/mesh3d/)。
- **结论边界**：该几何核算不是黑片渲染复现；仍不能排除投影/深度精度、绘制顺序、运行时 `_fullData` 或 GPU 交互。黑片仍**未修复**、根因**不确定**。

### 2026-10-25 Sol：winding 反转代理对照复核

- **代理（渲染诊断，非科学验证/非用户桌面复现）**：Sol 独立检查 `build/bed-black-winding-control-20261025-rerun-01/`。在固定的历史 v86 02:00 frame19 payload、相机、设备、视口和 Plotly 下只交换床面三角形 `i/j`。全场与 bed-only PNG 均逐像素一致，像素差 0，近黑计数未变；审计显示 `_fullData` 除内部 uid 外的显式床面属性一致。
- **状态**：本结果只表明该单一代理条件下 winding 反转无可见效果；不能推广至缺失的用户 06:00 桌面场景，不能确认唯一根因，也不是修复。黑片**未修复**、根因**不确定**。完整用户流程与四湖科学验证状态不变（均未全部完成）。本轮没有启动/删除案例、修改产品代码或打开应用。

### 2026-10-25 Sol：三角网络 3D 表现与科研 UI 参考核验

- **代理（源码/自动化验证，不是桌面视觉实测）**：Sol 抽查 Luna 对现有实现的规格审阅。`viz3d.js` 保持水湿单元稳定剖分，三角模式显示低调边界线和面片着色、可选连续面、可信拓扑缺失时拒绘，并将层间辅助线限制在具备数据的多层网格；元数据显示其为 display-only。视图状态/模板文案区分显示剖分、辅助抬升、垂向倍率与求解器物理拓扑/水深。现有相机与高度控制测试以及网格元数据测试由实现代理运行 **40/40** 通过；更宽 render/style 测试出现 **20 项** VM fixture 缺少 `URL` 的错误，不纳入功能通过结论。
- **服务同步（HTTP 实测）**：只读探测 52812 首页返回 200；实现代理核对首页所引用的 `view_controls.js?v=8`、`viz3d.js?v=123`、`app.js?v=73` 均 HTTP 200，响应 SHA-256 与工作树对应文件相同。没有代码修改，因此没有重启/热加载；没有打开或刷新桌面 APP。
- **Sol 研究与取舍**：新增 Cytoscape 官方手册作为食性/网络属性映射参考；结合 ParaView、napari、QGIS 官方手册，采用“数据画布优先、图层职责独立、属性有显式映射、相机/倍率可直接控制”的科研交互原则。色彩方案仍是低饱和纸白/石色、湖蓝灰、灰绿与少量赭石的产品艺术指导，不声称客观排名，也不复刻品牌视觉。来源及理由写入 [设计规格](../../superpowers/specs/2026-10-25-restrained-scientific-3d-design.md)。
- **限制与状态**：源码/DOM 测试和静态资源字节一致属于**代理**，未在实际桌面窗口检查“更强 3D 表现力”、全站最终 UI 或新加载状态；参考图仍为 `（待补充：参考图的具体路径或链接）`。该核验与黑片根因/修复无关，黑片仍**未修复**、根因**不确定**。完整用户流程以及 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍未全部完成。没有启动/删除案例。

### 2026-10-25 Sol：06:00 存档输出载荷可恢复

- **实测（只读数据提取）**：用 Flask test client 指向预存 Erken real-location baseline 读取 `output.nc` 索引5，恢复 `2020-01-01 06:00`、layer 9、target96 温度/床面/拓扑载荷到 `build/bed-black-frame19-readonly-probe-20261025/frame06-2020-target96-layer9.json`。API HTTP 200；shape 1×18×44，source shape 10×18×44，stride 1×1×1、376湿格，拓扑有效。没有运行模型或更改案例。
- **代理限制**：该数据的 layer-9 温度约 2.1800–2.1836°C，与历史 frame19 阳性探针的 8.3006–14.8710°C 不同；只能补齐时间标签/床面几何，不等于历史截图相同变量场。后续任何截图仍须列为代理，除非取得与原图一致的完整输入和设备状态。
- **状态**：黑片仍**未修复**、根因仍**不确定**；完整用户流程及四湖科学验证未全部完成。参考图仍为 `（待补充：参考图的具体路径或链接）`。本轮没有启动/删除案例或打开 APP。
- **精确指纹**：原 NetCDF SHA-256 `63a96af290181df23d840c14d1aec969fc690f8aefad54ea529030991cd28187`；提取 JSON SHA-256 `fd251973feb8b53b3291f369ef1843d1a2fff678f690cff2b2998edbea290614`；NetCDF time[5] 解码为 `2020-01-01 06:00:00`。

### 2026-10-25 Sol：06:00 当前 renderer 的分条件代理验收

- **代理**：我独立检查 `build/bed-black-current-render-frame06-20261025-02/README.md`、`renderer-report.json` 与联系图。当前 renderer 以同一只读Erken输出分别渲染200×静态bed、50×temp叠层、166.5×temp叠层。A/B/C各8/9/8条trace；床面均1504顶点/752面；B含356面wet boundary wall，其他两组按当前策略无墙。三场景全图/ROI RGB<40均为0；25条逐trace截图也均为0。
- **Sol视觉复核**：输出联系图未显示历史截图中的近黑床面片；然而 payload 温度约2.18°C，而历史阳性载荷约8.30–14.87°C，且原截图 camera 未完整保存。该 headless SwiftShader 检查因此仍是**代理**，不能说已修复或复现用户症状。
- **状态**：黑片**未修复**、根因**不确定**。当前 UI/3D 未做桌面窗口视觉验收；完整用户流程和Erken/Lake Ravn/Bryrup/Arreskov科学验证仍未全部完成。只读复用已有输出，无模型启动/案例清理/APP窗口操作。

### 2026-10-25 Sol：存档黑片截图时刻复核与记录更正

- **实测（本地截图标题）**：黑片归档并非单一时刻：`erkens-black-bed-remains`、`erken-black-bed-final`、`erken-black-bed-flatshading` 三图标题记录 2020-DOY001 02:00；`erken-bed-color-range-before/after` 两图记录同日 06:00。两组图均显示黑片。
- **代理（02:00版本对照）**：现有 v86 vs v123回放使用02:00 frame19 target96温度载荷（8.3006–14.871°C）及相同床面几何/视角；v86图出现近黑区域，v123图未出现。床面`color/intensity/colorscale/lighting` 属性同时改变，所以只能支持“当前源路径在此历史渲染代理下不出黑”，不能隔离具体根因或推翻用户桌面仍未修复的事实。
- **更正**：此前“target96 02:00 与归档黑床截图 06:00 相差4小时”仅适用于 06:00 色标截图；不适用于 `erken-black-bed-remains/final/flatshading` 这组02:00归档图。现存 real-location baseline 的06:00温度约2.18°C，也与06:00旧图温度范围不符。
- **状态**：用户参考图仍为 `（待补充：参考图的具体路径或链接）`；黑片**未修复**、根因**不确定**。历史v86/v123和06:00渲染结果均为代理，当前桌面窗口未验收。没有启动或清理案例，没有打开APP。

### 2026-10-25 Sol：现有桌面/UI 通道只读盘点

- **实测（通道状态）**：只读取当前 CUA surface inventory，没有打开或刷新应用；当前没有已连接的 Windows 原生应用，也没有 IAB/MCP Apps 标签页。故此刻无法从用户桌面采集新版本 DOM、WebGL `_fullData` 或屏幕图；服务端 HTTP 静态资源匹配不能替代桌面可见状态。
- **状态**：用户桌面视觉验收**未完成**。没有启动/关闭任何应用或案例；保留此前用户提出的避免重复打开桌面应用要求。

### 2026-10-25 Sol：Erken 已有24小时输出与小时观测剖面配对核算

- **代理（模型—观测配对，不是完整科学验证）**：只读复用 baseline `output.nc` 和 SITES Erken anchored TW-profile 小时 CSV，未运行模型。时间标签配对为 2020-01-01 01:00 至 2020-01-02 00:00；每小时在最近湿格 `(y=8,x=36)` 与观测剖面逐深度线性插值配对，仅纳入实测深度 1.0–15.5m 内的模型层中心，共 192 点/24个时次。观测锚点与最近湿格相距 102.32m，未作水平插值。
- **数值**：模型减观测总体 bias `+0.05959°C`、RMSE `0.06274°C`、MAE `0.05959°C`、最大绝对误差 `0.10668°C`。这些统计只描述这一个 24 小时 exploratory proxy run 与一个测点的配对结果，不是验收阈值或模型 skill 结论。
- **关键限制**：SITES 时钟标注 UTC+1；NetCDF time units 为 `seconds since 2020-01-01 00:00:00`、未注明 timezone。本次按相同日时标签匹配，没有加时差；该时钟对应关系仍待确认。模型存在云量/蒸发默认代理及生态、营养盐、流量代理；最近湿格与传感器非同点；15.5m 以下无观测，已排除深层，不把 endpoint hold 当实测。
- **产物**：配对脚本 [`pair_2020_01_01.py`](../../../build/erken-observation-pair-20261025/pair_2020_01_01.py) 与逐点/逐时指标 [`paired-metrics.json`](../../../build/erken-observation-pair-20261025/paired-metrics.json)。观测 CSV SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`；模型输出 SHA-256 `63a96af290181df23d840c14d1aec969fc690f8aefad54ea529030991cd28187`；指标 JSON SHA-256 `0ef26522875509be13608e53c8f51d5589b48fe95e7699abeda41afb81a8e93b`。
- **状态**：该 Erken 项目保留为**代理**，科学验证仍**未完成**；其他三个湖案例和完整流程仍**未完成**。参考图继续保留 `（待补充：参考图的具体路径或链接）`。本次未创建、删除或运行案例，未改应用源码，也没有打开/刷新桌面 APP，因此没有应用同步动作。

### 2026-10-25 Sol：完整用户流程 attempt62 失败门禁溯源

- **代理（隔离副本工作流）**：复核 `build/full-workflow-20261025-attempt62/round.json` 与 `ui/ui-report.json`。external workflow、功能矩阵、结果模式、SciPy、ABC 与 restart 六阶段均通过；UI 检查 9/10 通过，含预处理/网格保存、初值重载、模块/网络/湖点、导航/诊断/运行、结果仪表板、校准、结果文件、语言持久化、缩放/导出。它们来自隔离副本及合成数据，不等于正式桌面完整流程或科学验证。
- **唯一未通过项**：ETA/完成/失败提醒检查标为 incomplete：合成运行到 600/600 并完成，失败状态仅用模拟 API 检查应用内 toast；WebView 系统通知权限提示仍挂起，FABM 状态汇总没有证据。记录见 `build/full-workflow-20261025-attempt62/ui/eta_completion_failure_notifications.txt`。
- **根因**：源码 `3DWET/app/static/js/app.js` 的 `startRun()` 无条件发起 `Notification.requestPermission()`（当 permission 为 default），所以普通模型运行会触发系统权限 UI。页面本身已经具有无需系统权限的持久进度/ETA/终态面板和失败 toast。已交由 Luna 实现显式选择的桌面通知启用入口；普通启动路径应不再弹权限提示，应用内提醒继续默认工作。
- **状态**：attempt62 整体**未完成**；当前 52812 服务 HTTP 200 且资源标签为 `app.js?v=73`、`viz3d.js?v=123`、`i18n.js?v=16`、`academic_ui.css?v=8`、`studio_icons.js?v=2`。没有桌面可见窗口通道，不据此宣称现有原生窗口已加载当前版。没有新启动或删除案例，也没有打开 APP。

### 2026-10-25 Sol：通知入口修复与当前源码 UI 同步核对

- **实测（自动化 WebView UI smoke，隔离临时模型目录）**：运行 `3DWET/app/launcher.py --ui-smoke` 一次，EdgeChromium 实际渲染页面检查通过：document complete、应用布局可见、pywebview bridge ready、本地 health ready、语言包可用、Chart/Plotly/Leaflet 加载、模型状态 idle。测试窗口由 harness 自动关闭；临时服务端口 60880 已退出。此为源码 UI smoke 实测，不代表用户常驻桌面窗口已经打开或完成目视验收。
- **实测（源码服务同步）**：当前既有 52812 源码服务仍 ready，model root 指向仓库 `3DWET`，首页缓存版本为 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=123`、`i18n.js?v=17`、`app.js?v=74`。该服务没有新建可见窗口；是否已加载到用户之前看到的原生窗口，仍**未确认**。
- **代理（通知权限行为测试）**：Luna 对普通启动不再请求系统通知权限、显式点击后再请求的改动通过 3 项聚焦 Node 自动化测试（3/3）。这是源码/DOM/模拟权限测试，不是 Windows 原生权限交付的端到端实测。
- **工作流状态**：attempt62 原 UI 9/10 的历史报告保留原样，不改写为全通过。通知权限弹窗的源码触发路径已移除普通启动自动请求，并提供用户主动开启入口；应用内状态面板仍默认可用。attempt62 的 FABM 状态审计、用户桌面完整流程及失败通知在正式 WebView 的端到端验证仍**未完成**。
- **边界**：本次仅运行 UI smoke，没有启动或删除湖泊案例，也没有声称科学验证完成。黑色床面片仍**未修复**，唯一根因**不确定**；Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍未全部完成。参考图路径继续保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：当前源码 attempt65 后端验收

- **代理（隔离合成工作流）**：在全新目录 `build/full-workflow-20261025-attempt65/`、新 seed `2026102506` 下运行六个后端阶段。`external`、`features`、`results`、`scipy`、`abc`、`restart` 全部 `passed=true`；六个报告 SHA-256 已写入 `round.json`。版本锁 `93cef1326017fed4150ff1419c707fd204b5860e4740cdf89b2b8675334efdef`，ledger 状态 `awaiting_ui`。该工作流使用生成的随机湖与合成观测，结果是代理工程门禁，不是任何真实湖泊科学验证。
- **版本过期记录**：attempt63 的 UI 流程记录包含常规流程、失败/ETA通知等实测界面操作，但 round 被记录为 `failed`，因为其 `viz3d.js`/`index.html` 来源版本早于随后修改；attempt64 同样因当前源码哈希不匹配，在完成必要记录后记为 `failed`。两轮日志留作历史代理诊断，不拿来接受当前版本。
- **实测（同步服务）**：仓库源码服务 52812 健康，model root 为当前 `3DWET`，静态资源 `viz3d.js?v=123`、`i18n.js?v=17`、`app.js?v=74`。当前 CUA 浏览器 surface 无可复用标签；本次未再打开桌面应用或浏览器窗口，所以 attempt65 的同版本 10 项 UI 验收尚未做，round 保持 `awaiting_ui`。
- **案例清理边界**：attempt65 使用新隔离模型根，未复用或覆盖旧合成案例；attempt63/64 的证据目录保留供审计。没有启动 Erken、Lake Ravn、Bryrup、Arreskov。
- **总体状态**：黑色床面片仍**未修复**、根因**不确定**；完整用户流程与指定案例科学验证仍**未完成**。参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-26 Sol：attempt65 当前版本局部回归

- **代理（自动化组件/DOM 覆盖）**：5 个 Node 用例通过：普通运行不请求系统通知权限、显式开启才请求、无权限时 ETA/进度/终态回退、通知去重和终态呈现、食性网络家族过滤/编辑预览应用/重载拒绝行为，以及网络无障碍焦点与单一编辑器；5/5 pass。
- **代理（科研主题样式测试）**：`3DWET/tests/test_ui_theme.py` 3/3 pass。此为样式约束自动化测试，不代表用户桌面视觉验收。
- **未完成项**：attempt65 的完整 UI checklist 尚未执行；组件回归不替代十项用户流程交互证据。黑色床面片仍未修复，四个指定湖泊科学验证状态不变。

### 2026-10-26 Sol：attempt65 隔离 UI 渲染 smoke

- **实测（无头 Edge 页面渲染）**：对 attempt65 的隔离模型根启动 web 服务，并在隐藏、独立的 Edge profile 渲染当前源码首页。document complete、页面布局可见、语言初始化完成、health ready、模型 idle，Chart/Plotly/Leaflet 均加载；health 返回的 model root 与 attempt65 一致。实际加载资源含 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=123`、`i18n.js?v=17`、`app.js?v=74`。渲染截图和结构化结果分别见 `build/full-workflow-20261025-attempt65/ui/headless-ui-smoke.png` 与 `headless-ui-smoke.json`。
- **边界**：这是实际浏览器页面渲染 smoke；采用 `--web`，所以 pywebview bridge 不存在属于预期，不能据此声称桌面 bridge 实测通过。Edge headless 进程与 53517/65494 一类临时服务已结束；用户桌面 APP 未打开。
- **验收状态**：上述 smoke 只验证同版本页面渲染、资源和隔离模型根，不覆盖 workflow_acceptance 所需的十项真实 UI 交互，attempt65 仍 `awaiting_ui`。黑片仍未修复；四湖科学验证仍未全部完成。

### 2026-10-26 Sol：attempt65 合成案例页面导航与 3D 表现检查

- **实测（无头浏览器 UI 交互；案例为代理数据）**：从案例管理 UI 加载隔离的 `Imported Random Lake`，案例徽标和仪表盘激活状态匹配；19 个导航路由均激活了对应页面。随后在 3D 面板选中 `temp`，实际 Plotly 场景有 10 条可见 trace（含 `mesh3d` 与 `scatter3d`），三角剖分、变量色带和湖盆可见。截图：`build/full-workflow-20261025-attempt65/ui/headless-ui-smoke.png`；结构化观测：`headless-ui-smoke.json`。
- **实测（显示控制）**：三角网格画面由自动倍率改为 50× 后，镜头仰角方向保持不变（计算差 0°）；单独把镜头控制改到 47° 后，读数与 Plotly 相机方向为 47°。这验证的是显示层相机/垂向显示控制在该合成湖体中的分离，不涉及求解器几何或真实湖泊表现。
- **状态边界**：这是 `attempt65` synthetic proxy 的 UI/render 实测，不能称为 Erken/Lake Ravn/Bryrup/Arreskov 科学验证，也没有复现或修复黑色床面片。页面 smoke 使用 web renderer，无 pywebview bridge；桌面 bridge 与完整 10 项 checklist 仍未验收。attempt65 round 继续为 `awaiting_ui`。
- **同步与清理**：52812 当前源码服务仍健康且资源标签匹配 v74/v17/v123；临时 headless Edge 与 attempt65 HTTP 服务已关闭。未打开桌面窗口，也未创建第二个合成案例。

### 2026-10-26 Sol：attempt65 十项完整 UI 流程门禁

- **代理（版本绑定的 UI 验收草案）**：`build/full-workflow-20261025-attempt65/ui/ui-report.json` 绑定 seed `2026102506` 与源码版本 `93cef1326017fed4150ff1419c707fd204b5860e4740cdf89b2b8675334efdef`。十项 checklist 为 **0 项完成、10 项未完成**；报告逐项记录证据与缺失操作。现有无头 smoke 仅覆盖案例加载、19 路由、3D 温度网格及部分镜头控制，不能代替上传/保存、参数重载、网络编辑、UI 求解、校准、结果管理、语言持久化、全结果模式和通知终态等流程。没有执行 `--review-ui`，`round.json` 保持 `awaiting_ui`。
- **窗口处理**：使用隐藏的 Edge/CDP 与隔离 web 服务，无可见桌面窗口；临时服务和 headless Edge 已结束。没有重复打开桌面 APP。
- **状态**：完整用户流程仍**未完成**；黑片仍未修复，根因不确定；四个指定湖泊科学验证仍未全部完成。

### 2026-10-26 Sol：黑片决策复核与网络/UI 局部回归

- **代理（实现审查）**：GPT-6 Luna 中复核了当前生产床面绘制逻辑、矩阵和现有测试；没有生产改动。Sol 高确认基线输入不匹配且多个渲染属性联动变化，拒绝将代理渲染无黑片当作目标修复。黑片仍**未修复**、根因**不确定**；区分性证据已列入 `black-bed-cause-matrix.md`。
- **代理（代码回归）**：通知权限/回退/终态 3 项、食性网络家族过滤与编辑/应用/重载拒绝 1 项、网络路由与无障碍编辑器 1 项，Node 共 **5/5** 通过。科研主题 CSS 约束中的 **3/3** 测试函数通过（以 Python 直接调用测试函数；环境未安装 pytest）。这些是组件级检查，不等于完整用户流程验收。
- **实测（页面视觉观察）**：复核 attempt65 隐藏 Edge 3D 截图，暖纸色与低饱和灰绿界面已呈现，模型窗口有蓝色三角湖盆网格和变量色带；该图来自 Imported Random Lake 合成代理数据，不能视作四湖验证或桌面目视验收。
- **同步/窗口**：52812 现有服务返回 HTTP 200，资源标签为 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=123`、`academic_ui.css?v=8`、`studio_icons.js?v=2`。未修改源码、未重启服务、未打开桌面窗口。
- **仍未完成**：attempt65 UI checklist 0/10；四湖科学验证仍未全部完成；黑片修复等待目标现场可比证据。

### 2026-10-26 Sol/Luna：attempt65 隔离 UI 动作验收进展

- **代理（同版本/同 seed 合成流程）**：GPT-6 Luna 在 attempt65 `Imported Random Lake` 上使用隐藏 Edge/CDP 实际操作，版本 `93cef1326017fed4150ff1419c707fd204b5860e4740cdf89b2b8675334efdef`、seed `2026102506`。检查级 **5/10 通过，5/10 未完成或部分完成**。通过：初始条件保存/重载；网格、模块、点位与食性网络页面查看；地图/2D/3D 结果模式；语言包导入/启用；诊断修复和 UI 求解器运行。详情见 `build/full-workflow-20261025-attempt65/ui/ui-report.json`。
- **实测（隔离合成案例 UI）**：预检 0 blockers；通过 UI 启用 CFL 检查并重检后仍 0 blockers（剩1项输出量提醒）；UI 启动 solver 完成600/600步，约6.14秒，捕获中途 ETA 与终态。此为 Imported Random Lake 合成代理流程，不是四湖科学验证。
- **代理（失败通知路径）**：实际调用 `pollRunStatus()`，注入标记为合成的 failed API payload，页面展示失败摘要、toast 与应用内通知记录。非真实 solver 失败；Edge不支持原生 Notification API，未测试原生通知/权限。
- **部分/未完成**：校准 UI 已上传两行合成温度数据并显示2配对点（RMSE 0.0524、MAE 0.0504等），SciPy job 被触发但未捕获终态，ABC-SMC未启动，故该项部分完成；重复文件扫描识别1个副本，但自定义确认/回收/恢复步骤卡住；2D export 点击重放未复现下载，故视图控件项部分完成；完整预处理上传/网格/保存流程未执行；原生通知及完成态通知未验收。
- **保护与清理**：原案例26/26文件与新快照 SHA-256 一致；app/data 3/3文件恢复一致；round.json SHA-256 `7f4f34779964269db7683741bbf506f453fbc0098b0fd0febdf75db7b24cfc8c` 未变，状态仍 `awaiting_ui`。临时副本、CSV、Edge profile、Edge和隔离服务已清理。未运行`--review-ui`、未启动Erken/Ravn/Bryrup/Arreskov、未打开桌面窗口。
- **总体状态**：完整用户流程仍**未完成**；黑片仍**未修复/根因不确定**；四湖科学验证仍未全部完成。当前源码服务 52812 返回 HTTP 200，资源版本为 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=123`、`academic_ui.css?v=8`、`studio_icons.js?v=2`。

### 2026-10-26 Sol：attempt65 完整 UI 验收更新

- **代理 / 实测边界**：attempt65 的同版本 UI 清单目前为 **6/10 项通过、4/10 项未完成或部分完成**。六项通过的是预处理上传/网格/保存、参数重载、模块/网络/点位页面、诊断修复并运行合成求解、地图/2D/3D模式、语言包切换持久化；其中输入与求解案例是 Imported Random Lake 合成代理，不能作为四湖科学验证。
- **未完成**：校准只捕获两点合成对比及 SciPy 作业启动，没有终态或 ABC-SMC；结果文件重复项重放未达到页面就绪条件，没有发生扫描/确认/恢复；缩放/拖动等局部通过但导出未生成文件；失败通知来自合成 API payload，原生系统通知与完整终态通知未验收。证据见 `build/full-workflow-20261025-attempt65/ui/ui-report.json` 与 `phase1-duplicate-ui-20261026-retry2.json`。未运行 `--review-ui`，round 仍 `awaiting_ui`。
- **清理与完整性**：重复 UI 重放创建的唯一测试副本及文件夹已删除；Imported Random Lake 26 个文件清单、`app/data` 三个文件与运行前一致；round SHA-256 仍为 `7f4f34779964269db7683741bbf506f453fbc0098b0fd0febdf75db7b24cfc8c`。本轮隔离 Edge profile 与服务已结束；没有打开可见桌面应用。
- **总体状态**：黑色床面片仍**未修复**、根因**不确定**；Erken、Lake Ravn、Bryrup、Arreskov 的目标 GETM 3D 科学验证仍未全部完成。代理结果未升级为实测科学验证。

### 2026-10-26 Sol：黑片历史重放单变量强度探针

- **代理（受控渲染）**：对历史 v86 黑片 bed-only trace 仅增加 `intensity = customdata`（1504 个顶点水深值），沿用原几何、相机、视口和 Plotly/ANGLE 渲染器。固定 ROI 的近黑像素从 245,173 降至 0；单独改绿色或光照的既有对照仍为 245,173。完整产物及解释见 `build/bed-black-intensity-isolation-run-20261026/` 和 `black-bed-cause-matrix.md`。
- **Sol 判断**：显式顶点强度/由此触发的自动色标映射是该归档代理复现中的有效候选因素；尚不能从自动映射内部、WebGL 差异和其他联动中确定唯一根因。当前 v123 产品已有显式床面强度数组与深度色标，但桌面目标现场未验证。黑片仍**未修复**、根因**不确定**，不能把历史代理像素改善写成桌面修复验收。
- **同步与清理**：未改产品源码，故未重启桌面程序；未打开可见应用窗口，没有创建或删除模型案例。

### 2026-10-26 Sol：床面/3D 网格渲染回归检查

- **代理（代码级）**：执行 `node --test 3DWET/tests/test_lake_display_mesh.js 3DWET/tests/test_viz_waterbody_patch.js`，**77/77** 项通过。覆盖湿网格三角显示、未知/干单元不桥接、独立床面深度强度、高垂向倍率保留床面、倍率阈值重建、三角网络显示不改变原模型拓扑，以及播放帧相机状态等。
- **验收边界**：这些测试验证代码契约与代理网格，不是用户桌面的黑片复现，也不是四湖 GETM 科学验证；不更改黑片“未修复/根因不确定”状态。
- **桌面同步**：产品源码未改动；源码服务 52812 的 `/api/system/health` 为 ready、HTTP 200，页面资源仍为 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=123`、`academic_ui.css?v=8`、`studio_icons.js?v=2`。未打开新窗口。

### 2026-10-26 Sol：校准与 ABC-SMC UI 完整性更新

- **实测 UI 交互 / 代理数据**：隐藏 Edge 在 attempt65 的 Imported Random Lake 合成流程完成率定点创建、CSV 导入、2 个观测—模拟配对和 SciPy L-BFGS-B。随后用合法 ABC-SMC 预算（population 2，最多 4 次模拟）完成作业，engine=`pyabc-abcsmc`、success=true。观测和模型数据均为合成代理；不构成任何指定湖泊验证。
- **验收计数**：attempt65 UI checklist 更新为 **7/10 通过、3/10 未完成或部分完成**。仍未完成：结果文件重复项清理/恢复，完整视图控件与导出，完整 ETA/原生系统通知验收。round 仍 `awaiting_ui`，未运行 `--review-ui`。
- **清理与同步**：case、`app/data` 和 round 均哈希恢复基线，临时 CSV、隐藏 Edge profile 与服务关闭。产品源码未改；未打开可见桌面窗口。

### 2026-10-26 Sol：Erken SITES 实测水温配对（24 h，局部验证）

- 已在用户授权下接受 SITES CC BY 4.0 数据说明并下载官方 Erken anchored TW-profile CSV（2017-06-28 至 2024-09-14）。解包 CSV SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e` 与数据门户元数据一致；来源、PID、许可证、原始压缩包、许可 PDF 和下载位置见 `build/full-workflow-20261025-attempt65/ui/workflow-downloads/erken-2017-2024-ccby4/` 及同级 ZIP。
- **实测（有限窗口）**：将 SITES UTC+1 的 2020-01-01 01:00 至 2020-01-02 00:00 共 24 个实测剖面，与已有 Erken-real-location-24h GETM baseline 输出逐时配对。站点最近湿格距离 102.3 m；对 50 个名义传感器深度（1–15.5 m）使用逐帧 `zc` 将模型温度垂向线性插值到传感器深度，共 1,200 个观测—模型对。Bias（模型−观测）+0.0536°C、MAE 0.0542°C、RMSE 0.0591°C、NSE −3.23、相关系数平方 0.271。逐点结果及方法记录：`build/real-use-validation-20261021/erken-real-location-24h/evidence/erken_temp_obs_model_pairing_2020-01-01_24h.json` 与 `erken_temp_obs_model_pairs_2020-01-01_24h.csv`。
- **判断**：这是实测物理水温的 24 h 单站局部配对，且模型初始温度使用 00:00 实测剖面；后续 24 小时作为评分窗。负 NSE 说明该窗口水温预测表现较差。仅因输入和观测为真实资料，不可把这一结果外推为完整 Erken 验证；营养盐/生态初值仍有代理项，底部未观测，单日单点也不代表季节或全湖表现。Erken 总体科学验证仍**未完成**，但现有 evidence 中新增了一项明确标记为实测的短窗水温比较。
- 数据引用：Erken Laboratory (2024), *Physical variables - lake temperature profile from Erken, year-round anchored TW-profile, 2017-06-28–2024-09-14* [Data set], SITES, [PID 11676.1/Kq6E7t69ZyKJejMcANJQVoHP](https://hdl.handle.net/11676.1/Kq6E7t69ZyKJejMcANJQVoHP), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 本报告使用该数据；对 CSV 未作修改，仅将模型输出内插到传感器名义深度并生成配对表。若用于出版物，SITES 要求致谢 “This study/report has been made possible by data provided by the Swedish Infrastructure for Ecosystem Science (SITES).”
- 未修改模型输入、案例、求解器或产品源码；本次没有启动或打开桌面应用。

### 2026-10-26 Sol 高：视图控件重放与清单计数更正

- **代理（合成案例 UI）**：attempt65 `Imported Random Lake` 隐藏 Edge 实测 2D 尺寸、PNG 导出、平移、Ctrl+滚轮缩放/Ctrl+0复位和工具栏展开；导出 PNG 1200×1050、102,345 字节，已目视检查图面、图例、元信息与说明。视图控件项由部分完成更正为通过。
- **计数**：当前 UI 清单为 **8/10 通过、2/10 未完成**。结果文件副本清理/恢复仍未通过；ETA/完成/失败通知项仍缺原生通知能力与持久完成态验收。合成代理 UI 通过不代表湖泊科学验证。
- **保护**：视图控件重放后 Imported Random Lake 26/26 文件与保护快照一致，round 未变；Edge 与隔离服务已退出。上一只读 runner 导入副作用曾改写 `initial_conditions.json`，已单文件恢复并确认全量哈希一致。Luna 随后给 smoke harness 增加导入守卫，并静态检查通过。

### Sol 高复核：结果文件扫描 UI 未完成（2026-10-26）

- retry3 的 CDP 误选 Edge 扩展后台页，未执行应用动作；retry4 修正 target 后加载应用与案例，但没有得到扫描完成反馈。retry5 使用符合 `run_*` 规则的唯一测试副本，页面/案例加载成功，扫描按钮可用且已点击；90 秒后结果区仍显示“正在处理”，没有完成或错误反馈，故未到清理/恢复步骤。
- retry3–5 均确认临时副本不存在；retry4/5 的 Imported Random Lake 26 文件、`app/data` 3 文件和 `round.json` 哈希与基线一致，临时 Edge 与隔离服务退出。证据见各 `phase1-duplicate-ui-20261026-retry*.json`。
- **不确定**：扫描请求持续 pending 的原因尚未确定；本证据不能说明具体产品根因。副本清理/恢复验收仍**未完成**，整体 UI 清单仍 8/10。

### 2026-10-26 Sol：学术案例源码来源复核

- **实测（源码来源核验）**：通过官方公开 GitLab API 按 Ravn 运行日志中的短提交号解析 GOTM `c0add0a2`、FABM `f73ec4c`、WET `943d3c4` 的完整提交，并按提交下载/校验源码归档。文件哈希和子模块指针见 `build/academic-case-source-audit-20261026/`。该发现修正了此前“官方提交无法获取”的旧记录；但 GOTM 存储库内 FABM 子模块指针与运行日志 FABM 版本号尚未对齐，完整 build identity 仍**未完成**。
- **实测（Bryrup 输入恢复）**：官方 Zenodo WET v1.0 包含 Bryrup 的配置、气象、水文输入与输出字段定义；其八个 case 文件与当前仓库副本字节不同。没有从该压缩包恢复到校准输出或 NOVANA 观测数据，因此 Bryrup 科学验证仍**未完成**。
- **未完成（构建/运行）**：当前机器未发现 CMake、gfortran、Intel Fortran 或标准 Visual Studio CMake 工具链；本轮没有编译、启动求解器或创建模型案例。Lake Ravn 归因、Bryrup科学验证与四湖完整 GETM 3D 验证状态均未改变；Erken现有24小时配对仍按代理结果记录。
- 参考：[官方 WET v1.0 Zenodo 记录](https://zenodo.org/records/6482852)、[WET 1.0 Lake Bryrup 论文](https://gmd.copernicus.org/articles/15/3861/2022/gmd-15-3861-2022.html)、[WET开发者源码说明](https://projects.au.dk/wet/for-developers/)。

### 2026-10-26 Sol：工具链核验更正

- 上一条源码审计只检查了 PATH 与常见安装目录，遗漏 `C:\Users\23801\.codex\toolchains\msys64\ucrt64\bin`。该用户级目录实际包含 CMake 4.4.4、Ninja 1.13.2、GNU Fortran 16.2.0；此前同目录还存在 GOTM 5.4 / WET 1.0 的隔离兼容性构建和未积分 smoke 记录。
- 正在评估用已恢复的 GOTM/FABM/WET 精确提交重新建立独立构建。此发现仅改变“本机无构建工具”的判断，不改变四湖科学验证或黑片修复状态；尚未运行案例。

### Sol 高：继续执行与工作窗口约束（2026-10-26）

- **用户指示**：工作时不要重复打开桌面 APP；如果打开应用窗口，必须在本轮结束前关闭。本次没有打开或刷新桌面 APP，也没有创建浏览器窗口。CUA 当前应用/标签清单为空。
- **实测（服务同步）**：已有 52812 源码服务 HTTP 首页与 `/api/system/health` 均可读取；首页引用 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=123`、`academic_ui.css?v=8`、`studio_icons.js?v=2`。这是源码服务状态，不证明此前的桌面 WebView 已加载该版本。
- **实测（SITES 下载证据复核）**：用户已明确授权接受 SITES CC BY 4.0 并下载 Erken 2017–2024 资料。已存在的日频历史版压缩包 SHA-256 为 `498e7f45476188a4643c620f233abd63bd5fa158c7bda99d82479415a91c746e`；小时频历史版压缩包 SHA-256 为 `0edcc4ff20344acc98001c8c301b5d353ec0d5a497b4691a49275aadddb940a8`，许可接受、数据 PID、时间范围、下载/提取 SHA-256 见 `build/source-downloads-20261025/erken-2017-2024-provenance.json` 与 `build/source-downloads-20261025/erken-hourly-2017-2024/erken-2017-2024-hourly-provenance.json`。小时频旧版本被数据源标记为 deprecated；模型配对使用当前 SITES 发布版和已有案例输出，不把历史源版本重复导入或称为新增验证。
- **设计与 3D 状态**：设计决策和取舍记录于 `docs/superpowers/specs/2026-10-25-restrained-scientific-3d-design.md`；产品源码已有整站低饱和纸石色系统、重绘技术图标、三角网格面片/分层显示辅助。现有自动化与隐藏 Edge 检查仍是代理数据范围，未进行用户桌面整站最终视觉验收。设计参考图继续保留 `（待补充：参考图的具体路径或链接）`。
- **仍未完成**：黑色床面片仍**未修复**，根因仍**不确定**；attempt65 完整 UI 流程目前为 **8/10 通过、2/10 未完成**（结果文件副本清理/恢复，以及 ETA/完成/失败通知）；Erken 整体科学验证、Lake Ravn、Bryrup、Arreskov 科学验证仍**未完成**。Erken 存在限定时段实测温度配对，运行及总体验证仍含代理限制；不得升级其状态。

### Sol 高 / Luna 中：结果副本扫描阻塞的追加根因审查（2026-10-26）

- **实测（历史 UI 记录复核）**：attempt65 retry5 确认正确隔离应用与 Imported Random Lake 已加载，扫描按钮可用且点击后 UI 持续显示 pending 90 秒；但当时没有记录 Network 请求/响应状态或服务端请求耗时，因此无法确定卡在浏览器发出、WSGI 请求处理或响应返回阶段。临时重复文件已清除，案例 26 文件、app/data 与 round 哈希均回到记录的基线。
- **实测（当前代码链路）**：页面 `result_files.js` 调用 `POST /api/results/files/duplicates`；后端当前 duplicates 路由以 `shared_lock=False` 绕过共享 NetCDF 锁，但仍保留本地路由锁、忙碌门禁、revision 与文件签名校验。retry5 测试扫描时 5 个受管理文件共约 159.9 MB；实验副本与同大小来源文件各约 83.8 KB，故现有证据不支持“哈希较大重复文件造成 90 秒等待”的解释。
- **代理（局部回归）**：Sol 在当前源码独立运行 `node --test tests/js/result_files_case_switch.test.cjs`，2/2 通过；覆盖切换案例后不恢复旧 pending 消息、模板脚本版本标记。该结果不覆盖重复扫描请求完成。`python -m pytest tests/test_result_files.py -q` 因当前 Python 3.10 环境未安装 pytest 而未能运行；不据此宣称后端测试通过。
- **Sol 决策**：Luna 未找到可确认的根因，因此没有猜测式代码改动，也没有创建/启动案例或打开 APP。当前 blocker 是缺少同一次扫描的 Network 请求/响应与服务端计时证据。重复副本清理/恢复 UI 验收仍**未完成**；该 pending 现象的产品根因仍**不确定**。

### Sol 高 / Luna 中：3D 三角湖盆默认取景调整（2026-10-26）

- **实测（代码回归）**：Luna 将 `LAKE_ORTHOGRAPHIC_ZOOM` 默认值从 3 调至 4，只扩大正交场景取景中的湖盆占比；不改变网格、床面几何、变量值、色标或求解器。Sol 独立运行相机拟合、窄屏布局、相机轴、水体补丁和湖显示网格测试，**82/82** 通过。
- **实测（服务资源内容）**：本地 `viz3d.js` SHA-256 与 52812 返回脚本正文一致（`43E5E51EE7E42187C3EBB874630EF6B0C6351D2924A4C5E24D2FDAA3513801B2`），正文默认值为 4。当前运行的服务首页仍引用 `viz3d.js?v=123`，而仓库模板已改为 v124；故服务进程持有旧模板缓存，完整同步**未完成**。尝试重启该无界面服务进程被本机执行策略拒绝，未尝试替代强制终止方式。
- **边界**：没有打开桌面 APP 或浏览器，也没有运行湖泊案例。此取景改动尚无更新后的桌面目视验收；黑色床面片仍**未修复**、根因仍**不确定**。四湖验证和完整流程状态均未因此改变。

### Sol 高：Lake Ravn 既有输出与官方验证基准的只读对照（2026-10-26）

- **实测（既有 NetCDF 文件审计）**：`build/ravn-official-working-copy-run-20261021-attempt01/case/output.nc` 为既有只读结果，时间范围 1990-01-01 至 2005-12-31、5844 个记录、`z=32` 与 `zi=33`、单列 `lat=1, lon=1`。该文件来自旧的工作副本运行，不能代表当前 GUI 的 GETM 三维案例，也未在本轮重跑。
- **实测（官方报告基准摘录）**：DCE Scientific Report 402 将 Ravnsø 作为 1D GOTM-FABM-PCLake 案例，给出最大深度 32.6 m、平均深度 14.9 m、面积 1.8 km²、33 个模型层；1996–2003 验证期上层 0–5.2 m 的水温统计为 `n=208`、BIAS `−1.8%`、R² `0.99`，溶氧为 `n=203`、BIAS `+3.6%`、R² `0.82`。这是已发表模型的验收参照，不是本仓库运行结果。
- **未完成（科学验证）**：尚无与旧输出同日期、同深度筛选的 ODA 原始观测配对；旧运行的可执行文件/完整源码装配也不能与新恢复的 Ravn 精确源码构建绑定。因此不据此计算或宣称本仓库 Ravn 的 Bias/R²，不把此旧运行升级为科学验证。DCE 官方监测页列出 ODA 入口；只读打开该入口会转至 `login.aspx`。本轮未提交登录信息或请求导出，因此尚未取得原始观测。
- **下一步证据要求**：取得有来源/质量标记的 Ravnsø 1996–2005 温度与溶氧观测数据；把这些观测与明确版本的模型输出按 0–5.2 m 观测深度规则配对，剔除预热期后报告样本量、BIAS 与 R²；另行跑通用户指定的当前 GETM 三维案例。参考：[DCE Report 402](https://dce.au.dk/udgivelser/vr/nr-401-450/abstracts/nr-402-dynamiske-procesbaserede-modeller-som-forvaltningsvaerktoej-for-danske-soeer/)、[DCE ODA 数据入口](https://dce.au.dk/overvaagning/)、[ODA 直接入口](https://odaforalle.au.dk/)、[NOVANA 湖泊监测说明](https://sgavmst.dk/natur-og-jagt/naturen-i-danmark/novana-overvaagning-af-natur-og-vandmiljoe/soeer)。
- **实测（变量来源审计）**：同一旧输出的 `temp_obs` 有 187,008 个有效格点值，全部恒为 5.0 °C；其 `gotm.yaml` 温度 profile 文件路径为空，并设置上/下层初始温度均为 5.0 °C。故不能将该变量标签当作观测来源或配对数据。旧案例标题/位置也是 `QWET` / `QWET 1D case`；它是旧工作副本模拟结果，不是 Ravnsø 的实测场。

### 2026-10-26 Sol：Erken 2024-06-13 至 2024-06-20 温度配对（existing C-arm）

- **实测（有限窗口温度观测—模型配对）**：对既有 attempt03 C 臂完成重跑输出进行只读配对，168 个小时帧 × 50 个观测深度，共 8,400 对；范围 1.0–15.5 m，RMSE 4.2081 °C、MAE 4.0332 °C、总体 Bias（model−obs）+0.0243 °C。独立从六位小数 CSV 重算的样本数与指标和摘要一致。浅层 1.0 m 平均残差 −4.57 °C，深层 15.5 m 平均残差 +5.09 °C；整体 Bias 接近零掩盖了明显相反方向的剖面误差。
- **实验与方法边界**：输出为机制敏感性 attempt03 C 臂，使用 candidate solver（非 production solver），不是基线或正式外部案例验收。首个保存帧为 2024-06-13 14:00，末帧 2024-06-20 13:00；13:00 实测初始温度剖面与同一 SITES 来源逐层完全一致（最大差 0），但 t=0 没有模型保存帧，因此没有将其计入模型配对。按站点最近湿格、sigma 层中心与逐时自由面计算实际深度，线性插值到传感器深度，不外推。NetCDF 时间单位未声明时区，按 SITES UTC+1 本地钟面精确标签匹配仍是假设。
- **Sol 源码映射复核**：GETM `save_grid_ncdf.F90` 写出界面坐标 `ga(0:kmax)`；`save_3d_ncdf.F90` 通过 `cnv_3d` 写出温度 `k=0..kmax`，而 `sigma_coordinates.F90` 定义 `ga(0)=-1`、`ga(kmax)=0`，`ver_interpol.F90` 将实际温度存于层中心索引 `k=1..kmax`，`k=0` 是底边界填充值槽。配对脚本排除 `k=0` 并用相邻界面中点定位层中心，和源码索引相符。观测到的浅层负、深层正残差仍未能归因；简单层序颠倒不受当前源码证据支持，但物理原因仍不确定。
- **代理输入与限制**：原实验保留固定云量 0.5、零蒸发、无河流、单站气象广播和多数生态/营养初值代理；温度剖面对初始观测有条件依赖。不能将此配对解释为独立验证、校准、生态验证或完整 Erken 科学验证。
- 可复现脚本、配对 CSV、JSON 摘要与方法记录见 [`Erken June 2024 C-arm temperature pairing`](../../../build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/erken-june24-C-temp-observation-pairing-20261026/)。**状态：有限温度配对为实测；Erken 完整科学验证仍未完成。**

### 2026-10-26 Sol 高 / Luna 中：黑片代码证据门槛与源码服务复核

- **实测（代码审查）**：Luna 检查当前脏工作区中的 `viz3d.js` 与黑片证据矩阵，未修改产品代码。床面渲染已显式设置逐顶点 `intensity`、固定深度色标/范围和 ambient-only 照明；历史 v86 阳性代理里增加 vertex intensity 可消除近黑像素，但目标桌面真实 `_fullData` 与原始用户画面仍缺失。近期 frame06 当前源码代理载荷的温度值约 2.18°C，与归档黑片截图约 8.30–14.87°C 不匹配，且当前复现为负结果。
- **候选（均不确定）**：床面几何/投影退化与视角、垂向倍率交互；底图与动态覆盖 trace 的组合、遮挡及 trace 顺序；Plotly intensity/color scale 与 WebGL/GPU 交互；`Plotly.react`/缓存中的运行态差异；深度精度。现有证据排除不了这些项，也不支持其中任何一项作为唯一根因。
- **需要的区分证据**：原场景对应的精确案例结果与帧；同帧全量数据和床面几何；运行态 Plotly `_fullData` 全 trace 顺序及 x/y/z/i/j/k、intensity/customdata/color/colorscale/range/visible/meta；相机 center/up/projection、viewport、VE、变量/层与图层开关；浏览器、Plotly、GPU/驱动版本。拿到同一正复现场景后再逐项单变量对照。原始参考图继续为 `（待补充：参考图的具体路径或链接）`。
- **桌面源码服务（实测，只读 HTTP）**：初查时现有 52812 服务 PID 84156 首页仍引用旧 `viz3d.js?v=123`。确认 `/api/run/status` 为 idle 且进程确为 `launcher.py --web --no-open --port 52812` 后，只重启该无窗口服务。新 PID 90160 ready，首页 HTTP 200 并引用工作区版本 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=124`、`academic_ui.css?v=8`、`studio_icons.js?v=2`；`viz3d.js` HTTP 正文 SHA-256 `43e5e51ee7e42187c3ebb874630ef6b0c6351d2924a4c5e24d2fdaa3513801b2` 与磁盘一致，运行状态 idle。没有打开/刷新可见窗口；用户原生窗口是否加载当前版仍未验收。
- **状态**：黑片仍**未修复**，根因仍**不确定**；未运行或清理案例。本轮只同步无窗口源码服务，未启动桌面 APP。

### 2026-10-26 Sol：Lake Ravn 官方原始观测数据可用性推进

- **实测（官方源查询与只读下载）**：DCE 监测页将湖泊观测数据指向 ODA；ODA 当前跳转登录页。进一步发现 Danmarks Miljøportal 的 KemiData API 与公开 WFS 可只读查阅 Ravnsø 官方监测站 `21000355`（内部 station UUID `fd96faa2-2ea6-4058-b807-ce9464879641`），站名 `RAVNSØ, MIDT -- RAV1 - vandkemi`。公开 `/api/search` 对 `Datamart Feltmåling Sø`、媒介 `Sø`、该站及 1996-01-01 至 2003-12-31 返回 `canDownload=true`、8,159 条结果；首次/末次采样日期分别为 1996-01-01 和 2003-12-16。随后从 KemiData `/api/download` 下载此筛选范围的 CSV，文件 SHA-256 `764db33aab7fd6160daa755b6dbe869195aff769ce861e742b019c44c570feef`，8159 行均为该站，实际 `Dato` 日期范围 1996-01-01 至 2003-12-16；温度 2,736 行、氧含量 2,711 行、氧饱和度 2,712 行，质量标记保留为原始类别 1/2。文件：`build/observation-evidence-20261026/ravnso-feltmaaling-1996-2003/Salt, ilt, temperatur, ph måling - Sø_20261025_205122.csv`。
- **数据适用范围**：DCE 2020 Report 402 的验证期是 1996-2003，并明确对 0–5.2 m 上层水温和溶氧统计；当前下载至少提供时间/深度匹配所需的原始温度、氧浓度和质量字段。数据源页面称该 VanDa 数据集含地点、时间、测点、深度、参数及结果；此处记录使用官方 API 响应和下载件，不把门户展示的统计量当作本仓库模型结果。文件许可的具体条款需以原始数据集“Feltmåling Sø”元数据核验；未将其误写为 SITES 的 CC BY 4.0，也未把 Datavejviser 对**元数据**的 CC0 标记套用于原始测量值。
- **未完成**：这只是拿到可配对的实测资料，不等于科学验证。接下来需按同日期/深度从观测与已有模型输出生成配对，记录 00:00 每日模型帧与白天采样时间之间的时差，比较本地旧 1D QWET 输出与 DCE 发布统计；旧输出不能代表当前 GUI 的 GETM 三维案例。全湖/生态科学验证仍未完成。本轮没有创建、运行或删除模型案例，也没有操作桌面 APP。
- **来源**：[DCE 监测数据入口](https://dce.au.dk/overvaagning/)、[DMP Arealdata“Feltmåling Sø”目录](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe)、[KemiData API OpenAPI](https://kemidata.miljoeportal.dk/api/swagger/v1/swagger.json)、[DCE Report 402](https://dce.au.dk/udgivelser/vr/nr-401-450/abstracts/nr-402-dynamiske-procesbaserede-modeller-som-forvaltningsvaerktoej-for-danske-soeer/)。

### Sol 高：Ravnsø 实测资料与旧 1D 输出的有限配对核验（2026-10-26）

- **实测（产物与哈希核对）**：独立检查 `build/observation-evidence-20261027-ravnso-pairing/summary.json`、`METHOD.md`、配对 CSV 与脚本；观测源 SHA-256 与下载文件一致（`764db33aab7fd6160daa755b6dbe869195aff769ce861e742b019c44c570feef`；完整值见观测目录文件哈希；配对脚本摘要记录为 `764db33aab7fd6160daa755b6dbe869195aff769ce861e742b019c44c570feef`）。模型 NetCDF SHA-256 记为 `8edd2faf797368757b7fd12ae27d02e40f703bdcdb892c00ddc756b2295a51bf`，配对 CSV SHA-256 为 `9ee3714a02fe196ef87b1df9bb27bf48c1de3d8e82f63b6773c7b55c0b7ddeff`。
- **实测（有限描述性配对）**：按 Ravnsø 测站 21000355、观测深度 0–5.2 m、同日日期进行配对；温度 638/685、溶氧 632/677 条获得模型值，总计 1,270/1,362 条。其余 92 条位于模型最浅层中心上方（模型 z 中心最浅为 −0.5 m），未外推。观测白天时间与模型日值 00:00 不匹配，采样时刻保留在 CSV；剖面方向使用 z=−深度并在层中心间线性插值，质量标记保留。CSV 中站点显示名字段为 `Aktivitetssted`；配对依据为 Station ID 与源站点目录映射，不将这显示字段误称为站点正式名称。
- **限制 / 未完成（科学验证）**：这是旧的 QWET 1D 工作副本 output.nc 的有限配对，不是当前 GUI 的 GETM 三维结果，不足以报告独立科学验证结论，也没有完成报告 402 同期统计量的同口径复现。此前“尚无原始观测配对”的记录已由本节更新；Lake Ravn 科学验证状态仍为**未完成**。配对 CSV 中的 `source_link` 为数据源逐条记录链接；原始数据许可条件仍需按 KemiData 数据下载页和数据说明核实，未将目录元数据许可扩展至观测数据。
- 配对方法、脚本、输入指纹、逐条行状态和输出在 [`Ravnsø legacy 1D pairing`](../../../build/observation-evidence-20261027-ravnso-pairing/)；数据来源为 [DMP Feltmåling Sø 数据集目录](https://arealdata.miljoeportal.dk/datasets/urn:dmp:ds:feltmaaling-soe) 与 [KemiData API 文档](https://kemidata.miljoeportal.dk/api/swagger/v1/swagger.json)。不启动或删除任何案例。

### Sol 高：Erken SITES 2017–2024 实测温度剖面获授权下载（2026-10-26）

- **实测（数据获取与来源校验）**：收到用户明确授权后，访问 SITES “Yes, I accept”路径并接受数据使用说明，下载了 Erken year-round anchored TW-profile 的 2017-06-28 至 2024-09-14、60 分钟数据。文件哈希与 SITES 元数据页发布的 SHA-256 一致；站点 ZIP、CSV、`!TOC.csv`、`!LICENCE.pdf` 及来源/校验清单保存在 [`Erken SITES 2017–2024 source`](../../../build/observation-evidence-20261027-sites-erken-2017-2024/)。
- **来源与许可**：数据集 PID `11676.1/Kq6E7t69ZyKJejMcANJQVoHP`，引用 Erken Laboratory (2024)，SITES CC BY 4.0；需保留适当署名、许可证链接及修改说明。SITES landing page 已标注该 2024 数据集为 deprecated，并指向 2025-12-01 最新版本。本次按用户授权下载目标版本，不称其为最新发布。
- **状态边界**：这是实测来源文件的下载/校验状态，尚未形成新的模型配对或独立验证；本轮没有创建、运行、清理案例，没有改动产品代码，也没有打开桌面应用/浏览器窗口。现有 Erken 有限窗口配对状态不变，整体科学验证仍**未完成**。
- 来源：[SITES 数据集页](https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP)、[SITES 数据政策与 CC BY 4.0](https://data.fieldsites.se/licence)。

### Sol 高：Erken SITES 数据源交叉核对（2026-10-26）

- **实测（来源一致性）**：新下载的 2017–2024 SITES 温度 CSV SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e` 与既有 attempt03 C 臂有限配对的 `observations` 输入指纹完全相同，也与已有 2020/2024 配对输入副本一致。因此本次授权下载是对既有源文件的独立出处/哈希复核，没有引入新的观测数据版本或增加新的配对样本。
- **状态**：Erken 已有 2024 年 C 臂 8,400 对温度值、及既有短窗口配对仍属于有限实测配对；C 臂为候选求解器/机制敏感性实验，存在初始温度条件依赖与强迫项代理限制，不构成完整、独立科学验证。完整 Erken 验证仍**未完成**。

### Sol 高复核 / Luna 中操作：attempt65 重复结果清理与恢复 UI 流程

- **代理（真实隐藏 UI 实测）**：在隔离的 `Imported Random Lake` 合成代理案例中，UI 扫描识别 1 组重复、选中唯一临时副本、显示 1 个文件的确认提示并确认“移至回收区”；随后通过 UI 恢复，观察到“结果文件已恢复”提示，回收区计数归零，恢复副本 SHA-256 与源相同（`9eeace4455cad1286ab2d766855bdb70ab863d15f7e9fa2ce7b508c67e5331bd`）。清理点击后的 CDP 调用异常，故清理 toast 未采集；唯一 trash manifest 与后续 UI 恢复链证明清理确实生效。
- **实测（回滚保护）**：案例 26 文件基线、`round.json` 与三项 app/data 均匹配；本轮唯一副本、空 trash、Edge profile、隔离服务和 Edge 进程已清理。没有运行求解器/校准，也没有改产品代码。报告：[`phase1 duplicate cleanup and restore final`](../../../build/full-workflow-20261025-attempt65/ui/phase1-duplicate-ui-20261026-final.json)。
- **检查结论**：retry2 `.app-layout` 超时更可能来自测试 harness 的 CDP target/probe 记录问题，而非已确认产品故障；retry2 缺少足以确定当时 target 的记录，故具体原因仍不确定。后续显式 page target 的 attempt6/7 均成功加载 app；本轮 duplicate 流程实际通过。
- **完整流程状态**：attempt65 汇总现为 **9/10** 项通过、**1/10 未完成**。剩余 ETA/完成/失败与系统通知验收；模拟运行的进度和 ETA、合成失败 payload 的应用内提示均有证据，但持久完成条目/系统通知未完整捕获。流程仍用合成代理案例，不能当作四湖科学验证。

### Sol 高：Lake Ravn 流路证据补充与 3D 构建边界（2026-10-26）

- **实测（官方/专业流域文件的文献核查）**：Gudenå 段 Knud Å 1999 年河道 regulativ 将“Veng Sø 出口—Ravnsø 入口”与“Ravnsø 出口—Knudsø 入口”分别列为两段；DTU Aqua 的 Gudenaa 鱼类养护报告也描述 Knud Å 按 Veng Sø → Ravnsø → Knudsø 的顺序穿湖连通。这补充确认了主入/出流方向，不提供本工作网格上的可验证河口坐标或完整小支流流量分配。
- **不确定 / 未完成**：目前还没有从官方线要素把这两个河口配到拟建 GETM 网格的 `(i,j)`，也没有证据证实源 INLOW 的聚合流量应仅施加于单个主河口或怎样处理其它小溪。先前 readiness 中“无入/出流定位”的表述更新为：**主通道方向有资料支持，具体河口坐标、网格单元分配及小支流处理仍未解决**。这没有批准或执行深度带→连续水深转换、河流入流分配、强迫项或历史校准参数迁移；Ravn 的当前 GETM 3D case 仍未构建/运行，科学验证仍**未完成**。
- 来源：[Knud Å 河道 regulativ（Veng Sø—Ravnsø—Knudsø）](https://www.gudenaakomiteen.dk/media/16117/61251-11_v1_vandloeb-regulativ-for-knud-aa_veng-soe_ravn-soe_knud-soe-af-1999.pdf)、[DTU Aqua Plan for fiskepleje i Gudenå, del 2](https://orbit.dtu.dk/files/222261154/73_Plan_for_fiskepleje_i_Gudenaa_del2.pdf)、[SGAV 河道规章说明](https://sgavmst.dk/vandmiljoe/vandloeb)。本次仅作来源核查，不启动/删除案例。

### Sol 高：阶段验收状态校正（2026-10-27）

- **黑色床面片：未完成**。现有证据只支持现象随湖底图层、视角与垂向倍率变化；frame19 的 200×静态床面和 50×叠层对照未复现。候选根因仍为**不确定**，没有据此改代码或宣称修复。尚缺能复现原现象的同版本场景/截图、对应图层与视角/垂向倍率，以及同次复现的 Network 请求/响应和服务端计时证据。参考图继续保留 `（待补充：参考图的具体路径或链接）`。
- **用户流程：代理，9/10**。attempt65 的合成案例 UI 流程完成 9 项；ETA 列表/完成态 UI 有合成状态输入证据，通知适配器 43 项测试通过，但 headless Edge 不支持 Notification API，原生桌面通知投递仍**未完成**。因此不能报告完整流程跑通；合成案例也不能代表四湖实测。
- **Erken：有限实测配对，完整科学验证未完成**。已有 8,400 对温度值与 SITES 数据来源校验；运行含初始温度条件依赖及云量、蒸发、河流等代理，属于 candidate solver 机制敏感性，不是独立科学验证。
- **Lake Ravn：有限实测配对，当前 GETM 3D 案例及科学验证未完成**。1,270/1,362 条同日配对来自旧 QWET 1D 工作副本；浅层 92 条未外推。当前 3D 构建仍缺连续水深派生规则、河口到网格单元映射、支流处理及输入迁移。
- **Bryrup：实测观测整理已完成，运行/科学验证未完成**。观测规范化包含 1,242 行 1996–1999 温度与溶氧记录，但没有模型配对；精确历史执行器与论文配置等价性仍不确定。
- **Arreskov：未完成**。现有记录只包含可执行文件/来源审查，没有本仓库目标案例的可复现运行与观测配对，因此不能称作案例跑通或科学验证。
- **食性网络与 UI：**源码/离线及合成 UI 代理检查已完成相应改进；实际运行时摄食机制和原生桌面窗口视觉验收仍未完成。此项不改变以上四湖状态。
- **桌面同步：**已验证本地源服务资源字节与磁盘一致，当前页面引用的资源版本为 app.js v74、i18n.js v17、viz3d.js v124、ecology_network.js v31、academic_ui.css v8、studio_icons.js v2、result_files.js v3；只证明服务端正在提供当前源码，不能证明既有原生桌面窗口已加载该版本。按用户要求本轮未再次打开 APP。
- **案例清理与边界：**本轮没有启动、创建或删除任何模型案例。attempt65 留有两个隔离 Edge profile 临时目录；安全删除调用被本机命令审查以 `blocked by policy` 拒绝，未绕过。完整验收目标仍有上述未完成项。

### Sol 高：Erken 配对窗口扩展可行性复核（2026-10-27）

- **实测（现有 NetCDF 时间轴）**：只读检查既有 C 臂重跑 `arm_C_rerun_20261023/case/output.nc`，维度为 `time=168, xc=44, yc=18, sigma=10`；时间单位 `seconds since 2024-06-13 13:00:00`，保存帧从运行 1 小时至 168 小时。该输出最多支持此 7 日运行窗口的后续同口径配对，不能与 SITES 2017–2024 全期观测配成长期验证。
- **配对状态边界**：现有该输出的 8,400 对温度记录仍是 168 个时刻 × 50 个观测深度的有限观测配对；本轮没有生成新的模型输出或新增配对样本。全期 SITES 实测数据已下载及校验，但尚无覆盖该全期的对应 Erken 模型输出。故 Erken 完整科学验证仍**未完成**，不能用较长观测来源的存在推断已完成验证。
- **操作边界**：本轮只读 NetCDF 元数据，没有创建、启动、覆盖或删除案例，没有更改产品源码，也没有打开 APP。

### Sol 高集成 / Luna 中实现：黑片诊断导出准备（2026-10-27）

- **Luna 实现**：在现有显式 opt-in `?viz3d-trace-audit=1` 区域增加“导出黑色床面诊断 JSON + PNG”。JSON 使用白名单记录实际 Plotly trace 的绘制属性及几何数组、scene camera/aspect/坐标轴、视口、时间/变量/层/实际 VE/网格模式、Plotly/浏览器/WebGL renderer 和本地资源标识；不遍历 Plotly 内部 scene/module 对象。PNG 导出独立失败捕获，失败时不撤回 JSON。普通用户默认界面不增加该控件。文件：`3DWET/app/static/js/viz3d.js`，模板源码引用版本 v125。
- **Sol 验收（代理/代码证据）**：`node --test 3DWET/tests/test_viz_waterbody_patch.js` **26/26通过**；`node --test tests/viz3d_bathymetry_surface.test.cjs` **11/11通过**；`node --check` 与 `git diff --check` 通过。这验证了既有 trace audit 及水盆渲染回归，不等于在用户 GPU 复现黑片或修复缺陷。
- **服务同步（实测/部分）**：`127.0.0.1:52812` health ready、root 为仓库 `3DWET`、PID 90160、run idle。v124 与 v125 查询 URL 的 `viz3d.js` 返回字节 SHA-256 均为 `37A35FB68B773EDD938615BDBE5E35959405B292FA2A7FAF08E6791A0F974890`，与工作区最终 JS 一致；但运行服务首页仍引用 v124，工作区模板已为 v125，表明服务的模板缓存尚未更新。未重新打开或刷新桌面 APP；既有原生窗口是否已加载最终版本**未验证**。
- **黑片状态**：此改动只改善下一次自然复现时的取证，不改变生产渲染路径；黑片仍**未修复**、根因仍**不确定**。历史代理中 vertex intensity 与近黑像素消失相关，但目前目标设备/原场景缺少匹配 `_fullData`，不能据此认定根因或修复。
- **案例状态**：本轮没有启动、创建或删除任何案例；Erken、Lake Ravn、Bryrup、Arreskov 的既有状态不变，完整用户流程仍为合成 UI 代理 9/10，原生通知与四湖案例目标验收未完成。

### Sol 高：Erken SITES 最新温度剖面更新与窗口重配对（2026-10-26）

- **实测（公开观测源下载与校验）**：经用户授权接受 SITES CC BY 4.0 数据政策后，下载 Erken Laboratory 最新 `SITES_TW-PROF_ERK_LRK_20170628-20251201_L2_60min.csv` 数据包。官方元数据范围为 2017-06-28 至 2025-12-01，73,875 行；解包 CSV 为 34,486,929 字节，SHA-256 `8154189b468d3ebc8546d9f60a97aecf3c0526ad0d23c1eb1e4a64146f094821` 与 SITES 元数据完全一致。保留原 ZIP、`!LICENCE.pdf`、`!TOC.csv` 和下载响应头。数据与许可材料见 [`Erken SITES 2017–2025 package`](../../../build/real-use-validation-20261023/erken-sites-profile-2017-2025/)。
- **实测观测 + 代理模型配对（不是正式科学验证）**：对既有 attempt03 C 臂 NetCDF 只读重跑配对脚本，窗口仍为 168 帧 × 50 深度 = 8,400 对；新旧观测源产生的配对 CSV SHA-256 完全相同，RMSE 4.2081 °C、MAE 4.0332 °C、Bias +0.0243 °C。该结果说明新发布版在本次 2024-06-13 至 2024-06-20 配对窗未改变既有配对值；它仍是 candidate solver 机制敏感性臂，且包含观测温度初始化、气象/生态/水文代理，不能称独立验证或完整 Erken 科学验证。
- **来源与复现**：Erken Laboratory (2026), *Physical variables - lake temperature profile from Erken, year-round anchored TW-profile, 2017-06-28–2025-12-01*, SITES, PID [11676.1/gVQYm0aNPryFRtn2CpeuzzwF](https://hdl.handle.net/11676.1/gVQYm0aNPryFRtn2CpeuzzwF), [CC BY 4.0 数据政策](https://data.fieldsites.se/licence?ids=%5B%22gVQYm0aNPryFRtn2CpeuzzwF%22%5D&fileName=SITES_TW-PROF_ERK_LRK_20170628-20251201_L2_60min)。配对脚本和结果见 [`latest-source-pairing-20261027`](../../../build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/erken-june24-C-temp-observation-pairing-20261026/latest-source-pairing-20261027/)。
- **边界**：下载的是最新观测版本，不是新的 Erken 模型运行。本轮只生成独立的只读配对产物，没有创建、启动、覆盖或删除模型案例，没有改产品源码，也未打开桌面 APP。完整 Erken 科学验证、用户全流程及其它湖泊验收状态未改变。

### Sol 高独立验收：科研 UI / 三角网络（2026-10-27）

- **参考与设计**：依照 [`SCIENCE_UI_DESIGN_DIRECTION.md`](SCIENCE_UI_DESIGN_DIRECTION.md) 采用 ParaView、QGIS、MATLAB 官方文档中可核验的科学工作台共性：模型/数据画布为主、任务侧栏与检查器承载控制、状态和来源清楚。采用暖矿物纸色、石色与低饱和灰绿/蓝绿/赭色层级；保留模型数值色带作为主要高彩通道。没有采用纯黑白主题或消费型彩色卡片风格。参考图仍是 `（待补充：参考图的具体路径或链接）`。
- **Luna 实现**：重绘 58 个稳定图标符号的路径几何，保持 API 与符号 ID；食性网络图标改为节点—连边语义。三角网络显示层的透明度/线宽增强、按层使用低饱和递进色，作为几何展示而不编码变量数值，也未改模型场、床面数据或求解器拓扑。
- **Sol 独立代理验收**：现有图标、食性网络、3D 渲染/网格回归 `node --test ...` **108/108 通过**（包含网络过滤/编辑交互、可访问路由、三角边与层间连线、湿单元约束、床面与色标分离等）。这是代码/离线代理验证，不代表原生桌面视觉检查或生态摄食机制的科学验证。
- **桌面同步实测**：本地服务 health `ready=true`、PID 90160、model root 为仓库 `3DWET`。新静态资源请求均为 HTTP 200（academic UI、icons、viz3d）。但是首页 HTTP 200 HTML 仍引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`；源码模板已更新至 v9/v5/v127。故当前服务首页模板/桌面窗口同步**未完成**，不能声称用户桌面已加载新 UI。本轮没有再次打开 APP，也没有重启或杀进程。
- **总验收状态**：科研 UI 和 3D 表现改动已落入源代码且代理回归通过；黑色床面仍**未修复/根因不确定**，完整用户流程与 Erken、Lake Ravn、Bryrup、Arreskov 的完整科学验证仍**未完成**（各项证据状态及边界见上文）。本轮没有启动、创建、覆盖或删除任何案例。

### Luna 中实现 / Sol 高独立验收：叠层三角视图的体积表现（2026-10-27）

- **实现**：在显式选择“叠层 + 三角显示”时，为相邻原始层之间的共同有效湿单元边缘增加独立浅色低透明度三角侧面；缺失/不匹配单元不连造体积，原始层序有间隔时跳过。大网格按 12,000 个侧面四边形预算抽稀。侧面不包含变量样本、色标、hover 数值或床面几何；UI 状态文字注明侧面仅是显示辅助，不是求解器实体边界。模板脚本引用提升到 v128。文件：`3DWET/app/static/js/viz3d.js`、`3DWET/app/templates/index.html`、`3DWET/tests/test_lake_display_mesh.js`。
- **Sol 独立代理验收**：食性网络、图标、3D 网格和渲染回归合计 **109/109 通过**；新增用例覆盖字段样本及色标不变、床面 z 不变、相邻层实际高程、非连续层序跳过以及显示辅助说明。限定文件 `git diff --check` 通过。此结果是合成/离线渲染代理，尚非原生桌面视觉检查或湖泊科学验证。
- **HTTP 同步实测**：52812 health ready（PID 90160）。新脚本 URL `viz3d.js?v=128` HTTP 200 且响应包含层间侧面代码；但运行服务根首页仍引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`。因此服务端当前返回文件中包含新静态代码，但首页模板/已打开桌面是否已加载 v128 **仍未确认**。没有重启、重开或关闭 APP。
- **既有状态保持**：没有启动、创建、覆盖或删除案例；黑色床面片仍未修复、根因不确定。完整用户流程和四湖科学验证保持各自原状态，不能用本次 UI/渲染代理测试代替实测。

### Sol 高｜官方案例来源复核（2026-10-27）

- **Lake Ravn（来源实测，非模型验证）**：从 [Aarhus University WET Cases](https://projects.au.dk/wet/cases) 提供的官方链接取得 `testcase_Lake_Ravn.zip`，保存在 `build/source-research-au-cases-20261027/`。HTTP 下载成功，24 个归档条目，6,156,522 bytes，SHA-256 `4C34001BA96C777C09B936A6A6C140E3454FCBA95003BEDE06B7416C240C92A2`。包内有 `gotm.yaml`、`fabm.yaml`、完整强迫/湖盆输入、`gotm.exe`、`wet_obs.xml` 和 8 类校准观测。只读解析配置确认目标 Lake Ravn，深度 32.65m、33 层，模拟窗口 1990-01-01 至 2000-12-31。本轮仅独立重下载并核对归档，SHA-256 与 2026-10-24 已保存并运行的官方源包完全一致，因此本轮没有新增模型运行。既有 `lake-ravn-official-rerun-20261024.md` 记录官方源执行成功及 post-spinup 实测配对，但所有科学拟合指标明确为**代理**，且不是独立 holdout；`lake-ravn-calibrated-upstream-run-20261025.md` 记录官方 1D 校准配置运行成功，但出现 249,644 次未解释的 FABM 内部状态修复。故上游源案例运行/观测配对有证据，目标仓库的 3D GETM 案例和完整科学验证仍未完成。下载包本身不含可直接验证许可证；当前这份源包此前已由既有审计运行，执行器兼容性对该上游运行已证实，但不代表与当前 3D 应用兼容。AU 页面介绍该包用于校准，并描述 Ravn 长期监测背景；它不能证明本仓库当前 3D 案例已通过。
- **Bryrup**：WET 1.0 论文记载原物理驱动器为 GOTM 5.2.2-au、最大深度 9m/18 层，校准 1996–2004、验证 2004–2006，观测来自 NOVANA（月到半月频率）。本仓库已有 WET upstream `lake_bryrup_denmark` 配置及观测整理，但既有运行因执行器/配置兼容问题未完成，论文标准时间段的科学验证仍未完成。来源：[WET 1.0 论文](https://gmd.copernicus.org/articles/15/3861/2022/gmd-15-3861-2022.html)。
- **Arreskov 来源冲突（不确定）**：论文明确写道湖区模型配置包含于 WET v0.1.0 仓库/测试案例：[论文 PDF](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf)。但已有固定 Zenodo v0.1.0 归档、官方公开 Git 历史与当前树审计记录均没有 Arreskov 专属 `fabm.yaml` 或 calibration ensemble，当前正确公开项目 API 路径为 `wateritech-public/waterecosystemstool/wet`（project ID 50484945）；只列出 v0.2.0、v0.2.1、v2.2、v2.3 四个 tags，v0.1.0 tag 查询返回404。当前 master 的 `testcases/lake_arreskov_denmark` 树为13项（README、GOTM/forcing 文件和 `.gitkeep`），无 `fabm.yaml`；与既有提交树/SHA 审计一致。论文历史表述与现存公开发布工件之间的缺口仍**不确定**，尚需原始 v0.1.0 Git 快照、已归档配置或作者来源才能消解；不能仅据论文表述宣称配置已经恢复，也不能把通用 YAML 补作论文复现。既有来源审计见 `build/academic-case-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md`。
- **操作边界**：本轮只浏览论文/官方页面、下载并检查官方 Ravn 压缩包目录与文本配置；没有解压到运行案例目录、启动/覆盖/删除模型案例，或更改模型输入。案例清理指令仍适用于未来每次真正启动案例前。

### Sol 高｜观测—模型状态校正与当前学术 UI 离线回归（2026-10-26）

- **状态分类更正**：将 Erken 2020 单日 1,200 点温度对照从“实测配对”更正为**代理**（实测 SITES 观测 × 既有 WET 模型输出）；观测源仍为**实测**，模型输出为**代理**，完整 Erken 科学验证为**未完成**。原单日记录与本文件摘要已同步更正。
- **代理回归**：对当前工作树的学术主题、SVG 图标、食性网络筛选/编辑/可访问性、三角网格/体积表现、床面样式与显示路径、工作台壳层/导航等 13 个 Node 测试文件重新运行，**102/102 通过**。该结果是离线代码代理，不是原生桌面视觉验收、床面缺陷修复证明或湖泊科学验证。
- **桌面同步只读核对**：`127.0.0.1:52812/` 返回 HTTP 200，监听 PID 90160；首页仍引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`。本轮未打开或刷新 APP、未重启进程；新首页模板在桌面窗口中的加载仍**未验证**。
- **Erken 原档重下载**：执行本轮用户授权的 SITES CC BY 4.0 接受并下载后，CSV SHA-256 与官方元数据及此前归档一致。冗余副本留在 `docs/audit/user-journey-20261021/source-data/`；本机策略拒绝了删除尝试。规范归档 `build/observation-evidence-20261027-sites-erken-2017-2024/` 保留不变。该操作没有触及模型案例。
- **总体状态**：黑片仍**未修复**、根因**不确定**、参考图仍为 `（待补充：参考图的具体路径或链接）`；完整流程仍为**代理 9/10**（原生失败通知送达未完成）；Erken、Lake Ravn、Bryrup、Arreskov 科学验证均仍**未完成**。没有启动、创建、覆盖或清理任何案例。

### Sol 高｜源码版桌面 smoke 与通知桥核验（2026-10-27）

- **原生 UI 实测（隔离 smoke）**：使用 `launcher.py --ui-smoke`，通过专用空模型树 `build/source-ui-smoke-20261027/model-root/` 起动源码版 EdgeChromium/WebView2 窗口；报告 `ui-smoke-report.json` 为 `passed=true`，DOM `complete`、无 hero 卡、应用桥/布局/health ready，Chart/Plotly/Leaflet 均加载。smoke 成功后启动器自行销毁窗口并退出 0；端口 50471 已不再监听。这个隔离启动确认源码能显示在原生 WebView，但**不是旧的用户桌面会话**。
- **原生通知桥实测（挂接，不含送达）**：smoke 期间 `launcher.log` 记载 `Desktop notification permission handling attached for http://127.0.0.1:50471`。没有触发权限请求、没有点击同意、没有发送系统通知，因此系统通知送达仍未完成。该步骤没有运行求解器或案例。
- **同步边界**：全新 smoke 使用当前仓库源码模板（CSS v9、icons v5、viz3d v128）。旧服务 PID 90160 仍运行于 52812，HTTP 首页依旧引用 CSS v8、icons v2、viz3d v124；没有关闭、重启或再次打开该旧会话。故源码版 native startup 实测通过，原有桌面会话同步仍未完成。
- **通知回归（代理）**：Node 终态/ETA/opt-in/无权限回退用例 **3/3 通过**。尝试运行 `tests/test_desktop_notifications.py` 的 Python pytest 套件时，本机 Python 3.10 环境未安装 pytest，命令以 `No module named pytest` 退出；没有安装依赖或改写测试。模块已有历史 43 项测试记录，但本轮不把它记作新运行结果。

### Sol 高｜Bryrup GOTM 5.2.2-au 可获取性核查（2026-10-27）

- **文献实测（来源页面核查）**：WET 1.0 论文明确记载 Bryrup 使用 Aarhus University 的 GOTM 湖泊分支 `5.2.2-au`，给出 9.0m 最大深度、18 层，以及 1996–2004 校准、2004–2006 验证与 NOVANA 观测背景。来源：[WET 1.0 论文](https://gmd.copernicus.org/articles/15/3861/2022/)。
- **源码获取状态未完成 / 版本不确定**：论文指向的旧地址 `https://gitlab.com/WET/gotm` 匿名浏览时跳转登录页；随后查到 Aarhus WET 开发者页记录的新地址 `wateritech-public/waterecosystemstool/gotm`。该新项目当前公开可查询，GitLab API 显示默认分支 `master`，匿名分支列表只有 `master`，没有 `au` 分支，标签列表为空；`git ls-remote --heads ... au` 也没有返回 ref。因此已确认当前该公开分支表面上不能提供文档要求的 `au` 分支，但 `5.2.2-au` 是否被移入历史提交、改名分支或需登录权限仍**不确定**。不把主线 GOTM v5.2/v6 等同为指定 Aarhus fork。来源：[Aarhus WET 开发者下载说明](https://projects.au.dk/wet/for-developers/)、[论文所指 GOTM 项目](https://gitlab.com/WET/gotm)、[当前公开 GOTM 项目](https://gitlab.com/wateritech-public/waterecosystemstool/gotm)、[官方 GOTM v5.2 发布说明](https://gotm.net/blog/release_5_2/)。
- **案例与操作边界**：Bryrup 运行和科学验证仍**未完成**；未启动、创建、覆盖或清理案例，没有改代码，也没有打开桌面应用。未来启动前仍按用户要求先清理此前生成的无用案例；目前没有执行该动作。

### Sol 高｜已运行服务的源码版本复核（2026-10-27）

- **HTTP 实测**：当前仅对已运行服务 `127.0.0.1:52812` 发起只读请求：`/` 返回 HTTP 200，但模板引用仍是 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`；工作树模板/源文件分别为 CSS v9、icons v5、viz3d v128。监听 PID 90160 命令行为本仓库 `3DWET/app/launcher.py --web --no-open --port 52812`。另查 `/api/health` 返回 404，因此不将其作为健康状态证据。该旧服务仍未载入最新首页模板。
- **窗口与案例边界**：本轮没有新开、关闭或刷新桌面 APP/浏览器窗口；没有停止或重启正在运行的进程；没有启动、创建、覆盖或删除案例。用户要求避免重复打开应用，后续同步应复用现有会话，不通过重复开窗验收。是否可安全热更新/重启仍需进一步确认。

### Luna 中实现 / Sol 高复核｜学术 UI 回归断言与当前静态资源（2026-10-27）

- **Luna 代码变更（仅测试）**：学术 UI 测试不再把 CSS 缓存版本写死为 v8，而是验证 `academic_ui.css` 在 `workbench.css` 之后加载；同步更新了四项颜色断言至当前源码值。产品 UI、湖底渲染、模型数据和求解器未改。
- **实测（代理回归）**：Sol 独立运行 9 个 3D 网格/床面、显示预设、食性网络、图标和学术 UI Node 测试文件，**93/93 通过**。之前同一组测试在旧断言下因模板 v9 对比测试 v8 失败；本次更正后通过。该回归是代码代理，不是桌面视觉验收或科学验证。
- **只读服务核对**：对 52812 的 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124` 下载字节并逐一 SHA-256 与当前工作树静态文件比较，三者均完全一致。这表明旧服务虽保留旧首页模板/查询版本字符串，但其静态路由提供的是当前文件内容；Jinja 首页缓存仍未重载。此前“静态资源是否同步”的不确定性已收窄为“首页模板/浏览器页面是否刷新”未完成。
- **同步和案例边界**：本机 UI 通道只读库存返回 `apps=[]`、现有浏览器 `tabs=[]`，没有可复用的目标窗口/标签，因此没有创建或打开新的 APP/浏览器窗口；也没有重启服务。52812 首页依然返回旧版本字符串，桌面当前已显示页面仍未核验。没有启动、创建、覆盖或删除案例。黑片仍未修复，根因不确定。

### Sol 高｜同步重启被本机策略阻止（2026-10-27）

- **尝试与结果**：先确认 52812 服务身份有效、求解器状态 `idle`、没有已建立 TCP 客户端或求解器进程后，尝试停止并在同一端口启动 `--web --no-open` 服务。进程停止调用在执行前被本机策略拒绝；没有启动替代进程、没有创建窗口。随后只读复核确认 PID 90160 仍运行，`/` 仍为旧 `academic_ui.css?v=8` 模板。未使用其他路径绕过该拦截。
- **状态**：静态资源字节与当前源码一致，但首页模板和桌面显示版本仍**未同步/未验证**；需通过本机策略允许的正常应用关闭/重新启动或可访问的现有窗口刷新完成同步。该限制不影响本轮 93/93 离线代理回归结论，也不表示黑片已修复。

### Sol 高｜桌面通知权限单元测试（2026-10-27）

- **代理（无原生窗口的自动化测试）**：改用仓库 `.venv` 中的 pytest 执行 `python -m pytest tests/test_desktop_notifications.py -q`，结果 **43 passed**。覆盖通知权限仅针对本地服务 origin、明确布尔同意/拒绝、非通知权限不受影响、跨源/畸形 URL fail-closed、会话选择、线程调度/deferral 生命周期、host 失败拒绝和窗口绑定解绑等。测试文件声明不打开原生窗口；因此它验证权限桥逻辑，不验证真实 WebView2 上用户点击同意或 OS 通知送达。
- **状态**：完整用户流程仍 **9/10 代理**，原生系统通知投递仍**未完成**。本次没有打开 APP/浏览器，也没有启动/创建/覆盖/删除案例。

### Sol 高｜Arreskov 原论文补充材料追查（2026-10-26）

- **来源核查（实测）**：打开 Aarhus University Pure 的原论文记录，页面列出的可访问文件只有 CC BY 论文 PDF；论文摘要说明 12 年资料用于多单模型集合校准，且状态转变时序未被很好重现。ScienceDirect 论文页面当前返回 403，未能从该页面核对 supporting information 附件。
- **公开配置线索（来源记录，非复现）**：论文正文的软件可用性段落称，Arreskov GOTM-WET 配置作为 WET 仓库 test case 提供；但现存固定 v0.1.0 归档和公开仓库树缺少湖泊专属 `fabm.yaml` 与校准参数集合（详见 `build/academic-case-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md`）。原论文表述与目前可见工件之间的差异仍**不确定**，待原始历史快照/附件或作者材料佐证。
- **案例状态**：没有启动、创建、覆盖或删除 Arreskov 案例；没有将公开来源记录当作运行或科学验证。Arreskov 运行与完整科学验证仍**未完成**。完整用户流程以及 Erken、Lake Ravn、Bryrup 状态不变；黑色床面片仍**未修复**且根因**不确定**。

### Sol 高｜Arreskov 附录补充材料原件核验（2026-10-26）

- **原件获取（实测）**：根据原论文正文“Supplementary data”线索，Elsevier 附件端点的 PDF 变体返回 404，DOCX 变体返回 200。原件保存在独立来源目录 [`source-research-arreskov-20261026`](../../../build/source-research-arreskov-20261026/)，文件 `1-s2.0-S1364815222002043-mmc1.docx`，2,128,323 bytes，SHA-256 `bd6ba85bdef35a38b296d2237681712e8ae06a6fc062c13a24fe9e158620c4ab`。未放入任何运行案例目录。
- **内容核验（实测）**：该 Appendix A 提供 catchment 图、外源营养盐估算、月均硅输入估算方法、六类模型集合的筛选指标/样本数、观察误差估算方法及相关图表说明。实际文件没有模型配置 YAML、参数化集合成员表、完整原始逐时/逐日观测序列或模型 NetCDF 输出；不能据此复现原论文的完整模型或宣称验证完成。
- **Arreskov 状态**：仅增加了可审计的论文来源材料；没有启动、创建、覆盖或删除案例。Arreskov 原配置/校准成员仍未恢复，运行和科学验证仍**未完成**。来源：[论文记录及 DOI](https://pure.au.dk/portal/en/publications/simulating-shifting-ecological-states-in-a-restored-shallow-lake-/)、[Elsevier 补充文件](https://ars.els-cdn.com/content/image/1-s2.0-S1364815222002043-mmc1.docx)。

### Sol 高｜活动服务首页与源码版本只读复核（2026-10-26）

- **HTTP 实测**：对已存在的 `127.0.0.1:52812` 进行只读 GET；服务 health 返回 `ready=true`、model root 指向本仓库 `3DWET`、PID 90160。首页 200 仍引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`，而工作树模板已是 CSS v9、icons v5、viz3d v128；`i18n.js?v=17` 和 `app.js?v=74` 与当前模板一致。服务 PID 命令行仍为 `launcher.py --web --no-open --port 52812`。
- **隔离诊断服务**：端口 52862 仍服务 `build/bed-black-userjourney-probe-20261024/model-root`，其 `/` 引用 viz3d v108、i18n v7、app v68；此服务不是用户桌面目标案例，不将其当作桌面同步证据。
- **同步状态与边界**：首页模板/既有桌面页是否加载当前 UI 与 3D 源码仍**未同步/未验证**。没有新开、刷新、关闭或重启任何 APP/浏览器，没有停止服务；没有启动、创建、覆盖或删除模型案例。黑色床面片仍**未修复**、根因**不确定**。

### Sol 高｜当前床面审查与可用窗口核查（2026-10-26）

- **Luna 中代码审查**：复核当前床面 trace、现有 mesh regression 及 v86 单属性对照后，没有找到能由现有证据确认的当前实现缺陷。当前 trace 已显式给出顶点强度、独立深度色标与固定深度范围；旧代理里加入 intensity 同时会改变 Plotly 自动色标路径。该旧对照不证明当前目标场景已修复，也不足以确定唯一根因。故本次未改代码、未添加测试、未声称修复。
- **缺少的判别证据**：仍需在原始黑片正复现输入下获取同一帧的 `_fullData`（床面/墙/陆地/场图 trace）、相机和投影、画布像素尺寸、垂向倍率以及浏览器/GPU 信息；`（待补充：参考图的具体路径或链接）` 未提供。需要这些证据才能把几何/拓扑、trace 交互、深度着色或相机投影等候选区分开。
- **窗口库存实测**：本次仅查询已有计算机使用窗口清单，返回 `apps=[]`、浏览器 `tabs=[]`；没有可复用的目标页面用于读取运行时 trace，也没有新开窗口。故黑片实测修复与用户桌面最终 UI 同步均继续标为**未完成**。本次无案例操作、无产品代码改动，静态服务同步状态沿用上节 HTTP 记录。

### Sol 高：Arreskov 官方观测导出路径补查（2026-10-26）

- **官方来源核对（实测/来源）**：Danmarks Miljøportal 的 Kemidata 说明支持按测点、参数和调查类型检索化学观测并导出 CSV；官方 Arealdata 的“Vandkemi Sø”目录将数据标为 CC0，并列有 CSV 文件提取服务 `https://arealdata-api.miljoeportal.dk/data/vanda-ue-26/file`。Arreskov 的观测站号 `45000018` 也出现在 DCE 公开湖泊表中。
- **状态边界**：本次只验证公开检索/下载入口及站号线索，没有获取或导入原始 Arreskov 水质序列，没有建立模型配对或运行案例。因此 Arreskov 仍为**未完成**；目录和站号线索不等同于观测序列，更不等同于科学验证。
- **来源**：[Kemidata（Danmarks Miljøportal）](https://kemidata.miljoeportal.dk/?sp=1064_6508)、[Vandkemi Sø 数据目录（CC0，含 CSV 服务）](https://arealdata.miljoeportal.dk/datasets/urn%3Admp%3Ads%3Avandkemi-soe)、[DCE 湖泊表中的 Arreskov 测点 45000018](https://dce2.au.dk/pub/TR146_Lakes.pdf)。
- **操作边界**：没有接受任何新许可、下载原始数据、启动/创建/删除案例或打开 APP。服务仍处于既有状态；本轮未尝试重启或切换窗口。

### Sol 高｜Arreskov 官方监测源追查（2026-10-26）

- **官方站点元数据（实测）**：Danmarks Miljøportal 的 WFS 中，Arreskov Sø 检索到 5 个水化学监测站。`45000018`（Arreskov Sø /004）监测日期范围为 1989-01-05 至 2026-10-12，与论文使用的模型时段部分重叠。WFS 只返回站点元数据；官方 Arealdata “Vandkemi Sø” 数据集标记 CC0，但它的 CSV 文件端点匿名请求返回 HTTP 401，因此本轮没有取得或保存站点观测原始记录。
- **官方历史报告（实测来源）**：DCE 官方档案列出 Arreskov Sø 1989–2003 多份监测报告。本轮下载 1990 报告（31,749,675 bytes，SHA-256 `779055b3d1c6602b5b2697b780ed831d45b2144b4de1732af084c3dfcf99096f`），并从扫描 PDF 印刷页 43 手工转录 11 条**报告汇总值**：温度最低/最高 1.8/20.8 °C、夏季 TN 3200 µg N/L、TP 275 µg P/L、正磷酸盐 P 32 µg P/L、叶绿素 a 最高 147 µg/L、对应浮游植物生物量 34 mm³/L、Secchi 深度均值 0.25 m、pH 夏均值/最高值 9.2/9.7、冬季均值 8.1。数据见 [`arreskov-1990-reported-summary.csv`](../../../build/source-research-arreskov-20261026/arreskov-1990-reported-summary.csv)，原 PDF 与来源说明同在 [`source-research-arreskov-20261026`](../../../build/source-research-arreskov-20261026/)。这是有来源的实测摘要，不是原始时间序列，也没有与模型输出配对，因此不构成科学验证。
- **Arreskov 状态**：来源证据比前轮更充分；没有恢复论文 WET 配置/校准集合，没有启动、创建、覆盖或删除案例，Arreskov 运行及科学验证仍**未完成**。来源：[DCE 官方湖泊报告档案](https://dce.au.dk/udgivelser/tidligere-udgivelser/amtsrapporter)、[Arealdata CC0 水化学数据集](https://arealdata.miljoeportal.dk/datasets/urn%3Admp%3Ads%3Avandkemi-soe)、[DCE 监测职责说明](https://dce.au.dk/overvaagning)。

### Sol 高｜Aarhus WET 校准包身份核验（2026-10-26）

- **官方来源与文件完整性（实测）**：从 [Aarhus WET GLEON workshop 页面](https://projects.au.dk/wet/gleon-gsa-limnoseries-wet) 提供的链接下载 `calibrated_config.zip`（14,015 bytes，SHA-256 `849cc7c11b24525945b66c2923e320e82e8cc6056aba717eefd65cee677a2039`）；ZIP CRC 检查通过，含两套 GOTM/WET 配置 YAML。
- **案例归属**：`gotm-all_obs.yaml` 明确写 `Lake Ravn`、32.65 m、33 层；`gotm-temp_do.yaml` 写 `QWET 1D case`、32 m、32 层，同坐标。该包没有 Arreskov 配置、forcing、观测序列或 NetCDF 输出，不得替代 Arreskov 论文案例；对 Lake Ravn 也只是配置来源，不是本仓库目标 3D 案例的运行/科学验证。
- **操作状态**：文件只保存在来源审计目录，未解压到运行案例目录；没有启动、创建、覆盖或删除案例。

### Sol 高：Arreskov 水化学原始导出获取（2026-10-26）

- **实测（原始观测数据来源）**：通过 Danmarks Miljøportal 的 Kemidata 对 `Vandkemi - Sø` 按站点 `45000018` 导出 CSV。界面报告 613 次调查、9,982 条结果，日期范围 1989-01-05 至 2026-10-12。原 ZIP、CSV、SHA-256、字段解析方式和数据质量边界记录于 [`kemidata-export/README.md`](../../../build/source-research-arreskov-20261026/kemidata-export/README.md)。原始文件位于同一目录，未修改。
- **实测变量覆盖**：导出含 TN、TP、正磷酸盐、铵/氨氮、亚硝酸盐/硝酸盐、溶氧、氧饱和度、叶绿素 a 和 pH 等观测记录。共 293 条结果带 `<` 检出限属性；样本位置含湖内活动点与 12 条出水口记录，不能把出水口当湖内水柱数据。质量码含 1/2/3，含义待核对。原导出不含水温。
- **候选配对数据准备（代理/数据整理）**：从未修改的原始表生成 5,271 行核心参数候选子集，保留原始样本位置、深度、单位、检出限属性、质量码和来源链接；日期和小数仅标准化表示。子集仍含 256 条左删失记录、5 条出水口和 72 条站点标签样本，因此它尚不是可直接评分的正式配对表。文件 SHA-256 为 `87C8997C5CCD64D76FAEA19C3A555F97596B1CAFAEDE097894AE2C530B70FD0E`。
- **未完成项**：`Feltmåling Sø` 官方查询界面显示 602 次调查/10,020 条结果，但两次导出未生成文件；水温原始序列仍未取得。未做时空/垂向配对，也未运行 Arreskov 模型，因此案例科学验证仍**未完成**。
- **操作边界**：只在审计区保存 CC0 来源导出；未启动、创建、覆盖或删除任何案例。临时 Kemidata 浏览器标签已关闭；没有打开 3DWET Studio。

### Sol 高｜当前 UI、三维网格与食性网络离线回归复核（2026-10-26）

- **代理回归**：当前工作树运行学术 UI、SVG 图标、食性网络 UI/过滤/i18n、三角网格模式、床面渲染诊断及水盆拓扑 8 个 Node 测试文件，**25/25 通过**。
- **证据范围**：该结果确认当前代码中的回归断言通过，不是原生桌面视觉验收，不是黑片复现/修复证明，也不是四湖科学验证。
- **操作边界**：无源码改动、无案例运行、无案例目录清理；本轮用于查温度数据的 Kemidata 临时标签已关闭，未打开 3DWET Studio。既有桌面首页模板同步仍未验证。

### Sol 高｜Arreskov 本地案例配置与既有失败运行复核（2026-10-26）

- **官方案例源（实测/文件）**：当前仓库有 `3DWET/src/wet/testcases/lake_arreskov_denmark/README.md`、`gotm.yaml` 和配套 forcing/hypsograph；README 说明原案例期为 1990–2014，并建议因流域/湖泊监测不确定性将模拟期限制在 1990–2006。由此修正“没有 Arreskov 案例文件”的宽泛说法：物理/水文测试用例文件存在。
- **配置缺口（实测）**：该案例目录没有 `fabm.yaml`。既有 `build/real-use-validation-20261023/arreskov-luna-attempt01/` 中两次执行日志都在 GOTM 初始化后终止，错误为 `fabm_create_model_from_yaml_file: Unable to open fabm.yaml for reading.`，两个退出码均为 1；没有生成 NetCDF 输出。这不是一次有效模型运行。
- **不能直接替换缺失配置**：`3DWET/src/wet/testcases/fabm-wet.yaml` 和 QWET 模板是通用/模板配置。尚无证据表明它们等同于论文的 Arreskov 率定配置与 ensemble parameter set；未经核实复制到案例不能称为论文复现或科学验证。
- **状态**：Arreskov 来源目录可用于恢复物理/水文输入，但缺少明确匹配的 FABM 配置，科学验证仍**未完成**。本轮只读检查，未清理旧 attempt、未创建/运行案例、未打开 APP。

### Sol 高｜Erken 温度剖面许可授权与原档复用（2026-10-26）

- **用户授权**：用户明确授权接受 SITES CC BY 4.0 数据使用说明并下载公开 Erken 2017–2024 温度剖面。
- **原档核验（实测/来源）**：授权目标与现有来源目录 `build/observation-evidence-20261027-sites-erken-2017-2024/` 中已保存的原始 ZIP、CSV、`!LICENCE.pdf`、`!TOC.csv` 和下载清单完全对应。门户元数据确认文件大小 29,452,645 bytes、62,959 数据行、SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`；本地清单中的下载文件哈希与门户一致，因此复用现存原档，没有再生成重复下载。
- **时间与范围限制**：这份 2017–2024 数据集标记为 deprecated，门户指向 2025-12-01 的更新版；旧版覆盖 2017-06-28 至 2024-09-14（UTC+1），不得描述成涵盖完整 2024 年或当前最新版本。来源：[SITES Erken 温度剖面数据集](https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP)。
- **验证状态**：原始测量档已取得并核对；数据取得不等于模型配对或科学验证。Erken 的模型对照、完整用户流程以及四湖科学验证总状态仍按既有记录，不因该次授权而提升。未运行模型案例、未清理或创建案例、未打开 APP。

### Sol 高｜现有桌面服务版本只读核对与黑片代码复审

- **本机窗口状态（实测）**：计算机使用接口返回原生应用 `apps=[]`、浏览器 `tabs=[]`。本次没有打开、关闭、刷新或切换任何 APP/浏览器窗口。
- **服务模板状态（HTTP 实测）**：目标服务 `127.0.0.1:52812` 仍可返回 HTTP 200，但首页 HTML 使用旧引用 `academic_ui.css?v=8`、`studio_icons.js?v=2`、`viz3d.js?v=124`；`app.js?v=74` 与 `i18n.js?v=17` 引用与当前模板相同。连接 `127.0.0.1:64257` 被拒绝；`52862` 返回旧诊断资源 v108，不是用户桌面目标。对 52812 的旧查询参数逐一 GET 后，CSS、图标、viz3d、app、i18n 这五个资源的远程字节哈希都与本地工作树当前文件一致。此结果证明服务静态资源路由返回当前文件，但首页模板引用仍旧；不证明用户屏幕的窗口已刷新。
- **同步状态**：用户要求不要重复打开 APP，本次遵守该边界。源码 `server.py` 的首页通过 Flask `render_template("index.html")` 返回；服务没有启用 `TEMPLATES_AUTO_RELOAD`，也没有模板清缓存/热重载路由，因此当前进程没有可用的受支持首页热重载入口。旧服务首页模板/桌面窗口同步仍**未完成核验**；没有尝试停止或重启进程。
- **黑片复审（Luna 中代码审查；代理证据）**：历史 v86 正复现代理载荷中，单独增加床面 vertex `intensity` 会使近黑像素由 245,173 降为 0；但 Plotly 同时进入自动色彩映射，因此不能把改善唯一归因于 intensity 数组。当前 `viz3d.js` 已显式使用床面顶点强度、独立深度色标和 `cmin/cmax`；当前历史重放未见黑片，但它仍是代理结果。没有发现可由现有证据确认的当前生产代码缺陷，故本轮未改床面源码。
- **缺陷结论**：目标用户场景中的黑色床面片仍**未修复**，唯一根因仍**不确定**。还缺正复现现场的精确帧输入、运行时 `_fullData` 与 trace 顺序、相机/视口、垂向倍率及浏览器/Plotly/GPU 信息；参考图路径继续保留 `（待补充：参考图的具体路径或链接）`。代理画面无黑片不能替代目标桌面验收。
- **案例与流程边界**：本次没有启动、创建、覆盖、删除或清理案例，也没有运行模型。完整用户流程与 Erken、Lake Ravn、Bryrup、Arreskov 科学验证仍按各自记录标为**未完成**，不提升代理状态。

### Sol 高｜Erken 2017–2024 已授权原档结构与时间戳质量核对

- **实测（原档读取/哈希复核）**：用户明确授权接受 SITES CC BY 4.0 数据说明并下载后，本轮实际再次取得目标 CSV；SHA-256 与既有归档及官方公布值相同。重复下载副本位于 `docs/audit/user-journey-20261021/source-data/`，删除尝试被本机策略拒绝，故仍保留；既有规范归档继续位于 `build/observation-evidence-20261027-sites-erken-2017-2024/`。文件标注 UTC+1、小时水温剖面，50 个深度列覆盖 1.0–15.5 m，字段单位为 °C。原档有 62,959 行、62,897 个唯一时间戳，全部温度单元格非空；排序后的首末记录为 2017-06-28 19:00 至 2024-09-14 08:00（文件标示时区 UTC+1）。
- **数据质量限制（实测）**：原始行序并非严格递增，发现 1 次时间回退、2 次相邻重复，且总计 62 个重复时间戳键（各出现两次）。需先按时间排序并制定重复记录处理规则，再做模型—观测配对；不得把行序直接解释为规则小时序列。该检查没有对值做筛选、插值或合并。
- **状态边界**：原档取得与字段/时间戳审计属于实测数据核查；尚未完成对目标模拟输出的时空/垂向配对、误差统计或 Erken 科学验证，仍为**未完成**。本次无代码改动、无模型运行、无案例新建/清理、未打开 APP。

### Sol 高｜Erken 2024 六月既有候选配对窗复核

- **实测（配对键复核）**：复核既有 2024-06-13 13:00 至 2024-06-20 13:00 SITES 窗口：169 个观测时间标签（含初值时刻），该窗口内无重复且逐小时无缺；模型的 168 个保存帧也逐小时连续。全原档的 62 个重复时间戳键与一次行序回退均不在此窗口。配对脚本按时间索引直接查询该窗口时间标签，因此此次已报告 8,400 个配对点不受全档其他时间段重复键影响。
- **解释限制**：该配对仅为 attempt03 C 候选求解器的温度描述性对照，不是生产求解器结果；模型时钟与 SITES UTC+1 标签的对应未经独立 UTC 校正，初值复用了观测剖面，且有代理云量/蒸发、禁用河流和代理生态/营养盐初值。报告的 RMSE/MAE/bias 不足以升级为完整 Erken 科学验证；Erken 案例总体仍为**未完成**。
- **操作边界**：只读复核现有 CSV、配对脚本和结果 JSON；没有重跑配对脚本、覆盖产物、启动模型或清理案例；未打开 APP。

### Sol 高｜Lake Ravn 官方湖深等值面源核查

- **官方来源（实测/只读查询）**：检查 Styrelsen for Grøn Arealomlægning og Vandmiljø 的 NOVANA “Soe_dybdekort_konturer” WFS 图层及其字段（湖名、湖 ID、深度区间、面积、几何）。官方图层说明该数据来自国家 NOVANA 监测的选定湖泊深度测绘，供监测与技术分析使用；不是所有湖泊都覆盖。来源：[图层元数据与 WFS 入口](https://semanticgis.org/Data/Datasets-by-Owner/styrelsen-for-groen-arealomlaegning-og-vandmiljoe/hypsografiske-kurver-dybdekort-over-danske-soeer-novana)、[官方 WFS](https://geodata.fvm.dk/geoserver/NOVANA/ows)。
- **查询结果（实测）**：按 `soe_navn ILIKE '%Ravn%'` 和 `'%ravns%'` 查询官方湖深等值面图层，均返回 0 条匹配。该特定数据源当前不能提供 Lake Ravn 的空间等深面，不能据此生成或插值该湖的 GETM 3D 水深网格。
- **状态与边界**：这只排除了一个官方湖深图层作为可直接复用来源；不证明其他地形测绘资料不存在。Lake Ravn 的空间水深、河口网格映射、3D 强迫及历史参数迁移仍**未完成**，旧 QWET 1D 实测配对仍仅为有限描述性比较，不升级成当前 3D 科学验证。本轮未创建/清理/运行案例、未修改产品代码、未打开 APP。

### Sol 高｜Fortran/CMake 工具链 PATH 外复核（2026-10-27）

- **实测（本机工具链）**：先前按 PATH 查询曾报告未发现 CMake/gfortran；本次进一步检查 `C:\Users\23801\.codex\toolchains\msys64\ucrt64\bin`，确认可执行 GNU Fortran 16.2.0、CMake 4.4.4、Ninja 1.13.2。当前环境虽未将它们加入 PATH，不能再笼统称为“机器没有工具链”。
- **既有构建证据（实测/工件）**：已有 Ravn exact-stack `gotm.exe`，SHA-256 `3C90276468665607B8AACD66796DC70C63212CC09E08700EA48494180A48C67F`，CMakeCache 记录 Fortran 编译器即上述 gfortran。该可执行文件属于 GOTM 1D；不等于当前 GETM 3D 案例已构建或科学验证。
- **操作边界**：只核对工具版本、构建缓存和可执行文件哈希；未编译、未运行模型、未创建/清理案例、未打开 APP。黑片仍未修复、唯一根因仍不确定；案例和完整流程状态不提升。
### Sol 高｜2026-10-27 源码服务同步核对（不打开桌面窗口）

- **实测（HTTP 服务）**：只读检查 localhost 服务，52812 由工作区 `launcher.py --web --no-open` 提供，首页 HTTP 200，引用 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=124` 和 `academic_ui.css?v=9`；逐文件下载字节与工作区对应静态资源 SHA-256 一致。
- **桌面窗口状态**：64257 当前没有监听进程；本次未尝试启动或重复打开 3DWET Studio。故能确认的是源码服务已同步，不能确认用户持有的旧桌面窗口已经刷新或已关闭。
- **验收边界**：此次只是同步核对，没有产品代码改动，没有运行/创建/清理科学案例。完整用户流程与四湖科学验证维持原状态；黑片仍未修复，根因仍不确定。

### Sol 高｜Bryrup 1990 smoke 与早期实测覆盖检查

- **代理（归档配置/日志核对）**：现有 `bryrup-wet1-stim-one-day` 成功 smoke 只运行 1990-01-01 12:00 至 1990-01-02 12:00。已归档的站点 `Feltmåling Sø` CSV 覆盖 1996–2006，与该输出没有时间重叠。
- **实测（官方监测范围）**：SGAV 官方指南说明 Bryrup 于 1989 年开始纳入监测，且 1989–2015 年每年采集营养盐/氧数据。故本地 CSV 没有 1990 记录不能推出当年没有实测。
- **实测（数据集级元数据）**：官方 Feltmåling Sø 目录给出的整体覆盖期始于 1939-07-31，许可为 CC0；该范围不等同于 Bryrup 站点覆盖，更不等同于 1990 温度剖面已可配对。
- **实测（站点级元数据）**：官方 WFS 对站点 21000361 返回首个调查 1978-04-12、最近调查 2025-12-09，故站点档案整体覆盖 1990；这仍不能证明 1990-01-01/02 有温度剖面。需要取得按站点和日期过滤的逐条记录才能确认。
- **实测（官方 API 导出）**：按站点 21000361、湖泊介质、Feltmåling Sø、1990-01-01 至 1990-12-31 筛选后，现已归档 182,208 字节 CC0 CSV，SHA-256 `F18CE9C915B20470DAE7EF92CC5E9652D9A69D81E7585AA0A50310B061C8F062`。含 561 条测量、187 条温度值，分布于 19 个剖面日期；每次 9–13 深度，0.2–8 m。首末温度剖面日期为 1990-01-23 和 1990-12-04。
- **未完成**：1990 观测档已取得，但当前 smoke 只跑 1 月 1–2 日，没有同日剖面，尚未配对；需使用有覆盖的模型运行时段再做变量、日期、时区、深度与单位核对。观测为**实测**，既有 smoke 为**代理**，Bryrup 科学验证仍**未完成**。来源与限制见 `bryrup-official-observation-source-note-20261025.md`。

### Luna 中实现 / Sol 高复核｜三角网格 3D 表现力

- **代码实现**：三角显示模式采用更明确的方向光照（ambient 0.48 / diffuse 0.52，低强度 specular 0.08）、2.3 px 三角层边界，以及 opacity 0.22 的显示辅助层间侧面。设计仍保持低饱和几何色；变量色标范围和数据值未改，床面/求解器拓扑未改，界面保留“三角化不是求解器原生网格”的说明。
- **代理验证**：`node --test tests/viz3d_bathymetry_surface.test.cjs`，13/13 通过；测试断言了字段色标不变、层间面及三角边可见。尚无当前原生桌面画面的视觉验收，故只证明渲染配置与回归，不证明桌面观感或科学验证。
- **桌面同步**：运行服务 `127.0.0.1:52812` 健康且静态 JS 与工作树 SHA-256 一致（`E733B056B2B3F024E6EE420EE18270306945FC8FB44CDAD2EA0D28609D065BE0`）；但首页仍使用 `viz3d.js?v=124`，当前模板为 `v128`。未找到受支持的模板热重载方式；本次未打开、刷新、重启或终止应用。因此桌面模板加载最终资源状态**未完成核验**。
- **缺陷边界**：黑色床面片仍**未修复**，根因仍**不确定**；该三角显示改动不构成修复或根因证据。

### Sol 高｜Bryrup 1990–1995 输入覆盖评估（只读）

- **代理（配置/输入文件范围核对）**：归档 WET upstream Bryrup 配置设定 1990-01-01 至 1995-12-31；随附气象强迫覆盖 1979-01-01 至 1999-12-31，入流和化学强迫从 1990 年开始。因此归档输入的时间范围覆盖 1990 温度剖面观测日期；本项只是文件范围检查，不证明强迫为独立实测，也不证明科学有效。
- **未完成/不构成运行**：本次只读查看配置和输入首末时间，没有启动求解器或案例；也没有确认这份旧 WET 配置能否原样用于当前 3DWET 可执行程序，更没有产出可配对的模型输出。它只表明存在可供下一步审查的潜在强迫资料，不代表 Bryrup 复现或验证成功。

### Luna 中实现 / Sol 高复核｜Flask 模板自动重载

- **代码实现**：`3DWET/app/server.py` 设置 `TEMPLATES_AUTO_RELOAD=True`；新增首页模板变更回归测试，模拟同一客户端先后读取模板 v1/v2。
- **代理验证**：`.venv\\Scripts\\python.exe -m pytest 3DWET/tests/test_template_auto_reload.py -q`，1/1 通过。该测试验证 Flask 配置和模板加载器行为，不是桌面应用视觉验收。
- **桌面服务实测**：只读 HTTP 检查 `127.0.0.1:52812/` 得到 HTTP 200，但首页仍引用 `viz3d.js?v=124`；`/api/health` 返回 404。说明在线进程/模板与当前工作区版本尚未完成同步核验。本次未重复打开窗口、未刷新页面、未重启或终止进程。
- **未完成**：新 Python 配置须由受支持的应用生命周期重载后才可能影响现有进程。桌面同步和最终版本核验仍未完成；不据此声称应用已更新。

### Sol 高｜科研软件设计资料复核与当前资源版本对照

- **来源复核（官方文档）**：ParaView 官方指南记录 Render View、Pipeline Browser 与表示属性；QGIS 官方 GUI 指南记录地图主画布、2D/3D map view、可切换面板；COMSOL 6.3 文档将 Model Builder、Settings 与 Graphics 分为模型工作区，并说明 Graphics 工具含视角、照明、透明和线框；MathWorks 官方文档说明 MATLAB 使用稳定的 Files/Workspace/Command 等停靠面板。引用及采用理由见 `SCIENCE_UI_DESIGN_DIRECTION.md`。这里比较的是科研工作流与界面结构，不对产品作“世界最佳”排名。
- **当前实现核对**：本地 `index.html` 引用 `app.js?v=75`、`i18n.js?v=17`、`viz3d.js?v=128`、`academic_ui.css?v=9`、`studio_icons.js?v=5`；服务首页仍回送旧模板标签 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=124`、`academic_ui.css?v=8`。但对上述五个静态文件做 HTTP 原始字节 SHA-256 对比，服务响应均与当前工作树一致。这证明静态文件服务内容同步，不证明现有浏览器缓存或桌面窗口已载入最终模板/资产。
- **界面代码核对**：学术工作台色板为纸白、石色、浅鼠尾草与灰湖蓝，并包含克制赭色；图标走统一 SVG 科学线稿目录，包含网格、剖面、图层和仪器等语义，不是黑白主题。代码与设计方向一致；当前窗口的最终视觉验收仍**未完成**。
- **操作边界**：只读检查网页源码/HTTP 资源与文档；未打开新窗口、未启动/清理案例、未刷新或重启应用。

### Luna 中实现 / Sol 高复核｜三角网络回归断言对齐（2026-10-27）

- **发现**：三角显示测试仍断言旧线宽、旧面片光照和旧层间侧面透明度，与工作树当前已确认的低饱和 3D 显示实现不一致。原始定向测试 69/72 通过，3 项失败均指向以上旧期望值。
- **Luna 修改**：仅把 `3DWET/tests/test_lake_display_mesh.js` 中这些显示参数断言更新为当前实现值（2.3 px；ambient .48 / diffuse .52 / specular .08 / roughness .82；opacity .22），没有改模型字段、色标、床面或求解器拓扑。
- **Sol 独立代理验收**：复跑 6 个相关 Node 测试文件，共 **72/72 通过**，覆盖三角面/边、层间显示辅助、床面/色标分离、食性网络筛选/编辑与国际化。测试文件在当前工作树为未跟踪文件；这是代理回归，不是桌面视觉、黑片修复或生态运行时科学验证。
- **同步/操作边界**：生产静态文件未在本次修改；只读 HTTP 哈希仍与工作树一致，但首页标签仍为旧版，原生桌面同步未完成。本轮未打开/刷新/重启 APP，未运行、创建或删除案例。

### Sol 高｜在线模板结构与健康端点补充核验（2026-10-26）

- **模板对照（实测）**：对本地 `index.html` 与 HTTP 首页做行差异比较，确认差异不止 query 版本号：服务页面还保留旧 `viz3d.js`/`app.js`/`ecology_network.js`/图标/工作区样式版本、网格透明度默认值以及旧版 SVG sprite 段落。故当前工作区模板尚未被在线服务重新读取。此前将 `/api/health` 当作健康端点不准确；启动器定义的端点是 `/api/system/health`。
- **健康状态（实测）**：`/api/system/health` HTTP 200，application=`3dwet-studio`、ready=true、model_root 指向本工作区的 `3DWET`、PID 90160；`/api/system/diagnostics` HTTP 200。健康只证明服务存活及诊断路由可用，不表示模板/桌面窗口同步，也不表示案例运行验证。
- **安全边界**：Launcher 将正常关闭与活动求解器保护放在拥有服务的本地进程生命周期里；源码没有远程关闭/重载路由。本轮没有用强制终止替代正常关闭，没有重复打开或刷新应用，没有运行/创建/删除案例。
- **结论**：应用模板加载与原生窗口最终视觉验收仍**未完成**。要同步 Python/Jinja 已更新部分，需要通过应用自身受支持的正常关闭并重启；当前此服务未提供由外部进程触发的安全关闭入口。

### Sol 高｜Bryrup/Ravn/Arreskov NOVANA 深度服务候选源核查（2026-10-26）

- **实测（官方 WFS 响应核查）**：官方 `https://geodata.fvm.dk/geoserver/NOVANA/ows` capabilities 列出 `NOVANA:Soe_dybdekort_punkter`；字段为观测深度 `depth`、湖名 `soe_navn`、点 ID 与几何。服务无筛选时报告全库 114,694 个点；以 `soe_navn LIKE '%Store%'` 得到 4,114 条，验证名称字段及过滤确实生效。该数据集目录说明测点为声呐现场测深、用于深度图插值；目录与 WFS 字段说明见 [NOVANA depth soundings metadata](https://semanticgis.org/Data/Datasets-by-Owner/styrelsen-for-groen-arealomlaegning-og-vandmiljoe/opmaalingspunkter-dybdekort-over-danske-soeer-novana)。
- **筛选结果（实测/服务查询）**：按 `Arreskov`、`Bryrup`、`Ravn`、`Lake Ravn` 过滤测点图层均返回 0；同一官方服务的 `NOVANA:Soe_dybdekort_konturer` 等深线图层按 `Arreskov`、`Bryrup`、`Ravn` 过滤也均返回 0。筛选为零只排除这两个 NOVANA 深度图层作为这些湖泊可直接下载的来源，不证明其他测绘来源不存在。Lake Ravn 的“Ravn”筛选与已有复核一致。
- **科学验证影响（未完成）**：目前不能从上述两个图层获得这些案例所需的空间水深点/等深线；没有生成插值网格，也没有把其它湖泊的深度数据代替实测。需继续找带可追溯测深、坐标系、垂直基准及许可的湖泊专属来源，再核对与案例边界/模拟输入的匹配。
- **操作边界**：仅查询官方 WFS 元数据与零结果，不保存或覆盖模型案例数据；未运行、创建、清理案例，也未打开 3DWET Studio。

### Sol 高｜隔离模型根目录 WebView UI smoke（2026-10-26）

- **实测（隔离 UI smoke）**：按启动器受支持的 `--ui-smoke` 路径启动一次 EdgeChromium WebView，使用仅含空 `bin/` 与 `case/` 的隔离模型根目录。报告 `build/ui-smoke-source-20261026-01/report.json` 显示 `passed=true`、document complete、bridge ready、layout visible、health ready、language ready，Chart/Plotly/Leaflet 均已加载；窗口由 smoke 正常关闭。临时服务端口 65475 随进程退出，无监听。
- **边界**：该 smoke 验证当前源代码在隔离根目录的 UI 启动，不使用真实案例/求解器（报告明确缺少隔离目录内 solver/runtime），不代表现有 52812 页面模板已更新、不代表用户原生窗口已视觉验收，也不构成完整用户流程或科学案例验证。
- **清理边界**：曾尝试清除本次 smoke 建立的空隔离目录（非湖泊案例）；本机策略拒绝递归删除调用，故保留隔离目录和报告，没有用其他命令绕过。未触碰真实 `3DWET/case` 或已归档证据。

### Sol 高｜SITES 许可确认与桌面服务版本只读核验（2026-10-26）

- **实测（许可步骤）**：用户明确授权接受并下载 SITES Erken 2017–2024 温度剖面。已在目标数据集下载流程打开并确认 “Yes, I accept”。官方页面说明该数据按 CC BY 4.0 提供，要求保留归属、许可链接与原数据集链接。精确数据记录是 2017-06-28 至 2024-09-14 的 60 分钟 CSV；本地原始归档哈希与元数据一致。此动作不代表观测—模型配对或科学验证通过；既有科学状态保持“实测观测源 / 代理单日对照 / 完整验证未完成”。
- **实测（只读桌面服务状态）**：没有再打开或刷新 Studio 窗口；只读请求 `127.0.0.1:52812/` 返回 HTTP 200，`/api/system/health` 返回 ready=true，PID 90160、model_root 为当前仓库 `3DWET`。服务首页仍引用 `app.js?v=74`、`viz3d.js?v=124`、`academic_ui.css?v=8`，而工作区模板分别为 `v75`、`v128`、`v9`。因此已重开的桌面实例/服务仍未载入当前模板版本，最终同步验收**未完成**。本轮未尝试重启或关闭该 PID，也未运行、创建或删除案例。

### Sol 高｜完整流程既有验收轮次版本一致性复核（2026-10-26）

- **代理（既有验收证据）**：`build/full-workflow-20261025-attempt65/round.json` 记录 external、features、results、scipy、abc、restart 六个后端阶段均通过，状态为 `awaiting_ui`；同目录 `ui/ui-report.json` 有 10 项检查，其中 9 项记录通过、`eta_completion_failure_notifications` 失败。该轮实际使用合成 `Imported Random Lake`，不构成 Erken、Ravn、Bryrup 或 Arreskov 科学验证。
- **未完成/证据不可升级**：只读调用验收脚本的版本哈希逻辑，attempt65 版本为 `93cef132…`，当前工作区为 `2527877a…`，两者不同。由于每项 UI 证据要求与完全相同源码版本和 seed 对应，attempt65 不能作为当前源码的完整用户流程通过证据。UI 报告说明通知项只验证了页面内状态与合成轮询事件；宿主通知 API 在该隐藏 Edge 环境不支持，真实桌面通知投递仍未验证。没有修改 round、ledger 或旧产物，也没有启动新案例/打开 Studio。
- **下一步边界**：要重建当前版本的完整流程验收，须使用全新 seed 和独立工作目录；桌面通知检查需在受支持的原生 WebView2 宿主中实测，并且完成后端要求的 10 项完整证据。现存旧轮次保留作历史记录，不冒充当前版验收。

### Luna 中审查 / Sol 高独立验收｜三角网络 3D 表现力（2026-10-26）

- **当前实现（代码核查）**：三角显示已有分层边线、层间连接线、低饱和方向光照，以及叠层时的显示辅助侧面；网格节点默认隐藏。测试与实现都标明这些只表达视图结构，不改变 GETM/FABM 数值、变量色标、湿网格面拓扑或床面几何。
- **代理验证**：Luna 从仓库根目录和 Sol 独立复跑 `node --test 3DWET/tests/test_lake_display_mesh.js`，均为 52/52 通过。该结果覆盖网格/层间关系及科学数据不变性，不证明当前桌面视觉已加载该版本或用户认为表现力足够。
- **决策与边界**：没有当前桌面截图/交互观察能证明现有 3D 表现有明确缺口；本轮不添加主观几何、颜色或材质效果。没有改代码，因此无需应用同步。当前桌面加载状态仍按前述版本核验结果为**未完成**。

### Sol 高｜活动服务进程来源与受支持重载路径核查（2026-10-26）

- **实测（进程只读核查）**：端口 52812 的 PID 90160 确为从当前仓库启动：`C:\Users\23801\Desktop\GETM-FABM-WET-260928\3DWET\app\launcher.py --web --no-open --port 52812`；model_root 也指向本仓库。由此排除了“该服务来自另一个安装路径”的解释，但没有证明浏览器已经载入工作区模板。
- **受支持同步判断**：当前源码仅暴露 health/diagnostics 只读端点，没有 reload/shutdown 路由；外部没有安全重载入口。工作区 `server.py` 的模板自动刷新配置只能在新进程载入，不能改变 PID 90160 已有的 Python 配置。按用户要求不再重复开窗，本轮不关闭/终止该进程，也不另开应用。
- **结果**：服务仍回送旧模板标签，桌面同步未完成。要继续完成同步，需要经应用拥有的正常关闭/重启生命周期重载同一仓库服务；本轮没有进行绕过方式。

### Sol 高｜Erken 2024 既有温度配对 ±1 小时时标敏感性（2026-10-26）

- **代理（已有模型输出 × 实测观测）**：只读使用已存在的 168 帧 × 50 个观测深度配对表与 SITES 原始剖面，在观测标签相对模型标签 −1 h / 0 h / +1 h 下重新配对。三种情形均为 8,400 对且窗口内时间键唯一；偏差分别 +0.03715 / +0.02427 / +0.01248 °C，MAE 4.02757 / 4.03318 / 4.03910 °C，RMSE 4.20348 / 4.20809 / 4.21281 °C。零时差复现已有 summary（舍入精度）。
- **Sol 判断**：这段候选求解器窗口的 RMSE 对 ±1 h 偏移不敏感（跨度约 0.0093 °C），有符号偏差有小幅变化。较低 RMSE 不能反推哪种时标正确；SITES 标注 UTC+1，而模型 CF units 无时区，正确映射仍**不确定**。
- **状态限制**：配对基于 attempt03 C 臂候选求解器机制敏感性实验，初始剖面也参与模型初始化，强迫/初值代理限制仍在；此项不等于独立或完整 Erken 科学验证，Erken 总体验证仍**未完成**。未运行、创建或清理案例，未打开/刷新 APP。方法与结果见 [`Erken ±1 h sensitivity`](erken-june24-timezone-lag-sensitivity-20261026.md)。
### Sol 高｜Erken 模型输出覆盖盘点（2026-10-26）

- **代理资料盘点（只读）**：扫描 `build/` 下路径含 Erken 且名为 `*.3d.nc` 的文件 127 个；91 个含时间帧，34 个时间轴为空，2 个不可读。最长非空模型输出为 168 个小时帧（2024-06-13 14:00 至 2024-06-20 13:00）。此前广泛 NetCDF 清单中的更长 369 帧文件是 `meteo.nc` / `rivers.nc` 强迫输入，并非模型输出。
- **代理**：现有七日候选求解器输出与观测配对分析。**未完成**：Erken 季节/长期科学验证，以及 Erken、Lake Ravn、Bryrup、Arreskov 完整流程。盘点仅覆盖当前 `build/` 和上述命名规则，不能证明该范围之外没有其他输出；详见 [`Erken 模型输出覆盖盘点`](erken-model-output-coverage-inventory-20261026.md)。
- 本次未创建、运行、删除、清理或覆盖案例；未打开或刷新桌面应用。

### Sol 高｜Erken seasonal attempt02 配置就绪审计（2026-10-26）

- **实测（只读文件审计）**：SITES 2017-06-29 至 2017-09-30 每日温度剖面有 94 日 × 50 深度共 4,700 个值；另有 2,256 小时混合强迫候选，之前的来源审计报告连续完整时段为 2,238 小时。强迫包括 Svanberga 邻站观测和 ERA5 再分析填补，故属于混合/代理强迫。
- **关键错配**：标记为 `Erken_2017_seasonal` 的 attempt02 运行目录中，`getm.inp` 仍设置 2020-01-01 至 2020-01-02，温度文件仍为 2020 单日初值；`meteo.nc` 时间轴也仅有 2020-01-01 至 2020-01-02 共 25 帧。目录没有 `*.3d.nc` 或 `output.nc` 模型结果，输出子目录仅有 README。因此不得把此目录描述为 2017 季节模拟或季节验证。
- **代理**：2017 混合强迫 CSV 只是候选输入。**未完成**：正确配置的 2017 季节案例尚未运行，且代理/混合强迫仍需与纯观测强迫区分。没有改动或清理 attempt02 源材料，没有创建/启动新案例；因该目录没有已生成模型结果可清理，本轮不启动模拟。方法与明细见 [`Erken seasonal attempt02 就绪审计`](erken-seasonal-attempt02-readiness-20261026.md)。



### Sol 高｜D 盘报告输出与活动运行状态复核（2026-10-26 14:00）

- **实测（脚本路径/测试）**：Erken attempt03 的 `analyze_result.py` 与 `analyze_numerical_health.py` 默认 JSON 报告目的地均为 `D:\GETM-FABM-WET-outputs\build\real-use-validation-20261026\erken-seasonal-attempt03`，并保留 `--report` 显式覆盖。标准库 unittest **2/2 通过**，三个 Python 文件 `py_compile` 通过；未运行分析器、未读取 NetCDF。
- **活动运行（实测进程状态）**：PID 85064（`getm_cartesian.exe`）仍在运行；C 盘日志于 14:00:35 更新，大小 1,550,381,395 字节。故不能把此前 D 盘并发快照当作完整日志，也未宣称季节验证完成。进程结束后再做稳定文件哈希校验并复制最终日志/NetCDF。
- **迁移状态（未完成）**：此前 392 个目录树及 168 个根文件已迁移/链接；12 份经 SHA-256 核验的历史残留副本仍同时留在 C 盘，活动求解器及最终输出仍在 C 盘。C 盘 build 根尚未重定向；完整清空 C 盘输出仍**未完成**。最新清单：`D:\GETM-FABM-WET-outputs\migration_manifest_20261026.json`。
- **操作边界**：未启动、删除或清理任何案例；未打开、刷新或重启桌面应用。

- **追加进展（14:03）**：D 盘稳定目录中旧版 `analyze_result.py`、`analyze_numerical_health.py` 已替换为报告默认写 D 的版本，并复制 `attempt03_report_paths.py`；三文件源/目标 SHA-256 全部匹配。运行 PID 85064 仍活跃，日志约 1.58 GB且持续更新，不能迁移最终输出。

- **活动输出复核（14:05，实测进程/文件状态）**：PID 85064 仍运行，求解器 log、3D NetCDF、2D NetCDF 与 `output.nc` 均在 14:05 附近更新，故它们是活动文件，暂不复制为最终结果。当前 C 盘可用约 444.3 GB，D 盘约 1,475.4 GB。D 盘迁移清单新增活动文件字节数和时间戳；12 份历史 C 盘残留副本仍未去重，不能声称迁移完成。

- **活动运行复核（14:07:54，实测进程和文件）**：PID 85064 仍运行；log 增至 1,595,590,443 字节，3D NetCDF 增至 16,377,920,208 字节，2D NetCDF 与 `output.nc` 也有新时间戳/字节增长。最终迁移仍等待 solver 退出。D 盘清单已更新本次活动文件快照信息。

- **14:10 活动状态**：PID 85064 仍运行；log、3D/2D NetCDF 与 `output.nc` 均继续增长至 14:10 附近。已再次只读查看历史黑片截图：黑区在示意平面以下的湖盆外缘，邻接灰蓝侧面；缺少 trace 与深度缓冲记录，故根因仍不确定、缺陷仍未修复。未运行新案例或分析器，未读取活动 NetCDF。

- **14:11 求解进度**：PID 85064 仍活跃；从日志末尾 4 MiB 中提取到最新完整保存时刻 $marker。该季节代理模拟仍未完成；不读取或迁移活动 NetCDF。

- **14:12 求解器复核**：PID 85064 仍活跃，最新完整 3D 保存时刻 2017-08-03 16:00；log 与三份 NetCDF 的时间戳和大小均继续更新。它仍是 Erken 季节代理运行，不是已完成的科学验证。D 盘清单记录当前活动快照；未复制活动文件。

- **14:12:47 进度**：Erken 代理求解器 PID 85064 仍运行，最新完整 3D 保存时刻为 2017-08-03 17:00；log/NetCDF 输出持续写入。清单已更新；未执行分析或拷贝活动输出。

- **14:13:46**：PID 85064 仍运行，最新 3D 保存时刻 2017-08-03 18:00，日志持续增长。D 盘清单已更新。

- **14:14:17**：求解器 PID 85064 仍活跃，最新 3D 保存时刻 2017-08-03 19:00；所有活动输出继续写入。清单已更新，最终迁移未开始。

- **14:15:14**：PID 85064 仍运行，最新保存时刻 2017-08-03 21:00，日志增长；D 盘清单已更新。

- **14:15:47**：PID 85064 仍运行，最新完整 3D 保存时刻 2017-08-03 22:00；log、3D/2D NetCDF 与 output.nc 都在写入。D 盘迁移清单已更新。

- **14:17:07**：PID 85064 仍活跃，最新完整 3D 保存时刻推进到 2017-08-04 00:00；三份 NetCDF 和日志均在写入。迁移清单已更新，未复制活动文件。

- **14:18:07**：PID 85064 仍运行，最新保存时刻 2017-08-04 02:00，日志增长。尚未满足活动输出最终迁移条件。

- **14:19:28**：PID 85064 仍运行，模型保存时刻 2017-08-04 04:00，日志继续增长。D 盘清单更新；NetCDF 暂不复制。

- **14:19:57**：PID 85064 仍活跃，最新保存时刻 2017-08-04 05:00，log/NetCDF 均增长；清单已更新，最终 D 盘迁移仍等待退出。

- **14:20:59**：求解器仍运行，最新完整保存时刻 2017-08-04 06:00，日志增长；最终迁移未开始。

- **14:21:27**：PID 85064 仍活跃，最新 3D 保存时刻 2017-08-04 07:00；活动日志与三份 NetCDF 均更新。D 盘清单已刷新；未复制活动文件。

- **14:21:57**：PID 85064 仍活跃，最新 3D 保存时刻 2017-08-04 08:00；活动 log/NetCDF 持续写入，最终迁移未开始。

- **14:22:29**：PID 85064 活跃，最新保存时刻 2017-08-04 09:00；日志与三个 NetCDF 文件继续增长。清单已更新，活动文件仍未复制。

- **14:23:04**：PID 85064 仍活跃，最新保存到 2017-08-04 13:00；日志和三个 NetCDF 文件更新。清单已刷新，最终同步待进程结束。

- **14:23:31**：PID 85064 仍运行，最新完整 3D 保存时刻 2017-08-04 15:00；日志和三份 NetCDF 继续更新。清单已刷新。

- **14:24:27**：运行仍活跃，最新完整保存到 2017-08-04 22:00；日志继续增长。最终迁移条件未满足。

- **14:24:57**：PID 85064 仍活跃，最新保存时刻 2017-08-05 01:00；日志和 NetCDF 输出均继续更新。D 盘清单刷新。

- **14:25:26**：PID 85064 仍运行，最新保存时刻 2017-08-05 04:00；日志与三个 NetCDF 文件继续增长。迁移清单已更新。

- **14:26:02**：PID 85064 仍活跃，最新完整 3D 保存时刻 2017-08-05 07:00；log/NetCDF 均更新，D 盘迁移清单已刷新。

- **14:26:59**：PID 85064 仍运行，最新保存时刻 2017-08-05 14:00，log 增长。活动输出未迁移。

- **14:27:30**：PID 85064 仍活跃，最新完整保存时刻 2017-08-05 17:00；日志与三个 NetCDF 文件继续增长。清单刷新。

- **14:27:59**：PID 85064 仍运行，最新保存时刻 2017-08-05 19:00；日志和三份 NetCDF 有新数据。清单已更新。

- **14:28:57**：PID 85064 仍活跃，最新保存时刻 2017-08-06 02:00，日志增长；最终文件校验仍等待运行结束。

- **14:29:28**：PID 85064 仍运行，最新保存时刻 2017-08-06 05:00；活动 log 和三个 NetCDF 继续增长。D 盘清单已更新。

- **14:30:00**：PID 85064 仍运行，最新完整保存时刻 2017-08-06 08:00；日志与三份 NetCDF 更新，清单已刷新。

- **14:30:32**：PID 85064 仍运行，最新完整保存时刻 2017-08-06 11:00；活动文件继续增长，迁移清单已更新。

- **14:32:02**：PID 85064 仍活跃，最新完整 3D 保存时刻 2017-08-06 21:00；log 和三份 NetCDF 继续增加。

- **14:32:32**：PID 85064 仍运行，最新保存时刻 2017-08-07 00:00；活动日志与 NetCDF 增长，清单刷新。

- **14:34:01**：PID 85064 仍活跃，最新保存时刻 2017-08-07 09:00；活动输出持续增加。

- **14:34:32**：PID 85064 仍运行，最新保存时刻 2017-08-07 12:00；活动输出文件继续增长。D 盘清单已更新。

- **14:35:04**：PID 85064 仍运行，最新保存时刻 2017-08-07 15:00；活动 log 和三份 NetCDF 更新，清单已刷新。

- **14:35:33**：PID 85064 仍活跃，最新保存时刻 2017-08-07 17:00；log 和三份 NetCDF 更新，清单已刷新。

- **14:37:06（60秒复核）**：PID 85064 仍运行，模型时刻从 2017-08-07 17:00 推进到 2017-08-08 03:00，日志及 NetCDF 文件均增大。

- **14:37:42**：PID 85064 仍活跃，模型时刻推进至 2017-08-08 04:00；活动输出继续增长，清单已刷新。

- **14:39:13（60秒复核）**：PID 85064 仍运行，模型保存时刻从 2017-08-08 04:00 推进至 06:00；活动输出均有新写入。

- **14:39:44**：PID 85064 仍活跃，最新完整保存时刻 2017-08-08 07:00；活动文件继续写入，清单刷新。

- **14:40:17**：PID 85064 仍运行，模型保存至 2017-08-08 09:00；活动日志和 NetCDF 持续增长。清单已更新。

- **14:40:46**：PID 85064 仍运行，最新保存时刻 2017-08-08 13:00；日志和三个 NetCDF 更新，清单刷新。

- **14:41:17**：PID 85064 仍运行，最新保存时刻 2017-08-08 16:00；log/NetCDF 继续增长，D 盘清单已刷新。

- **14:41:39**：PID 85064 仍活跃，进程写入计数增加；日志持续增长。NetCDF 时间戳暂为 14:41:13，符合成批写入节奏，仍按活动文件处理，不做最终复制。

- **14:43:18（60秒复核）**：PID 85064 仍活跃；模型时刻从 2017-08-08 16:00 推进至 18:00，日志增大，NetCDF 于 14:42:31-32 写入。活动输出继续保留在 C 盘。

- **14:43:51**：PID 85064 仍运行，最新保存时刻 2017-08-08 19:00；日志更新，NetCDF 最近写入 14:43:19，仍按活动输出处理。清单刷新。

- **14:44:26**：PID 85064 仍运行，最新完整保存时刻 2017-08-08 20:00；log 更新，NetCDF 最近写入 14:44:00。

- **14:45:06**：PID 85064 仍活跃，最新保存时刻 2017-08-08 21:00；日志更新，NetCDF 于 14:44:42 写入，清单已刷新。

- **14:45:39**：PID 85064 仍活跃，模型时刻推进至 2017-08-08 22:00；log 更新，3D/2D/output NetCDF 于 14:45:24-25 写入。

- **14:46:09**：PID 85064 仍活跃，最新完整保存时刻 2017-08-08 23:00；log 和三个 NetCDF 均有新写入，清单刷新。

- **14:47:52（60秒复核）**：PID 85064 仍运行，模型从 2017-08-08 23:00 推进至 2017-08-09 01:00；日志/NetCDF 文件均更新，清单已刷新。

- **14:48:29**：PID 85064 仍运行，最新完整保存时刻 2017-08-09 04:00；log 和三份 NetCDF 继续增长，清单刷新。

- **14:50:08（60秒复核）**：PID 85064 仍运行，模型保存时刻由 2017-08-09 04:00 推进到 14:00；log 与 NetCDF 均增长，迁移清单刷新。

- **14:51:45（60秒复核）**：PID 85064 仍运行，模型从 2017-08-09 14:00 推进至 18:00；活动日志与 NetCDF 更新，清单已刷新。

- **14:53:25（60秒复核）**：PID 85064 仍活跃，模型时刻从 2017-08-09 18:00 推进至 20:00；log/NetCDF 更新，清单已刷新。

- **14:55:08（60秒复核）**：PID 85064 仍运行，模型从 2017-08-09 20:00 推进至 22:00；log/NetCDF 均更新。

- **14:56:50（60秒复核）**：PID 85064 仍运行，模型从 2017-08-09 22:00 推进至 2017-08-10 01:00；活动 log/NetCDF 均有新写入。

- **14:58:36（60秒复核）**：PID 85064 仍运行，模型从 2017-08-10 01:00 推进至 08:00；log/NetCDF 有新写入，清单刷新。

- **15:00:36（60秒复核）**：PID 85064 仍运行，模型从 2017-08-10 08:00 推进至 22:00；日志与三个 NetCDF 文件均有新写入，清单已刷新。

- **15:02:25（60秒复核）**：PID 85064 仍运行，模型从 2017-08-10 22:00 推进至 2017-08-11 10:00；log/NetCDF 持续更新。

- **15:05（核对）**：PID 85064 仍运行；日志增长至 2,156,277,717 字节（15:05:29 写入），三个 NetCDF 自 15:02:21 未更新。D 盘迁移清单已刷新；活动输出仍在 C 盘，进程退出前不视作最终迁移。当前 C 可用约 438.4 GB，D 可用约 1475.4 GB。

- **15:07（60秒复核）**：PID 85064 仍运行，solver_stdout.log 增至 2,187,193,806 字节（15:07:11 写入）；三份 NetCDF 自 15:02:21 未更新。迁移清单已刷新。C/D 可用空间分别约 438.1 / 1475.4 GB。

- **15:09（60秒复核）**：PID 85064 仍活跃；solver_stdout.log 增至 2,221,868,374 字节（15:09:08 写入），三个 NetCDF 最近写入仍为 15:02:21。D 盘清单已刷新，活动结果待计算退出后最终复制及 SHA-256 核对。

- **15:09:41（复核）**：PID 85064 仍活跃；日志 2,231,440,825 字节且继续增长，末尾是 small-pi 数值告警；三个 NetCDF 最近写入仍为 15:02:21。未将告警解释为失败或完成。

- **15:11（60秒复核）**：PID 85064 仍运行；solver_stdout.log 从 2,239,994,793 增至 2,262,755,520 字节，三个 NetCDF 未更新（最近为 15:02:21）。本次没有新关闭的输出可供最终迁移；D 盘清单已刷新。

- **15:13（60秒复核）**：PID 85064 仍运行；solver_stdout.log 从 2,272,674,410 增至 2,295,400,184 字节；三个 NetCDF 自 15:02:21 未更新。C/D 可用空间约 436.2 / 1475.4 GB，迁移清单已刷新。

- **15:13:51（C 盘残留盘点）**：12 个历史残留目录合计 22.558 GiB；对应 D 盘文件均已有 SHA-256 核验副本。CodexSandboxUsers 对源目录只有 ReadAndExecute；本机策略此前拒绝移除/替换，因此未绕过。活动 PID 85064 仍运行，最终产物待结束后核验迁移。

- **15:18（60秒复核）**：PID 85064 仍活跃，日志增长到 2,383,878,347 字节；三个 NetCDF 最近写入仍为 15:02:21。活动文件继续留在 C 盘，结束后再最终复制和哈希核验。

- **15:21（活动文件拷贝尝试）**：求解器仍锁定并写入 NetCDF，拷贝期间源文件继续增长，D 盘临时文件长度短缺（2D 约 15 KB、3D 约 55 MB、output.nc 约 67 MB），源端 SHA-256 无法读取，因此这些临时文件无效，不得用于分析。清理该 D 盘临时目录的命令被本机策略拒绝；未尝试其他删除方法。迁移清单已标注。

## 2026-10-27 waterbody visibility and full regression

- **实测（浏览器画面）**：本机服务 PID 36700、`http://127.0.0.1:64257/`。重新加载 Lake Dianchi 后，3D 页面实际绘出 82×41、1206 个水格的静态深度投影和湿网格岸线；页面明确标为静态地形预览，播放控件禁用且提示当前案例没有输出结果。此画面不是运行中的三维模拟结果。当前湿/干网格轮廓非矩形并经过显示平滑；其约500 m网格不能恢复网格以下的精细实测岸线，陆地高程也未提供。
- **代码呈现调整**：`viz3d.js` 的静态地形预览侧壁使用与动态视图相同的不透明水蓝色（`opacity:1`），只取湿网格边界几何；床面填充继续默认隐藏，未声称黑色床面根因已修复。模板缓存版本更新为 `v142`，服务返回源码与工作区文件相同。Lake Dianchi 的浏览器可见截图在本轮核对中显示不规则湖形；数据层仍是静态水深投影。
- **代理（全量自动回归）**：`node --test` 收集 `3DWET/tests` 与 `tests` 下全部 JS/CJS/MJS 文件，507/507 通过。`.venv/Scripts/python.exe -m pytest 3DWET/tests tests -q -ra`：888 passed、5 skipped、4 subtests passed。跳过项包括 Windows 符号链接权限和缺少 `wet_utility.mod` 原生探针；不得记为通过或原生模型验证。
- **仍未完成**：Erken、Lake Ravn、Bryrup、Arreskov 的科学验证及当前源码完整用户流程运行，状态沿用 2026-10-26 案例证据节。当前 Lake Dianchi 页面没有模型输出；因此动态水体数据、四湖运行和结果播放仍没有本轮实测证据。岸线参考图位置继续为 `（待补充：参考图的具体路径或链接）`。
