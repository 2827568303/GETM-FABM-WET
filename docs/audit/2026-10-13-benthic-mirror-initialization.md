# WET 底面库存与 PV 镜像初始化修复

连续完整验收仍为 **0/5**。以下是同输入诊断与独立回归，不计作完整新轮。

第9次完整尝试已失败：外部输入、功能、结果阶段通过，但真实 SciPy 率定约446.72秒，超过五分钟要求。日志进一步发现，求解器虽返回0并输出 Completed，仍产生零状态负导数错误；不能凭退出码或结果有限就认定模型健康。

## 根因与修复

生成的空间初值将沉水植物底面库存赋为正值，YAML 中四项 PV 为0。仅修复该组后，DOM 仍存在同类不一致：底面 D/N/P/C 分别为10、0.06、0.01、4，PV 默认值却为0.001、0.0001、0.00001、0.0004。矿化根据底面库存计算损失，向 PV 施加相应导数，过小 PV 快速耗尽，EMP 出现 small-pi 停滞。

`init_getm_fabm_fields` 在初始化方法1/2的 YAML 和可选 NetCDF 加载完成后、halo 更新前调用 `initialize_wet_benthic_mirrors`。它按完整变量名逐项匹配规范 WET 实例的 D/N/P/C，将湿单元底面库存复制至物理底层 k=1 的 PV。真实零值保持零，不添加 epsilon，不修改生态通量或 EMP 算法。方法0热启动不改写。foreign `_PV` 不套用此约定。

规范实例范围：macrophytes、zoobenthos、bivalves、POM、DOM、humus、cyanobacteria、diatoms、greens。任意重新命名的其他实例尚未覆盖，不能把本修复描述为所有第三方 FABM 模型的通用初始化。

运行层新增识别实际 `Error: state variable ... is zero and has negative derivative!`，避免将退出码0的此类运行归为成功。单独 small-pi 警告不据此规则判失败；本次原生回归另外检查其数量为0。

## 实际证据

- 首次4项 helper 和日志测试先失败、修复后8项通过；扩展白名单后9种原生编译测试及运行层共16项通过。测试打乱变量注册顺序，使用不等比例库存，检查零值、干单元、上层、边界层、foreign 及缺失变量。
- [旧/新求解器同输入对比](../../build/benthic-mirrors-native-diagnostic/verification.json)：旧版零状态负导数30,400次、small-pi警告17,696次（其中精确0共16,370次）；新候选两类均0。实际注册32项镜像初差均0；所有扫描状态有限，底面库存发生实际变化。21输出记录覆盖0至20分钟。
- 候选求解器 SHA-256：`e587217cb411d123dc19f5f6dc6d2657b1491528365077710a6174c4fbb4710f`，构建见 `build/native-benthic-mirrors-fix/build.json`。
- 仅沉水植物修复的中间候选仍有8,010次精确0 small-pi警告，不能宣称已解决全部初始化；保留在 `build/macrophyte-mirrors-diagnostic/verification.json`。该中间候选的真实率定30次评估达到精确0，但约423.94秒，仍未满足性能要求。
- 独立只读审查未发现当前白名单复制逻辑的可操作缺陷；bivalves未在本次实际案例注册，其证据来自原生编译 helper 测试。

完整白名单候选的[热启动复测](../../build/benthic-mirrors-restart-diagnostic/verification.json)通过：T/z/U/V/uu/vv/hn差值0，fabm_pel最大差约9.56e-11，fabm_ben约2.70e-11，均在既定rtol=1e-9、atol=1e-10内。最终全量回归为361 passed、3 skipped（Windows符号链接权限），80.07秒；独立审查16项通过。

默认求解器已提升为该候选，旧版保存在 `build/solver-before-benthic-promotion-20261013/getm_cartesian.exe`。第10次完整尝试使用新种子2026101308、面测深数据从头开始，记录见 `build/full-workflow-20261013-attempt10/round.json`；须全部六后台阶段、十项真实界面检查通过才能计为1/5。正式安装包尚未同步。短程合成数据不证明全年科学准确性。
