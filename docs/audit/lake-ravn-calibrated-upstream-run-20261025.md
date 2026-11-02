# Lake Ravn upstream calibrated-config run audit (2026-10-25)

## Status

- **实测（运行执行）**：the official upstream GOTM-WET `gotm_release.exe` completed a 1990-01-01 12:00 to 2005-12-31 12:00 run in an isolated directory. It produced 5,844 daily outputs over 33 vertical layers; all cells in the eight expected temperature, oxygen, nutrient, chlorophyll and total nutrient fields checked here were finite.
- **未完成（Lake Ravn scientific validation）**: this is a one-dimensional upstream reference executable, not the repository's target 3D GETM application. The extracted `wet_obs.xml` names `pclake_*` CHLA/TOTN/TOTP outputs that do not exist, but the companion official `parsac/wet_cal.xml` explicitly maps those same observations to the generated `wet_*` outputs. Exact WET source `943d3c40` confirms the `wet_totN`/`wet_totP` aggregation contributors, so the name mapping is now source-backed rather than guessed. The aggregate NetCDF unit strings are still blank; units/bases below use the official configuration and source-defined contributor semantics. The fit check is on the upstream 1D calibrated configuration, not an independent holdout or target 3D validation. State repairs remain unexplained.
- **未完成（solver state-quality audit）**: the log reports 249,644 FABM interior-state repairs, zero surface repairs, and zero bottom repairs. The run exits successfully, but that repair count needs interpretation and a variable/time breakdown before the output can be treated as physically trustworthy.

The checked-in GOTM/FABM host wrapper increments `repair_interior_count` once when an interior `fabm_check_state` call returns invalid (`3DWET/src/gotm/src/fabm/gotm_fabm.F90`, around line 1697); FABM then clips invalid state values to configured bounds (`3DWET/src/fabm/src/fabm.F90`, around lines 3499–3512). This counter is a count of invalid check calls, not a count of variables, cells, or the magnitude of the corrections. The available summary does not identify which state or how far it was clipped, so no stronger interpretation is justified.

## Provenance and run evidence

- Official case listing: https://projects.au.dk/wet/cases
- Official Lake Ravn test-case archive: https://projects.au.dk/fileadmin/projects/wet/testcase_Lake_Ravn.zip
- Official workshop page with calibrated parameter configuration: https://projects.au.dk/wet/gleon-gsa-limnoseries-wet
- The isolated input directory is `build/real-use-validation-20261025/lake-ravn-official-calibrated-run-1990-2005/`.
- Run log: `official-calibrated-run.log`; process exit code was 0. The log records 140,232 micro time steps and warns that `/output` is ignored because `output.yaml` is present. The output file is at the case root.
- Runtime versions recorded during this run: GOTM `v5.3-679-gc0add0a2-dirty (au branch)`, WET `943d3c4 (master branch)`, FABM `v0.95.3-298-gf73ec4c (au branch)`, Intel 18 compiler. The abbreviated WET revision resolves to public upstream commit [`943d3c40`](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/commit/943d3c4), titled “Minor revision to chladummy to allow debug compilation.” This anchors the source used to establish aggregate semantics; it does not resolve the blank raw NetCDF unit attributes, state-repair interpretation, or validate the target 3D application.
- SHA-256: `gotm.yaml` `98A58430FA6AB225E1F5A0595EC5940C5FD26B4E809A8F0C956049E9BE79CD9F`; `fabm.yaml` `C6092806E7448F492FAE79274239BB03CBAB08A14B3AB3B8756B67B8FB79EF6D`; `output.nc` `7671A674FFC36B5936B1A1FC136716627BE9D8F1F16AC888AFA94DE61812FFE9`; `official-calibrated-run.log` `EF78A9263C970F6CC0C216155D423283059900D34AE47A8365FA05C899B27822`.

## Output-to-observation mapping and source audit

- The copied `wet_obs.xml` maps CHLA/TOTN/TOTP to historical `pclake_*` names. Its companion [`parsac/wet_cal.xml`](../../build/real-use-validation-20261025/lake-ravn-official-wet/parsac/wet_cal.xml) explicitly maps CHLA→`wet_chla_calculator_result`, TOTN→`wet_totN_calculator_result`, and TOTP→`wet_totP_calculator_result`; it also maps NO23, NH4, and PO4 to their WET state variables. This supplies a provenance-backed mapping for this official calibrated configuration.
- At exact upstream WET commit [`943d3c40`, `abiotic_water.F90`](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/943d3c40/src/abiotic_water.F90), `wet_totN` aggregates particulate/dissolved organic N, NH4, and NO3; `wet_totP` aggregates PO4, adsorbed P, and particulate/dissolved organic P. [`phytoplankton.F90`](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/943d3c40/src/phytoplankton.F90) and [`zooplankton.F90`](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/blob/943d3c40/src/zooplankton.F90) add their explicitly `gN/m3` and `gP/m3` state pools. The abiotic contributor unit strings are generic `g/m3`, and the aggregate output unit attributes are blank; the elemental aggregate basis is supported by their N/P names, process fluxes, and the official calibration mapping, while the raw NetCDF metadata remains incomplete.
- The official [WET observation-file guidance](https://projects.au.dk/wet/resources) says values use units corresponding to model output, giving temperature in Celsius, nutrients/oxygen in mg/L, and chlorophyll-a in μg/L. Since 1 g/m³ = 1 mg/L, the aggregate fit calculation uses the model's elemental gN/m³ or gP/m³ numerically as mgN/L or mgP/L. This is a source-backed configured comparison, but the released `.obs` records themselves do not carry per-file unit/basis headers.

Hashes for the exact profile inputs and mapping artifacts used here:

| File | SHA-256 |
|---|---|
| `wet_obs.xml` | `680078B3EA97510DC1CC35DBB7239BF6B6305C1EAE8F85CDB7CE8EDBF4B24C3B` |
| `parsac/wet_cal.xml` | `8A37AD973CD056D0F0A0E118EE9FF9F68D823FBAEA88CFB5EAA3ECD39D3BFEFA` |
| `TEMP.obs` | `059F102895E18A9770E14043D624BF4413B78ED7582EDD548F9B552341F512E6` |
| `DO.obs` | `582236DF6824B1B6C4620BCC4DB5CDDBD0F600B66FE794C2F76A775F69253A95` |
| `CHLA.obs` | `5B065B51B55356711183BB1223D6576D8447B08AF447E6F75476805A8AEBCE67` |
| `NO23.obs` | `3E73C13590BC84AF90C06E73BE76337BB62B851433EE5660F7399FC860CFFC8B` |
| `NH4.obs` | `8A3323050BB3FF3D9CC201223B91426633AF2E782863761A58CAC42D703658A3` |
| `PO4.obs` | `467F224F1E8AE85BF1F1C4EF6B6C68DEF9339974B330C21C9F895A8FFCED3C61` |
| `TOTN.obs` | `4AFB7D01C24E6A8087F395D1FAF9C7A12F9D2D186591BECF5537362AC9CC5274` |
| `TOTP.obs` | `299B5C2A87B33ED02D5F2F0FDE7BB1160300B927855CBF2D2F46E1307D3EFEA9` |

## Post-spin-up profile-fit diagnostics (proxy, not target-case validation)

I compared the official measured `.obs` records to the official calibrated 1D output after the configured six-year spin-up (`1996-01-01` onward), interpolating linearly in time and between model depth centers. I treated observation timestamps as using the model case time basis; the `.obs` files do not declare a timezone. I did not extrapolate outside the model time/depth range. The model has one horizontal column and vertical centers from −32.371 m to −0.649 m. Surface observations at −0.2 m and deeper records such as −99 m are therefore excluded. No duplicate time/depth keys remain in the matched evaluation subset.

| Official observation | Configured model output | Matched records | Bias (model − observed) | RMSE | MAE | Unit/interpretation |
|---|---|---:|---:|---:|---:|---|
| TEMP | `temp` | 3,359 | −0.257 | 1.064 | 0.848 | °C |
| DO | `abiotic_water_sO2W` | 3,306 | +0.396 | 1.859 | 1.285 | mg/L (numeric g/m³) |
| CHLA | `wet_chla_calculator_result` | 573 | −1.719 | 4.418 | 3.081 | μg/L |
| NO23 | `abiotic_water_sNO3W` | 642 | +0.020 | 0.253 | 0.197 | mg/L numeric; official proxy to nitrate only, observation basis undocumented |
| NH4 | `abiotic_water_sNH4W` | 638 | −0.046 | 0.239 | 0.096 | mg/L numeric; raw observation basis not declared |
| PO4 | `abiotic_water_sPO4W` | 637 | +0.0007 | 0.0103 | 0.0075 | mg/L numeric; raw observation basis not declared |
| TOTN | `wet_totN_calculator_result` | 646 | −0.320 | 0.473 | 0.382 | model basis gN/m³; obs basis inferred from official mapping, not written in raw file |
| TOTP | `wet_totP_calculator_result` | 635 | +0.0027 | 0.0323 | 0.0149 | model basis gP/m³; obs basis inferred from official mapping, not written in raw file |

All rows are **代理（official calibrated 1D output compared with measured observations）**. The metric subset is within the configured model period and depth range; it is not an independent validation split. The official workshop material distinguishes temperature/DO and all-observation calibration configurations, but this packaged run does not record an auditable training/holdout split. Raw NH4/PO4 observation basis and total aggregate NetCDF unit attributes remain undocumented in the files. Do not present these diagnostics as validation of the target 3D GETM application. The unexplained 249,644 FABM interior-state repairs remain a material model-output quality issue.
