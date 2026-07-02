"""Check macrophyte and fish values in output to diagnose why macrophytes are 0."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

# Check output.nc (FABM output) for macrophytes and fish
ds = nc.Dataset(os.path.join(CASE_DIR, "output.nc"))
print("=" * 70)
print("output.nc variables related to macrophytes and fish")
print("=" * 70)

# Find macrophyte variables
all_vars = list(ds.variables.keys())
print(f"Total variables: {len(all_vars)}")

macroph_vars = [v for v in all_vars if 'macro' in v.lower() or 'veg' in v.lower() or 'macrophyte' in v.lower()]
print(f"\nMacrophyte variables: {macroph_vars}")

fish_vars = [v for v in all_vars if 'fish' in v.lower() or 'ju' in v.lower() or 'ad' in v.lower() or 'pisc' in v.lower()]
print(f"Fish variables: {fish_vars}")

# Check values for each
print("\n" + "=" * 70)
print("Macrophyte values")
print("=" * 70)
for vname in macroph_vars:
    v = ds.variables[vname]
    data = v[:]
    print(f"\n{vname}:")
    print(f"  shape: {v.shape}, dims: {v.dimensions}")
    if len(v.shape) == 3:  # (time, y, x)
        for t_idx in [0, len(data)//2, -1]:
            t_val = data[t_idx]
            print(f"  t={t_idx}: min={np.nanmin(t_val):.6f}, max={np.nanmax(t_val):.6f}, mean={np.nanmean(t_val):.6f}")
    elif len(v.shape) == 1:  # (time,)
        print(f"  values: {data[:5]}...{data[-3:]}")
    else:
        print(f"  shape: {v.shape}")

print("\n" + "=" * 70)
print("Fish values")
print("=" * 70)
for vname in fish_vars:
    v = ds.variables[vname]
    data = v[:]
    print(f"\n{vname}:")
    print(f"  shape: {v.shape}, dims: {v.dimensions}")
    if len(v.shape) == 4:  # (time, z, y, x)
        for t_idx in [0, len(data)//2, -1]:
            t_val = data[t_idx]
            print(f"  t={t_idx}: min={np.nanmin(t_val):.6f}, max={np.nanmax(t_val):.6f}, mean={np.nanmean(t_val):.6f}")
    elif len(v.shape) == 3:  # (time, y, x) or (time, z, ...)
        for t_idx in [0, len(data)//2, -1]:
            t_val = data[t_idx]
            print(f"  t={t_idx}: min={np.nanmin(t_val):.6f}, max={np.nanmax(t_val):.6f}, mean={np.nanmean(t_val):.6f}")

ds.close()

# Also check 3d.nc for any macrophyte/fish diagnostics
print("\n" + "=" * 70)
print("Checking 3d.nc for macrophyte/fish variables")
print("=" * 70)
ds3d = nc.Dataset(os.path.join(CASE_DIR, "LUOMAHU_WET.3d.nc"))
all_vars_3d = list(ds3d.variables.keys())
macroph_3d = [v for v in all_vars_3d if 'macro' in v.lower() or 'veg' in v.lower()]
fish_3d = [v for v in all_vars_3d if 'fish' in v.lower() or 'JuFish' in v or 'AdFish' in v or 'PiscFish' in v]
print(f"3d.nc macrophyte vars: {macroph_3d}")
print(f"3d.nc fish vars: {fish_3d}")

for vname in macroph_3d + fish_3d:
    v = ds3d.variables[vname]
    data = v[:]
    print(f"\n{vname}: shape={v.shape}, dims={v.dimensions}")
    if len(v.shape) >= 3:
        t_val = data[0]
        print(f"  t=0: min={np.nanmin(t_val):.6f}, max={np.nanmax(t_val):.6f}, mean={np.nanmean(t_val):.6f}")
        if len(data) > 1:
            t_val = data[-1]
            print(f"  t=-1: min={np.nanmin(t_val):.6f}, max={np.nanmax(t_val):.6f}, mean={np.nanmean(t_val):.6f}")

ds3d.close()
