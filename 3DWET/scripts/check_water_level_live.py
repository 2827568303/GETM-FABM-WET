"""Check water level from 2d.nc bypassing numrecs=0 issue.

GETM writes NetCDF3 Classic format. During model run, numrecs in the file
header is not updated in real-time, so netCDF4 library reads 0 records.
This script uses scipy.io.netcdf_file which can read records by file size.
"""
import os
import sys
import numpy as np

try:
    from scipy.io import netcdf_file
except ImportError:
    print("scipy not available, trying alternative...")
    sys.exit(1)

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
f2d = os.path.join(case_dir, "LUOMAHU_WET.2d.nc")

if not os.path.exists(f2d):
    print("2d.nc not found")
    sys.exit(1)

print(f"File size: {os.path.getsize(f2d)} bytes")
print(f"Trying scipy.io.netcdf_file (mmap=False to read live file)...")

try:
    ds = netcdf_file(f2d, mode='r', mmap=False)
    print(f"Dimensions: {dict(ds.dimensions)}")
    print(f"Variables: {list(ds.variables.keys())}")

    if 'time' in ds.variables:
        t = ds.variables['time'][:]
        print(f"\nTime records: {len(t)}")
        if len(t) > 0:
            print(f"Time values (days): {t/86400.0}")

    if 'elev' in ds.variables and 'time' in ds.variables:
        elev = ds.variables['elev'][:]
        print(f"\nElev shape: {elev.shape}")
        print("Water level (elev) statistics per output time:")
        n = min(len(t), 20)
        for i in range(n):
            e = elev[i]
            mean_e = np.nanmean(e)
            max_e = np.nanmax(e)
            min_e = np.nanmin(e)
            print(f"  t={t[i]/86400:.2f}d: mean={mean_e:+.4f}m, max={max_e:+.4f}m, min={min_e:+.4f}m")

        if len(t) >= 2:
            delta = np.nanmean(elev[-1]) - np.nanmean(elev[0])
            days = (t[-1] - t[0]) / 86400.0
            rate = delta / days if days > 0 else 0
            print(f"\nOverall: {delta:+.4f}m over {days:.2f} days ({rate*1000:+.3f} mm/day)")
            print(f"\nExpected: fwf mean ~0.322 mm/day (precip-evap balance from Excel data)")
    ds.close()
except Exception as e:
    print(f"scipy read failed: {e}")
    print("\nFalling back to file-size estimation...")
    # Estimate records from file size
    fsize = os.path.getsize(f2d)
    # Each 2d record: elev(54*44) + u(54*44) + v(54*44) floats = 3*2376*4 = 28512 bytes
    # Plus time (8 bytes) per record
    # This is rough; use ncdump for precise record_size
    print(f"File size: {fsize} bytes")
    print("Use calc_numrecs.py for precise record count after model finishes.")
