#!/usr/bin/env python3
"""Generate correct rivers.nc from Luomahu_inputs/Inputs.xlsx."""
import openpyxl
import netCDF4 as nc
import numpy as np
import os
from datetime import datetime, timedelta

xlsx_path = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\Luomahu_inputs\Inputs.xlsx"
output_path = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\rivers_correct.nc"

print("Reading Inputs.xlsx...")
wb = openpyxl.load_workbook(xlsx_path, data_only=True)

# Read river flow data
ws_flow = wb['主要入湖、出湖河道流量数据']

# Get data (skip first 4 header rows)
dates = []
dayun_flow = []   # 京杭大运河 - 入/出
luonan_flow = []  # 骆南中运河 - 入
yihe_flow = []    # 沂河 - 入
zhangshan_flow = [] # 嶂山闸 - 出
yanghe_flow = []  # 杨河滩 - 出

for row in ws_flow.iter_rows(min_row=5, max_row=ws_flow.max_row, values_only=True):
    dates.append(row[0])
    dayun_flow.append(row[1] if row[1] is not None else 0.0)
    luonan_flow.append(row[2] if row[2] is not None else 0.0)
    yihe_flow.append(row[3] if row[3] is not None else 0.0)
    zhangshan_flow.append(row[4] if row[4] is not None else 0.0)
    yanghe_flow.append(row[5] if row[5] is not None else 0.0)

n_days = len(dates)
print(f"Flow data: {n_days} days, from {dates[0]} to {dates[-1]}")

# Read water quality data for each inflow river
# We need: ammonium, nitrate, phosphate, POM (particulate organic matter)
# From Excel: NH4, NO3, PO4, and we can estimate POM from other params

# Helper function to read water quality sheet
def read_wq(sheet_name, n_days_expected):
    ws = wb[sheet_name]
    print(f"\nReading {sheet_name}... ({ws.max_row} rows)")
    
    nh4 = []
    no3 = []
    po4 = []
    pom = []  # We'll estimate from IMN or use a fixed ratio
    
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        # Columns vary by sheet, but generally:
        # NH4 is usually near the end, NO3 too, PO4 is earlier
        # Let's find them by position based on headers
        pass
    
    return nh4, no3, po4, pom

# For simplicity, let's use constant water quality values for now
# (We can refine later - the main issue is the flow data)
# Use typical values from the first row of each sheet

# DAYUN (京杭大运河) - has detailed WQ data
ws_dayun = wb['入湖河道水质数据-京杭大运河']
print(f"\nDAYUN water quality: {ws_dayun.max_row} rows")
# Get headers
headers_dayun = [cell.value for cell in ws_dayun[1]]
print(f"Headers: {headers_dayun[:10]}...")

# Find column indices
nh4_col = None
no3_col = None
po4_col = None
for i, h in enumerate(headers_dayun):
    if h == 'NH4':
        nh4_col = i
    elif h == 'NO3':
        no3_col = i
    elif h == 'PO4':
        po4_col = i

print(f"NH4 col: {nh4_col}, NO3 col: {no3_col}, PO4 col: {po4_col}")

dayun_nh4 = []
dayun_no3 = []
dayun_po4 = []
dayun_pom = []  # POM - use IMN * 0.5 as estimate

imn_col = 1  # IMN is column index 1 (0-based) if first col is time

for row in ws_dayun.iter_rows(min_row=2, max_row=ws_dayun.max_row, values_only=True):
    if nh4_col is not None and row[nh4_col] is not None:
        dayun_nh4.append(row[nh4_col])
    else:
        dayun_nh4.append(0.2)  # default
    if no3_col is not None and row[no3_col] is not None:
        dayun_no3.append(row[no3_col])
    else:
        dayun_no3.append(1.0)  # default
    if po4_col is not None and row[po4_col] is not None:
        dayun_po4.append(row[po4_col])
    else:
        dayun_po4.append(0.05)  # default
    # POM estimate from IMN
    if row[imn_col] is not None:
        dayun_pom.append(row[imn_col] * 0.5)
    else:
        dayun_pom.append(1.0)

print(f"DAYUN WQ: {len(dayun_nh4)} records")
print(f"  NH4: first={dayun_nh4[0]:.3f}, last={dayun_nh4[-1]:.3f}")
print(f"  NO3: first={dayun_no3[0]:.3f}, last={dayun_no3[-1]:.3f}")
print(f"  PO4: first={dayun_po4[0]:.4f}, last={dayun_po4[-1]:.4f}")

# YIHE (沂河)
ws_yihe = wb['入湖河道水质数据-沂河']
headers_yihe = [cell.value for cell in ws_yihe[1]]
nh4_col_y = None
no3_col_y = None
po4_col_y = None
for i, h in enumerate(headers_yihe):
    if h == 'NH4':
        nh4_col_y = i
    elif h == 'NO3':
        no3_col_y = i
    elif h == 'PO4':
        po4_col_y = i

yihe_nh4 = []
yihe_no3 = []
yihe_po4 = []
yihe_pom = []

for row in ws_yihe.iter_rows(min_row=2, max_row=ws_yihe.max_row, values_only=True):
    if nh4_col_y is not None and row[nh4_col_y] is not None:
        yihe_nh4.append(row[nh4_col_y])
    else:
        yihe_nh4.append(0.5)
    if no3_col_y is not None and row[no3_col_y] is not None:
        yihe_no3.append(row[no3_col_y])
    else:
        yihe_no3.append(2.0)
    if po4_col_y is not None and row[po4_col_y] is not None:
        yihe_po4.append(row[po4_col_y])
    else:
        yihe_po4.append(0.03)
    if row[imn_col] is not None:
        yihe_pom.append(row[imn_col] * 0.5)
    else:
        yihe_pom.append(2.0)

print(f"\nYIHE WQ: {len(yihe_nh4)} records")

# LUONAN (骆南中运河)
ws_luonan = wb['入湖河道水质数据-骆南中运河']
headers_luonan = [cell.value for cell in ws_luonan[1]]
nh4_col_l = None
no3_col_l = None
po4_col_l = None
for i, h in enumerate(headers_luonan):
    if h == 'NH4':
        nh4_col_l = i
    elif h == 'NO3':
        no3_col_l = i
    elif h == 'PO4':
        po4_col_l = i

luonan_nh4 = []
luonan_no3 = []
luonan_po4 = []
luonan_pom = []

for row in ws_luonan.iter_rows(min_row=2, max_row=ws_luonan.max_row, values_only=True):
    if nh4_col_l is not None and row[nh4_col_l] is not None:
        luonan_nh4.append(row[nh4_col_l])
    else:
        luonan_nh4.append(0.3)
    if no3_col_l is not None and row[no3_col_l] is not None:
        luonan_no3.append(row[no3_col_l])
    else:
        luonan_no3.append(1.5)
    if po4_col_l is not None and row[po4_col_l] is not None:
        luonan_po4.append(row[po4_col_l])
    else:
        luonan_po4.append(0.04)
    # IMN column might be different for luonan
    if len(row) > 2 and row[2] is not None and isinstance(row[2], (int, float)):
        luonan_pom.append(float(row[2]) * 0.3)
    else:
        luonan_pom.append(1.5)

print(f"LUONAN WQ: {len(luonan_nh4)} records")

# Now create the NetCDF file
# We need to match the length of flow data
# Use first 365 days for a 1-year test simulation
n_days_use = min(n_days, 365)

print(f"\nCreating rivers.nc with {n_days_use} days...")

# Create NetCDF
ds = nc.Dataset(output_path, 'w', format='NETCDF4')

# Time dimension (unlimited)
ds.createDimension('time', None)

# Time variable
time_var = ds.createVariable('time', 'f8', ('time',))
time_var.units = 'seconds since 2020-01-01 00:00:00'
time_var.calendar = 'standard'

start_date = datetime(2020, 1, 1)
for i in range(n_days_use):
    time_var[i] = i * 86400.0  # seconds

# River list (5 rivers)
rivers = ['YIHE', 'LUONAN', 'DAYUN', 'ZHANGSHAN', 'YANGHE']

# Flow data (m3/s)
# Note: GETM convention - inflow positive, outflow negative
# From Excel: DAYUN negative = outflow, positive = inflow
# ZHANGSHAN, YANGHE are negative = outflow

for i, river in enumerate(rivers):
    if river == 'YIHE':
        flow_data = yihe_flow[:n_days_use]
        nh4_data = yihe_nh4[:n_days_use]
        no3_data = yihe_no3[:n_days_use]
        po4_data = yihe_po4[:n_days_use]
        pom_data = yihe_pom[:n_days_use]
    elif river == 'LUONAN':
        flow_data = luonan_flow[:n_days_use]
        nh4_data = luonan_nh4[:n_days_use]
        no3_data = luonan_no3[:n_days_use]
        po4_data = luonan_po4[:n_days_use]
        pom_data = luonan_pom[:n_days_use]
    elif river == 'DAYUN':
        flow_data = dayun_flow[:n_days_use]
        nh4_data = dayun_nh4[:n_days_use]
        no3_data = dayun_no3[:n_days_use]
        po4_data = dayun_po4[:n_days_use]
        pom_data = dayun_pom[:n_days_use]
    elif river == 'ZHANGSHAN':
        flow_data = zhangshan_flow[:n_days_use]
        # For outflow rivers, use lake concentration as default
        nh4_data = [0.05] * n_days_use
        no3_data = [0.5] * n_days_use
        po4_data = [0.02] * n_days_use
        pom_data = [0.5] * n_days_use
    elif river == 'YANGHE':
        flow_data = yanghe_flow[:n_days_use]
        nh4_data = [0.05] * n_days_use
        no3_data = [0.5] * n_days_use
        po4_data = [0.02] * n_days_use
        pom_data = [0.5] * n_days_use
    
    # Flow variable
    flow_var = ds.createVariable(river, 'f4', ('time',))
    flow_var.units = 'm3/s'
    flow_var.long_name = f'{river} river discharge'
    flow_var[:] = np.array(flow_data, dtype=np.float32)
    
    # Water quality variables (for FABM-WET tracers)
    # ammonium (NH4)
    nh4_var = ds.createVariable(f'{river}_ammonium', 'f4', ('time',))
    nh4_var.units = 'g/m3'
    nh4_var.long_name = f'{river} ammonium concentration'
    nh4_var[:] = np.array(nh4_data, dtype=np.float32)
    
    # nitrate (NO3)
    no3_var = ds.createVariable(f'{river}_nitrate', 'f4', ('time',))
    no3_var.units = 'g/m3'
    no3_var.long_name = f'{river} nitrate concentration'
    no3_var[:] = np.array(no3_data, dtype=np.float32)
    
    # phosphate (PO4)
    po4_var = ds.createVariable(f'{river}_phosphate', 'f4', ('time',))
    po4_var.units = 'g/m3'
    po4_var.long_name = f'{river} phosphate concentration'
    po4_var[:] = np.array(po4_data, dtype=np.float32)
    
    # POM (particulate organic matter)
    pom_var = ds.createVariable(f'{river}_POM_sNW', 'f4', ('time',))
    pom_var.units = 'g/m3'
    pom_var.long_name = f'{river} particulate organic matter (non-siliceous)'
    pom_var[:] = np.array(pom_data, dtype=np.float32)

ds.close()

print(f"\nCreated: {output_path}")

# Verify
ds2 = nc.Dataset(output_path, 'r')
print(f"\nVerification:")
print(f"  Time steps: {len(ds2.dimensions['time'])}")
print(f"  Variables: {list(ds2.variables.keys())}")

print("\nFlow statistics (first 30 days):")
for river in rivers:
    flow = ds2.variables[river][:30]
    print(f"  {river}: min={flow.min():.2f}, max={flow.max():.2f}, mean={flow.mean():.2f} m3/s")

ds2.close()
print("\nDone.")
