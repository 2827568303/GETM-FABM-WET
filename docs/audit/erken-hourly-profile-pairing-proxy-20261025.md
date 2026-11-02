# Erken hourly temperature-profile pairing check — 2026-10-25

## Status

**代理 — exploratory model-output pairing only; Erken scientific validation remains 未完成.** This check reuses an existing output file and does not create a model case or start the solver.

## Measured source

- SITES record: [Physical variables — lake temperature profile from Erken, year-round anchored TW-profile, 2017-06-28–2024-09-14](https://meta.fieldsites.se/objects/Kq6E7t69ZyKJejMcANJQVoHP), PID `11676.1/Kq6E7t69ZyKJejMcANJQVoHP`.
- Official metadata reports 62,959 hourly records, 2017-06-28 19:00 through 2024-09-14 08:00 (UTC+1), temperature at 49 depth columns spanning 1.0–15.5 m, and sampling location 59.84247° N, 18.630983° E. SITES marks this historical release deprecated and points to a newer version; it is retained here because it is the requested 2017–2024 hourly source.
- Licence: [SITES CC BY 4.0](https://data.fieldsites.se/licence). The user explicitly authorized accepting the SITES notice and downloading this source. The source archive and extracted CSV are retained at `build/source-downloads-20261025/erken-hourly-2017-2024/`.
- Extracted CSV SHA-256 `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e` exactly matches the official metadata. Archive SHA-256 is `0edcc4ff20344acc98001c8c301b5d353ec0d5a497b4691a49275aadddb940a8`. Machine-readable provenance is in `erken-2017-2024-hourly-provenance.json`.
- **Source distinction:** the earlier retained PID `11676.1/XwTfEa8hviDoL_TEhBCYFkt9` is a separate *daily* profile file, not this 60-minute file. Do not describe that daily file as the requested hourly dataset.

## Existing output and method

- Reused `build/erken-production-compare-20261024/case-production-legacy/output.nc` (SHA-256 `784b37d30e0b99ed83838369fba2a9c8bddffc1d427937b93ad36c3758d7788e`). It contains 168 hourly snapshots from 2024-06-13 14:00 to 2024-06-20 13:00, with 10 vertical layers on a 44×18 grid. No new solver execution occurred.
- Selected the nearest wet cell to the SITES station using great-circle distance: `(yc=8, xc=36)`, 0.1023 km away; its initial water depth is 16.4715 m. This is a nearest-cell comparison, not a spatially averaged station footprint.
- For each model output, linearly interpolated the 10 model temperature values by that time's layer-center depths to the 49 measured depths. Exact hourly timestamp matches yielded 168 profiles and 8,232 temperature pairs for each clock-offset hypothesis.
- The source CSV states `TIME ZONE: UTC +1`; the NetCDF model time units have no timezone annotation. Since clock semantics remain unresolved, all three candidate offsets were retained. `offset_model_minus_label_h` means the model timestamp used equals the source label plus that offset.

| Candidate clock offset | Profile times | Depth pairs | Bias (°C) | RMSE (°C) | MAE (°C) |
|---:|---:|---:|---:|---:|---:|
| 0 h | 168 | 8,232 | +0.1020 | 4.1839 | 3.9958 |
| −1 h | 168 | 8,232 | +0.0900 | 4.1879 | 4.0013 |
| +1 h | 168 | 8,232 | +0.1150 | 4.1799 | 3.9905 |

## Interpretation and limits

The fit metrics are similar across the three clock candidates, so they do not identify the correct time interpretation. SITES reports hourly averages of one-minute measurements, while the model file stores hourly output snapshots; equivalence of those temporal supports is not established. Spatial mapping is only nearest-cell, and the existing experiment manifest identifies proxy/missing ecology, discharge, nutrients, evaporation and cloud inputs. The score is therefore a **proxy diagnostic**, not an independent field validation, model reproduction, calibration result, or proof that the case is scientifically valid. No unique cause for the profile mismatch is established.

**Erken scientific validation: 未完成.** Before any new case or solver run, remove only prior generated cases that are confirmed unwanted; do not delete this source archive or provenance.
