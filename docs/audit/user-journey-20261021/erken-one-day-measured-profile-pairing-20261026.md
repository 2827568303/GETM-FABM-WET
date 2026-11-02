# Erken existing one-day profile pairing

**Owner:** Sol 高

**Status:** **代理**对照（实测观测 × 既有模型输出）；限于单日诊断。Erken scientific validation remains **未完成**.

## Evidence and method

- Reused the authorized [SITES Erken hourly profile](https://hdl.handle.net/11676.1/Kq6E7t69ZyKJejMcANJQVoHP), file `SITES_TW-PROF_ERK_LRK_20170628-20240914_L2_60min.csv`. It identifies the Erken Laboratory anchored temperature profile at 59.84247°N, 18.630983°E, reports timezone UTC+1, and has SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`.
- Read the pre-existing WET model output `build/real-use-validation-20261021/erken-real-location-24h/baseline/output/output.nc`; no solver was run. This is model output and is classified **代理**, not measurement. Its SHA-256 is `63a96af290181df23d840c14d1aec969fc690f8aefad54ea529030991cd28187`; the file has 24 hourly frames from 2020-01-01 01:00 through 2020-01-02 00:00, a 10-layer sigma profile, and 376 wet horizontal cells.
- Matched the 24 output labels to the Erken observations by identical timestamp text. This window has 24 unique measured rows and 50 non-missing depths per row (1.0–15.5 m), for 1,200 pairs. Timezone equivalence was not independently established: observation metadata states UTC+1, while the model NetCDF time unit does not state a timezone.
- Selected the nearest wet model cell to the station: `(yc=8, xc=36)`, approximately 0.108 km from the reported station coordinate, with bathymetry 16.471 m. Interpolated the model temperature linearly between saved sigma-layer center elevations (`zc`) after converting them to positive depth below the model surface; paired only within the observed sensor-depth interval.

## Result

Across the 1,200 timestamp/depth pairs, model minus observation bias is **+0.0536 °C**, MAE **0.0542 °C**, and RMSE **0.0591 °C**. Observations span 2.0588–2.2237 °C; paired model values span 2.1595–2.2124 °C.

The error is not constant through the day: the first six saved frames (01:00–06:00) have bias **+0.0374 °C** and RMSE **0.0437 °C**; the last six (19:00–24:00) have bias **+0.0742 °C** and RMSE **0.0772 °C**. Depth-band RMSE is 0.0579 °C at 1.0–5.0 m, 0.0535 °C at 5.25–10.0 m, and 0.0650 °C at 10.5–15.5 m. This indicates the positive model-minus-observation difference grows over this one-day window and is somewhat larger in the deepest sampled band; it does not identify the physical cause.

These are descriptive statistics for this existing one-day output and measured profile. They do not demonstrate seasonal or long-term skill, nor do they establish the cause of the warm bias. The model was initialized from an observed Erken profile at 2020-01-01 00:00, making this a short post-initialization comparison. Its meteorological provenance is a measured SITES Malma station 3.517 km away with `confirmed: false`; the run also uses configured constant heat-flux terms and disables rivers. These setup limits and unverified time-zone alignment prevent upgrading the result to a complete Erken validation.

## Correct status

- SITES source/profile rows: **实测**.
- Existing WET model output: **代理**.
- Timestamp/depth pairing and metrics in this note: **代理**（实测观测 × 代理模型输出的有限诊断对照）.
- Full Erken scientific validation: **未完成**.
- Model rerun, case creation or cleanup: **未执行**.
