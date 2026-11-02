# Bryrup legacy binary compatibility check (2026-10-25)

## Candidate examined

The archived official Ravn executable was checked as a possible exact-era runner for the WET v0.1.0 Bryrup configuration. The executable is `build/real-use-validation-20261022/ravn-default-calibration-source/case/gotm_release.exe`, SHA-256 `9840DC304B5F1D013CBD10861CE1DA14D992C3555DB1EC930F32D8F95121B6E4`. Its recorded runtime identifies GOTM `v5.3-679-gc0add0a2-dirty` (`au`), FABM `v0.95.3-298-gf73ec4c` (`au`), and WET `943d3c4` (`master`). The WET commit resolves to `943d3c4023c9f8a6082ac64749b57212784abebc`, dated 2020-04-06.

This WET source still declares and uses the old `cCPerDWS` sediment parameter, unlike the current product WET module. However, the commit's `wet_model_library.F90` registers fish models as `fish_mod` and `fish_dist`; it does not register the Bryrup archive's requested `wet/fish` model. Source-level parameter-set comparison also found missing case parameters in both fish candidates, plus `qTrans` in `phytoplankton` and `cPref1/2/3`, `lSi2`, and `prey_suffix1/2/3` in `zooplankton`. The old `abiotic_water`, burial, macrophyte and resuspension parameter sets were present; this does not resolve the missing modules/parameters.

An earlier preflight with this executable already stopped with `"wet/fish" is not a valid model name`. Mapping that module to a similarly named implementation or deleting unsupported parameters would change or leave unknown trophic behavior, so it is not a valid compatibility repair. This confirms the candidate is unsuitable for the case as supplied; it does not show that the WET v0.1.0 case itself is invalid.

## Result and status

- Candidate binary/source version check: **实测** (artifact/log inspection only; not scientific validation).
- Bryrup full-case execution and paper reproduction: **未完成**.
- No new solver case was launched and no source/configuration was altered by this check.
- A compiler toolchain is not available in the current environment (`gfortran`, `ifx`, `ifort`, `flang`, CMake and Ninja were not found), so no version-matched WET v0.1.0 binary was built here.

Sources: official WET v0.1.0 files in the [recovered release audit](../../../build/academic-case-validation-20261023/arreskov-v010-recovery/RECOVERY_AUDIT.md); the mirrored WET source commit in `build/arreskov-wet-mirror-audit-20261022.git`; and the candidate binary's recorded runtime log in `build/real-use-validation-20261022/ravn-knitrw-profile-20261022/runs/grid_11_0.30/model_run.log`.

## Official release route recheck (2026-10-25)

The current official WET project documentation identifies v0.1.0 as the 5 June 2021 stable release and points to the historical `WET/wet` release; it states that v0.1.0 included the backwards-compatible PCLake-style fish module. The current project has since replaced that repository, and the official tags page now lists the maintained project's newer v0.2.x tags. This confirms a plausible versioned source route, but does not provide a verified Windows executable or establish compatibility of any available binary with the archived Bryrup case. No source archive was built or case launched in this recheck.

- Official current WET documentation: https://gitlab.com/wateritech-public/waterecosystemstool/wet
- Official current WET tags: https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/tags
- Exact-era executable/build availability: **不确定**; the public pages found here do not establish a downloadable matching executable.
- Bryrup execution and scientific reproduction: **未完成**.

## Existing smoke output overlap check (2026-10-25)

The existing one-day `bryrup-wet1-stim-one-day/output.nc` was inspected read-only. Its two temperature time records span `1990-01-01 12:00` through `1990-01-02 12:00` (`seconds since 1990-01-01 12:00:00`); it is an engineering smoke output, not the 1996–2006 evaluation run. The official station 21000361 temperature CSV has 1,676 rows on 226 dates, from `1996-01-25 10:30` through `2006-12-12 14:00` local timestamps. These intervals do not overlap, so no temperature score can be computed from this output without extrapolation. This is **实测** file/metadata inspection plus **实测** observation-data acquisition, not model validation. Bryrup science validation remains **未完成**; do not start a replacement case without first inventorying and cleaning only clearly disposable prior cases.

## Exact WET v0.1.0 archive and Bryrup case presence (2026-10-25)

Correction/clarification: the official WET v0.1.0 Zenodo archive is already recovered locally (record DOI `10.5281/zenodo.4903142`, archive SHA-256 `B238D49CED074CA9297DC8FF2AD26A3F6E6DA4A0642138458B5D3B8B5EF17CE1`). It **does include** a complete dated Bryrup case directory with `fabm.yaml`, `gotm.yaml`, `output.yaml`, `inflow.dat`, `inflow_chem.dat`, `outflow.dat`, `meteo_file.dat`, and `hypsograph.dat`. The ecological and physical config hashes are respectively `CA2B3F18D2E76797BD049BE9F35C670200246C27725E1B69B41A50A4B4081E78` and `FE310E46548DF2407B45973886D116BE427129C942B0D3B925D0364F7F7E8AFE`; see `build/academic-case-validation-20261023/arreskov-v010-recovery/extracted/wet-v0.1.0/testcases/lake_bryrup_denmark/`.

This corrects any reading of the prior notes as saying the old archive lacks a Bryrup configuration or forcing files. It does **not** establish that this generic versioned archive is identical to a later published calibration/validation configuration, prove the case can execute in the current product runner, or supply the missing 1996–2006 matched output. The candidate archived Ravn executable remains incompatible with this config (`wet/fish` model name and parameter mismatch); no substitution was made. The current environment check again found no `cmake`, `ninja`, `gfortran`, Intel Fortran, Flang, or MSVC `cl` command on PATH, so the exact archive was not built here. No solver case was started.

- Archived WET source and Bryrup files: **实测** artifact/file inspection.
- Bryrup execution and scientific validation: **未完成**.
- Next executable route remains **不确定** until an exact compatible GOTM/FABM/WET toolchain is obtained or the historical Windows package is recovered. Before any future case start, first identify and remove only prior disposable generated cases; preserve source archives, user cases, and evidence.

## WSL toolchain and historical source snapshot recheck (2026-10-25)

A Windows-only PATH check is not the whole machine state: Ubuntu 22.04 WSL is installed and provides CMake 3.22.1, GNU Fortran 11.4.0, GCC 11.4.0, Make, and Git. Therefore the earlier statement that no compiler/build tools were available is narrowed to the native Windows PATH; a source build is technically possible in WSL.

The public historical GOTM clone was also checked at its final pre-migration development commit `2895ac9449a2d2bfc31ba9f23406c6d841910d36` (2021-11-25). It reports 5.3.0 in `src/CMakeLists.txt` while the outer CMake project identifies 5.4.0; neither identifies the paper's GOTM 5.2.2-au. The reachable FABM history includes commit `39101776e36f166380d62c452c4dabd64b174e40` (2021-04-27), but the public migrated repositories expose no `au` branch ref. These sources may support a version-mismatched compatibility build, but cannot establish the paper's pinned runner. No build or model case was started in this recheck.

This changes the blocker from “no compiler present” to “the published exact GOTM 5.2.2-au/FABM source snapshot and pinned recursive dependencies are not yet recovered.” The WSL toolchain makes compilation feasible once the provenance decision is resolved; it does not make a different version scientifically equivalent. Bryrup execution/scientific validation remains **未完成**.

## Observation overlap and comparison feasibility (2026-10-25)

A read-only count of the acquired official Bryrup field-measurement CSV finds, from 1996-01-25 through 1999-12-08, 622 temperature rows on 83 dates and 620 oxygen rows on 82 dates. The historical WET v0.1.0 forcing files `meteo_file.dat`, `inflow.dat`, and `inflow_chem.dat` extend through 1999-12-31, while its unmodified `gotm.yaml` run stops on 1995-12-31. This creates a potential four-year comparison window only if a separately identified derivative run is explicitly extended; it does not change the archived case and no such run has been made. Sampling times carry Danish UTC offsets and profile depths, so timestamp conversion, vertical interpolation, data-quality handling, and unit conventions remain necessary before scoring.

The published WET 1.0 Bryrup setup is specifically the 1D GOTM lake branch (18 layers of 0.5 m, with attached sediment layers), whereas this product's interactive target is GETM 3D. Treat a faithful paper reproduction and a product GETM 3D application as distinct validation questions; one must not be substituted for the other. Source: [WET 1.0 paper](https://gmd.copernicus.org/articles/15/3861/2022/).

- Observation rows/counts: **实测** (CSV inspection).
- Existing model run within the 1996–1999 observation window: **未完成**.
- Bryrup model-observation pairing and science validation: **未完成**.

## Reproducible 1996–1999 observation extract

A separate normalized file now preserves the original station record number, parameter, local sample date/time and explicit UTC offset, derived UTC timestamp, depth, numeric value, original and normalized qualifier, source unit, quality marker, and source record link: `build/bryrup-observations-1996-1999-normalized-20261025/bryrup-station-21000361-temp-oxygen-1996-1999.csv`. Its README records the filter and limits. The 1,242-row extract was re-read and checked: required cells missing 0; local-to-UTC mismatches 0; local-date mismatches 0; duplicate groups for parameter + local timestamp + depth 0. CSV SHA-256: `B89EE6D96FEB0C737B8104FD69429566F630267A3281EF25F9D3707A0406BD8F`.

The extract is **实测** source-data handling only. No model output was paired, no score was calculated, and no case was started or removed.

## Published exact GOTM release pointer (2026-10-25)

The WET 1.0 paper's software-availability section names the exact GOTM release URL `https://gitlab.com/WET/gotm/-/releases/v5.2.2-au`. The AU developer page continues to document the required GOTM `au`/FABM `au`/WET `master` source workflow and says GitLab download requires a free account. An anonymous open of the exact release URL currently redirects to GitLab sign-in. This establishes a published, version-specific recovery pointer; it does not establish whether the release/archive is still downloadable after authenticated access, nor reveal a commit hash or recursive submodule pins. The current migrated public clone has no reachable `5.2.2` string/tag and its visible history does not identify that release.

Sources: [WET 1.0 software availability](https://pure.au.dk/ws/files/333228766/1_s2.0_S1364815222002043_main.pdf); [AU WET developer instructions](https://projects.au.dk/wet/for-developers/); [published release URL](https://gitlab.com/WET/gotm/-/releases/v5.2.2-au).

Status: exact release pointer **实测（文献/官方说明）**; anonymous archive retrieval **未完成**; availability after sign-in and exact source commit **不确定**. No login/session was attempted and no model case was run.
