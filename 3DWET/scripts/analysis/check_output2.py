#!/usr/bin/env python3
"""Check simulation output results - fixed version."""
import netCDF4 as nc
import numpy as np
import os

case_dir = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"

print("=== LUOMAHU_WET.3d.nc - Key Results ===")
ds = nc.Dataset(os.path.join(case_dir, "LUOMAHU_WET.3d.nc"), 'r')

print(f"Grid: xc={len(ds.dimensions['xc'])}, yc={len(ds.dimensions['yc'])}, sigma={len(ds.dimensions['sigma'])}, time={len(ds.dimensions['time'])}")

time_idx = -1  # last time step (day 30)
lev_surf = -1  # surface layer
lev_bot = 0    # bottom layer

cx = len(ds.dimensions['xc']) // 2
cy = len(ds.dimensions['yc']) // 2

print(f"Center point: cx={cx}, cy={cy}")
print(f"Time step {time_idx}: {ds.variables['time'][time_idx]/86400:.1f} days")

# Check for NaN and valid points
bathymetry = ds.variables['bathymetry'][:]
valid_mask = bathymetry > 0
print(f"\nValid water cells: {np.sum(valid_mask)} / {bathymetry.size}")

# List all variables
var_list = list(ds.variables.keys())
print(f"\nTotal variables: {len(var_list)}")

# Key variables to check
key_vars = [
    'temp',
    'abiotic_water_sNH4W',
    'abiotic_water_sNO3W', 
    'abiotic_water_sPO4W',
    'abiotic_water_sO2W',
    'cyanobacteria_Biomass',
    'greens_Biomass',
    'zooplankton_Biomass',
]

print("\n=== Key Variables at Center Point ===")
print(f"{'Variable':<35} {'Surface':>12} {'Bottom':>12}")
print("-" * 62)

for var in key_vars:
    if var in ds.variables:
        v = ds.variables[var]
        val_surf = v[time_idx, lev_surf, cy, cx]
        val_bot = v[time_idx, lev_bot, cy, cx]
        units = v.units if hasattr(v, 'units') else ''
        print(f"{var:<35} {val_surf:>10.4f} {val_bot:>10.4f} {units}")
    else:
        print(f"{var:<35} {'NOT FOUND':>12}")

# Check time series at surface center
print("\n=== Time Series (Surface, Center) ===")
print(f"{'Day':>6} {'Temp':>8} {'NH4':>8} {'NO3':>8} {'PO4':>8} {'O2':>8}")
print("-" * 50)

time_days = ds.variables['time'][:] / 86400.0

for t in range(0, len(time_days), max(1, len(time_days)//10)):
    temp = ds.variables['temp'][t, lev_surf, cy, cx] if 'temp' in ds.variables else float('nan')
    nh4 = ds.variables['abiotic_water_sNH4W'][t, lev_surf, cy, cx] if 'abiotic_water_sNH4W' in ds.variables else float('nan')
    no3 = ds.variables['abiotic_water_sNO3W'][t, lev_surf, cy, cx] if 'abiotic_water_sNO3W' in ds.variables else float('nan')
    po4 = ds.variables['abiotic_water_sPO4W'][t, lev_surf, cy, cx] if 'abiotic_water_sPO4W' in ds.variables else float('nan')
    o2 = ds.variables['abiotic_water_sO2W'][t, lev_surf, cy, cx] if 'abiotic_water_sO2W' in ds.variables else float('nan')
    print(f"{time_days[t]:>6.1f} {temp:>8.2f} {nh4:>8.4f} {no3:>8.4f} {po4:>8.4f} {o2:>8.2f}")

# Check for NaN values
print("\n=== NaN Check ===")
for var in ['temp', 'abiotic_water_sNH4W', 'abiotic_water_sO2W']:
    if var in ds.variables:
        data = ds.variables[var][:]
        n_nan = np.sum(np.isnan(data))
        n_total = data.size
        print(f"  {var}: {n_nan}/{n_total} NaN ({100*n_nan/n_total:.2f}%)")

ds.close()
print("\nDone.")
