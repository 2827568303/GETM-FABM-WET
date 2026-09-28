# GETM-FABM-WET Debug History Report

## Overview

This report summarizes the debugging history of the **GETM-FABM-WET** project, which couples the GETM 3D hydrodynamic model with the FABM framework and the WET (Water Ecological Tool) lake ecosystem model, applied to Luomahu Lake (骆马湖). The development spans compiler issues, host-model interface patches, food-web configuration coupling, and boundary-condition setup. The debug history is recorded across a dated log (`debug_log_20240628.md`), a large collection of `check_*.py` / `fix_*.py` / `run_*.py` scripts, and several patched Fortran source files (`.F90`) kept at the repository root.

The recurring theme is that the WET model exposes host-model gaps: variables it depends on (`time_step`, `bot_pel_conv`, pelagic-mirror `_PV` state) were not provided or correctly linked by the standard GETM-FABM interface, leading to segfaults and fatal coupling errors. Debugging proceeded via an iterative *run → parse FATAL ERROR → auto-fix config → rerun* loop and via incremental module addition to isolate the breaking module.

---

## 1. Compilation / Build Problems

### 1.1 GCC 13.3.0 Internal Compiler Error (ICE)
- **Symptom**: GCC 13.3.0 aborts with an internal compiler error while compiling `gotm_fabm.F90`.
- **Root cause**: Compiler bug in GCC 13 for this Fortran source; not a source-code error.
- **Fix**: Installed GCC 9.5.0 and rebuilt FABM + GETM with `build_gcc9_v5.sh`. An alternative test (`test_gcc13_O0.py`) tried GCC 13 with `-O0 -g` (Debug build) to bypass the ICE.
- **Related files**: `3DWET/scripts/debug/test_gcc13_O0.py`, `debug_log_20240628.md`, `install_gcc9_v5/bin/getm_cartesian`.

---

## 2. Data Format / NetCDF Problems

### 2.1 Bad Attributes in `rivers.nc`
- **Symptom**: River forcing file contained erroneous `temp` attributes that confused the GETM reader.
- **Root cause**: Original `rivers.nc` was generated with extra/incorrect variable attributes.
- **Fix**: `fix_rivers_format.py` recreates the file from scratch with clean dimensions (`time`), correct units (`m3 s-1` for flow, `mmol m-3` for nutrients) and no spurious `temp` attributes; copies result to `rivers.nc`.
- **Related files**: `3DWET/scripts/fix/fix_rivers_format.py`.

### 2.2 Masked-Array Output Inspection
- **Symptom**: 2D/3D NetCDF outputs (`LUOMAHU_WET.2d.nc`, `LUOMAHU_WET.3d.nc`) are NumPy masked arrays; naive reads gave misleading NaN/mask counts.
- **Root cause**: GETM masks dry land cells; analysis scripts must handle `.mask` and use `.filled(np.nan)`.
- **Fix**: A family of `check_*.py` scripts (`check_2d_vars.py`, `check_vars.py`, `check_3d_vars.py`, `check_2d_3d.py`, `check_0idx.py`) inspect shapes, dims, units, mask counts, and valid-cell ranges to verify output integrity.
- **Related files**: `luomahu_case/check_2d_vars.py`, `luomahu_case/check_vars.py`, `luomahu_case/check_sigma.py`, `3DWET/scripts/analysis/check_2d_3d.py`, `check_3d_vars.py`, `check_bathy_detail.py`.

---

## 3. River / Boundary Condition Problems

### 3.1 River Positions Falling on Land
- **Symptom**: Several rivers in `riverinfo.dat` pointed to land cells (bathymetry <= 0), e.g. DAYUN at (35,5) and LUONAN at (3,23) were dry; the model produced no valid river input there.
- **Root cause**: River (j,i) coordinates were guessed, not verified against the bathymetry grid.
- **Fix**: `fix_river_positions.py` reads `bathymetry.nc`, scans each row for water cells, and rewrites `riverinfo.dat` with corrected coordinates (e.g. DAYUN→(35,15), LUONAN→(3,28), ZHANGSHAN→(13,30)). `luomahu_case/check_rivers.py` validates the result.
- **Related files**: `3DWET/scripts/fix/fix_river_positions.py`, `fix_river_pos.py`, `luomahu_case/check_rivers.py`, `check_rivers_detail.py`.

### 3.2 ERHE River on Wrong Row
- **Symptom**: ERHE at j=51 was land (depth=-10 m).
- **Root cause**: Off-by-one row error.
- **Fix**: `fix_erhe.py` moved ERHE to j=50, i=15 (valid water, depth>0) and rewrote `riverinfo.dat`.
- **Related files**: `3DWET/scripts/fix/fix_erhe.py`.

### 3.3 `riverinfo.dat` Column-Order / Indexing Ambiguity
- **Symptom**: Uncertainty whether `riverinfo.dat` uses `i j` or `j i` ordering and 0- vs 1-based indexing.
- **Root cause**: GETM documentation ambiguity for the cartesian river format.
- **Fix**: `swap_riverinfo_order.py` tested `j i` order; `check_0idx.py` verified output against 0-indexed assumptions; final working format is `j i NAME -1 -1` (1-based).
- **Related files**: `3DWET/scripts/fix/swap_riverinfo_order.py`, `fix_riverinfo_idx.py`, `3DWET/scripts/analysis/check_0idx.py`.

---

## 4. FABM Ecological Model Configuration Problems

### 4.1 `time_step` Dangling Pointer (Critical Segfault)
- **Symptom**: Segfault (`SIGSEGV`) in `fabm_update_time1` / `calculate_derived_input` whenever phytoplankton (which needs `temporal_mean` of PAR) or the fish module was active. Abiotic-only runs worked.
- **Root cause**: `time_step` was linked to the **local** `dt` parameter of `init_gotm_fabm`. When that subroutine returned, the local variable went out of scope, leaving FABM reading freed memory.
- **Fix**: Move the `time_step` link to `set_env_gotm_fabm`, immediately after `dt = dt_`, so it points to the **module-level** `dt` that persists for the whole simulation. The `time_step_id` is still looked up in `init_gotm_fabm` but only *linked* later.
- **Related files**: `gotm_fabm_itime_fixed.F90`, `3DWET/scripts/fix/fix_time_step_dangling.py`, `fix_time_step_dangling_v2.py`, `fix_time_step_dangling_v3.py`, `debug_log_20240628.md`.

### 4.2 Missing `bot_pel_conv` Host Variable
- **Symptom**: WET benthic modules (zoobenthos, macrophytes, `om_pool`) require `bot_pel_conv` (benthic-pelagic conversion factor = 1/dz) to scale `_PV` (pelagic-mirror) bottom exchanges, but the GETM-FABM interface did not provide it → unfulfilled dependency.
- **Root cause**: Standard GETM-FABM host never linked `bot_pel_conv` as a bulk standard variable.
- **Fix**: Patch `getm_fabm.F90` to allocate `bot_pel_conv_col(kmax)`, compute `_ONE_/max(hn,1e-6)` per layer inside the column loop, and `link_bulk_data` it. `om_pool_patched.F90` registers the matching `id_bot_pel_conv` horizontal dependency and applies it in `_SET_BOTTOM_EXCHANGE_` for `sDS_PV`/`sNS_PV`/`sPS_PV`/`sCS_PV`.
- **Related files**: `getm_fabm_patched.F90`, `getm_fabm_v2_patched.F90`, `om_pool_patched.F90`, `3DWET/scripts/fix/patch_bot_pel_conv.py`, `patch_bot_pel_conv_v2.py`, `fix_bot_pel_conv_link.py`.

### 4.3 Missing `_PV` (Pelagic-Mirror) Couplings (~24 variables)
- **Symptom**: FABM fatal error `Variable <inst>/<name> must be coupled to an existing state variable.` for many `_PV` variables (e.g. `POM_DW_pool_sediment_PV`, `DOM_N_pool_sediment_PV`).
- **Root cause**: The WET template `fabm-wet.yaml` did not declare the pelagic-mirror couplings that benthic and consumer modules need to exchange sediment↔water fluxes.
- **Fix**: Iterative scripts parse each `FATAL ERROR` line, infer the target (e.g. `POM_DW_pool_sediment_PV` → `POM/sDS_PV`), add the coupling to `fabm.yaml`, and rerun — looping until the model integrates. `fix_pv_couplings.py` applies a static map of 13 known `_PV` targets; `fix_nofish_iterative.py` / `fix_and_test.py` / `fix_foodweb_config.py` automate the run-parse-fix loop.
- **Related files**: `3DWET/scripts/fix/fix_pv_couplings.py`, `fix_pv_couplings_v2.py`, `fix_pv_iterative.py`, `fix_all_pv.py`, `fix_dom_pv.py`, `fix_nofish_iterative.py`, `fix_and_test.py`, `luomahu_case/fix_foodweb_config.py`.

### 4.4 Fish Module `time_step` Dependency
- **Symptom**: Fish modules (`JuFish`, `AdFish`, `PiscFish`, model `wet/fish`) declare `id_time_step`; combined with the dangling-pointer bug they caused persistent segfaults even after phytoplankton was fixed.
- **Root cause**: `wet_fish.F90` registers a `time_step` dependency that the host linked unsafely.
- **Fix attempts** (escalating): (a) `getm_fabm_patched.F90` v1 added per-column `time_step_col` linking; (b) `fish_v2_patched.F90` / `fish_v3_donothing.F90` **removed** the `id_time_step` declaration; (c) `fish_donothing.F90` is a fully stubbed module for isolation testing; (d) `switch_to_fish_pclake.py` swapped `wet/fish` → `wet/fish_pclake` to avoid the dependency; (e) **final workaround** `remove_fish.py` deletes all fish instances from `fabm.yaml`.
- **Final state**: Working config runs **without fish**; `validate_foodweb.py` notes "Fish modules disabled due to time_step variable dependency issue."
- **Related files**: `fish_patched.F90`, `fish_v2_patched.F90`, `fish_v3_donothing.F90`, `fish_donothing.F90`, `getm_fabm_patched.F90`, `luomahu_case/switch_to_fish_pclake.py`, `luomahu_case/remove_fish.py`.

### 4.5 Zooplankton `prey_suffix` for Phytoplankton Coupling
- **Symptom**: Zooplankton (cladocerans, copepods) could not locate phytoplankton prey state variables.
- **Root cause**: WET zooplankton couples to prey via `sD<suffix>`; phytoplankton expose pelagic state with a `_W` suffix that must be declared per prey slot.
- **Fix**: `fix_prey_suffix.py` / `fix_cladecerans.py` add `prey_suffix1-3: _W` (phytoplankton prey) and `prey_suffix4: ''` (POM prey) plus `nPrey: 4` to both zooplankton instances.
- **Related files**: `3DWET/scripts/fix/fix_prey_suffix.py`, `fix_cladecerans.py`.

### 4.6 `hypsograph` and `lSi` Flag Errors
- **Symptom**: Config failed with `hypsograph: true` (no hypsography in cartesian setup) and zooplankton silica-prey flags `lSi1-4: true` caused coupling errors.
- **Fix**: `fix_foodweb_config.py` sets `hypsograph: false` globally and `lSi1-4: false` for all zooplankton.
- **Related files**: `luomahu_case/fix_foodweb_config.py`.

### 4.7 Adding Diatoms (Silica Phytoplankton)
- **Symptom**: Need a 3rd phytoplankton group (diatoms) with silica dynamics, but template only had cyanobacteria + greens.
- **Fix**: `step1_add_diatoms.py` clones `greens`, sets diatom-specific params (`lSi: true`, `cSiD`, `hSiAss`), initializes `sDW/sNW/sPW/sCW` plus `_PV` mirrors, increments `burial.nPHYT` to 3, adds `POM_phytoplankton_update3`, and bumps zooplankton `nPrey` to 3 with `prey_model3: diatoms`.
- **Related files**: `luomahu_case/step1_add_diatoms.py`.

### 4.8 Macrophytes Causing Segfault
- **Symptom**: Including `macrophytes` triggered segfault / unresolved coupling errors.
- **Fix (workaround)**: `remove_macrophytes.py` strips the macrophytes instance block, its `POM_macrophyte_update1` coupling, and fish `cRelVegPlan`/`cRelVegBent` references. Macrophytes later re-enabled once `bot_pel_conv` and `_PV` couplings were fixed.
- **Related files**: `luomahu_case/remove_macrophytes.py`.

### 4.9 GETM-FABM Import Statement Error
- **Symptom**: `type_scalar_variable_id` was imported from the wrong module after the `time_step` patch, causing a compile error.
- **Fix**: `fix_import.py` moves `type_scalar_variable_id` from the `fabm_types` import to the `fabm` import where it is actually exported.
- **Related files**: `3DWET/scripts/fix/fix_import.py`.

---

## 5. Numerical Stability Problems

### 5.1 `temporal_mean` PAR Segfault (resolved by 4.1)
- **Symptom**: Adding any phytoplankton (cyanobacteria/diatoms/greens) → segfault in `fabm_update_time1` because `temporal_mean(PAR)` history arrays were accessed via the dangling `time_step` pointer.
- **Root cause**: Same as 4.1 — `temporal_mean` internally depends on `time_step`; once linked to module-level `dt`, the segfault disappeared and the 30-day run became stable.
- **Verification**: `test_luomahu_step/run_step3.py` (phytoplankton step) checks for "Segmentation fault"; `luomahu_case/validate_foodweb.py` confirms no NaN blowup over 30 days.

### 5.2 Incremental Module Isolation
- **Symptom**: Unknown which module in the full food web triggered failures.
- **Fix**: `debug_incremental.py` and `test_luomahu_step/run_step1.py` (abiotic) → `run_step2.py` (+sediment) → `run_step3.py` (+phytoplankton) add modules progressively; each script copies a stage-specific `fabm_stepN_*.yaml`, runs GETM via WSL, and reports exit code + segfault detection. This isolated the breakage to phytoplankton/fish and the `time_step` link.
- **Related files**: `3DWET/scripts/debug/debug_incremental.py`, `test_luomahu_step/run_step1.py`, `run_step2.py`, `run_step3.py`.

### 5.3 NaN Monitoring
- **Symptom**: Need to confirm runs do not diverge.
- **Fix**: `check_nan.py` / `check_nan_details.py` scan `elev`, `temp`, `z` and ecological variables for NaN counts and value ranges across timesteps; `validate_foodweb.py` performs a final NaN check on all state variables.
- **Related files**: `3DWET/scripts/analysis/check_nan.py`, `check_nan_details.py`, `luomahu_case/validate_foodweb.py`.

---

## 6. Output / Visualization Problems

### 6.1 Sigma-Layer and Vertical Structure Verification
- **Symptom**: Needed to confirm 3D sigma coordinates and layer thicknesses were written correctly.
- **Fix**: `check_sigma.py` reads `sigma` values; `check_3d_vars.py` reports per-variable valid-layer counts; `check_vertical_sigma.py` / `check_vertical.py` inspect the z-coordinate field.
- **Related files**: `luomahu_case/check_sigma.py`, `3DWET/scripts/analysis/check_3d_vars.py`, `check_vertical_sigma.py`.

### 6.2 Bathymetry / Grid Validation
- **Symptom**: River and model cells must align with the wet domain.
- **Fix**: `check_bathy_detail.py` / `check_bathy_elev.py` print full row/column traces of `bathymetry.nc` to locate the water/land boundary and confirm river depths.
- **Related files**: `3DWET/scripts/analysis/check_bathy_detail.py`, `check_bathy_elev.py`, `check_bathy_format.py`.

### 6.3 Result Validation Pipeline
- **Symptom**: Need end-to-end confirmation that the full food web produces ecologically plausible output.
- **Fix**: `validate_foodweb.py` computes lake-averaged surface concentrations for 3 phytoplankton groups (Chla), 2 zooplankton, macrophytes, zoobenthos, and nutrients (NH4/NO3/PO4/O2) at day 30, plus Day1→Day30 time series and a NaN check across all state variables.
- **Related files**: `luomahu_case/validate_foodweb.py`.

---

## Key Lessons Learned

1. **Never link FABM data pointers to local subroutine variables.** The `time_step` dangling pointer was the single most damaging bug — silent until `temporal_mean` or fish accessed it, then segfault. Always link to module-level or host-persisted storage (`set_env_gotm_fabm`'s `dt`, not `init_gotm_fabm`'s local `dt`).

2. **The WET model assumes host capabilities GETM-FABM did not provide.** `bot_pel_conv` (1/dz) and the `_PV` pelagic-mirror state variables require explicit host linking and YAML coupling declarations. Any new WET benthic module will hit the same gap until the host is patched.

3. **Iterative run→parse→fix loops tame coupling-heavy configs.** With ~24 missing `_PV` couplings, manual editing was infeasible. Scripts that parse `FATAL ERROR` lines and auto-patch `fabm.yaml` (`fix_nofish_iterative.py`, `fix_foodweb_config.py`) converged where hand-editing stalled.

4. **Incremental module addition isolates failure.** Adding abiotic → sediment → phytoplankton → zooplankton → fish in stages (`debug_incremental.py`, `run_step1-3.py`) pinpointed phytoplankton/fish as the break point, directing attention to `temporal_mean`/`time_step`.

5. **Validate river positions against bathymetry.** Several rivers landed on dry cells because coordinates were guessed. Always cross-check `(j,i)` against `bathymetry.nc > 0` before running.

6. **Newer GCC is not always better.** GCC 13.3.0 had an internal compiler error on `gotm_fabm.F90`; GCC 9.5.0 built cleanly. Pin a known-good toolchain.

7. **When a module cannot be fixed in time, stub it.** `fish_donothing.F90` (empty `do` routines) and `remove_fish.py` kept the rest of the food web runnable while the `time_step` issue remained open.

8. **Keep patched `.F90` files as committed artifacts.** The root-level `*_patched.F90` / `*_fixed.F90` snapshots document exactly which host patches are required to run WET under GETM, independent of the upstream source tree.
