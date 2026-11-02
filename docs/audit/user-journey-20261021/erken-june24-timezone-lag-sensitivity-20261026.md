# Erken June 2024 pairing: ±1 h label sensitivity

**负责人：Sol 高**  
**状态：代理分析（SITES 实测观测 × 已有候选求解器输出）；不构成完整科学验证。**

## Question

The existing pairing uses identical naive wall-clock labels. SITES metadata says `UTC+1`; the NetCDF time unit says `seconds since 2024-06-13 13:00:00` without a timezone. This read-only calculation checks whether the descriptive error changes materially if the observation labels are instead one hour earlier or later than each model label. It does not establish which alignment is correct.

## Inputs and method

- Observation source: the existing SITES Erken 2017–2025 source package, PID `11676.1/gVQYm0aNPryFRtn2CpeuzzwF`; the file is preserved at `build/real-use-validation-20261023/erken-sites-profile-2017-2025/SITES_TW-PROF_ERK_LRK_20170628-20251201_L2_60min.zip`. Existing source audit records its CSV SHA-256 as `8154189b468d3ebc8546d9f60a97aecf3c0526ad0d23c1eb1e4a64146f094821`.
- Model values: the already-produced depth-interpolated table `build/real-use-validation-20261023/erken-june2024-competition-luna-attempt03/erken-june24-C-temp-observation-pairing-20261026/latest-source-pairing-20261027/hourly-depth-pairs.csv`, containing 168 model frames and 50 sensor depths (8,400 candidate pairs). No solver was run and no model output was changed.
- The 2017–2025 CSV was parsed from the supplied ZIP in memory. Its timestamp keys in the examined window were unique. For each existing model time and sensor depth, the observation lookup used timestamp offsets −1 h, 0 h, and +1 h; model-minus-observation bias, MAE, and RMSE were recomputed. The zero-offset values reproduce the existing summary to rounding precision.

## Results

| Observation timestamp relative to model label | Pairs | Bias (°C) | MAE (°C) | RMSE (°C) |
|---:|---:|---:|---:|---:|
| −1 h | 8,400 | +0.03715 | 4.02757 | 4.20348 |
| 0 h | 8,400 | +0.02427 | 4.03318 | 4.20809 |
| +1 h | 8,400 | +0.01248 | 4.03910 | 4.21281 |

Across these three possible label alignments, RMSE spans about 0.0093 °C, while signed bias shifts by about 0.0247 °C. The absolute temperature-profile error remains around 4.2 °C under each alignment.

## Interpretation and limits

- **代理结果**: the 168-hour candidate-solver diagnostic is not very sensitive in RMSE to a ±1-hour pairing shift. The signed bias does move modestly, so the time convention still matters for reporting.
- **不确定**: this sensitivity test cannot identify the correct UTC offset. SITES' metadata convention and the model's timezone-free CF units remain unreconciled; a lower RMSE under one shift is not independent evidence that the shift is physically correct.
- **未完成**: the run is a mechanism-sensitivity candidate-solver arm, its first observed profile was also used as model initialization, and its forcing/initial-state limitations remain. It does not establish seasonal skill or full Erken scientific validation.
- No model case was started, created, deleted, cleaned, or overwritten. No application window was opened or refreshed.
