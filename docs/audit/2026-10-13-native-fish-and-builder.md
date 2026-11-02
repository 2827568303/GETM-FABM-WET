> 后续更新见 [应用内确认窗口与新数据实测](2026-10-13-in-app-dialogs.md)：第四次六后台阶段全部通过，但界面修复导致版本改变，整轮已记失败；完整连续计数仍为 0/5。

# 鱼类越界与一键构建修复

日期：2026-10-13。完整连续验收仍为 **0/5**。本次关闭三个已复现问题，不能把专项验证当成完整五轮，也尚未更新正式安装包或替换默认求解器。

## 1. 生态状态随机损坏

此前外部面测深数据（种子 2026101207）分段续算与连续模拟的生态变量最大差为 1999。逐阶段探测进一步发现：第一段冷启动的检查点已经损坏，因此不能仅归因为重启文件读写。

零步重启时 fabm_pel 与检查点一致；重复冷/热运行表现不确定。单独重新编译 GOTM 驱动并不能稳定消除差异，未作为修复采纳。诊断构建在 FABM 自定义状态检查的 `PiscFish` 调用处捕获到碱度被改写；随后只为真实 fish 模块启用 Fortran 边界检查，稳定得到：

```text
fish.F90:1212
Index '-1' of dimension 2 of array 'environment%prefetch' below lower bound of 1
```

根因：`qStage=0` 时未注册 `sFRes`，但 `check_state` 仍读取它，并在 `qTrans>1` 时写回；未注册 ID 的索引为 -1，越界可破坏其他生态状态。此外 `diagnostics=false` 时未注册四项繁殖诊断，原代码仍向 scratch 写入它们；修复第一处后边界检查在这第二处再次失败。

修复仅按注册条件访问这些可选变量，保留有效状态边界检查、鱼类过程、合法诊断和分龄逻辑。未用关闭状态修复、扩大容差或过滤湿水域差异的方法消除失败。

新增原生回归实际编译执行 `fish%check_state`，覆盖分龄 0–3、输运 0–3、诊断开/关共 **32 组合**，验证其他状态与 scratch 哨兵不被修改。使用历史原代码编译同一测试时稳定越界失败；修复后通过。[原代码失败记录](../../build/fish-regression-red/verification.json)。该测试不替代繁殖季节或年度科学验证。

候选构建脚本现在将修改后的 fish 源码编译进私有 FABM 库，不再仅链接历史 archive；支持指定隔离输出目录，保留默认求解器。候选 SHA-256：`4dff1d27b7044a1925545f84384093c8982958de704e7a2654ed640b35aceb09`。

- 原失败案例的边界检查构建复测：九组最终状态全部一致。[报告](../../build/restart-fish-bounds-green-1207-02/verification.json)。
- 优化发布候选再次复测：九组最大绝对差均为 **0**。[报告](../../build/restart-fish-release-20261013-1207/verification.json)。
- 此候选五源码内置案例逐个求解和结果专项均通过：Lake Dianchi、Lake Luoma、NativeTest、Theoretical lake、_fish_probe。[报告](../../build/builtin-fish-fix-20261013-01/verification.json)。这不是最终安装包六案例验收；StudioDemo 仍待最终同版检查。

## 2. 构建配置的逻辑值引号

实际网页载入随机外部案例 `UI Random Lake 1208`、体检显示可以运行，求解器却在读取 getm.inp 时退出：`Cannot match namelist object name '.false.'`。生成器将 35 个逻辑常量写成字符串，如 `dryrun = '.false.'`。

新增真实 Fortran namelist 读取测试先稳定失败，再修复生成器输出裸逻辑值。旧配置体检现在报告阻断问题，可跳转到物理配置，并提供带备份的一键修复；只移除已知逻辑字段的引号，不修改真假值、注释或标题字符串。启动接口也会预先拒绝这类旧配置。

实际浏览器已显示错误、执行一键修复并重新检查解除该阻断。[诊断截图](2026-10-13-native-fish-and-builder/quoted-logicals-detected.png)。之前外部流程在构建后保存初始条件，该操作重写 namelist，间接掩盖了生成器错误；本次增加直接验证构建原始输出的证据。

## 3. 短时模拟没有输出记录

解除逻辑值问题后，实际网页模型计算到 600 步终点，但健康检查正确拒绝成功：三类输出的 time 均为 0。原生成器使用每日 Flexout 输出和固定 8640 步的旧输出间隔，20 分钟模拟没有可用帧。[失败记录](2026-10-13-native-fish-and-builder/empty-output-before-fix.json)。

生成器现在按实际模拟时长和步长生成间隔：短时约 20 帧，长时帧间隔不超过一天；Flexout 和旧 2D/3D 输出采用同一间隔。20 分钟、2 秒步长现在输出每 60 秒一帧。

实际调用构建接口后直接启动原生模型，**没有再保存初始条件或输出设置**；模型正常完成，getm.inp/output.yaml 在运行前后的 SHA-256 不变，三类输出各有 **20 个时间记录**。[构建与运行证据](2026-10-13-native-fish-and-builder/builder-default-native.json)、[记录数](2026-10-13-native-fish-and-builder/output-after-fix.json)。浏览器随后实际载入结果、选择水温和终点帧。此项原始构建默认值由 API/原生运行验证；构建按钮的原生确认框曾使验收浏览器控制超时，该确认操作未记为 UI 通过。

## 回归与后续验收

- 最新完整 Python：**344 passed、3 skipped，37.53 秒，退出码 0**。[终端结果摘要](2026-10-13-native-fish-and-builder/python-summary.txt)。跳过仍涉及 Windows 符号链接权限。
- 前端：**25 组退出码均为 0**。[逐组输出](2026-10-13-native-fish-and-builder/javascript.json)。
- 第三次完整尝试（2026101301）外部阶段通过，但期间修复生成器和诊断，驱动器按源码版本改变自动记录 failed。没有计入连续成功。
- 第四次完整尝试正在用新种子 **2026101302**、面测深数据和修复候选运行。须全部后台阶段及十项真实 UI 检查通过后才能计为一轮。实际状态以[账本](five-workflows/ledger.json)和对应 round.json 为准。
- 仍需完成连续五轮、全部界面/语言/导出/清理操作、最终安装包和六出厂案例的同版验证。所有临时诊断构建保留到必要证据归档后再清理。

