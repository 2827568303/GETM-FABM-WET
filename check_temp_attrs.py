import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')

# Check temp variable attributes
temp_var = nc3d['temp']
print("Temp variable attributes:")
for attr in temp_var.ncattrs():
    print(f"  {attr}: {temp_var.getncattr(attr)}")

# Check with scale/offset
print(f"\nTemp scale_factor: {getattr(temp_var, 'scale_factor', 'N/A')}")
print(f"Temp add_offset: {getattr(temp_var, 'add_offset', 'N/A')}")

# Try to read without auto mask/scale
nc3d.set_auto_mask(False)
nc3d.set_auto_scale(False)
temp_raw = nc3d['temp'][:]
print(f"\nRaw temp (no mask/scale): dtype={temp_raw.dtype}")
print(f"Unique values: {np.unique(temp_raw.flatten())[:20]}")

# Check _FillValue type
fill = getattr(temp_var, '_FillValue', None)
print(f"\n_FillValue: {fill}, type: {type(fill) if fill is not None else 'None'}")

nc3d.close()