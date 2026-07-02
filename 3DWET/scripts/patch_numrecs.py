"""Patch numrecs to correct value for all NetCDF3 output files.

Reads the time dimension from each file and patches the 4-byte header
at offset 4 with the correct record count.
"""
import struct
import os
import netCDF4 as nc
import numpy as np

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

for fname in ['LUOMAHU_WET.2d.nc', 'LUOMAHU_WET.3d.nc', 'output.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        continue

    print(f"\nRepairing: {fname}")
    # Read time dimension to determine correct numrecs
    with nc.Dataset(path, 'r') as ds:
        t = ds.variables['time'][:]
        correct_numrecs = len(t)
        print(f"  time dim len: {correct_numrecs}")
        print(f"  time values: first={t[0]}, last={t[-1]}")

    with open(path, 'r+b') as f:
        f.seek(4)
        old = struct.unpack('>I', f.read(4))[0]
        f.seek(4)
        f.write(struct.pack('>I', correct_numrecs))
        print(f"  numrecs: {old} -> {correct_numrecs}")

    # Verify
    with nc.Dataset(path, 'r') as ds:
        t = ds.variables['time'][:]
        print(f"  time dim len: {len(t)}")
        print(f"  time values: {t}")
        # Check data validity
        for vname in ['elev', 'temp', 'uu']:
            if vname in ds.variables:
                v = ds.variables[vname]
                if len(v.shape) == 3:
                    d_last = v[-1, :, :]
                    print(f"  {vname} last step: min={np.nanmin(d_last):.4f}, max={np.nanmax(d_last):.4f}")
                elif len(v.shape) == 4:
                    d_last = v[-1, -1, :, :]
                    print(f"  {vname} surface last step: min={np.nanmin(d_last):.4f}, max={np.nanmax(d_last):.4f}")
                break
