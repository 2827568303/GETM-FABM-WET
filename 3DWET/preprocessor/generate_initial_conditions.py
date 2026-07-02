"""Generate FABM initial conditions (fabm_init.nc) for a lake.

This module produces the NetCDF4 file consumed by GETM-FABM-WET as the initial
state of the FABM variables. Only state variables that require a spatial
distribution are written here; all other variables (nutrients, pelagic
phytoplankton/zooplankton/fish) are left to the uniform initialization defined
in fabm.yaml.

Currently the only spatially-varying variable is `macrophytes_sD` (submerged
macrophyte biomass, gDW/m2), which is placed in shallow littoral cells defined
by `LakeConfig.macrophyte_depth_range`.

Reference: scripts/theoretical_lake/gen_yilong_lake.py, Step 5.
"""
from __future__ import annotations

import os

import numpy as np
import netCDF4 as nc

from .lake_config import LakeConfig


def generate_initial_conditions(config: LakeConfig,
                                bathymetry_path: str,
                                output_dir: str) -> str:
    """Generate the fabm_init.nc initial-conditions file.

    Parameters
    ----------
    config : LakeConfig
        Lake configuration. Reads nx, ny and macrophyte_* fields.
    bathymetry_path : str
        Path to an existing bathymetry.nc file. Reads `bathymetry`, `lake_mask`
        (if present, otherwise derived from bathymetry > 0) and the 2D `lonc`/
        `latc` arrays (first row / first column become the 1D lon/lat axes).
    output_dir : str
        Directory where fabm_init.nc will be written (created if missing).

    Returns
    -------
    str
        Absolute path to the generated fabm_init.nc file.
    """
    nx, ny = config.nx, config.ny
    macrophyte_biomass = config.macrophyte_biomass
    depth_min, depth_max = config.macrophyte_depth_range

    # ------------------------------------------------------------------
    # Read lake_mask, bathymetry and lon/lat from bathymetry.nc
    # ------------------------------------------------------------------
    with nc.Dataset(bathymetry_path, "r") as ds_bathy:
        bathymetry = ds_bathy.variables["bathymetry"][:]

        # Prefer an explicit lake_mask variable; otherwise derive it from
        # positive bathymetry (land cells are typically -9999.0).
        if "lake_mask" in ds_bathy.variables:
            lake_mask = np.asarray(ds_bathy.variables["lake_mask"][:], dtype=bool)
        else:
            lake_mask = np.asarray(bathymetry, dtype=float) > 0.0

        lonc = ds_bathy.variables["lonc"][:]  # 2D (y, x)
        latc = ds_bathy.variables["latc"][:]  # 2D (y, x)

    # 1D axes from the first row / first column
    lon_1d = np.asarray(lonc[0, :], dtype=np.float64)
    lat_1d = np.asarray(latc[:, 0], dtype=np.float64)

    # Sanity: ensure shapes match config
    if lake_mask.shape != (ny, nx):
        raise ValueError(
            f"lake_mask shape {lake_mask.shape} does not match "
            f"config (ny={ny}, nx={nx})"
        )
    if lon_1d.shape != (nx,) or lat_1d.shape != (ny,):
        raise ValueError(
            f"lon/lat axes have wrong shape: lon={lon_1d.shape}, lat={lat_1d.shape}, "
            f"expected ({nx},) and ({ny},)"
        )

    # ------------------------------------------------------------------
    # Build macrophyte mask: shallow water cells inside the lake
    # ------------------------------------------------------------------
    bathymetry = np.asarray(bathymetry, dtype=float)
    macrophyte_mask = (
        lake_mask
        & (bathymetry >= depth_min)
        & (bathymetry <= depth_max)
    )
    n_macro = int(macrophyte_mask.sum())
    n_water = int(lake_mask.sum())
    coverage_pct = (n_macro / n_water * 100.0) if n_water > 0 else 0.0

    # 3D macrophyte field (z, y, x) with biomass where mask is True
    macro_field = np.zeros((1, ny, nx), dtype=np.float64)
    macro_field[0][macrophyte_mask] = macrophyte_biomass

    # ------------------------------------------------------------------
    # Write fabm_init.nc
    # ------------------------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fabm_init.nc")

    with nc.Dataset(output_path, "w", format="NETCDF4") as ds:
        ds.createDimension("x", nx)
        ds.createDimension("y", ny)
        ds.createDimension("z", 1)

        lon_v = ds.createVariable("lon", "f8", ("x",))
        lon_v.units = "degrees_east"
        lon_v.long_name = "longitude"
        lon_v[:] = lon_1d

        lat_v = ds.createVariable("lat", "f8", ("y",))
        lat_v.units = "degrees_north"
        lat_v.long_name = "latitude"
        lat_v[:] = lat_1d

        z_v = ds.createVariable("z", "f8", ("z",))
        z_v.units = "m"
        z_v.long_name = "depth"
        z_v[:] = [0.0]

        macro_var = ds.createVariable(
            "macrophytes_sD", "f8", ("z", "y", "x"))
        macro_var.units = "gDW/m2"
        macro_var.long_name = "submerged macrophyte initial biomass"
        macro_var.coordinates = "lon lat"
        macro_var[:] = macro_field

        ds.title = f"{config.lake_name} FABM initial conditions"
        ds.source = "Generated by preprocessor.generate_initial_conditions"
        ds.runid = config.runid

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    print(f"[fabm_init] wrote {output_path}")
    print(f"  macrophyte cells: {n_macro} / {n_water} water cells "
          f"({coverage_pct:.1f}% coverage)")
    print(f"  macrophyte depth range: {depth_min}-{depth_max} m, "
          f"biomass: {macrophyte_biomass} gDW/m2")

    return output_path
