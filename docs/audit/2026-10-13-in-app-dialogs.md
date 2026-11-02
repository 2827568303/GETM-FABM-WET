# 应用内确认窗口与新数据界面实测

日期：2026-10-13。**完整连续计数仍为 0/5。** 本次为功能修复和独立实测，未把第四次后台通过等同于完整轮次。

## 第四次后台与版本状态

种子 2026101302 生成新的湖岸、面测深、气象及入出流数据，六个后台阶段 external、features、results、scipy、abc、restart 全部通过。[实际记录](../../build/full-workflow-20261013-attempt04/round.json)。其中续算已包含鱼类越界修复候选。

实际界面测试发现原生确认框阻塞后实施前端修复；源码版本发生变化，驱动器最终将整轮记录为 `failed`，错误为 `Source changed during round`。该结果保留在[账本](five-workflows/ledger.json)，不计成功轮数。后续完整轮次必须使用新种子和固定版本。

## 确认框修复

点击一键构建时，浏览器原生 `confirm` 暂停页面，验收浏览器的对话框接口未返回可操作对象；同源页面脚本也被暂停。关闭该临时标签后其他同源页面恢复响应。没有通过删除确认步骤绕过覆盖提醒。

新增应用内异步确认/输入窗口，沿用工作台现有样式。构建、模块开关、参数恢复、河流操作、网格放弃修改、结果清理和案例名称输入均使用它。保留原确认文字、取消行为和名称核验；消息用 textContent 呈现，支持 Escape、输入框 Enter、焦点循环、返回原控件以及拒绝第二个并发请求。

- 新确认组件测试先因缺失失败，再验证等待决策、取消、确认、文本输入、纯文本消息、焦点恢复与并发保护。
- 构建流程测试先因未等待应用内确认失败；修复后验证确认之前不调用写接口、取消零写入、确认只构建一次。
- 实际页面显示[构建确认窗口](five-workflows/attempt04-ui/build-confirm.png)。点击取消后案例内 **15 个文件的 SHA-256 均未改变**：[哈希证据](five-workflows/attempt04-ui/cancel-unchanged.json)。再次点击确认后显示构建成功，[页面记录](five-workflows/attempt04-ui/build-success.txt)。该操作不再阻塞页面。

## 同一新数据的真实界面操作

在独立模型目录新建 `Round4 UI Lake 1302`，没有修改后台验收使用的 `Imported Random Lake` 输入。

1. 上传 boundary 四组件、depth_polygons 四组件；识别 121 个边界顶点、5 个测深面和 3–7m 深度。
2. 50m 网格生成 19×14、165 水格；插值平均水深 5.08m，保存后公共加载状态显示完整路径和正确案例名。[前处理记录](five-workflows/attempt04-ui/preprocess.txt)。
3. 逐个导入该种子的 meteo、inflow、outflow CSV 并生成文件；河流点位与后台一致：SEED_IN (11,6)、SEED_OUT (4,9)。
4. 使用年内日输入 2020-DOY001 00:00:00–00:20:00，2 秒、6 层；实际点击确认构建，未用后台调用代替这次构建按钮操作。
5. 体检定位按钮确实将焦点移到 `domain.check_cfl`，随后一键启用并提示原文件已备份。[焦点证据](five-workflows/attempt04-ui/diagnostic-location.txt)。
6. 从页面启动原生求解，显示 **600/600、已完成、耗时约 7 秒**，结果归档位置明确列出。[终点页面记录](five-workflows/attempt04-ui/run-completed.txt)。
7. 在该生成案例的 output 内建立一个与原 3D 文件 SHA-256 相同的测试副本。实际刷新、扫描识别一组重复、快捷选中并[确认清理](five-workflows/attempt04-ui/cleanup-confirm.png)。仅副本移入可恢复回收区，原结果及九项输入/配置均仍存在：[文件检查](five-workflows/attempt04-ui/cleanup-files.json)。
8. 实际点击“恢复最近一次清理”，恢复文件与原结果 SHA-256 完全相同：[恢复检查](five-workflows/attempt04-ui/restore-files.json)。没有执行永久清空回收区。

以上只是已经实测的范围。参数/初值全部组合、生态网络与点位编辑、所有图形交互/导出、完整率定界面、语言包持久化、通知和最终安装版仍需逐项完成；该案例不作为完整成功轮次。

## 本次回归

- Python：`.venv/Scripts/python.exe -m pytest 3DWET/tests tests -q -ra`，**344 passed、3 skipped，37.91 秒，退出码 0**。跳过仍涉及 Windows 符号链接权限。
- 前端：**27 组全部退出码 0**。[逐组记录](five-workflows/attempt04-ui/javascript-after-dialogs.json)。旧日期/参数测试仅将同步确认桩改为异步确认桩，原断言保留。

先完成剩余独立功能实测并关闭发现的问题，再固定版本从新数据开始连续五轮；不将修复复测、六个阶段或多个内置案例凑成五轮。
