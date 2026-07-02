"""Bathymetry generator for the 3DWET preprocessor.

Generates ``bathymetry.nc`` for a GETM-FABM-WET lake model run from a
``LakeConfig``.  The file contains the curvilinear grid definition
(cell-centre coordinates in both UTM metres and geographic degrees) and
the bottom-depth field.

Supported lake shapes (``config.shape``):
  - "oval":         elongated east-west, wider in the middle and narrower
                    at the two ends via a cosine width profile (mirrors the
                    Yilong-lake reference geometry).
  - "rectangular":  every grid cell is water.
  - "elliptical":   a standard ellipse inscribed in the grid.

The depth field uses a quadratic falloff from the lake centre (deep in the
middle, shallow at the edges) and is then scaled so the mean water depth
matches ``config.avg_depth``.  Land cells are encoded with ``-9999`` and
water cells carry a positive depth value.

The netCDF layout (dimensions, variables and attributes) follows the
format used by ``scripts/theoretical_lake/gen_yilong_lake.py``.
"""
from __future__ import annotations

import math
import os
from datetime import datetime

import numpy as np
import netCDF4 as nc

from .lake_config import LakeConfig


# ---------------------------------------------------------------------
# Lake-shape masks
# ---------------------------------------------------------------------
def _oval_mask(nx: int, ny: int, shape_param: float) -> np.ndarray:
    """Elongated east-west lake with a cosine-shaped width profile.

    The half-width in y varies along x so the lake is widest in the middle
    and tapers towards the east and west ends.  ``shape_param`` (0-1)
    controls how strongly the width varies; the default LakeConfig value
    reproduces the Yilong-like taper used in ``gen_yilong_lake.py``.
    """
    mask = np.zeros((ny, nx), dtype=bool)
    cx = (nx - 1) / 2.0
    cy_center = (ny - 1) / 2.0
    for j in range(ny):
        dy_norm = abs((j - cy_center) / cy_center) if cy_center > 0 else 0.0
        for i in range(nx):
            dx_norm = (i - cx) / cx if cx > 0 else 0.0
            # Half-width in y at this x position (narrower at ends, wider in middle)
            half_width = 0.5 + shape_param * math.cos(dx_norm * math.pi * 0.8)
            half_width = max(0.05, min(1.0, half_width))
            if dy_norm <= half_width:
                mask[j, i] = True
    return mask


def _rectangular_mask(nx: int, ny: int) -> np.ndarray:
    """Every grid cell is water."""
    return np.ones((ny, nx), dtype=bool)


def _elliptical_mask(nx: int, ny: int) -> np.ndarray:
    """Standard ellipse inscribed in the grid."""
    mask = np.zeros((ny, nx), dtype=bool)
    cx = (nx - 1) / 2.0
    cy = (ny - 1) / 2.0
    for j in range(ny):
        for i in range(nx):
            dx_norm = (i - cx) / cx if cx > 0 else 0.0
            dy_norm = (j - cy) / cy if cy > 0 else 0.0
            if dx_norm * dx_norm + dy_norm * dy_norm <= 1.0:
                mask[j, i] = True
    return mask


def _build_lake_mask(config: LakeConfig) -> np.ndarray:
    """Dispatch to the shape requested by the config."""
    shape = config.shape.lower()
    if shape == "oval":
        return _oval_mask(config.nx, config.ny, config.shape_param)
    if shape == "rectangular":
        return _rectangular_mask(config.nx, config.ny)
    if shape == "elliptical":
        return _elliptical_mask(config.nx, config.ny)
    raise ValueError(
        f"Unknown lake shape: {config.shape!r} "
        f"(expected 'oval', 'rectangular' or 'elliptical')"
    )


# ---------------------------------------------------------------------
# Bathymetry (depth field)
# ---------------------------------------------------------------------
def _build_bathymetry(config: LakeConfig, lake_mask: np.ndarray) -> np.ndarray:
    """Build the depth field with a quadratic falloff from the lake centre.

    Land cells are set to ``-9999.0``; water cells are clipped to
    ``[min_depth, max_depth]`` and the whole field is then scaled so the
    mean water depth matches ``config.avg_depth``.
    """
    nx, ny = config.nx, config.ny
    bathymetry = np.full((ny, nx), -9999.0)
    cx = (nx - 1) / 2.0
    cy = (ny - 1) / 2.0

    for j in range(ny):
        for i in range(nx):
            if not lake_mask[j, i]:
                continue
            dx_norm = (i - cx) / cx if cx > 0 else 0.0
            dy_norm = (j - cy) / cy if cy > 0 else 0.0
            # Quadratic depth falloff: centre = 1.0, edge ~ 0.3
            r2 = dx_norm * dx_norm + dy_norm * dy_norm
            depth_factor = 1.0 - 0.7 * r2
            base_depth = config.max_depth * depth_factor
            base_depth = max(config.min_depth, min(config.max_depth, base_depth))
            bathymetry[j, i] = base_depth

    # Scale so the mean water depth matches the target average depth.
    water_depths = bathymetry[lake_mask]
    current_avg = float(water_depths.mean())
    if current_avg > 0:
        scale = config.avg_depth / current_avg
        bathymetry[lake_mask] = np.clip(
            bathymetry[lake_mask] * scale,
            config.min_depth,
            config.max_depth,
        )
    return bathymetry


# ---------------------------------------------------------------------
# NetCDF writer
# ---------------------------------------------------------------------
def _write_bathymetry_nc(path: str, config: LakeConfig, bathymetry: np.ndarray) -> None:
    """Write the bathymetry field to a NETCDF4 file."""
    nx, ny = config.nx, config.ny
    ds = nc.Dataset(path, "w", format="NETCDF4")

    # Dimensions: cell-centre axes plus the +1 corner (q) axes.
    ds.createDimension("x", nx)
    ds.createDimension("y", ny)
    ds.createDimension("xq", nx + 1)
    ds.createDimension("yq", ny + 1)

    # grid_type scalar (1 = Cartesian)
    grid_type_var = ds.createVariable("grid_type", "i4")
    grid_type_var[:] = 1

    # Cell-centre x coordinates (UTM metres)
    x_var = ds.createVariable("x", "f8", ("x",))
    x_var.units = "m"
    x_var.long_name = "x coordinate of cell centers"
    x_var[:] = config.x0_utm + np.arange(nx) * config.dx + config.dx / 2.0

    # Cell-centre y coordinates (UTM metres)
    y_var = ds.createVariable("y", "f8", ("y",))
    y_var.units = "m"
    y_var.long_name = "y coordinate of cell centers"
    y_var[:] = config.y0_utm + np.arange(ny) * config.dy + config.dy / 2.0

    # Latitudes of cell centres (j increases southwards -> latitude decreases)
    lat_var = ds.createVariable("latc", "f8", ("y", "x"))
    lat_var.units = "degrees_north"
    lat_var.long_name = "latitude of cell centers"
    for j in range(ny):
        lat_var[j, :] = config.lat0 + ((ny - 1) / 2.0 - j) * (config.dy / 111000.0)

    # Longitudes of cell centres (account for cos(lat) longitude scaling)
    lon_var = ds.createVariable("lonc", "f8", ("y", "x"))
    lon_var.units = "degrees_east"
    lon_var.long_name = "longitude of cell centers"
    cos_lat = math.cos(math.radians(config.lat0))
    for i in range(nx):
        lon_var[:, i] = config.lon0 + (i - (nx - 1) / 2.0) * (config.dx / (111000.0 * cos_lat))

    # Bathymetry field (positive depth, -9999 for land)
    bath_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
    bath_var.units = "m"
    bath_var.long_name = "water depth"
    bath_var.standard_name = "sea_floor_depth"
    bath_var.coordinates = "lonc latc"
    bath_var[:] = bathymetry

    # Global attributes
    ds.title = f"{config.lake_name} bathymetry"
    ds.source = "Generated by 3DWET preprocessor (generate_bathymetry.py)"
    ds.history = f"Created {datetime.now()}"
    ds.Conventions = "CF-1.0"
    ds.close()


# ---------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------
def generate_bathymetry(config: LakeConfig, output_dir: str) -> str:
    """Generate ``bathymetry.nc`` from a LakeConfig.

    Parameters
    ----------
    config : LakeConfig
        Lake definition (grid, shape, bathymetry, geography).
    output_dir : str
        Directory in which to write ``bathymetry.nc`` (created if missing).

    Returns
    -------
    str
        Absolute path to the generated ``bathymetry.nc`` file.
    """
    print("=" * 70)
    print(f"Generating bathymetry for {config.lake_name}")
    print("=" * 70)
    print(f"  Grid:   {config.nx} x {config.ny} cells, "
          f"dx={config.dx}m, dy={config.dy}m")
    print(f"  Shape:  {config.shape} (shape_param={config.shape_param})")
    print(f"  Depth:  avg={config.avg_depth}m, max={config.max_depth}m, "
          f"min={config.min_depth}m")

    # 1. Lake shape mask
    lake_mask = _build_lake_mask(config)
    n_water = int(lake_mask.sum())
    n_total = config.nx * config.ny
    lake_area = n_water * config.dx * config.dy
    print(f"  Lake cells: {n_water}/{n_total} "
          f"= {n_water / n_total * 100:.1f}%")
    print(f"  Lake area: {lake_area / 1e6:.2f} km2")

    # 2. Bathymetry (depth field)
    bathymetry = _build_bathymetry(config, lake_mask)
    water_depths = bathymetry[lake_mask]
    print(f"  Bathymetry (water cells): "
          f"avg={water_depths.mean():.2f}m, "
          f"min={water_depths.min():.2f}m, "
          f"max={water_depths.max():.2f}m")
    lake_volume = float(np.sum(water_depths) * config.dx * config.dy)
    print(f"  Lake volume: {lake_volume:.0f} m3 = {lake_volume / 1e6:.2f} Mm3")

    # 3. Write bathymetry.nc
    os.makedirs(output_dir, exist_ok=True)
    bathy_path = os.path.join(output_dir, "bathymetry.nc")
    print(f"  Writing {bathy_path}...")
    _write_bathymetry_nc(bathy_path, config, bathymetry)
    print("  Done!")
    return bathy_path
