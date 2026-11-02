#!/usr/bin/env python3
"""Check input data reasonableness for Theoretical Lake GETM-FABM-WET case.

Verifies:
  - Water balance: inflow vs outflow vs water-level change
  - bathymetry.nc: depth range, wet cells, anomalies
  - rivers.nc: discharge time series range, trends, jumps
  - meteo.nc: temperature, wind, radiation ranges
  - fabm_init.nc: ecological initial concentrations
"""

import os
import sys
import numpy as np
from netCDF4 import Dataset, num2date

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
F_BATHY = os.path.join(CASE_DIR, "bathymetry.nc")
F_RIVERS = os.path.join(CASE_DIR, "rivers.nc")
F_METEO = os.path.join(CASE_DIR, "meteo.nc")
F_INIT = os.path.join(CASE_DIR, "fabm_init.nc")
F_2D = os.path.join(CASE_DIR, "THEORETICAL_LAKE.2d.nc")

# River design values (from lake_summary.txt)
RIVER_MEAN = {
    "INFL_NW": 4.0, "INFL_NE": 1.5, "INFL_W": 1.5,
    "OUTFL_S": -2.25, "OUTFL_E": -4.51,
}


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def safe_minmax(arr):
    arr = np.asarray(arr)
    if arr.dtype.kind != "f":
        return float(arr.min()), float(arr.max()), arr.size
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None, None, 0
    return float(finite.min()), float(finite.max()), finite.size


def main():
    banner("INPUT DATA REASONABLENESS CHECK - Theoretical Lake")

    # ------------------------------------------------------------------
    # 1. BATHYMETRY
    # ------------------------------------------------------------------
    banner("1. bathymetry.nc")
    if not os.path.exists(F_BATHY):
        print("  MISSING")
    else:
        with Dataset(F_BATHY) as ds:
            print("  Variables:", list(ds.variables.keys()))
            print("  Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
            if "bathymetry" in ds.variables:
                b = ds.variables["bathymetry"][:]
                bset = ds.variables["bathymetry"]
                fill = getattr(bset, "_FillValue", None)
                print(f"  _FillValue: {fill}")
                b_f = b[np.isfinite(b)]
                if fill is not None:
                    b_f = b_f[b_f != fill]
                # wet cells: depth > 0 (or > crit_depth 0.3)
                wet = b_f[b_f > 0.0]
                wet_cells_2d = int((b > 0.0).sum())
                wet_cells_crit = int((b > 0.3).sum())
                print(f"  bathymetry min={b_f.min():.3f} max={b_f.max():.3f} "
                      f"mean={b_f.mean():.3f}")
                print(f"  cells with depth>0: {wet_cells_2d}  "
                      f"(expected 280 wet cells)")
                print(f"  cells with depth>0.3 (crit_depth): {wet_cells_crit}")
                print(f"  cells with depth<=0 (land): {int((b <= 0.0).sum())}")
                # check for negative depths (anomaly)
                neg = int((b < 0).sum())
                print(f"  negative depth cells (anomaly): {neg}")
                # volume estimate (500m x 500m cells)
                cellarea = 500.0 * 500.0
                vol = float((wet * cellarea).sum())
                print(f"  estimated volume: {vol/1e6:.2f} Mm3 "
                      f"(expected ~371 Mm3)")
                print(f"  avg depth (wet): {wet.mean():.3f} m "
                      f"(expected ~5.3 m)")
            # dx/dy
            for n in ("dx", "dy"):
                if n in ds.variables:
                    print(f"  {n} = {ds.variables[n][:]}")

    # ------------------------------------------------------------------
    # 2. RIVERS
    # ------------------------------------------------------------------
    banner("2. rivers.nc")
    if not os.path.exists(F_RIVERS):
        print("  MISSING")
    else:
        with Dataset(F_RIVERS) as ds:
            print("  Variables:", list(ds.variables.keys()))
            print("  Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
            t = ds.variables.get("time")
            if t is not None:
                try:
                    dates = num2date(t[:], units=t.units)
                    print(f"  time: {len(t)} steps, {dates[0]} .. {dates[-1]}")
                except Exception as e:
                    print(f"  time decode error: {e}")
            # find discharge variable(s)
            qvars = [v for v in ds.variables
                     if any(k in v.lower() for k in
                            ["discharge", "flow", "q", "river"])]
            print(f"  candidate discharge vars: {qvars}")
            for v in ds.variables:
                if v in ("time", "x", "y", "lon", "lat", "xc", "yc",
                         "lonc", "latc", "grid_type", "ioff", "joff",
                         "dx", "dy", "convc", "latu", "latv",
                         "projection", "crs"):
                    continue
                arr = ds.variables[v][:]
                if arr.ndim == 0:
                    continue
                vmin, vmax, n = safe_minmax(arr)
                if vmin is None:
                    continue
                print(f"  {v}: ndim={arr.ndim} shape={arr.shape} "
                      f"min={vmin:.4f} max={vmax:.4f} n={n}")

            # ---- Water balance analysis ----
            print("\n  -- Water balance --")
            # Try to identify river names/discharges
            rnames = ds.variables.get("river_name") or ds.variables.get("rivers")
            print(f"  River design mean Q (m3/s): {RIVER_MEAN}")
            tot_in = sum(v for v in RIVER_MEAN.values() if v > 0)
            tot_out = sum(v for v in RIVER_MEAN.values() if v < 0)
            print(f"  Total inflow = {tot_in:.2f} m3/s")
            print(f"  Total outflow = {tot_out:.2f} m3/s")
            print(f"  Net (in+out) = {tot_in + tot_out:.2f} m3/s  "
                  f"(positive => storage gain)")
            # volume change over 366 days from net flow
            net_q = tot_in + tot_out  # m3/s
            dV_river = net_q * 86400.0 * 366  # m3
            print(f"  dV from rivers over 366 d = {dV_river/1e6:.2f} Mm3")
            lake_vol = 371.05e6  # m3 from summary
            dh_river = dV_river / (70e6)  # m, surface area 70 km2
            print(f"  implied level change from rivers = {dh_river:.3f} m "
                  f"(over 70 km2)")

    # ------------------------------------------------------------------
    # 3. METEO
    # ------------------------------------------------------------------
    banner("3. meteo.nc")
    if not os.path.exists(F_METEO):
        print("  MISSING")
    else:
        with Dataset(F_METEO) as ds:
            print("  Variables:", list(ds.variables.keys()))
            print("  Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
            t = ds.variables.get("time")
            if t is not None:
                try:
                    dates = num2date(t[:], units=t.units)
                    span = (dates[-1] - dates[0])
                    print(f"  time: {len(t)} steps, {dates[0]} .. {dates[-1]}")
                except Exception as e:
                    print(f"  time decode error: {e}")
            for v in ds.variables:
                if v in ("time", "x", "y", "lon", "lat", "xc", "yc",
                         "grid_type", "ioff", "joff", "dx", "dy", "convc",
                         "latu", "latv", "projection", "crs"):
                    continue
                arr = ds.variables[v][:]
                if arr.ndim == 0:
                    continue
                vmin, vmax, n = safe_minmax(arr)
                if vmin is None:
                    print(f"  {v}: no finite data (shape {arr.shape})")
                    continue
                mean = float(np.nanmean(arr[np.isfinite(arr)])) \
                    if np.isfinite(arr).any() else float("nan")
                print(f"  {v}: min={vmin:.4f} max={vmax:.4f} "
                      f"mean={mean:.4f} shape={arr.shape}")

    # ------------------------------------------------------------------
    # 4. FABM INIT
    # ------------------------------------------------------------------
    banner("4. fabm_init.nc")
    if not os.path.exists(F_INIT):
        print("  MISSING")
    else:
        with Dataset(F_INIT) as ds:
            print("  Variables:", list(ds.variables.keys()))
            print("  Dimensions:", {k: len(v) for k, v in ds.dimensions.items()})
            for v in ds.variables:
                if v in ("time", "x", "y", "lon", "lat", "xc", "yc",
                         "grid_type", "ioff", "joff", "dx", "dy", "convc",
                         "latu", "latv", "projection", "crs", "z", "sigma",
                         "level"):
                    continue
                arr = ds.variables[v][:]
                if arr.ndim == 0:
                    continue
                vmin, vmax, n = safe_minmax(arr)
                if vmin is None:
                    print(f"  {v}: no finite data (shape {arr.shape})")
                    continue
                finite = arr[np.isfinite(arr)]
                mean = float(finite.mean()) if finite.size else float("nan")
                # detect if it is a spatial field (2D/3D) vs scalar
                print(f"  {v}: min={vmin:.6g} max={vmax:.6g} "
                      f"mean={mean:.6g} shape={arr.shape}")

    # ------------------------------------------------------------------
    # 5. Water-level change from 2D output (cross-check balance)
    # ------------------------------------------------------------------
    banner("5. Water-level change from 2d output (balance cross-check)")
    if os.path.exists(F_2D):
        with Dataset(F_2D) as ds:
            if "elev" in ds.variables:
                ev = ds.variables["elev"][:]
                # use finite only
                # mean water level first vs last
                ev0 = ev[0]
                ev1 = ev[-1]
                e0 = float(np.nanmean(ev0[np.isfinite(ev0)])) if np.isfinite(ev0).any() else float("nan")
                e1 = float(np.nanmean(ev1[np.isfinite(ev1)])) if np.isfinite(ev1).any() else float("nan")
                print(f"  elev mean at first step: {e0:.4f} m")
                print(f"  elev mean at last  step: {e1:.4f} m")
                print(f"  elev mean change       : {e1-e0:.4f} m")
                # also max change
                # compute spatial mean per timestep
                nt = ev.shape[0]
                means = np.full(nt, np.nan)
                for k in range(nt):
                    f = ev[k]
                    ff = f[np.isfinite(f)]
                    if ff.size:
                        means[k] = ff.mean()
                if np.isfinite(means).any():
                    fm = means[np.isfinite(means)]
                    print(f"  elev timeseries mean: min={fm.min():.4f} "
                          f"max={fm.max():.4f} range={fm.max()-fm.min():.4f}")
                    print(f"  elev first finite mean={fm[0]:.4f} "
                          f"last finite mean={fm[-1]:.4f}")
    print("\n  DONE.")


if __name__ == "__main__":
    main()
