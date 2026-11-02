# 当前列诊断与原生日志修复

连续完整验收仍为 **0/5**，第13次失败保留。以下同输入追踪和候选复验均不算新的完整轮次。

## 故障与因果证据

第13次20分钟连续运行与10分钟后重启运行的水动力七项完全相同，生态pelagic最大差1.407519850005201e-6、benthic最大差1.3331009540706873e-7，差异集中在首个湿格底部无机物及沉积交换链。

隔离诊断程序 `build/diagnose_restart_bioturb.py` 保留原始源码不动，只在私有sediment_exchange副本记录依赖和通量。`build/restart-bioturb-trace`、`build/restart-bioturb-trace2`复现完全相同的差异。对齐连续运行600秒之后首次RHS与热启动首次RHS：

|量|连续|热启动|
|---|---:|---:|
|当前底部水体DIM|9.978028292250043|9.978028292250043|
|当前沉积DIM|31700.005957628524|31700.005957628524|
|底部剪切|4.681045684409686e-9|4.681045684409686e-9|
|植被聚合依赖DragVeg|14.674500746240094|14.997963595652882|
|鱼类扰动BioTurb|0.4041715389087434|0.4041713115567383|
|DIM再悬浮通量|1.2272574245036278e-6|1.1527149980139934e-6|

FABM底部调用列表不执行interior `source_do`，而植被聚合和鱼类扰动等依赖由interior计算更新。正常RHS原先先bottom后interior，使用前列缓存；启动额外interior计算改变首格缓存，所以相同状态的热启动路径发生分歧。该原因由源码与真实通量追踪相互支持，不是放宽容差后的“通过”。

## 修复与验证

- GOTM RHS每次链接当前列/积分阶段并检查状态后，仅执行一次interior，单独存储体积源项。随后计算底部/表面通量、完成面积到体积换算，最后相加。PP/DD同样使用独立矩阵，避免底层interior项错误除层厚。
- `tests/test_native_rhs_diagnostics.py`编译实际RHS及PP/DD例程，以状态依赖诊断模拟不同阶段，检查当前缓存、单次调用、不同层厚、多个底层交换、表面通量、benthic项及零层不污染；两项通过。真实WET PP/DD运行与任意第三方FABM依赖环不由该stub证明。
- `scripts/rebuild_native_pressure_fix.py`私有重编译GOTM驱动后再链接；最终候选 `build/native-current-column-diagnostics/getm_cartesian.exe` SHA256 `7bd2eeba7c261f355c65bacf5e82cc72cbc7ede7d6e6e857e821ed1aa68615f2`，尚未替换默认求解器。
- 最终源码候选真实复验 `build/restart-current-column-final/verification.json`：九项全部通过，包含pelagic/benthic，每项最大绝对差均为0。
- 完整Python回归：`pytest tests 3DWET/tests -q --tb=short`，**384 passed、3 skipped，33.04秒**，跳过项为Windows符号链接权限。
- 独立只读审查未发现当前WET配置下新增可操作缺陷，并明确提醒必须保留interior源项单位、避免重复计算。

另一次 `current-column-mirrors-diagnostic`调用了专为“旧二进制必须复现零状态错误”设计的历史比较脚本，旧默认二进制已含镜像修复，所以该脚本首个历史前提断言失败；该报告保持失败。候选实际运行已完成，零负导数、零small-pi警告，初始镜像无误差，不能把这个脚本的失败改写成整体验收通过。

原生运行线程另已修复stdout被丢弃的问题：stdout与stderr共同写入日志，检测到零状态负导数立即终止并判失败，不归档成功输出。真实编译Fortran进程回归覆盖此路径，相关15项测试通过。

## 尚待处理

24小时PAR temporal_mean的长时间历史没有保存到热启动文件；共享单列驱动还需要核对是否在水柱间混用历史。此次20分钟mean尚未有效，不能以九项一致宣称长期历史已修复。需独立验证和修复后，再从全新数据开始完整五轮。正式安装版交付及六个内置案例最终验收也尚未完成。

后续核对已确认共享历史及采样顺序缺口。`build/diagnose_temporal_history.py`仅在隔离的phytoplankton源码副本将period/resolution改为120/20秒，生产源码仍为86400/3600秒。原始短窗口构建曾因同名archive member覆盖SELMA对象而链接失败；改为显式对象优先链接、保留原archive后成功。`build/restart-short-memory-probe2/verification.json`实际连续/重启对比失败：水动力七项仍0差异，生态pelagic差2.0502641362440954e-7、benthic差8.846789967265067e-9。此为加速记忆诊断，不是改变生产科学窗口的验收替代。

当前源码五案例复验 `build/current-column-builtin-cases/verification.json` 仅Lake Dianchi、NativeTest通过；Lake Luoma、Theoretical lake、_fish_probe被体检正确阻断（旧`fabm = '.true.'`）。三个源配置已复用现有UI同一窄范围修复函数移除引号，原文件及逐项hash保存在 `build/builtin-logical-source-backup-20261014-02`，未改变真假值。新复验目录 `build/current-column-builtin-fixed-config2` 尚须读最终报告。误启动的 `current-column-builtin-fixed-config` 已主动停止，不能视为成功证据。旧release stage仍含旧配置及旧程序，未交付更新。
