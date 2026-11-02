#!/usr/bin/env python3
"""Check completeness and validity of GETM-FABM-WET output for Theoretical Lake.

Verifies:
  - 2d.nc / 3d.nc time coverage (expected 366 days, daily output)
  - NaN / Inf / negative checks for key variables (elev, temp, uu, vv)
  - FABM ecological variables (phytoplankton, zooplankton, fish, nutrients)
  - Water level range, temperature range (-2..40 C), ecological ranges
  - Full variable listing in 3d.nc
"""

import os
import sys
import numpy as np
from netCDF4 import Dataset, num2date

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
F2D = os.path.join(CASE_DIR, "THEORETICAL_LAKE.2d.nc")
F3D = os.path.join(CASE_DIR, "THEORETICAL_LAKE.3d.nc")
EXPECTED_DAYS = 366  # 2020 is a leap year
DAILY_STEPS_EXPECTED = 367  # start + 366 days inclusive


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def check_time(ds, label, expected_steps):
    """Check time coverage of a dataset. Returns (n_steps, t0, t1)."""
    t = ds.variables["time"]
    n = len(t)
    units = t.units if hasattr(t, "units") else "seconds since ..."
    try:
        dates = num2date(t[:], units=units)
        t0 = dates[0]
        t1 = dates[-1]
        span_days = (t1 - t0).days if hasattr(t1 - t0, "days") else None
        print(f"[{label}] time steps = {n}  (expected ~{expected_steps})")
        print(f"[{label}] first = {t0}   last = {t1}")
        if span_days is not None:
            print(f"[{label}] span = {span_days} days (expected 366)")
        ok = (n >= expected_steps - 1) and (span_days is None or span_days >= 365)
        print(f"[{label}] time coverage OK: {ok}")
        return n, t0, t1, ok
    except Exception as e:
        print(f"[{label}] time decode error: {e}")
        return n, None, None, False


def var_stats(name, arr, mask=None):
    """Return NaN/Inf/negative counts and min/max ignoring mask values."""
    arr = np.asarray(arr)
    flat = arr.ravel()
    if flat.dtype.kind == "f":
        n_nan = int(np.isnan(flat).sum())
        n_inf = int(np.isinf(flat).sum())
        finite = flat[np.isfinite(flat)]
    else:
        n_nan = 0
        n_inf = 0
        finite = flat
    if finite.size == 0:
        return dict(n_nan=n_nan, n_inf=n_inf, n_neg=0, vmin=None, vmax=None, n=flat.size)
    n_neg = int((finite < 0).sum())
    return dict(
        n_nan=n_nan, n_inf=n_inf, n_neg=n_neg,
        vmin=float(np.nanmin(finite)), vmax=float(np.nanmax(finite)),
        n=flat.size,
    )


def check_var(ds, name, label, allow_negative=False, vmin=None, vmax=None):
    """Check a single variable for NaN/Inf/range issues."""
    if name not in ds.variables:
        print(f"  [{label}] {name}: MISSING")
        return None
    arr = ds.variables[name][:]
    st = var_stats(name, arr)
    flag = "OK"
    issues = []
    if st["n_nan"] > 0:
        issues.append(f"NaN={st['n_nan']}")
    if st["n_inf"] > 0:
        issues.append(f"Inf={st['n_inf']}")
    if not allow_negative and st["n_neg"] > 0:
        issues.append(f"NEG={st['n_neg']}")
    if vmin is not None and st["vmin"] is not None and st["vmin"] < vmin:
        issues.append(f"min<{vmin}")
    if vmax is not None and st["vmax"] is not None and st["vmax"] > vmax:
        issues.append(f"max>{vmax}")
    flag = "ISSUES" if issues else "OK"
    print(f"  [{label}] {name:30s} min={st['vmin']} max={st['vmax']} "
          f"nan={st['n_nan']} inf={st['n_inf']} neg={st['n_neg']} -> {flag}"
          + (f"  [{'|'.join(issues)}]" if issues else ""))
    return st


def main():
    banner("OUTPUT COMPLETENESS CHECK - Theoretical Lake")

    results = {}

    # ---- 2D file ----
    banner("1. THEORETICAL_LAKE.2d.nc")
    if not os.path.exists(F2D):
        print(f"  MISSING: {F2D}")
        sys.exit(1)
    with Dataset(F2D) as ds:
        print("  Variables in 2d.nc:", list(ds.variables.keys()))
        n2, t0_2, t1_2, ok2 = check_time(ds, "2d", DAILY_STEPS_EXPECTED)
        results["2d_time"] = (n2, ok2)
        print("\n  -- Key 2D variables --")
        results["elev"] = check_var(ds, "elev", "2d", allow_negative=True)
        results["uu"] = check_var(ds, "uu", "2d", allow_negative=True)
        results["vv"] = check_var(ds, "vv", "2d", allow_negative=True)
        # water level range check (reasonable: -2..2 m for a lake)
        if "elev" in ds.variables:
            ev = ds.variables["elev"][:]
            ev_f = ev[np.isfinite(ev)]
            if ev_f.size:
                print(f"  [2d] elev range: {ev_f.min():.4f} .. {ev_f.max():.4f} m "
                      f"(mean {ev_f.mean():.4f})")

    # ---- 3D file ----
    banner("2. THEORETICAL_LAKE.3d.nc")
    if not os.path.exists(F3D):
        print(f"  MISSING: {F3D}")
        sys.exit(1)
    with Dataset(F3D) as ds:
        all_vars = list(ds.variables.keys())
        print(f"  Total variables in 3d.nc: {len(all_vars)}")
        for v in all_vars:
            print(f"    - {v}")
        results["3d_vars"] = all_vars
        n3, t0_3, t1_3, ok3 = check_time(ds, "3d", DAILY_STEPS_EXPECTED)
        results["3d_time"] = (n3, ok3)

        print("\n  -- Physical variables (3d) --")
        results["temp"] = check_var(ds, "temp", "3d", allow_negative=False,
                                    vmin=-2.0, vmax=40.0)
        results["uu"] = check_var(ds, "uu", "3d", allow_negative=True)
        results["vv"] = check_var(ds, "vv", "3d", allow_negative=True)
        results["salt"] = check_var(ds, "salt", "3d", allow_negative=False) \
            if "salt" in ds.variables else None

        # ---- FABM ecological variables ----
        print("\n  -- FABM ecological variables (3d) --")
        # Map category -> list of candidate variable-name fragments
        eco_groups = {
            "phytoplankton": ["cyanobacteria", "diatoms", "greens"],
            "zooplankton": ["cladocerans", "copepods"],
            "fish": ["JuFish", "AdFish", "PiscFish"],
            "zoobenthos": ["zoobenthos"],
            "macrophytes": ["macrophytes"],
            "nutrients": ["sNH4", "sNO3", "sPO4", "sSiO2", "sO2", "sDIN", "sDIP"],
            "organic_matter": ["POM", "DOM", "humus"],
        }
        # Find all FABM state variables (commonly prefixed by instance name)
        fabm_state_vars = [v for v in all_vars
                           if any(p in v for p in
                                  ["cyanobacteria", "diatoms", "greens",
                                   "cladocerans", "copepods", "JuFish", "AdFish",
                                   "PiscFish", "zoobenthos", "macrophytes",
                                   "sNH4", "sNO3", "sPO4", "sSiO2", "sO2",
                                   "sDIM", "sSiPa", "POM", "DOM", "humus",
                                   "abiotic"])]
        print(f"  FABM-related variables found: {len(fabm_state_vars)}")

        eco_results = {}
        for v in sorted(set(fabm_state_vars)):
            # ecological variables should be non-negative; no explosive growth
            st = check_var(ds, v, "eco", allow_negative=False)
            eco_results[v] = st
        results["eco"] = eco_results

        # ---- Explosive growth check on key DW state vars ----
        print("\n  -- Explosive growth check (DW vars, ratio last/first) --")
        for v in sorted(set(fabm_state_vars)):
            if v not in ds.variables:
                continue
            if not (v.endswith("/sDW") or v.endswith("_sDW")
                    or v.endswith("/sD") or v.endswith("_sD")
                    or "sDW" in v or "/sD" in v or "_sD" in v):
                # still check any state variable ending in sD/sDW
                pass
            try:
                arr = ds.variables[v][:]
                if arr.ndim < 1:
                    continue
                first = np.nanmean(arr[0]) if arr.shape[0] > 0 else np.nan
                last = np.nanmean(arr[-1]) if arr.shape[0] > 1 else np.nan
                if np.isfinite(first) and np.isfinite(last) and first > 1e-12:
                    ratio = last / first
                    flag = "EXPLOSIVE" if ratio > 1000 else ("COLLAPSE" if ratio < 0.01 else "ok")
                    if flag != "ok":
                        print(f"    {v:40s} first_mean={first:.4g} "
                              f"last_mean={last:.4g} ratio={ratio:.2g} -> {flag}")
            except Exception:
                pass

        # ---- Temperature range summary ----
        print("\n  -- Temperature range summary --")
        if "temp" in ds.variables:
            tp = ds.variables["temp"][:]
            tp_f = tp[np.isfinite(tp)]
            if tp_f.size:
                print(f"  temp: min={tp_f.min():.3f} C  max={tp_f.max():.3f} C "
                      f"mean={tp_f.mean():.3f} C")
                out_of_range = ((tp_f < -2.0) | (tp_f > 40.0)).sum()
                print(f"  temp out-of-range count (-2..40): {int(out_of_range)}")

    # ---- Summary ----
    banner("SUMMARY")
    print(f"  2d.nc time OK: {results['2d_time'][1]}  (steps={results['2d_time'][0]})")
    print(f"  3d.nc time OK: {results['3d_time'][1]}  (steps={results['3d_time'][0]})")
    print(f"  3d.nc variable count: {len(results['3d_vars'])}")
    # overall NaN/Inf/neg tally
    total_nan = total_inf = total_neg = 0
    for cat in ("elev", "uu", "vv", "temp"):
        st = results.get(cat)
        if st:
            total_nan += st["n_nan"]; total_inf += st["n_inf"]; total_neg += st["n_neg"]
    for v, st in results.get("eco", {}).items():
        if st:
            total_nan += st["n_nan"]; total_inf += st["n_inf"]; total_neg += st["n_neg"]
    print(f"  Total NaN across checked vars: {total_nan}")
    print(f"  Total Inf across checked vars: {total_inf}")
    print(f"  Total negative (eco vars)   : {total_neg}")
    print("  DONE.")


if __name__ == "__main__":
    main()
