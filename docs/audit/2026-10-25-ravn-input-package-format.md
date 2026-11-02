# Lake Ravn official package format comparison

Date: 2026-10-25 (Asia/Shanghai)

## Finding

The disposable directory `build/real-use-validation-20261025/lake-ravn-official-validation-1990-2005/` was copied from the official workshop `testcase_Lake_Ravn.zip` and configured for 1990-01-01 through 2005-12-31. Its solver stopped before the first integration step with `Error reading time series from inflow_chem.dat at line 1`.

This is explained by an input/configuration mismatch in that archive, not by a model-state or scientific result:

- The archive's `inflow_chem.dat` contains five concentration values after the timestamp. Its first record is `1990-01-01 00:00:00 6.4634 0.5975 0.6983 0.0777 0.0252` (SHA-256 `8DE00A9D84EDF80B6712C702AFE7B51F474EB75A640C4602055496B38B6883BE`).
- The paired `gotm.yaml` maps seven inflow chemistry variables to this file, including nitrate, ammonium, particulate/dissolved organic nitrogen and phosphorus. The seven file-backed inputs request columns 1–7; silica is separately configured as a constant and does not add a file-backed column.
- In `3DWET/src/gotm/src/input/input.F90`, `read_obs` reads one value for each variable attached to the same time-series file. If the record ends early, it converts the end-of-record status to a read error. Thus the five-value record cannot satisfy the seven-variable reader request.
- The recorded run log confirms the first-line failure. No `output.nc` or scientific metric was produced; this attempt is **未完成**, not a Lake Ravn model result.

The separately downloaded official `default_lakeRavn_setup.zip` carries a complete seven-value `inflow_chem.dat` record and a matching column mapping. Its first record includes the two zero-valued organic-pool inputs missing from the test-case archive. The default ZIP SHA-256 is `A6AB09C604ED39C802CF7567482EB81FA09BB196C9D1127EB6DD582FE1DB827E`. A prior isolated working copy from this default package completed the 1990–2005 GOTM-WET run and has its own `run_report.json`; it is the reusable result source for subsequent Ravn diagnostics, so this audit does not repeat the solver run.

## Evidence and scope

| Evidence | Status |
|---|---|
| Exact archive/input/config file comparison and parser source inspection | **实测** (file and code inspection) |
| `testcase_Lake_Ravn.zip` run | **未完成** (failed before integration; no output) |
| Prior full-period run from `default_lakeRavn_setup.zip` | **实测** (solver execution/output coverage only; not by itself independent scientific validation) |
| Lake Ravn science validation | **未完成**; official calibrated files' training dates and an independent holdout are still not established |

The official WET resources distinguish the complete default setup with model executables from the workshop case materials and provide calibrated parameter sets, but this file comparison does not identify which parameter values were fitted to which dates. Do not use an observation period for an independent validation claim unless its separation from calibration is supported by the source configuration or an explicitly documented new study design.

No inputs were edited, no new case was created, and no solver was started for this comparison. The failed disposable attempt and prior successful output were preserved. The desktop source was not changed, so no application synchronization was needed.

## Sources

- Aarhus University WET resources and Lake Ravn packages: [WET resources](https://projects.au.dk/wet/resources), [Lake Ravn case](https://projects.au.dk/wet/cases), and [GLEON workshop materials](https://projects.au.dk/wet/gleon-gsa-limnoseries-wet).
- Parser behavior: `3DWET/src/gotm/src/input/input.F90`, `read_obs` and `timeseries_file_update`.
- Failed run log: `build/real-use-validation-20261025/lake-ravn-official-validation-1990-2005/official-validation-run.log`.
- Reusable full-period run record: `build/ravn-official-working-copy-run-20261021-attempt01/run_report.json`.
