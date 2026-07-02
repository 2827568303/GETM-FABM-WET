import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== 3D Output (with kdum=10) ===")
nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
nc3d.set_auto_mask(False)

# Check sigma
sigma = nc3d['sigma'][:]
print(f"Sigma layers: {len(sigma)}")
print(f"Sigma values: {sigma}")

# Check temp
temp = nc3d['temp'][:]
print(f"\nTemp shape: {temp.shape}")
print(f"Temp raw min/max: {temp.min():.4f} / {temp.max():.4f}")

# Count valid values (not -9999)
valid = temp[temp != -9999]
print(f"Valid temp values: {len(valid)}")
if len(valid) > 0:
    print(f"Valid temp range: {valid.min():.2f} / {valid.max():.2f}")

# Check center column
print(f"\nCenter column (j=2,i=2) at t=0:")
temp_col = temp[0, :, 2, 2]
print(f"  Temp: {temp_col}")

# Check FABM variables
if 'cyanobacteria_oChla' in nc3d.variables:
    chla = nc3d['cyanobacteria_oChla'][:]
    valid_chla = chla[chla != -9999]
    print(f"\nCyanobacteria Chla: shape={chla.shape}")
    print(f"Valid values: {len(valid_chla)}")
    if len(valid_chla) > 0:
        print(f"Range: {valid_chla.min():.6f} / {valid_chla.max():.6f}")
    # Center column
    print(f"Center column at t=0: {chla[0, :, 2, 2]}")

if 'wet_chla' in nc3d.variables:
    wet_chla = nc3d['wet_chla'][:]
    valid_wet = wet_chla[wet_chla != -9999]
    print(f"\nwet_chla: shape={wet_chla.shape}")
    print(f"Valid values: {len(valid_wet)}")
    if len(valid_wet) > 0:
        print(f"Range: {valid_wet.min():.6f} / {valid_wet.max():.6f}")

# Check bathymetry
bathy = nc3d['bathymetry'][:]
print(f"\nBathymetry: {bathy}")

nc3d.close()

print("\n=== 2D Output ===")
nc2d = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')
nc2d.set_auto_mask(False)
elev = nc2d['elev'][:]
valid_elev = elev[elev != -9999]
print(f"Elev valid: {len(valid_elev)}, range: {valid_elev.min():.6f} / {valid_elev.max():.6f}")
print(f"Elev at t=0: {elev[0, :, :]}")
nc2d.close()