"""Check output.nc variables for Theoretical Lake."""
import netCDF4 as nc
import os

# Locate case dir relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
case_dir = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..', 'case', 'Theoretical lake'))

print('=' * 70)
print('output.nc variables')
print('=' * 70)
ds = nc.Dataset(os.path.join(case_dir, 'output.nc'))
vars_list = list(ds.variables.keys())
print(f'Total variables: {len(vars_list)}')

# Group by prefix
wet_vars = [v for v in vars_list if '_s' in v and not v.startswith('time')]
print(f'WET state-like vars: {len(wet_vars)}')
for v in sorted(wet_vars):
    var = ds.variables[v]
    print(f'  {v}: shape={var.shape}, units={getattr(var, "units", "?")}')

print()
print('=' * 70)
print('3D file variables (hydrodynamic)')
print('=' * 70)
ds3d = nc.Dataset(os.path.join(case_dir, 'THEORETICAL_LAKE.3d.nc'))
v3d = [v for v in ds3d.variables.keys()]
print(f'Total: {len(v3d)}')
print(f'Key vars: {[v for v in v3d if v in ["temp", "salt", "u", "v", "uu", "vv", "w", "tke", "eps", "num", "nuh", "sigma", "time", "lonc", "latc"]]}')

print()
print('=' * 70)
print('2D file variables')
print('=' * 70)
ds2d = nc.Dataset(os.path.join(case_dir, 'THEORETICAL_LAKE.2d.nc'))
v2d = [v for v in ds2d.variables.keys()]
print(f'Total: {len(v2d)}')
print(f'Vars: {v2d}')

print()
print('=' * 70)
print('Time and dimension info')
print('=' * 70)
t2d = ds2d.variables['time'][:]
t3d = ds3d.variables['time'][:]
tout = ds.variables['time'][:]
sigma = ds3d.variables['sigma'][:]
print(f'2D time: {len(t2d)} records, range [{t2d[0]/86400:.1f}, {t2d[-1]/86400:.1f}] days')
print(f'3D time: {len(t3d)} records, range [{t3d[0]/86400:.1f}, {t3d[-1]/86400:.1f}] days')
print(f'output time: {len(tout)} records, range [{tout[0]:.1f}, {tout[-1]:.1f}] (units: {getattr(ds.variables["time"], "units", "?")})')
print(f'sigma: {sigma}')
print(f'sigma range: [{sigma.min():.3f}, {sigma.max():.3f}]')

ds.close()
ds3d.close()
ds2d.close()
