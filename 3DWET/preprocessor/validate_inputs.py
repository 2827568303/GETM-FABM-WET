"""Validate generated input files against GETM-FABM-WET requirements.

Checks file existence, NetCDF dimensions/variables, and basic data integrity.
Run after generate_* to catch format errors before model execution.
"""
from __future__ import annotations

import os
import numpy as np
import netCDF4 as nc
from typing import List

from .lake_config import LakeConfig


def validate_all(config: LakeConfig, output_dir: str) -> List[str]:
    """Validate all expected input files in output_dir.

    Returns a list of error messages; empty list means all OK.
    """
    errors: List[str] = []

    # bathymetry.nc
    bathy_path = os.path.join(output_dir, "bathymetry.nc")
    if not os.path.exists(bathy_path):
        errors.append(f"Missing: {bathy_path}")
    else:
        errors.extend(_check_bathymetry(bathy_path, config))

    # riverinfo.dat
    riverinfo_path = os.path.join(output_dir, "riverinfo.dat")
    if not os.path.exists(riverinfo_path):
        errors.append(f"Missing: {riverinfo_path}")
    else:
        errors.extend(_check_riverinfo(riverinfo_path, config))

    # rivers.nc (only if there are rivers)
    rivers_path = os.path.join(output_dir, "rivers.nc")
    if config.rivers and not os.path.exists(rivers_path):
        errors.append(f"Missing: {rivers_path} (config has {len(config.rivers)} rivers)")

    # meteo.nc
    meteo_path = os.path.join(output_dir, "meteo.nc")
    if not os.path.exists(meteo_path):
        errors.append(f"Missing: {meteo_path}")
    else:
        errors.extend(_check_meteo(meteo_path, config))

    # meteo_input.txt
    meteo_input_path = os.path.join(output_dir, "meteo_input.txt")
    if not os.path.exists(meteo_input_path):
        errors.append(f"Missing: {meteo_input_path}")

    # fabm_init.nc
    fabm_init_path = os.path.join(output_dir, "fabm_init.nc")
    if not os.path.exists(fabm_init_path):
        errors.append(f"Missing: {fabm_init_path}")
    else:
        errors.extend(_check_fabm_init(fabm_init_path, config))

    return errors


def _check_bathymetry(path: str, config: LakeConfig) -> List[str]:
    """Check bathymetry.nc dimensions, variables, and values."""
    errors = []
    try:
        ds = nc.Dataset(path, "r")
        # Dimensions
        for dim, expected in [("x", config.nx), ("y", config.ny)]:
            if dim not in ds.dimensions:
                errors.append(f"bathymetry.nc: missing dimension '{dim}'")
            elif len(ds.dimensions[dim]) != expected:
                errors.append(f"bathymetry.nc: dimension '{dim}' = {len(ds.dimensions[dim])}, expected {expected}")

        # Variables
        for var in ["x", "y", "latc", "lonc", "bathymetry"]:
            if var not in ds.variables:
                errors.append(f"bathymetry.nc: missing variable '{var}'")

        if "bathymetry" in ds.variables:
            bathy = ds.variables["bathymetry"][:]
            bathy_np = np.ma.filled(bathy, np.nan)
            water = bathy_np[bathy_np > 0]
            if water.size == 0:
                errors.append("bathymetry.nc: no water cells (all <= 0)")
            else:
                if water.min() < config.min_depth:
                    errors.append(f"bathymetry.nc: min water depth {water.min():.2f}m < config.min_depth {config.min_depth}m")
                if water.max() > config.max_depth + 0.5:
                    errors.append(f"bathymetry.nc: max water depth {water.max():.2f}m > config.max_depth {config.max_depth}m + 0.5")
                avg = water.mean()
                if abs(avg - config.avg_depth) > config.avg_depth * 0.15:
                    errors.append(f"bathymetry.nc: avg depth {avg:.2f}m differs from target {config.avg_depth}m by >15%")
        ds.close()
    except Exception as e:
        errors.append(f"bathymetry.nc: read error: {e}")
    return errors


def _check_riverinfo(path: str, config: LakeConfig) -> List[str]:
    """Check riverinfo.dat format."""
    errors = []
    try:
        with open(path, "r") as f:
            lines = f.read().strip().split("\n")
        n_rivers = int(lines[0].strip())
        data_lines = [l for l in lines[1:] if l.strip()]
        if n_rivers != len(data_lines):
            errors.append(f"riverinfo.dat: header says {n_rivers} rivers, found {len(data_lines)} lines")
        for i, line in enumerate(data_lines):
            parts = line.split()
            if len(parts) < 3:
                errors.append(f"riverinfo.dat: line {i+2} has < 3 fields: '{line}'")
                continue
            try:
                ii, jj = int(parts[0]), int(parts[1])
                if not (1 <= ii <= config.nx):
                    errors.append(f"riverinfo.dat: river {i} i={ii} out of range [1,{config.nx}]")
                if not (1 <= jj <= config.ny):
                    errors.append(f"riverinfo.dat: river {i} j={jj} out of range [1,{config.ny}]")
            except ValueError:
                errors.append(f"riverinfo.dat: line {i+2} invalid i/j: '{line}'")
    except Exception as e:
        errors.append(f"riverinfo.dat: read error: {e}")
    return errors


def _check_meteo(path: str, config: LakeConfig) -> List[str]:
    """Check meteo.nc dimensions and variables."""
    errors = []
    try:
        ds = nc.Dataset(path, "r")
        # meteo has n_days+1 time points (extra day to cover stop time, see generate_meteo)
        for dim, expected in [("lon", config.nx), ("lat", config.ny), ("time", config.n_days + 1)]:
            if dim not in ds.dimensions:
                errors.append(f"meteo.nc: missing dimension '{dim}'")
            elif len(ds.dimensions[dim]) != expected:
                errors.append(f"meteo.nc: dimension '{dim}' = {len(ds.dimensions[dim])}, expected {expected}")
        for var in ["lon", "lat", "time", "u10", "v10", "slp", "t2", "rh", "tcc", "precip", "evap"]:
            if var not in ds.variables:
                errors.append(f"meteo.nc: missing variable '{var}'")
        ds.close()
    except Exception as e:
        errors.append(f"meteo.nc: read error: {e}")
    return errors


def _check_fabm_init(path: str, config: LakeConfig) -> List[str]:
    """Check fabm_init.nc dimensions and variables."""
    errors = []
    try:
        ds = nc.Dataset(path, "r")
        for dim, expected in [("x", config.nx), ("y", config.ny)]:
            if dim not in ds.dimensions:
                errors.append(f"fabm_init.nc: missing dimension '{dim}'")
            elif len(ds.dimensions[dim]) != expected:
                errors.append(f"fabm_init.nc: dimension '{dim}' = {len(ds.dimensions[dim])}, expected {expected}")
        if "macrophytes_sD" not in ds.variables:
            errors.append("fabm_init.nc: missing variable 'macrophytes_sD'")
        ds.close()
    except Exception as e:
        errors.append(f"fabm_init.nc: read error: {e}")
    return errors
