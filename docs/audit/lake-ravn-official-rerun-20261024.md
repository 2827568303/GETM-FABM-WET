# Lake Ravn official-package rerun (2026-10-24)

Status: **代理** rerun and preliminary observation comparison; **未完成** scientific validation.

## Source and run

- Official WET case listing: https://projects.au.dk/wet/cases
- Official package: https://projects.au.dk/fileadmin/projects/wet/testcase_Lake_Ravn.zip
- Downloaded package SHA-256: `4C34001BA96C777C09B936A6A6C140E3454FCBA95003BEDE06B7416C240C92A2`
- Isolated run directory: `build/real-use-validation-20261024/ravn-official-full/run_official_default`
- The official `gotm.exe` exited successfully and generated daily `output.nc` for 1990-01-01 12:00 through 2000-12-31 12:00, 4018 output times and 33 vertical layers. The run log reports GOTM v5.3-680-g1650d26f, WET `218f484`, FABM v0.95.3-298-gf73ec4c. This verifies execution of the supplied configuration, not scientific correctness.
- Official observation files in `official_source/parsac/*.obs` span 1971–2018. A preliminary paired score used only observations from 1996-01-01 through 2000-12-31, after the `wet_obs.xml` configured six-year spin-up. Model values were linearly interpolated in time and vertical coordinate to observation time/depth. Metrics below are exploratory proxy comparisons from the official package, not an independently held-out validation and not a claim of calibration success.

| Variable | Pairs | RMSE | MAE | Bias (model − observation) | Status |
|---|---:|---:|---:|---:|---|
| TEMP | 1688 | 1.1975 | 0.8726 | -0.1002 | 代理 |
| DO | 1673 | 2.9535 | 2.1031 | 1.5235 | 代理 |
| CHLA | 386 | 18.9818 | 9.0817 | 7.1494 | 代理 |
| NO23 | 389 | 0.7769 | 0.6569 | -0.3925 | 代理 |
| NH4 | 385 | 0.2974 | 0.1143 | -0.0973 | 代理 |
| PO4 | 382 | 0.0166 | 0.0121 | 0.0040 | 代理 |
| TOTN | 389 | 0.5215 | 0.4232 | -0.2303 | 代理 |
| TOTP | 381 | 0.0568 | 0.0538 | 0.0503 | 代理 |

## Limits and next evidence needed

This comparison does not reproduce the official calibration workflow or establish independent predictive skill. Confirm output/observation units and aggregation semantics for all totals, verify sample depth and time matching against the official Parsac objective implementation, reproduce the documented calibration, and use a declared independent period before assigning **实测** scientific validation. The official case guide and WET paper describe case-specific setup and calibration/validation context; see the [WET cases](https://projects.au.dk/wet/cases) and [WET 1.0 paper](https://gmd.copernicus.org/articles/15/3861/2022/).
