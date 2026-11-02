# 2D / 3D playback prefetch acceptance (Sol)

Date: 2026-10-21 (Asia/Shanghai)

## Changes reviewed

- 3D playback starts one next-frame `/api/results/3d_surface` request while the current Plotly frame is being prepared/drawn, then reuses that response only for the matching case, URL, and frame. It stops prefetching at the selected inclusive end frame.
- 2D playback starts one next-frame `/api/results/2d` request while the current result is drawn, then reuses it only for the matching case revision, variable, level, URL, and frame. It stops prefetching at the selected inclusive end frame.
- Existing scheduler behavior still renders one frame at a time, avoids catch-up bursts, and stops on failed renders.
- The color range mode “当前帧自动（逐帧缩放）” continues to recalculate the visible range on each frame. Locked/custom modes remain available for comparisons.

## Sol verification

Targeted command:

```text
node --test 3DWET/tests/test_viz2d_playback_prefetch.js 3DWET/tests/test_viz3d_playback_prefetch.js 3DWET/tests/test_scientific_playback_range.js 3DWET/tests/test_viz_scientific_style.js 3DWET/tests/test_viz_variable_height.js
```

Result: 78 passed, 0 failed. Coverage includes request overlap/reuse, inclusive playback endpoints, stale selections, case/variable/layer changes, invalid results, slow-frame scheduling, pause/resume, and 2D/3D color ranges.

The visible desktop app at `http://127.0.0.1:8766/` was independently exercised. Both views played from frame 0 through a temporary end frame 5 at a 12 frames/s target, stopped at frame 5, and reset the play button to paused. After playback, each displayed frame/time label, range, and value changed with the selected output frame:

| View | Frame 0 | Frame 5 |
|---|---|---|
| 2D temperature, level 5 | range 15.3399–15.4447 °C; mean 15.4175 °C | mean 15.7150 °C; 14×21 field |
| 3D temperature | range 15.33995–15.49342 °C | range 15.49146–15.78764 °C; label 2020-DOY001 06:00:00 |

The app was restored to 3D temperature at frame 23, paused, with the 1 frames/s target and end frame 23.

## Service synchronization

- `/`, `/api/run/status`, `/static/js/app.js`, and `/static/js/viz2d_playback_prefetch.js` returned HTTP 200 after the service restart.
- The served app page contains `viz2d_playback_prefetch.js?v=1` before `app.js?v=45`.
- Served and on-disk SHA-256 match for the helper (`3AB312D371BF2AE5B20E98B76F169CD0A151F042479CA48C3ED246B68F017C54`) and `app.js` (`D4D64F37C9BBE21E2FB4120B2620763212C55B1363AE2C88420F6C97A861DE4A`).
- The final UI check showed `page-viz3d`, frame 23, paused, with the final frame range 14.15688–15.55717 °C.

## Performance limits and remaining work

The prior warm endpoint medians were 248.5 ms for 2D and 129 ms for 3D. Post-change observations were 252.4 ms for 2D and 127.9 ms for 3D. These are effectively unchanged; the optimization overlaps the next request with current drawing rather than reducing server/API latency. At that earlier measurement point, no reliable before/after frontend cadence or fixed 12 frames/s result had been recorded; the later desktop measurements below cover this gap for the tested 24-frame case. The generated `competition_treatment` case is a playback reproduction fixture, not real-lake validation.

## Additional desktop playback acceptance

The playback timer now keeps its cadence start index relative to the rolling window of the most recent 60 successful frames. After restart, the synchronized desktop service reported instance `330a560ad0874a3fa4d73db2f5107c28` (PID 43352); the home page referenced `playback_performance.js?v=5`, and the served JavaScript SHA-256 matched the workspace file (`AFA654E8B33E721FFAFBD07006B92F7A4F856E9FCF3CE30A36FA7DFD8DCD1309`).

On the same portable 24-frame case, the UI playback panel retained all 24 successful frames and showed no over-budget frames during these observations:

| View / variable | Playback observation |
|---|---|
| 2D `temp` | 11.4 frames/s; all 24 frames completed; automatic color range followed each frame. |
| 3D `temp` | 12.1 frames/s; P95 whole-frame time 38 ms. |
| 3D `greens_competitor_sDW` | 12.1 frames/s; P95 31 ms; range changed from 0.078764–0.080840 at frame 0 to 0.070116–0.073039 at frame 23. |
| 3D `diatoms_sDW` | 12.0 frames/s; P95 38 ms; range changed from 0.097459–0.099277 at frame 0 to 0.074743–0.079472 at frame 23. |

These measurements describe this 24-frame case and the tested desktop/browser only. Although the timer now retains and rolls a 60-frame window, visible end-to-end playback on a larger grid and a session exceeding 60 frames have not yet been measured; no long-session or larger-grid performance conclusion is made here.

## Non-vertical metric and latest desktop verification

Date: 2026-10-21 (Asia/Shanghai)

After the 3D variable handling update, the loaded portable case was exercised in the visible desktop application. A no-vertical-dimension variable remains selectable in 2D and in the 3D main variable selector. Selecting `D` switches the 3D main view to `surface2d` and states that Z is variable value, not physical water depth or water surface. Trying a waterbody render with `D` returns the selector to `surface2d`. The point-profile and vertical-average selectors keep `D` disabled, while 4D `temp` remains usable in waterbody mode.

Both `D` playback runs completed all 24 real output frames at a 12 frames/s target, with 0 over-budget frames and no missed-interval count:

| View / variable | Playback observation |
|---|---|
| 2D `D` | 12.0 frames/s; P95 whole-frame time 4 ms; auto range updated from 2.394433–8.938541 at frame 0 to 2.393462–8.938517 at frame 23. |
| 3D variable-height surface `D` | 12.0 frames/s; P95 whole-frame time 48 ms; 24/24 successful frames. |

The synchronized service was instance `cc96b704661545e8bd04cd4c3e1adcc1` (PID 50884). The visible page loaded `app.js?v=53`; served and workspace `app.js` SHA-256 both equaled `766D1D935C19C1D75768F90820E4015E42F65258EC7340B401D9FF991F0838CD`. The app was reloaded after documentation changes and restored the portable case. This is a UI and playback check for the supplied local case, not scientific validation of `D` or a general performance guarantee.

## Same-case 3D `greens_sDW` cadence rerun

Sol repeated the complete 24-frame `competition_treatment` playback three times with the same variable and display settings after an earlier run showed 11.2 frames/s and P95 102 ms. The repeated runs completed all 24 frames at the 12 frames/s target:

| Run | Actual frame rate | P95 whole-frame time | Frames over draw budget | Slow intervals |
|---|---:|---:|---:|---:|
| 1 | 12.0 frames/s | 82 ms | 1/24 | 1 |
| 2 | 12.0 frames/s | 77 ms | 1/24 | 0 |
| 3 | 12.0 frames/s | 71 ms | 1/24 | 0 |

The final frame's automatic color range updated as expected in each run. The earlier 11.2 frames/s observation was not reproduced, so it does not establish a stable variable-specific bottleneck. No rendering algorithm change was made from that single outlier. These measurements apply only to this 24-frame fixture and the tested desktop/browser; they do not establish performance for larger grids or longer histories.

## Portable case playback spot check

Sol also exercised `portable_greens_clone_treatment` in the visible UI at a target of 4 frames/s. This was a partial 2.2-second playback of its 24-frame sequence: playback advanced from frame 0 to frame 9 (about 4.1 frames/s by frame delta), and the UI returned to paused after stopping. Automatic color ranges followed the selected frame:

| View / variable | Frame 0 range | Frame 23 range | Playback telemetry |
|---|---|---|---|
| 2D `greens_competitor_sDW` | 0.0788–0.0795 | 0.0701–0.0725 | Partial run to frame 9; ~4.1 frames/s by frame delta. |
| 3D `greens_competitor_sDW` | 0.0788–0.0808 | 0.0701–0.0730 | Target 4, actual 4.0 frames/s, 10 successful frames; whole-frame 32 ms, P50 30 ms, P95 59 ms, 0/10 over budget. |

The 3D view responded to a side-view camera preset; the oblique camera was restored afterward. This is a local UI check on the portable 24-frame case, not a scientific validation or a performance guarantee for other data sizes/devices.

## UI auto-range spot check across result variables

Sol inspected the first and last frames of the same 24-frame `portable_greens_clone_treatment` in the UI. The 2D values below are the displayed surface layer; the 3D values are the displayed surface layer in the 3D view. Units are transcribed from each selected variable's UI metadata. Auto color limits changed between frames for every listed variable:

| View | Variable | UI unit | Frame 0 range | Frame 23 range |
|---|---|---|---:|---:|
| 2D surface | `temp` | Celsius | 14.744689–15.074357 | 12.006480–12.928408 |
| 2D surface | `elev` | meters | -0.000275–0.000449 | -0.001200–0.001775 |
| 2D surface | `u` | m/s | -0.007374–0.023462 | -0.031199–0.066204 |
| 2D surface | `greens_sDW` | gDW/m3 | 0.078605–0.079350 | 0.067051–0.069299 |
| 2D surface | `diatoms_sDW` | gDW/m3 | 0.097459–0.098900 | 0.074743–0.079252 |
| 2D surface | `abiotic_water_sO2W` | g/m3 | 8.521457–8.609329 | 8.843837–9.190042 |
| 2D surface | `D` | m | 2.394433–8.938541 | 2.393462–8.938518 |
| 3D surface layer | `temp` | Celsius | 15.033987–15.176597 | 12.129846–13.039227 |
| 3D surface layer | `greens_competitor_sDW` | gDW/m3 | 0.079720–0.080840 | 0.070506–0.073039 |
| 3D surface layer | `diatoms_sDW` | gDW/m3 | 0.098693–0.099277 | 0.075059–0.079471 |
| 3D surface layer | `abiotic_water_sO2W` | g/m3 | 8.492291–8.535216 | 8.825543–9.161662 |
| 3D surface layer | `u` | m/s | -0.007374–0.023462 | -0.031199–0.066204 |
| 3D surface layer | `D` | m | 2.394433–8.938541 | 2.393462–8.938518 |

This confirms that the UI's current-frame automatic ranges respond to the selected output frame for these variables and layers. It does not establish scientific validity of the outputs, nor performance for other cases, grid sizes, or devices.

## v60 mesh-network playback recheck

Sol compared network modes in the visible UI using the same 24-frame `portable_greens_clone_treatment`, variable `greens_competitor_sDW`, and target 12 frames/s. Two triangle-network runs reached 11.5 and 11.8 frames/s (P95 whole-frame 99 and 88 ms); the network-generation stage was 19 and 18 ms, with 4/24 and 5/24 frames over the draw budget. Orthogonal mode reached 12.0 frames/s with P95 54 ms, 6 ms network generation, and 0/24 over-budget frames.

The earlier comparison for the same device and case was 10.2 frames/s, P95 103 ms, and 39 ms/frame for network generation. These are asynchronous same-device observations rather than a fully controlled benchmark; they suggest improvement but do not establish a general speed gain. In the two v60 triangle runs, remaining long frames included about 26 ms total mesh work plus roughly 30 ms Plotly drawing, so network-line generation alone was no longer the dominant cost. Orthogonal mode met the selected target in this check. Results apply only to this case, settings, browser, and device.

The current synchronized desktop service was ready and idle on instance `7eaf94ff41b2434481fda0b1ce12131a`, PID `52732`. The page referenced `viz3d.js?v=60`; served and workspace SHA-256 both equaled `08965EFFC512CCC1AEF57756B8F9432EF4BF3F2B9DB0E9569EAC5B9CBBA992D0`.

## Erken baseline playback recheck and 3D optimization proposal

Sol's later UI recheck used the 44×18×10 Erken-location baseline, variable `temp`, and a 12 frames/s target. The 2D run began at frame 5 and completed the remaining 19 frames through frame 23: actual 10.4 frames/s, P95 whole-frame time 215 ms, 1/19 frame over draw budget and 6 slow intervals. The 3D run completed 24/24 frames: actual 8.0 frames/s, P50 108 ms/P95 147 ms, 24/24 over draw budget and 23 slow intervals; reported assembly was about 46 ms and Plotly draw about 55 ms. In both views the time cursor and current-frame automatic temperature range changed. This is a measured local playback shortfall at the 12 frames/s target, not a successful smooth-playback result; previous faster observations were from separate runs/settings and do not override this check.

### POM_sDW same-baseline playback and bounded lookahead trial

Sol later replayed the same Erken baseline at a 12 frames/s target with `POM_sDW` selected. The 2D run completed 24/24 frames at 10.7 frames/s, P95 whole-frame time 107 ms, with request stage 94 ms and canvas draw 3 ms. The 3D stacked-waterbody v63 run completed 24/24 frames at 9.8 frames/s, P95 125 ms (request 82 ms, decode 13 ms, assembly 48 ms, Plotly draw 27 ms). These stage timings are client-observed elapsed times; the request stage can include browser/main-thread scheduling and is not a server-only endpoint duration. The 12 frames/s menu value is a target ceiling, not a guaranteed rate; achieved cadence depends on device, grid and indicator complexity. A subsequent v64 two-frame lookahead is implemented and focused regression-tested, but still awaits matched browser measurement; no throughput gain is claimed for it yet.

### Candidate implementation boundary

The current main-view render computes `basin` from each response's `water_depth` (falling back to static `bottom`), then passes that full frame geometry into `lakeGeometryForFrame()`. Its geometry key includes the exact basin values and vertical scale. When water depth changes between frames, the geometry key changes; `viz3dPlot()` therefore rejects the existing waterbody patch and falls back to `Plotly.react()`. That path redraws basin and field traces together even when wet-cell connectivity remains unchanged.

A narrow optimization should separate an immutable topology signature from the frame's dynamic arrays. The topology signature must include case/output identity, horizontal coordinates, wet/dry and land masks, display-topology contract, selected mesh mode/refinement, layer selection, and relevant render options. A patch may be used only when trace order, types/names, mesh connectivity (`i/j/k`), and every updated array's shape are compatible. It must update all frame-dependent values in one serialized Plotly operation where supported: water-depth floor/wall/contour heights, scientific field coordinates and values, missing-data masks, `customdata`, automatic `cmin/cmax` and colorbar, title/time label, axis scale, and the current layout. Otherwise it must retain the existing `Plotly.react()` fallback.

Acceptance invariants: stale or failed requests cannot replace the last successfully displayed frame or move the time control ahead; updates remain serialized with no catch-up queue; the current-frame automatic range and exact cell-center hover values remain correct; dry-cell topology and missing-data masks remain unchanged; camera gestures and `uirevision` survive each update; case, variable, layer, range, vertical scale, mesh-mode, or output revision changes invalidate incompatible cached topology. Regression coverage should exercise same-topology frames with changed field/depth and ranges, changed topology/schema fallback, stale out-of-order responses, and camera retention during playback. A paired 24-frame Erken UI comparison must report actual fps, P50/P95, draw-budget overruns, slow intervals and successful frame/time alignment; no speed improvement is claimed until that same-case before/after check demonstrates it.

## 2026-10-22 Follow-up: isolated Nfix frame-color investigation

Sol tested an exact copy of the active Nfix `nfix_on` case in the isolated 8767 application (24 output frames, 6 layers, 189 wet cells). For 3D `cyanobacteria_competitor_sDW`, using continuous waterbody rendering, layer `-1` (physical layer 5), and the upward camera, the water-colored field and colorbar remained visible on manual frame 1 and during 1 fps playback through frame 4. The UI reported zero missing water values, zero missing geometry, and P95 whole-frame time 51 ms. An 8 fps target run reached frame 22 with 23 successful frames; P50 was 24 ms and P95 31 ms.

After switching to `temp`, continuous-waterbody playback through frame 2 retained its colored water surface. In isosurface mode at frame 2, the visible surface appeared narrower from the chosen camera, while field diagnostics still showed 1,134 valid values, zero missing values, and zero missing geometry. A 2D `temp` heatmap remained visible through 2020-DOY001 05:00:00 (frame 4); its automatic range changed from approximately 14.52–14.99 to 14.35–14.92.

The `hn` text in the 3D diagnostic footer identifies the vertical-geometry source (native layer thickness); `hn+zc` means layer thickness plus vertical-center geometry. It does not identify or replace the selected scientific variable, which is carried separately by the result request and colorbar. This follow-up **did not reproduce** the reported second-frame color loss and does not establish a fix or cover every variable, render mode, layer, or camera. No code was changed. The main 8766 service remained healthy and served `viz3d.js?v=79`; its active case and service were not touched.
