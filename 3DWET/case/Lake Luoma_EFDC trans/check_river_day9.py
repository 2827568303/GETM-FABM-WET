"""Check river flow values around day 9-10 divergence."""
import netCDF4 as nc
import numpy as np

CASE = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"

# Check capped rivers.nc
ds = nc.Dataset(f"{CASE}/rivers.nc")
t = ds.variables['time'][:] / 86400.0
print(f"River time range: day {t[0]:.2f} to {t[-1]:.2f}, {len(t)} records")
print("\nFlow values around day 7-12:")
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    print(f"\n{name}:")
    for i in range(len(t)):
        if 6 <= t[i] <= 13:
            print(f"  day {t[i]:.2f}: Q={q[i]:.2f}")
ds.close()

# Also check original
print("\n=== ORIGINAL (uncapped) ===")
ds = nc.Dataset(f"{CASE}/rivers_orig.nc")
t = ds.variables['time'][:] / 86400.0
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    print(f"\n{name} (day 7-12):")
    for i in range(len(t)):
        if 6 <= t[i] <= 13:
            print(f"  day {t[i]:.2f}: Q={q[i]:.2f}")
ds.close()
