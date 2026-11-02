# 科学可视化工作台 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 实施已批准的2D/3D科学工作台，修复显示状态错误，并以五次不同数据的完整工作流验证最终同一版本。

**Architecture:** 保留Canvas2D、Plotly、现有结果API及应用导航。小型共享纯函数模块负责颜色/范围和坐标几何；渲染器负责数据与几何，界面控制器负责DOM与播放/选项联动。局部替换结果页布局，不改模型科学计算。

**Tech Stack:** 原生JavaScript、CSS、Canvas2D、现有Plotly/Chart.js、Flask；Node实际行为回归、Python接口/原生模型验证、Cua真实浏览器。

当前工作分支codex/unified-studio已有大量本目标及用户修改，继续在当前工作区操作，保留所有已有修改与证据。实施前第17次六后端已通过但UI未完成，任何源码变化须把该次记为失败并从新种子重新累计。

## 模块与共享接口

新增 `3DWET/app/static/js/scientific_style.js`，暴露 `window.ScientificStyle`：

```js
ScientificStyle.get(caseKey, variable); // {palette:'lake',mode:'auto',min:null,max:null}
ScientificStyle.set(caseKey, variable, patch); // 校验并保存；无效自定义范围抛错且不变更旧设置
ScientificStyle.resolve({caseKey, variable, min, max}); // {min,max,palette,colorscale,mode,tickvals,ticktext}
ScientificStyle.color(t, palette='lake'); // rgb()字符串，palette支持lake/cividis/viridis
ScientificStyle.ticks(min,max,count=5); // {values,labels}，窄范围刻度可区分，常量一刻度
```

新增 `scientific_heatmap.js`，暴露 `window.ScientificHeatmap`：

```js
ScientificHeatmap.layout(width,height,rows,cols,{xc,yc}); // 返回plot矩形、坐标模式、cellAt(x,y)、center(i,j)
ScientificHeatmap.draw(canvas,data,{min,max,palette,wetMask,xc,yc,showGrid}); // 返回相同geometry
```

geometry使用canvas backing-store坐标；坐标不可靠时明确I/J回退。`wetMask`与字段有限性分开，零/负数有效。root把geometry绑定canvas，点击和多边形共用cellAt/center；现有ViewControls负责CSS平移缩放。

`viz3d.js`各函数保留现有签名，opts新增或一致采用 `ve,opacity,timeLabel,caseKey`。共享色标可选，未加载时保留现有回退，避免破坏独立渲染测试。新 `scientific_workspace.js`由root负责面板、范围、时间、选项联动和导出；HTML保持现有id以兼容旧功能。

## Task 1 — 共享色标及2D科学几何（独立实现代理）

Files: 新增scientific_style.js、scientific_heatmap.js；新增 `3DWET/tests/test_scientific_style.js`、`test_scientific_heatmap.js`。不编辑app.js、模板、viz3d.js或CSS。

- [x] 写并运行纯函数行为红测试：例如 `assert.notEqual(ticks(15.149,15.150).labels[0],ticks(15.149,15.150).labels[1])`；同一case/var锁定后下一帧仍同范围；另一case无污染；非法上下限不覆盖原设置。
- [x] 实现湖蓝/Cividis/Viridis共享映射和范围模式；锁定第一次有效范围，自定义须有限min<max；全空返回明确无数据而非伪造0。
- [x] 写并运行几何红测试：真实非正方间距保持比例；yc递增时屏幕向上且命中返回原j；边距返回null；I/J回退与原索引一致。
- [x] 实现plot边距、可逆投影及绘制；岸线从wetMask，缺测湿格不同填充，内部网格可选，轴/单位/比例尺仅在可靠米制坐标显示。预计算256色查表，避免逐格反复插值。正确处理DPR/backing-store与重绘。
- [x] 测试命令 `node 3DWET/tests/test_scientific_style.js`、`node 3DWET/tests/test_scientific_heatmap.js`；检查常量/零/负值、内部缺测、岛屿和非方格。向root报告接口与测试证据。

## Task 2 — 3D科学渲染及并发正确性（独立实现代理）

Files: 修改 `3DWET/app/static/js/viz3d.js`；新增3D request/style/camera回归文件，仅编辑本任务文件，不编辑app.js及模板。

- [x] 红测试延迟旧案例fetch，改变caseRevision但不触发新3D请求，旧响应不可plot也不可更新VariableGuide/错误面板；覆盖水体/点云/等值面/地形预览/空间剖面/变量高度表面。
- [x] 在渲染开始捕获案例身份、请求令牌；各await后共同校验。可选AbortController取消本视口旧请求，避免后台积压；中止不显示错误。
- [x] 色标使用ScientificStyle.resolve，取值与Plotly cmin/cmax/ticks一致；默认数据层ambient=1以避免光照扭曲定量色；湖底中性材质，叠层透明时明确说明。
- [x] 所有真实深度模式一致接收ve；轴显示真实米数；变量高度表面明确标题。增加命名镜头入口函数（斜视/俯视/正面/侧面/复位），保留用户镜头刷新行为及正交投影。
- [x] 标题与导出包含实际timeLabel、层位和有效倍数；窄范围刻度可区分；加载/失败保留上一图但明确标记旧状态，不冒充新选择。无WebGL提示2D/剖面路径。
- [x] 跑已有test_viz_geometry.js、test_viz_render.js、test_spatial_sections.js及新回归；向root报告测试和需要的app.js调用变更。

## Task 3 — 结果页布局与响应式（独立实现代理）

Files: 只修改 `3DWET/app/templates/index.html` 的page-viz2d/page-viz3d两个区块，新增 `3DWET/app/static/css/scientific_workspace.css`。root另负责head脚本引用与版本号；不编辑其他页面或JS。

- [x] 依据批准的concept-v1把两页改为主图优先结构，保留现有控件id、inline回调、工具、参考值与分析功能。类名使用 `.scientific-workspace,.sw-command,.sw-main,.sw-viewport,.sw-rail,.sw-timeline,.sw-details,.sw-summary,.sw-analysis,.sw-camera,.sw-status`。
- [x] 保留原变量/层/渲染模式等id，新增每页range控制：`viz2d-palette, viz2d-range-mode, viz2d-range-min, viz2d-range-max`及对应viz3d；palette值lake/cividis/viridis，mode值auto/locked/custom。
- [x] 新增 `viz2d-prev,play,next,speed`、对应viz3d（speed数值frames/s）；3D新增`viz3d-camera`值oblique/top/front/side/reset，`viz3d-opacity`值1/0.55。按钮有明确title/aria-label，状态区域role=status。
- [x] 变量说明/参考来源置于可折叠details，主变量/单位仍可见；高级设置在右侧rail，剖面与点位剖面/平均全部保留。每页新增导出按钮id `viz2d-export`/`viz3d-export`，root实现行为。
- [x] 新增右侧设置开关id `viz2d-settings-toggle`/`viz3d-settings-toggle`，移动端展开后能关闭，不覆盖所有主图；对应rail id `viz2d-settings`/`viz3d-settings`。1400×900主图首屏可读，390×844可见主图+图例，844×390横屏主图优先，不能横向裁切控件。
- [x] 只做本任务布局；root浏览器整合截图后再调整CSS，不以文件存在宣称视觉验收通过。

## Task 4 — Root整合控制与数据

Files: app.js、scientific_workspace.js、index.html head引用、必要的server.py只读结果几何元数据接口及Python回归。

- [x] 所有script按style→heatmap→workspace→app调用可用顺序加载，增加CSS引用及缓存版本；延续本地依赖，不下载新渲染框架。
- [x] 红测试app.js真实调用：点云/等值面/地形预览均接收所选ve；快速变量、帧及案例切换一致。命令 `node 3DWET/tests/test_result_request_order.js` 等相关文件。
- [x] 2D缓存本案例geo/grid，使用其湿mask及可靠xc/yc；结果shape不匹配明确回退/拒绝；drawHeatmap的viz2d路径委托新模块，其余mini/avg保持原功能且选定色标一致。
- [x] getCanvasCell及polygon绘制使用geometry逆变换/center；CSS变换与backing-store共同验证。悬停区分陆地和无数据，显示原值，禁止点击图边距误选边格。
- [x] workspace按case+var管理范围并更新UI；custom非法在DOM显示且保留旧图；prev/next/play实际帧推进，播放锁定起始范围并提示越界，隐藏页面或切案例停止计时器。框架无状态时独立测试不崩溃。
- [x] 同步2D/3D主变量与时步的显式切换；高级剖面按当前变量/时刻刷新并给主图定位指示。错误/加载标记与最后成功画面身份共同显示。
- [x] 2D导出组合画布+完整元数据/色标；3D使用Plotly导出包含标题/图例/倍数；在原有ViewControls重置/全屏/缩放/尺寸机制上测试，不新建竞争事件循环。

## Task 5 — 审查、视觉验收与完整五轮

- [ ] 每个实现任务先按spec核查缺项，再独立质量审查；明确发现交由对应代理修复，不盲目接受审查意见。
- [ ] 运行全部Python与逐个Node test_*.js，修复必要回归；使用真实当前17输出在浏览器检查桌面/竖屏/横屏、无数据、细数值刻度、色标锁定、相机、剖面、缩放命中、全屏、导出。
- [ ] 比较已批准概念与实际截图，允许科学纠正示意的数字/方位，但不偏离主图优先阅读顺序。保存截图和观测，并记录质量/性能限制。
- [ ] 固定最终版本，明确关闭第17次旧版本待UI报告，依次从全新种子启动六后台+十UI组五次；中途任何失败/源变更重置。
- [ ] 更新安装包与实际安装，验证六个出厂案例及启动/依赖/快捷方式/通知/可恢复清理，最后逐项审计目标全部证据。未全部完成时goal保持active。
