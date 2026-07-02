"""Read river discharge data and lake levels in detail."""
import openpyxl
import os
from datetime import datetime

INPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "case", "inputs", "Inputs.xlsx"
)

wb = openpyxl.load_workbook(INPUT_PATH, data_only=True)

# Sheet 3: River discharge
print("=" * 70)
print("Sheet 3: 主要入湖、出湖河道流量数据")
print("=" * 70)
ws = wb["主要入湖、出湖河道流量数据"]
print(f"Rows: {ws.max_row}, Cols: {ws.max_column}")
for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True)):
    display_row = [str(c)[:20] if c is not None else "" for c in row]
    print(f"  Row {r_idx+1}: {display_row}")
print("  ...")
# Print last few rows
for r_idx, row in enumerate(ws.iter_rows(min_row=ws.max_row-3, max_row=ws.max_row, values_only=True)):
    display_row = [str(c)[:20] if c is not None else "" for c in row]
    print(f"  Row {ws.max_row-3+r_idx}: {display_row}")

# Sheet 7: Lake levels (sample every 100 rows to find time range)
print("\n" + "=" * 70)
print("Sheet 7: 湖内各点位水位数据")
print("=" * 70)
ws = wb["湖内各点位水位数据"]
print(f"Rows: {ws.max_row}, Cols: {ws.max_column}")
# Print first 5 rows
for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True)):
    display_row = [str(c)[:25] if c is not None else "" for c in row]
    print(f"  Row {r_idx+1}: {display_row}")
# Find unique time range by sampling
print("  Sampling time range...")
times_found = []
for r_idx, row in enumerate(ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=True)):
    if r_idx % 50000 == 0:
        print(f"    Row {r_idx+3}: {row[0]}")
    if row[0] is not None and r_idx < 5:
        times_found.append(row[0])
print(f"  First times: {times_found}")

# Sheet 8: Lake WQ - get 2020-01-01 values
print("\n" + "=" * 70)
print("Sheet 8: 湖内三场点位水质数据 - First 5 rows")
print("=" * 70)
ws = wb["湖内三场点位水质数据"]
for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True)):
    print(f"  Row {r_idx+1}: {row}")

# Check river discharge sign convention - print values for a few dates
print("\n" + "=" * 70)
print("River discharge values (first 10 days)")
print("=" * 70)
ws = wb["主要入湖、出湖河道流量数据"]
for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=15, values_only=True)):
    print(f"  Row {r_idx+1}: {row}")
