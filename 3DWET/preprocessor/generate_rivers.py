"""River data generator for the 3DWET preprocessor.

Generates the two river input files consumed by GETM-FABM-WET from a
``LakeConfig``:

  - ``riverinfo.dat`` : text index file listing each river cell (1-indexed
    grid coordinates) and the GETM river name it maps to.
  - ``rivers.nc``     : NetCDF4 time series of per-river discharge, water
    temperature and water-quality concentrations.

River positions are derived from the lake mask stored in an existing
``bathymetry.nc`` (a ``lake_mask`` variable is preferred, otherwise water
cells are taken as ``bathymetry > 0``). Each river is placed on a single
edge cell selected by ``RiverConfig.edge`` ("north"/"south"/"west"/"east").

Discharge follows a wet/dry-season sinusoidal modulation for inflows; for
outflows a simplified water balance is used (outflow = -total inflow, split
equally across outflow rivers). The seasonal convention matches
``generate_meteo`` (0-based simulation day index compared against
``wet_season_start``/``wet_season_end``).

Reference: ``scripts/theoretical_lake/gen_yilong_lake.py`` Step 2 (edge
cell placement) and Step 4 (discharge computation and rivers.nc layout).
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np
import netCDF4 as nc

from .lake_config import LakeConfig, RiverConfig


# Seasonal amplitude of river water temperature (degC). Mirrors the
# ``river.temp + 8 * sin(...)`` form used in gen_yilong_lake.py Step 4;
# the phase is taken from ``LakeConfig.temp_peak_day`` so river temperature
# peaks together with the air-temperature cycle modelled by generate_meteo.
RIVER_TEMP_SEASONAL_AMP = 8.0

# Water-quality variables written per river (name suffix -> units).
_WQ_VARS: List[Tuple[str, str]] = [
    ("nh4", "g/m3"),
    ("no3", "g/m3"),
    ("po4", "g/m3"),
    ("doc", "g/m3"),
    ("poc", "g/m3"),
]


# ---------------------------------------------------------------------
# Edge-cell placement
# ---------------------------------------------------------------------
def _find_edge_cell(edge: str, lake_mask: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find a water cell on the requested lake edge.

    Returns ``(i, j)`` 0-indexed grid coordinates where ``i`` is the column
    (x) index and ``j`` is the row (y) index. The chosen cell is the middle
    of the first/last water row (north/south) or column (west/east), matching
    ``find_edge_cell`` in gen_yilong_lake.py. Returns ``None`` if no water
    cell exists for the requested edge.
    """
    ny, nx = lake_mask.shape
    edge = edge.lower()

    if edge == "north":  # smallest j (row) that contains water
        for j in range(ny):
            if lake_mask[j].any():
                water_is = np.where(lake_mask[j])[0]
                return int(water_is[len(water_is) // 2]), j
    elif edge == "south":  # largest j (row) that contains water
        for j in range(ny - 1, -1, -1):
            if lake_mask[j].any():
                water_is = np.where(lake_mask[j])[0]
                return int(water_is[len(water_is) // 2]), j
    elif edge == "west":  # smallest i (column) that contains water
        for i in range(nx):
            if lake_mask[:, i].any():
                water_js = np.where(lake_mask[:, i])[0]
                return i, int(water_js[len(water_js) // 2])
    elif edge == "east":  # largest i (column) that contains water
        for i in range(nx - 1, -1, -1):
            if lake_mask[:, i].any():
                water_js = np.where(lake_mask[:, i])[0]
                return i, int(water_js[len(water_js) // 2])
    return None


# ---------------------------------------------------------------------
# Discharge and temperature time series
# ---------------------------------------------------------------------
def _seasonal_factor(days: np.ndarray, river: RiverConfig) -> np.ndarray:
    """Seasonal discharge multiplier for each simulation day.

    Wet season (``wet_season_start`` <= day <= ``wet_season_end``):
    ``1 + amp * sin(2*pi*(day-start)/duration)`` completing one full cycle
    across the wet window. Dry season: ``1 - amp * 0.5``.
    """
    wet_start = river.wet_season_start
    wet_end = river.wet_season_end
    wet_duration = wet_end - wet_start

    # Dry-season baseline applied everywhere, wet-season values overwritten.
    factor = np.full(days.shape, 1.0 - river.seasonal_amp * 0.5, dtype=np.float64)
    is_wet = (days >= wet_start) & (days <= wet_end)
    if wet_duration > 0:
        wet_phase = 2.0 * np.pi * (days[is_wet] - wet_start) / wet_duration
        factor[is_wet] = 1.0 + river.seasonal_amp * np.sin(wet_phase)
    elif is_wet.any():
        # Degenerate single-day wet window: apply the full positive swing.
        factor[is_wet] = 1.0 + river.seasonal_amp
    return factor


def _river_temperature(days: np.ndarray, river: RiverConfig,
                       temp_peak_day: int) -> np.ndarray:
    """River water temperature (degC) with a seasonal sinusoidal cycle.

    Uses ``river.temp + RIVER_TEMP_SEASONAL_AMP * sin(...)`` with the phase
    set by ``temp_peak_day`` so the peak aligns with the air-temperature
    peak modelled by generate_meteo.
    """
    return river.temp + RIVER_TEMP_SEASONAL_AMP * np.sin(
        2.0 * np.pi * (days - temp_peak_day) / 365.0
    )


def _compute_discharge(days: np.ndarray,
                       config: LakeConfig) -> dict:
    """Compute per-river discharge time series (m3/s).

    Inflow rivers use ``base_flow * seasonal_factor``. Outflow rivers use a
    simplified water balance (outflow = -total inflow, split equally across
    outflow rivers) so total outflow matches total inflow.
    """
    n_days = days.shape[0]
    discharge = {river.name: np.zeros(n_days, dtype=np.float64)
                 for river in config.rivers}

    # Inflows: base flow modulated by the seasonal factor.
    inflow_total = np.zeros(n_days, dtype=np.float64)
    for river in config.inflow_rivers:
        q = river.base_flow * _seasonal_factor(days, river)
        discharge[river.name] = q
        inflow_total += q

    # Outflows: simplified water balance, split equally (negative sign).
    outflow_rivers = config.outflow_rivers
    if outflow_rivers:
        outflow_q = -inflow_total / len(outflow_rivers)
        for river in outflow_rivers:
            discharge[river.name] = outflow_q

    return discharge


# ---------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------
def generate_rivers(config: LakeConfig, bathymetry_path: str,
                    output_dir: str) -> str:
    """Generate ``riverinfo.dat`` and ``rivers.nc`` for a lake.

    Parameters
    ----------
    config : LakeConfig
        Lake configuration. Reads ``rivers``, ``start_date``, ``n_days``,
        ``temp_peak_day`` and ``lake_name``.
    bathymetry_path : str
        Path to an existing ``bathymetry.nc``. The lake mask is read from a
        ``lake_mask`` variable if present, otherwise derived as
        ``bathymetry > 0`` (land cells are typically ``-9999``).
    output_dir : str
        Directory where ``riverinfo.dat`` and ``rivers.nc`` are written
        (created if it does not exist).

    Returns
    -------
    str
        Path to the generated ``rivers.nc`` file, or an empty string if
        ``config.rivers`` is empty (in which case only a stub
        ``riverinfo.dat`` containing ``"0"`` is written and no ``rivers.nc``
        is created).
    """
    os.makedirs(output_dir, exist_ok=True)
    riverinfo_path = os.path.join(output_dir, "riverinfo.dat")
    rivers_path = os.path.join(output_dir, "rivers.nc")

    # --- Empty-rivers case: stub riverinfo.dat, no rivers.nc ---
    if not config.rivers:
        with open(riverinfo_path, "w") as f:
            f.write("0\n")
        print(f"[rivers] no rivers configured; wrote stub {riverinfo_path}")
        return ""

    print("=" * 70)
    print(f"Generating rivers for {config.lake_name}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Read lake mask from bathymetry.nc
    # ------------------------------------------------------------------
    with nc.Dataset(bathymetry_path, "r") as ds:
        bathymetry = ds.variables["bathymetry"][:]
        if "lake_mask" in ds.variables:
            lake_mask = np.asarray(ds.variables["lake_mask"][:], dtype=bool)
        else:
            lake_mask = np.asarray(bathymetry, dtype=float) > 0.0

    # ------------------------------------------------------------------
    # 2. Locate one edge cell per river (0-indexed), then convert to 1-indexed
    # ------------------------------------------------------------------
    river_cells: List[Tuple[str, int, int]] = []  # (name, i_1indexed, j_1indexed)
    for river in config.rivers:
        pos = _find_edge_cell(river.edge, lake_mask)
        if pos is None:
            raise ValueError(
                f"No water cell found on edge {river.edge!r} "
                f"for river {river.name!r}"
            )
        i0, j0 = pos
        river_cells.append((river.name, i0 + 1, j0 + 1))
        print(f"  {river.name} ({river.edge}/{river.flow_type}): "
              f"grid (i={i0 + 1}, j={j0 + 1})")

    # ------------------------------------------------------------------
    # 3. Write riverinfo.dat (1-indexed coordinates)
    # ------------------------------------------------------------------
    with open(riverinfo_path, "w") as f:
        f.write(f"{len(river_cells)}\n")
        for name, i, j in river_cells:
            f.write(f"{i} {j} {name} -1 -1\n")
    print(f"  riverinfo.dat: {len(river_cells)} river cells")

    # ------------------------------------------------------------------
    # 4. Compute discharge + water-quality time series
    # ------------------------------------------------------------------
    n_days = config.n_days
    days = np.arange(n_days, dtype=np.float64)
    discharge = _compute_discharge(days, config)

    # Water-balance diagnostics (simplified: outflow == inflow).
    inflow_rivers = config.inflow_rivers
    outflow_rivers = config.outflow_rivers
    total_in_vol = sum(discharge[r.name].sum() for r in inflow_rivers) * 86400.0
    total_out_vol = sum((-discharge[r.name].sum()) for r in outflow_rivers) * 86400.0
    print(f"  Inflow volume:  {total_in_vol / 1e6:.2f} Mm3 over {n_days} days")
    print(f"  Outflow volume: {total_out_vol / 1e6:.2f} Mm3 over {n_days} days")

    # ------------------------------------------------------------------
    # 5. Write rivers.nc (NetCDF4, unlimited time dimension)
    # ------------------------------------------------------------------
    time_units = f"seconds since {config.start_date} 00:00:00"
    print(f"  Writing {rivers_path}...")

    ds_riv = nc.Dataset(rivers_path, "w", format="NETCDF4")
    ds_riv.createDimension("time", None)  # unlimited

    time_v = ds_riv.createVariable("time", "f8", ("time",))
    time_v.units = time_units
    time_v.long_name = "time"
    time_v[:] = days * 86400.0

    for river in config.rivers:
        name = river.name

        # Discharge (positive = inflow, negative = outflow)
        var_q = ds_riv.createVariable(name, "f8", ("time",))
        var_q.units = "m3/s"
        var_q.long_name = f"{name} discharge (positive=inflow, negative=outflow)"
        var_q[:] = discharge[name]

        # Water temperature with seasonal variation
        var_t = ds_riv.createVariable(f"{name}_temp", "f8", ("time",))
        var_t.units = "degC"
        var_t.long_name = f"{name} water temperature"
        var_t[:] = _river_temperature(days, river, config.temp_peak_day)

        # Water-quality concentrations (constant in time)
        for wq_name, wq_units in _WQ_VARS:
            var_wq = ds_riv.createVariable(f"{name}_{wq_name}", "f8", ("time",))
            var_wq.units = wq_units
            var_wq.long_name = f"{name} {wq_name}"
            var_wq[:] = np.full(n_days, getattr(river, wq_name), dtype=np.float64)

    ds_riv.title = f"{config.lake_name} river data"
    ds_riv.source = "Generated by 3DWET preprocessor (generate_rivers.py)"
    ds_riv.history = f"Created {datetime.now()}"
    ds_riv.Conventions = "CF-1.0"
    ds_riv.close()
    print("  Done!")

    return rivers_path
