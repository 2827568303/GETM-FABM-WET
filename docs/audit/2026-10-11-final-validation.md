# 3DWET Studio 1.3.0 最终验证记录

验收日期：2026-10-11。网页与 Windows 桌面程序使用同一套 QGIS 风格界面和湖盆分层图标。已安装到 `C:\Users\23801\AppData\Local\Programs\3DWET Studio`，桌面保留一个 `3DWET Studio.lnk`；开始菜单保留桌面和浏览器入口。安装器说明依赖并内置科学计算环境、原生运行库和 WebView2 离线安装程序。

## 实际计算与结果验证

六个安装包内置案例均采用交付配置原样运行：2 秒步长、20 分钟模拟、每60秒输出。下面的耗时为这台机器上的计算与运行状态收尾耗时，不含逐变量接口验收；同时执行的验收可能影响耗时。

| 案例 | 实际求解器运行 | 耗时 | 通过的结果检查项 |
| --- | --- | --- | --- |
| Lake Dianchi | 通过 | 26.79 秒 | 810 |
| Lake Luoma | 通过 | 27.75 秒 | 679 |
| NativeTest | 通过 | 3.87 秒 | 399 |
| StudioDemo | 通过 | 7.16 秒 | 866 |
| Theoretical lake | 通过 | 7.22 秒 | 866 |
| _fish_probe | 通过 | 24.69 秒 | 810 |

所有六个案例均检查最终时刻、实际湿格点的数值有限性、三维几何，以及逐变量切片、点/区域/全湖时间序列、分层、剖面、仪表盘等结果接口。水深、层厚均为正，层厚求和与总水深之差低于1毫米容差。原生旧格式三维文件额外检查了空边界层与物理层的索引对应。源目录五个案例也有独立验证记录。

外部合成案例使用固定种子20261010、121个边界顶点、250个水深点、8天气象及两条河流驱动；完成上传、网格、水深插值、构建、15个文件SHA-256导入校验、诊断修复和20分钟实际计算。鱼类及无机碳/甲烷变量均存在。结果接口检查通过812项，共执行869次HTTP请求；10项无有效数据的诊断量列为不适用，2项浏览器交互类别由其他验证覆盖或明确限定。可重复使用的纯输入资料是 `release/ExternalSyntheticLake-inputs.zip`，含完整可导入的 `complete_case`。

编辑与运行功能的13组工作流全部通过：项目另存/导入/删除，点位拖动/CRUD/撤销重做，生态网络和物理参数编辑及冲突保护，故障跳转/修复，生态/鱼类/温室气体切换，时间/热启动/输出配置，河流编辑，真实模型自动率定/参数应用/观测对比，率定停止及模型运行停止。联合验证覆盖 84/86 个界面使用的API方法与路径。

## 修复与展示

- 随机崩溃定位到原生压力梯度计算所用的未初始化下界。Sigma与general垂向坐标初始化已修正并重新编译，连续20次Luoma原生运行通过；不是通过关闭文件锁规避崩溃。
- Theoretical lake原来把1880米绝对高程当作相对水位，已改为相对基准0米，并增加异常水位诊断。
- 结果读取优先使用包含生态变量的主output.nc；保留旧格式独有变量，并修正其空边界层索引。
- 率定排除历史输出，拒绝求解失败、无效数值、缺失/过早停止的结果；界面如实标注SciPy L-BFGS-B。旧PEST/GLUE/贝叶斯配置仅作兼容别名，并返回明确提示，没有实现这些独立算法。
- 湖岸采用真实湿网格边界，湖底采用输入水深，增加分层水体、等深线与可切换计算网格，保持相机视角并使用清晰的科学色标。
- 界面日期统一显示年内儒略日（DOY），例如 `2020-DOY001`；底层模型配置仍使用原生ISO时间。已验证闰年、跨年、UTC、图表与输入转换。

样式参考及截图见 `2026-10-10-lake-visual-references.md` 和 `2026-10-10-lake-luoma-bathymetry.png`。参考QGIS官方三维地图文档与Deltares官方Delft3D资料；没有将示意景观当作真实模型数据。

## 安装、界面与检查

- Python检查201项通过，1项因Windows符号链接创建权限跳过。5组JavaScript检查通过：日期转换、日期界面、缩放控制、湖泊几何及渲染数组。
- 冻结程序自检、WebView2实际界面及安装后界面检查通过；Chart.js、Plotly、Leaflet、桌面桥与本地健康检查均可用，首页无大字横幅。
- 安装后在清除开发Python路径、设置无效PYTHONHOME的隔离环境中，StudioDemo实际完成计算；output.nc含21个时刻、864个变量，数值检查通过。
- 安装升级测试确认旧出厂配置先备份再更新，用户自定义配置保持原样；程序、求解器、术语文件和统一图标的安装后SHA-256与验收文件一致。ICO覆盖16至256像素，并写入Windows可执行程序资源。
- 安装包SHA-256：`0CE7A908AA13F27F5CE01B34488A8E9F4DD67171B6C43DC6C3E6C2953671CDB6`。

这些检查验证短时运行与功能链路，不代表年度模拟稳定性或真实湖泊预测精度。两个操作系统交互接口（文件夹选择器、Explorer打开目录）没有自动点选验收；Ctrl+滚轮的组合按键逻辑有单元验证，但未在真实桌面上自动组合按键。此前已实测三维旋转/缩放、相机保持、图层/图例、全屏及PNG导出；不能据此声称每个界面控件都经过逐一人工验收。

## 证据与清理

`2026-10-11-evidence`保存最终JSON结果及校验和，历史失败尝试另存为historical-attempts.json，避免将旧失败误当最终结论。报告中的build路径是当时的隔离验证位置；大体积模型输出副本在验收后清理。源码、用户原有案例和数据、原配置备份、必要构建工具及原生回滚快照保留。清理路径与实际释放字节详见 `2026-10-11-cleanup.json`。

重放验收时使用新建的隔离目录，例如：

```powershell
.\.venv\Scripts\python.exe scripts/verify_builtin_cases.py --work build/recheck --keep-defaults --model-source "C:/Users/23801/AppData/Local/Programs/3DWET Studio/3DWET" --launcher "C:/Users/23801/AppData/Local/Programs/3DWET Studio/3DWETStudio.exe"
.\.venv\Scripts\python.exe scripts/verify_external_workflow.py --work build/recheck-external --model-source "C:/Users/23801/AppData/Local/Programs/3DWET Studio/3DWET" --launcher "C:/Users/23801/AppData/Local/Programs/3DWET Studio/3DWETStudio.exe"
```
