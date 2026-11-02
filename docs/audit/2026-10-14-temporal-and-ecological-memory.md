# 逐水柱记忆、原生诊断与重启验证

本记录补充 `2026-10-14-current-column-diagnostics.md` 的早期诊断；早期失败报告保留，不计入完整五轮。

## 修复范围

- GETM 逐水柱恢复/保存 FABM temporal_mean 的完整环形历史、采样时钟与有效标志；使用 Julian-day 秒，FABM 时间单位设为一秒，恢复生产 86400 秒窗口。
- 当前 PAR 在采样前更新；时间推进仅在物理步首个拆分阶段进行，启动派生输入不额外推进历史。
- checkpoint schema 2 校验表达式身份、窗口、形状、时钟、环形索引、有限值及 NetCDF 填充值；Python 热启动入口先校验后修改案例。表达式缺失值元数据使用 expression_missing_value，避免将合法零历史标记为 CF missing_value。
- 植被消光从当前水柱状态计算；yeartrans 每次调用重置。萌发日期是明确标记的 column_memory 诊断，逐列保存及重启恢复；合法未萌发代码 -1 与缺失值 -2e20 分离。
- OM 转移量使用 bottom 生产阶段；FABM 显式垂向移动调用保存相应生产诊断。重编译所有启用的 WET 源文件并显式链接，避免旧 archive 的同名对象覆盖。
- 三个内置配置的带引号逻辑值通过现有体检修复函数更正，原文件保存在 builtin-logical-source-backup-20261014-02。

## 当前候选与证据

候选：`build/native-ecological-memory-final/getm_cartesian.exe`，SHA256 `98f359433fb6646f5d597d24fe5234b43c1246cb3a9ef8f606bf2e69c5e63aaf`。

- `build/restart-ecological-memory-final-crossyear/verification.json`：实际原生 28 小时跨年运行、25 小时检查点后续跑 3 小时。9 项状态、20 项 temporal_mean 字段及植被记忆共 30 项，最大绝对误差全部为 0；生产窗口保持 86400/3600 秒。
- `build/vegetation-column-onset-memory-clock-check/verification.json`：不同水柱生成萌发日期 110/120，冷启动和续跑均成功，检查点时钟推进至 1200 秒；萌发日期最大误差 0，根比例分别约 0.1821785/0.5943849。验证脚本已补两次 passed/status 及检查点日期、秒数断言。
- Python 全套：405 passed、3 skipped，39.74 秒；跳过项为 Windows 符号链接权限。
- 独立只读审查未发现原生记忆实现新增明确缺陷；指出的验证脚本成功/时钟断言缺口已修复并实际重跑通过。

## 证据边界

中间的错误时间单位、旧消光缓存以及未补全诊断候选各有失败报告，均不覆盖、不计数。以上为机制与独立功能验证，不能代替五次不同数据的完整工作流，也不证明实测生态预测精度。完整五轮仍为 0/5；内置案例最终整体验证、UI 全功能、安装版验收尚待完成。
