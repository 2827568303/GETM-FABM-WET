"""Quick check of output file dimensions while model is still running."""
import netCDF4 as nc
import numpy as np

for fname in ['THEORETICAL_LAKE.2d.nc', 'THEORETICAL_LAKE.3d.nc']:
    try:
        ds = nc.Dataset(fname)
        print(f'\n=== {fname} ===')
        print(f'Dimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}')
        if 'bathymetry' in ds.variables:
            bathy = np.ma.filled(ds.variables['bathymetry'][:], 0.0)
            print(f'bathymetry shape: {bathy.shape}')
            print(f'wet cells: {(bathy > 0).sum()}')
        if 'time' in ds.variables:
            t = ds.variables['time'][:]
            print(f'time records: {len(t)}, first={t[0]:.0f}, last={t[-1]:.0f}')
        ds.close()
    except Exception as e:
        print(f'{fname}: {e}')
