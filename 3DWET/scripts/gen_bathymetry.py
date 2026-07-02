"""Generate bathymetry.nc from real Bottom_Elev.p2d and boundary data.

Converts bottom elevation (m above sea level) to water depth (m):
  depth = initial_water_level - bottom_elevation
  initial_water_level = 21.79 m (average of 3 stations on 2020-01-01)

Land cells (outside lake boundary) are set to -10.0.

Coordinate system: UTM zone 50N (WGS84)
  - x/y are UTM easting/northing (meters)
  - lonc/latc are computed via direct UTM->lat/lon conversion
"""
import netCDF4 as nc
import numpy as np
from scipy.interpolate import griddata
from matplotlib.path import Path
import os
import sys
import math

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")

# Grid parameters (must match existing bathymetry.nc)
IL, IH = 1, 44
JL, JH = 1, 54
DX, DY = 500.0, 500.0
X0, Y0 = 599250.0, 3762250.0  # lower-left corner of first cell

# Initial water level (average of 3 stations on 2020-01-01)
INITIAL_WATER_LEVEL = 21.79

# Land marker
LAND_VALUE = -10.0

# UTM zone for Luomahu Lake (118E -> zone 50)
UTM_ZONE = 50


def utm_to_latlon(easting, northing, zone=UTM_ZONE):
    """Convert UTM (WGS84) to lat/lon. Vectorized.

    Args:
        easting: UTM easting in meters (scalar or array)
        northing: UTM northing in meters (scalar or array)
        zone: UTM zone number

    Returns:
        (lat, lon) in degrees
    """
    # WGS84 parameters
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e2 = 2*f - f*f
    e_prime2 = e2 / (1 - e2)

    x = np.asarray(easting) - 500000.0
    y = np.asarray(northing)

    M = y / k0
    mu = M / (a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))

    e1 = (1 - np.sqrt(1 - e2)) / (1 + np.sqrt(1 - e2))
    phi1 = mu + (3*e1/2 - 27*e1**3/32) * np.sin(2*mu)
    phi1 = phi1 + (21*e1**2/16 - 55*e1**4/32) * np.sin(4*mu)
    phi1 = phi1 + (151*e1**3/96) * np.sin(6*mu)

    N1 = a / np.sqrt(1 - e2 * np.sin(phi1)**2)
    T1 = np.tan(phi1)**2
    C1 = e_prime2 * np.cos(phi1)**2
    R1 = a * (1 - e2) / (1 - e2 * np.sin(phi1)**2)**1.5
    D = x / (N1 * k0)

    lat = phi1 - (N1 * np.tan(phi1) / R1) * (D**2/2
         - (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e_prime2) * D**4/24
         + (61 + 90*T1 + 298*C1 + 45*T1**2 - 252*e_prime2 - 3*C1**2) * D**6/720)

    lon = (D - (1 + 2*T1 + C1) * D**3/6
          + (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e_prime2 + 24*T1**2) * D**5/120) / np.cos(phi1)
    lon = lon * 180/np.pi + zone * 6 - 183  # Central meridian
    lat = lat * 180/np.pi

    return lat, lon


def read_p2d_elevation(filepath):
    """Read X Y Z elevation points from p2d file."""
    data = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    data.append((x, y, z))
                except ValueError:
                    continue
    return np.array(data)


def read_boundary(filepath):
    """Read boundary polygon points."""
    pts = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    x, y = float(parts[0]), float(parts[1])
                    pts.append((x, y))
                except ValueError:
                    continue
    return np.array(pts)


def main():
    print("=" * 70)
    print("Generating bathymetry.nc from real elevation data")
    print("=" * 70)

    # Read real elevation data
    elev_data = read_p2d_elevation(os.path.join(INPUTS_DIR, "Bottom_Elev.p2d"))
    print(f"Elevation points: {len(elev_data)}")
    print(f"  X: {elev_data[:, 0].min():.1f} to {elev_data[:, 0].max():.1f}")
    print(f"  Y: {elev_data[:, 1].min():.1f} to {elev_data[:, 1].max():.1f}")
    print(f"  Z: {elev_data[:, 2].min():.2f} to {elev_data[:, 2].max():.2f}")

    # Read boundary
    boundary = read_boundary(os.path.join(INPUTS_DIR, "骆马湖_边界.p2d"))
    print(f"Boundary points: {len(boundary)}")

    # Create grid cell centers
    nx, ny = IH - IL + 1, JH - JL + 1
    x_centers = X0 + (np.arange(nx) + 0.5) * DX
    y_centers = Y0 + (np.arange(ny) + 0.5) * DY
    print(f"Grid: {nx} x {ny}")
    print(f"  X centers: {x_centers[0]:.1f} to {x_centers[-1]:.1f}")
    print(f"  Y centers: {y_centers[0]:.1f} to {y_centers[-1]:.1f}")

    # Create 2D meshgrid of cell centers
    Xg, Yg = np.meshgrid(x_centers, y_centers)  # shape (ny, nx)
    grid_points = np.column_stack([Xg.ravel(), Yg.ravel()])

    # Interpolate elevation to grid using nearest then linear
    print("Interpolating elevations to grid...")
    # Use linear interpolation, fallback to nearest for extrapolation
    elev_linear = griddata(elev_data[:, :2], elev_data[:, 2], grid_points, method="linear")
    elev_nearest = griddata(elev_data[:, :2], elev_data[:, 2], grid_points, method="nearest")
    elev_grid = np.where(np.isnan(elev_linear), elev_nearest, elev_linear)
    elev_grid = elev_grid.reshape(ny, nx)
    print(f"  Grid elevation: min={np.nanmin(elev_grid):.2f}, max={np.nanmax(elev_grid):.2f}, mean={np.nanmean(elev_grid):.2f}")

    # Determine lake mask using boundary polygon
    print("Determining lake boundary mask...")
    # Close the polygon
    boundary_closed = np.vstack([boundary, boundary[0:1]])
    lake_path = Path(boundary_closed)
    inside = lake_path.contains_points(grid_points)
    inside = inside.reshape(ny, nx)
    print(f"  Water cells (inside boundary): {np.sum(inside)} of {nx * ny}")

    # Convert elevation to water depth
    depth_grid = INITIAL_WATER_LEVEL - elev_grid
    # Set cells outside boundary to land
    depth_grid[~inside] = LAND_VALUE
    # Set cells with very small depth (< 0.1m) to land
    depth_grid[depth_grid < 0.1] = LAND_VALUE
    # Cap maximum depth
    depth_grid[depth_grid > 20.0] = 20.0

    n_water = np.sum(depth_grid > 0)
    n_land = np.sum(depth_grid <= 0)
    print(f"Final bathymetry:")
    print(f"  Water cells: {n_water}")
    print(f"  Land cells: {n_land}")
    print(f"  Depth range: {depth_grid[depth_grid > 0].min():.2f} to {depth_grid[depth_grid > 0].max():.2f} m")
    print(f"  Mean depth: {depth_grid[depth_grid > 0].mean():.2f} m")

    # Compute lon/lat from UTM (zone 50N) using direct conversion
    print("Computing lon/lat from UTM (zone 50N)...")
    # Create 2D meshgrid of UTM coordinates
    Xg_utm, Yg_utm = np.meshgrid(x_centers, y_centers)  # shape (ny, nx)
    LATC, LONC = utm_to_latlon(Xg_utm, Yg_utm)
    print(f"  lonc range: {LONC.min():.4f} to {LONC.max():.4f}")
    print(f"  latc range: {LATC.min():.4f} to {LATC.max():.4f}")

    # Write bathymetry.nc
    out_path = os.path.join(CASE_DIR, "bathymetry.nc")
    print(f"\nWriting {out_path}...")

    # Backup original
    backup_path = out_path + ".bak"
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(out_path, backup_path)
        print(f"  Backed up original to {backup_path}")

    ds = nc.Dataset(out_path, "w", format="NETCDF4")

    # Dimensions
    ds.createDimension("x", nx)
    ds.createDimension("y", ny)
    ds.createDimension("xq", nx + 1)
    ds.createDimension("yq", ny + 1)

    # Variables
    grid_type = ds.createVariable("grid_type", "i4")
    grid_type[:] = 1  # cartesian

    x_var = ds.createVariable("x", "f8", ("x",))
    x_var[:] = x_centers
    x_var.units = "m"
    x_var.long_name = "x coordinate of cell centers"

    y_var = ds.createVariable("y", "f8", ("y",))
    y_var[:] = y_centers
    y_var.units = "m"
    y_var.long_name = "y coordinate of cell centers"

    lonc_var = ds.createVariable("lonc", "f8", ("y", "x"))
    lonc_var[:] = LONC
    lonc_var.units = "degrees_east"
    lonc_var.long_name = "longitude of cell centers"

    latc_var = ds.createVariable("latc", "f8", ("y", "x"))
    latc_var[:] = LATC
    latc_var.units = "degrees_north"
    latc_var.long_name = "latitude of cell centers"

    bathy_var = ds.createVariable("bathymetry", "f8", ("y", "x"))
    bathy_var[:] = depth_grid
    bathy_var.units = "m"
    bathy_var.long_name = "water depth"
    bathy_var.standard_name = "sea_floor_depth"
    bathy_var.coordinates = "lonc latc"

    ds.title = "Luomahu Lake bathymetry (real data)"
    ds.source = "Generated from Bottom_Elev.p2d and boundary data"
    ds.history = f"Created {np.datetime64('now')} with gen_bathymetry.py"
    ds.Conventions = "CF-1.0"

    ds.close()
    print("Done!")

    # Print summary for river position determination
    print("\n" + "=" * 70)
    print("Grid cell coordinates (for river placement)")
    print("=" * 70)
    print("Water cells on boundary (edge of lake):")
    # Find boundary water cells (water cells adjacent to land)
    water_mask = depth_grid > 0
    edge_cells = []
    for j in range(ny):
        for i in range(nx):
            if not water_mask[j, i]:
                continue
            # Check if any neighbor is land
            is_edge = False
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nj, ni = j + dj, i + di
                if 0 <= nj < ny and 0 <= ni < nx:
                    if not water_mask[nj, ni]:
                        is_edge = True
                        break
                else:
                    is_edge = True
                    break
            if is_edge:
                edge_cells.append((i + 1, j + 1, x_centers[i], y_centers[j]))
    print(f"  Total edge cells: {len(edge_cells)}")
    # Print edge cells grouped by side
    north = [c for c in edge_cells if c[3] > y_centers[-1] - 1500]
    south = [c for c in edge_cells if c[3] < y_centers[0] + 1500]
    west = [c for c in edge_cells if c[2] < x_centers[0] + 1500]
    east = [c for c in edge_cells if c[2] > x_centers[-1] - 1500]
    print(f"  North edge: {len(north)} cells")
    for c in north[:5]:
        print(f"    i={c[0]}, j={c[1]}, x={c[2]:.0f}, y={c[3]:.0f}")
    print(f"  South edge: {len(south)} cells")
    for c in south[:5]:
        print(f"    i={c[0]}, j={c[1]}, x={c[2]:.0f}, y={c[3]:.0f}")
    print(f"  West edge: {len(west)} cells")
    for c in west[:5]:
        print(f"    i={c[0]}, j={c[1]}, x={c[2]:.0f}, y={c[3]:.0f}")
    print(f"  East edge: {len(east)} cells")
    for c in east[:5]:
        print(f"    i={c[0]}, j={c[1]}, x={c[2]:.0f}, y={c[3]:.0f}")


if __name__ == "__main__":
    main()
