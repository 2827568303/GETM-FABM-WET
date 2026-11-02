# 同湖实测文件夹与深度率定实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task. 本文件落实已批准设计；不再要求用户重新批准。各项红→绿并独立审查，完成源码后仍须统一桌面更新与五轮完整验收。

**Goal:** 让用户导入真实观测文件夹，以同湖、同位置、同时间、同深度和同单位进行比较与实际优化，并提供可运行的官方Ravn原柱模型案例。

**Architecture:** 独立观测解析/存储模块保留原文、来源和质量标记；匹配模块直接按观测读取原生时刻与垂向几何，不使用绘图抽稀结果。当前GETM与官方原GOTM案例由明确引擎适配器读写，原柱模型代表性假设不得冒充三维测站。

**Tech Stack:** 现有Python/Flask、NetCDF4/NumPy、CSV/openpyxl、原生JavaScript，现有SciPy/ABC率定控制器与实际本地求解器。

依据：`docs/audit/2026-10-16-ravn-observation-mapping.md`。官方默认GOTM原样16年运行证据见 `build/ravn-official-replay-20261017-attempt01`；隔离工作副本的应用原生运行工程复现见 `build/ravn-official-working-copy-run-20261021-attempt01`。该次运行只证明默认一维 GOTM 工程链路及输出可用，不完成此计划中的观测核验、率定、训练/留出优化或五轮完整验收。科学基线与五套新生成验证数据分开记录，正式计数0/5。

## 任务1：保留完整观测语义的解析器

Files: create `3DWET/app/observations.py`, `tests/test_observations.py`；modify server的CSV/XLSX解析入口，保持已有time/value导入可读。

- [ ] 写红测试：官方四列`.obs`的日期+时间、负的米深度转正向下、原值/行号/文件SHA保留；CSV/XLSX保留depth、unit、station、lake、quality；NaN/Inf与无日期值拒绝且给逐行原因。不得静默丢字段或坏行。
- [ ] 运行 `.venv/Scripts/python.exe -m pytest tests/test_observations.py -q` 确认失败。
- [ ] 实现 `parse_observations(path, mapping)` 返回规范记录及逐行诊断。记录字段：`time,value,depth_m,unit,variable,lake_id,station_id,quality,source_file,source_line,source_sha256`；源时间无时区时保留`time_basis=source_naive`，不按本机时区移位。映射缺失字段保持未知，不填虚假测站/单位。
- [ ] 相同湖/站/变量/时刻/深度的完全重复记录可折叠并保存全部来源；冲突值隔离。TEMP72°C、-99m不更正或丢弃，标为待审；范围筛选与原文分开。
- [ ] 以保留的8份Ravn原观测重跑，逐文件核对盘点总行数、重复/冲突及异常证据；测试通过后独立审查。

## 任务2：案例隔离存储与原子导入

Files: create `3DWET/app/observation_store.py`, `tests/test_observation_store.py`；modify `server.py`校准保存/加载及导入API。

- [ ] 红测试两个不同案例相同point_id不得互见观测；无活动案例拒绝写入；路径穿越/符号链接跳出所选目录拒绝；导入失败不得部分覆盖已有数据；运行/率定中的配置快照保持不变。
- [ ] 实现案例目录 `calibration/observations.json` 和来源manifest的版本化存储，临时写后原子替换并保留前版本备份。原全局time/value数据仅经明确迁移目标进入案例，未知湖身份不自动宣称匹配。
- [ ] 文件夹流程分为preview与apply。preview返回文件、变量/单位、时间/深度范围、湖/站身份、异常与待补映射，不写正式库；apply提交预览内容SHA及映射版本，拒绝预览后文件变化。
- [ ] API仅接受用户选择的本地目录或上传文件，不自动扫描用户其他目录。JSON/CSV/OBS是数据，不执行其中命令或脚本。
- [ ] 运行 `.venv/Scripts/python.exe -m pytest tests/test_observation_store.py tests/test_observations.py -q`，实际创建两个隔离诊断案例导入/重载/恢复并核对SHA。

## 任务3：严格深度、时间与单位匹配

Files: create `3DWET/app/observation_matching.py`, `tests/test_observation_matching.py`；modify `server.py:calibration_comparison`、`calibration.py:run_model_in_temp`及评分调用。

- [ ] 红测试：同名不同湖拒绝；不同测站或未知三维坐标不自动最近格套用；观测10米不得匹配表层；同一时刻不同深度全部保留；不重用同一观察行重复计权；无时间重叠返回明确无配对。
- [ ] 对GETM直接使用共享 `read_vertical_geometry` 获取对应时刻实际hn/zc及列深度，观测深度在有效中心间按显式线性插值；超出有效中心范围不外推，并报告未配对原因。干格/缺测/坏几何不填零。接口变量不能冒充层中心浓度。
- [ ] 时间在原生有效输出时刻间线性插值，限定最大间隔；不先抽稀3000点，不按全局24h容差盲配；超过模拟窗和不兼容calendar拒绝。声明无时区的官方原柱模型/原观测可按同一原历时比较，UTC三维案例须有对应时间依据。
- [ ] 单位按量纲和物质基础白名单变换：mg/L与g/m³数值相等，µg/L与mg/m³相等，°C按实际metadata识别；N/P/O2质量基础不能凭名称推断；未知/冲突单位拒绝进入目标。NO23默认不映射为纯NO3，总N/P必须确认实际聚合定义及单位。
- [ ] 返回每条配对的原观测引用、模拟两侧时刻/层、插值权重、深度与单位转换、排除理由；图与优化共享同一个配对器及快照，避免界面评分与优化评分不同。
- [ ] 运行 `.venv/Scripts/python.exe -m pytest tests/test_observation_matching.py -q`；对一套独立可手算的多时刻/非等厚层测试核对精确数值，再以真实native结果抽样复核。

## 任务4：官方Ravn可运行案例适配

Files: create `3DWET/app/reference_cases.py`, `3DWET/app/reference_gotm.py`, `tests/test_reference_ravn.py`；modify现有案例发现/运行/输出查找/率定参数适配，不把旧模型直接复制成GETM配置。

- [x] 校验官方默认ZIP SHA、在新目录原样运行1990–2005完整模型，检查退出、完整时间窗、层厚、有限输出及变更文件；证据已保存。
- [ ] 红测试原GOTM输出 `time,z,lat,lon` 与h层厚、计算器别名/单位；引擎标识不得误报GETM；原始restart写出保持源ZIP可恢复；配置路径/运行日志/输出完整性按该引擎实际约定验证。
- [ ] 适配 `engine=official_gotm_reference` 案例，明确旧GOTM/FABM/WET具体版本及原柱模型代表性；从用户已下载原目录或官方URL按需复制/下载到用户案例空间，保存来源和校验，不将未核实再分发许可的原exe/数据塞进公开安装包。
- [ ] Ravn库绑定官方文档湖身份和原柱模型范围，观测未知精确站位不生成三维(i,j)。不同湖及GETM三维项目不能自动应用Ravn观测；三维迁移另需真实站位/河口/原配置映射与原生验证。
- [ ] 先以TEMP/DO/CHLA具备明确量纲字段的观测完成实际基线比较；NH4/PO4/总N/P等按确认的物质基础/聚合metadata逐项启用，NO23保留待核实。保留1971–2018全库但评分只取模型时间窗。
- [ ] 实际优化使用默认参数起点和明确参数边界，1990–1995热身、1996–2000训练、2001–2005留出；此分割是工程选择，并非官方原训练分割。已率定官方参数不可称为留出未使用的起点。记录真实每次模型运行/目标值，完成最优应用、重跑与备份恢复；模型失败不得给伪评分。

## 任务5：简洁的观测管理与科学比较界面

Files: create `static/js/observation_manager.js` 和对应样式；modify `index.html`, `workflow_navigation.js`, `app.js`, `static/i18n/en.json`；tests `3DWET/tests/test_observation_manager.js`及实际浏览器。

- [ ] 红测试两个入口“已有实测案例/导入观测文件夹”可达且不扩大初始五组菜单；预览显示真实变量/单位/深度/时间/来源；未知项无法静默通过自动匹配。
- [ ] 界面分为选择目录→审阅映射与质量→应用到当前同湖案例；日常使用只显示摘要和下一步，逐行诊断及插值证据按需展开。保留旧CSV/XLSX入口及明确的表层旧数据语义。
- [ ] 比较图清晰区分观测/模型、训练/留出、深度、单位；无配对不画虚假曲线；所有图例/轴与白背景对比足够。优化/停止/结果/应用最佳/恢复使用已有运行控制器和事务回执。
- [ ] 实际UI导入官方文件夹和自有含多个深度/冲突/错误单位的文件夹：预览、拒绝错湖、应用、重载、同深度比较、训练、留出、停止、最佳应用和恢复，检查桌面与窄屏、双语及真实导出。

## 任务6：整版集成与五轮门槛

- [ ] 全部前后端回归，需求审查后质量审查，运行官方原Ravn实际比较/优化闭环并保留输入、结果和评分依据；不能只以解析器或原模型退出0声称率定完成。
- [ ] 与生态实例、显示几何、通知及其他既有问题集中集成后统一冻结源码/求解器/资源、更新桌面；所有专项在实际安装版复验。
- [ ] 五轮各生成不同的新数据，从上传/网格/配置/原生完整模型到全部功能与最终产物连续成功。任何失败或未跑完归零；Ravn真实科学示例单独验，不把它当五个新数据案例，也不把合成核验数据冒充实测。

当前状态：除原官方运行基线外均未实施；不得据此计划文字宣称功能已交付。
