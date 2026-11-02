# 三维湖盆表现：参考与验证

本次范围仅为 `viz3d.js` 的科学三维表现、`studio.css` 中三维画布的局部样式和相关测试。保留已确认的 QGIS 工作台布局、案例数据、模型计算与 API。

## 官方参考

- [QGIS 4.2 三维地图视图](https://docs.qgis.org/4.2/en/docs/user_manual/map_views/3d_map_view.html)：参考基于高程数据的地形、明确的垂向比例、材质光照、轨道导航与全图复位。实际查看了官方 [三维地图截图](https://docs.qgis.org/4.2/en/_images/3dmapview.png)，取其清楚的地形层次与中性工作台画布。
- [Deltares Delft3D Flexible Mesh 官方简介](https://cms.deltares.nl/assets/common/downloads/Brochure-Delft3D-Flexible-Mesh-Suite.pdf)：参考水动力建模中几何、网格和结果的分层表达。网页工具读取了 PDF 内容；其截图工具及内置浏览器未能稳定打开 PDF 画面，因此不宣称逐图复刻。
- [D-Flow FM 官方用户手册](https://content.oss.deltares.nl/delft3d/D-Flow_FM_User_Manual.pdf)：本次在线读取失败，未将未读取的细节当作实现依据。

## 实现与科学边界

1. 以原有正水深湿网格生成湖底、水面和边界剖面；岸线明确标为“湿网格边界”。保留岛屿、干格与不连通水域，不绘制虚构陆地、山体、植被或波浪。
2. 等深线与已显示湖底的每一个三角形求交；不跨越干格连接线段。自动采用易读的深度间隔，悬浮读数仍为真实水深。
3. “计算网格”沿实际单元边缘显示，并在密网格中抽稀线条。默认关闭，可通过图例启用；湖盆、水面、岸线和等深线也可在图例切换。
4. 水深使用浅至深的连续蓝绿色带，科学变量使用 Viridis；水深色标从 0 到输入水深最大值，垂向放大不改变深度标签。湖底采用克制的漫反射材质，淡透明水面用于提示零深度平面。仅显示水深时，图标题也改为湖盆地形。Plotly 自带浅色背景，导出的 PNG 不依赖网页 CSS。
5. 为避免共面的 WebGL 线条与三角面闪烁，只有显示的等深线/网格线向上偏移最大水深的 0.2%（乘同一垂向比例）；湖底几何、求交计算、科学数据与标签不变。该偏移不用于模型或分析。
6. 刷新前保存实时相机；保留旋转和滚轮缩放。所附 Plotly 2.35.2 的滚轮事件可能返回旧布局相机，因此优先读取其已存在的实时场景相机，保留公开事件及布局回退。

## 验证

- `node 3DWET/tests/test_viz_geometry.js`：湿格、岛屿、断开水域、坐标有效性、sigma 层心、垂向比例、等深线高程、网格边缘。
- `node 3DWET/tests/test_viz_render.js`：变量掩膜、空数据、真实水深标签、色标范围、图层默认状态、滚轮配置、相机保存及实时相机优先级。
- `node --check 3DWET/app/static/js/viz3d.js`。
- `.venv/Scripts/python.exe -m pytest 3DWET/tests/test_ui_theme.py -q`：3 项通过。
- 网页核查使用独立端口 8788，`WET_MODEL_ROOT` 指向 `build/verify-all-builtin-cases-20261009-2/3DWET` 隔离副本，未通过浏览器写入源案例。实际检查骆马湖水深与温度覆盖、图层图例、全屏、轨道旋转、滚轮缩放、刷新后相机保留和图形复位。
- 实际点击 Plotly “Download plot as a png” 并获得 PNG 文件，已复制为 [`2026-10-10-lake-luoma-bathymetry.png`](2026-10-10-lake-luoma-bathymetry.png) 并打开核查图例、标题和浅色背景。当前三维页面没有科学结果 CSV 导出按钮；另实际点击了“输入数据 → 下载 CSV 模板”，获得 `meteo_template.csv`，这是气象输入模板，不能等同于结果导出。
- 控制工具不能组合按住 Ctrl 与滚轮，因此 Ctrl+滚轮仅由现有视图控件测试覆盖，未宣称完成该组合的浏览器人工核查。
