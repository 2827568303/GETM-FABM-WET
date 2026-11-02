import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from netcdf_io import open_dataset


def test_non_ascii_case_path_read_write_append(tmp_path):
    folder = tmp_path / '耦合湖泊示例'
    folder.mkdir()
    path = folder / 'bathymetry.nc'
    with open_dataset(path, 'w') as ds:
        ds.createDimension('x', 2)
        ds.createVariable('depth', 'f4', ('x',))[:] = [1, 2]
    with open_dataset(path, 'r+') as ds:
        ds.variables['depth'][1] = 4
    with open_dataset(path) as ds:
        np.testing.assert_array_equal(ds.variables['depth'][:], [1, 4])
