# Sol review: black bed patches and workbench design

Date: 2026-10-24 (Asia/Shanghai)

## 1. Bed rendering evidence and hypotheses

### Status

**Black bed patch: unresolved and not repaired. Root cause: uncertain.** The user reported that the current browser comparison did not reproduce the patch and instructed us to preserve the unresolved status. Earlier browser comparisons did reproduce it under some settings. Neither the negative current comparison nor the diagnostic-only display mode counts as a production fix.

### Observed variable-to-phenomenon relationship

| Variable | Recorded browser observations | What the observation supports | What it does not establish |
|---|---|---|---|
| Bed layer / rendering path | Earlier browser checks found that hiding the bed mesh removed the black patch, while hiding shore/land alone did not. A later forced-bed diagnostic view showed black/white anomalies; changing its fill color path changed the appearance. Current static bathymetry at 200× and an overlay view at 50× did not show an obvious patch. | The symptom is associated with the bed trace; fill path may affect its appearance. | It does not identify which trace attribute or renderer behavior is responsible; diagnostic paths are not the normal user path or a production repair. |
| View / camera | The issue is reported to vary with viewing angle. A diagnostic observation used a 34° elevation; other comparisons did not isolate camera while holding all other rendering inputs fixed. | View dependence remains a relevant factor to test. | Camera angle as an independent cause is not established. |
| Vertical exaggeration (VE) | Historical comparison: 1×/50× did not show an obvious patch; 100× showed a lower-edge black patch, and automatic ~166.4× showed it clearly. Current-version frame 19 at 200× static bathymetry, 50× overlay and frame 3 at 50× did not reproduce it. High-VE dynamic temperature paths can suppress bed fill. | There is a recorded association between VE and the symptom in some combinations. | VE alone cannot explain all comparisons; suppression is not repair evidence. |

These observations are conditional and span different frames, view states, overlays, lake traces, and diagnostic modes. A full controlled comparison has not yet isolated each variable. Preserve the original source records in `docs/audit/user-journey-20261021/STATUS.md`.

### Additional primary-source review of the rendering candidates

The [Plotly Mesh3d reference](https://plotly.com/python/reference/mesh3d/) distinguishes `color` (one color for the whole mesh) from `intensity` plus `colorscale` (vertex- or cell-valued colors), and says `flatshading` controls normal smoothing. This makes a same-geometry direct-color versus uniform-colorscale comparison useful, but it does **not** imply that either encoding is safer or is the cause here. A historical [Plotly.js Mesh3d issue on hardware-dependent dark rendering](https://github.com/plotly/plotly.js/issues/1368) discusses GPU variation and normal-calculation precision as possible contributors. It is a precedent for keeping renderer/hardware and normal behavior among the hypotheses, not evidence that this lake trace has the same bug or that the issue applies to bundled Plotly 2.35.2.

The current production trace has `flatshading:false`, absolute projected X/Y coordinates, bathymetry-derived Z scaled by VE, and ambient-only lighting. Required discriminating evidence remains an ordinary-user-path reproduction plus same-frame, same-camera, same-VE floor/wall/land captures and the serialized mesh attributes/indices; a direct-color diagnostic alone cannot establish cause.

### Candidate causes and discriminating evidence

All entries below are **hypotheses**, not root-cause claims.

| Candidate hypothesis | Evidence that would distinguish it | Minimum controlled check |
|---|---|---|
| Bed/shore/wall/land depth overlap or occlusion | Actual visible trace order, depth-test behavior, and per-trace geometry/color data | Reproduce the patch at a fixed frame/view/VE; capture a screenshot and Plotly trace names, coordinates, indices, colors, and visibility; suppress floor, wall, and land one at a time, not together. |
| Bed mesh topology, winding, or face-normal issue | Triangle indices, signed orientation, normal/material behavior and whether the artifact follows specific cells/faces | Use the same mesh and camera with per-cell IDs or wireframe, inspect triangle winding and normals, then change one face/material setting at a time. |
| Vertex color interpolation or depth/color data | Bed vertex values versus rendered face colors; flat versus interpolated coloring | Hold geometry and camera fixed; compare flat face colors to interpolated vertex colors and inspect values for the affected faces. |
| Vertical span / camera depth precision interaction | Artifact appears only for a particular view-distance / Z-span combination, independently of color and mesh topology | Sweep VE and camera distance/elevation as a small factorial matrix, while holding frame, overlay, traces, and geometry fixed; record both the far/near clip ranges and actual Z coordinates. |

**Required evidence before production repair:** a repeatable current-version user-path reproduction, screenshot, frozen frame/overlay/camera/VE, and runtime floor/wall/land trace data. The user reference image remains `（待补充：参考图的具体路径或链接）`.

## 2. Design references reviewed by Sol

The user requested globally respected design references. There is no objective, verified ranking of “the best” companies or models, so these are cited as established primary design-system guidance rather than as a league table.

| Source | Adopted guidance | Why it fits this product |
|---|---|---|
| [Apple UI Design Dos and Don’ts](https://developer.apple.com/design/tips/) | Keep controls close to the content they modify; organize and align content so relationships are clear. | The 2D/3D result canvas should remain primary, with playback, view and variable controls adjacent to it. |
| [Figma design-system foundations](https://help.figma.com/hc/en-us/articles/14552740206743-Lesson-2-Define-your-design-system) | Treat accessibility, semantic color, typography, icon sizing, and spatial rules as shared foundations; do not rely on color alone for state. | Scientific evidence status and validation warnings need consistent tokens, legible labels, and text/icons as well as color. |
| [U.S. Web Design System design principles](https://designsystem.digital.gov/design-principles/) | Start with real needs, earn trust, support accessibility, and maintain continuity across a user journey. | The workbench has a multistep case workflow and must show when evidence is measured, proxy, missing, or unvalidated. |
| [USWDS data visualization guidance](https://designsystem.digital.gov/components/data-visualizations/) | Prefer understandable, focused visualizations; simplify color and treat usability and accessibility together. | The model’s scientific colormap carries data meaning; interface chrome should use restrained accents and avoid competing saturation. |

## 3. Art direction and trade-offs

The user approved the recommended direction: a light scientific workbench with a warm-white/cool-gray foundation, restrained blue-green accents, high-contrast typography, semantic status colors, and a canvas-first layout. Navigation groups case/data, configuration, and run/review. A contextual inspector supports variable selection, foodweb editing, diagnostics, and selected-object details. The foodweb topology stays synchronized with a direct relationship editor and validation evidence.

As art director, the central trade-off is to make dense science readable without turning the interface into a generic card dashboard. Let data plots and maps carry the saturated color; keep product chrome calm. Use spacing, type, section hierarchy, and consistent controls instead of gradients or oversized marketing type. Prefer progressive disclosure for advanced parameters while keeping units, defaults, provenance, and validation messages visible when needed. Maintain non-color status cues and keyboard focus.

Reference image: `（待补充：参考图的具体路径或链接）`.

## 4. Implementation and acceptance boundary

The approved design direction is recorded in `docs/superpowers/specs/2026-10-24-scientific-workbench-ui-design.md`. Luna implemented the consumer selector synchronized with the module selector, a per-group restore action for unsaved prey edits, visible field/unit labels, and teal/amber workbench accents. Focused foodweb/network/filter/instance/theme UI checks, JavaScript syntax, and the focused Python contract passed (1 passed, 18 deselected). These checks establish editor behavior only; they do not validate solver registrations, runtime feeding fluxes, or ecological correctness.

Desktop synchronization check: the old `3DWET Studio` window was closed through its normal window event while the model state was idle, then relaunched from the repository launcher. The current native window title is `3DWET Studio`; the local service at `http://127.0.0.1:8768` reports idle, with its active case path in the repository. The HTML response still references `ecology_network.js?v=24` and `studio.css?v=4`, while the checked-in template says v26/v5. Requesting those older asset URLs returns bytes whose SHA-256 matches the current local JS and CSS sources. Windows UI Automation separately confirmed that the native app renders the ecology/network page and its updated interactions. The HTML cache-busting reference discrepancy remains a synchronization detail to resolve or explain.

Sol independently reran the five focused Node UI checks, the foodweb JavaScript syntax check, and the Python clone UI contract; all passed (Python: 1 passed, 18 deselected). The Python contract is at repository root `tests/test_ecology_network.py`.

The full user journey and the scientific validation of Erken, Lake Ravn, Bryrup, and Arreskov remain **未完成** according to the current audit ledger. Proxy runs and engineering smoke tests must retain their **代理** label.

### Supplemental isolation-fixture observation (2026-10-24)

- **实测（诊断页面渲染行为）**: Sol opened the read-only static fixture `build/real-use-validation/20261023/erken-june2024-competition-luna-attempt03/bed-black-render-repro/` at `time=167 / target=26` and visually inspected the production-like baseline, VE=1, data-aspect, centered X/Y, neutral bed color, and the floor-only and walls-only states. No black patch was visible in these fixture panels. The data describe 22×18 sampled cells / 185 wet cells and are from the exploratory `luna-attempt03` output.
- **代理（科学证据）**: The underlying Erken output is still an engineering/exploratory model result; this render-only fixture does not validate Erken science and is not the reported frame19 state.
- **Uncertainty**: The observation does not adjudicate the reported frame19 behavior. Panel F is an explicit isolation tool that can force-show wet-grid walls, while the current production high-VE path omits those walls; a positive/negative result in F does not establish normal-path trace behavior. No root cause or production fix is established. The current mismatch between the user-reported frame19 state and the available time167 fixture remains **不确定**; black bed patch remains **未修复**.
- **Next discriminating evidence**: capture the ordinary-path frame19 3D API response and screenshot for static bathymetry and overlay under the same recorded camera and VE; include `Plotly._fullData` trace visibility, bed geometry/indices, intensity/color attributes, and axis/camera ranges. Change one trace or one rendering attribute at a time. Reference image remains `（待补充：参考图的具体路径或链接）`.

### Additional native UI acceptance evidence (2026-10-24)

- **实测（desktop UI behavior only）**: `3DWET Studio` window was present and rendered the ecology/network page. The consumer selector showed `cladocerans · wet/zooplankton`; the user-facing group label and `m3/gDW/d` clearance-rate unit were visible.
- **实测（desktop UI behavior only）**: “还原此组未保存编辑” restored the displayed prey-row count to four after a transient local edit. No save was issued and no scientific configuration was changed.
- **未完成**: no conclusion about actual model feeding, runtime port registration, ecological validity, the bed-rendering defect, or end-to-end workflow follows from this interaction.

### Current workbench source preview and desktop sync recheck (2026-10-24)

- **实测（隔离源码预览的 UI 行为）**: Started an isolated 3DWET service from the current workspace source using a temporary empty model root at `http://127.0.0.1:8769`. The rendered page includes the new canvas-first dashboard, grouped case/configuration/run navigation, and workbench inspector. The 2D and 3D workspaces show the existing variable, layer, camera, and display controls; both inspector and display-settings toggles collapsed and expanded successfully. This preview does not use a scientific case and does not establish scientific or native-desktop acceptance. The temporary service was stopped after inspection.
- **实测（source checks）**: `node --test 3DWET/tests/test_workbench_shell.js 3DWET/tests/test_parameter_module_loading.js` passed (2/2); `node --check` passed for `app.js` and `scientific_workspace.js`. The source template references `workbench.css?v=2`, `scientific_workspace.js?v=17`, and `app.js?v=68`.
- **未完成（native desktop sync）**: The existing desktop service at port 60336 remains the 2026-10-24 15:14 instance (PID 25832) and returns its cached old dashboard: no `dashboard-canvas` or `workbench.css`, and `app.js?v=65`. Its served `app.js?v=68` asset bytes match the current disk source hash, but that does not refresh the cached homepage template. A normal desktop close/reopen after the final template changes is still required to verify native synchronization.
- **未完成（black bed defect）**: The isolated preview has no case or bathymetry and cannot reproduce the bed artifact. Current evidence remains as recorded above: diagnostic neutral-color behavior and negative ordinary comparisons do not identify a unique root cause or demonstrate a production fix. Keep cause **不确定** and defect **未修复** pending a repeatable normal-path case/frame/camera/VE capture with screenshot and runtime trace attributes.
- **实测（Erken browser-render negative comparison, not scientific validation）**: On the existing 60336 service, the active `luna-attempt03` Erken exploration output was viewed at `temp`, frame 19, oblique camera 34°, continuous mesh, with the land plane visible. At automatic 166.4× overlay, 200× overlay, 200× static bathymetry (overlay disabled), and 50× overlay, no clear large black bed patch was visible in the captured browser viewport. The 3D render identifies the source grid as 10×18×44 with 376 valid water cells. The model output remains **代理** for scientific status; only visual rendering behavior was **实测**. This negative comparison is conditional and does not demonstrate a fix. Together with the prior diagnostic-only reproduction, it keeps the bed trace/color path, mesh/material interaction, camera, and vertical-scale interaction as candidates; a unique root cause remains **不确定**.
- The user reference image remains `（待补充：参考图的具体路径或链接）`. Case science and complete journey statuses remain unchanged from `docs/audit/user-journey-20261021/STATUS.md`.

### Final desktop reload verification (2026-10-24)

- **实测（native desktop source synchronization）**: Closed the stale `3DWET Studio` window through its normal close control while the UI showed idle. Its old service at port 60336 stopped. Relaunched `3DWET/app/launcher.py --desktop` from the repository workspace; the new native process started at 15:47 and its service at port 64509 reports ready for model root `C:\Users\23801\Desktop\GETM-FABM-WET-260928\3DWET` (PID 90964).
- **实测（served source version）**: The new homepage returns HTTP 200 and references `app.js?v=68`, `workbench.css`, and `scientific_workspace.js?v=17`; it does not reference `app.js?v=65`. The visible native window shows the canvas-first “湖泊模型工作台” dashboard, grouped “案例与数据” navigation, spatial preview, and workbench inspector. This confirms current source is loaded in the desktop app.
- **未完成（black bed defect / scientific validation / full workflow）**: This sync check is UI/version evidence only. It neither reproduces nor repairs the black bed patch, and it does not change the proxy/science status of Erken or any other case. Root cause remains **不确定**; defect remains **未修复**. The full workflow and scientific validation statuses stay as listed in `docs/audit/user-journey-20261021/STATUS.md`.

### Native workbench Erken 3D recheck (2026-10-24)

- **实测（rendering only）**: In the newly synchronized native workbench (service port64509, home v68), used the toolbar to enter the 3D result page for the active Erken attempt03 arm_A output. The page showed `temp`, frame 19 (2024-DOY166 09:00), camera elevation 34°, continuous waterbody, VE 200×. No obvious large black bed patch appeared in the captured overlay view.
- **Unresolved**: This was the dynamic waterbody overlay, not static bathymetry with the selected-variable water surface disabled. It is a conditional negative render observation, not a repair or scientific validation; historical black patches under other views/settings remain relevant. Defect **未修复**; unique root cause **不确定**. Static bathymetry A/B screenshot and reference image path remain `（待补充：…）`.

### Native frame19 static-bed / 50× overlay negative comparison (2026-10-24)

- **实测 (render behavior only)**: On the native service at port64509, active Erken attempt03 arm_A, `temp`, frame19 (2024-DOY166 09:00), 34° camera, selected 200× and unchecked “water surface shows selected variable”; the current UI path called `renderBathymetry3D` and showed static bathymetry. No obvious large black bed patch appeared in the screenshot. Re-enabled the selected-variable overlay and selected 50×; the normal waterbody overlay also showed no obvious large black patch.
- **Limit**: The two states vary layer and VE together, so this does not isolate either variable. This conditional negative comparison neither overturns prior reproductions nor proves a fix. Bed defect remains **未修复**, root cause **不确定**; the Erken attempt03 model result remains **代理** for scientific validation. Continue with a reproducible state and one-trace-at-a-time floor/wall/land captures plus trace geometry/color/index evidence. Reference image stays `（待补充：参考图的具体路径或链接）`.

### Desktop synchronization recheck (2026-10-25)

- **实测（desktop runtime/UI）**: Launched a new repository `3DWET Studio` WebView process after confirming the existing model run was idle. The launcher reused the already-published service for the same model root at `http://127.0.0.1:61310` rather than binding requested port 64257; no listener existed at 64257. The new native window (identified by its newly started process/window handle) visibly rendered the current canvas-first workbench.
- **实测（served source version）**: `/` returned HTTP 200 and references `workbench.css?v=3`, `scientific_workspace.js?v=17`, `i18n.js?v=14`, `app.js?v=71`, and `ecology_network.js?v=28`. The served `ecology_network.js` SHA-256 exactly matches the workspace source (`FA73A99F5DBB46473829575ADB20612D2941EAB480BD269F7E7A9EC620E4BCEA`); `/api/system/health` reports ready and the expected repository model root. The screenshot showed Lake Dianchi as the active desktop case; this is a UI/source synchronization check, not a scientific case validation.
- **未完成（complete user flow and case science）**: This confirms the newly opened window is on current workbench source, but does not complete the full user journey or validate any of the four named lake cases.
