import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== 3D Output (NO FABM, kdum=10) ===")
nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
nc3d.set_auto_mask(False)

# Check sigma
sigma = nc3d['sigma'][:]
print(f"Sigma layers: {len(sigma)}")
print(f"Sigma: {sigma}")

# Check temp
temp = nc3d['temp'][:]
print(f"\nTemp shape: {temp.shape}")
print(f"Temp min/max: {temp.min():.4f} / {temp.max():.4f}")

# Count -9999 and NaN
print(f"  == -9999: {(temp == -9999).sum()}")
print(f"  is NaN: {np.isnan(temp).sum()}")
valid = temp[(temp != -9999) & (~np.isnan(temp))]
print(f"  valid: {len(valid)}")
if len(valid) > 0:
    print(f"  valid range: {valid.min():.2f} / {valid.max():.2f}")

# Center column
print(f"\nCenter column (2,2) at t=0:")
print(f"  Temp: {temp[0, :, 2, 2]}")

# Check 2D elev
nc2d = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')
nc2d.set_auto_mask(False)
elev = nc2d['elev'][:]
print(f"\nElev: shape={elev.shape}")
print(f"  min/max: {elev.min():.6f} / {elev.max():.6f}")
print(f"  NaN: {np.isnan(elev).sum()}")
print(f"  == -9999: {(elev == -9999).sum()}")
print(f"  elev[0]: {elev[0, :, :]}")

nc3d.close()
nc2d.close()