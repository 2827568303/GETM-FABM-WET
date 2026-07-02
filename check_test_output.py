import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case')

print("=== test_case 2D output (after fresh run) ===")
nc = netCDF4.Dataset('GETM_FABM_WET_TEST.2d.nc', 'r')

# Check bathymetry
bathy = np.array(nc['bathymetry'][:])
print(f"Bathymetry: shape={bathy.shape}, all positive: {(bathy > 0).all()}")

# Check elev
elev = np.array(nc['elev'][:])
print(f"\nElev: shape={elev.shape}")
print(f"Elev at t=0: min={elev[0].min():.6f}, max={elev[0].max():.6f}")
print(f"Elev at t=-1: min={elev[-1].min():.6f}, max={elev[-1].max():.6f}")

# Check u, v
u = np.array(nc['u'][:])
v = np.array(nc['v'][:])
print(f"\nU: shape={u.shape}, min={u.min():.6f}, max={u.max():.6f}")
print(f"V: shape={v.shape}, min={v.min():.6f}, max={v.max():.6f}")

# Check fill value
if hasattr(nc['elev'], '_FillValue'):
    print(f"\nElev _FillValue: {nc['elev']._FillValue}")
if hasattr(nc['elev'], 'missing_value'):
    print(f"Elev missing_value: {nc['elev'].missing_value}")

nc.close()

print("\n=== test_case 3D output ===")
nc3d = netCDF4.Dataset('GETM_FABM_WET_TEST.3d.nc', 'r')

# Check sigma
sigma = nc3d['sigma'][:]
print(f"Sigma: {sigma} (len={len(sigma)})")

# Check temp
temp = np.array(nc3d['temp'][:])
print(f"\nTemp: shape={temp.shape}")
print(f"Temp at t=0, all layers at center (2,2): {temp[0, :, 2, 2]}")
print(f"Temp min/max: {np.nanmin(temp):.2f} / {np.nanmax(temp):.2f}")

# Check z
z = np.array(nc3d['z'][:])
print(f"\nZ: shape={z.shape}")
print(f"Z at t=0, center: {z[0, :, 2, 2]}")

# Check FABM variable
if 'cyanobacteria_oChla' in nc3d.variables:
    chla = np.array(nc3d['cyanobacteria_oChla'][:])
    print(f"\nCyanobacteria Chla: shape={chla.shape}")
    print(f"Chla at t=0, surface, center: {chla[0, -1, 2, 2]:.6f}")
    print(f"Chla min/max: {np.nanmin(chla):.6f} / {np.nanmax(chla):.6f}")

# Check wet_chla
if 'wet_chla' in nc3d.variables:
    wet_chla = np.array(nc3d['wet_chla'][:])
    print(f"\nwet_chla: shape={wet_chla.shape}")
    print(f"wet_chla at t=0: {wet_chla[0, :, 2, 2]}")

nc3d.close()