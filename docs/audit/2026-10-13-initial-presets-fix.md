# 初始条件预设与保存修复

日期：2026-10-13。**连续完整验收仍为 0/5**；这是先修复独立功能的专项验证，未开始新的完整轮次。

## 根因与修改

实际界面将营养状态预设的 `label` 文本当成 number 输入，浏览器把它显示为空，保存时触发“初始条件 label 必须填写有限数值”。已有初值测试没有真实调用额外预设字段的生成，未覆盖这个组合。

进一步核对发现带模块名称的 `DOM_sDW`、`POM_sDW` 等预设未映射到实际模块输入，生成了重复额外字段，且原“套用预设”取错输入标识。不同有机物实例的 `sDW` 不能只按裸变量名回填。

- 预设映射增加模块名加下划线/点号的精确键；只有唯一的裸变量名才映射，避免别名指向第一个实例。
- 额外字段排除非数值元数据、非有限值与已映射的模块别名；`macro_sD` 仍使用专用沉水植物控件。
- 显式“按当前营养状态回填”按精确映射更新，并标记为当前预设值；选择性套用/营养状态切换保护用户修改，更新未修改的预设值。
- 回填后同步草稿，过滤或重新渲染不恢复旧值。静态脚本缓存版本更新为 v30。

新增 `test_initial_presets.js` 执行真实渲染/保存/回填函数，含具有 `label` 和重复变量名的预设。测试在修改实现前首先稳定失败于“preset label must never become a numeric water-quality field”，修复后通过。测试 DOM 桩按浏览器行为将非法 number 值置空，`getElementById` 缺失返回 null。

## 实际页面验证

模型目录为 `build/full-workflow-20261013-attempt04/external/3DWET`，案例 `Round4 UI Lake 1302`，该案例来源于此前生成的种子 2026101302。此处复用失败场景诊断，不计为新数据完整轮次。

1. 修复前失败证据：[DOM](five-workflows/attempt04-ui/initial-save-label-failure.txt)、[截图](five-workflows/attempt04-ui/initial-save-label-failure.png)。
2. 修复后实际页面额外 `icv-new-*` 字段数量为 **0**。从页面输入水温 16.25、O2 8.5、NH4 0.03、NO3 0.3、PO4 0.015、DOM.sDW 6.125、POM.sDW 7.25；点击保存，提示 **112 项水质初值已保存**。[成功页面](five-workflows/attempt04-ui/initial-save-after-fix.txt)。
3. 实际点击“重新读取”，以上七个值全部一致；独立读取 `fabm.yaml` 验证 DOM/POM/O2 等值。[重读页面](five-workflows/attempt04-ui/initial-reloaded-after-fix.txt)、[YAML 核对](five-workflows/attempt04-ui/initial-saved-yaml.json)。
4. 页面体检允许运行，实际点击启动，原生模型完成 **600/600 步，约 8 秒**。[终点页面](five-workflows/attempt04-ui/initial-run-after-fix.txt)、[截图](five-workflows/attempt04-ui/initial-run-after-fix.png)。
5. 三类输出各 **20 帧**。第一帧是模拟 60 秒后的状态，水温 16.244959–16.250219、DOM.sDW 6.124961–6.125000、POM.sDW 7.246985–7.252956、O2 8.499907–8.500570，与新初值经积分后的结果相符；不是声称该帧等于零时刻。[实际输出与完整运行状态](five-workflows/attempt04-ui/initial-native-output.json)。
6. 再从页面显式回填富营养值：DOM=10、POM=5、O2=10，humus.sDS=3719 保持不变。手动将 DOM 改为 6.375，选择中营养后 DOM 仍为 6.375，POM=2、O2=8。[预设切换页面](five-workflows/attempt04-ui/initial-preset-switch.txt)。此组测试草稿未保存，最后重新读取已保存初值。

## 回归和剩余工作

- Python 全部现有回归：**344 passed、3 skipped，35.19 秒，退出码 0**；跳过仍是 Windows 符号链接权限。
- 前端 **28 组，0 失败**。[逐组输出](five-workflows/attempt04-ui/javascript-after-presets.json)。
- 未修改正式安装包或默认求解器。语言单语言显示偏差、其他独立界面操作、新数据固定版本连续五轮、最终安装包同版验收仍未完成。

本次关闭的是已复现的 label 保存阻断与现有模块预设映射链路，不宣称所有初值数据、未声明模块、任意变量新增、长期科研模拟或全部开发目标已验收。
