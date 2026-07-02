"""Analyze river discharge data to determine if single grid cell is sufficient.

For each river:
1. Read max discharge from Inputs.xlsx
2. Calculate required flow area: A = Q / v (v = max 1 m/s for stability)
3. Compare with grid cell cross-section: width * depth
4. Determine how many grid cells are needed
"""
import openpyxl
import numpy as np
import netCDF4 as nc
import os
from datetime import datetime

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
INPUTS_DIR = os.path.join(CASE_DIR, "inputs")
INPUT_PATH = os.path.join(INPUTS_DIR, "Inputs.xlsx")

# Read bathymetry for depth at river positions
ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
bathy = ds.variables['bathymetry'][:]
ds.close()

# River positions (1-based, i=col, j=row)
rivers = {
    'YIHE':     {'i': 21, 'j': 50, 'cn': '沂河',         'type': 'inflow'},
    'LUONAN':   {'i': 28, 'j':  2, 'cn': '骆南河',       'type': 'inflow'},
    'DAYUN':    {'i':  2, 'j': 32, 'cn': '京杭大运河',    'type': 'bidirectional'},
    'ZHANGSHAN':{'i': 42, 'j': 27, 'cn': '嶂山闸',       'type': 'outflow'},
    'YANGHE':   {'i': 35, 'j': 28, 'cn': '洋河',         'type': 'outflow'},
}

# Get depth at each river position
for name, info in rivers.items():
    i0, j0 = info['i']-1, info['j']-1
    info['depth'] = float(bathy[j0, i0])

# Read Inputs.xlsx for discharge data
wb = openpyxl.load_workbook(INPUT_PATH, data_only=True)
print("Sheet names:", wb.sheetnames)

# Find river discharge sheet - likely "河道流量" or similar
discharge_sheet = None
for sn in wb.sheetnames:
    if '河道' in sn or '流量' in sn or 'river' in sn.lower():
        discharge_sheet = wb[sn]
        print(f"\nUsing sheet: {sn}")
        break

if discharge_sheet is None:
    # Try first few sheets
    for sn in wb.sheetnames[:3]:
        print(f"\nSheet '{sn}' first row:")
        ws = wb[sn]
        for row in ws.iter_rows(min_row=1, max_row=3, values_only=True):
            print(f"  {row}")

# Print header and first few rows of discharge sheet
if discharge_sheet:
    print("\nHeader row:")
    for row in discharge_sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        for i, val in enumerate(row):
            if val is not None:
                print(f"  col {i}: {val}")

    print("\nFirst 5 data rows:")
    for row in discharge_sheet.iter_rows(min_row=2, max_row=6, values_only=True):
        print(f"  {row}")

# Read all discharge data for each river
print("\n" + "=" * 70)
print("Reading discharge data for each river")
print("=" * 70)

# Parse discharge data - need to find which columns correspond to which river
# Based on rivers.nc variable names: YIHE, LUONAN, DAYUN, ZHANGSHAN, YANGHE
river_discharge = {name: [] for name in rivers}
river_dates = []

for row in discharge_sheet.iter_rows(min_row=2, values_only=True):
    if row[0] is None:
        continue
    if isinstance(row[0], datetime):
        river_dates.append(row[0])
        for name in rivers:
            # Try to find discharge value - need to identify column
            # This depends on the actual sheet structure
            pass

# Read from rivers.nc which has the actual discharge values used
print("\nReading discharge from rivers.nc:")
ds_rivers = nc.Dataset(os.path.join(CASE_DIR, "rivers.nc"))
print(f"  Variables: {list(ds_rivers.variables.keys())}")

for name in rivers:
    if name in ds_rivers.variables:
        discharge = ds_rivers.variables[name][:]
        print(f"\n  {name} ({rivers[name]['cn']}, {rivers[name]['type']}):")
        print(f"    discharge range: {discharge.min():.2f} to {discharge.max():.2f} m3/s")
        print(f"    |discharge| max: {np.abs(discharge).max():.2f} m3/s")
        print(f"    mean: {discharge.mean():.2f} m3/s")
        print(f"    depth at river: {rivers[name]['depth']:.2f} m")

        # Calculate required cross-section area
        max_q = np.abs(discharge).max()
        # Assume max velocity 0.5 m/s for stability (typical for lake inlets)
        v_max = 0.5  # m/s
        required_area = max_q / v_max  # m2
        # Single grid cell cross-section = width * depth
        grid_width = 500.0  # m
        cell_area = grid_width * rivers[name]['depth']
        n_cells_needed = max(1, int(np.ceil(required_area / cell_area)))

        print(f"    Required flow area (at v={v_max} m/s): {required_area:.1f} m2")
        print(f"    Single cell area (500m x {rivers[name]['depth']:.1f}m): {cell_area:.1f} m2")
        print(f"    Cells needed: {n_cells_needed}")
        rivers[name]['max_q'] = max_q
        rivers[name]['required_area'] = required_area
        rivers[name]['cell_area'] = cell_area
        rivers[name]['n_cells_needed'] = n_cells_needed

ds_rivers.close()

print("\n" + "=" * 70)
print("Summary: Grid cells needed for each river")
print("=" * 70)
print(f"{'River':<15} {'CN Name':<15} {'Type':<15} {'Max Q':>10} {'Depth':>8} {'Cells':>6}")
print("-" * 75)
for name, info in rivers.items():
    print(f"{name:<15} {info['cn']:<15} {info['type']:<15} {info.get('max_q',0):>10.1f} {info['depth']:>8.2f} {info.get('n_cells_needed',1):>6}")
