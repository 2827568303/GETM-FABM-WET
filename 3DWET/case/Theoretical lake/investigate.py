#!/usr/bin/env python3
"""Focused investigation: last-timestep zero issue, diatoms growth,
river discharge values (excluding fill), and time decoding."""

import os
import numpy as np
from netCDF4 import Dataset, num2date

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
F3D = os.path.join(CASE_DIR, "THEORETICAL_LAKE.3d.nc")
F2D = os.path.join(CASE_DIR, "THEORETICAL_LAKE.2d.nc")
F_RIVERS = os.path.join(CASE_DIR, "rivers.nc")


def banner(t):
    print("\n" + "=" * 70); print(t); print("=" * 70)


def main():
    # ---- Time variable inspection ----
    banner("A. Time variable raw inspection (2d & 3d)")
    for f, lbl in [(F2D, "2d"), (F3D, "3d")]:
        with Dataset(f) as ds:
            t = ds.variables["time"]
            raw = t[:]
            print(f"[{lbl}] time units='{getattr(t,'units','?')}' "
                  f"calendar='{getattr(t,'calendar','?')}'")
            print(f"[{lbl}] raw first 3 = {raw[:3]}")
            print(f"[{lbl}] raw last 3  = {raw[-3:]}")
            print(f"[{lbl}] n={len(t)}  raw min={raw.min()} raw max={raw.max()}")
            diffs = np.diff(raw)
            print(f"[{lbl}] dt min={diffs.min()} max={diffs.max()} "
                  f"mean={diffs.mean()}  (unique dt count={len(np.unique(diffs))})")

    # ---- Last-timestep zero investigation ----
    banner("B. Last-timestep zero investigation (3d.nc)")
    with Dataset(F3D) as ds:
        t = ds.variables["time"][:]
        nt = len(t)
        for vname in ["temp", "diatoms_sDW", "cyanobacteria_sDW",
                      "abiotic_water_sNH4W", "JuFish_sD"]:
            if vname not in ds.variables:
                continue
            arr = ds.variables[vname][:]
            print(f"\n  {vname} (shape {arr.shape}):")
            for k in [0, nt//4, nt//2, 3*nt//4, nt-3, nt-2, nt-1]:
                sl = arr[k]
                fin = sl[np.isfinite(sl)]
                # exclude fill values < -1e19
                fin = fin[fin > -1e19]
                if fin.size:
                    print(f"    t[{k}] mean={fin.mean():.6g} "
                          f"min={fin.min():.6g} max={fin.max():.6g} "
                          f"n_finite={fin.size}/{sl.size}")
                else:
                    print(f"    t[{k}] ALL FILL/ZERO  n_finite={fin.size}/{sl.size}")

    # ---- Diatoms growth time series ----
    banner("C. Diatoms & key phyto time series (spatial mean per step)")
    with Dataset(F3D) as ds:
        nt = len(ds.variables["time"])
        for vname in ["diatoms_sDW", "cyanobacteria_sDW", "greens_sDW",
                      "cladocerans_sD", "copepods_sD",
                      "abiotic_water_sPO4W", "abiotic_water_sNO3W",
                      "abiotic_water_sO2W", "temp"]:
            if vname not in ds.variables:
                continue
            arr = ds.variables[vname][:]
            means = []
            for k in range(nt):
                sl = arr[k]
                fin = sl[np.isfinite(sl)]
                fin = fin[fin > -1e19]
                means.append(fin.mean() if fin.size else np.nan)
            means = np.array(means)
            print(f"  {vname}:")
            idx = np.isfinite(means)
            if idx.any():
                fm = means[idx]
                print(f"    finite mean series: min={fm.min():.4g} "
                      f"max={fm.max():.4g}")
                # print quarterly snapshots
                qs = [0, nt//4, nt//2, 3*nt//4, nt-3, nt-2, nt-1]
                for q in qs:
                    print(f"      t[{q}] mean={means[q]:.6g}")
                # peak location
                pk = np.nanargmax(means)
                print(f"    PEAK at t[{pk}] value={means[pk]:.6g}")

    # ---- Rivers: discharge excluding fill ----
    banner("D. Rivers.nc discharge (excluding fill 9.97e36)")
    with Dataset(F_RIVERS) as ds:
        for v in ["INFL_NW", "INFL_NE", "INFL_W", "OUTFL_S", "OUTFL_E"]:
            arr = ds.variables[v][:]
            fill = getattr(ds.variables[v], "_FillValue", None)
            fav = arr[arr < 1e30]
            if fav.size:
                print(f"  {v}: real-range min={fav.min():.4f} "
                      f"max={fav.max():.4f} mean={fav.mean():.4f} "
                      f"n_real={fav.size}/{arr.size}  _FillValue={fill}")
            else:
                print(f"  {v}: ALL FILL  _FillValue={fill}")
        # nutrient ranges for inflows
        print("\n  River nutrient concentrations (real values):")
        for v in ds.variables:
            if v.endswith("_nh4") or v.endswith("_no3") or v.endswith("_po4") \
               or v.endswith("_temp"):
                arr = ds.variables[v][:]
                fav = arr[arr < 1e30]
                if fav.size:
                    print(f"  {v}: min={fav.min():.4f} max={fav.max():.4f} "
                          f"mean={fav.mean():.4f}")

    # ---- Elev time series from 2D ----
    banner("E. Elev spatial-mean time series (2d)")
    with Dataset(F2D) as ds:
        ev = ds.variables["elev"][:]
        nt = ev.shape[0]
        means = []
        for k in range(nt):
            sl = ev[k]
            fin = sl[np.isfinite(sl)]
            fin = fin[fin > -1e19]
            means.append(fin.mean() if fin.size else np.nan)
        means = np.array(means)
        idx = np.isfinite(means)
        if idx.any():
            fm = means[idx]
            print(f"  elev mean series: min={fm.min():.4f} max={fm.max():.4f} "
                  f"first={means[0]:.4f} last={means[-1]:.4f}")
            for q in [0, nt//4, nt//2, 3*nt//4, nt-1]:
                print(f"    t[{q}] elev_mean={means[q]:.4f}")

    print("\n  DONE.")


if __name__ == "__main__":
    main()
