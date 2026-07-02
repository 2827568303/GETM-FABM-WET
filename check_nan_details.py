import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
nc3d.set_auto_mask(False)

temp = nc3d['temp'][:]

print("Temp stats:")
print(f"  Total values: {temp.size}")
print(f"  == -9999: {(temp == -9999).sum()}")
print(f"  is NaN: {np.isnan(temp).sum()}")
print(f"  other (valid): {temp.size - (temp == -9999).sum() - np.isnan(temp).sum()}")

# Check last time step
print(f"\nLast time step (t=-1):")
temp_last = temp[-1, :, :, :]
print(f"  == -9999: {(temp_last == -9999).sum()}")
print(f"  is NaN: {np.isnan(temp_last).sum()}")

# Check surface layer last time step
print(f"\nSurface layer (k=-1) at t=-1:")
surf = temp[-1, -1, :, :]
print(surf)

# Check layer 5 at last time step center
print(f"\nLayer 5 at center (2,2) over time:")
for t in range(0, 24, 4):
    print(f"  t={t}: {temp[t, 5, 2, 2]}")

# Check what values exist besides -9999 and NaN
not_9999 = temp[temp != -9999]
not_nan = not_9999[~np.isnan(not_9999)]
print(f"\nValues that are not -9999 and not NaN: {len(not_nan)}")
if len(not_nan) > 0:
    print(f"  Min/max: {not_nan.min()} / {not_nan.max()}")
    print(f"  First 10: {not_nan[:10]}")

nc3d.close()

# Same for 2D elev
print("\n=== 2D elev ===")
nc2d = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')
nc2d.set_auto_mask(False)
elev = nc2d['elev'][:]
print(f"Total: {elev.size}")
print(f"== -9999: {(elev == -9999).sum()}")
print(f"is NaN: {np.isnan(elev).sum()}")
nc2d.close()