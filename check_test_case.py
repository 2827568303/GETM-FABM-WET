import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== test_case 2D output ===")
nc = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')
print("Variables:", list(nc.variables.keys())[:20])
print("Dimensions:", dict(nc.dimensions))

# Check bathymetry/topo
if 'bathymetry' in nc.variables:
    bathy = np.array(nc['bathymetry'][:])
    print(f"\nBathymetry shape: {bathy.shape}")
    print(f"Bathymetry min/max: {bathy.min():.2f}/{bathy.max():.2f}")
    print(f"Water cells (bathy > 0): {(bathy > 0).sum()}")
    print(f"Negative cells: {(bathy < 0).sum()}")

# Check elev
if 'elev' in nc.variables:
    elev = np.array(nc['elev'][0, :, :])
    print(f"\nElev shape: {elev.shape}")
    print(f"Elev min/max: {np.nanmin(elev):.4f}/{np.nanmax(elev):.4f}")
    print(f"NaN count: {np.isnan(elev).sum()}")
    print(f"Valid cells: {(~np.isnan(elev)).sum()}")

nc.close()

print("\n=== test_case 3D output ===")
nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
print("Variables count:", len(nc3d.variables.keys()))
print("First 10 vars:", list(nc3d.variables.keys())[:10])

# Check sigma
if 'sigma' in nc3d.variables:
    sigma = nc3d['sigma'][:]
    print(f"\nSigma: {sigma}")
    print(f"Number of sigma layers: {len(sigma)}")

# Check temp
if 'temp' in nc3d.variables:
    temp = np.array(nc3d['temp'][0, :, :, :])
    print(f"\nTemp shape (t=0): {temp.shape}")
    print(f"Temp min/max: {np.nanmin(temp):.2f}/{np.nanmax(temp):.2f}")
    print(f"NaN count: {np.isnan(temp).sum()}")

# Check FABM variable
fabm_vars = [v for v in nc3d.variables.keys() if 'cyanobacteria' in v or 'wet_chla' in v]
print(f"\nFABM variables found: {fabm_vars[:5]}")

nc3d.close()