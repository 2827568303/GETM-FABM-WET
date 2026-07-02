"""Force-patch numrecs for Theoretical Lake NetCDF3 output files.

The netCDF4 library cannot read time records when numrecs=0, so we
force-write the correct record count (730 = 365 days * 2 saves/day)
to the 4-byte header field at offset 4.
"""
import struct
import os
import netCDF4 as nc
import numpy as np

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")

# Simulation: 365 days (Jan 1 00:00 to Dec 31 00:00), 30-sec timestep
# step_2d = step_3d = 1440 (12 hours), first_2d = first_3d = 1
# Number of saves = floor((1051200 - 1) / 1440) + 1 = 730
NUM_RECS = 730

for fname in ['THEORETICAL_LAKE.2d.nc', 'THEORETICAL_LAKE.3d.nc']:
    path = os.path.join(CASE_DIR, fname)
    if not os.path.exists(path):
        print(f"Skipping {fname}: not found")
        continue

    print(f"\n{'='*60}")
    print(f"Repairing: {fname}")
    print(f"{'='*60}")
    file_size = os.path.getsize(path)
    print(f"  File size: {file_size:,} bytes ({file_size/1e6:.1f} MB)")

    # Read current numrecs
    with open(path, 'r+b') as f:
        f.seek(4)
        old_numrecs = struct.unpack('>I', f.read(4))[0]
        print(f"  Current numrecs: {old_numrecs}")

        # Force-write correct numrecs
        f.seek(4)
        f.write(struct.pack('>I', NUM_RECS))
        print(f"  Patched numrecs: {old_numrecs} -> {NUM_RECS}")

    # Verify by reading with netCDF4
    try:
        with nc.Dataset(path, 'r') as ds:
            print(f"  Dimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}")
            t = ds.variables['time'][:]
            print(f"  Time records: {len(t)}")
            if len(t) > 0:
                print(f"    First: {t[0]}, Last: {t[-1]}")

                # Check water level (elev)
                if 'elev' in ds.variables:
                    elev = ds.variables['elev'][:]
                    print(f"  elev: shape={elev.shape}")
                    print(f"    Initial (t=0): mean={np.nanmean(elev[0]):.4f}m, range=[{np.nanmin(elev[0]):.4f}, {np.nanmax(elev[0]):.4f}]")
                    print(f"    Mid (t={len(t)//2}):   mean={np.nanmean(elev[len(t)//2]):.4f}m, range=[{np.nanmin(elev[len(t)//2]):.4f}, {np.nanmax(elev[len(t)//2]):.4f}]")
                    print(f"    Final (t={len(t)-1}):  mean={np.nanmean(elev[-1]):.4f}m, range=[{np.nanmin(elev[-1]):.4f}, {np.nanmax(elev[-1]):.4f}]")
                    print(f"    Net change: {np.nanmean(elev[-1]) - np.nanmean(elev[0]):.4f}m")
                    print(f"    Max fluctuation: [{np.nanmin(np.nanmean(elev, axis=(1,2))):.4f}, {np.nanmax(np.nanmean(elev, axis=(1,2))):.4f}]")

                # Check temperature
                if 'temp' in ds.variables:
                    temp = ds.variables['temp'][:]
                    print(f"  temp: shape={temp.shape}")
                    # Surface layer (last sigma index)
                    if temp.ndim == 4:
                        surf = temp[:, -1, :, :]
                        print(f"    Surface temp: range=[{np.nanmin(surf):.2f}, {np.nanmax(surf):.2f}]°C")
                        print(f"    Initial: {np.nanmean(surf[0]):.2f}°C, Final: {np.nanmean(surf[-1]):.2f}°C")
    except Exception as e:
        print(f"  ERROR reading patched file: {e}")
        print(f"  Trying with different numrecs...")

        # If 730 doesn't work, try other values
        for try_recs in [731, 729, 732]:
            with open(path, 'r+b') as f:
                f.seek(4)
                f.write(struct.pack('>I', try_recs))
            try:
                with nc.Dataset(path, 'r') as ds:
                    t = ds.variables['time'][:]
                    if len(t) == try_recs and not np.isnan(t).any():
                        print(f"  Success with numrecs={try_recs}")
                        break
            except:
                continue
