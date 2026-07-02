#!/usr/bin/env python3
"""Read Luomahu input data from Inputs.xlsx."""
import openpyxl
import os

xlsx_path = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\luomahu_case\Luomahu_inputs\Inputs.xlsx"

print("Reading:", xlsx_path)
wb = openpyxl.load_workbook(xlsx_path, data_only=True)
print("Sheet names:", wb.sheetnames)
print()

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f"=== {sheet_name} ===")
    print(f"  Rows: {ws.max_row}, Cols: {ws.max_column}")
    print("  First 10 rows:")
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=min(10, ws.max_row), values_only=True)):
        print(f"    Row {i+1}: {row}")
    print()

print("\nDone.")
