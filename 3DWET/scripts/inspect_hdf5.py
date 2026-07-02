"""Check and repair NetCDF4 files that were not properly closed.

When GETM crashes/exits without calling nf90_close(), the unlimited 'time'
dimension metadata may not be updated, even though the actual data was written
to the HDF5 file. This script inspects the raw HDF5 structure and attempts
to repair the time dimension.
"""
import h5py
import netCDF4 as nc
import numpy as np
import os
import sys

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        print(f"\n{fname}: NOT FOUND")
        continue

    print(f"\n{'='*60}")
    print(f"Inspecting: {fname}")
    print(f"{'='*60}")

    # Open with h5py to see raw HDF5 structure
    with h5py.File(path, 'r') as h:
        # Check time variable
        if 'time' in h:
            time_data = h['time'][:]
            print(f"  HDF5 'time' dataset: shape={time_data.shape}, dtype={time_data.dtype}")
            if len(time_data) > 0:
                print(f"    values: {time_data[:5]}...{time_data[-3:]}")
        else:
            print(f"  HDF5 'time' dataset: NOT FOUND")

        # Check a data variable to see actual time dimension
        test_vars = ['elev', 'temp', 'uu', 'abiotic_water_sNH4W']
        for vname in test_vars:
            if vname in h:
                v = h[vname]
                print(f"  HDF5 '{vname}': shape={v.shape}, dtype={v.dtype}")
                if len(v.shape) >= 3 and v.shape[0] > 0:
                    data = v[0:1, 0:1, 0:2, 0:2] if len(v.shape) == 4 else v[0:1, 0:2, 0:2]
                    print(f"    sample (first 2x2): {np.array(data).ravel()[:4]}")
                break

    # Check with netCDF4
    with nc.Dataset(path, 'r') as ds:
        print(f"  NetCDF time dim len: {len(ds.dimensions.get('time', type('',(),{'__len__':lambda s:0})()))}")
        tvar = ds.variables.get('time')
        if tvar is not None:
            print(f"  NetCDF time var shape: {tvar.shape}")
