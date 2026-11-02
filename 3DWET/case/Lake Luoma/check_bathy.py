import netCDF4
import numpy as np

nc = netCDF4.Dataset('bathymetry.nc')
print("Variables:", list(nc.variables.keys()))
print("Dimensions:", dict((k, len(v)) for k, v in nc.dimensions.items()))

bathy = nc.variables['bathymetry'][:]
print(f"\nBathymetry shape: {bathy.shape}")
print(f"Min: {bathy.min()}, Max: {bathy.max()}")
print(f"Mean: {bathy.mean()}, Std: {bathy.std()}")
print(f"Unique values (first 20): {np.unique(bathy)[:20]}")
print(f"Num unique: {len(np.unique(bathy))}")

# Check for problematic values
print(f"\nZero values: {(bathy == 0).sum()}")
print(f"Negative values: {(bathy < 0).sum()}")
print(f"NaN values: {np.isnan(bathy).sum()}")
print(f"Inf values: {np.isinf(bathy).sum()}")

# Check waterpoints (depth > 0)
waterpoints = (bathy > 0).sum()
print(f"\nWaterpoints (depth>0): {waterpoints} / {bathy.size}")

# Check critical depth
print(f"\nDepths < crit_depth(1.5): {(bathy[bathy > 0] < 1.5).sum()}")
print(f"Depths < min_depth(0.5): {(bathy[bathy > 0] < 0.5).sum()}")

# Check for very shallow cells
print(f"\nDepths between 0 and 0.5: {((bathy > 0) & (bathy < 0.5)).sum()}")
print(f"Depths between 0.5 and 1.5: {((bathy >= 0.5) & (bathy < 1.5)).sum()}")

# Show distribution
print("\nDepth distribution:")
for d in [0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0]:
    print(f"  <= {d}m: {(bathy <= d).sum()}")

# Check x, y coordinates
if 'x' in nc.variables:
    x = nc.variables['x'][:]
    print(f"\nx: {x.min()} to {x.max()}, len={len(x)}")
if 'y' in nc.variables:
    y = nc.variables['y'][:]
    print(f"y: {y.min()} to {y.max()}, len={len(y)}")
if 'lonc' in nc.variables:
    lonc = nc.variables['lonc'][:]
    print(f"lonc: {lonc.min()} to {lonc.max()}")
if 'latc' in nc.variables:
    latc = nc.variables['latc'][:]
    print(f"latc: {latc.min()} to {latc.max()}")

nc.close()
