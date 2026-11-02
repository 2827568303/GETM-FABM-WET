# 续算一致性修复与验证

本轮已在隔离原生候选中修复 NativeTest 续算差异，并实际证明指定分段运行与连续运行一致。**完整五轮不同数据工作流仍为 0/5，正式安装包尚未更新。**

## 根因与修改

1. 气象模块在数据记录处计算依赖水温的热通量和风应力，再按时间插值。旧检查点没有保存这些缓存，热启动用新的检查点水温重算，导致同一绝对时刻热通量相差约 1.78 W/m²。见 [首步通量对比](2026-10-12-restart-cache-validation/first-step-flux-difference.json)。
2. 原热启动会重置步数，底摩擦更新周期因此改变；补充绝对微步偏移并按绝对步数保持动量交替顺序。epoch 模式已使用绝对步数，不叠加偏移。
3. 延续上一阶段修改，保存二维动量项和河流入流后的滞后计算水深；初始化边界后恢复内部状态。
4. 气象缓存采用带 schema 的 NetCDF 字段，保存绝对时间边界。恢复后，在同一气象区间重用原缓存，进入真正新气象区间则沿用正常更新。周期性检查点写入可复用已定义字段，避免第二次写入时重复定义失败。旧检查点没有缓存时仍可读取，但不能据此保证严格一致性。
5. 热启动网格验证改用 `domain.kdum` 判断垂向层数；`m3d.M` 是时间分裂因子。针对两者不相等的失败测试已复现并修复。

## 实际原生证据

所有比较保持 `rtol=1e-9, atol=1e-10`，没有放宽标准：

| 实验 | 结果 |
|---|---|
| 16+4 分钟，修复气象缓存后 | [通过](2026-10-12-restart-cache-validation/aligned-passed.json)。检查的 T、z、U/V、uu/vv、hn、水柱 FABM 72 个状态、底部 FABM 39 个状态，最大绝对误差均为 0。 |
| 10+10 分钟，仅修复气象缓存 | [保留失败](2026-10-12-restart-cache-validation/friction-phase-failed.json)。进一步定位到底摩擦更新周期重置。 |
| 10+10 分钟，补齐更新周期后 | [通过](2026-10-12-restart-cache-validation/ten-plus-ten-passed.json)。上述状态最大绝对误差均为 0。 |
| 每 30 步保存一次检查点，再续跑 10 分钟 | [通过](2026-10-12-restart-cache-validation/periodic-passed.json)。重复写入实际执行，最终检查点及续算结果有效；上述状态最大绝对误差均为 0。 |

可复现：`python scripts/rebuild_native_pressure_fix.py --restart`，再运行 `python scripts/verify_restart_acceptance.py --work <新目录> --solver build/native-restart-fix/getm_cartesian.exe`。另可加 `--checkpoint-seconds 960` 或 `--checkpoint-every-steps 30`。构建工具及候选均留在 build，原 `3DWET/bin/getm_cartesian.exe` 未替换。[最新候选构建清单](2026-10-12-restart-cache-validation/candidate-build.json) 和验收 JSON 保留实际求解器 SHA-256。

这些证据限于当前 NativeTest、原配置的气象计算方式及所列检查点时间。尚未证明非完整三维宏步检查点、其他强迫方式、epoch 模式、MPI、多次连续重启或改变时间步长后的严格一致性；不能据此宣称所有重启组合均通过。

## 回归与剩余验收

- Python：**326 passed，3 skipped，21.76 秒**，见 [完整输出](2026-10-12-restart-cache-validation/python-tests.txt)。跳过项仍为符号链接权限限制。
- 前端：**19 组通过**，见 [逐组输出](2026-10-12-restart-cache-validation/javascript-tests.json)。修复英语界面把质量“中”显示为“in”，改用明确的“中等 / Medium”；补充生成剖面按钮翻译。另有 UI 结构 3 项针对性回归通过。此处不声称实际浏览器全界面已验收。
- 当前源码存在有效输入的案例共五个，隔离候选正在逐一执行默认配置求解和完整结果 API 验收。已收到 Lake Dianchi、Lake Luoma、NativeTest、Theoretical lake 通过输出；剩余结果必须等待正在运行的验证进程，不重复启动。工作目录 `build/builtin-restart-candidate-20261012-01`，执行会话 93044。下轮需先复核进程真实状态，再据最终 JSON 更新结论。
- 安装包还会生成 StudioDemo 教学案例，源码五案例验收不能替代最终安装包六案例验收。
- 动态语言覆盖、通知与面测深链路、不同数据五轮完整流程、最终打包安装及清理仍需完成。短时一致性也不替代真实观测精度、年度稳定性及守恒验证。
