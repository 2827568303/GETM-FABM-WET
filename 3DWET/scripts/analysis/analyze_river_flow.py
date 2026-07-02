#!/usr/bin/env python3
"""Analyze Luomahu river flow data."""
import openpyxl
import os

xlsx_path = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\Luomahu_inputs\Inputs.xlsx"

wb = openpyxl.load_workbook(xlsx_path, data_only=True)

# Analyze river flow data
ws = wb['主要入湖、出湖河道流量数据']
print("=== 主要入湖、出湖河道流量数据 ===")
print(f"Total rows: {ws.max_row}, Cols: {ws.max_column}")

# Headers (rows 1-4)
print("\nHeaders:")
for i in range(1, 5):
    row = [cell.value for cell in ws[i]]
    print(f"  Row {i}: {row}")

# Get all data
dates = []
dayun = []  # 京杭大运河 - 入/出
luonan = [] # 骆南中运河 - 入
yihe = []  # 沂河 - 入
zhangshan = [] # 嶂山闸 - 出
yanghe = [] # 杨河滩 - 出

for row in ws.iter_rows(min_row=5, max_row=ws.max_row, values_only=True):
    dates.append(row[0])
    dayun.append(row[1])
    luonan.append(row[2])
    yihe.append(row[3])
    zhangshan.append(row[4])
    yanghe.append(row[5])

print(f"\nData points: {len(dates)}")
print(f"Date range: {dates[0]} to {dates[-1]}")

# Calculate statistics
def stats(name, data):
    valid = [x for x in data if x is not None]
    if not valid:
        print(f"  {name}: no data")
        return
    print(f"  {name}: min={min(valid):.2f}, max={max(valid):.2f}, mean={sum(valid)/len(valid):.2f} CMS")
    # Count positive (inflow) and negative (outflow)
    pos = sum(1 for x in valid if x > 0)
    neg = sum(1 for x in valid if x < 0)
    zero = sum(1 for x in valid if x == 0)
    print(f"    Positive(inflow): {pos}, Negative(outflow): {neg}, Zero: {zero}")

print("\nFlow statistics (CMS):")
stats("京杭大运河(DAYUN)", dayun)
stats("骆南中运河(LUONAN)", luonan)
stats("沂河(YIHE)", yihe)
stats("嶂山闸(ZHANGSHAN)", zhangshan)
stats("杨河滩(YANGHE)", yanghe)

# Calculate total inflow and outflow
total_in = []
total_out = []
for i in range(len(dates)):
    inflow = 0
    outflow = 0
    if dayun[i] is not None:
        if dayun[i] > 0:
            inflow += dayun[i]
        else:
            outflow += abs(dayun[i])
    if luonan[i] is not None and luonan[i] > 0:
        inflow += luonan[i]
    if yihe[i] is not None and yihe[i] > 0:
        inflow += yihe[i]
    if zhangshan[i] is not None and zhangshan[i] < 0:
        outflow += abs(zhangshan[i])
    if yanghe[i] is not None and yanghe[i] < 0:
        outflow += abs(yanghe[i])
    total_in.append(inflow)
    total_out.append(outflow)

print(f"\nTotal inflow:  min={min(total_in):.2f}, max={max(total_in):.2f}, mean={sum(total_in)/len(total_in):.2f} CMS")
print(f"Total outflow: min={min(total_out):.2f}, max={max(total_out):.2f}, mean={sum(total_out)/len(total_out):.2f} CMS")

# Check first 30 days
print("\nFirst 30 days flow data:")
print(f"{'Date':<12} {'DAYUN':>8} {'LUONAN':>8} {'YIHE':>8} {'ZHANGSHAN':>10} {'YANGHE':>8} {'TotalIn':>9} {'TotalOut':>10}")
for i in range(min(30, len(dates))):
    print(f"{str(dates[i])[:10]:<12} {dayun[i] if dayun[i] is not None else 0:>8.2f} "
          f"{luonan[i] if luonan[i] is not None else 0:>8.2f} "
          f"{yihe[i] if yihe[i] is not None else 0:>8.2f} "
          f"{zhangshan[i] if zhangshan[i] is not None else 0:>10.2f} "
          f"{yanghe[i] if yanghe[i] is not None else 0:>8.2f} "
          f"{total_in[i]:>9.2f} {total_out[i]:>10.2f}")

print("\nDone.")
