"""Diagnose bathymetry and river position issues.

Check:
1. bathymetry.nc contents (grid, depth, coordinates)
2. riverinfo.dat vs actual grid positions
3. Whether rivers fall on water cells
"""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

print("=" * 70)
print("1. Bathymetry file inspection")
print("=" * 70)

bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
print(f"  Dimensions: {dict((d, len(bathy_ds.dimensions[d])) for d in bathy_ds.dimensions)}")
print(f"  Variables: {list(bathy_ds.variables.keys())}")

x = bathy_ds.variables['x'][:]
y = bathy_ds.variables['y'][:]
lonc = bathy_ds.variables['lonc'][:]
latc = bathy_ds.variables['latc'][:]
bathymetry = bathy_ds.variables['bathymetry'][:]

print(f"\n  x (m): min={x.min():.1f}, max={x.max():.1f}, n={len(x)}, dx={x[1]-x[0]:.1f}")
print(f"  y (m): min={y.min():.1f}, max={y.max():.1f}, n={len(y)}, dy={y[1]-y[0]:.1f}")
print(f"  lonc shape: {lonc.shape}, range: [{lonc.min():.4f}, {lonc.max():.4f}]")
print(f"  latc shape: {latc.shape}, range: [{latc.min():.4f}, {latc.max():.4f}]")

# bathymetry: positive = water depth, negative = land (or vice versa?)
print(f"\n  bathymetry stats:")
print(f"    min={np.nanmin(bathymetry):.2f}, max={np.nanmax(bathymetry):.2f}")
print(f"    mean={np.nanmean(bathymetry):.2f}")
print(f"    n_water_cells (bathy>0): {(bathymetry > 0).sum()}")
print(f"    n_land_cells (bathy<=0): {(bathymetry <= 0).sum()}")
print(f"    total cells: {bathymetry.size}")

# Show a slice of bathymetry
print(f"\n  bathymetry[20:30, 20:25] (sample):")
print(bathymetry[20:30, 20:25])

bathy_ds.close()

print()
print("=" * 70)
print("2. River positions vs grid")
print("=" * 70)

# Read riverinfo.dat
with open(os.path.join(CASE_DIR, "riverinfo.dat"), 'r') as f:
    lines = f.readlines()
print(f"  riverinfo.dat contents:")
for line in lines:
    print(f"    {line.strip()}")

# Parse river positions (i j name -1 -1)
# Note: GETM riverinfo.dat uses 1-based indexing: i=column (x), j=row (y)
n_rivers = int(lines[0].strip())
print(f"\n  River positions on grid (1-based, i=col, j=row):")
for line in lines[1:1+n_rivers]:
    parts = line.split()
    i, j, name = int(parts[0]), int(parts[1]), parts[2]
    # Convert to 0-based for array indexing
    i0, j0 = i-1, j-1
    # Check bathymetry at river position
    bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
    bathy_val = bathy_ds.variables['bathymetry'][j0, i0]  # bathymetry(y, x) = bathymetry[j, i]
    x_val = bathy_ds.variables['x'][i0]
    y_val = bathy_ds.variables['y'][j0]
    lon_val = bathy_ds.variables['lonc'][j0, i0]
    lat_val = bathy_ds.variables['latc'][j0, i0]
    print(f"    {name}: i={i}, j={j} -> x={x_val:.1f}m, y={y_val:.1f}m, "
          f"lon={lon_val:.4f}, lat={lat_val:.4f}, bathy={bathy_val:.2f}m")
    bathy_ds.close()

print()
print("=" * 70)
print("3. Check rivers.nc discharge data")
print("=" * 70)

rivers_ds = nc.Dataset(os.path.join(CASE_DIR, "rivers.nc"))
print(f"  Dimensions: {dict((d, len(rivers_ds.dimensions[d])) for d in rivers_ds.dimensions)}")
print(f"  Variables: {list(rivers_ds.variables.keys())}")

# Find river name variable or list
for vname in rivers_ds.variables:
    v = rivers_ds.variables[vname]
    if len(v.shape) == 1 and len(v) == n_rivers:
        print(f"  {vname}: {v[:]}")

# Check discharge for each river
for vname in rivers_ds.variables:
    if 'discharge' in vname.lower() or 'Q' in vname:
        v = rivers_ds.variables[vname]
        if len(v.shape) == 2:  # (time, river)
            data = v[:]
            print(f"\n  {vname} shape={v.shape}")
            for r in range(min(n_rivers, v.shape[1])):
                print(f"    River {r+1}: min={data[:,r].min():.2f}, max={data[:,r].max():.2f}, "
                      f"mean={data[:,r].mean():.2f}, first={data[0,r]:.2f}, last={data[-1,r]:.2f}")

rivers_ds.close()
