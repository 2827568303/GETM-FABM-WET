"""Deep analysis of Theoretical Lake model results -合理性诊断.

Extracts key statistics for all major variables to diagnose whether
unreasonable results stem from code, equations, model structure, or input data.
"""
import numpy as np
import netCDF4 as nc
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GETM_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CASE_DIR = os.path.join(GETM_ROOT, "case", "Theoretical lake")

def to_np(data):
    return np.ma.filled(data, np.nan)

def safe_stat(data, label):
    """Print statistics for a data array."""
    valid = data[~np.isnan(data)]
    if len(valid) == 0:
        print(f"  {label}: ALL NaN!")
        return
    print(f"  {label}: n={len(valid)}, min={valid.min():.6f}, max={valid.max():.6f}, "
          f"mean={valid.mean():.6f}, median={np.median(valid):.6f}, std={valid.std():.6f}")

def seasonal_stats(data_3d_t, time_days, label):
    """Print seasonal statistics for a time series (spatial mean already computed)."""
    valid_mask = ~np.isnan(data_3d_t)
    if valid_mask.sum() == 0:
        print(f"  {label}: ALL NaN!")
        return
    # Split into seasons
    seasons = {
        "Spring (Mar-May, day 60-150)": (60, 150),
        "Summer (Jun-Aug, day 150-240)": (150, 240),
        "Autumn (Sep-Nov, day 240-330)": (240, 330),
        "Winter (Dec-Feb, day 330-366+0-60)": None,
    }
    print(f"  {label} seasonal means:")
    for sname, drange in seasons.items():
        if drange is None:
            idx = (time_days >= 330) | (time_days < 60)
        else:
            idx = (time_days >= drange[0]) & (time_days < drange[1])
        if idx.sum() > 0:
            vals = data_3d_t[idx]
            vals = vals[~np.isnan(vals)]
            if len(vals) > 0:
                print(f"    {sname}: mean={vals.mean():.6f}, min={vals.min():.6f}, max={vals.max():.6f}")
            else:
                print(f"    {sname}: all NaN")
        else:
            print(f"    {sname}: no data")

print("=" * 70)
print("THEORETICAL LAKE - DEEP ANALYSIS OF MODEL RESULTS")
print("=" * 70)

# ============================================================
# 1. Load data
# ============================================================
ds2d = nc.Dataset(os.path.join(CASE_DIR, "THEORETICAL_LAKE.2d.nc"))
ds3d = nc.Dataset(os.path.join(CASE_DIR, "THEORETICAL_LAKE.3d.nc"))
dsout = nc.Dataset(os.path.join(CASE_DIR, "output.nc"))
bathy_ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))

time2d = to_np(ds2d.variables['time'][:]) / 86400.0
time3d = to_np(ds3d.variables['time'][:]) / 86400.0
timeout = to_np(dsout.variables['time'][:]) / 86400.0
sigma3d = to_np(ds3d.variables['sigma'][:])
bathymetry = to_np(bathy_ds.variables['bathymetry'][:])

# Filter valid time records (handle numrecs patch artifacts)
def filter_valid_time(time_arr, data_arr):
    """Keep only records with strictly increasing time > 0."""
    valid_idx = []
    prev = -np.inf
    for i, t in enumerate(time_arr):
        if t > prev and t > 0:
            valid_idx.append(i)
            prev = t
    return np.array(valid_idx)

idx2d = filter_valid_time(time2d, None)
idx3d = filter_valid_time(time3d, None)
idxout = filter_valid_time(timeout, None)

time2d = time2d[idx2d]
time3d = time3d[idx3d]
timeout = timeout[idxout]

print(f"\nValid records: 2D={len(time2d)}, 3D={len(time3d)}, output={len(timeout)}")
print(f"Time ranges: 2D [{time2d[0]:.1f}, {time2d[-1]:.1f}], "
      f"3D [{time3d[0]:.1f}, {time3d[-1]:.1f}], "
      f"out [{timeout[0]:.1f}, {timeout[-1]:.1f}] days")
print(f"Sigma (3d): {sigma3d}")
print(f"Bathymetry: avg={np.nanmean(bathymetry):.2f}m, min={np.nanmin(bathymetry):.2f}m, max={np.nanmax(bathymetry):.2f}m")
print(f"Grid: {bathymetry.shape[1]}x{bathymetry.shape[0]} (x×y)")

# Sigma indices
idx_surf = np.argmin(np.abs(sigma3d - 0.0))
idx_bot = np.argmin(np.abs(sigma3d - (-1.0)))
# Fallback: if bottom layer is all NaN, use second-to-last
print(f"Surface sigma idx={idx_surf} (sigma={sigma3d[idx_surf]}), Bottom sigma idx={idx_bot} (sigma={sigma3d[idx_bot]})")

# Check which sigma layers have valid temp data
temp_check = to_np(ds3d.variables['temp'][:])
for k in range(len(sigma3d)):
    n_valid = np.sum(~np.isnan(temp_check[:, k, :, :]))
    if n_valid > 0:
        print(f"  sigma[{k}]={sigma3d[k]:.1f}: {n_valid} valid values")
# Use the deepest layer that has data
for k_test in [idx_bot, idx_bot - 1 if idx_bot > 0 else 0, idx_bot - 2 if idx_bot > 1 else 0]:
    if k_test >= 0 and np.sum(~np.isnan(temp_check[:, k_test, :, :])) > 0:
        idx_bot = k_test
        print(f"  Using bottom sigma idx={idx_bot} (sigma={sigma3d[idx_bot]})")
        break

# ============================================================
# 2. HYDRODYNAMICS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: HYDRODYNAMICS")
print("=" * 70)

# Water level
elev = to_np(ds2d.variables['elev'][:])[idx2d]
elev_mean = np.nanmean(elev, axis=(1, 2))
print("\n--- Water Level (elev) ---")
safe_stat(elev_mean, "Overall")
print(f"  Initial (t=0): {elev_mean[0]:.4f}m")
print(f"  Final:         {elev_mean[-1]:.4f}m")
print(f"  Net change:    {elev_mean[-1] - elev_mean[0]:.4f}m")
print(f"  Range:         [{elev_mean.min():.4f}, {elev_mean.max():.4f}]m")
print(f"  Std:           {elev_mean.std():.4f}m")
# Check for drift
n = len(elev_mean)
q1 = elev_mean[:n//4].mean()
q4 = elev_mean[3*n//4:].mean()
print(f"  Q1 mean: {q1:.4f}m, Q4 mean: {q4:.4f}m, drift: {q4-q1:.4f}m")

# Temperature
temp = to_np(ds3d.variables['temp'][:])[idx3d]
temp_surf = np.nanmean(temp[:, idx_surf, :, :], axis=(1, 2))
temp_bot = np.nanmean(temp[:, idx_bot, :, :], axis=(1, 2))
temp_diff = temp_surf - temp_bot
print("\n--- Temperature ---")
safe_stat(temp_surf, "Surface")
safe_stat(temp_bot, "Bottom")
print(f"  Surface: initial={temp_surf[0]:.2f}°C, final={temp_surf[-1]:.2f}°C")
print(f"  Max surface temp: {np.nanmax(temp_surf):.2f}°C at day {time3d[np.nanargmax(temp_surf)]:.0f}")
print(f"  Min surface temp: {np.nanmin(temp_surf):.2f}°C at day {time3d[np.nanargmin(temp_surf)]:.0f}")
print(f"  Max stratification (surf-bot): {np.nanmax(temp_diff):.2f}°C")
print(f"  Mean stratification: {np.nanmean(temp_diff):.3f}°C")
# Check if temperature follows seasonal pattern
summer_idx = (time3d >= 150) & (time3d <= 240)
winter_idx = (time3d >= 330) | (time3d <= 60)
print(f"  Summer mean (surf): {temp_surf[summer_idx].mean():.2f}°C")
print(f"  Winter mean (surf): {temp_surf[winter_idx].mean():.2f}°C")

# Velocity
if 'uu' in ds3d.variables:
    uu = to_np(ds3d.variables['uu'][:])[idx3d]
    vv = to_np(ds3d.variables['vv'][:])[idx3d]
    speed = np.sqrt(uu**2 + vv**2)
    print("\n--- Velocity ---")
    safe_stat(speed, "Speed (3D)")
    print(f"  Max speed: {np.nanmax(speed):.4f} m/s")
    print(f"  Mean speed: {np.nanmean(speed):.4f} m/s")

# ============================================================
# 3. WATER QUALITY (Nutrients & Oxygen)
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: WATER QUALITY (Nutrients & Oxygen)")
print("=" * 70)

nutrient_vars = {
    'abiotic_water_sNH4W': 'NH4 (gN/m3)',
    'abiotic_water_sNO3W': 'NO3 (gN/m3)',
    'abiotic_water_sPO4W': 'PO4 (gP/m3)',
    'abiotic_water_sO2W': 'O2 (g/m3)',
    'abiotic_water_sSiO2W': 'SiO2 (g/m3)',
}

for vname, label in nutrient_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        # Surface layer
        surf = np.nanmean(data[:, -1, :, :], axis=(1, 2))  # last sigma = surface
        bot = np.nanmean(data[:, 0, :, :], axis=(1, 2))    # first sigma = bottom
        print(f"\n--- {label} ({vname}) ---")
        safe_stat(surf, "Surface (spatial mean)")
        print(f"  Initial: {surf[0]:.6f}, Final: {surf[-1]:.6f}")
        seasonal_stats(surf, timeout, "Surface")
        # Check vertical gradient
        grad = surf - bot
        print(f"  Surface-Bottom diff: mean={np.nanmean(grad):.6f}, max={np.nanmax(grad):.6f}")

# ============================================================
# 4. PHYTOPLANKTON
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: PHYTOPLANKTON")
print("=" * 70)

phyto_vars = {
    'cyanobacteria_sDW': 'Cyanobacteria (gDW/m3)',
    'diatoms_sDW': 'Diatoms (gDW/m3)',
    'greens_sDW': 'Greens (gDW/m3)',
}

for vname, label in phyto_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        # Depth-averaged (using first 10 sigma layers from 3d file)
        sigma_out = np.sort(sigma3d)[:data.shape[1]]  # match output layers
        depth_2d = bathymetry
        nz = data.shape[1]
        dz = np.zeros((nz, depth_2d.shape[0], depth_2d.shape[1]))
        for k in range(nz):
            if k == 0:
                dz[k] = depth_2d * (sigma_out[k+1] - sigma_out[k])
            elif k == nz - 1:
                dz[k] = depth_2d * (sigma_out[k] - sigma_out[k-1])
            else:
                dz[k] = depth_2d * 0.5 * (sigma_out[k+1] - sigma_out[k-1])
        total_dz = np.nansum(dz, axis=0)
        total_dz[total_dz == 0] = np.nan
        depth_avg = np.nansum(data * dz[np.newaxis, :, :, :], axis=1) / total_dz[np.newaxis, :, :]
        ts = np.nanmean(depth_avg, axis=(1, 2))

        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Depth-avg spatial mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        print(f"  Peak: {np.nanmax(ts):.6f} at day {timeout[np.nanargmax(ts)]:.0f}")
        seasonal_stats(ts, timeout, "Depth-avg")

        # Check spatial distribution
        spatial_t180 = depth_avg[min(180, len(timeout)-1)]
        print(f"  Spatial (t=180): mean={np.nanmean(spatial_t180):.6f}, "
              f"min={np.nanmin(spatial_t180):.6f}, max={np.nanmax(spatial_t180):.6f}")

# ============================================================
# 5. ZOOPLANKTON
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: ZOOPLANKTON")
print("=" * 70)

zoo_vars = {
    'cladocerans_sD': 'Cladocerans (gDW/m3)',
    'copepods_sD': 'Copepods (gDW/m3)',
}

for vname, label in zoo_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        # depth-avg
        sigma_out = np.sort(sigma3d)[:data.shape[1]]
        depth_2d = bathymetry
        nz = data.shape[1]
        dz = np.zeros((nz, depth_2d.shape[0], depth_2d.shape[1]))
        for k in range(nz):
            if k == 0:
                dz[k] = depth_2d * (sigma_out[k+1] - sigma_out[k])
            elif k == nz - 1:
                dz[k] = depth_2d * (sigma_out[k] - sigma_out[k-1])
            else:
                dz[k] = depth_2d * 0.5 * (sigma_out[k+1] - sigma_out[k-1])
        total_dz = np.nansum(dz, axis=0)
        total_dz[total_dz == 0] = np.nan
        depth_avg = np.nansum(data * dz[np.newaxis, :, :, :], axis=1) / total_dz[np.newaxis, :, :]
        ts = np.nanmean(depth_avg, axis=(1, 2))

        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Depth-avg spatial mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        print(f"  Peak: {np.nanmax(ts):.6f} at day {timeout[np.nanargmax(ts)]:.0f}")
        seasonal_stats(ts, timeout, "Depth-avg")

# ============================================================
# 6. FISH
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: FISH")
print("=" * 70)

fish_vars = {
    'JuFish_sD': 'Juvenile Fish (gDW/m3)',
    'AdFish_sD': 'Adult Fish (gDW/m3)',
    'PiscFish_sD': 'Piscivorous Fish (gDW/m3)',
}

for vname, label in fish_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        sigma_out = np.sort(sigma3d)[:data.shape[1]]
        depth_2d = bathymetry
        nz = data.shape[1]
        dz = np.zeros((nz, depth_2d.shape[0], depth_2d.shape[1]))
        for k in range(nz):
            if k == 0:
                dz[k] = depth_2d * (sigma_out[k+1] - sigma_out[k])
            elif k == nz - 1:
                dz[k] = depth_2d * (sigma_out[k] - sigma_out[k-1])
            else:
                dz[k] = depth_2d * 0.5 * (sigma_out[k+1] - sigma_out[k-1])
        total_dz = np.nansum(dz, axis=0)
        total_dz[total_dz == 0] = np.nan
        depth_avg = np.nansum(data * dz[np.newaxis, :, :, :], axis=1) / total_dz[np.newaxis, :, :]
        ts = np.nanmean(depth_avg, axis=(1, 2))

        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Depth-avg spatial mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        print(f"  Peak: {np.nanmax(ts):.6f} at day {timeout[np.nanargmax(ts)]:.0f}")
        seasonal_stats(ts, timeout, "Depth-avg")

        # Check vertical distribution
        surf_val = np.nanmean(data[:, -1, :, :])
        bot_val = np.nanmean(data[:, 0, :, :])
        print(f"  Vertical: surface mean={surf_val:.6f}, bottom mean={bot_val:.6f}, ratio={surf_val/max(bot_val,1e-10):.2f}")

# ============================================================
# 7. MACROPHYTES & BENTHOS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: MACROPHYTES & BENTHOS (2D benthic)")
print("=" * 70)

benthic_vars = {
    'macrophytes_sD': 'Macrophytes (gDW/m2)',
    'zoobenthos_sD': 'Zoobenthos (gDW/m2)',
}

# SE bay mask (0-indexed: i>=2, j>=4)
se_mask = np.zeros_like(bathymetry, dtype=bool)
se_mask[4:, 2:] = True  # j>=4, i>=2

for vname, label in benthic_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        ts_all = np.nanmean(data, axis=(1, 2))
        ts_se = np.nanmean(data[:, se_mask], axis=1) if se_mask.sum() > 0 else np.full(len(timeout), np.nan)
        ts_non_se = np.nanmean(data[:, ~se_mask], axis=1) if (~se_mask).sum() > 0 else np.full(len(timeout), np.nan)

        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts_all, "Whole lake mean")
        print(f"  Initial: {ts_all[0]:.6f}, Final: {ts_all[-1]:.6f}")
        print(f"  SE bay mean: initial={ts_se[0]:.6f}, final={ts_se[-1]:.6f}")
        print(f"  Non-SE mean: initial={ts_non_se[0]:.6f}, final={ts_non_se[-1]:.6f}")

        # Check if macrophytes spread beyond SE bay
        t180 = data[min(180, len(timeout)-1)]
        se_vals = t180[se_mask]
        non_se_vals = t180[~se_mask]
        print(f"  t=180: SE bay mean={np.nanmean(se_vals):.6f}, non-SE mean={np.nanmean(non_se_vals):.6f}")
        # Count cells with macrophytes
        nonzero_threshold = 0.001
        n_nonzero = np.sum(t180 > nonzero_threshold)
        n_nonzero_se = np.sum(t180[se_mask] > nonzero_threshold)
        n_nonzero_non_se = np.sum(t180[~se_mask] > nonzero_threshold)
        print(f"  t=180: {n_nonzero}/{bathymetry.size} cells have macrophytes "
              f"(SE: {n_nonzero_se}/{se_mask.sum()}, non-SE: {n_nonzero_non_se}/{(~se_mask).sum()})")

# ============================================================
# 8. ORGANIC MATTER
# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: ORGANIC MATTER")
print("=" * 70)

om_vars_3d = {'POM_sDW': 'POM water (gDW/m3)', 'DOM_sDW': 'DOM water (gDW/m3)'}
om_vars_2d = {'POM_sDS': 'POM sediment (gDW/m2)', 'DOM_sDS': 'DOM sediment (gDW/m2)'}

for vname, label in om_vars_3d.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        ts = np.nanmean(data, axis=(1, 2, 3))
        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        seasonal_stats(ts, timeout, "Mean")

for vname, label in om_vars_2d.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        ts = np.nanmean(data, axis=(1, 2))
        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        seasonal_stats(ts, timeout, "Mean")

# ============================================================
# 9. SEDIMENT NUTRIENTS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: SEDIMENT NUTRIENTS (2D benthic)")
print("=" * 70)

sed_vars = {
    'abiotic_sediment_sNH4S': 'Sediment NH4 (gN/m2)',
    'abiotic_sediment_sNO3S': 'Sediment NO3 (gN/m2)',
    'abiotic_sediment_sPO4S': 'Sediment PO4 (gP/m2)',
    'abiotic_sediment_sSiO2S': 'Sediment SiO2 (g/m2)',
}

for vname, label in sed_vars.items():
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        ts = np.nanmean(data, axis=(1, 2))
        print(f"\n--- {label} ({vname}) ---")
        safe_stat(ts, "Mean")
        print(f"  Initial: {ts[0]:.6f}, Final: {ts[-1]:.6f}")
        seasonal_stats(ts, timeout, "Mean")

# ============================================================
# 10. MASS BALANCE CHECK
# ============================================================
print("\n" + "=" * 70)
print("SECTION 9: MASS BALANCE & CONSERVATION CHECKS")
print("=" * 70)

# Total nitrogen in system
print("\n--- Total Nitrogen in system ---")
# Water column: NH4W + NO3W + phytoplankton N + zooplankton N + fish N + POM_NW + DOM_NW
# Simplified: just check key pools
if 'abiotic_water_sNH4W' in dsout.variables:
    nh4 = to_np(dsout.variables['abiotic_water_sNH4W'][:])[idxout]
    no3 = to_np(dsout.variables['abiotic_water_sNO3W'][:])[idxout]
    # Total inorganic N in water (depth-integrated)
    sigma_out = np.sort(sigma3d)[:nh4.shape[1]]
    depth_2d = bathymetry
    nz = nh4.shape[1]
    dz = np.zeros((nz, depth_2d.shape[0], depth_2d.shape[1]))
    for k in range(nz):
        if k == 0:
            dz[k] = depth_2d * (sigma_out[k+1] - sigma_out[k])
        elif k == nz - 1:
            dz[k] = depth_2d * (sigma_out[k] - sigma_out[k-1])
        else:
            dz[k] = depth_2d * 0.5 * (sigma_out[k+1] - sigma_out[k-1])
    total_dz = np.nansum(dz, axis=0)

    # Depth-integrated NH4+NO3 (gN/m2)
    nh4_int = np.nansum(nh4 * dz[np.newaxis, :, :, :], axis=1)
    no3_int = np.nansum(no3 * dz[np.newaxis, :, :, :], axis=1)
    din_total = (nh4_int + no3_int) * 250000  # * cell area (500*500)
    din_ts = np.nansum(din_total, axis=(1, 2))  # total in lake
    print(f"  DIN (NH4+NO3) total: initial={din_ts[0]:.1f} gN, final={din_ts[-1]:.1f} gN")
    print(f"  DIN change: {din_ts[-1]-din_ts[0]:.1f} gN ({(din_ts[-1]-din_ts[0])/max(din_ts[0],1)*100:.1f}%)")

# ============================================================
# 11. KEY DIAGNOSTIC FLAGS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 10: KEY DIAGNOSTIC FLAGS")
print("=" * 70)

flags = []

# Check 1: Water level stability
elev_net = elev_mean[-1] - elev_mean[0]
if abs(elev_net) > 0.1:
    flags.append(f"WARNING: Water level net change = {elev_net:.4f}m (target ~0)")
else:
    print(f"  OK: Water level net change = {elev_net:.4f}m")

# Check 2: Temperature seasonal pattern
if temp_surf.max() < 20 or temp_surf.max() > 35:
    flags.append(f"WARNING: Max surface temp = {temp_surf.max():.2f}°C (expected 25-32°C)")
else:
    print(f"  OK: Max surface temp = {temp_surf.max():.2f}°C")

if temp_surf.min() > 2:
    flags.append(f"WARNING: Min surface temp = {temp_surf.min():.2f}°C (expected <2°C in winter)")
else:
    print(f"  OK: Min surface temp = {temp_surf.min():.2f}°C")

# Check 3: Nutrient ranges
for vname, expected_range in [('abiotic_water_sNH4W', (0, 1.0)),
                                ('abiotic_water_sNO3W', (0, 5.0)),
                                ('abiotic_water_sPO4W', (0, 0.2)),
                                ('abiotic_water_sO2W', (0, 15.0))]:
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        dmin, dmax = np.nanmin(data), np.nanmax(data)
        if dmin < 0:
            flags.append(f"WARNING: {vname} has negative values: min={dmin:.6f}")
        if dmax > expected_range[1] * 3:
            flags.append(f"WARNING: {vname} very high: max={dmax:.6f} (expected <{expected_range[1]})")
        if dmin < expected_range[0]:
            flags.append(f"WARNING: {vname} below expected: min={dmin:.6f}")
        else:
            print(f"  OK: {vname} range [{dmin:.6f}, {dmax:.6f}]")

# Check 4: Phytoplankton seasonal pattern
for vname in ['cyanobacteria_sDW', 'diatoms_sDW', 'greens_sDW']:
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        sigma_out = np.sort(sigma3d)[:data.shape[1]]
        nz = data.shape[1]
        dz = np.zeros((nz, bathymetry.shape[0], bathymetry.shape[1]))
        for k in range(nz):
            if k == 0:
                dz[k] = bathymetry * (sigma_out[k+1] - sigma_out[k])
            elif k == nz - 1:
                dz[k] = bathymetry * (sigma_out[k] - sigma_out[k-1])
            else:
                dz[k] = bathymetry * 0.5 * (sigma_out[k+1] - sigma_out[k-1])
        total_dz = np.nansum(dz, axis=0)
        total_dz[total_dz == 0] = np.nan
        depth_avg = np.nansum(data * dz[np.newaxis, :, :, :], axis=1) / total_dz[np.newaxis, :, :]
        ts = np.nanmean(depth_avg, axis=(1, 2))

        if np.nanmax(ts) < 0.001:
            flags.append(f"WARNING: {vname} very low: max={np.nanmax(ts):.6f} gDW/m3")
        elif np.nanmax(ts) > 10:
            flags.append(f"WARNING: {vname} very high: max={np.nanmax(ts):.6f} gDW/m3")
        else:
            print(f"  OK: {vname} max={np.nanmax(ts):.6f} gDW/m3 at day {timeout[np.nanargmax(ts)]:.0f}")

        if ts[-1] / max(ts[0], 1e-10) > 100:
            flags.append(f"WARNING: {vname} grew >100x: {ts[0]:.6f} -> {ts[-1]:.6f}")
        elif ts[-1] / max(ts[0], 1e-10) < 0.01:
            flags.append(f"WARNING: {vname} collapsed to <1%: {ts[0]:.6f} -> {ts[-1]:.6f}")

# Check 5: Fish dynamics
for vname in ['JuFish_sD', 'AdFish_sD', 'PiscFish_sD']:
    if vname in dsout.variables:
        data = to_np(dsout.variables[vname][:])[idxout]
        ts = np.nanmean(data, axis=(1, 2, 3))
        if ts[-1] < ts[0] * 0.1:
            flags.append(f"WARNING: {vname} declined >90%: {ts[0]:.6f} -> {ts[-1]:.6f}")
        elif ts[-1] > ts[0] * 10:
            flags.append(f"WARNING: {vname} grew >10x: {ts[0]:.6f} -> {ts[-1]:.6f}")
        else:
            print(f"  OK: {vname} {ts[0]:.6f} -> {ts[-1]:.6f}")

# Check 6: Macrophyte confinement
if 'macrophytes_sD' in dsout.variables:
    data = to_np(dsout.variables['macrophytes_sD'][:])[idxout]
    t180 = data[min(180, len(timeout)-1)]
    non_se_max = np.nanmax(t180[~se_mask])
    se_max = np.nanmax(t180[se_mask])
    if non_se_max > se_max * 0.5:
        flags.append(f"WARNING: Macrophytes spread beyond SE bay (non-SE max={non_se_max:.4f}, SE max={se_max:.4f})")
    else:
        print(f"  OK: Macrophytes confined to SE bay (non-SE max={non_se_max:.4f}, SE max={se_max:.4f})")

# Check 7: Oxygen levels
if 'abiotic_water_sO2W' in dsout.variables:
    o2 = to_np(dsout.variables['abiotic_water_sO2W'][:])[idxout]
    o2_min = np.nanmin(o2)
    if o2_min < 0:
        flags.append(f"WARNING: O2 has negative values: min={o2_min:.6f}")
    elif o2_min < 2:
        flags.append(f"WARNING: O2 very low: min={o2_min:.6f} g/m3 (hypoxia)")
    else:
        print(f"  OK: O2 min={o2_min:.6f} g/m3")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC FLAGS SUMMARY")
print("=" * 70)
if flags:
    for f in flags:
        print(f"  {f}")
else:
    print("  No warnings - all checks passed!")

# Close datasets
ds2d.close()
ds3d.close()
dsout.close()
bathy_ds.close()

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
