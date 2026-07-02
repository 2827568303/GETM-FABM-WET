"""Verify repaired NetCDF files have valid data."""
import netCDF4 as nc
import numpy as np
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        continue

    print(f"\n{'='*60}")
    print(f"Verifying: {fname}")
    print(f"{'='*60}")

    with nc.Dataset(path, 'r') as ds:
        t = ds.variables['time'][:]
        print(f"  time: {t}")

        # Check a data variable
        test_vars = ['elev', 'temp', 'uu', 'abiotic_water_sNH4W']
        for vname in test_vars:
            if vname in ds.variables:
                v = ds.variables[vname]
                print(f"  {vname}: shape={v.shape}")
                # Read first and last time step
                if len(v.shape) == 3:  # (time, y, x)
                    d0 = v[0, :, :]
                    d_last = v[-1, :, :]
                    print(f"    t=0: min={np.nanmin(d0):.4f}, max={np.nanmax(d0):.4f}")
                    print(f"    t=-1: min={np.nanmin(d_last):.4f}, max={np.nanmax(d_last):.4f}")
                elif len(v.shape) == 4:  # (time, sigma, y, x)
                    d0 = v[0, -1, :, :]  # surface, first time
                    d_last = v[-1, -1, :, :]  # surface, last time
                    print(f"    surface t=0: min={np.nanmin(d0):.4f}, max={np.nanmax(d0):.4f}")
                    print(f"    surface t=-1: min={np.nanmin(d_last):.4f}, max={np.nanmax(d_last):.4f}")
                break
