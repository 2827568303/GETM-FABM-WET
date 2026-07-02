"""Patch numrecs and check phytoplankton results."""
import struct, os
import netCDF4 as nc
import numpy as np

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
os.chdir(CASE)

# Patch numrecs with known values (730 for 2D/3D = 366 days * 2 saves/day, 365 for output.nc)
print("=== Patching numrecs ===")
NUM_RECS = {'THEORETICAL_LAKE.2d.nc': 730, 'THEORETICAL_LAKE.3d.nc': 730, 'output.nc': 365}
for fname, correct in NUM_RECS.items():
    if not os.path.exists(fname):
        continue
    with open(fname, 'r+b') as f:
        f.seek(4)
        old = struct.unpack('>I', f.read(4))[0]
        f.seek(4)
        f.write(struct.pack('>I', correct))
    print(f"  {fname}: numrecs {old} -> {correct}")

# Now verify and check results
print("\n=== Phytoplankton check ===")
with nc.Dataset('output.nc', 'r') as ds:
    t = ds.variables['time'][:]
    print(f"  time: {len(t)} records, range [{t[0]:.1f}, {t[-1]:.1f}]")
    for v in ['diatoms_sDW', 'greens_sDW', 'cyanobacteria_sDW',
              'diatoms_aLLim', 'greens_aLLim', 'cyanobacteria_aLLim']:
        if v not in ds.variables:
            print(f"  {v}: NOT FOUND")
            continue
        data = ds.variables[v][:]
        if len(data.shape) == 4:
            surf = data[:, 0, :, :]
            ts = np.nanmean(surf, axis=(1, 2))
        elif len(data.shape) == 3:
            ts = np.nanmean(data, axis=(1, 2))
        else:
            ts = data[:]
        print(f"  {v}: shape={data.shape}, range=[{np.nanmin(data):.6f}, {np.nanmax(data):.6f}]")
        if len(ts) > 20:
            print(f"    first 5: {ts[:5]}")
            print(f"    day 30-34: {ts[30:35]}")
            print(f"    day 90-94: {ts[90:95]}")
            print(f"    day 180-184: {ts[180:185]}")
            print(f"    last 5: {ts[-5:]}")

print("\n=== Temperature check ===")
with nc.Dataset('THEORETICAL_LAKE.3d.nc', 'r') as ds:
    if 'temp' in ds.variables:
        temp = ds.variables['temp'][:]
        surf_temp = np.nanmean(temp[:, 0, :, :], axis=(1, 2))
        print(f"  Surface temp: min={np.nanmin(surf_temp):.2f}, max={np.nanmax(surf_temp):.2f}")
        print(f"  First 5: {surf_temp[:5]}")
        print(f"  Summer (180-184): {surf_temp[180:185]}")
        print(f"  Last 5: {surf_temp[-5:]}")

print("\n=== Water level check ===")
with nc.Dataset('THEORETICAL_LAKE.2d.nc', 'r') as ds:
    if 'elev' in ds.variables:
        elev = ds.variables['elev'][:]
        ts = np.nanmean(elev, axis=(1, 2))
        print(f"  Net change: {ts[-1] - ts[0]:.4f}m")
        print(f"  Range: [{np.nanmin(ts):.4f}, {np.nanmax(ts):.4f}]m, std={np.nanstd(ts):.4f}m")

print("\n=== Food web check ===")
with nc.Dataset('output.nc', 'r') as ds:
    for v in ['cladocerans_sD', 'copepods_sD', 'JuFish_sD', 'AdFish_sD', 'PiscFish_sD',
              'abiotic_water_sNH4W', 'abiotic_water_sNO3W', 'abiotic_water_sPO4W']:
        if v not in ds.variables:
            print(f"  {v}: NOT FOUND")
            continue
        data = ds.variables[v][:]
        if len(data.shape) == 4:
            ts = np.nanmean(data[:, 0, :, :], axis=(1, 2))
        elif len(data.shape) == 3:
            ts = np.nanmean(data, axis=(1, 2))
        else:
            ts = data[:]
        print(f"  {v}: [{np.nanmin(data):.6f}, {np.nanmax(data):.6f}], first={ts[0]:.6f}, last={ts[-1]:.6f}")

print("\nDone!")
