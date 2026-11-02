# 二维、三维共用可编辑色标实施计划

> **For agentic workers:** 使用 executing-plans 在当前会话逐项执行，先观察失败再实现。用户已授权自主定稿并继续实施，不再次要求选择方向。当前分支保留现有全部工作。

**Goal:** 用户可编辑多个颜色节点、反转、连续/分级显示、缺测颜色并导入导出方案，二维、三维、剖面、图例和导出保持同一数值映射。

**Architecture:** ScientificStyle 继续拥有按案例/变量隔离的色标和范围；颜色节点均为归一化位置，不改变模型数值。一个映射实现生成 Canvas 颜色、Plotly colorscale 和图例节点，避免多个渲染器各自插值。原 v1 配置严格迁移到 v2；无效补丁和导入原子拒绝。

**Tech Stack:** 现有 JavaScript/Canvas/Plotly，node:test，真实浏览器工作台。

## 已定稿参考与边界

- ParaView 6.2 的 Color Map Editor：控制点、预设、反转、范围锁定与导入导出；同一变量跨视图共享映射。
  https://docs.paraview.org/en/latest/ReferenceManual/colorMapping.html
- QGIS 3.44 多节点渐变和连续/离散映射：
  https://documentation.qgis.org/3.44/en/docs/user_manual/style_library/style_manager.html
- 采用 RGB 插值，明确显示插值方式，不声称实现尚未验证的 Lab/HSV 插值。预设保留 lake/cividis/viridis，增加发散蓝红；自由节点通过颜色选择器及百分比编辑。
- 范围模式仍是 auto/locked/custom，与配色方案 custom 分别存储。显示三角化不改变 GETM 的计算拓扑。陆地、湖底结构材料与数值色标分别设置。

## 任务 1：单一色标映射与持久化

Files: `3DWET/app/static/js/scientific_style.js`；新测试 `3DWET/tests/test_scientific_colormap.js`；更新现有 `test_scientific_style.js` 的默认配置断言。

- [x] 加入并运行红测试：非均匀位置节点、反转、缺测值、离散边界、非法/重复/缺端点节点、原子拒绝、外部数组不能修改存储、v1 迁移与 v2 重载。
```javascript
const stops=[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']];
S.set('A','temp',{palette:'custom',stops,reverse:false});
assert.equal(S.color(.125,S.get('A','temp')),'rgb(128,0,0)');
assert.equal(S.color(.625,S.get('A','temp')),'rgb(255,128,128)');
S.set('A','temp',{reverse:true});
assert.equal(S.color(.875,S.get('A','temp')),'rgb(128,0,0)');
```
- [x] 配置新增 `stops`（2..32 个严格递增的 `[position,#RRGGBB]`，必须 0/1 两端）、`reverse` 布尔、`mapping` continuous/discrete、`classes` 2..20 整数、`nanColor` 六位颜色。颜色/方案输入只接受受控格式，拒绝任意 CSS、脚本或超大数据。
- [x] `color(t, configOrPreset)`兼容原字符串调用；非有限 t 返回缺测色。`resolve`返回完整配置及由同一算法生成的 colorscale。分级采用等宽区间，最末区间包含 1。
- [x] `exportConfig(case,variable)`输出 version2 色标对象，`importConfig(case,variable,payload)`完整验证后一次应用；不从导入文件改变案例或变量身份。
- [x] 运行 `node --test 3DWET/tests/test_scientific_colormap.js` 和 `node 3DWET/tests/test_scientific_style.js`。有效状态重载一致，无效输入不写内存/持久化。

## 任务 2：统一所有渲染路径

Files: `scientific_heatmap.js`、`app.js`、`viz3d.js`、`scientific_workspace.js`；测试 `test_scientific_heatmap.js`、`test_viz_scientific_style.js` 与新的跨渲染映射测试。

- [x] 红测试使用同一非均匀三节点方案：二维格点、三维 intensity、关联剖面和导出图例得到相同颜色/范围；重复修改节点不可复用旧 Canvas 缓存；缺测水格采用自定义缺测色、干格采用独立陆地色。
- [x] Canvas draw 接收完整 `style`，缓存键包含实际 colorscale/反转/分级配置；分级直接按区间取色，不能用256格量化移动边界。默认旧调用仍可用。
- [x] 所有 legend/fullscreen/export 调用传完整 range，而不是只传 palette 名。CSS/Canvas 图例使用实际 colorscale 节点，分级保留阶跃。
- [x] `viz3dInheritedRange`继续严格检查数值范围、节点格式、刻度及单位；允许受验证的 custom 方案，保持关联剖面精确继承成功主图的映射。
- [x] 执行相关 Node 测试，之后完整 JavaScript 回归。不得以图例正确推断数据层正确。

## 任务 3：可用的色标编辑界面

Files: 新 `scientific_colormap_editor.js` / `.css`；`index.html`；`scientific_workspace.js`；测试采用现有底层/导出回归和真实浏览器的节点编辑、应用、取消、导入导出、键盘与窄屏流程。

- [x] 编辑器实施前真实DOM记录两个入口均缺失；实施后分别实测增删节点、位置/颜色编辑、重复位置阻止应用、取消保留已保存方案、导入导出。键盘循环另在专项复验中检查。
- [x] 在二维和三维“颜色与范围”处加入“编辑色标…”按钮。编辑器显示预览、预设、反转、连续/分级及级数、缺测颜色、可增删节点表。端点锁定位置，节点颜色自由编辑；中间节点严格排序。显示真实最小/最大值对应节点值。
- [x] 应用通过 ScientificStyle.importConfig 完整验证后原子提交并请求现有视图刷新。取消不写入；同一案例/变量另一视图自动读到新方案。导入使用普通 JSON 文件，不执行文件内容。导出只含配置/版本，不带私有路径。
- [ ] 用户保存后重开页面/重启服务能恢复；切换案例/变量不会串色标；播放中修改不重置时间、镜头或区间。

## 任务 4：真实界面与安装版验收依赖

- [ ] 用 UI_2026101601 的实际温度输出创建黑→红（25%）→白方案；比较二维、三维、XZ、全屏及真实导出；测试反转、5级分级和缺测色。
- [x] 测试430宽和900×480横屏编辑器：节点表可滚动、按钮可达、键盘可用；保留全部顶部菜单/工具。
- [ ] 集成到本批次桌面更新后，再以实际安装版验证上述功能。该功能的专项通过不是正式5轮通过。
- [x] 更新诊断账本及版本证据；最终固定版之前持续保持正式计数0/5。

## 源码专项证据（2026-10-17）

57个前端测试脚本通过；时间/ABC/完整性/导航相关Python70项通过。真实UI证据在 docs/audit/navigation-20261017：13编辑器、14二维共享分级、15实际二维导出、16初次三维导出、17窄屏编辑器、18播放中移动镜头后修改色标。实际关联剖面曾因Plotly原位规范化RGB字符串而失败，新增红测试并在绘图库边界复制colorscale后修复；主图与剖面真实UI重新通过。16初次导出没有完整关联标线，后续修复的最终导出另存。三维缺测区域的专用材料与整版陆地/连续水体仍需后续几何集成，最终安装版验收未完成，0/5。

补充：实际三维关联剖面修复后导出为audit目录中编号20的实际三维PNG，全屏19与横屏21已核对；不以初次失败的16冒充最终成功。2026-10-17全套Python512通过/3跳过、前端59个脚本通过，见诊断账本。原生安装版与3D缺测材料仍待完成，正式0/5。
