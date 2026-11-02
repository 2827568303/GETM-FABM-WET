# 原生续算差异定位（继续调查）

**后续进展：** 已定位主要差异为气象插值缓存重算及底摩擦周期重置，隔离候选在 16+4、10+10 分钟和周期性检查点实验中均通过，所比较状态误差为零。详见 [修复后的验证](2026-10-12-restart-cache-validation.md)。本文保留前阶段失败证据，未替换正式求解器；完整五轮仍为 0/5。

本轮取得了新的状态级证据，尚未修复全部续算差异。五轮完整验收仍为 **0/5**。原始用户案例、正式求解器及已安装程序均未替换。

## 可复现的新证据

新增 `scripts/probe_restart_state.py`：在隔离目录复制检查点，以零时长原生热启动后再次写出检查点，逐变量双精度比较；也可推进指定秒数，与同一绝对时刻的冷启动连续运行比较。

- [原求解器零步读入](2026-10-12-restart-investigation/original-zero-step.json)：水温 T、水位 z、流量 U/V、水柱和底部 FABM 状态一致。loop 被原生热启动重置；陆地上的 S/tke 等发生初始化处理。不能据此认定整个状态完整。
- [原求解器首个 2 秒时间步](2026-10-12-restart-investigation/original-first-step.json)：在 16 分钟检查点后第一步 V 已有约 2.07e-8 的差异，说明无需等到长时段末才能观察问题。
- [新增派生水深观测](2026-10-12-restart-investigation/derived-depth-difference.json)：零步初始化就使 D、DU、DV 分别变化约 8.94e-6、2.24e-6、4.47e-6 米。原积分顺序在 depth_update 后调用河流入流，水位变化但计算水深保留滞后状态；原检查点不保存 D/DU/DV，热启动重新计算改变这个状态。这是确认的一个差异来源，尚不能解释全部误差。

## 候选源码修正与结果

在原生源码增加 fU/fV、ru/rv 及 D/DU/DV、dry_u/dry_v 的检查点字段；读取旧文件保持兼容。读取完整新检查点时，初始化边界与 halo 后保留保存的内部计算水深，避免提前更新。科氏力在当前 NativeTest 中为零，因此不能用该案例证明新增 fU/fV 的非零科氏力行为。

通过 `scripts/rebuild_native_pressure_fix.py --restart` 构建隔离候选 `build/native-restart-fix/getm_cartesian.exe`。补齐了带校验的 MSYS2 NetCDF Fortran 开发模块和虚拟依赖解析；这些是构建工具，不加入用户安装依赖。构建清单见 [候选构建](2026-10-12-restart-investigation/candidate-build.json)。

候选首次水深恢复实验出现非有限结果，真实输出健康检查正确判失败。已修复局部备份数组误用含 halo 的维度造成的形状不一致，随后候选实际运行重新完成、结果有限；保留原失败工作目录 `-06`、`-07`，没有修改有效性检查标准。

**最新完整候选分段对比仍失败**：[实际报告](2026-10-12-restart-investigation/candidate-consistency-failed.json)，对应 `build/restart-acceptance-20261012-08`。16+4 分钟后 T 差约 0.0003685962°C，水柱 FABM 差约 0.0000364771。上述状态保存修正尚未消除主要误差，不应作为已修复交付；仍需检查时间步阶段、其他未序列化状态和强迫插值。继续沿第一步差异定位，不放宽 `rtol=1e-9, atol=1e-10`。

本轮原生候选构建成功，诊断/验收脚本语法检查成功。此前 325 passed / 3 skipped、前端 19 组证据仅覆盖 Python/JavaScript；不能证明这些新增原生源码已全面验收。正式求解器仍保留原文件，SHA-256 为 `f06a7219490a9d160f72c18788db463fe9cf1ec4881b0b0c52141d8762e65e8a`。
