# 修复时间均值水柱隔离与续算

现有目标仍要求每项功能独立验证及不同数据连续完整五轮，当前0/5。时间记忆缺陷现已修复，详见下方最新状态；早期证据与计划保留。

## 最新执行状态

2026-10-14：步骤1–6完成。最终98f359…候选的28小时生产窗口跨年续算30字段全部0差，萌发记忆的独立原生测试通过；五个源码内置案例全部运行和结果验证通过；405 passed/3 skipped。详见 `docs/audit/2026-10-14-temporal-and-ecological-memory.md`。

步骤7进行中：旧默认已备份至 `build/solver-before-ecological-memory-promotion-20261014`，默认提升为98f359…；第14次完整尝试使用全新2026101404种子、多边形水深。只有六后端阶段及十UI组全部完成才可计为1/5。安装版与五轮尚未完成。

## 已有证据

- 首列interior诊断缓存问题已在最终候选修复，`restart-current-column-final`九状态最大差均0。默认二进制仍旧e587…，未提升7bd2…候选。
- 原生RHS/PPDD组合测试2通过，完整Python384通过/3权限跳过。
- 生产24小时PAR窗口源码未改变；隔离120秒窗口真实对比失败，见 `restart-short-memory-probe2`。
- 独立审查确认：共享FABM单列model/root每表达式只有一份history，所有GETM水柱复用；`calculate_derived_input`先`fabm_update_time`，之后`light`才更新当前列PAR；当前传入年内秒跨年回退。

## 实施顺序

1. 先加可编译真实代码回归：两列不同PAR、正反遍历顺序、跨采样边界、bulk/horizontal各自首次初始化语义、续算恢复、跨年单调时间。不要以当前PAR填满缺失24小时历史。
2. GETM adapter枚举 `model%root%first_expression`，为实际bulk/horizontal temporal_mean逐湿格存储完整n+3槽history、last_time、next_save_time、ioldest；bulk还保存valid。其余垂直积分等表达式不纳入记忆状态。
3. 每列恢复表达式状态→链接当前环境/状态→更新light/PAR→采样时间表达式→积分→保存该列。history必须原位复制，保持FABM输出指针。启动时零时间更新不能覆盖恢复的记忆。
4. 统一固定epoch绝对秒或从原始模型起点单调累计秒，不能使用年内秒；同时保存/校验时间基准。
5. 在create/read/write restart中持久化所有记忆字段，带表达式身份和period/n/missing_value一致性检查。初始化方法1/2重置，方法0恢复。旧checkpoint缺记忆时明确拒绝精确续算，不静默伪造历史。
6. 最终源码重编译私有候选；先短窗口真实复现转绿，再生产24小时以上的真实续算（驱动覆盖必须真实延长，不能跳过预检），再全部内置案例。按必要范围增加回归并独立审查。
7. 只在所有必要修复完成后备份/提升默认solver，固定app/solver/verifier版本，使用全新种子从完整第1轮重新开始；六后台阶段与十UI组缺一不可。之后新包、实际安装、六出厂案例及清理。

## 源码入口

- `3DWET/src/getm/src/3d/getm_fabm.F90` 逐(i,j)复制cc_col、start_gotm_fabm、do_gotm_fabm；初始化在getm initialise line264，fields热启动分支line339。
- `3DWET/src/gotm/src/fabm/gotm_fabm.F90` calculate_derived_input line1271/时间更新1322，do_gotm_fabm先derive line1366，light在split循环line1510；start里的零时间derive line1098。
- `3DWET/src/fabm/src/fabm_expressions.F90` 两类temporal_mean公开类型；bulk history rank2、horizontal rank1（GOTM列driver）；bulk valid初始false/ioldest-1。
- `3DWET/src/fabm/src/fabm.F90` fabm_update_time1真实环形缓存算法。
- GETM ncdf create/read/write_restart_ncdf 已依赖getm_fabm，可通过adapter helpers持久化状态；注意数组分配必须先于读取，首次fabm_update_time之前完成恢复。
