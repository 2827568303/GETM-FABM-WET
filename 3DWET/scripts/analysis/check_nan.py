import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Check 2D output
nc2d = netCDF4.Dataset('LUOMAHU_WET.2d.nc', 'r')
print("2D Variables:", list(nc2d.variables.keys()))

# Check elev
elev = nc2d['elev'][:]
print(f"\nelev: shape={elev.shape}")
print(f"  First 5 values at t=0: {elev[0, 20:25, 20:25]}")

# Check time
time = nc2d['time'][:]
print(f"\nTime: {time[:5]} ... {time[-5:]}")

# Check if NaN
print(f"\nNaN count in elev: {np.isnan(elev).sum()}")

# Check first timestep
elev_t0 = elev[0, :, :]
print(f"\nelev at t=0: min={np.nanmin(elev_t0):.3f}, max={np.nanmax(elev_t0):.3f}")
print(f"Non-NaN cells: {np.sum(~np.isnan(elev_t0))}")

# Check a specific location
print(f"\nelev at (27,20) over time: {elev[:10, 27, 20]}")

nc2d.close()

# Check 3D output
nc3d = netCDF4.Dataset('LUOMAHU_WET.3d.nc', 'r')
print("\n=== 3D Output ===")

# Check sigma
sigma = nc3d['sigma'][:]
print(f"sigma: {sigma}")

# Check z
z = nc3d['z'][:]
print(f"\nz: shape={z.shape}")
print(f"z at t=0: {z[0, :, 27, 20] if z.ndim == 4 else 'N/A'}")

# Check temperature
temp = nc3d['temp'][:]
print(f"\ntemp: shape={temp.shape}")
print(f"NaN count: {np.isnan(temp).sum()}")
print(f"temp at t=0, surface: {temp[0, -1, 27, 20] if temp.ndim == 4 else 'N/A'}")

nc3d.close()