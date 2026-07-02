import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

print("=== Checking output files ===\n")

# Check 2D output
nc2d = netCDF4.Dataset('LUOMAHU_WET.2d.nc', 'r')
print("2D Output Variables:", list(nc2d.variables.keys())[:15], "...")
print("Dimensions:", dict(nc2d.dimensions))

# Check elevation
if 'D' in nc2d.variables:
    D = nc2d['D'][:]
    print(f"\nWater level D: shape={D.shape}, min={D.min():.3f}, max={D.max():.3f}")
    # Check time variation
    D_time = D[:, 27, 20]  # middle of lake
    print(f"Water level at center over time: min={D_time.min():.3f}, max={D_time.max():.3f}")

# Check velocity U
if 'u' in nc2d.variables:
    u = nc2d['u'][:]
    print(f"\nVelocity U: shape={u.shape}, min={u.min():.4f}, max={u.max():.4f}")

# Check velocity V
if 'v' in nc2d.variables:
    v = nc2d['v'][:]
    print(f"Velocity V: shape={v.shape}, min={v.min():.4f}, max={v.max():.4f}")

nc2d.close()

# Check 3D output
print("\n=== 3D Output ===")
nc3d = netCDF4.Dataset('LUOMAHU_WET.3d.nc', 'r')
print("Variables:", list(nc3d.variables.keys())[:15], "...")

# Check temperature
if 'temp' in nc3d.variables:
    temp = nc3d['temp'][:]
    print(f"\nTemperature: shape={temp.shape}")
    if temp.size > 0:
        print(f"  min={temp.min():.2f}, max={temp.max():.2f}")
        # Check spatial variation at surface
        temp_surf = temp[:, -1, :, :]  # surface layer
        print(f"  Surface: min={temp_surf.min():.2f}, max={temp_surf.max():.2f}")

# Check sigma levels
if 'z' in nc3d.variables:
    z = nc3d['z'][:]
    print(f"\nSigma levels (z): shape={z.shape}")
    if z.size > 0:
        print(f"  z values: {z[0, :5] if z.ndim > 1 else z[:5]}")

# Check some FABM variables
if 'cyanobacteria_oChla' in nc3d.variables:
    chla = nc3d['cyanobacteria_oChla'][:]
    print(f"\nCyanobacteria Chla: shape={chla.shape}")
    if chla.size > 0:
        print(f"  min={chla.min():.4f}, max={chla.max():.4f}")

nc3d.close()

print("\n=== File sizes ===")
for f in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc']:
    size = os.path.getsize(f) / (1024*1024)
    print(f"{f}: {size:.2f} MB")