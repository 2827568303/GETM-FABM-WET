# Erken 2024 observation-pairing feasibility check — 2026-10-25

## Purpose and status

This is a read-only diagnostic pairing a measured Lake Erken temperature profile with an already existing exploratory model output. No case was created and no solver was started. The local model output and comparison remain **代理**; these calculations do not validate Erken science.

## Measured-data source

- **实测（官方来源元数据）**: SITES identifies the year-round anchored Erken temperature-profile dataset, current version PID [`11676.1/wGiZX7JjzAt6ZmD_V1msIID_`](https://meta.fieldsites.se/objects/wGiZX7JjzAt6ZmD_V1msIID_), as daily, 2017-06-29 through 2025-11-30, 3,077 rows, 1,424,576 bytes. The profile columns span approximately 1.0–15.5 m and are reported in °C. The sampling point is 59.84247° N, 18.630983° E. SITES reports a CC BY 4.0 license and provides a dataset citation and SHA-256 on the metadata page.
- The local case already contains the current SITES CSV at `build/black-bed-followup-20261025/model-root/case/Erken 20-frame historical readonly/Input/SITES_TW-PROF_ERK_LRK_20170629-20251130_L2_daily.csv` and its provenance manifest at `build/black-bed-followup-20261025/model-root/case/Erken 20-frame historical readonly/Input/temperature_profile_manifest.json`. The independently computed CSV SHA-256 is `c068995fb263cc0b7a6660ff5759ac2080ffd5bd1156c6884a2d6e58813c36e3`, matching the manifest. The old 2017–2024 PID [`11676.1/XwTfEa8hviDoL_TEhBCYFkt9`](https://meta.fieldsites.se/objects/XwTfEa8hviDoL_TEhBCYFkt9) is marked deprecated in favor of the current version; the current dataset includes the full model overlap. Following the user's explicit authorization, the SITES data-use notice was accepted and the historical release downloaded from the official portal. Its archive and extracted CSV hashes are recorded in `build/source-downloads-20261025/erken-2017-2024-provenance.json`; the archive bytes are in the adjacent ZIP. The historical copy is retained as source provenance only; model pairing continues to use the already-present current version.
- **实测（CSV schema/provenance）**: The CSV contains date-only `TIMESTAMP` values, a `TIME ZONE: UTC+1` note, and profile columns from `TW_-1.0m` through `TW_-15.5m` in °C. Since timestamps are daily dates rather than exact sampling times, the observation time of day and any daylight-saving interpretation are not available for hourly matching.

## Existing model-output geometry and temporal overlap

- **代理（local exploratory output metadata）**: Read-only inspection of `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/arms_168h_direct_swr_padding_verified/arm_A/case/output.nc` found 168 hourly outputs from 2024-06-13 14:00 to 2024-06-20 13:00 (NetCDF time units `seconds since 2024-06-13 13:00:00`, calendar `standard`), on a 44×18 horizontal grid with 10 sigma layers and 376 wet cells.
- **代理（spatial pairing feasibility）**: Using the SITES station coordinates and the output's wet-cell `lonc`/`latc`, the nearest wet cell is `(yc=8, xc=36)`, at 59.8431358° N, 18.6322441° E. Its approximate equirectangular separation is 0.102 km. At the 2024-06-15 14:00 output, its water depth is 16.478 m and sigma-center depths range from −15.647 m to −0.817 m. This brackets the SITES profile's nominal 1.0–15.5 m depth span, so vertical interpolation is geometrically possible at this grid cell.
- **代理（proxy-vs-measured diagnostic）**: The 168 hourly model profiles were vertically interpolated at the nearest wet cell to each measured SITES depth using the time-varying sigma-center depths, then averaged over each complete UTC model day. Six full days (2024-06-14 through 2024-06-19), 50 depths per day, yielded 300 pairs. Model-minus-observation bias was +0.3008 °C, RMSE 4.0158 °C, and MAE 3.7809 °C. Daily 1 m / 15.5 m temperatures and top-to-bottom gradients were:

  | Date | Observed 1 m °C | Model 1 m °C | Observed 15.5 m °C | Model 15.5 m °C | Observed gradient °C | Model gradient °C |
  |---|---:|---:|---:|---:|---:|---:|
  | 2024-06-14 | 16.872 | 12.268 | 7.709 | 12.320 | 9.164 | -0.052 |
  | 2024-06-15 | 16.992 | 12.936 | 7.683 | 13.256 | 9.309 | -0.320 |
  | 2024-06-16 | 17.174 | 13.165 | 7.658 | 13.281 | 9.515 | -0.116 |
  | 2024-06-17 | 17.665 | 13.204 | 7.934 | 13.294 | 9.730 | -0.089 |
  | 2024-06-18 | 17.745 | 13.196 | 7.926 | 13.281 | 9.819 | -0.085 |
  | 2024-06-19 | 17.861 | 13.145 | 7.924 | 13.184 | 9.937 | -0.039 |

- **Uncertain / limitations**: Daily observations have no sampling time of day, while the model is hourly and its timezone has not been reconciled with the source's UTC+1 note. The daily averaging above is therefore an approximate diagnostic. The six-day window is short; the proxy run's forcing/input provenance includes synthetic/proxy/padding elements and has no documented independent calibration/holdout design. The near-zero modeled vertical gradients versus measured gradients around 9.2–9.9 °C indicate a large profile-shape mismatch in this diagnostic, but do not uniquely identify its cause. No conclusion here validates the production GETM/WET case or ecological science.

## Additional cross-check against an existing production-solver output

- **实测（正式求解器执行记录）**: An already completed run in `build/erken-production-compare-20261024/case-production-legacy/` used the repository production solver SHA-256 `902a7db609469a2ddf1ae6bbe59386c5079ec206ec6b4b07864f8a59256df672` and completed 120,960 steps over 168 hourly frames. Its existing `output.nc` SHA-256 is `784b37d30e0b99ed83838369fba2a9c8bddffc1d427937b93ad36c3758d7788e`. No solver was launched for this cross-check.
- **代理（production-output vs measured-profile diagnostic）**: Applying the same nearest-wet-cell `(yc=8, xc=36)` (~0.1024 km from SITES), time-varying vertical interpolation, complete model-day averaging, and SITES daily profile yields 300 pairs over 2024-06-14 through 2024-06-19. Bias is +0.4767 °C, RMSE 4.0305 °C, and MAE 3.7752 °C. The daily 1 m / 15.5 m values and gradients are:

  | Date | Observed 1 m °C | Model 1 m °C | Observed 15.5 m °C | Model 15.5 m °C | Observed gradient °C | Model gradient °C |
  |---|---:|---:|---:|---:|---:|---:|
  | 2024-06-14 | 16.872 | 12.348 | 7.709 | 12.370 | 9.164 | -0.021 |
  | 2024-06-15 | 16.992 | 13.080 | 7.683 | 13.401 | 9.309 | -0.321 |
  | 2024-06-16 | 17.174 | 13.326 | 7.658 | 13.443 | 9.515 | -0.117 |
  | 2024-06-17 | 17.665 | 13.414 | 7.934 | 13.480 | 9.730 | -0.065 |
  | 2024-06-18 | 17.745 | 13.416 | 7.926 | 13.502 | 9.819 | -0.086 |
  | 2024-06-19 | 17.861 | 13.427 | 7.924 | 13.461 | 9.937 | -0.034 |

- **代理边界**: The forcing manifest records fixed cloud fraction, zero evaporation, no river flow, default/proxy ecosystem initial states, and one static measured temperature profile at the start. The profile comparison is therefore not an independent field-validation experiment. The daily observation has no sampling hour and the model/SITES time-zone mapping remains unresolved. The strong measured-vs-modeled vertical-gradient mismatch is a result of this run, not a uniquely diagnosed cause or a validated scientific conclusion. Keep Erken scientific validation **未完成**.

## Next step and guardrails

The local current-version CSV and manifest are already present and the file hash matches its recorded provenance. Preserve the source citation/license and the date-only/time-zone caveats. The comparison is a read-only proxy diagnostic; retain **代理** labeling until a scientifically appropriate, reproducible target-case run and independent validation design exist. Before any new case or run, follow the user's cleanup instruction for prior unwanted generated cases; this check did not start one.

## Overall case status

Erken scientific validation remains **未完成**. The existing exploratory output remains **代理**. No model-observation skill score is reported here.

## Hourly June 2024 observation pairing — 2026-10-25

- **代理 (read-only pairing of an existing output)**: `build/erken-2024-observation-pairing-20261025/` pairs 168 existing hourly outputs from 2024-06-13 14:00 through 2024-06-20 13:00 against hourly SITES temperature profiles. Exact timestamp labels and 50 depths per time yield 8,400 pairs over 1.0–15.5 m. Overall RMSE is 4.208091 °C, MAE 4.033181 °C, and bias (simulated − observed) +0.024272 °C. Mean observed/simulated values are 12.934034/12.958305 °C.
- **Method**: nearest wet cell to station `(j=8, i=36)`, about 0.102131 km away; active GETM levels `k=1..10` represented at adjacent sigma-interface midpoints, time-varying physical depth, and linear vertical interpolation without extrapolation. Residuals are simulated minus observed. The model timestamps have no timezone; they are matched to SITES fixed UTC+01 standard-time labels without daylight-saving adjustment, assuming clock-label equivalence.
- **Initialization cross-check (proxy evidence)**: `initial-profile-audit.json` shows that the static input profile matches the 50 SITES sensor values at 2024-06-13 13:00 exactly (RMSE/max absolute difference 0 °C). By the first output at 14:00, its profile RMSE against that hour's observations is 2.0844 °C with bias −0.6534 °C; against the initial profile mapped to model sigma centers the RMSE is 2.0567 °C, mean change −0.2641 °C, max absolute change 3.1088 °C. This supports correct source/value mapping at 13:00 but shows a discrepancy by the first output after one model hour. Cause remains uncertain; time label, representativeness, vertical mapping, early dynamics, and forcing are possibilities, not established causes.
- **Material provenance defect**: the June run's `Input/source_manifest.json` is stale and describes Jan. 1, 2020 meteorology/profile provenance. The associated `meteo_provenance.json`, `getm.inp`, and `Input/Erken_TW_profile_2024-06-13_1300.txt` refer to June 2024. Therefore this pairing remains **代理 / incomplete provenance**, despite input/output hash checks by the pairing script. Resolve and regenerate the manifest before claiming complete reproducibility.
- **Caveats**: the initial profile at 2024-06-13 13:00 is from the same SITES source; cloud fraction is fixed at 0.5, evaporation is zero proxy, river flow is absent, and most ecological/nutrient initial states are defaults/proxies. Only one nearest wet cell and one 168-hour window are evaluated; there is no independent holdout, horizontal interpolation, or uncertainty propagation. The low net bias does not remove the depth-dependent errors. These metrics are not scientific validation; Erken validation remains **未完成**. This evidence does not establish that the black-bed issue is fixed (it remains **未修复**).
- **Reproducibility artifacts and SHA-256**: see `build/erken-2024-observation-pairing-20261025/README.md`. Observation CSV `2aae84eedebd6722897a331c00d2505681cf98de7966b2e88aaa4ec30211d83e`; model NetCDF `6dc7a0b8fe53d226984796596495cc07af137e65e0139d1fc7c16aae0d40475e`; pointwise pairs `1e8eb8e5f32afad9e0268bac7fc4a42c2c955c3e9219e5f0ebd90d2ff920801b`; by-depth summary `209e094a956f2798ef401a0837a152223c0c13c84642a11201554242f6a74b2b`; summary JSON `1ef807270cda800fcb1803e847e12880fdee37210ed03a4fd56c3b07f9c8480c`.
- **Desktop synchronization**: documentation-only edits do not change application source. A process check found existing `launcher.py --web` services but no matching native desktop launcher; no desktop window was opened or restarted, so current UI synchronization was not visually verified.
