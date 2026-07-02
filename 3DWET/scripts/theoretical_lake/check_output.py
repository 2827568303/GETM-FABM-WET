"""Comprehensive check of Theoretical Lake model output including FABM."""
import netCDF4 as nc
import numpy as np
import os
import struct

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_GETM_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
CASE_DIR = os.path.join(_GETM_ROOT, "case", "Theoretical lake")

# First, patch numrecs for output.nc if needed
output_path = os.path.join(CASE_DIR, "output.nc")
if os.path.exists(output_path):
    with open(output_path, 'r+b') as f:
        magic = f.read(4)
        if magic == b'CDF\x01':  # NetCDF3 Classic
            f.seek(4)
            numrecs = struct.unpack('>I', f.read(4))[0]
            if numrecs == 0:
                # Determine correct numrecs: 365 days * 1 save/day = 365
                # output.yaml has time_step: 1 (day)
                correct = 365
                f.seek(4)
                f.write(struct.pack('>I', correct))
                print(f"Patched output.nc numrecs: 0 -> {correct}")

# Now check all files
files_to_check = [
    ("THEORETICAL_LAKE.2d.nc", "2D Hydrodynamic"),
    ("THEORETICAL_LAKE.3d.nc", "3D Hydrodynamic"),
    ("output.nc", "FABM Biogeochemical"),
]

for fname, label in files_to_check:
    fpath = os.path.join(CASE_DIR, fname)
    print(f"\n{'='*70}")
    print(f"{label}: {fname}")
    print(f"{'='*70}")
    if not os.path.exists(fpath):
        print(f"  FILE NOT FOUND")
        continue

    ds = nc.Dataset(fpath)
    print(f"  Format: {ds.data_model}")
    print(f"  Dimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}")
    print(f"  Variables: {len(ds.variables)}")

    if "time" in ds.variables:
        time = ds.variables["time"][:]
        n_time = len(time)
        print(f"  Time records: {n_time}")
    else:
        n_time = 0
        print(f"  No time variable!")

    # Key variables check
    if "2d" in fname or "3d" in fname:
        # Hydrodynamic variables
        if "elev" in ds.variables and n_time > 0:
            elev = ds.variables["elev"][:]
            elev_mean = np.nanmean(elev, axis=(1, 2)) if elev.ndim > 1 else elev
            print(f"\n  Water Level (elev):")
            print(f"    shape: {elev.shape}")
            print(f"    Initial: {elev_mean[0]:.4f}m")
            print(f"    Mid:     {elev_mean[n_time // 2]:.4f}m")
            print(f"    Final:   {elev_mean[-1]:.4f}m")
            print(f"    Net change: {elev_mean[-1] - elev_mean[0]:.4f}m")
            print(f"    Range: [{elev_mean.min():.4f}, {elev_mean.max():.4f}]m")
            print(f"    Std:   {elev_mean.std():.4f}m")

        if "temp" in ds.variables and n_time > 0:
            temp = ds.variables["temp"][:]
            if temp.ndim == 4:
                surf = temp[:, -1, :, :]  # surface layer
                bott = temp[:, 0, :, :]   # bottom layer
                surf_mean = np.nanmean(surf, axis=(1, 2))
                bott_mean = np.nanmean(bott, axis=(1, 2))
                print(f"\n  Temperature:")
                print(f"    shape: {temp.shape}")
                print(f"    Surface range: [{np.nanmin(surf):.2f}, {np.nanmax(surf):.2f}]°C")
                print(f"    Bottom range:  [{np.nanmin(bott):.2f}, {np.nanmax(bott):.2f}]°C")
                print(f"    Initial (surf): {surf_mean[0]:.2f}°C, Final (surf): {surf_mean[-1]:.2f}°C")
                print(f"    Max stratification: {np.nanmax(surf_mean - bott_mean):.2f}°C")

    elif "output" in fname:
        # FABM biogeochemical variables
        # Find key biogeochemical variables
        bio_vars = {}
        for vname in ds.variables:
            vname_lower = vname.lower()
            if any(k in vname_lower for k in ["nh4", "no3", "po4", "o2", "chla", "silica", "sio2"]):
                if vname not in bio_vars:
                    bio_vars[vname] = vname

        # Also check for specific WET variables
        wet_vars = {}
        for vname in ds.variables:
            for prefix in ["cyanobacteria", "diatoms", "greens", "cladocerans", "copepods",
                           "macrophytes", "zoobenthos", "JuFish", "AdFish", "PiscFish",
                           "POM_s", "DOM_s", "abiotic_water_s"]:
                if vname.startswith(prefix) and "_s" in vname and "sms" not in vname_lower and "sfl" not in vname_lower and "bfl" not in vname_lower:
                    # Only state variables (not diagnostic)
                    if vname not in wet_vars:
                        wet_vars[vname] = vname
                    break

        print(f"\n  Key biogeochemical variables ({len(bio_vars)}):")
        for vname in sorted(bio_vars.keys())[:10]:
            var = ds.variables[vname]
            if n_time > 0 and var.ndim >= 2:
                data = var[:]
                if data.size > 0:
                    has_nan = np.isnan(data).any()
                    if has_nan:
                        print(f"    {vname}: NaN={np.isnan(data).sum()}/{data.size}, range=[{np.nanmin(data):.4f}, {np.nanmax(data):.4f}]")
                    else:
                        print(f"    {vname}: range=[{data.min():.4f}, {data.max():.4f}], shape={data.shape}")

        print(f"\n  WET state variables ({len(wet_vars)}):")
        for vname in sorted(wet_vars.keys())[:20]:
            var = ds.variables[vname]
            if n_time > 0 and var.ndim >= 2:
                data = var[:]
                if data.size > 0:
                    has_nan = np.isnan(data).any()
                    if has_nan:
                        nan_frac = np.isnan(data).sum() / data.size
                        print(f"    {vname}: NaN={nan_frac*100:.1f}%, valid=[{np.nanmin(data):.6f}, {np.nanmax(data):.6f}]")
                    else:
                        print(f"    {vname}: range=[{data.min():.6f}, {data.max():.6f}], shape={data.shape}")

    ds.close()

# Summary
print(f"\n{'='*70}")
print("STABILITY SUMMARY")
print(f"{'='*70}")
fpath = os.path.join(CASE_DIR, "THEORETICAL_LAKE.2d.nc")
if os.path.exists(fpath):
    ds = nc.Dataset(fpath)
    if "elev" in ds.variables:
        elev = ds.variables["elev"][:]
        elev_mean = np.nanmean(elev, axis=(1, 2))
        print(f"  Water level net change: {elev_mean[-1] - elev_mean[0]:.4f}m (target: ~0)")
        print(f"  Water level max range:  {elev_mean.max() - elev_mean.min():.4f}m")
        print(f"  Water level std:        {elev_mean.std():.4f}m")
    ds.close()
