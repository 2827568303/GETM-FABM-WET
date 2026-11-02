# Lake Ravn official observation pairing: Sol review

Date: 2026-10-21 (Asia/Shanghai)

## Scope

This report covers a direct, read-only replay of the observation parser and native model pairing code plus a later in-app, read-only comparison against the archived official Ravn GOTM-WET default run and workshop `.obs` files. It is not parameter calibration, independent validation, or a current GETM model run. The official model is a 1D representative column.

## Fixed artifacts

- Official replay directory: `build/ravn-official-replay-20261017-attempt01/Default/`.
- Engine: original workshop GOTM/FABM/WET binary; `verification.json` records exit code 0, 5,844 daily outputs (1990-01-01 through 2005-12-31), 32 layers, and 155,083,660 output bytes. It is not the desktop GETM binary.
- Output SHA-256: `8edd2faf797368757b7fd12ae27d02e40f703bdcdb892c00ddc756b2295a51bf`.
- Official `wet_obs.xml` SHA-256: `db1c2583113581bd484df63ede33d725bd82f602117c441c01a1d5b75c04c5e0`.
- Observation files reside in `build/ravn-calibration-research-20261016/QWET_test_case_Lake_Ravn_workshop/OBSERVATIONS/`.
- Input SHA-256: `TEMP.obs` `059f102895e18a9770e14043d624bf4413b78ed7582edd548f9b552341f512e6`; `DO.obs` `582236df6824b1b6c4620cc4db5cddbd0f600b66fe794c2f76a775f69253a95`; `CHLA.obs` `5b065b51b55356711183bb1223d6576d8447b08af447e6f75476805a8aebce67`.
- Added `native_variable_metadata.json` next to the isolated output, hash-bound to that exact NetCDF and based on archived run metadata. This enables source-backed native O2 metadata; the NetCDF bytes were not changed.

## Explicit mappings used for the analysis

| File | Source variable mapping | Observation unit | Model output | Basis / note |
|---|---|---|---|---|
| `TEMP.obs` | `temp` | `degC` | `temp` | Workshop `wet_obs.xml`; negative depths converted to positive-down. |
| `DO.obs` | `abiotic_water_sO2W` | `mg/L` | `abiotic_water_sO2W` | Workshop mapping; source basis explicitly set to O2 for this comparison; native producer metadata attests O2. |
| `CHLA.obs` | `wet_chla_calculator_result` | `ug/L` | same | Workshop `wet_obs.xml`; unit is consistent with the archived native output. |

All three were assigned `lake_id=Ravn`, `point_id=Ravn-column`, positive-down depths, and a 32.65 m review limit to match the explicit GOTM-column comparison target. Observation times have no timezone in source files; this analysis retains source-naive clocks and assumes the original model and observation convention aligns. That assumption must remain visible in any later UI comparison.

## Pairing results and discovered blocker

Before the post-fix verification below, the matcher compared this number with the full interval between adjacent model samples, rather than the distance from the observation time to its nearest model sample. The Ravn output is daily, so a 12-hour setting rejected every in-range observation that fell between daily samples, including observations at the midpoint. The fix now applies the limit to the nearer bracketing sample and still linearly interpolates between samples.

| File | Raw rows | Usable rows | Source diagnostics | Pairs at 12 h | Pairs at 24 h | 24 h RMSE | 24 h bias (sim − obs) | Additional exclusions at 24 h |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `TEMP.obs` | 11,904 | 11,832 | 19 conflicting duplicate groups | 0 | 5,813 | 1.928 °C | −1.129 °C | 5,852 outside model time; 166 outside model layer centers; 1 physical-range review. |
| `DO.obs` | 11,680 | 11,622 | 14 conflicting duplicate groups | 0 | 5,704 | 2.729 mg/L (numerically equivalent to g O2/m³) | +1.130 mg/L | 5,755 outside model time; 163 outside model layer centers. |
| `CHLA.obs` | 1,420 | 1,420 | none | 0 | 1,063 | 26.406 µg/L | +8.810 µg/L | 346 outside model time; 11 outside model layer centers. |

The 24-hour statistics are a diagnostic comparison of the official default run, not a calibration score or scientific acceptance. The data span dates outside the run and were historically used by the official workflow; no independent train/holdout claim is made. Pair counts exclude conflicting duplicate observations and rows flagged for review.

## In-app Ravn comparison and remaining limits

The running desktop app now supports opening the native replay folder as a read-only GOTM result and comparing selected `.obs` data against an explicit representative water column. It retains the source `h`/`z` layer geometry and does not create station coordinates, a CRS, or a GETM grid cell. The UI hides GETM point editing, run, observation apply, and automatic-calibration controls while this read-only case is active. It exposes per-file mapping and only variables present in the selected native output.

The actual UI workflow selected the complete official `TEMP.obs` file (SHA-256 `059f102895e18a9770e14043d624bf4413b78ed7582edd548f9b552341f512e6`), explicitly mapped it to model variable `temp` and unit `degC`, and used a 12-hour maximum nearest-sample distance. The UI displayed the source filename, hash, pairing plot, exclusions, and processing time. It produced 5,813 pairs from 11,904 source rows against 5,844 native daily outputs (1990-01-01 through 2005-12-31). The API reported `processing_ms` 678 ms; browser-observed end-to-end time was about 1.38 s.

The application was serving this verification on instance `5f0b0366...` (PID 15372); Sol verified the app healthy and the actual page response. Opening the Ravn folder did not create entries in the source directory. Attempts to change case configuration were rejected in read-only mode. This verifies the route and UI behavior, not scientific validity.

Pair counts depend on source selection: the full workshop file above yields 5,813; the curated `selected_postspinup_obs/TEMP.obs` file (SHA-256 `ec8286accde6fcc65f29bc46e58b380d90412bb970e341d2e7abaff0d78705c0`) contains 3,540 post-spinup records and yields 3,467 pairs, with 73 depths outside model layer centers. The curated file is a different input row set and must not be treated as a mismatch in the full-file UI result.

## Post-fix verification (2026-10-21)

- Focused verification: `tests/test_observation_matching.py`, `tests/test_observation_routes.py`, and `tests/test_observations.py` pass (**36 passed**). The regression covers a midpoint observation between daily samples at a 12-hour nearest-sample limit, and rejection when the nearest sample is farther away.
- Replaying the official `TEMP.obs` against the same official daily output at 12 hours now yields **5,813 pairs**, with the same RMSE (1.928 °C) and bias (−1.129 °C) as the 24-hour replay. This confirms the threshold semantics fix; it does not change the scientific interpretation of the diagnostic scores.
- The running desktop app was synchronized to the updated source (instance `fbcb50bd210e4fdebdb0ec17994fe62e`, PID 45224) and reported ready/idle. In the real UI, a read-only preview was generated for `CHLA.obs`, `DO.obs`, and `TEMP.obs`, each with its own explicit model-variable and unit mapping. The preview displayed file hashes and row diagnostics. It was not applied to the current `competition_treatment` case.
- The earlier UI preview tested per-file mapping only; the later in-app read-only comparison above verified the 1D representative-column path.
- These results use the archived official default run. They are pairing diagnostics only, not calibration, independent holdout validation, or a current GETM run.

## Follow-up: packaged `temp_do` replay (2026-10-22)

The separately supplied official `calibrated_config/gotm-temp_do.yaml` and `fabm-temp_do.yaml` were compared with the default files and run in isolated copies using the workshop's official GOTM-WET executable. Their upstream provenance is the official `calibrated_config.zip` and duplicate copies in the official workshop ZIP. `wet_obs.xml` maps TEMP to `temp`, DO to `abiotic_water_sO2W`, and declares six spin-up years. The package makes seven active GOTM parameter value changes and nine FABM parameter value changes; exact paths/values, archive and file hashes, output checks, and logs are recorded in the [Ravn packaged TEMP/DO replay report](../../../build/real-use-validation-20261022/ravn-temp-do-review/REPORT.md).

Both isolated runs completed all 5,844 daily records and 32 layers with no unmasked non-finite output values. With identical 1996–2000 and 2001–2005 diagnostic windows, packaged TEMP RMSE changed from 1.953 to 0.800 °C and 1.966 to 0.889 °C; DO RMSE changed from 2.240 to 2.291 mg O2/L and 2.451 to 2.270 mg O2/L. **The 2001–2005 values are not holdout validation:** no inspected source documents the package's fitting dates or establishes that this period was excluded from fitting. The package is an upstream-supplied TEMP/DO configuration; it is not evidence of our requested split fit, a reproduction of official ParSAC, or validation of GETM 3D. Packaged DO reached 36.33 mg O2/L and the run repaired interior FABM state 230,813 times; both are physical/numerical review items.

The previous single-parameter experiment remains distinct and nonconverged. This packaged-config replay does not promote it to calibration.
