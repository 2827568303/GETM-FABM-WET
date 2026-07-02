"""Check output.nc format and water level (z variable)."""
import netCDF4 as nc
import numpy as np
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
fout = os.path.join(case_dir, "output.nc")

ds = nc.Dataset(fout)
print(f"data_model: {ds.data_model}")
print(f"time dim: {len(ds.dimensions['time'])}")
print(f"Variables: {list(ds.variables.keys())[:20]}...")

if 'z' in ds.variables:
    z = ds.variables['z']
    print(f"\nz variable shape: {z.shape}")
    t = ds.variables['time'][:]
    print(f"Time records: {len(t)}")
    if len(t) > 0:
        print(f"Time values (days): {t/86400.0}")
        print("\nWater level (z) statistics:")
        for i in range(min(len(t), 20)):
            zi = z[i]
            mean_z = np.nanmean(zi)
            print(f"  t={t[i]/86400:.2f}d: mean={mean_z:+.4f}m")
        if len(t) >= 2:
            delta = np.nanmean(z[-1]) - np.nanmean(z[0])
            days = (t[-1] - t[0]) / 86400.0
            rate = delta / days if days > 0 else 0
            print(f"\nOverall: {delta:+.4f}m over {days:.2f} days ({rate*1000:+.3f} mm/day)")
            print(f"Expected: fwf mean ~0.322 mm/day (from Excel precip-evap balance)")
ds.close()
