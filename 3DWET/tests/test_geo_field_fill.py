import sys
from pathlib import Path

import netCDF4
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))


@pytest.fixture
def masked_output(tmp_path):
    path = tmp_path / 'output.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        ds.createDimension('time', 1)
        ds.createDimension('y', 2)
        ds.createDimension('x', 3)
        values = ds.createVariable('greens_sDW', 'f8', ('time', 'y', 'x'),
                                   fill_value=-2e20)
        values.missing_value = -9999.0
        values[0] = [[1.5, -0.25, -2e20], [2.5, -9999.0, 3.5]]
    return path


def test_geo_field_preserves_netcdf_mask_and_valid_extrema(monkeypatch, masked_output):
    import server

    monkeypatch.setattr(server, 'active_case_path', masked_output.parent)
    monkeypatch.setattr(server, 'find_output_files', lambda *args: {'3d': masked_output, '2d': None})
    response = server.app.test_client().get('/api/geo/field?var=greens_sDW&time=0&level=-1')

    assert response.status_code == 200
    assert response.json['values'] == [[1.5, -0.25, None], [2.5, None, 3.5]]
    assert response.json['min'] == -0.25
    assert response.json['max'] == 3.5
