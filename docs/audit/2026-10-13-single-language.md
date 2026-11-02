# 单语言科学说明与语言包实测

> 后续：[结果请求乱序与变量选择修复](2026-10-13-result-request-order.md)。下文记录的异步选择重置已有源码修复、确定性乱序回归和实际快速切换验证；首次加载性能仍待优化。

日期：2026-10-13。连续完整验收 **0/5**，本次是独立功能修复；未把此前案例复测计作新的完整轮次。

## 本次修改及测试

`scientificText()` 原先将所选语言、中文、英文拼接，即使用户选择英文仍显示中文。本次按最新用户要求改为只返回所选语言；中文元数据缺失时保留可用原文，导入语言缺词条时使用英文词典或已有英文元数据，仍未知的内容保留原文。变量代码、单位、路径、输入值不参与翻译。

先将科学说明回归改为用户要求的单语言断言，测试在修改实现前失败：实际“水温 / Water temperature”，期望“水温”。修复后通过。旧图表/初值/仪表盘测试的双语断言已按当前需求调整，保留切换、源元数据、既有图表重绘等覆盖；3D 测试增加不得附带另一种语言名称的否定断言。旧双语图表字符串的切换兼容测试仍保留。

实际页面发现“表层、底层、均值、形状”以及三类营养状态名称缺词条，新增对应回归先失败，再补充英文词典。`i18n.js` 缓存版本更新为 v3，语言包使用说明同步改为单语言显示。

## 实际页面与重启验证

测试使用独立模型目录 `build/full-workflow-20261013-attempt04/external/3DWET`；没有改变用户另一个端口上的工作案例。对已有随机湖案例的结果做语言专项，不计完整五轮。

1. 从内置独立语言窗口选择 English 并应用。仪表盘变量名称不再附带中文；初值页面显示英文分类、模块含义和变量说明。[仪表盘](five-workflows/attempt04-ui/language-en-dashboard.txt)、[初值](five-workflows/attempt04-ui/language-en-initial.txt)。
2. 实际点击“Choose language pack file”，选择本地 [法语测试包](five-workflows/attempt04-ui/language-fr-test.json)，导入后出现新选项、法语预览，点击 Apply 启用。
3. 二维水温变量卡、选择项和色标显示 `Température de l’eau`，变量代码 `temp` 和单位保持原样；缺少的说明使用英文。[当时页面](five-workflows/attempt04-ui/language-fr-2d.txt)。该截图时点尚有表层/均值等漏译，随后已补词典，不能将其当作最终全界面通过截图。
4. 确认模型空闲后重启本任务服务，并从 **62575 换到 62576**。新来源地址没有旧端口的 localStorage；页面仍显示法语仪表盘名称，独立窗口仍选中已导入法语包，证明服务端保存有效。[重启新端口证据](five-workflows/attempt04-ui/language-restart-new-port.txt)、[截图](five-workflows/attempt04-ui/language-restart-new-port.png)。
5. 同一水温数据切回中文再英文，最终英文状态为 `Variable: Water temperature (temp) | Time step: 0 (2020-DOY001) | Mean: 16.2468 | Shape: 14×19`，表层/底层显示 Surface/Bottom。代码、时步和数值不因翻译改变。[中文页面](five-workflows/attempt04-ui/language-zh-2d-after-fix.txt)、[英文页面](five-workflows/attempt04-ui/language-en-2d-after-fix.txt)、[英文截图](five-workflows/attempt04-ui/language-en-2d-after-fix.png)。
6. 服务端文件确认含所选语言和法语包。[重启后偏好快照](five-workflows/attempt04-ui/language-preferences-after-restart.json)。测试服务最后保留 English，不改正式工作目录的语言偏好。

## 本轮回归

- Python 全部现有测试：**344 passed、3 skipped，37.18 秒，退出码 0**。跳过仍涉及 Windows 符号链接权限。
- 前端 **28 组全部退出码 0**。[逐组记录](five-workflows/attempt04-ui/javascript-single-language.json)。
- 3D 标题/悬浮说明与已有图表切换有真实函数回归；本次未穷尽全部 3D 视图实际操作或桌面安装版。

## 剩余事项

单语言拼接偏差已在共享科学说明函数修复，但不等于所有页面已经完全本地化。实际检查还看到初值页的动态地形说明、仪表盘帧数提示等未入词典的内容，应继续改为可翻译模板并验证；用户输入、配置原始注释与求解器日志另按原文保留规则处理。参考卡的其他语言细节和全部页面也需继续核查。

案例刚加载后，后台模型信息仍可能刷新变量选择为默认水深；本次等待实际变量及结果加载后完成同一水温切换。应继续检查异步加载时保留用户选择，不能把异步未完成时的默认水深图误归为已验证水温图。

正式安装包、默认求解器统一、全部功能真实交互、新数据固定版本连续五轮和最终清理仍未完成，目标保持进行中。
