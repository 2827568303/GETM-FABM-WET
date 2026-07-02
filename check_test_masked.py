import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== test_case 2D output (correct masked reading) ===")
nc = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')

# Use masked array (default)
elev = nc['elev'][:]
print(f"Elev type: {type(elev)}")
print(f"Elev is masked: {np.ma.is_masked(elev)}")
print(f"Elev shape: {elev.shape}")

# Get valid values
elev_data = np.ma.getdata(elev)
elev_mask = np.ma.getmask(elev)
print(f"Elev data raw min/max: {elev_data.min():.6f} / {elev_data.max():.6f}")
print(f"Elev mask count: {elev_mask.sum()}")
print(f"Valid values (not masked): {(~elev_mask).sum()}")

# Check if _FillValue is being applied
print(f"\nElev _FillValue: {nc['elev']._FillValue}")

# Check without auto-masking
nc.set_auto_mask(False)
elev_raw = nc['elev'][:]
print(f"\nRaw elev (no auto-mask): min={elev_raw.min():.6f}, max={elev_raw.max():.6f}")
print(f"Where elev_raw != -9999: {(elev_raw != -9999).sum()}")
print(f"elev_raw[0, :, :]:")
print(elev_raw[0, :, :])

nc.close()

print("\n=== test_case 3D output ===")
nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')
nc3d.set_auto_mask(False)

# Check temp
temp = nc3d['temp'][:]
print(f"Temp raw: shape={temp.shape}")
print(f"Temp raw min/max: {temp.min():.4f} / {temp.max():.4f}")
print(f"Temp != -9999: {(temp != -9999).sum()}")

# t=0, center
print(f"\nTemp at t=0, center (k=1, j=2, i=2):")
print(f"  All layers: {temp[0, :, 2, 2]}")

# Check bathymetry in 3d
bathy3d = nc3d['bathymetry'][:]
print(f"\nBathy in 3d: shape={bathy3d.shape}")
print(f"Bathy values: {bathy3d}")

# Check some FABM variables
fabm_vars_to_check = ['abiotic_water_sO2W', 'cyanobacteria_oChla', 'wet_chla']
for var in fabm_vars_to_check:
    if var in nc3d.variables:
        data = nc3d[var][:]
        valid = data[data != -9999]
        print(f"\n{var}: shape={data.shape}")
        if len(valid) > 0:
            print(f"  valid min/max: {valid.min():.6f} / {valid.max():.6f}")
            print(f"  valid count: {len(valid)}")
            # Print center value at t=0
            print(f"  t=0, center: {data[0, :, 2, 2] if data.ndim == 4 else data[0, 2, 2]}")

nc3d.close()