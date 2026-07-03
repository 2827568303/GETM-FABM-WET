"""Check river flow values around day 16-18 (crash at day 17.9)."""
import netCDF4 as nc
import numpy as np

CASE = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"

ds = nc.Dataset(f"{CASE}/rivers.nc")
t = ds.variables['time'][:] / 86400.0
print("Flow values around day 14-22:")
for name in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    q = ds.variables[name][:]
    print(f"\n{name}:")
    for i in range(len(t)):
        if 13 <= t[i] <= 22:
            print(f"  day {t[i]:.2f}: Q={q[i]:.2f}")
ds.close()
