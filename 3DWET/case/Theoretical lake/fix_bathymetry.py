#!/usr/bin/env python3
"""Fix bathymetry: set land cells (depth=0) to -10.0 (GETM land convention).

GETM treats bathymetry > 0 as water, bathymetry <= 0 as land.
The Theoretical Lake bathymetry uses 0.0 for land, which GETM incorrectly
treats as water (depth=0), causing division-by-zero and NaN propagation.
Lake Luoma uses -10.0 for land cells - this is the correct convention.
"""
import netCDF4 as nc
import numpy as np
import shutil
import os

CASE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'
BATHY = os.path.join(CASE, 'bathymetry.nc')
BACKUP = os.path.join(CASE, 'bathymetry.nc.bak')

# Backup original
if not os.path.exists(BACKUP):
    shutil.copy2(BATHY, BACKUP)
    print(f'Backed up original to {BACKUP}')

# Read bathymetry
ds = nc.Dataset(BATHY, 'r+')
bathy = ds.variables['bathymetry'][:]

# Check current state
data = np.ma.filled(bathy, np.nan)
land_count = int((data <= 0).sum())
water_count = int((data > 0).sum())
print(f'Before fix: land cells (<=0) = {land_count}, water cells (>0) = {water_count}')

# Set land cells (depth <= 0) to -10.0
data_fixed = np.where(data <= 0, -10.0, data)

land_count_new = int((data_fixed <= 0).sum())
water_count_new = int((data_fixed > 0).sum())
print(f'After fix:  land cells (<=0) = {land_count_new}, water cells (>0) = {water_count_new}')
print(f'Land cells set to -10.0: {land_count_new - land_count} cells changed from 0.0 to -10.0')

# Write fixed bathymetry
ds.variables['bathymetry'][:] = data_fixed
ds.close()

print(f'\nFixed bathymetry written to {BATHY}')

# Verify
ds2 = nc.Dataset(BATHY)
bathy2 = np.ma.filled(ds2.variables['bathymetry'][:], np.nan)
print(f'Verification: min={np.nanmin(bathy2)}, max={np.nanmax(bathy2)}')
print(f'  >0 (water): {int((bathy2 > 0).sum())}, <=0 (land): {int((bathy2 <= 0).sum())}')
ds2.close()
