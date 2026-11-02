# WET 多实例链路代码图（只读调查）

调查时间：2026-10-16。本文是设计依据，不表示新增实例功能已经实施或模型验证已通过。此次只读调查没有修改产品代码、已有文档、测试或浏览器，也没有运行模型、编译求解器、安装或提交。

## 已核实的结论

1. FABM 的 `instances` 本来就支持多个 `wet/phytoplankton` / `wet/fish` 对象，实例名决定原生状态路径。当前真正的限制在应用层和模板重建流程。
2. 本地与固定官方 master 都有动态猎物数/动态模型依赖端口，鱼类不是只能有三个实例。`fish_support.py` 的固定三鱼只是便捷模板，不是 WET 模型上限。
3. 猎物模型端口（例如 `PLANprey1: algae_a`）和状态端口（例如 `juvenile_C: fish_a/sC`）是两种不同类型。现有网络 API 只允许包含 `/` 的已有目标，因此不能完整编辑模型依赖猎物端口。
4. `/api/case/build` 从 Lake Luoma 覆盖 `fabm.yaml`，随后只恢复存活实例的初值；只给网络 UI 加“新增”会在重建时丢失实例。
5. 原生藻类贡献 `wet_chla`、`wet_totN/P/C`、`wet_totSusPar`；FABM 在装配时创建聚合计算器。新增藻实例不需要维护固定三藻的手工汇总列表。鱼类当前贡献 `wet_fish_totD`，不能未经核实把鱼 N/P/C 加进现有 `wet_totN/P/C` 定义。
6. GETM 检查点 `fabm_pel`/`fabm_ben` 按索引保存；当前 Python 热启动检查没有实例/状态顺序签名。新增、删除、重命名或调换实例后应拒绝复用旧检查点，即使数组长度未变。
7. 官方阶段鱼样例不是可直接照搬的生产模板：源码注册 `juvenile_C` 和 `adult_C`，高级样例相关阶段块没有这两项。必须按源码端口完整生成 C 耦合并真实验证。

## 本地文件与职责

路径均相对工作区 `C:/Users/23801/Desktop/GETM-FABM-WET-260928`；行号为调查时定位，实施时以函数名核对。

| 文件/定位 | 当前行为 | 所需集成点 |
|---|---|---|
| `3DWET/app/server.py:343` `MODULE_CATEGORIES` | 以 diatoms、greens、JuFish 等固定引用名分类 | 首先以 `model` 分类，旧名只作兼容；新增实例必须正确归入水质/生态独立目录 |
| `server.py:492` `parse_fabm_yaml` | 读 `fabm.yaml` 与 `fabm_disabled.yaml`，提供参数和初值，注释解析；可能迁移 legacy `_disabled` | 新目录纯读不能触发迁移/默认值落盘；分类、模型端口依赖和新状态由统一目录提供 |
| `server.py:582` `coupling_refs` | 仅解析含 `/` 的引用 | 必须包含 `prey_modelN`、`PLANpreyN` 等裸实例引用，才能保护删除/禁用 |
| `server.py:662` `_fabm_set_value` | 参数与 initialization 的旧单字段更新 | 涉及实例结构/初值的写入统一经过事务，避免绕过 revision |
| `server.py:727` `toggle_fabm_module` | 启停现有模块/侧文件 | 纳入跨文件备份、依赖预览和重启失效检查 |
| `server.py:2262` `/api/config/fabm` 系列 | 现有参数/模块入口 | 保留兼容路由；水质与生态分别按模型族过滤同一实际 FABM 文档 |
| `server.py:2455` `_fabm_instances` / output routes | 输出配置已有实例目录，兼容各种输出路径 | 与确切原生 manifest 合并，不能把旧结果字段当作新实例注册证据 |
| `server.py:6230` `/api/case/build`，6296–6356 | 无条件复制 Luoma 模板、固定鱼开关、保存的 `water_quality` 初值覆盖 | 新建与重建分开：已有 FABM 文档不覆盖；保留用户实例、耦合、参数、显示名与输出设置 |
| `server.py:5982` `_gen_fabm_init` | 本地修复后的 macrophytes 初值为 `(y,x)`、D/N/P/C 四个场 | 必须保留；不能退回 CLI generator 的单个 `(z,y,x)` 植物场 |
| `server.py:6916`–7190 `/api/case/init_conditions` | GET 按真实实例读 initialization，POST 保存 `module.variable` 到 `initial_conditions.json.water_quality`；POST 较宽松 | 保持旧字段兼容，改成 schema 校验/有限值/原子事务；新增鱼/藻各自初值不能丢失或串到旧实例 |
| `3DWET/app/lake_points_api.py:20` `native_yaml_scalar` | 使用当前 Fortran YAML 能读的单行标量，拒绝引号/流式括号/控制字符/歧义文本 | 新结构写入同样使用；不能直接让 safe_dump 的引号/锚点破坏 native reader |
| `lake_points_api.py:193` `load`；250 `network` | sha256(text + disabled text) revision，锁、案例身份、运行中保护、逐标量替换及备份 | 迁出实例相关逻辑到小模块；现有安全保护复用，扩展多文件 revision 和结构操作 |
| `lake_points_api.py:229` targets | 仅从 initialization 和现有 coupling 推目标，最终过滤必须含 `/` | 以已采用模型/条件端口能力目录生成“模型引用/状态引用”两类候选 |
| `3DWET/app/static/js/ecology_network.js` | 在 gridstudio 附加卡片，编辑已有 scalar/已有 port，无新增/复制/删除 | 真正实例组装器与关系编辑；可在独立生态页嵌入共用组件 |
| `3DWET/app/fish_support.py:34` / 102 / 176 | `FISH_INSTANCES` 三个固定名；固定启用三鱼、移除三鱼、判断必须三鱼都在 | 仅保留“添加标准三鱼组合”兼容模板；一般启用状态按 `model == wet/fish`，不得覆盖/删除自定义鱼 |
| `3DWET/model_builder/build_fabm_yaml.py:42` | 14 个固定 placeholder：三藻、两浮游动物、三鱼等 | 新案例种子模板仍可用；已有文档与任意实例通过共享装配服务保留 |
| `3DWET/model_builder/assemble_case.py:35` | build_all_configs + template builder | 和服务端使用同一创建/重建策略，避免 CLI 覆盖生态配置 |
| `3DWET/preprocessor/generate_initial_conditions.py:25` | 只生成固定 macrophytes_sD `(z,y,x)` | 与 `_gen_fabm_init` 存在已知路径差异；本任务统一到已修复 `(y,x)` D/N/P/C 生成器，保留旧接口 |
| `3DWET/app/output_subscriptions.py:82` `_inventory` | 按任意真实实例名展开 native `instance_state`；变量来自 docs 与 initialization，合并旧输出 observed 字段 | 条件状态/动态 diagnostics 必须以已采用 binary 指纹的 manifest 校验，明确 expected 与 observed；新鱼最小输出加入默认订阅 |
| `3DWET/app/output_subscriptions.py:166` `preset_sources` | standard 只含水质四状态、藻 sDW、碳/甲烷；无鱼 | 生态必需状态显式订阅，已有用户 exact selectors 不自动泛化为所有字段 |
| `3DWET/app/variable_reference.py:194` `_instance` | 最长实例名前缀匹配；能读自定义实例模型 | 复用动态前缀能力，label 读显示名，原生 units 优先；suffix 识别不要假设固定名 |
| `variable_reference.py:206` `_record`；`variable_registry.json` | model→local variable 元数据、支持 `*` 数字诊断规则；docs fallback | 动态 nPrey 家族及 qStage 条件标记在能力目录中，不复制每个新实例到全局 registry |
| `3DWET/app/parameter_defaults.py:90` `annotate_defaults` | 默认值快照按实例名存储 | 复制/重命名/删除/恢复时同步快照，避免旧名残留与新实例默认值取错 |
| `3DWET/app/hotstart.py:16` `_temporal_memory_info`，100 `prepare_restart` | 检查 grid、现有 FABM 状态存在、光照时间均值/植物诊断记忆；设置 init method=0 | 补生态文档/solver/状态顺序签名与 checkpoint 文件 hash，拓扑变更拒绝热启，不重写 native 数组 |
| `3DWET/app/server.py:1728` `run_model_thread` /1689 archive | 运行当前 executable；输出健康检查后归档 | 启动时固定 revision，检查点登记保存此 revision/solver 与签名；重启旁车随检查点复制/归档 |
| `3DWET/app/run_output_health.py:114` | 最终记录有限值检查，检测数值失败，不证明科学正确 | 验收脚本额外扫描新增必需状态全时段湿网格、响应和耦合通量 |

## 原生模型与端口证据

### 鱼类

`3DWET/src/wet/src/fish.F90`：

- 110：`qStage=0/1/2/3`，对应无阶段/繁殖/成熟/两者。
- 136–170：nPLAN、nBEN、nPISC 分别分配动态数组；每猎物 clearance 与 gut occupation 参数。
- 199–218：独立 sD/sN/sP/sC/fVul；qStage>0 额外 sFRes/sDSiz；qTrans 决定运输。
- 224：每实例对 wet_fish_totD 的贡献。
- 251–259：`PLANpreyN` **模型依赖**，自动请求目标 `sD/P/N/C + PLANprey_suffixN`。藻类水相后缀是 W，普通 zoo 后缀省略空值。
- 293–310：`BENTpreyN` 模型依赖，同步请求底栖 sD/P/N/C 与 `_PV`；普通底栖后缀空，有机物沉积相通常 S。仅有 g/m3 状态的对象不能充当 BEN prey。
- 338–353：`PISCpreyN` 模型依赖，目标必须有 sD/N/P/C、fVul、pred_dummy；不能只检查目标名存在。
- 363–390：阶段需要 `juvenile_D/N/P/C/Res/Siz` 与 `adult_D/N/P/C/Res/Siz` **状态依赖**；官方注释说明自动模型阶段耦合有 circular dependency，手动状态映射可用，不应虚构 `adult_target` 端口。
- 451–452：Day_last 是 hidden diagnostic，并没有 `column_memory` property。现有 temporal restart 的 diagnostic memory 只保存带该 property 的变量；阶段繁殖跨重启日期的记忆需专项验证，不能由 qStage=0 通过推断 qStage>0 通过。
- 1209–1279：check_state 读取/更新 Day_last 和 reserve；本地 qStage guard 与 reproduction diagnostic guard 是需要保留的修复。

### 藻类与浮游动物

`3DWET/src/wet/src/phytoplankton.F90:154` 起注册独立水相 sDW/sNW/sPW/sCW、沉积相与 pelagic mirror；`:254–259` 注册聚合贡献。每藻的营养盐、氧、POM/DOM、沉积物/界面是真实状态依赖，不应因“生态独立入口”而从水质过程断开。

`3DWET/src/wet/src/zooplankton.F90:81–94` 动态 `nPrey`、`cClearPreyN`、`fGutOccPreyN`、`prey_suffixN`、`lSiN`；`:142–153` `prey_modelN` 模型依赖与 sD/N/P/C 后缀，lSiN=true 时还需要 oSi 后缀。新增藻要进入食物网，必须增加 prey_modelN 与 nPrey/相关参数，不能只连图。

### 聚合与原生字段

`3DWET/src/fabm/src/fabm_coupling.F90:126–136` 的 create_aggregate_models 在耦合时从真实模型贡献创建求和对象；`:565` 起收集贡献。当前案例 YAML 没有固定三藻的 wet_chla_calculator 实例块，观察到的 calculator 结果由 FABM 自动生成。实施需保留自动聚合，若导入案例含显式自定义 summation 实例，只按确切识别模型重写其真实列表并预览差异，未知自定义汇总阻止有破坏性的删除，不猜测公式。

`3DWET/src/getm/src/3d/getm_fabm.F90:327–360`：cold method 1/2 先用 YAML uniform states；method 2 只覆盖初值文件里存在的字段（missing不报错）。新增藻/鱼的 uniform initialization 可以直接生效，但必须拒绝旧 fabm_init.nc 中同名字段无意覆盖新初值。`:468–478` 按 model registered state name/units 注册输出字段。

`3DWET/src/getm/src/ncdf/create_restart_ncdf.F90:83,252–262`：FABM pel/benthic维数与数组；`open_restart_ncdf.F90:292–301` 只查数组变量；`read_restart_ncdf.F90:429` 起按当前数组长度读取。原生 `fabm_temporal_restart.h` 已核验 temporal expression identity 和 diagnostic name，不等于普通 FABM state identity 已核验。

## 官方来源与采用边界

- 最新发布：v2.3，`89e172cd6f113bff2ffe9e9680cbbeb7e0dd92a6`，已保存官方 tags API 原文。官方 [Zenodo v2.3](https://zenodo.org/records/17453175) 说明阶段鱼仍是 development version；不能将其描述为已验证稳定的物种模型。
- 最新 master 固定：`d2eee4419ab6762c092e07dc79316feff9efec5c`。已保存源码 ZIP SHA256 `457c39fcb052799189a6379bead90dd98501aae798a6ef2516270e3ebc058941`；本次从 ZIP 直接读取并核对以下能力，不依赖网页印象。
- [官方 fish 固定源码](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/d2eee4419ab6762c092e07dc79316feff9efec5c/src/fish.F90)：137/149/162动态计数，252/294/339模型端口；225鱼总干重聚合。
- [官方 zooplankton 固定源码](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/d2eee4419ab6762c092e07dc79316feff9efec5c/src/zooplankton.F90)：81动态计数，142–153动态模型依赖；与本地逐行规范换行后相同。
- [官方 phytoplankton 固定源码](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/d2eee4419ab6762c092e07dc79316feff9efec5c/src/phytoplankton.F90)：259–264聚合贡献仍保留。
- [官方高级鱼样例](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/d2eee4419ab6762c092e07dc79316feff9efec5c/testcases/fabm-wet_advanced_fish.yaml)：F0/F1/F2/F3/P0五鱼、diatoms/largeCyano/smallCyano三藻、四个 pisc prey，证明不是三个硬编码实例；阶段映射未列 C，生成器应依据源码补齐。
- 网页工具读取 GitLab 固定 blob 返回403；以上源码定位依据已下载并校验 ZIP。Zenodo 页面已成功读取。官方仓库地址：[WET GitLab](https://gitlab.com/wateritech-public/waterecosystemstool/wet)。

现有规范换行差异表 `build/wet-upstream-research-20261016/source-comparison-normalized.json` 显示：zooplankton、zoobenthos、bivalves、bot_pel_interface、fish_pclake 等一致；fish 126差异行、macrophytes 269、om_pool 713、phytoplankton 277。差异方向是“本地→上游”，`fish.F90.diff` 中 `+ id_time_step` 意味着上游仍有旧依赖，不能当成应回补的新修复。本任务采用官方最新核实的动态能力并保留本地修复，不整体覆盖 WET 树，不替换运行中的 solver，不启用 master 的 ghg_gasses 替代自有 inorganic_carbon/methane。

## 自审记录

- 已覆盖任意两藻+两鱼、唯一引用名/显示名、真 prey ports、重建、初值、输出、聚合、重启和上游保护。
- 已区分源码能力、当前 UI 功能和计划功能；没有将本研究计为真实运行或正式五轮通过。
- 阶段鱼 Day_last 持久化与旧检查点普通状态身份是待实施验证风险，明确列出，未虚报已解决。
- 独立实施计划：`docs/superpowers/plans/2026-10-16-wet-instances-implementation.md`。
