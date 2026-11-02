# 整版诊断集中修复：时间、完整性与播放镜头

> **For agentic workers:** 使用 executing-plans 在当前会话逐项执行；每项先观察失败再修复。用户已授权继续实施和自主定稿，不再要求选择执行方式。原有大量工作留在当前 codex/unified-studio 工作分支；不重置或另行复制未提交文件。

**Goal:** 修复已实际复现的时间、率定完整性、ABC证据及播放镜头问题，作为同一版本修复批次的一部分；本计划通过不等于五轮验收通过。

**Architecture:** 沿实际求解器时间语义核验输出；后端统一把有时区时间归一为UTC无时区值，保留微秒；前端保留输入小数且不因JS毫秒取整跨秒。三维相机在排队绘制真正开始时读取实时WebGL镜头，并连续记录拖动事件。

**Tech Stack:** Python/pytest/netCDF4/pyabc，JavaScript/node:test，现有Plotly绘图队列和安装版UI。

## 任务1：保留ABC粒子身份

Files: `scripts/verify_calibration_acceptance.py`、`tests/test_abc_acceptance_evidence.py`。

- [x] 红测试已存在：`test_distinct_particles_with_equal_distance_and_weight_are_all_verified`；真实SQLite保存每代4个不同参数、相同距离/权重，旧读取返回1行。
- [ ] 运行 `.venv/Scripts/python.exe -m pytest tests/test_abc_acceptance_evidence.py -q`，确认失败位于`len(extended)`而非模型运行。
- [ ] 将读取改为`stored.get_population_extended(m=0,t=t,tidy=False)`，按`particle_id`分组；对每粒子读取唯一distance及`par_name/par_val`，构建参数元组。确认粒子数、参数名、接受距离、实际trial匹配，保留权重/后验/预算/固定基线所有原检查。
- [ ] 重跑同一文件，所有通过；用attempt19原结果重放证据，另存修复后报告，不改原失败记录。

## 任务2：微秒时间与实际观测配对

Files: `3DWET/app/static/js/model_dates.js`、`3DWET/tests/test_model_dates.js`、`3DWET/app/server.py`、`tests/test_weighted_calibration.py`。

- [ ] 前端加入红断言：
```javascript
assert.equal(D.format('2020-01-01 00:20:00.785733'),'2020-DOY001 00:20:00.785733');
assert.equal(D.format('2024-12-31T23:59:59.999999Z'),'2024-DOY366 23:59:59.999999');
assert.equal(D.toIso('2025-DOY001 00:00:00.000001+01:00'),'2024-12-31 23:00:00.000001');
assert.equal(D.formatText('时刻 2020-01-01 00:20:00.785733'),'时刻 2020-DOY001 00:20:00.785733');
```
- [ ] 运行 `node 3DWET/tests/test_model_dates.js`，观察首条微秒断言失败。
- [ ] 时间正则接受1..6位小数；`date.setUTCHours(hour,minute,second,0)`后仅设置小数的前三位毫秒，完整小数单独保留，不使用四舍五入使时间跨秒。字符串替换需消费整个微秒时刻。
- [ ] 后端加入7个实际微秒时刻的零容差配对测试及UTC/正负偏移、无效日期测试：`pairs,_=server._pair_obs_sim(obs,sim,max_lag_hours=0); assert len(pairs)==7`；运行pytest观察旧解析返回零对。
- [ ] `_parse_iso_time`优先`datetime.fromisoformat`，接受Z、微秒与偏移；有时区`astimezone(timezone.utc).replace(tzinfo=None)`；原DOY/斜线/数字兼容路径保留，所有返回值统一UTC。不得丢深度或放宽lag替代时间修复。
- [ ] 前后端日期与配对相关测试全部通过。

## 任务3：严格复刻原生输出计划

Files: `3DWET/app/output_schedule.py`、`3DWET/app/calibration.py`、`tests/test_output_schedule.py`、`tests/test_calibration_integrity.py`。

- [x] 已定位GETM `src/futils/time.F90` 的`MaxN=nint(nsecs/timestep)`；Flexout `in_window`用整数secondsofday，微秒在窗口判断中不参与比较；native输出时间仍保留微秒。
- [x] 红测试已存在：dt1.9060091、630步、60秒周期，完整终帧为1200.785733秒，而旧计划返回1141.699451秒。
- [ ] 新增dt3.1/1200秒窗口测试，GETM最终387步为1199.7秒，必须只期望前一60秒计划；新增显式time_stop在小数步长中只允许整数秒窗口内输出的测试；运行观察失败。
- [ ] 根据原生NINT正数取整计算真实末步：`last_step=math.floor(duration/timestep+0.5)`；输出窗口以原生整数秒判断，允许终帧小于stop+1秒且不超过真实last_step。不以“有文件”、固定放宽误差或任意ceil(stop/dt)替代。
- [ ] `_validate_trial_output`由最终nc时间的年月日时分秒微秒构造datetime，保存`final_time`和`scheduled_final_time`；错误消息同时列实际和预期计划终帧。有限值、文件新鲜度、solver完成、坏变量及早停检查全部保留。
- [ ] 运行 `.venv/Scripts/python.exe -m pytest tests/test_output_schedule.py tests/test_calibration_integrity.py -q`，全部通过；对保留真实目录`3dwet_calib_v3l7kjgd`重放健康检查，保存报告。

## 任务4：播放期间实时相机

Files: `3DWET/app/static/js/viz3d.js`、`3DWET/tests/test_viz_camera_axes.js`及现有draw/resize/playback测试。

- [x] 红测试`a camera moved while the next output frame loads is retained by the actual draw`实际失败，证明取数开始时保存的镜头覆盖后续鼠标移动。
- [ ] 查看`viz3dPlot`排队任务内部，在Plotly.react前立即读取现有`scene._scene.getCamera()`，不要用取数开始缓存覆盖它；首次绘制和新案例重置仍按明确逻辑执行。
- [ ] `plotly_relayouting`与最终`plotly_relayout`共用相机记录函数；事件更新相机状态和轴可见性，无相机事件不改镜头；保留绘制/resize串行队列。
- [ ] 新增正在拖动事件、排队绘制期间视角变化、平移/缩放与新案例重置测试，先失败再修复。
- [ ] 运行 `node --test 3DWET/tests/test_viz_camera_axes.js`及已有camera/queue/playback脚本，全部通过；后续统一安装版真实鼠标验证，不只用单测宣称修复。

## 后续批次与验收依赖

本计划之后继续同一集中修复版本：真实垂向深度及图表主题；五组层级导航、独立水质/生态配置；可组装真实WET实例；连续水体、正交网格和陆地；Lake Ravn真实观测文件夹。各子系统写单独实施计划再实现。保留顶部工具、真实单位与数据。

最终统一构建/更新桌面、核对六个内置案例、真实UI各功能组和桌面通知。源码/求解器/资源指纹固定后才启动五套新数据的连续完整验收，任一失败清零。当前0/5。
