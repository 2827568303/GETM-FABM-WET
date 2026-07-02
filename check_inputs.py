import numpy as np
import pandas as pd
from pathlib import Path

input_dir = Path(r'C:\Users\dinod\Desktop\GETM-FABM-WET\Luomahu_inputs')

print('=== 1. 检查 Bottom_Elev.p2d (底部高程) ===')
elev_file = input_dir / 'Bottom_Elev.p2d'
with open(elev_file, 'r') as f:
    lines = f.readlines()
    print(f'总行数: {len(lines)}')
    print(f'前10行:')
    for i, line in enumerate(lines[:10]):
        print(f'  {i}: {line.rstrip()}')

print()
print('=== 2. 检查 骆马湖_边界.p2d (边界) ===')
bdy_file = input_dir / '骆马湖_边界.p2d'
with open(bdy_file, 'r') as f:
    lines = f.readlines()
    print(f'总行数: {len(lines)}')
    print(f'前20行:')
    for i, line in enumerate(lines[:20]):
        print(f'  {i}: {line.rstrip()}')

print()
print('=== 3. 检查 Inputs.xlsx ===')
xlsx_file = input_dir / 'Inputs.xlsx'
xls = pd.ExcelFile(xlsx_file)
print(f'Sheet列表: {xls.sheet_names}')
for sheet in xls.sheet_names:
    df = pd.read_excel(xlsx_file, sheet_name=sheet, nrows=5)
    print(f'\nSheet: {sheet}')
    print(f'  列名: {list(df.columns)}')
    print(f'  行数: {len(pd.read_excel(xlsx_file, sheet_name=sheet))}')
    print(f'  前3行:')
    print(df.head(3).to_string())
