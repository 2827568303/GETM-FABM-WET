import openpyxl
import sys

wb = openpyxl.load_workbook('/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/luomahu_case/Luomahu_inputs/Inputs.xlsx', read_only=True)
print('Sheet names:', wb.sheetnames)

for name in wb.sheetnames:
    ws = wb[name]
    print(f'\n=== {name} ({ws.max_row} rows x {ws.max_column} cols) ===')
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=8, values_only=True)):
        print(row)
