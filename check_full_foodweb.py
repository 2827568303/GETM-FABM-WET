#!/usr/bin/env python3
"""Check full food web simulation output."""
import netCDF4 as nc
import numpy as np
import os

case_dir = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case"

print("=== Full Food Web - 30 Day Simulation Results ===")
ds = nc.Dataset(os.path.join(case_dir, "LUOMAHU_WET.3d.nc"), 'r')

print(f"Grid: xc={len(ds.dimensions['xc'])}, yc={len(ds.dimensions['yc'])}, sigma={len(ds.dimensions['sigma'])}, time={len(ds.dimensions['time'])}")

time_idx = -1
lev_surf = -1
lev_bot = 0

cx = len(ds.dimensions['xc']) // 2
cy = len(ds.dimensions['yc']) // 2

# Count total variables
var_list = list(ds.variables.keys())
print(f"\nTotal variables: {len(var_list)}")

# Find all food web related variables
phytos = ['cyanobacteria', 'diatoms', 'greens']
zoos = ['cladocerans', 'copepods']
benthos = ['zoobenthos']
macros = ['macrophytes']

all_groups = phytos + zoos + benthos + macros

print("\n=== Food Web Groups (Surface, Center, Day 30) ===")
print(f"{'Group':<20} {'DW (g/m3)':>12} {'N (g/m3)':>12} {'P (g/m3)':>12} {'C (g/m3)':>12}")
print("-" * 72)

for group in all_groups:
    dw_var = f"{group}_sDW"
    n_var = f"{group}_sNW"
    p_var = f"{group}_sPW"
    c_var = f"{group}_sCW"
    
    dw = ds.variables[dw_var][time_idx, lev_surf, cy, cx] if dw_var in ds.variables else float('nan')
    n = ds.variables[n_var][time_idx, lev_surf, cy, cx] if n_var in ds.variables else float('nan')
    p = ds.variables[p_var][time_idx, lev_surf, cy, cx] if p_var in ds.variables else float('nan')
    c = ds.variables[c_var][time_idx, lev_surf, cy, cx] if c_var in ds.variables else float('nan')
    
    print(f"{group:<20} {dw:>12.6f} {n:>12.6f} {p:>12.6f} {c:>12.6f}")

# Time series of key variables
print("\n=== Time Series (Surface, Center) ===")
print(f"{'Day':>6} {'Temp':>8} {'NH4':>8} {'NO3':>8} {'PO4':>8} {'O2':>8} {'Cya':>8} {'Greens':>8} {'Diatom':>8} {'Zoo':>8}")
print("-" * 90)

time_days = ds.variables['time'][:] / 86400.0

for t in range(0, len(time_days), max(1, len(time_days)//10)):
    temp = ds.variables['temp'][t, lev_surf, cy, cx] if 'temp' in ds.variables else float('nan')
    nh4 = ds.variables['abiotic_water_sNH4W'][t, lev_surf, cy, cx] if 'abiotic_water_sNH4W' in ds.variables else float('nan')
    no3 = ds.variables['abiotic_water_sNO3W'][t, lev_surf, cy, cx] if 'abiotic_water_sNO3W' in ds.variables else float('nan')
    po4 = ds.variables['abiotic_water_sPO4W'][t, lev_surf, cy, cx] if 'abiotic_water_sPO4W' in ds.variables else float('nan')
    o2 = ds.variables['abiotic_water_sO2W'][t, lev_surf, cy, cx] if 'abiotic_water_sO2W' in ds.variables else float('nan')
    cya = ds.variables['cyanobacteria_sDW'][t, lev_surf, cy, cx] if 'cyanobacteria_sDW' in ds.variables else float('nan')
    gre = ds.variables['greens_sDW'][t, lev_surf, cy, cx] if 'greens_sDW' in ds.variables else float('nan')
    dia = ds.variables['diatoms_sDW'][t, lev_surf, cy, cx] if 'diatoms_sDW' in ds.variables else float('nan')
    
    # Zooplankton - sum cladocerans + copepods
    zoo = 0
    if 'cladocerans_sDW' in ds.variables:
        zoo += ds.variables['cladocerans_sDW'][t, lev_surf, cy, cx]
    if 'copepods_sDW' in ds.variables:
        zoo += ds.variables['copepods_sDW'][t, lev_surf, cy, cx]
    
    print(f"{time_days[t]:>6.1f} {temp:>8.2f} {nh4:>8.4f} {no3:>8.4f} {po4:>8.4f} {o2:>8.2f} {cya:>8.4f} {gre:>8.4f} {dia:>8.4f} {zoo:>8.4f}")

# Macrophytes and zoobenthos (likely 2D or bottom variables)
print("\n=== Benthic / Macrophytes (Center Point) ===")
for var_name in ['macrophytes_sDW', 'zoobenthos_sDW']:
    if var_name in ds.variables:
        v = ds.variables[var_name]
        print(f"  {var_name}: shape={v.shape}")
        if len(v.shape) == 3:  # time, y, x
            print(f"    Day 1:  {v[0, cy, cx]:.6f}")
            print(f"    Day 30: {v[-1, cy, cx]:.6f}")
        elif len(v.shape) == 4:  # time, sigma, y, x
            print(f"    Day 1 bottom:  {v[0, 0, cy, cx]:.6f}")
            print(f"    Day 30 bottom: {v[-1, 0, cy, cx]:.6f}")

# Check for NaN values in key variables
print("\n=== NaN Check ===")
key_vars = ['temp', 'abiotic_water_sNH4W', 'abiotic_water_sO2W', 
            'cyanobacteria_sDW', 'diatoms_sDW', 'greens_sDW',
            'cladocerans_sDW', 'copepods_sDW']
for var in key_vars:
    if var in ds.variables:
        data = ds.variables[var][:]
        n_nan = np.sum(np.isnan(data))
        n_total = data.size
        if n_nan > 0:
            print(f"  {var}: {n_nan}/{n_total} NaN ({100*n_nan/n_total:.2f}%)")
        else:
            print(f"  {var}: OK (no NaN)")

ds.close()
print("\nDone.")
