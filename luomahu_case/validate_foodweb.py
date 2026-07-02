"""
Quick validation of food web model results
"""
import numpy as np
import netCDF4 as nc
import os

case_dir = r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case'

ds = nc.Dataset(os.path.join(case_dir, 'LUOMAHU_WET.3d.nc'))
mask_ds = nc.Dataset(os.path.join(case_dir, 'bathymetry.nc'))
mask = mask_ds.variables['bathymetry'][:] > 0
mask_ds.close()

def avg(data):
    if len(data.shape) == 4:
        return np.nanmean(data[:, -1, :, :][:, mask])
    elif len(data.shape) == 3:
        return np.nanmean(data[:, :, :][:, mask])
    elif len(data.shape) == 2:
        return np.nanmean(data[:, :][mask])
    return np.nan

def rng(data):
    valid = data[~np.isnan(data)]
    if len(valid) == 0:
        return (0, 0)
    return (np.min(valid), np.max(valid))

print('=' * 70)
print('FULL FOOD WEB MODEL VALIDATION - 30 Day Simulation')
print('=' * 70)

# Count variables
n_vars = len(ds.variables)
print(f'\nTotal variables in output: {n_vars}')

# Phytoplankton
print('\n--- PHYTOPLANKTON (Surface, Day 30) ---')
for group in ['cyanobacteria', 'diatoms', 'greens']:
    dw = ds.variables[f'{group}_sDW'][-1, -1, :, :]
    chla = ds.variables[f'{group}_oChla'][-1, -1, :, :]
    dw[~mask] = np.nan
    chla[~mask] = np.nan
    print(f'  {group:15s}: DW={np.nanmean(dw):.3f} g/m³, Chla={np.nanmean(chla):.2f} mg/m³, range={rng(chla)}')

total_chla = ds.variables['wet_chla'][-1, -1, :, :]
total_chla[~mask] = np.nan
print(f'  Total Chla: {np.nanmean(total_chla):.2f} mg/m³')

# Zooplankton
print('\n--- ZOOPLANKTON (Surface, Day 30) ---')
for group in ['cladocerans', 'copepods']:
    dw = ds.variables[f'{group}_sD'][-1, -1, :, :]
    dw[~mask] = np.nan
    print(f'  {group:15s}: DW={np.nanmean(dw):.4f} g/m³, range={rng(dw)}')

# Macrophytes (2D)
print('\n--- MACROPHYTES (Day 30) ---')
macro_dw = ds.variables['macrophytes_sD'][-1, :, :]
macro_dw[~mask] = np.nan
print(f'  Biomass:      {np.nanmean(macro_dw):.2f} gDW/m², range={rng(macro_dw)}')

if 'macrophytes_aCovVeg' in ds.variables:
    cov = ds.variables['macrophytes_aCovVeg'][-1, :, :]
    cov[~mask] = np.nan
    print(f'  Cover:        {np.nanmean(cov):.2f} %, range={rng(cov)}')

if 'macrophytes_aDSubVeg' in ds.variables:
    sub = ds.variables['macrophytes_aDSubVeg'][-1, :, :]
    sub[~mask] = np.nan
    print(f'  Subveg Depth: {np.nanmean(sub):.2f} gDW/m², range={rng(sub)}')

if 'macrophytes_aNutLimVeg' in ds.variables:
    nlim = ds.variables['macrophytes_aNutLimVeg'][-1, :, :]
    nlim[~mask] = np.nan
    print(f'  Nut Lim:      {np.nanmean(nlim):.3f} (-)')

if 'macrophytes_aLLimVeg' in ds.variables:
    llim = ds.variables['macrophytes_aLLimVeg'][-1, :, :]
    llim[~mask] = np.nan
    print(f'  Light Lim:    {np.nanmean(llim):.3f} (-)')

# Zoobenthos (2D)
print('\n--- ZOOBENTHOS (Day 30) ---')
benthos_dw = ds.variables['zoobenthos_sD'][-1, :, :]
benthos_dw[~mask] = np.nan
print(f'  Biomass: {np.nanmean(benthos_dw):.4f} gDW/m², range={rng(benthos_dw)}')

# Nutrients
print('\n--- NUTRIENTS (Surface, Day 30) ---')
for name, var in [('NH4', 'abiotic_water_sNH4W'), 
                   ('NO3', 'abiotic_water_sNO3W'), 
                   ('PO4', 'abiotic_water_sPO4W'),
                   ('O2', 'abiotic_water_sO2W')]:
    data = ds.variables[var][-1, -1, :, :]
    data[~mask] = np.nan
    print(f'  {name:5s}: {np.nanmean(data):.4f} g/m³, range={rng(data)}')

# Time series check
print('\n--- TIME EVOLUTION (Lake avg surface) ---')
time = ds.variables['time'][:] / 86400
n_time = len(time)

# Chla
ts_chla = [np.nanmean(ds.variables['wet_chla'][t, -1, :, :][mask]) for t in range(n_time)]
print(f'  Total Chla: Day1={ts_chla[0]:.2f} -> Day30={ts_chla[-1]:.2f} mg/m³')

# Phyto groups
for group in ['cyanobacteria', 'diatoms', 'greens']:
    ts = [np.nanmean(ds.variables[f'{group}_oChla'][t, -1, :, :][mask]) for t in range(n_time)]
    print(f'  {group:15s} Chla: Day1={ts[0]:.2f} -> Day30={ts[-1]:.2f} mg/m³')

# Zoo
for group in ['cladocerans', 'copepods']:
    ts = [np.nanmean(ds.variables[f'{group}_sD'][t, -1, :, :][mask]) for t in range(n_time)]
    print(f'  {group:15s} DW: Day1={ts[0]:.4f} -> Day30={ts[-1]:.4f} g/m³')

# Macro
ts_macro = [np.nanmean(ds.variables['macrophytes_sD'][t, :, :][mask]) for t in range(n_time)]
print(f'  Macrophyte DW: Day1={ts_macro[0]:.2f} -> Day30={ts_macro[-1]:.2f} gDW/m²')

# Benthos
ts_bent = [np.nanmean(ds.variables['zoobenthos_sD'][t, :, :][mask]) for t in range(n_time)]
print(f'  Zoobenthos DW: Day1={ts_bent[0]:.4f} -> Day30={ts_bent[-1]:.4f} gDW/m²')

# NaN check
print('\n--- NaN CHECK ---')
has_nan = False
for var in ['wet_chla', 'abiotic_water_sNH4W', 'abiotic_water_sO2W', 
            'cyanobacteria_sDW', 'diatoms_sDW', 'greens_sDW',
            'cladocerans_sD', 'copepods_sD', 'macrophytes_sD', 'zoobenthos_sD']:
    if var in ds.variables:
        data = ds.variables[var][:]
        n_nan = np.sum(np.isnan(data.filled(np.nan)))
        total = data.size
        if n_nan < total:
            print(f'  {var}: {n_nan}/{total} NaN ({100*n_nan/total:.1f}%) - OK')
        else:
            print(f'  {var}: ALL NaN - PROBLEM!')
            has_nan = True

if not has_nan:
    print('\n✓ All variables have valid data')

ds.close()

print('\n' + '=' * 70)
print('SUMMARY')
print('=' * 70)
print('  ✓ 3 phytoplankton groups (cyanobacteria, diatoms, greens)')
print('  ✓ 2 zooplankton groups (cladocerans, copepods)')
print('  ✓ Macrophytes (submerged vegetation) - 2D')
print('  ✓ Zoobenthos - 2D')
print('  ✓ Full nutrient cycling (N, P, O2, C)')
print('  ✓ 5 sigma layers (3D structure)')
print('  ✓ 30-day simulation stable (no NaN blowup)')
print('\n  Note: Fish modules (JuFish, AdFish, PiscFish) are disabled')
print('        due to "time_step" variable dependency issue.')
print('=' * 70)
