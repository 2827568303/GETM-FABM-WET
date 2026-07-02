"""Check existing bathymetry and p2d data."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")

# Check existing bathymetry
print("=" * 70)
print("Current bathymetry.nc")
print("=" * 70)
ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
b = ds.variables["bathymetry"][:]
xc = ds.variables["x"][:]
yc = ds.variables["y"][:]
lonc = ds.variables["lonc"][:]
latc = ds.variables["latc"][:]
print(f"Shape: {b.shape}")
print(f"Bathymetry: min={np.nanmin(b):.2f}, max={np.nanmax(b):.2f}, mean={np.nanmean(b):.2f}")
print(f"Water cells (b>0): {np.sum(b > 0)} of {b.size}")
print(f"x: {xc.min():.0f} to {xc.max():.0f}, dx={xc[1]-xc[0]:.0f}")
print(f"y: {yc.min():.0f} to {yc.max():.0f}, dy={yc[1]-yc[0]:.0f}")
print(f"lonc: {lonc.min():.6f} to {lonc.max():.6f}")
print(f"latc: {latc.min():.6f} to {latc.max():.6f}")
print(f"Variables: {list(ds.variables.keys())}")
ds.close()

# Read Bottom_Elev.p2d
print("\n" + "=" * 70)
print("Bottom_Elev.p2d (real bathymetry points)")
print("=" * 70)
p2d_path = os.path.join(INPUTS_DIR, "Bottom_Elev.p2d")
data = []
with open(p2d_path, "r") as f:
    header = f.readline()
    print(f"Header: {header.strip()}")
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                data.append((x, y, z))
            except ValueError:
                pass

data = np.array(data)
print(f"Points: {len(data)}")
print(f"X: {data[:, 0].min():.1f} to {data[:, 0].max():.1f}")
print(f"Y: {data[:, 1].min():.1f} to {data[:, 1].max():.1f}")
print(f"Z (elevation): {data[:, 2].min():.2f} to {data[:, 2].max():.2f}, mean={data[:, 2].mean():.2f}")
print(f"Z < 21.77 (submerged): {np.sum(data[:, 2] < 21.77)} of {len(data)}")
print(f"Z < 20.0: {np.sum(data[:, 2] < 20.0)}")
print(f"Z < 18.0: {np.sum(data[:, 2] < 18.0)}")

# Read boundary
print("\n" + "=" * 70)
print("骆马湖_边界.p2d (boundary)")
print("=" * 70)
bnd_path = os.path.join(INPUTS_DIR, "骆马湖_边界.p2d")
bnd = []
with open(bnd_path, "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                x, y = float(parts[0]), float(parts[1])
                bnd.append((x, y))
            except ValueError:
                pass
bnd = np.array(bnd)
print(f"Boundary points: {len(bnd)}")
if len(bnd) > 0:
    print(f"X: {bnd[:, 0].min():.1f} to {bnd[:, 0].max():.1f}")
    print(f"Y: {bnd[:, 1].min():.1f} to {bnd[:, 1].max():.1f}")

# Compare ranges
print("\n" + "=" * 70)
print("Comparison")
print("=" * 70)
print(f"Current bathy X range: {xc.min():.0f} to {xc.max():.0f}")
print(f"Real data X range:     {data[:, 0].min():.0f} to {data[:, 0].max():.0f}")
print(f"Current bathy Y range: {yc.min():.0f} to {yc.max():.0f}")
print(f"Real data Y range:     {data[:, 1].min():.1f} to {data[:, 1].max():.1f}")
