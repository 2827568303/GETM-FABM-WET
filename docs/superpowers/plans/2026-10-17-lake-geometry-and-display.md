# 真实垂向几何与可选网格显示实施计划

> 当前会话按 executing-plans 逐项执行。用户已批准科学工作台并委托成熟模型定稿，不再要求选择布局。每项先观察失败，再实现和回归；最终桌面版本及五轮要求不缩减。

**Goal:** 使水体位置依据实际结果几何，并提供可选择的显示网格和有据可查的岸边陆地。

**Architecture:** Python单独读取一时刻、对应采样网格的hn/zc/z几何，主图、关联剖面及后续垂向热图共用相同语义。纯JavaScript几何函数管理水体/陆地/显示线条；现有renderer的令牌、绘制队列和实时相机保留。显示模式不能修改求解网格或原始状态。

**Tech Stack:** 现有NetCDF4/NumPy、原生JavaScript、Plotly、pytest/node:test、真实本地浏览器。

## 任务1：输出的真实垂向几何

Files: create `3DWET/app/vertical_geometry.py`、`tests/test_vertical_geometry.py`；modify `3DWET/app/server.py`、`tests/test_3d_surface_geometry.py`。

- [x] 测试同一湖底10米、两层hn=[3,9]、实际水位2米：中心深度[10.5,4.5]、层界面深度[12,9,0]、中心高程[-8.5,-2.5]；第二时刻不同hn不得复用首帧。明确原层序从底到面。
- [x] 添加原生padding去除、实际zc读取、不同采样步长/选层、干格和坏hn整列屏蔽检查。hn存在却坏值时不得退回sigma伪造有效几何。接口型变量匹配层界面，不能当层中心。
- [x] 函数 `read_vertical_geometry(ds,var,time,bottom,ys=slice(None),xs=slice(None))` 返回 `center_depth/center_elevation/depth_edges/surface_elevation/valid/source/position`。从hn独立物理层起点读取；相对水面深度由自顶向下累加，床面高程=-bathymetry，实际zc在网格/时间/层数一致时采用，并检查其位于对应层界面内。无hn时只接受显式sigma，结合当前z/D或明确标记静态bathymetry；无真实几何返回明确错误。
- [x] volume API同时下发与data完全对应的采样深度、高程、水位、湿格和来源；不由目标层采样丢掉hn的全层厚。JSON只输出有限数或null。
- [x] 运行 `.venv/Scripts/python.exe -m pytest tests/test_vertical_geometry.py tests/test_3d_surface_geometry.py tests/test_result_layers.py -q`。真实grid-25结果逐点对照native zc/hn与API。

## 任务2：主图与剖面使用相同几何

Files: modify `viz3d.js`、`spatial_sections.py`；tests `test_viz_geometry.js`、`test_viz_metadata.js`、`3DWET/tests/test_spatial_sections.py`。

- [x] 红测试使同一sigma、不同hn的两列得到不同真实z；分层/点云/等值面都使用返回几何，不读取旧帧。图内注明深度基准；静态sigma回退不能称为实际hn。
- [x] 主图使用负的正向下水面深度；hover独立保留实际层中心深度及模型高程。空间剖面共用Python读取器，保留横坐标、原始层序与干格间断，不让主相机影响剖面视角。
- [x] 运行相关Node及Python几何/剖面回归，再用实际hn/zc结果核对两种视图与导出。

任务1–2证据（源码专项，不计整版轮次）：全Python536 passed/3 skipped；60个Node脚本首次全过，静态预览基准回归追加后相关25项再次通过；需求及质量独立审查通过。`vertical-native-review.json`核对25米原生三帧，每帧624/624湿列有效；`vertical-live-http-review.json`通过59124实时API核对12.5米首/中/末帧，原生标量、高程、深度及XZ剖面最大误差均0，输入/输出哈希前后一致。实际UI三种体视图均ready，末帧PNG保留真实坐标、深度轴、hn+zc、色标与剖面位置；`geometry-native-last-frame-export-20261017.png`。静态预览轴标明静态水面。另发现静态预览返回结果会丢当前帧，交任务3一起修复；整版及显示网格/陆地尚未通过。

原生分步更新时间细节：hn+zc几何以`sum(hn)-H`为三维状态水面；二维z可能已前进一个微步，差异单独返回，不因时间错位屏蔽正常三维列。首帧两个河流格的约0.000204米差异由原生积分顺序确认，没有放宽物理有效性规则。

## 任务3：显示网格与陆地

Files: modify `viz3d.js`、`app.js`、`index.html`、`scientific_workspace.js`、`static/i18n/en.json`；create `3DWET/tests/test_lake_display_mesh.js`。

- [ ] 用岛屿、对角湿格、单格窄通道写红测试：三角面仅来自真实湿格，不跨干格；正交线保留原格边；选择不改变标量、坐标、层序和求解器拓扑。密度和透明度独立控制线条。
- [ ] 控件提供连续水体/原正交线/三角面片/隐藏网格，切换通过现有队列刷新并保留相机、播放区间和颜色。原计算网格若被采样，明确为采样显示；不伪称原始完整网格。
- [ ] 有明确DEM单位/坐标时用真实陆地高程；未提供时用由真实干格得到的中性平面，标注高程未提供。水体和变量高度表面均有邻接陆地，但后者继续明确其z是变量值而非真实水面。
- [ ] 对缺测湿格用已选nanColor的独立材料；不把缺测当干格，也不让缺测色污染定量色标。连续几何中所有插值明确为显示插值，不修改原数据；保留原始单元值/位置供hover核对。
- [ ] 实际UI分别检查四种显示、线条透明度/密度、岸线岛屿、缺测材料、播放时换模式和鼠标相机保持，二维/三维/关联剖面色标一致，真实PNG全屏与窄屏。

## 任务4：新建网格建议与统一验收

- [ ] 新建小湖25米起点与可编辑分辨率一起落地；先估算网格总量和基于水深的CFL建议，大湖不盲目应用小湖值，用户显式输入不自动覆盖。对比证据为 `docs/audit/2026-10-17-grid-resolution-decision.md`。
- [ ] 完整前后端回归和独立审查；修正本批所有已知问题后统一冻结/安装。原生桌面、生态多实例、Ravn实测率定及所有功能仍由整版清单追踪。
- [ ] 最终安装版固定指纹后，用五套不同新数据各自完整从上传到模型/率定/导出及所有UI功能连续通过。任一失败归零；本计划专项不计正式轮次，当前0/5。
