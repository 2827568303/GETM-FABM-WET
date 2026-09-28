# Theoretical Lake — GETM-FABM-WET Model Run Analysis Report

**Case directory:** `3DWET/case/Theoretical lake/`
**Analysis date:** 2026-07-10
**Analysis scripts:** `check_output.py`, `check_inputs.py`, `investigate.py` (read-only, generated for this report)

---

## 1. Run Status: Completeness, NaN Check, Time Coverage

### 1.1 Output files
| File | Size | Time steps | Time resolution | Status |
|------|------|-----------|-----------------|--------|
| `THEORETICAL_LAKE.2d.nc` | 296 KB | 730 | 12-hourly (dt = 43200 s) | Last 3 records corrupt (time = 0) |
| `THEORETICAL_LAKE.3d.nc` | 341.6 MB | 730 | 12-hourly (dt = 43200 s) | Last record corrupt (time = 0, all-zero) |
| `output.nc` | 154.2 MB | — | FABM diagnostics | Not separately re-checked |

### 1.2 Time coverage
- Time units: `seconds since 2020-01-01 00:00:00`.
- Raw time series: first = 43200 s (12 h), increments of 43200 s.
- Last valid record (3d, index 728): `t = 31492800 s ≈ 364.5 d` → ~2020-12-30 12:00.
- **The final record (index 729) has `time = 0` and all-zero / masked data.** In `2d.nc` the last **three** records carry `time = 0`. This is a corrupt trailing record written at model termination; it is responsible for the spurious "COLLAPSE" flags produced by a naive first-vs-last comparison. All real ecological dynamics are intact up to index 728.
- 729 valid 12-hourly records cover ~364.5 days of the 366-day target — **essentially complete**, the only gap being the final half-day.

### 1.3 NaN / Inf / negative check
- **NaN count: 0. Inf count: 0** across all checked variables.
- The minimum value `-2.0e+20` reported for pelagic 3-D variables is the **netCDF `_FillValue` for dry/land cells**, not real negative concentration. The 3-D grid is `time × 11 × 7 × 5` (compacted wet domain, 385 cells); 35 of these are inactive at the top layer, giving the consistent "fill" subset. **Real wet-cell data are non-negative for all ecological state variables.**
- `temp` also shows `-9999.0` (a separate dry-cell sentinel) and a real minimum of `-0.031 °C`.

### 1.4 Variables in `3d.nc`
545 variables total, including: physical (`temp`, `uu`, `vv`, `w`, `tke`, `num`, `nuh`, `diss`, `elev`, `hcc`), FABM states (e.g. `cyanobacteria_sDW/sNW/sPW/sCW` + sediment `sDS…` for all 3 phytoplankton groups; `cladocerans_sD/sN/sP/sC`; `copepods_sD…`; `JuFish/AdFish/PiscFish_sD/sN/sP/sC`; `zoobenthos_sD…`; `macrophytes_sD…`; `POM/DOM/humus_sDW…`; `abiotic_water_sNH4W/sNO3W/sPO4W/sO2W/sSiO2W…`; `abiotic_sediment_sNH4S…`), and a large number of FABM diagnostic/rate variables (`*_tDMin`, `*_wNMin`, `*_aNutLim`, `*_oChla`, `*_rNDW`, etc.).

---

## 2. Input Data Assessment

### 2.1 Bathymetry (`bathymetry.nc`) — **OK**
- Grid 24 × 20, cell size 500 m × 500 m.
- Depth range: 0.0 – 10.2 m; mean over wet cells = **5.301 m** (design 5.3 m).
- Wet cells (depth > 0): **280** (matches design exactly); all 280 exceed `crit_depth = 0.3`.
- No negative depths, no anomalies.
- Estimated volume = **371.05 Mm³** (matches design 371 Mm³).

### 2.2 Rivers (`rivers.nc`) — **Acceptable, minor data-quality issue**
- 369 time steps, 2020-01-01 → 2021-01-03. **3 trailing records are fill values (9.97e36)**; only 366 carry real data. The model evidently tolerated these (run completed), but the file should be trimmed.
- Discharge ranges (real values only):
  | River | Design mean | Actual min | Actual max | Actual mean |
  |-------|-------------|-----------|-----------|------------|
  | INFL_NW | +4.00 | 2.00 | 6.00 | 3.995 |
  | INFL_NE | +1.50 | 0.75 | 2.25 | 1.498 |
  | INFL_W  | +1.50 | 0.75 | 2.25 | 1.498 |
  | OUTFL_S | −2.25 | −3.44 | −1.08 | −2.255 |
  | OUTFL_E | −4.51 | −6.88 | −2.16 | −4.509 |
- River water temperature: 2.0 – 22.0 °C (mean 11.97), consistent with meteo `t2`.
- River nutrient concentrations are **constant in time** (simplified): inflow NH4 = 0.10–0.15, NO3 = 0.8–1.2, PO4 = 0.02–0.025 g/m³; outflow concentrations set lower (NH4 = 0.05, NO3 = 1.0, PO4 = 0.02). Reasonable for moderately enriched rivers.

### 2.3 Water balance
- Total inflow = **7.00 m³/s**, total outflow = **−6.76 m³/s**, net = **+0.24 m³/s** (3.4 % surplus → storage gain).
- River-only implied level rise over 366 d ≈ **+0.108 m** (over 70 km²).
- Observed `elev` from 2-D output: rises from ~0.0 m to a peak mean of **+0.483 m** (range −0.151 to +0.483 m), i.e. the lake level drifts up ~0.4–0.48 m over the year rather than the 0.108 m predicted from mean net river flow. The extra rise indicates the prescribed outflow magnitudes do not fully compensate the inflow + any residual flux; the imbalance is **non-critical for a 1-year test** (~7 % of mean depth) but would compound on multi-year runs.
- `elev` returns to 0.0 m on the (corrupt) final record only.

### 2.4 Meteorology (`meteo.nc`) — **Reasonable but heavily simplified**
- 369 steps, 2020-01-01 → 2021-01-03.
- `u10`: −3.45 to 3.48 m/s (mean 0.007); `v10`: −2.39 to 2.40 m/s — reasonable, near-zero mean wind.
- `slp`: 101300 Pa **constant** (1013 hPa).
- `t2`: −2.0 to 22.0 °C (mean 9.87) — valid temperate annual cycle.
- `rh`: 64 – 80 % (mean 72) — reasonable.
- `tcc`: **0.50 constant** (cloud cover fixed at 50 %).
- `precip`: **0.0 everywhere** (no rainfall forcing).
- `evap`: **~0.0 everywhere** (no evaporation forcing).
- **Concern:** zero precipitation/evaporation means the atmospheric water flux is absent; the only hydrological forcing is rivers. This is an acceptable simplification for a theoretical test case but unrealistic for a real lake and contributes to the slow level drift.

### 2.5 Ecological initial conditions (`fabm_init.nc`)
- `fabm_init.nc` contains **only coordinate variables** (lon, lat, lonc, latc, time) — **no ecological state fields**.
- `getm_fabm.inp` sets `fabm_init_method = 2` (read from file), but because the file carries no state variables, **all ecological initial conditions fall back to the uniform scalar values in `fabm.yaml`**. The `macrophytes` comment "overridden by fabm_init.nc spatial field" is therefore not in effect; macrophytes start uniformly at `sD = 30.0 gDW/m²` from the yaml.
- Initial values used (from yaml):
  - cyanobacteria: sDW = 0.10 gDW/m³
  - diatoms: sDW = 0.50 gDW/m³
  - greens: sDW = 0.30 gDW/m³
  - cladocerans / copepods: sD = 0.10 gDW/m³
  - zoobenthos: sD = 0.50 gDW/m²
  - macrophytes: sD = 30.0 gDW/m²
  - JuFish: sD = 0.30; AdFish: sD = 0.80; PiscFish: sD = 0.10 gDW/m³
  - abiotic water: sNH4W = 0.3, sNO3W = 0.5, sPO4W = 0.03, sO2W = 10.0, sSiO2W = 3.5 g/m³

---

## 3. Output Results Assessment

Spatial-mean time series (12-hourly, valid records only):

### 3.1 Physical variables — **OK**
| Variable | Min | Max | Notes |
|----------|-----|-----|-------|
| `temp` | −0.03 °C | 29.9 °C (mean 12.9) | Valid seasonal cycle; winter ~0 °C, summer peak ~28 °C (day ~231). Within −2..40 limits. |
| `uu` / `vv` | −0.9999 / −0.9999 (sentinel) | 0.054 / 0.050 m/s | Weak circulation driven by river through-flow; physically plausible for a small lake. |
| `elev` | −0.151 m | 0.483 m | Slow rising trend (~+0.4 m/yr); see §2.3. |

### 3.2 Nutrients — **Reasonable seasonal cycling**
| Variable | t0 | Peak (time) | Summer min | t728 | Pattern |
|----------|----|-------------|-----------|------|---------|
| `sNO3W` | 0.53 | 0.91 (day 43) | 0.001 (day 182) | 0.36 | Winter build-up → summer drawdown by diatom bloom → winter recovery. ✓ |
| `sPO4W` | 0.10 | 0.103 (day 66) | 0.003 (day 182) | 0.043 | Initial rise above yaml init (0.03) suggests sediment P release; strong summer drawdown. ✓ |
| `sO2W` | 10.0 | 22.8 (day 103) | 8.4 (day 273) | 13.8 | No anoxia (min 8.4 mg/L). Peak during spring bloom, summer minimum. ✓ |
| `sNH4W` | 0.37 | — | 0.017 | 0.024 | Drops rapidly from init; reasonable. |

### 3.3 Phytoplankton — **Mixed: diatom bloom + greens collapse**
| Group | Init (yaml) | t0 output | Peak (time) | t728 | Verdict |
|-------|-------------|-----------|-------------|------|---------|
| `diatoms_sDW` | 0.50 | 0.053 | **21.73 gDW/m³** (day 108, spring) | 2.07 | **Excessive spring bloom.** Peak mean 21.7 (cell max 46.2) is far above typical 1–10 gDW/m³; driven by high `cMuMax = 2.4/d` and ample nutrients. |
| `cyanobacteria_sDW` | 0.10 | 0.095 | 1.23 (day 316, autumn) | 0.97 | **Reasonable.** Summer/autumn peak, low in spring (Si-limited competitors dominant). ✓ |
| `greens_sDW` | 0.30 | 0.047 | 0.047 (day 0) | 1.0e-4 | **Collapse.** Monotonic decline from start to near-extinction; out-competed by faster-growing diatoms. |

### 3.4 Zooplankton — **Collapse**
| Group | Init | t0 | t182 | t728 | Verdict |
|-------|------|-----|------|------|---------|
| `cladocerans_sD` | 0.10 | 0.096 | 2.3e-5 | 1.0e-5 (floor) | **Collapse to minimum threshold within ~3 months.** |
| `copepods_sD` | 0.10 | 0.096 | 6.1e-5 | 1.0e-5 (floor) | **Collapse to minimum threshold within ~3 months.** |

Both zooplankton groups crash to the `cDMinZoo = 1e-5` floor almost immediately and never recover.

### 3.5 Fish — **Collapse (cascade)**
| Group | Init | t182 | t365 | t728 | Verdict |
|-------|------|------|------|------|---------|
| `JuFish_sD` | 0.30 | 0.21 | 0.046 | 0.0036 | **Collapse.** Declines monotonically; starves once zooplankton prey collapse. |
| `AdFish_sD` | 0.80 | — | — | ~0.84 (max) | Roughly stable (benthivorous, feeds on zoobenthos which persists). |
| `PiscFish_sD` | 0.10 | — | — | ~0.10 | Roughly stable. |

### 3.6 Other groups
- `zoobenthos`, `macrophytes`, `POM`, `DOM`, `humus`: remain within plausible bounds (macrophytes near floor after winter die-back, recovering in growing season; humus/sediment pools slowly evolving).

---

## 4. Parameter Analysis (from `fabm.yaml`)

### 4.1 Phytoplankton key parameters
| Parameter | cyanobacteria | diatoms | greens | Default | Assessment |
|-----------|---------------|---------|--------|---------|------------|
| `cMuMax` (1/d) | 1.4 | **2.4** | **1.0** | 1.4 | Diatoms **+71 %** over default → bloom-prone; greens **−29 %** → uncompetitive. Mismatch drives the diatom-dominance + greens-collapse pattern. |
| `kDResp` (1/d) | 0.03 | 0.10 | 0.075 | 0.03 | Diatom/green respiration raised 2–2.5×; further penalises greens. |
| `cVSet` (m/d) | 0.03 | −0.5 (sinking) | −0.35 (sinking) | 0.05 | Diatoms/greens sink fast (negative = sinking); cyanobacteria near-neutral buoyancy. Favors cyanobacteria late in the year. |
| `cTmOpt` (°C) | 25 | 18 | 25 | 25 | Diatoms cool-optimum → spring bloom; cyano/green warm-optimum → summer. Consistent with output. |
| `cLOptRef` (W/m²) | 23 | 35 | 30 | 25 | Reasonable light optima. |

### 4.2 Zooplankton key parameters (cladocerans & copepods identical)
| Parameter | Value | Default | Assessment |
|-----------|-------|---------|------------|
| `kDConsMaxZoo` | **0.85** | 0.5 | Max consumption **+70 %** over default, but only realised at high prey density. |
| `kDRespZoo` | 0.2 | 0.2 | Maintenance respiration 0.2/d. |
| `kMortZoo` | 0.04 | 0.04 | Mortality 0.04/d. |
| `fDAssZoo` | 0.35 | 0.35 | Assimilation efficiency. |
| Break-even assimilation | 0.24/d | — | 0.2 (resp) + 0.04 (mort). Max assimilation = 0.85 × 0.35 = 0.30/d, only 25 % headroom and only at saturating prey. |
| `cDCarrZoo` | 25.0 | 25.0 | Carrying capacity. |
| `nPrey` | 4 | 1 | Feeds on cyano + diatoms + greens + POM. |

**Diagnosis:** With winter phytoplankton biomass only 0.05–0.5 gDW/m³ and a Type-II functional response, realised consumption is far below the 0.24/d break-even, so zooplankton net growth is negative from day 1 and they fall to the floor. This is the root cause of the zooplankton collapse.

### 4.3 Fish key parameters
| Parameter | JuFish | AdFish | PiscFish | Default |
|-----------|--------|--------|----------|---------|
| `kDConsMax` | 0.25 | 0.25 | 0.25 | 0.25 |
| `kDRespFi` | 0.01 | 0.01 | 0.01 | 0.01 |
| `kMortFi` | 0.001 | 0.001 | 0.001 | 0.001 |
| Prey | copepods+cladocerans | zoobenthos | JuFish+AdFish | — |
| Init sD | 0.30 | 0.80 | 0.10 | — |

JuFish depends entirely on the two zooplankton groups that collapse, so it starves despite low mortality (0.001/d). AdFish (benthivorous) and PiscFish (piscivorous) remain stable because their prey (zoobenthos, juvenile fish) persists. Note PiscFish remains stable only because AdFish persists — the JuFish prey pool collapses.

### 4.4 Nutrient / abiotic initial & river concentrations
- Water-column init: sNH4W = 0.3, sNO3W = 0.5, sPO4W = 0.03, sO2W = 10.0, sSiO2W = 3.5 g/m³ — reasonable mesotrophic winter values.
- River inflow: NH4 = 0.10–0.15, NO3 = 0.8–1.2, PO4 = 0.02–0.025 g/m³ — moderately enriched.
- No obviously toxic or starving initial concentrations.

---

## 5. Error Diagnosis

### 5.1 Distinguishing model-equation issues from parameter issues

| # | Issue | Category | Evidence |
|---|-------|----------|----------|
| 1 | **Corrupt final output record** (time = 0, all-zero data) in both `2d.nc` and `3d.nc`. | **Model/IO bug** (GETM output writer at run termination) | `time[-1] = 0` while `time[-2] = 31492800 s`; data at last record is uniformly 0 / masked. Not a numerical failure of the physics. |
| 2 | **Zooplankton collapse** (cladocerans + copepods → 1e-5 floor within 3 months). | **Parameterisation / food-web coupling** | Break-even assimilation (0.24/d) barely below max assimilation (0.30/d); at low winter prey the Type-II response yields net negative growth. This is the WET zooplankton starvation spiral — a known stability issue of the WET food-web coupling, here triggered by the parameter choice (low initial prey + high respiration). |
| 3 | **Greens collapse** (→ 1e-4). | **Parameter issue** | `cMuMax = 1.0` (default 1.4) vs diatoms 2.4; combined with higher respiration (0.075 vs 0.03) and sinking (−0.35), greens cannot compete. |
| 4 | **Diatom bloom** (peak 21.7 mean / 46.2 max gDW/m³). | **Parameter issue (consequence of #2 + #3)** | `cMuMax = 2.4` (default 1.4) + abundant nutrients + **no zooplankton grazing** (collapsed) → unchecked spring bloom. |
| 5 | **JuFish collapse** (0.30 → 0.0036). | **Consequence of #2** | Trophic cascade: zooplankton prey collapse → juvenile fish starvation. |
| 6 | **Water-level drift** (+0.4–0.48 m/yr). | **Forcing imbalance** | River net +0.24 m³/s with no precip/evap counter-flux; outflow magnitudes slightly under-tuned. Minor for 1 year. |
| 7 | **No NaN / no Inf** in any state variable. | — | Numerics stable; the run did not blow up. |

**Model-equation vs parameter distinction:**
- The only clear **model/IO defect** is the corrupt trailing output record (#1). The physics, transport, and FABM biogeochemistry solvers ran stably to completion with no NaN/Inf.
- The ecological collapses (#2–#5) are **driven by parameter choices**, not by an equation error per se. However, issue #2 reflects a **known fragility of the WET zooplankton food-web coupling**: the Type-II consumption + carrying-capacity formulation produces a starvation spiral when prey density is low relative to the respiration+mortality floor. The WET model is sensitive here; the same equations with higher initial prey or lower `kDRespZoo` would avoid the collapse. This is therefore a *parameter × formulation* interaction — the equation is not wrong, but it is unforgiving of the chosen parameters.

### 5.2 Non-issues (initially alarming, actually benign)
- The `-2.0e+20` minima on pelagic variables are `_FillValue` sentinels for dry cells, not negative concentrations.
- The `temp` minimum `-9999.0` is a separate dry-cell sentinel.
- The apparent "all variables COLLAPSE" signal from a first-vs-last comparison is an **artifact of the corrupt final record**; trends over valid records (t0 … t728) are the real dynamics.

---

## 6. Recommendations

### 6.1 Does the run need to be repeated?
**Not for diagnostic purposes** — the run completed, the numerics are clean (no NaN/Inf), and the physical + abiotic results are sensible. **A re-run is recommended only after parameter tuning** if realistic ecology is required, because the current zooplankton/greens/JuFish collapses make the food-web output unusable for ecological interpretation.

### 6.2 Parameter adjustments to address the collapses
1. **Zooplankton starvation (highest priority):**
   - Reduce `kDRespZoo` from 0.2 → ~0.05–0.1, **or**
   - Raise initial phytoplankton biomass (especially diatoms) so winter prey exceeds the half-saturation of the consumption response, **or**
   - Lower `kMortZoo` from 0.04 → ~0.01.
   - Re-examine `kDConsMaxZoo = 0.85` (default 0.5): the high max consumption does not help at low prey and only steepens the starvation once prey is depleted.
2. **Greens collapse:** raise `cMuMax` for greens from 1.0 → ~1.4 (default) and/or lower diatoms `cMuMax` from 2.4 → ~1.6–1.8 to reduce competitive exclusion.
3. **Diatom bloom magnitude:** even after zooplankton recovery, `cMuMax = 2.4` is aggressive; consider 1.8–2.0. The bloom will also moderate once grazing pressure is restored.
4. **JuFish:** will recover automatically once zooplankton prey are restored; no separate fish-parameter change needed for the cascade.

### 6.3 Forcing / data fixes
1. **Trim the 3 trailing fill records** from `rivers.nc` (9.97e36 values) to avoid any risk of the model reading fill on the last days.
2. **Add non-zero precipitation/evaporation** to `meteo.nc` if a closed water budget is desired; otherwise accept the ~0.4 m/yr level drift.
3. **Re-tune river outflow magnitudes** (or switch to a level-dependent outflow) so the mean net flux is closer to zero if multi-year stability is needed.
4. **Populate `fabm_init.nc` with spatial initial fields** if spatial heterogeneity is intended (currently all ecology starts uniform from yaml); otherwise document that yaml scalars are authoritative.

### 6.4 Output handling
- When post-processing, **drop the last record** of `2d.nc` and `3d.nc` (and the last 3 of `2d.nc` where `time == 0`). The valid series ends at index 728 (3d) / ~726 (2d).
- Consider setting `step_2d`/`step_3d` so the output cadence matches the intended daily sampling (current output is 12-hourly despite `step_2d = 1440`).

---

## Appendix: Key numeric reference table

| Quantity | Value | Source |
|----------|-------|--------|
| Grid | 24 × 20, 500 m cells | `lake_summary.txt` |
| Wet cells | 280 | `bathymetry.nc` |
| Volume | 371.05 Mm³ | `bathymetry.nc` |
| Avg / max depth | 5.30 / 10.2 m | `bathymetry.nc` |
| Simulation | 2020-01-01 → 2021-01-01 (366 d) | `getm.inp` |
| timestep / layers | 60 s / 10 sigma | `getm.inp` |
| Output records | 730 (729 valid + 1 corrupt) | `2d.nc` / `3d.nc` |
| Output cadence | 12-hourly (43200 s) | `time` variable |
| 3d.nc variables | 545 | `3d.nc` |
| NaN / Inf | 0 / 0 | all checked vars |
| Temp range | −0.03 … 29.9 °C | `temp` (valid cells) |
| Elev range | −0.151 … 0.483 m | `elev` |
| River net flux | +0.24 m³/s | `rivers.nc` |
| Diatom peak | 21.7 mean / 46.2 max gDW/m³ | `diatoms_sDW` |
| Zooplankton end | 1e-5 gDW/m³ (floor) | `cladocerans/copepods_sD` |
| JuFish end | 0.0036 gDW/m³ | `JuFish_sD` |
