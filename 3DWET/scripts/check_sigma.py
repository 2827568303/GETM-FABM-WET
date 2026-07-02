"""Quick check of sigma dimension and values in 3d.nc."""
import netCDF4 as nc
import os

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'case')
path = os.path.join(case_dir, 'LUOMAHU_WET.3d.nc')

with nc.Dataset(path) as ds:
    sigma = ds.variables['sigma'][:]
    print(f'sigma dimension size: {len(sigma)}')
    print(f'sigma values: {sigma[:]}')
    print(f'sigma min: {sigma.min()}, max: {sigma.max()}')

# Also check getm.inp for kdum
inp_path = os.path.join(case_dir, 'getm.inp')
with open(inp_path) as f:
    for line in f:
        s = line.strip()
        if s.startswith('kdum') or s.startswith('kmax') or s.startswith('vert_cord'):
            print(f'getm.inp: {s}')
