"""Check all sheets and meteo/river WQ data in Inputs.xlsx."""
import openpyxl
import os

INPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "case", "inputs", "Inputs.xlsx"
)

wb = openpyxl.load_workbook(INPUT_PATH, data_only=True)

print("=" * 70)
print("All sheets in Inputs.xlsx")
print("=" * 70)
for i, name in enumerate(wb.sheetnames, 1):
    ws = wb[name]
    print(f"  {i}. {name} (rows={ws.max_row}, cols={ws.max_column})")

# Print first 5 rows of each sheet
for name in wb.sheetnames:
    print("\n" + "=" * 70)
    print(f"Sheet: {name} - first 5 rows")
    print("=" * 70)
    ws = wb[name]
    for r_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=5, values_only=True)):
        display_row = [str(c)[:25] if c is not None else "" for c in row]
        print(f"  Row {r_idx+1}: {display_row}")
