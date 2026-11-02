# v92 browser playback, view and user-flow acceptance notes

Date: 2026-10-23 (Asia/Shanghai). Browser: local service `http://127.0.0.1:8766/`, active isolated case `build/real-use-validation-20261023/user-journey-Erken-baseline`. This was an actual local browser observation, not a source-code inference.

## Follow-up: raw CSV import and latest desktop build

After the generator fix in `3DWET/app/server.py`, a fresh isolated case `build/real-use-validation-20261023/user-journey-Erken-import` was populated through the browser CSV upload UI. The app parsed 27 hourly records, generated meteorology, built a two-hour setup, passed preflight, and ran 3,600 steps. The model completed in 44.1 seconds (80.7 steps/s); output validity passed and 20 actual output frames were available. This closes the earlier raw-CSV-upload gap for the import → build → preflight → run segment. The input provenance still labels the first 25 SITES-derived Erken records separately from two terminal padding records; `tcc=0.5`, zero evaporation, absent river flow and most ecological initial fields remain proxy/default assumptions.

In the same fresh case, the browser displayed the 2D output and actual playback advanced frames 0→2 at 1 fps (3 successful frames, P95 22 ms, no over-budget draw or target-interval violation). In 3D, the model position slider was set to +15, then playback advanced from frame 0 to frame 8 at a 4 fps target while the slider remained at +15. The completed playback status showed all 20 frames successful at 4.0 fps, P50/P95 whole-frame times 47/67 ms, 0/20 draws over budget, and zero frame intervals over target by more than 10%. This is a short 20-frame acceptance run, not a long-duration soak. The black underside polygons remained visible in the 3D plot and are still unresolved.

After viewing the imported-case run and moving the 3D model to +15%, the browser instance editor cloned cyanobacteria twice into `erken_workflow_algae` and `erken_added_algae_20261023_a1`, using equal-total split mode. The UI confirmed the second clone and noted that consumers' diet references were left unchanged; the configured 17 diet edges remained traceable and no new prey edge was invented. Both clones were present in `fabm.yaml` and in the result-variable selector. The case was rerun for 3,600 steps; it completed in 195.7 seconds at 18.3 steps/s, passed output validity, and archived 2D, 3D and NetCDF results. The result-analysis page extracted `erken_added_algae_20261023_a1_sDW` and rendered a time-series chart. The 3D playback was then run on this new output: 20/20 frames succeeded at a 4 fps target and actual rate, whole-frame P50/P95 50/68 ms, 0/20 over budget, zero target-interval violations; the model position remained +15% through the last frame. Thus the single-session engineering path—CSV import → setup/run → inspect dynamic results → adjust view → add algae → rerun → analyze the new output—is now **passed**. It does not establish biological validity or that the clones are distinct species/trait cohorts.

The imported case's food-web panel was opened before the clones: it reported 20 FABM instances, 358 explicit coupling ports, 17 parsed diet references, zero unresolved references, zero unconfigured diet ports, and zero closed three-node directed cycles. After adding two clones, the UI listed five algae instances (three originals plus two clones), retained 17 configured diet references, and showed the same explicit prey/consumer/port edges; hence 22 instances total by adding the two to the initial count. These are configured references, not proof of runtime trophic behavior.

The source fix changed generated integral `time_step` values from YAML decimal text (for example `360.0`, rejected by the solver) to integer text (`360`); a regression test covers integral and non-integral output intervals. Sol reran `python -m pytest tests/test_initial_conditions_rebuild.py -q`: 18 passed. The desktop application was restarted after this source change. Final desktop check: health endpoint reported model root `3DWET`, PID 78560, instance `7630e040d730458c8a2bcf3ec1b5d054`; process window title was “3DWET Studio”. HTTP 200 served `viz3d.js` SHA-256 matched the local source exactly: `BEDCC8128D45E7AB2DF05466410D7A36AD0A32BCC59CD6959B4B379C2C6CFE48`.

## Animation and camera

- The case produced 24 hourly output frames from 2020-DOY001 01:00 through 2020-DOY002 00:00. At a 4 fps target, 3D playback reached frame 23/23 with 24 successful frames, actual 4.0 fps, whole-frame P50/P95 51/93 ms, 0/24 over the one-second draw budget, and zero frame intervals more than 10% over target. 2D playback also reached the last frame with 24 successful frames at actual 4.0 fps, P50/P95 3/4 ms and 0/24 over budget.
- The independent “模型上下位置” control was observed at +15%; changing it to −15% visibly moved the lake in the opposite direction. After restoring +15%, moving from frame 23 to frame 22 kept the control at +15% and retained the translated view. Camera elevation was 34° during this observation.
- The 3D plot visibly retains large black underside polygons. They remain an unresolved rendering defect; no fix is claimed. Earlier observation also found that toggling the illustrative land layer did not remove the dark underside. This note preserves the visual finding without attributing it to a specific mesh trace.

## Display network and food web

- The display modes observed in the running 3D page were continuous water, orthogonal display grid, derived triangle display grid, and hidden grid. The panel exposed cell spacing, line opacity, and optional network nodes. Changing spacing from 1 to 2 changed the rendered display summary from 376 wet quads / 752 triangles / 1,217 edges to 90 / 180 / 669; spacing was restored to 1 afterward. These are display-only subdivisions of the structured GETM grid.
- The case food-web page listed 21 enabled FABM instances, 398 coupling ports, and 17 resolved diet references. Its expandable table showed prey instance, consumer instance, exact YAML port, and parse status for every edge. It reported zero unresolved references, zero unconfigured diet ports, and zero closed three-node cycles. The added `cyanobacteria_workflow` instance was not automatically given any prey relation; the graph did not invent one.

## User-flow copy and result analysis

- A disposable copy was saved from the existing Erken 2020 case. A second cyanobacteria instance was added through the food-web editor using equal-total split mode. Browser preflight reported zero reminders, then the app launched and completed a 24-hour, 17,280-step run in 226.1 seconds. The app log showed the finite-value check passing and archived 2D, 3D and NetCDF outputs.
- The input meteorology was SITES Erken first-day forcing already present in the case. To satisfy the app's coverage guard, the isolated copy's `meteo.nc` was extended for another 24 hours by holding the last input record constant; provenance labels these 24 added records as non-observational boundary padding. The case also used `tcc=0.5` as a longwave cloud proxy, zero evaporation, no river inputs and default/proxy values for most ecology and nutrient initial fields. This run demonstrates the app workflow and result viewer, not an Erken validation.
- In the result time-series page, the user extracted the new cyanobacteria instance's whole-lake mean. The displayed curve decreased from about 0.150 to 0.145 gDW/m³ during the first day. This is a descriptive result from the isolated run, not a normal-range or ecological-acceptance judgment.
- **Historical status at this observation: partial.** Case selection, module addition, preflight, model execution, playback, camera adjustment, and result analysis were observed in the browser, but that particular run had a duplicate-date draft and no successful raw CSV upload. The follow-up above later completed the full single-session path on the imported copy.

## Desktop/source synchronization

- At the earlier v92 observation, the desktop window was explicitly launched and its window title was observed as “3DWET Studio”. Its service `/api/system/health` was ready with model root `3DWET` and PID 77472; the follow-up synchronization after the server.py fix is documented above.
- The browser loaded `/static/js/viz3d.js?v=92`. Its served bytes matched `3DWET/app/static/js/viz3d.js` exactly, SHA-256 `BEDCC8128D45E7AB2DF05466410D7A36AD0A32BCC59CD6959B4B379C2C6CFE48`. The desktop launcher reused that ready service. The application window was running when checked.

## Remaining

- Fix and recheck the black underside rendering issue.
- None for the strict browser workflow path documented above. The separate case/reference and rendering issues remain open.
- User-provided reference image path/name is **待补充**. Read-only repository review distinguishes (a) derived display grid style/density, (b) new-case Cartesian `dx/dy` and `nx/ny` resolution, (c) existing-case bathymetry/wet-mask editing, and (d) a true unstructured triangular solver mesh. Only (a) is the 3D triangle display mode; (b)/(c) alter model input and (d) has no current implementation evidence. Keep this scope unresolved and avoid topology changes until a concrete product requirement identifies which of these operations is intended, the target case scope and remapping behavior.
- No additional repository implementation/delegation convention beyond the supplied root `AGENTS.md` has been located; any separate document path/name is **待补充**.

## Follow-up: final desktop/browser retest after opaque side walls

After the dynamic wall was changed from 12% to fully opaque, the desktop app was restarted and the browser hard-reloaded. The 8766 health endpoint was ready with model root `3DWET`, PID 70940, instance `37ec3b2bc3174d2ab8d70f4944189072`; the visible window title was `3DWET Studio`. The loaded page referenced `/static/js/viz3d.js?v=92`; an HTTP 200 response at that exact URL had SHA-256 `FEB259CB8A7A0DAAEFF0634C58A38EE688D63D2C463C88E8F67CC2E7BC4904A6`, equal to the current local file.

In the imported Erken browser case, at automatic vertical exaggeration 166.5×, the opaque-wall change made large side areas slate-blue, but visible black areas remain. An in-browser Plotly legend isolation provided a trace-level discriminator: hiding `湖盆水深` removed the black areas while the water field and opaque slate-blue outside wall remained. Restoring the bathymetry trace brought the black areas back. This points to an interaction involving the lake-bed trace at the extreme vertical exaggeration; exact depth/overdraw behavior remains under investigation. At 20× the same black underside was not prominent in the visual view. The lake-bed trace was restored, and the illustrative land layer was re-enabled after isolation.

The same latest desktop page completed a real 3D playback from frame 0 through frame 19 at target 4 fps: 20 successful frames, actual 4.0 fps, whole-frame P50/P95 35/50 ms, 0/20 over draw budget, and zero frame intervals over target by more than 10%. `模型上下位置` was set to +15% and remained there at the last frame. The final browser view is frame 19, auto vertical exaggeration, position +15%, land layer visible. This confirms playback and camera-offset persistence for this case; it does not close the remaining black underside defect.

The wall trace change and its regression are in `3DWET/app/static/js/viz3d.js` and `tests/viz3d_bathymetry_surface.test.cjs`. The regression was observed failing at 0.12 opacity before the change and passing at opacity 1 afterward. Focused rendering checks are recorded with the same code revision.

## 2026-10-23 Sol — lake-bed lighting retest and current desktop build

- Luna changed the `湖盆水深` trace to flat ambient lighting (`ambient=1`, `diffuse=0`) and added an assertion at VE=166.5×. Sol ran `node --test 3DWET/tests/test_viz_waterbody_patch.js 3DWET/tests/test_viz_render.js tests/viz3d_bathymetry_surface.test.cjs`: 21/21 passed. The browser screenshot still shows black bed polygons, so this lighting change is not considered a black-shadow fix; the bed trace color/geometry is under investigation.
- Restarted the desktop app to synchronize the code. Health returned ready, application `3dwet-studio`, model root `3DWET`, PID 88456, instance `a7a63d10904f40ff96a1c16dc21a483b`. Local and served `viz3d.js?v=92` SHA-256 both equal `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`, confirming the desktop service loaded the current source.
- In the browser, replayed 3D frames 0→19 for `user-journey-Erken-import`: target 4 fps, actual 4.0 fps, 20/20 frames, whole-frame P50/P95 50/66 ms, 0/20 draws over budget, zero frame intervals beyond the 10% target threshold. Started with model position +15%; it remained +15% at frame 19. Screenshot saved as `erkens-3d-playback-20261023.png`.
- The currently selected derived triangle display mode remains a view-only overlay; the displayed status explicitly says `仅显示网格；求解器拓扑不变`.

## 2026-10-23 Sol — 2D full-range browser playback

- In the same isolated Erken import case and current desktop build, the browser 2D view played output frames 0→19 at target 4 fps. It completed 20/20 frames at actual 4.0 fps; whole-frame P50/P95 3/4 ms; 0/20 draws over budget; zero intervals more than 10% above target. Screenshot: `erken-2d-playback-20261023.png`.
- Returned to 3D afterward. Browser DOM showed frame 19, saved 3D performance values 20/20 at 4 fps, and model position +15%. The unresolved black bed screenshot is `erken-black-bed-remains-20261023.png`.
- A focused source review of bed geometry/intensity did not establish a black-face cause. No further speculative rendering change was made. Next useful action is to inspect the actual live Plotly trace arrays at black pixels and vary one trace property at a time in a controlled browser reproduction.

## 2026-10-23 Sol — final browser playback, negative bed-rendering experiments, and Erken candidate run

- Browser recheck in `user-journey-Erken-import` on the final v92 source: 2D played frames 0–19 (20/20), target 4 fps, panel actual 4.0 fps, full-frame P50/P95 3/4 ms, 0 over-budget draws, and no interval more than 10% late. 3D played 0–19 (20/20), target 4 fps, actual 4.2 fps, full-frame P50/P95 46/80 ms, 1/20 over-budget draws, and no interval more than 10% late. These are one browser observation, not a universal performance guarantee.
- The independent model vertical-position control was +15% and remained at +15% after playback advanced to frame 19. This verifies the position control survives frame changes in this case.
- Black underside polygons remain unresolved. Hiding the depth legend trace removes them; restoring it brings them back, while disabling illustrative land did not remove them. A controlled browser `flatshading=true` experiment also left them visible and was reverted. A proposed color-range diagnosis was withdrawn after tracing the actual overlay call: overlay passes `style=null`, so its default 0..maxDepth range already applies. No root cause or fix is claimed.
- After reverting that experiment, desktop health was ready (PID 74028, root `3DWET`). The browser requested `viz3d.js?v=92`, HTTP 200; served and local source hashes matched: `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`.
- Separate Erken June 2024 A/B/C candidate runs are now complete and the C rerun validates 168 expected hourly frames in all NetCDF output axes with required variables finite. This is solver/output-integrity evidence only: it used a candidate solver binary distinct from production. The 168-hour result set has not yet been loaded and played in the browser, and the experiment is not scientific or field validation. See `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/ATTEMPT03.md` for forcing proxies, boundary padding and descriptive results.
- Evidence screenshots: `erken-2d-playback-20261023.png`, `erken-3d-final-playback-20261023.png`, and `erken-black-bed-flatshading-20261023.png`.

## 2026-10-24 Sol — full-range playback on Erken June 2024 A candidate output

- Opened the existing A candidate directory in the 8766 app. The browser 3D page reported 168 output steps and a frame slider range 0–167; selected `temp` (water temperature). No model rerun occurred.
- With playback range 0–167, target 4 fps and model position +15%, the visible slider advanced to frame 40 after 10 seconds, then reached frame 167. The displayed end time was `2024-DOY172 13:00:00`; the final panel reported target/actual 4.0/4.0 fps, 0/60 recent draws over budget, and 0 intervals more than 10% over target. Position remained +15%.
- Attempted the same 168-frame 2D playback. The browser automation click on the visible play button repeatedly timed out; the frame slider remained at 0. This long-range 2D test remains incomplete. A separate 20-frame 2D Erken run passed earlier, but does not substitute for this dataset.
- Restored the active case to `user-journey-Erken-import` and reloaded the browser. Desktop health remained ready (PID 74028, root `3DWET`). HTTP 200 `viz3d.js?v=92` UTF-8 body SHA-256 matched local source exactly: `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`. Only audit documentation changed this turn.

## 2026-10-24 Sol — full-range 2D playback on Erken June 2024 A candidate output

- In the same 8766 app and A candidate output, selected `temp` (water temperature), playback range 0–167, target 4 fps. The browser playback reached frame 61 at the 10-second checkpoint (`2024-DOY168 03:00`) and then frame 167 (`2024-DOY172 13:00`); playback automatically returned to paused. The final panel reported target/actual 4/4 fps, rolling 60-frame statistics, whole-frame P50/P95 4/5 ms, 0/60 draws over budget and zero frame intervals more than 10% late.
- This and the preceding full-range 3D run used the same candidate output set. Both prove actual browser playback across the 168-frame range for this case and variable, subject to the candidate-solver and proxy-forcing limits already recorded.
- Active case was restored to `user-journey-Erken-import` after the test. No source or server code changed.

## 2026-10-24 Sol — desktop Erken import 3D vertical-offset and active-playback spot check

- On the currently open 8766 browser page for `user-journey-Erken-import`, selected `连续水体` for a controlled visual comparison. At frame 0, set `模型上下位置` to +15%; accessibility state showed `Value: 15` and `+15%`. Clicked next frame: frame changed to 1 (`2020-DOY001 00:12:00`) and the slider remained `Value: 15` / `+15%`.
- Started playback at the page's 1 fps target. After 4.2 seconds the page showed frame 5 (`00:36:00`), the play checkbox remained active, target/actual 1/1.0 fps, successful frames 5, 0/5 over-budget draws, and zero frame intervals over target by 10%. This directly confirms frame advancement and offset persistence during active playback in this browser session; it is a spot check, while full-range 2D/3D results are recorded above.
- Rendering comparison: in the current 2020 import, dark interior spots are reduced in `连续水体` compared with the derived-triangle screenshot, but the current view does not reproduce the previously reported black underside at the same severity. This does not establish a fix or root cause; the candidate 2024 black underside remains unresolved.
- Desktop synchronization check: process listening on port 8766 is PID 74028, `python.exe`, command line starts `3DWET/app/launcher.py --desktop`. The page references `/static/js/viz3d.js?v=92`; fetched response and local `3DWET/app/static/js/viz3d.js` have identical UTF-8 SHA-256 `4E00F738FB1F540C0C61FA7446626CD6F88FAF6163FE87952F88D74D147AB3A2`. `/api/health` is not a route in this current server (404), so the process and exact served-source hash were used as runtime evidence. No source code changed; only this audit record was added.

### 2026-10-24 Sol 补记：同一 3D 播放自然完成全范围

上条记录的 4.2 秒检查点之后，播放器在本轮浏览器检查期间继续运行并自然到达第 19 帧、自动暂停。页面终态：frame 19/19，成功帧 20，目标/实际 1/1.0 fps，整帧 P50/P95 38/46 ms，0/20 绘制超预算，帧间隔超目标 10% 为 0。“模型上下位置”在终帧仍为 +15%。因此这次实际完成了该 20 帧 3D 输出范围的完整播放；之前对 168 帧 A 组的 4 fps 全范围实测仍是更长案例的验收证据。

### 2026-10-24 Sol：浏览器实时迹线隔离黑色湖底

- 在 `user-journey-Erken-import` 的实际 3D 页面（frame 19、自动垂向放大 166.5×、镜头仰角 34°、位置 +15%）通过图例单击隐藏“湖盆水深”迹线。黑色下侧多边形消失，同时水温场、岸壁蓝灰面、岸线、等深线和岸陆示意仍可见；恢复该迹线后，黑色下侧面立即重新出现。由页面实测可将异常定位到“湖盆水深”底面迹线的渲染路径，而不是岸壁单独着色。
- 源码中该迹线使用 `geometry.floor` 深度角点、深度色带，`ambient=1 / diffuse=0 / specular=0` 且 `flatshading=false`；但浏览器画面仍出现近黑色下侧面。此前的三角形法线/退化检查未发现几何错误。根因仍未确认，因此没有再做推测性代码修改。
- 对照期间将相机角度暂设为 89°、垂向放大暂设为 20×；之后已恢复镜头仰角 34°、自动垂向放大、连续水体、床面图例打开，模型上下位置 +15%。当前浏览器回到原 20 帧 Erken 导入结果的第 19 帧。桌面源码未改，服务无需重启。

### 2026-10-24 Sol：正常俯视与底视的黑面控制变量复核

- 对当前 20 帧 Erken 导入结果，保持 frame 19、连续水体、自动放大 166.5×、位置 +15%，正常俯视 +34°下，图例关闭“湖盆水深”时近黑色下侧面消失，恢复后复现。
- 将仰角设为 −34°时，页面明确显示“水体底视：已隐藏湖底与陆地示意平面”。该底视隐藏是现有设计行为，不能视作解决了正常视角下的黑面。此项把可见异常定位在底面迹线绘制，但尚不能区分 Plotly/WebGL 着色、深度缓冲或底面自身数据/投影交互；未改代码。
- 已把镜头恢复 +34°、自动放大 166.5×，浏览器当前仍是 frame 19，模型位置 +15%，播放器暂停。页面版本 v92 的服务端与本地哈希上一轮已核验相同；本轮无源码变更，无需同步重启。
