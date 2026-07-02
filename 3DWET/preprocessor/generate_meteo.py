"""Generate meteorological forcing file (meteo.nc) for GETM-FABM-WET.

This module is part of the 3DWET preprocessor. It reads climate parameters from a
LakeConfig and produces a NETCDF4 meteo.nc file containing daily meteorological
forcing fields (temperature, precipitation, evaporation, wind, pressure, humidity,
cloud cover) broadcast onto the lake grid.

The lake grid coordinates (lon, lat) are read from an existing bathymetry.nc file
(its 2D lonc/latc arrays; the first row / first column are used as 1D axes). A
companion meteo_input.txt (containing a single line "meteo.nc") is also written so
GETM can locate the meteo file at runtime.
"""
from __future__ import annotations

import os
from datetime import datetime

import numpy as np
import netCDF4 as nc

from .lake_config import LakeConfig


def generate_meteo(config: LakeConfig, bathymetry_path: str, output_dir: str) -> str:
    """Generate meteo.nc and meteo_input.txt for a lake.

    All climate parameters (temperature, precipitation, evaporation, wind, pressure,
    humidity, cloud cover) are read from ``config``; nothing is hardcoded.

    Parameters
    ----------
    config : LakeConfig
        Lake configuration carrying climate and grid parameters.
    bathymetry_path : str
        Path to an existing bathymetry.nc containing 2D ``lonc``/``latc`` variables.
    output_dir : str
        Directory where meteo.nc and meteo_input.txt will be written (created if
        it does not exist).

    Returns
    -------
    str
        Absolute path to the generated meteo.nc file.
    """
    os.makedirs(output_dir, exist_ok=True)

    nx, ny = config.nx, config.ny
    n_days = config.n_days
    # GETM's meteo reader looks for met_times(indx) > current_sim_time;
    # if the last meteo record equals the stop time, GETM hits EOF.
    # Fix: include one extra day of meteo data so the stop time is always covered.
    n_meteo = n_days + 1
    days = np.arange(n_meteo, dtype=np.float64)

    # Reproducible stochastic variation for precip/evap noise
    np.random.seed(42)

    # ------------------------------------------------------------------
    # 1. Read 1D lon/lat axes from bathymetry.nc
    # ------------------------------------------------------------------
    with nc.Dataset(bathymetry_path, "r") as bathy_ds:
        lonc_2d = bathy_ds.variables["lonc"][:]
        latc_2d = bathy_ds.variables["latc"][:]
    lon_1d = lonc_2d[0, :]   # first row  -> 1D lon axis (length nx)
    lat_1d = latc_2d[:, 0]   # first col  -> 1D lat axis (length ny)

    # ------------------------------------------------------------------
    # 2. Build 1-D daily meteorological time series (per day)
    # ------------------------------------------------------------------
    # Temperature: sinusoidal seasonal cycle, peak governed by temp_peak_day
    t2 = config.avg_temp + config.temp_amplitude * np.sin(
        2.0 * np.pi * (days - config.temp_peak_day) / 365.0
    )

    # Precipitation: wet season (wet_season_start..wet_season_end) high, dry season low
    base_avg_mm = config.annual_precip / n_days      # mm/day annual mean
    wet_avg_mm = base_avg_mm * 1.5                   # wet-season daily mean
    dry_avg_mm = base_avg_mm * 0.3                   # dry-season daily mean
    is_wet = (days >= config.wet_season_start) & (days <= config.wet_season_end)
    n_wet = int(is_wet.sum())
    n_dry = int((~is_wet).sum())

    precip_daily_mm = np.zeros(n_meteo, dtype=np.float64)
    # Wet season: base + exponential noise (skewed, always >= 0)
    precip_daily_mm[is_wet] = np.maximum(
        0.0, wet_avg_mm + np.random.exponential(wet_avg_mm, size=n_wet)
    )
    # Dry season: pure exponential (low mean)
    precip_daily_mm[~is_wet] = np.random.exponential(dry_avg_mm, size=n_dry)
    precip_mms = precip_daily_mm / 86400.0 / 1000.0   # mm/day -> m/s

    # Evaporation: dry season higher, wet season lower; negative = water loss
    evap_daily_mm = np.where(is_wet, config.evap_avg * 0.7, config.evap_avg * 1.3)
    evap_daily_mm = np.maximum(evap_daily_mm, 0.0)
    evap_mms = -evap_daily_mm / 86400.0 / 1000.0      # negative = water loss

    # Wind: sinusoidal; u10 amplitude = avg_wind_speed, v10 amplitude = wind_direction_variation
    wind_phase = 150.0  # mid-summer monsoon phase (days)
    u10 = config.avg_wind_speed * np.sin(
        2.0 * np.pi * (days - wind_phase) / 365.0
    )
    v10 = config.wind_direction_variation * np.cos(
        2.0 * np.pi * (days - wind_phase) / 365.0
    )

    # Sea level pressure (constant across the run)
    slp = np.full(n_meteo, float(config.slp), dtype=np.float64)

    # Relative humidity: avg + seasonal cycle, clipped to [30, 95]
    rh = config.avg_rh + 15.0 * np.sin(2.0 * np.pi * (days - 200.0) / 365.0)
    rh = np.clip(rh, 30.0, 95.0)

    # Total cloud cover: avg + seasonal cycle, clipped to [0.1, 0.9]
    tcc = config.avg_tcc + 0.3 * np.sin(2.0 * np.pi * (days - 200.0) / 365.0)
    tcc = np.clip(tcc, 0.1, 0.9)

    # Pack 1-D series; broadcast to (time, lat, lon) at write time
    meteo_1d = {
        "u10": u10,
        "v10": v10,
        "slp": slp,
        "t2": t2,
        "rh": rh,
        "tcc": tcc,
        "precip": precip_mms,
        "evap": evap_mms,
    }

    # ------------------------------------------------------------------
    # 3. Write meteo.nc (NETCDF4)
    # ------------------------------------------------------------------
    meteo_path = os.path.join(output_dir, "meteo.nc")
    ds_meteo = nc.Dataset(meteo_path, "w", format="NETCDF4")
    ds_meteo.createDimension("lon", nx)
    ds_meteo.createDimension("lat", ny)
    ds_meteo.createDimension("time", n_meteo)

    lon_v = ds_meteo.createVariable("lon", "f8", ("lon",))
    lon_v.units = "degrees_east"
    lon_v.long_name = "longitude"
    lon_v[:] = lon_1d

    lat_v = ds_meteo.createVariable("lat", "f8", ("lat",))
    lat_v.units = "degrees_north"
    lat_v.long_name = "latitude"
    lat_v[:] = lat_1d

    time_v = ds_meteo.createVariable("time", "f8", ("time",))
    time_v.units = f"seconds since {config.start_date} 00:00:00"
    time_v[:] = np.arange(n_meteo) * 86400.0

    # 32-bit float variables (wind, pressure, temperature, humidity, cloud)
    var_specs_f32 = [
        ("u10", "m s-1", "10m wind u-component"),
        ("v10", "m s-1", "10m wind v-component"),
        ("slp", "Pa", "sea level pressure"),
        ("t2", "degC", "2m air temperature"),
        ("rh", "1", "relative humidity"),
        ("tcc", "1", "total cloud cover"),
    ]
    # 64-bit float variables (water fluxes)
    var_specs_f64 = [
        ("precip", "m s-1", "precipitation rate"),
        ("evap", "m s-1", "evaporation rate (negative = water loss)"),
    ]

    for var_name, units, long_name in var_specs_f32:
        var = ds_meteo.createVariable(var_name, "f4", ("time", "lat", "lon"))
        var.units = units
        var.long_name = long_name
        data_1d = meteo_1d[var_name]
        var[:] = np.broadcast_to(
            data_1d[:, np.newaxis, np.newaxis], (n_meteo, ny, nx)
        )

    for var_name, units, long_name in var_specs_f64:
        var = ds_meteo.createVariable(var_name, "f8", ("time", "lat", "lon"))
        var.units = units
        var.long_name = long_name
        data_1d = meteo_1d[var_name]
        var[:] = np.broadcast_to(
            data_1d[:, np.newaxis, np.newaxis], (n_meteo, ny, nx)
        )

    ds_meteo.title = f"{config.lake_name} meteorology"
    ds_meteo.source = "Generated by 3DWET preprocessor generate_meteo()"
    ds_meteo.history = f"Created {datetime.now()}"
    ds_meteo.Conventions = "CF-1.0"
    ds_meteo.close()

    # ------------------------------------------------------------------
    # 4. Write meteo_input.txt (single-line pointer to meteo.nc)
    # ------------------------------------------------------------------
    meteo_input_path = os.path.join(output_dir, "meteo_input.txt")
    with open(meteo_input_path, "w") as f:
        f.write("meteo.nc\n")

    return meteo_path
