"""The scientific viewport needs full wet topology and verified metre coordinates."""
from pathlib import Path
import sys

import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


@pytest.mark.parametrize('units,expected', [('m', 'projected'), ('degrees_east', 'index'), ('', 'index')])
def test_geometry_keeps_mask_independent_of_scalar_values(tmp_path, units, expected):
    from scientific_geometry import read_scientific_geometry
    path = tmp_path / 'grid.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.createDimension('x', 3); ds.createDimension('y', 2)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = units; x[:] = [100, 150, 200]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = units; y[:] = [200, 300]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'), fill_value=99)[:] = [[0, 5, 99], [-10, 3, 4]]
    with nc.Dataset(path) as ds:
        result = read_scientific_geometry(ds)
    assert result['shape'] == [2, 3]
    assert result['wetMask'] == [[False, True, False], [False, True, True]]
    assert result['depth'] == [[None, 5, None], [None, 3, 4]]
    assert result['dry_mask'] == [[True, False, False], [True, False, False]]
    assert result['land_elevation'] is None
    import json
    json.dumps(result, allow_nan=False)
    assert result['coordinate_mode'] == expected
    if expected == 'projected':
        assert result['xc'] == [100, 150, 200]
        assert result['yc'] == [200, 300]
        assert result['coordinate_units'] == 'm'
    else:
        assert result['xc'] is None and result['yc'] is None


def test_nonmonotone_or_nonfinite_coordinates_fall_back(tmp_path):
    from scientific_geometry import read_scientific_geometry
    path = tmp_path / 'grid.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.createDimension('x', 3); ds.createDimension('y', 2)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [100, 90, 110]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [200, np.nan]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = 3
    with nc.Dataset(path) as ds:
        result = read_scientific_geometry(ds)
    assert result['coordinate_mode'] == 'index'
    assert result['wetMask'] == [[True] * 3] * 2


def test_dry_mask_identity_checks_unsampled_bathymetry(tmp_path):
    from scientific_geometry import matching_input_dry_mask
    for filename, axes in [('output.nc', ('xc', 'yc')), ('input.nc', ('x', 'y'))]:
        with nc.Dataset(tmp_path / filename, 'w') as ds:
            for name in axes:
                ds.createDimension(name, 3)
                coord = ds.createVariable(name, 'f8', (name,)); coord.units = 'm'; coord[:] = [0, 1, 2]
            b = ds.createVariable('bathymetry', 'f8', (axes[1], axes[0]), fill_value=99)
            b.units = 'm'; values = np.full((3, 3), 5.0)
            values[2, 2] = 99 if filename == 'output.nc' else -10
            if filename == 'input.nc':
                values[1, 1] = 999
            b[:] = values
    with nc.Dataset(tmp_path / 'output.nc') as output, nc.Dataset(tmp_path / 'input.nc') as grid:
        assert matching_input_dry_mask(output, grid, (3, 3)) is None
        assert matching_input_dry_mask(output, grid, (3, 3), slice(None, None, 2), slice(None, None, 2)) is None


def test_scientific_route_keeps_full_resolution_while_map_still_samples(tmp_path, monkeypatch):
    import server
    size = 142
    with nc.Dataset(tmp_path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', size); ds.createDimension('y', size)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = np.arange(size) * 50
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = np.arange(size) * 100
        depth = np.full((size, size), 5.)
        depth[71, 71] = -10
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = depth
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    client = server.app.test_client()
    response = client.get('/api/geo/grid?display=scientific')
    assert response.status_code == 200
    assert response.json['shape'] == [size, size]
    assert response.json['stride'] == 1
    assert response.json['wetMask'][71][71] is False
    assert response.json['depth'][71][71] is None
    assert client.get('/api/geo/grid').json['stride'] == 2
