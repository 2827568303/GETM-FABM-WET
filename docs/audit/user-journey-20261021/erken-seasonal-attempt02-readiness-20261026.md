# Erken seasonal attempt02 readiness audit

**负责人：Sol 高**  
**状态：只读配置审计；没有运行模拟。**

## Candidate science inputs

- The SITES daily temperature profile covers 2017-06-29 through 2017-09-30: 94 dates × 50 depths, 1 m to 15.5 m, all 4,700 expected values present. It is an observed source, not a model result.
- `audit/Erken_2017-06-29_2017-09-30_hourly_mixed_forcing.csv` contains 2,256 hourly records. The prior source audit reports 2,238 consecutive complete hours after combining Malma station observations, Svanberga station observations, and ERA5 reanalysis fills. This is a **mixed/proxy forcing candidate**, not purely measured forcing. The recorded wind comparison and other source limitations remain material.

## Runtime case mismatch

The directory labelled `runtime/3DWET/case/Erken_2017_seasonal` is not configured for the candidate 2017 period:

- `getm.inp` starts at `2020-01-01 00:00:00` and stops at `2020-01-02 00:00:00`.
- The temperature input configured in `getm.inp` is `Input/Erken_TW_profile_2020-01-01.txt`, not the 2017 daily profile.
- Its `meteo.nc` has 25 records from 2020-01-01 00:00 through 2020-01-02 00:00.
- No `*.3d.nc` or `output.nc` result exists in the attempt02 runtime case; its output folder contains only README files.

## Decision and status

- **实测**: read-only inspection of the SITES profile source, case configuration, and NetCDF time axis confirms the above dates and dimensions.
- **代理**: the 2017 mixed-forcing CSV is a prepared candidate only; its reanalysis/nearby-station components remain proxies.
- **未完成**: a correctly configured 2017 seasonal Erken case has not been run and cannot be scored against the observed daily profiles from this directory. The attempt02 folder was not edited or cleared because it contains source/configuration audit materials and no generated model result to clean; no new case was started. Before a future run, create a clean output target and retain its seed/config/input hashes so the user-requested stale-case cleanup can be scoped exactly.
