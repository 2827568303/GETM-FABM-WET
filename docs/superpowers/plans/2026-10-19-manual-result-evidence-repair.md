# Manual result evidence repair plan

Scope for this pass: repair calibration comparison rendering and map viewport behavior. Leave the full calibration-run closure and manual completion to the owner.

## Baseline and evidence

- Before edits, SHA-256 values for `app.js`, `server.py`, `calibration.py`, `scientific_geometry.py`, and existing relevant tests were recorded in `build/manual-result-repair-prechange-20261019/prechange-hashes.json`; existing calibration/map tests were copied to that folder. The checkout contains unrelated staged/unstaged and untracked work; preserve it.
- `workflow-evidence.json` records an isolated API comparison with 20 successful pairs. Its simulated payload is a native `[time][layer]` column and includes physical center depths. `observation_matching.pair_observations` interpolates each pair at the observation timestamp and depth; the API serializes those scalar values as `scatter_pairs[].sim` beside `obs` and `time`.
- `updateCalComparison` currently sends `simulated.values[time]` directly to a scalar Chart.js dataset. For multi-layer observations this is an array, so Chart.js cannot draw a scalar time line. The observed dataset also sets a transparent fill and zero border width, leaving its unconnected points invisible. Regression: `node 3DWET/tests/test_calibration_comparison_series.js` fails because chart values are arrays.
- In the isolated imported case, `bathymetry.nc` has independent x/y axes with metre units and valid `lonc`/`latc` axes in degrees. Thus the captured geographic map should use those valid geographic bounds; meter coordinates are not those screenshot's cause. `initLeafletMap` fits bounds while a page can be hidden, then its delayed callback only calls `invalidateSize`. It never reapplies the same grid bounds after the visible viewport is measured. Regression: `node 3DWET/tests/test_map_hidden_viewport.js` fails on the missing post-resize refit. Keep the separate XY-only path in `CRS.Simple`; do not invent a geographic CRS.

## Minimal repair and tests

1. Build the calibration chart from `scatter_pairs` (paired scalar model/observation/time values), sorted by parsed time. Use the backend's depth/time interpolation; never choose a layer from the native matrix in the browser. Give observation points a visible fill, outline, and radius. When there are no pairs, show a useful no-pair state and only use native values if they are truly scalar. Cover multi-layer native input, depth/time-paired scalar values, visible markers, and empty/missing data in the chart behavior regression.
2. After `invalidateSize` completes for the map, reapply valid geographic grid bounds; for local projected/index grids retain `CRS.Simple` and meter/index coordinates. Extend the map regression for hidden-page resize and XY mode, and retain the existing fill sentinel regression. Confirm map variable and field labeling stay aligned on refresh/selection.
3. Run the focused Node regressions and relevant existing calibration/map tests. Then launch the final source through `launcher.py --ui-smoke --port 0 --report <absolute path>` under an isolated `WET_MODEL_ROOT`; confirm the WebView2 DOM serves the final source and capture the actual map and calibration views through native UI actions. Record process/port/root and artifact hashes. Never change shared port 8766 state.

## Acceptance boundary

Only these two visualization root causes are in this pass. No hand-edited screenshots, API response substitution, synthetic drawing, shared-case mutation, model run, PR, or commit. The owner separately decides and verifies the successful real calibration closure and broader manual evidence.
