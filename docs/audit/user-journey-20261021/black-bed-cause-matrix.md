# 黑色床面片：证据矩阵与区分性验证

更新时间：2026-10-25（Sol 高）

## 已知事实与状态

- 黑色床面片缺陷状态：**未修复**（用户目标场景未完成最终验收）；历史正复现代理输入在当前 v123 source replay 中未再出现黑片，属“当前渲染路径已消除该代理复现”的证据，不等于用户桌面修复。
- 根因状态：**不确定**；现有证据不支持唯一根因。v86→v123 同几何同相机比较同时改变了床面着色属性，不能区分单一机制。
- 参考截图：`（待补充：参考图的具体路径或链接）`。
- 以下“实测”仅指浏览器/桌面中的渲染行为观察，不代表湖泊科学验证。

## 变量—现象关系

| 变量 | 已观察到的关系 | 可得结论 | 状态 |
|---|---|---|---|
| 湖底图层/trace | 历史诊断对照中，隐藏床面 trace 后黑面消失；单独保留床面 trace、禁用 intensity/色带并强制纯绿时黑面仍存在。普通用户路径在 frame19、200×静态床面和50×动态叠层的近期复查未见明显黑片。 | 黑片依赖床面 trace 绘制，但床面着色不是其在历史现场出现的必要条件；近期普通路径负观察不能推翻历史条件性复现，也不能证明修复。 | **实测**（历史浏览器诊断与渲染观察） |
| 颜色编码 | 同一静态代理几何、相机与 VE=200× 下，诊断 `mesh3d.color` 分支出现近黑像素，恒定中性色标与深度色标分支未出现；但历史真实浏览器的床面单 trace 隔离实验中，禁用 intensity/色带并强制纯绿后黑面仍存在。 | 颜色编码会影响一组代理渲染，但不能解释原现场黑面出现的必要条件，也不足以作为生产修复依据；可能与其他因素交互。 | **实测**（受控代理渲染与历史浏览器条件性对照） |
| 动态/静态绘制路径 | 同案例、同帧、同视角与 VE=200× 的历史浏览器对照中，静态 bathymetry 预览未见近黑大片，恢复动态变量叠层后黑面复现；两条路径的床面数据和 trace 属性不完全相同。动态场 trace 被隐藏、动态床深替换为静态 `bottom` 后仍曾观察到黑面。 | 支持动态/静态绘制路径或其与床面网格的交互为候选；trace/属性差异和历史运行版本尚未完整控制，不能锁定具体机制。 | **实测**（历史浏览器诊断） |
| 视角 | 既有浏览器对照称黑片随视角变化；在中性色 200× 诊断中俯视可见更大范围黑色湖盆面。当前 frame19/34°普通路径未明显复现。 | 视角影响可见性/覆盖范围；未固定颜色、几何与遮挡因素做完整角度单变量对照。 | **实测**（条件性观察） |
| 垂向倍率 | 既有对照称现象随 VE 变化；高 VE=200× 固定色静态诊断出现黑片，50×动态叠层色标路径未见同样黑片。普通路径 200×叠层近期未复现。 | VE 与显示路径可能交互；上述两条件同时改变图层/颜色路径，不能归因于 VE 单因子。 | **实测**（条件性观察） |

## 存档正复现截图的视觉复核（2026-10-26）

- **实测（历史截图观察）**：`erken-black-bed-final-20261023.png` 的标题记录 2020-DOY001 02:00、层 9/9、VE 166.5×、采样显示；`erken-bed-color-range-before-20261023.png` 记录同日 06:00、层 9/9、VE 166.5×。两图都显示温度场为蓝色，上部湖盆外缘以下有大块不规则黑色面片，部分邻接灰蓝色侧面。
- **证据限制**：截图只证明当时屏幕上出现这些黑色区域；图像未包含当时的 Plotly `_fullData`/trace 清单、几何 `x/y/z/i/j/k` 或 GPU 绘制信息。因此不能仅凭图像确认黑色像素来自床面、边界墙或其他重叠面，也不能把颜色或特定几何宣布为唯一根因。上述旧帧截图与用户后来反馈的当前 frame19 静态 200×/叠层 50×近期未复现并不冲突；当前缺陷仍**未修复**，根因仍**不确定**。
- **图片定位边界**：这些路径是仓库内历史黑片证据，不是用户提到的 UI 设计参考图。UI 参考图仍保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-26 Sol：存档截图局部视觉复核

- **实测（历史图像观察）**：重新查看 `erken-black-bed-final-20261023.png` 原图，黑色像素块主要显示在水平湖面/示意平面以下的湖盆外缘区域，旁边可见灰蓝侧面；水平面上方的温度场本身为蓝色。它使“床面与湿网格侧壁/下表面重叠”以及“网格三角面/投影交互”成为优先区分的候选。
- **不确定**：该 PNG 未包含对应图元的 trace 身份、原始 `_fullData`、深度缓冲/绘制顺序或三维顶点法线；无法从图像判断黑色究竟由床面、边界剖面还是两者遮挡/光照交互生成。因此本次只调整候选验证优先级，不确认根因、不修改生产渲染代码。需要原现场同帧载荷与 trace 审计，再单独开关床面和侧壁并记录像素变化。
- 黑色床面片仍为**未修复**，根因为**不确定**；该历史图观察不等于当前桌面复现。参考图仍保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 历史正复现载荷：旧版与当前源码重放

- **状态：代理（headless renderer 对照）**。同一 Erken frame19 代理载荷、相机、视口与床面 `x/y/z/i/j/k` 几何哈希，在历史 v86 与当前 v123 源码下重放。v86 全场 ROI 中 75,471/572,400 像素低于 RGB 40；当前 v123 为 0。床面单 trace 下 v86 为 245,173/572,400，v123 为 0。v86 强制纯绿且 ambient-only 仍为 245,173；因此该重放中的黑片不能简单归因于色值。
- **可确认结论**：当前 v123 的组合床面渲染路径消除了这份历史代理载荷的黑片复现。两版床面编码分支和照明属性同时不同，无法指出单个属性或 WebGL 内部唯一根因。
- **不确定/未完成**：用户所见桌面版本与目标 GPU 下最终验收仍未完成；参考图位置仍 `（待补充：参考图的具体路径或链接）`。该渲染重放不是湖泊科学验证。
- 复现细节、逐项像素筛查、输入/渲染器/相机哈希及限制见 [`v86 vs v123 replay`](../../../build/bed-black-v86-replay-20261025/README.md)。

## 2026-10-25 历史 v86 同轨迹单属性控制

- **状态：代理（headless renderer 对照）**。固定同一 v86 床面 trace、frame19 几何、相机、视口、Plotly 2.35.2 与 Edge/ANGLE RTX 4070；单独添加 direct `color`、单独添加 `intensity`、单独替换 constant colorscale，以及分别仅改 ambient/diffuse lighting。几何签名在全部组一致。
- ROI `(180,280)-(1240,820)` 中，旧版基线近黑像素 245,173（`max(R,G,B)<40`）；单独添加 intensity 后为0；仅改 direct color、常量 colorscale、ambient-only 或 diffuse-only 均仍为245,173。
- **区分结论**：此 harness 中 intensity/自动着色编码分支有区分性。添加 intensity 后 Plotly `_fullData` 自动选择 colorscale（旧 trace 的 `autocolorscale=true`），因此无法把结果再拆成 intensity 数组和自动 colorscale 的独立效应；不据此确认唯一根因或生产修复。
- 数据、脚本、六组截图、`_fullData`、哈希及 ROI 像素数见 [`single-property controls`](../../../build/bed-black-v86-attribute-ab-20261025/single-property-controls/README.md)。黑色床面片仍**未修复**，根因仍**不确定**；须在用户目标桌面实际正复现场景继续验证。

## 候选解释（均非已确认根因）

1. **床面几何/网格与视角、VE 交互（不确定；优先验证）**：历史真实浏览器中，床面单 trace 在禁用 intensity 和色带、改成纯绿色后仍保留黑面；历史截图的黑片主要位于示意平面下方的近侧湖盆边缘。局部几何、投影或高 VE 下屏幕空间退化仍可能参与，但尚无匹配 `_fullData`/目标设备复验。
2. **动态/静态绘制路径或 trace 更新交互（不确定）**：同案例历史画面在静态 bathymetry 与动态变量叠层间表现不同；即使隐藏动态场或替换动态床深，黑面仍曾出现。当前尚未在同一生产版本下比较实际床面及附属 trace 属性。
3. **床面、墙面、岸线或陆地示意面的遮挡/深度顺序（不确定）**：墙 trace 单独隐藏后黑面仍出现，说明独立墙 trace 不是充分解释；其他床面边缘/岸线/陆地 trace 的重叠顺序仍未在匹配基线下排除。
4. **mesh3d 着色路径交互（不确定；次要候选）**：同一代理几何在显式直接色诊断分支出现近黑像素，而恒定色标和深度色标分支未出现；但历史原现场的床面单 trace 在强制纯绿后仍黑，故此因素不是已证实的必要机制，也不支持当前生产代码按颜色分支直接宣称修复。
5. **trace 属性/缓存或更新状态（不确定）**：静态床底与动态叠层可能复用或更新 trace；运行时 `_fullData` 仍未在正复现场景采集，源 trace 属性不能代表实际渲染输入。
6. **深度缓冲、投影或数值精度（不确定）**：大 VE 压缩水平与垂向的深度范围，可能放大 z-fighting 或精度差异；现有代理单因素矩阵未复现黑片。

## 区分它们所需证据

先在用户原始场景可靠复现（frame19、同一湖底数据、变量、相机、VE、图层状态），保存截图和每次渲染的 Plotly trace 快照。逐项记录 `x/y/z/i/j/k`、`intensity`、`color/colorscale`、`cmin/cmax`、`visible`、trace 顺序及 `_fullData`，同时记录相机、投影、视口尺寸、GPU/浏览器版本。原始参考截图路径缺失，故其视角/图层仍需用户补充。

在黑片稳定出现的基线之上，每次只改变一个因素：

1. **床面几何**：在真实正复现基线下保留同一床面单 trace，逐一记录/可视化四边形、三角索引、顶点和面法向、有限值与投影后退化；纯色不应替代几何核查。
2. **绘制路径/图层组合**：固定帧/相机/VE/视口，保存静态预览与动态叠层各自的生产 `_fullData`；然后逐一显示/隐藏 bed、shoreline、coastal rim、land、wall、contour、field。历史墙 trace 隐藏与纯绿 bed-only 测试需保留为已有对照，不把它们重复当成新结果。
3. **颜色编码**：在已复现的实际生产 trace 上固定几何、属性范围和其他 trace，对比深度色标与恒定中性色标；单色诊断只作为分支交互测试，不将其结果外推为必要根因。
4. **视角**：固定上述输入，仅扫顶视与多个明确记录的方位/仰角；截图需保持同尺寸。
5. **VE**：固定图层、颜色及相机，仅按 50×、100×、200×变化；保存每次原始和压缩后的 Z 范围、极值/NaN 计数及三角形索引。
6. **深度检验**：仅在几何与图层对照后仍有证据时再查投影/深度精度；不要把颜色、图层与相机同时改动。

仅当同条件基线稳定复现、单变量干预可重复消除异常、并且生产路径以相同 trace 数据确认时，才将候选升级为可确认机制。否则继续保持根因**不确定**，不以当前负观察宣称修复。

## 2026-10-25 历史 frame 19 单变量 headless 因子矩阵

- **状态：代理（渲染诊断，非科学验证）；缺陷仍未修复。**使用既有只读历史代理 API 快照，保持 frame 19、`temp`、第 9/9 层、湿拓扑、值域、叠层透明度、方位、正交投影和视口固定。生产动态温度叠层与三角显示网络均开启；网络 trace 在 9/9 个条件中均可见，记录 55,212 个坐标点（对应 18,404 条显示边）。显示网络是从抽样湿结构网格派生的显示剖分，不是求解器原生三角单元。
- VE 对照为 50×、100×、166.5×、200×，相机仰角对照为 0°、34°、70°；另有 VE=166.5×、34° 下床面 trace 隐藏/显示成对条件。`render-summary.json` 中 `_fullData` 审计确认床面可见性只在最后一组成对条件间变化，温度叠层和三角网络保持可见。
- 9 张图在中央区域按 `max(R,G,B)<40` 的简单像素筛查均为 0 个近黑像素。该阈值不是床面分割；这些代理负结果不反驳历史条件性现象。联系表可见相机与 VE 改变了湖盆显示形态，床面 trace 隐藏时湖盆静态底面消失，但没有任何条件复现用户报告的黑片。
- 结果与复现边界记录于 `build/bed-black-historical-factor-matrix-20261025/results-05/README.md` 和 `render-summary.json`。未打开桌面 APP、未启动求解器、未创建或修改案例；未改应用代码。
- **结论：**床面绘制路径、视角、VE 仍是需分离的候选因素；本矩阵没有建立用户报告黑片的因果关系，也未证明已修复。唯一根因仍**不确定**，缺陷状态仍**未修复**。原始参考截图路径继续保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 当前源码算法的只读几何审计（代理输出）

- **代理（API/几何数据检查，非科学验证）**：复用既有隔离服务 `127.0.0.1:59467` 与只读案例 `Erken 20-frame historical readonly`，读取 frame 19、`temp`、目标层 26 的 surface API 数据。案例运行保持 idle。服务 HTML 的 `viz3d.js` 查询版本标签为 v116；但通过原始字节下载验证，服务实际返回的 `viz3d.js` SHA-256 为 `AB280EF731E8EE3E4453A4FEB282A54B379B791E43BF975CA41137BD13AC25F0`，与当前工作区源码相同，HTTP 缓存策略为 `no-cache`。因此下面的几何统计是用当前源码算法对代理输入计算，不是浏览器 `_fullData` 或 GPU 像素证据。
- API 网格为抽样 `1×18×22`、源网格 `10×18×44`，拓扑 `sampled-wet-topology-v1`。按动态 `water_depth`、200×倍率和 `buildLakeGeometry` 的角点邻格平均/三角化规则重算：168 个采样湿格、672 个床面顶点、336 个三角面；退化面 0；三角面积约 `63,466–406,598 m²`；336 个面法向 z 分量均为正。角点深度约 `0.9987–17.2961 m`，床面 z 约 `−3459.21–−199.74 m`。
- **结论限制**：这排除了该 API 抽样代理帧中可由零面积三角形或混合面绕序直接解释的情况；没有检查原始报告的完整网格、实际 Plotly `_fullData`、目标设备 WebGL 深度缓冲或屏幕空间遮挡。该代理帧也没有复现黑片，因此不能据此排除这些机制、确认唯一根因或宣称修复。黑片仍**未修复**、根因仍**不确定**。

## 2026-10-25 隔离 Erken baseline 生产页复查

- **状态：实测（可见渲染复查）；未复现；未修复。**为避免改变桌面当前案例，将已有 `erken-real-location-24h/baseline` 配置复制到独立 model root；输出目录链接到原始结果目录并仅用于读取。未启动新的求解，也未写入输出文件。
- 隔离服务 health 指向 `build/black-bed-followup-20261025/model-root`。活动案例为 Erken baseline isolated。可见 3D 页面脚本版本为 `app.js?v=71`、`i18n.js?v=14`、`viz3d.js?v=108`；服务端 `viz3d.js` 与工作区 SHA-256 均为 `F63DDE1F81D5B742895430C86C249E88A0E61BC65D9FF3C5ED94E757C1029700`。
- 结果来自 `ERKEN_REAL_20200101_24H__WET.3d.nc`，SHA-256 `B8EFEF78472F8A4437F18E73D387315E0BA4208EF7271E6CB5E59E5E012CD21C`。frame 19 对 `temp` 的 API 形状为采样 `1×18×22`、原生 `10×18×44`，值域 `2.18004894256592–2.18964958190918`，拓扑状态 `ready`、`surface_sync_mismatch=false`；frame 1 对应值域为 `2.18004894256592–2.18130779266357`，其余几何状态相同。
- 在 frame 19、层 9/9、当前 34° 初始视角下，实际页面分别显示 200× 和 50×，截图均未见明显黑片；另外在历史截图标注的 2020-DOY001 02:00、层 9/9、自动倍率 166.5×（frame 1）复查，也未见明显黑片。此页窗口宽度/图表绘图区与历史截图不同；API 结果是生产页面数据，但它不能替代缺失参考图，也不能确认历史异常原因。
- 本次覆盖动态水体叠层中的床面 trace。没有取得“床面-only / 静态地形预览”与叠层在完全相同相机、视口和 trace 属性下的成对截图与 `_fullData`；没有复现异常，所以没有实施渲染修复。湖底图层、相机、垂向倍率仍可能与现象有关，唯一根因仍为**不确定**。
- 隔离运行目录为 `build/black-bed-followup-20261025/`。当前主桌面服务没有被切换案例或改动，代码及求解器均未修改；此文档更新无需桌面同步。

## 2026-10-25 同一历史 20 帧 Erken 输出复查

- **实测（浏览器渲染观察；代理 Erken 求解结果）**：将 `build/real-use-validation-20261023/user-journey-Erken-import` 的案例输入复制到黑片隔离 model root，输出目录只读观察并链接至原输出；结果文件 `USER_JOURNEY_ERKEN_IMPOR_WET.3d.nc` SHA-256 为 `A94B84C353F205BA695E6364231A74DC3C4FFD452E1AC44C73276146CAE2D6E5`。未运行求解器，未编辑原案例或其输出。
- **实测（负复现）**：当前 v108 生产页设置为 `temp`、frame 19（2020-DOY001 02:00）、层 9/9、相机仰角 34°、自动垂向倍率 166.5×、模型位置 +15%，可见画面未复现历史截图中的大块黑色床面下侧面。额外观察 VE=200×（相机/帧保持不变）也未见该大块黑面。UI 状态与图像经当前页面直接读取。
- **可比性限制**：当前 IAB 浏览器视口约 405×700，历史截图约 1700×1000；Plotly 响应式图表的绘图区、像素密度与裁切范围不同。未取得 floor-only / overlay 同 viewport 截图，也未读取浏览器 `_fullData`。因此这两次是同一历史输出的负复现，不推翻历史 2026-10-24 同案例迹线隐藏/恢复的条件性复现，不证明当前版本已修复。
- **结论**：黑色床面片仍**未修复**；根因仍**不确定**。湖底迹线、视角、垂向倍率的各自因果作用仍未分离。下一项有区分力的验证仍需原始正式 viewport 与单因素 trace 对照；参考图路径保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 isolated camera-only comparison on Erken June 2024 attempt03

- **实测（render observation on proxy result）**: the local page at `127.0.0.1:52862` reported active case path `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`, with 168 output frames. The displayed UI state was frame 19, layer 9, `temp`, 200×, oblique 34°. No conspicuous near-black bed patch was visible in the current 405×700 browser viewport.
- **实测（single-factor camera comparison; still not a reproduction）**: with case, frame, layer, variable, and 200× held, changed only the camera preset to `View from below` (-89°). UI status explicitly said the bed and land reference plane were hidden in bottom view; no target black patch was visible. Restored the oblique 34° preset afterward. This supports that view selection changes which bed surfaces are rendered, but does not explain the historical black patch.
- **Limitations**: this 168-frame Erken arm_A output is an attempt03 engineering/proxy run, not a scientifically validated Erken case. The viewport remains smaller than the historical capture, and no floor-only/wall-only screenshots or Plotly `_fullData` were captured. The black patch remains **未修复**, with root cause **不确定**. Do not use this observation to claim the scientific case passed.

## 2026-10-25 static isolation harness visual check

- **实测（render observation on proxy fixture）**: served the existing read-only diagnostic fixture from `build/real-use-validation/20261023/erken-june2024-competition-luna-attempt03/bed-black-render-repro/` and visually compared its fixed API snapshot (`temp`, frame 167, target 26; 185 wet cells; auto VE 175.7×). The production-like and neutral-color panels show pronounced bed geometry in this high-VE projection but no conspicuous black patch. The direct neutral-color panel appears gray in this harness; it does not contradict the older v107 direct-color diagnostic because this is a different fixture/trace context and does not reproduce the reported frame19 user path.
- **实测（isolated trace visibility; proxy fixture only）**: the harness toggles floor-only versus walls-only with geometry and camera held fixed. The floor-only panel displays the bed surface; walls-only displays disconnected boundary wall faces. No black patch was visible in either state in the current viewport. This establishes what these isolated traces render for this captured fixture only; it cannot rule out a full-scene interaction involving the water surface, shoreline, contours, or land plane.
- **Limitations / next evidence**: no production change was made. The fixture is frame167, not the frame19 report; the plot uses a simplified scene, fixed camera/VE, and omits other traces. Root cause remains **不确定**, defect remains **未修复**, reference image remains `（待补充：参考图的具体路径或链接）`. The discriminating next step is a matched frame19 production `_fullData`/screenshot capture before any change.

### Frame19 API input snapshot for trace-audit planning

- **实测（API metadata; Erken attempt03 proxy output）**: requested the same current page state from `127.0.0.1:52862/api/results/3d_surface?var=temp&time=19&target=26&level=-1&layer_only=1&waterbody_compact=1`. The active case is Erken June 2024 competition attempt03 arm_A; response shape is sampled `1×18×22`, source `10×18×44`, stride `1×1×2`, 10 layers, `depth_source=hn+zc`, `surface_source=hn-bathymetry`, `surface_sync_mismatch=false`, topology status `ready`; all 185 sampled wet cells have finite temp, finite dynamic depth, finite bottom, and valid geometry. Temperature range is 10.7783–15.8922 °C.
- This rules out missing API values or a reported surface-depth sync mismatch for this sampled proxy frame. It does not verify the Plotly trace arrays after render, the screenshots at the original viewport, or a scientifically validated Erken run. The bed defect remains **未修复**, root cause **不确定**.

### 2026-10-25 production-path `_fullData` capture (frame 19)

- **实测（browser render; Erken June 2024 attempt03 arm_A proxy output）**: On the isolated probe service `127.0.0.1:52862`, `/api/case/current` identified the active case path as `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case`, run id `ERKEN_JUNE24_ABC_A`, 168 output frames. This remains a proxy/model candidate run, not scientific validation.
- **实测（render conditions）**: Opened the page with `?viz3d-trace-audit=1` to expose the actual Plotly `_fullData`; set frame 19, layer 9, `temp`, oblique 34°, 200×. The viewport screenshot showed no conspicuous black bed patch. The browser viewport/layout differs from the missing reference image.
- **实测（rendered trace data）**: The report contains seven traces. The bed trace is visible `mesh3d`, depth colorscale, opacity 1, neutral lighting (`ambient=1`, `diffuse=0`, `specular=0`); its x/y/z and i/j/k arrays are finite, with 1504 vertices and 752 face indices. The selected temperature trace is also visible `mesh3d`, opacity 1 and vertex intensity; its 1504 x/y/z/intensity values are finite. The water surface is `legendonly`; shoreline, contours, land reference, and triangulated land are separate visible traces. This rules out non-finite values in the reported bed and selected-data arrays for this rendered proxy state, but not WebGL rasterization, face winding/topology, z-buffer/overlap effects, or interactions with other traces.
- **未修复 / 不确定**: This is a negative reproduction under the current viewport and proxy output. It neither proves the original defect is fixed nor establishes a unique cause. No production render change was made. Exact screenshot, dimensions, GPU/browser details, selected bed-layer state, and matching trace report at the reported failure are still needed to distinguish candidates. Reference image remains `（待补充：参考图的具体路径或链接）`.

### 2026-10-25 current v116 render on Erken 2020 historical proxy

- **实测（render observation; proxy result only）**: On the isolated v116 renderer at `127.0.0.1:59467`, opened the existing `Erken 20-frame historical readonly` result; no solver was run. At frame 19 (`2020-DOY001 02:00`), `temp`, layer 9/9, oblique camera 34°, vertical exaggeration 200×, and model position 0%, the 1280×720 browser capture did not show a conspicuous near-black bed patch. The blue field surface, pale land reference plane, and blue basin walls remain distinguishable.
- **实测（read-only Plotly `_fullData`; proxy result only）**: The visible bed is trace 0, a depth-colored `mesh3d` with 1504 vertices and 752 faces; `x/y/z/i/j/k/intensity/customdata` contain no non-finite entries. The selected temperature field is trace 6, also 1504 vertices and 752 faces with finite coordinates and intensities. The water surface is `legendonly`; shoreline, contours, land reference plane, land triangle lines, and a separate display-triangulation line trace are present. This rules out non-finite array values in the captured bed and field traces for this state only. It does not rule out face-winding, rasterization, z-buffer, projection, or multi-trace overlap effects.
- **可比性限制**: This is the Erken 2020 20-frame readonly proxy result, not the historical user's specific reference condition. The viewport is 1280×720, not the missing original reference viewport. The renderer state is a negative reproduction; it cannot establish a fix or identify a unique cause.
- **结论**: The black-bed defect remains **未修复** and its root cause remains **不确定**. No bed geometry, material, or color production change was made. The reference location remains `（待补充：参考图的具体路径或链接）`.

### 2026-10-25 archived screenshot review and current source path

- **实测（historical screenshot review; not a new reproduction）**: inspected the repository's archived capture `erken-black-bed-remains-20261023.png`. It shows a faceted near-black region below the pale top plane around the basin perimeter. The visible annotation reads frame 2020-DOY001 02:00, layer 9/9, vertical 166.5×, sampled display. This is a recorded diagnostic image, not evidence that the user-specified missing reference has been supplied; retain `（待补充：参考图的具体路径或链接）`.
- **实测（source inspection, current working tree）**: `buildLakeGeometry` emits each wet-cell floor as four vertices and two triangles, with `z=-cornerDepth×VE` and depth-valued vertex intensity. `lakeTraces` renders this as a Plotly `mesh3d` using the depth colorscale and ambient-only lighting. For the current high-VE dynamic overlay path (`VE>80`), the separate wet-grid boundary-wall trace is omitted. The archived image predates the current source/render path and has no corresponding `_fullData` capture, so this does not establish that the historical dark facets came from the floor mesh.
- **结论**: the historical image strengthens the description of the symptom but does not make it reproducible on the current production path. Floor rendering, historical wall/floor overlap, topology, and camera/depth precision remain candidates; no unique root cause is confirmed. The black-bed issue remains **未修复** and the next discriminating evidence is still a matched current-path reproduction with the full trace set captured.

### 2026-10-25 Sol/Luna: bed color-domain invariant correction

- **实测（源码/回归测试）**：`lakeTraces()` 可接收科学变量的颜色范围，而床面深度网格使用独立的米制深度色带。回归测试构造高 VE 覆盖场景，先复现床面错误继承 `10..25` 变量范围而不是 `0..8 m`；修正后床面 `cmin/cmax` 固定为 `0..geometry.maxDepth`，科学场变量继续使用自身范围。
- **修正边界**：这是确定的色标单位/范围一致性错误；当前 `render3DWaterBody()` 高 VE 覆盖路径向 `lakeTraces()` 传入空 style，因此测试构造的继承路径不是当前常规高 VE 调用。修正没有复现用户黑片，也不能解释历史画面。
- **候选根因仍不确定**：黑片截图中可见湖盆下侧黑色三角面；已有可用诊断数据为 frame167，而目标报告为 frame19，且没有匹配的 `_fullData`/GPU 截图。床面三角网、视角/投影、深度精度和多 trace 遮挡仍是候选，不提升为唯一根因。
- **验收**：`test_lake_display_mesh.js` 51/51、`test_viz3d_waterbody_patch.js` 3/3；源码语法检查通过。桌面服务对 `viz3d.js?v=121` 返回字节与工作区 SHA-256 一致。黑色床面片仍**未修复**，参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol: archived controlled-render counterchecks

- **实测（历史截图观察）**：同一存档时刻 2020-DOY001 06:00、层 9/9、VE 166.5× 的 `erken-bed-color-range-before-20261023.png` 与 `erken-bed-color-range-after-20261023.png` 都保留近似相同的黑色湖盆下侧面；图中温度自动色标范围不同，但黑面没有随之消失。`erken-black-bed-flatshading-20261023.png` 也仍显示黑色三角区域。
- **区分性结论**：历史测试不足以排除颜色/着色与其他 trace 的交互，但反证了“单独改变所选温度范围”或“单独启用 flatshading”即可稳定消除该画面异常。它们不是已确认的充分修复。
- **限制与下一步**：这是历史存档的可视对照，不是当前源码或用户原始参考图的匹配复现；不同截图是否只改变单一参数还需根据当时运行记录确认。下一次有效验证应在同一帧/相机/VE/视口捕获当前完整 `_fullData`，分离 bed、land、shoreline、coastal rim/wall traces，再一次只切换一个遮挡/背面绘制因素。黑片继续**未修复**，唯一根因继续**不确定**。

### 2026-10-25 Sol/Luna：历史床面/侧壁证据与当前 trace 集对照

- **实测（历史浏览器记录，非当前版本复现）**：`STATUS.md` 的 2026-10-23 隔离图层记录显示，关闭 Plotly 图例中的“湖盆水深”床面后，黑区消失，而不透明蓝灰侧壁仍可见；恢复床面后黑区重现。关闭示意陆地没有消除黑区。该记录使床面绘制或其与极端垂向显示的交互更值得优先检查，也说明侧壁单独存在不足以解释该次黑区；它没有记录当前版本的匹配 `_fullData`，不能确认具体渲染机制。
- **实测（当前源码 trace 构成审阅）**：动态叠层在 `VE>80` 时保留独立深度色标的床面，但不生成 `waterbodyFrame=wall`；静态地形路径同样不生成该 wall trace，而额外生成已验证岸边的 coastal rim 和显示网格线。两种路径还分别包含科学变量场或静态床面样式，因此静态/动态差异不是只切换一面墙。现有 frame167 隔离夹具的 floor-only、walls-only 与组合对照没有复现黑区，且不包含正式场景的水面、岸线、等深线、显示网络和陆地平面。
- **结论与下一步**：现有证据优先支持“床面 trace 相关”，但不证明床面 trace 自身是唯一原因；几何、着色/插值、相机/垂向跨度、深度缓冲及多 trace 交互仍为**不确定**候选。只有当前生产路径在匹配 frame、相机、VE、视口复现后，逐条保存/隐藏 bed、rim、land、shoreline、contour、field 并取得重复像素差异，才足以决定生产修复。黑片仍**未修复**；参考图继续为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：当前渲染构造的 frame19 无头浏览器对照

- **代理（渲染诊断，非科学验证）**：复用既有 Erken engineering/proxy frame19 API 快照 `build/bed-black-frame19-readonly-probe-20261024/frame19-target26.json`，以当前 `viz3d.js` 的 `buildLakeGeometry`、`lakeTraces`、`lakeScene`、`lakeLayerCornerAverages` 和 `lakeLayerMeshes` 构建静态床面 200× 与 `temp` 动态叠层 50×，并由本地 Plotly 2.35.2 在 headless Edge/SwiftShader 中渲染。视口为 1800×900，固定正交相机 eye `{x:1.55,y:1.45,z:1.2}`。
- **实测（该无头诊断页面）**：两幅图均未出现明显近黑床面片。Plotly `_fullData` 中静态路径 7 条 trace、动态路径 8 条；床面均为 672 顶点/336 面，静态岸边 rim 为 160 顶点/80 面，动态温度场为 672 顶点/336 面；检查到的 trace `x/y/z` 全部有限。截图、summary、DOM 和 SHA-256 见 [`build/bed-black-frame19-current-render-audit-20261025/README.md`](../../../build/bed-black-frame19-current-render-audit-20261025/README.md)。
- **限制与结论**：输入是代理结果；无头 SwiftShader、固定相机和独立页面不等于原用户 GPU、浏览器及完整桌面渲染编排。它是同一代理快照上的当前代码负复现，不是修复证据，不能排除真实环境中的栅格化、深度或 trace 交互。黑片仍**未修复**，根因仍**不确定**；没有改生产代码。下一步仍需原报告状态的正式页面复现与逐 trace 对照；参考图保留 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：床面 Mesh3d 颜色编码单变量复现

- **代理（渲染诊断，非科学验证）**：在相同 frame19 proxy 快照、200×静态床面、固定正交相机和几何下，使用当前 `lakeTraces()` 构建三种床面：正常深度色标、显式诊断单色 `color`、恒定中性色 `colorscale`；另附50×动态温度对照。截图见 [`build/bed-black-frame19-color-encoding-audit-20261025/render.png`](../../../build/bed-black-frame19-color-encoding-audit-20261025/render.png)，方法与限制见同目录 [`README.md`](../../../build/bed-black-frame19-color-encoding-audit-20261025/README.md)。
- **实测（无头像素和 Plotly `_fullData`）**：三种静态 bed 的 `x/y/z/i/j/k` 几何签名相同，均672顶点/336面。直接单色 `color` 视图近黑像素比例8.8036%；正常深度色标与恒定中性色标各为0.0000%。直接单色床面没有 intensity；两种色标路径都有672个 intensity 值。结果支持颜色编码分支敏感性，但不确诊 Plotly/WebGL 内部机制，也不证明普通用户路径调用了该诊断分支。
- **桌面资源核对**：52812 服务健康、模型 idle，model root 是当前仓库。首页仍引用 `viz3d.js?v=119`，但该URL响应字节与当前工作区 renderer 哈希一致。旧 HTML 标签不能单独证明浏览器正在执行旧 renderer；本轮没有刷新/打开桌面，也没有检视实际 DOM 状态。
- **Sol判断/未完成**：已要求 Luna 增加防止床面 direct-color 分支产生黑面的最小代码保护，并保持物理深度色标和科学变量色标不变。现阶段结论是**候选机制得到更强支持**，但黑片仍**未修复**、唯一根因仍**不确定**；默认用户路径及原用户设备仍须单独验收。参考图继续为 `（待补充：参考图的具体路径或链接）`。
## 2026-10-25 post-Luna neutral encoding review

- **代理（headless visual render on proxy snapshot）**: reran the four-panel frame19 harness against the current `viz3d.js`. Depth bed, the `force-bed-neutral` diagnostic, constant-neutral-scale diagnostic, and VE 50× temperature overlay each measured 0.0000% near-black pixels at threshold `max(R,G,B)<40`. The diagnostic that previously emitted direct `mesh3d.color` now emits the constant neutral colorscale. Screenshot and hashes are in [`post-Luna render`](../../../build/bed-black-frame19-post-luna-audit-20261025/README.md).
- **代理（regression evidence）**: 11 bed-focused, 26 waterbody composition/playback, and 51 mesh display tests passed. Tests assert that the neutral bed keeps its depth intensity, geometry, hover information, and selected scientific field data.
- **Conclusion**: the explicit neutral direct-color branch is now protected and no longer reproduces black in this proxy/headless setup. This is not the originally reported production/user path, and the headless renderer is not the user's desktop GPU or camera. So the black bed remains **未修复**, and a unique cause remains **不确定**. Other live candidates include bed-vs-wall/shoreline overlap, camera-dependent face visibility/lighting, and high-VE projection interactions; separate geometry/visibility/lighting A/B traces under the actual state are needed to distinguish them. Reference image remains `（待补充：参考图的具体路径或链接）`.

## 2026-10-25 Sol/Luna：frame19 单变量视角、倍率与图层可见性矩阵

- **代理（渲染诊断，非科学验证）**：只读 runner 使用已有 frame19 proxy API 快照，固定字段、湖底、网格、方位、正交投影和视口，只分别改变视角（0°/34°/70°/−89°）、垂向倍率（20×/50×/100×/200×）或隐藏床面/墙面/岸线单一 trace。没有启动模型或新建案例，也没有打开或刷新桌面应用。
- 10 个场景的中央 ROI 与整张 PNG 都为 0 个近黑像素（`max(R,G,B)<40`）。这说明该 fixture 在本轮 headless Edge/SwiftShader 条件下仍未复现黑片；因没有阳性基线，矩阵不能判定缺陷根因或证明修复。黑片状态保持**未修复**，根因保持**不确定**。
- VE>80×时现有 renderer 会省略动态墙面 trace；该政策已记录在摘要中，是解释 VE 对照时的限制。参考图仍为 `（待补充：参考图的具体路径或链接）`。
- 方法、摘要、截图和限制见[矩阵报告](../../../build/bed-black-frame19-variable-matrix-20261025-02/README.md)及[对照总图](../../../build/bed-black-frame19-variable-matrix-20261025-02/matrix-contact.png)。矩阵工具单元测试：**代理，5/5 通过**。

## 2026-10-25 Sol：历史日期代理帧与床面编码补充对照

- **代理（headless Plotly 渲染，非科学验证）**：使用 2020-DOY001 frame 19 的只读 API payload，对齐历史截图记录的物理层 9/9、VE 166.5×、相机仰角 34°与模型垂直位置 +15%。该 payload 为抽样 `1×18×44`、源网格 `10×18×44`，并保留显示拓扑。当前生产深度色标、生产恒定中性色标和一个合成的旧式固定 `color` 编码对照均使用同一帧、网格、相机及视口。
- 三幅图均完成 7 条 trace 渲染且无异常；全图阈值 `max(R,G,B)<50` 的近黑像素数都是 0。合成固定色会改变床面色调/面片观感，但没有在此 payload 与相机下复现黑片。截图、`_fullData`、像素指标及哈希见[编码对照报告](../../../build/bed-black-patch-encoding-control-20261025/README.md)。
- **同当前工作区旧代理 payload 的元数据核对**：较早出现近黑像素的 target26 payload 为抽样 `1×18×22`、stride `1×1×2`，变量值域约 `10.778–15.892`；本次历史日期 target96 payload 为完整 `1×18×44`、stride `1×1×1`，值域约 `8.301–14.871`。两份输入同时在结果/网格分辨率与场值上不同，故它们之间无法归因于编码或分辨率中的任一单因子。下一项有区分力的检查是基于同一输出分别请求/重建两种有效采样拓扑，再做 `colorscale` 与固定 `color` 的交叉对照。
- **判断**：这项负结果表明“固定 `color` 编码单独足以在任意输入下产生该黑片”不受本代理帧支持；它不推翻较早 frame19 代理 payload 上固定色对照出现近黑区域的观察，也不证明历史生产路径采用了该编码。床面数据/几何、采样分辨率、光栅化、遮挡、视角与垂向投影等仍可能交互，唯一根因仍**不确定**。
- **状态**：黑片仍**未修复**。原始用户参考图仍为 `（待补充：参考图的具体路径或链接）`；当前 headless 代理渲染不能替代原用户设备与原视口的阳性复现。

## 2026-10-25 Sol/Luna：同一历史输出的采样分辨率 × 着色对照

- **代理（headless Edge/SwiftShader 渲染，非科学验证）**：将同一只读 Erken 2020 frame19、同一变量/层和静态相机分别请求为全分辨率 `1×18×44` 与 API 有效降采样 `1×18×22`（stride `1×1×2`）。每种分辨率内并排渲染生产深度色标、合成固定 `color` 和恒定中性色标；另列 50× 动态温度叠层。全分辨率与降采样结果来自同一输出，不是另一个案例。
- 两种分辨率的整张 PNG 在阈值 `max(R,G,B)<40` 下均为 0 近黑像素。视觉上降采样明显改变床面/岸边的离散轮廓和垂直面片；但三种着色在该同一输出的两种采样下都未产生报告中的黑片。该指标未做床面区域分割，但全图零计数意味着本次截图中不存在达到该阈值的像素。
- **区分性结论**：采样分辨率会改变可见网格形态；本对照不支持“分辨率降低”或“固定单色”单独足以在此输出中产生近黑片。它不能解释较早另一 proxy payload 上的阳性诊断，因为该 payload 的数据值和输出来源不同；不能将这些结果外推到用户原设备、真实原始数据或其他视角/VE。
- **状态**：黑片仍**未修复**，根因仍**不确定**。同一输出交叉对照的报告、图像与哈希见[分辨率/编码诊断包](../../../build/bed-black-resolution-control-20261025/README.md)。原始用户参考图继续为 `（待补充：参考图的具体路径或链接）`。

### 匹配度复核：历史截图包含三角显示网

- **实测（存档截图/诊断 trace 清单对照）**：存档截图 `erkens-black-bed-remains-20261023.png` 中选中温度表面上可见密集三角边网；此前同一 2020 frame19 的 headless `baseline.audit.json` 只有床面、水面、岸线、等深线、陆地和变量场等 7 条 trace，没有独立三角边/层间网 trace。因此日期/层号/相机/VE 匹配仍未覆盖截图中的全部显示状态。
- **影响**：该差异是尚未控制的显示状态，不是黑片根因结论。后续对照需打开 production mesh mode `triangles` 并记录实际 `inputTraces`/`_fullData`，再做视角、VE、图层单因素测试。黑片仍**未修复**、根因**不确定**；缺少的用户原始参考图仍为 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 Sol/Luna：床面播放补丁色标残留假设复核

- **源码检查（不构成黑片复现）**：曾怀疑 `viz3dWaterbodyRestyleGroups()` 的 bed 属性列表没有包含 `colorscale`，可能使播放中的床面沿用旧色标。追踪后确认播放补丁要求 `topologyKey` 相同，而 `playbackTopologyKey` 明确包含 `ve`；动态床面在 `VE<=80` 使用中性色标、`VE>80` 使用水深色标，跨该分支必然变更拓扑键并走完整 `Plotly.react`，不会复用该补丁。固定 VE 与诊断选项的帧播放中床面色标分支保持不变，水深上限变化时 `cmax` 已在补丁属性中更新。
- **结论**：本次检查**否定**“因该播放补丁遗漏 colorscale 而导致 VE 切换后黑片残留”这一特定假设；未发现同键生产帧会改变床面色标的证据，因此没有修改代码或添加针对该假设的测试。此结论只排除这条代码路径上的解释，不确认其他候选，也不构成修复证据。
- **状态**：黑片仍**未修复**，唯一根因仍**不确定**。本次没有运行或清理模型案例，没有操作桌面 APP。参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 Sol/Luna：frame19 三角显示模式匹配度对照

- **代理（headless Edge/SwiftShader 渲染，非科学验证）**：复用同一 Erken frame19、target 26、温度层 9 的只读 API 快照，保持水深、VE=166.5×、生产默认相机、轴范围、宽高比、896×760视口及其他显示条件一致，只切换 `meshMode`。当前生产路径的连续模式有7条 `_fullData` trace；三角模式有8条，其中多出生产三角显示剖分线 trace。近黑筛查阈值 `max(R,G,B)<40`：两种模式的中央 ROI 都为 0/383,966，全图均为 0/680,960。该指标是全图像素筛查，不是床面语义分割。
- **历史匹配边界**：仓库留存的 `erken-black-bed-flatshading-20261023.png` 显示三角显示网络与近黑床面，但没有记录当前 UI 的网格选择状态和相机坐标；当前对照使用的是代理输出及当前三角渲染实现，不能等同用户目标设备复现。报告记录了已知构造相机/轴/视口参数，并把它们与 `_fullData` trace 审计区分开。详见[`triangle mode compare`](../../../build/bed-black-frame19-triangle-mode-compare-20261025-02/README.md)及联系图。
- **结论/状态**：加入三角显示网络仍未在该代理帧复现黑片，因此不能解释或推翻历史现象，也不能证明已修复。黑片仍**未修复**，根因仍**不确定**；没有产品代码改动，没有启动/删除案例或操作桌面 APP。用户原始参考图位置继续为 `（待补充：参考图的具体路径或链接）`。

## 2026-10-25 Sol/Luna：三角模式对照控制条件纠正

既有 target26 对照及其相机/轴输入元数据补记保留为历史记录，但其“固定相机/轴/aspect”的匹配控制声明现为**无效并已被后续有效 target96 对照取代**：helper 的 JSON replacer 将嵌套 camera、轴范围、aspect 和 margin 对象/数组全变为 `null`，Plotly 实际使用回退场景。因此这些旧截图和 near-black 像素结果不支持之前声称的匹配条件结论。首轮 target96 默认相机对照同样作废但保留文件。

修正后的 target96 对照使用输入哈希 `85b2932d4149ff0e4b8e48667b374c072bf807dc2d46a879fafdf33c6e320a26`，回放审计哈希 `a433507f06b90694f5407cddff620b3157c432272eec010ccca8cd3fe8bf361c`；两模式构造输入中的 camera/axes/aspect/1410×905 viewport 非空且相同。真实 `_fullData` trace 为 continuous 7、triangles 8（含1条 triangle network trace），ROI 和全图阈值 `<40` 像素均为0。保存数据为 2020-DOY001 02:00，历史黑床图为同日 06:00，存在四小时差异；这是 SwiftShader headless 代理对照，不是用户设备复现。完整材料见 [triangle-mode comparison](../../../build/bed-black-frame19-triangle-mode-compare-20261025-02/README.md)。黑床仍未修复、唯一根因仍不确定。
- **精确产物指纹**：target96 输入 SHA-256 `85b2932d4149ff0e4b8e48667b374c072bf807dc2d46a879fafdf33c6e320a26`；回放审计 `a433507f06b90694f5407cddff620b3157c432272eec010ccca8cd3fe8bf361c`；序列化 viewport `{width:1410,height:905}` 哈希 `3bb89073abe82160994cfb07535c145a943c9177b005067b11eaae0352573fa9`；连续 PNG `f2fca12850620a928bec726831c48c3268d7403a1d9bb6ed7f5746b00dec57a4`；三角 PNG `6a4e28091de85d8179a19cb172c804bbf2f395d8c09c9780141877be6d937357`；并排 PNG `b0b7cf219a4bfafdcbcc95b5290cd5c7332e122a538033daf7a5fb223b271662`。

## 2026-10-25 Sol：退化面法线候选核对

- **代理（静态几何核算，非黑片复现）**：Plotly `mesh3d` 文档说明 `lighting.facenormalsepsilon` 默认值为 `1e-6`，用于避免退化几何下的面法线计算问题（[官方属性参考](https://plotly.com/python/reference/mesh3d/)）。床面构造代码按每个湿格的规则四角拆成两片三角面；对历史 18×44 frame19 床面 payload，中心坐标推导出的网格边长均为 250 m，376 个湿格对应752个三角形，每片水平投影面积均为31,250 m²。
- **区分结论**：这组网格没有零面积三角形，因此“面法线因零面积三角形退化”不是该 payload 的可支持解释；这不排除深度缓冲、投影、绘制顺序、其他网格/运行时 trace 或 GPU 差异，也不能外推为用户目标场景已被排除。
- **状态**：黑色床面片仍**未修复**，根因仍**不确定**。本次仅做已有 payload 的静态计算，没有修改源码、运行/清理案例或操作 APP。

### 2026-10-25 Sol：历史 v86 三角 winding 受控代理对照

- **代理（headless 渲染，不是用户设备实测）**：独立复核 `build/bed-black-winding-control-20261025-rerun-01/README.md`、`pair-comparison.json` 与输入/渲染器哈希。对同一 02:00 frame19 归档 v86 payload、相机、视口、Plotly 和 headless Edge/ANGLE 设备，仅交换床面每个三角形的 `i/j`；两组 `_fullData` 的其他显式床面属性一致。全场与 bed-only 两组 PNG 分别逐像素一致（各 0 像素变化），近黑像素计数相同。
- **结论边界**：该代理对照不支持“将全部床面三角形 winding 反转”作为此归档画面的有效控制，也不说明 Plotly 在所有状态下忽略 winding；其时间为 02:00，与归档用户黑片截图 06:00 不同，不能据此判断当前桌面场景或唯一根因。未改产品代码、未启动案例、未打开应用。
- **状态**：黑片仍**未修复**，根因仍**不确定**。继续需要原始 06:00 画面匹配的输入、完整 `_fullData`、几何/相机/垂向倍率与目标设备渲染证据；参考图仍为 `（待补充：参考图的具体路径或链接）`。

### 2026-10-25 Sol：既有 Erken 输出 06:00 只读载荷恢复

- **实测（既有文件只读 API 提取）**：从预先存在的 `build/real-use-validation-20261021/erken-real-location-24h/baseline/output/output.nc` 通过现有结果 API 提取索引 5（2020-01-01 06:00）、target96、原物理 layer 9 的温度/床面/拓扑载荷，写入 `build/bed-black-frame19-readonly-probe-20261025/frame06-2020-target96-layer9.json`。HTTP 测试客户端返回 200；载荷为 shape 1×18×44、原网格 10×18×44、stride 1×1×1、376 个湿单元，拓扑契约有效。未运行模型。
- **可比性边界**：本地历史 06:00 bed/坐标几何与存档目标相同，但现存 24h baseline 的温度范围约 2.1800–2.1836°C；历史阳性诊断载荷 02:00 范围约 8.3006–14.8710°C，且原始截图的完整场值未取得。因此即使帧时刻恢复，也仍非历史截图的完全同态输入，后续渲染只能标**代理**。
- **状态**：这是从已有模型输出的只读提取，不是新案例或完整科学验证；黑片仍**未修复**，根因仍**不确定**。参考图保留 `（待补充：参考图的具体路径或链接）`。
- **时间轴确认与指纹**：NetCDF `time[5]` 由 `seconds since 2020-01-01 00:00:00` 解码为 `2020-01-01 06:00:00`；现存输出 SHA-256 `63a96af290181df23d840c14d1aec969fc690f8aefad54ea529030991cd28187`，提取载荷 SHA-256 `fd251973feb8b53b3291f369ef1843d1a2fff678f690cff2b2998edbea290614`。

### 2026-10-25 Sol/Luna：06:00 既有输出的当前 renderer 对照

- **代理（headless 渲染，不是用户桌面实测）**：Sol 复核 Luna 的完整报告与联系图 [`frame06 current-render diagnostic`](../../../build/bed-black-current-render-frame06-20261025-02/README.md)。同一只读 06:00 payload、layer 9、target96、相机和1600×1000视口，当前 `viz3d.js` 分别渲染 (A) VE=200×静态床面、(B) VE=50× temp动态叠层、(C) VE=166.5× temp动态叠层。A/B/C均含床面1504顶点/752面；B含712顶点/356面边界墙，A/C不含墙；当前VE>80策略会省略动态墙。三条件全场 ROI 和整图 near-black（RGB max<40）均为0；逐 trace 的25次渲染筛查也均为0。
- **Sol 视觉复核**：contact sheet 的三张场景都未见历史截图那种下侧近黑面片；它们在颜色/视角上清楚可见与历史截图不同。SwiftShader 软件渲染和此载荷的温度场不等价用户设备/原始画面。
- **结论边界**：历史截图温度约8.30–14.87°C，此 payload 为2.18005–2.18363°C；原始相机参数也没有完整记录。该 06:00 时间和相同床形仍不足以构成原图复现，不能确认修复、反证原缺陷或锁定唯一根因。黑片**未修复**、根因**不确定**；参考图仍 `（待补充：参考图的具体路径或链接）`。
- **有效证据**：仅取 `build/bed-black-current-render-frame06-20261025-02/`；相邻 `-01`、`-03` 为 runner 调试失败尝试，已排除并保留，不作为结果。未改产品源码、未启动/删除案例、未开桌面应用。

### 2026-10-25 Sol：存档黑片截图时间标签更正

- **实测（图像标题复核）**：仓库内存在两组不同小时的黑片截图，不能将它们统称为单一 06:00 状态。`erkens-black-bed-remains-20261023.png`、`erken-black-bed-final-20261023.png` 与 `erken-black-bed-flatshading-20261023.png` 的画面标题均为 2020-DOY001 **02:00**、层9/9、VE166.5×；`erken-bed-color-range-before-20261023.png` 与 `erken-bed-color-range-after-20261023.png` 的标题为 **06:00**、层9/9、VE166.5×。两组图都可见黑色床面侧面。
- **交叉核对**：既有 frame19 target96 payload 为02:00，temp范围约8.3006–14.871°C，与02:00归档截图标注的temp范围相符。因此，先前称“target96与归档黑床图相差4小时”的记录只适用于06:00色标对照截图，不适用于02:00的 `erken-black-bed-remains/final/flatshading` 截图；该限制现予以精确限定。06:00新载荷来自另一份现存24h baseline，温度约2.18°C，仍不匹配06:00归档图。
- **结论与边界**：`bed-black-v86-replay-20261025` 在02:00 target96同一保存几何/相机下的 v86 代理渲染有近黑区，v123 代理渲染没有；两版本的床面显式颜色/着色属性同时变化，且这仍是 headless proxy，未从实际用户当前桌面取证。该结果不能改写用户已知的“黑片未修复”，也不能单独确认底层根因。参考图仍为 `（待补充：参考图的具体路径或链接）`。

## 2026-10-26 Sol/Luna：当前证据门槛复核

- **实测（证据审阅）**：Sol 高复核 Luna 中对当前 `viz3d.js` 与现有证据矩阵的独立审查。现有代理历史载荷显示 v86 旧渲染近黑像素、当前组合渲染为 0；但床面编码/照明属性在版本间同时变化。当前 06:00 载荷温度约 2.18°C，与黑片归档图约 8.30–14.87°C 不同，且缺原始完整相机设置。因此当前材料不构成对目标现场的单变量复现或修复验证。
- **实现决定**：Luna 未改源码。用不匹配输入增加/更改生产逻辑会是猜测，不能通过目标缺陷验收。黑片仍**未修复**，根因仍**不确定**；不把历史代理路径中消失的复现升级成目标用户场景修复。
- **待补证据**：原黑片场景对应的精确结果文件/帧、相同床面与字段载荷、运行时完整 Plotly `_fullData`（trace 顺序及属性）、相机与 viewport、垂向倍率、GPU/浏览器/Plotly 版本；随后对图层、相机、倍率和 trace 属性分别作单变量对照。参考图仍为 `（待补充：参考图的具体路径或链接）`。
- **操作边界**：本次无源码改动、未运行/删除案例、未打开桌面 APP；因此没有桌面同步动作。

## 2026-10-26 Sol：历史 v86 单变量强度属性隔离

- **代理（受控历史渲染）**：以 `bed-black-v86-replay-20261025/old_v86_baseline.audit.json` 为输入，用相同历史 payload、bed-only trace、几何、相机、viewport、Plotly 2.35.2 与 ANGLE/NVIDIA RTX 4070 renderer，基线与变体仅差一项：给 v86 bed trace 增加 `intensity = customdata`（1504 个逐顶点水深值）。ROI `(180,280)-(1240,820)` 共 572,400 像素；近黑阈值 `max(R,G,B)<40` 从 **245,173** 降至 **0**，湖盆可见。
- **对照**：历史已存的“仅把 bed 颜色改绿”和“仅把光照改为 ambient=1/diffuse=0”均仍为 245,173 个近黑像素。这次强度变体显示的是暖色自动色标，与 v123 蓝色显式深度色标不同，说明 Plotly 在增加 intensity 后也走入颜色映射路径。
- **判断**：在该历史代理复现中，显式 vertex intensity 是消除黑片的**充分候选条件**；这把调查从“整体版本差异”缩小到强度/色标计算路径。由于 `intensity` 触发 Plotly 自动色标，且没有目标用户设备、当前桌面相同帧的完整运行时 trace 和 GPU 对照，因此不能断言是唯一根因，也不能据此把桌面缺陷状态改为已修复。候选仍包括显式/隐式强度映射与 Plotly/WebGL交互；视角、底图层、垂向倍率仍需按目标场景单变量核验。
- **产物**：`build/bed-black-intensity-isolation-run-20261026/old_v86_bed_explicit_intensity.png`、`old_v86_bed_explicit_intensity.audit.json`、`summary.json`；唯一产品未变更。无模型案例被创建/删除。
- **当前产品源码对照**：当前 `viz3d.js` 的床面 trace 已使用 `geometry.floor.intensity`、`intensitymode:'vertex'` 与显式 `VIZ3D.depthScale`。现有当前 v123 历史回放无近黑像素，但这仍是代理；需拿目标现场同帧输入确认该路径被加载且在目标桌面上有效。黑片状态继续为**未修复**，根因继续为**不确定**；参考图保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-27 Sol：当前渲染源码缓存路径审查

- **实测（源码审查，不是运行时渲染）**：`lakeGeometryForFrame()` 的 exact geometry cache key 包含 `xc`、`yc`、当前帧 `bottom` 数组内容、`ve` 与 `displayTopology`；缓存命中会更新 LRU 次序，但不同坐标/床面数值/倍率/拓扑的内容不会共用该 geometry entry。`lakeStaticTraceKey()` 还包含案例路径/名称、case revision、output revision、static geometry key、playback wet/valid topology、变量、显示选项等身份。
- **排除范围**：因此，当前源码中的简单“几何缓存忽略帧床深或 VE，跨帧返回旧床面几何”假设不受支持。此审查不能排除 Plotly/WebGL 在 `react` 更新时的内部状态、运行时 `_fullData` 与源 trace 的差异、非当前版本代码、遮挡或几何投影交互。
- **状态与下一步**：黑片仍**未修复**，唯一根因仍**不确定**。区分上述剩余解释仍需要目标黑片现场的同帧输入与 `_fullData`、trace 顺序、相机/viewport、Plotly/GPU 身份，再做单变量复现；参考图路径保留 `（待补充：参考图的具体路径或链接）`。本次没有改代码、打开应用、运行或清理案例。

## 2026-10-26 Sol：当前源码服务同步复核

- **本地源码服务同步：实测**。确认旧进程 idle 后结束，并从工作区以 `launcher.py --web --no-open --port 52812` 重启；新 PID 77112。`/api/run/status` 返回 idle，首页引用 `app.js?v=74`、`i18n.js?v=17`、`viz3d.js?v=123`；HTTP 返回的三个资源与工作区文件内容一致。未打开新窗口。
- **重复结果扫描：实测（只读 API）**。对既有隔离 Erken 案例清单调用 `/api/results/files/duplicates` 用时 20 ms，返回 0 个重复路径；没有清理或改写案例文件。这只证明 idle 下 API 正常，不解释此前 90 秒 UI pending，也不验收 UI 按钮完整流程。
- **历史截图几何归属：不确定**。仓库历史截图显示暗色几何位于水平湖面/地形平面下方；截图并非用户后来承诺提供的参考图。仅凭截图不能可靠归属到床面、边界剖面或其他绘制 trace。
- **桌面 UI 启动烟测：实测通过；持久桌面窗口验收：未完成**。`build/ui-smoke-current-source-20261026.json` 记录 EdgeChromium `ready_state=complete`、bridge/layout/health/language ready、模型状态 idle；烟测窗口自动关闭。随后已恢复 52812 无界面源码服务（PID 84156），再次确认状态 idle、首页资源版本正确且 `app.js`/`i18n.js`/`viz3d.js` HTTP 内容逐字匹配工作区。烟测只验证应用壳，不验证用户原有桌面窗口已刷新，也不验证湖面渲染或黑片。
- 黑片继续为**未修复**，根因继续为**不确定**；参考图路径保留 `（待补充：参考图的具体路径或链接）`。

## 2026-10-26 Sol：修复 06:00 headless 报告并复核

- **代理（headless renderer）**：Luna 修复诊断脚本末尾误从浏览器上下文读取 Python 局部变量而报 `ReferenceError: fixture is not defined` 的报告错误。修复前 browser 已写出部分三场景截图，但无汇总报告；修复后重跑成功，`renderer-report.json` 包含 A/B/C 全部场景。
- **同载荷三条件**：frame06 `2020-01-01 06:00`、`temp`、target96、layer9、shape `[1,18,44]`、376 个 wet cells，输入 SHA-256 `fd251973feb8b53b3291f369ef1843d1a2fff678f690cff2b2998edbea290614`；current `viz3d.js` SHA-256 `06fcca575190f05ab85f6e80130b42518e1c619504dff96ac2381b2b1eab0cb7`。静态床面 200×、变量叠层 50×、变量叠层 166.5×均固定诊断相机、1600×1000 viewport、triangle display mode。全图及 ROI（899,840 像素）`max(R,G,B)<20` 与 `<40` 数量均为 0；单独床面 trace 的 ROI `<40` 也均为 0。
- **判断边界**：同一时间标签和网格形状不代表与历史截图浏览器 `_fullData`、变量场、viewport、设备/GPU完全相同；此结果支持“当前源码在这份 06:00 代理输入的三种显示条件下不产生阈值近黑像素”，不等于用户桌面缺陷已修复，也不能确认唯一根因。黑片继续标记**未修复**、根因**不确定**。
- 报告与图像见 [frame06 headless diagnostic](../../../build/bed-black-current-render-frame06-20261025-03/README.md)。未运行或清理案例；未修改产品渲染源码；未打开应用窗口。

## 2026-10-27 Sol/Luna：床面当前渲染链路复审

- **源码审查（实测）**：Luna 检查了 `buildLakeGeometry()`、`lakeGeometryForFrame()`、`lakeTraces()`、静态 trace cache key，以及床面、墙面、岸线和采样拓扑的组装关系。当前床面 trace 用顶点深度 intensity 与显式深度色标；几何 key 包含坐标、当前床深、垂向倍率和显示拓扑。没有发现忽略当前帧床深/VE 的同键缓存错误，也没有同一输入下可复现的当前生产代码阳性缺陷。
- **现有反例仍成立**：隐藏床面 trace 时历史黑片消失，床面单 trace 强制纯绿仍曾黑；静态 bathymetry 与动态 overlay 路径历史表现不同；当前 frame06 headless 三种条件均无阈值近黑像素。由此只能确认多因素/渲染路径候选，不能定唯一根因。
- **Sol 结论**：本次遵循 systematic-debugging 的“未定位根因不打补丁”，没有改源码。黑色床面片仍**未修复**，根因仍**不确定**。下一次有效区分须在目标黑片出现时保存同次帧输入、Plotly 源 trace 与 `_fullData`/绘制顺序、相机投影/视口、图层/VE、浏览器/Plotly/GPU 信息，再逐项切换床面、墙面、岸线和颜色属性。参考图继续为 `（待补充：参考图的具体路径或链接）`。
- **本轮边界**：未运行/清理模型案例，未打开/刷新/启动 APP；无产品代码改动，无桌面同步动作。

## 2026-10-27 Sol：v86 黑片代理的颜色属性交叉实验

- **代理（headless，不是用户桌面实测）**：在相同的 2020-DOY001 02:00 历史 payload、几何、Plotly 2.35.2、相机、1440×1000 视口和 RTX 4070 D3D11 渲染环境下，分别对 v86 的单床面 trace 单独替换当前色标、单独替换当前照明、同时替换两项。三组图仍可见同一块黑色床面；仅单独补入 `intensity=customdata` 的旧床面变为非黑。当前 v123 的单床面 trace 自带顶点 intensity，也未出现阈值近黑像素。
- **变量—现象关系（限该代理）**：在此存档阳性代理里，单独改变床面色标或照明未消除黑片；补入 intensity 后黑色消失。它让“trace 缺少可用 intensity/颜色映射输入”成为值得在现场验证的候选，但版本间仍同时存在其他 trace 属性变化；缺少用户当前桌面的 `_fullData` 和原始截图输入，无法确认现场是否具有同一条件，也不能据此宣布已修复或唯一根因。
- **可区分方式**：在黑片现场保存同一帧的原始 `data`、Plotly `_fullData`、trace 顺序、几何、相机/投影、VE、视口和设备信息；只补/移除 intensity 做 A/B；另分别替换色标与照明。若仅 intensity 开关能稳定改变目标黑片，才可支持该机制；若现场 trace 已有有效 intensity，应继续查渲染叠层/深度与几何面片路径。
- **产物**：`build/bed-black-crossed-controls-20261027/summary.json` 和各组 PNG/audit JSON。旧版本控制组产生黑面、当前版本组未产生；本实验未改产品源码、未运行或清理科学案例、未打开 3DWET Studio。
- **状态**：黑色床面片缺陷仍**未修复**；根因仍**不确定**；此交叉实验为**代理**。参考图位置仍为 `（待补充：参考图的具体路径或链接）`。

## 2026-10-26 Sol：当前 v128 源码重放与单属性区分

- **代理（headless renderer）**：以同一历史 frame19 阳性载荷、几何哈希 `df24c9d915aa0968a12f727935274fe890e58451f359ef24814a905587a7f013`、正交相机、1440×1000 视口、Plotly 2.35.2 和 ANGLE/RTX 4070 D3D11 渲染器，对比历史 v86 与当前 v128。固定 ROI `<RGB 40` 计数为：v86 床面单 trace 245,173/572,400，v86 全场 75,471/572,400；当前 v128 床面单 trace 和全场均为 0。原 v86 trace 单独补 `intensity=customdata` 后为 0；只改 direct color、色带或照明均仍为 245,173。
- **结论边界**：对该历史代理而言，intensity/颜色映射输入是目前最有区分度的渲染路径候选；当前 v128 组合路径没有重现该代理黑片。它不证明用户桌面场景已修复，也不锁定 Plotly/WebGL 底层唯一根因。历史参考图路径仍 `（待补充：参考图的具体路径或链接）`。
- **源码同步状态**：工作区模板引用 v128，但 52812 无窗口服务响应仍引用 v124 的模板；静态文件响应哈希与工作区相同，原生桌面端口 64257 无监听。对已核验服务的重启被本机策略拒绝。未打开或另启桌面窗口。
- 复现脚本、PNG、审计 JSON、逐像素计数与限制见 [`current v128 proxy replay`](../../../build/bed-black-current-v128-proxy-20261026/README.md)。黑片仍**未修复**，根因仍**不确定**。
