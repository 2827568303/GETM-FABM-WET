import numpy as np
import pandas as pd
from pathlib import Path

input_dir = Path(r'C:\Users\dinod\Desktop\GETM-FABM-WET\Luomahu_inputs')

print('=== 1. 分析 Bottom_Elev.p2d ===')
elev_data = []
with open(input_dir / 'Bottom_Elev.p2d', 'r') as f:
    header = f.readline()  # X Y Z
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 3:
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            elev_data.append((x, y, z))

elev_data = np.array(elev_data)
print(f'数据点数: {len(elev_data)}')
print(f'X范围: {elev_data[:,0].min():.2f} - {elev_data[:,0].max():.2f}')
print(f'Y范围: {elev_data[:,1].min():.2f} - {elev_data[:,1].max():.2f}')
print(f'Z(高程)范围: {elev_data[:,2].min():.2f} - {elev_data[:,2].max():.2f}')

# 检查网格分辨率
xs = np.unique(elev_data[:,0])
ys = np.unique(elev_data[:,1])
xs.sort()
ys.sort()
dx = np.diff(xs)
dy = np.diff(ys)
print(f'X方向网格数: {len(xs)}')
print(f'Y方向网格数: {len(ys)}')
print(f'dx 范围: {dx.min():.2f} - {dx.max():.2f} m')
print(f'dy 范围: {dy.min():.2f} - {dy.max():.2f} m')

print()
print('=== 2. 分析边界文件 ===')
bdy_points = []
with open(input_dir / '骆马湖_边界.p2d', 'r') as f:
    name = f.readline().strip()
    print(f'边界名称: {name}')
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            x, y = float(parts[0]), float(parts[1])
            bdy_points.append((x, y))

bdy_points = np.array(bdy_points)
print(f'边界点数: {len(bdy_points)}')
print(f'边界X范围: {bdy_points[:,0].min():.2f} - {bdy_points[:,0].max():.2f}')
print(f'边界Y范围: {bdy_points[:,1].min():.2f} - {bdy_points[:,1].max():.2f}')

print()
print('=== 3. 流量数据 ===')
df_flows = pd.read_excel(input_dir / 'Inputs.xlsx', sheet_name='Flows', header=2)
print(f'列名: {list(df_flows.columns)}')
print(f'行数: {len(df_flows)}')
print(df_flows.head(10).to_string())
