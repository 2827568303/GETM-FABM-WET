"""Variable metadata lookup supports companion output candidate collections."""
from pathlib import Path
import sys

import netCDF4 as nc
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
import server


def _output(path, variables):
    path.parent.mkdir(parents=True, exist_ok=True)
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 2), ('sigma', 1), ('y', 2), ('x', 3)]:
            ds.createDimension(name, size)
        time = ds.createVariable('time', 'f8', ('time',))
        time.units = 'hours since 2020-01-01 00:00:00'
        time[:] = [0, 1]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = 5
        for name in variables:
            variable = ds.createVariable(name, 'f4', ('time', 'sigma', 'y', 'x'))
            variable.units = 'gDW m-3'
            variable.long_name = name
            variable[:] = np.ones((2, 1, 2, 3), dtype=np.float32)


def _case(tmp_path, monkeypatch):
    case = tmp_path / 'case'
    case.mkdir()
    preferred = case / 'output.nc'
    companion = case / 'results.3d.nc'
    _output(preferred, ['temp'])
    _output(companion, ['greens_cohort2_sDW'])
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    with server._result_horizontal_geometry_cache_lock:
        server._result_horizontal_geometry_cache.clear()
    return case, companion


def test_lookup_result_variable_walks_companion_candidates(tmp_path, monkeypatch):
    _case(tmp_path, monkeypatch)

    result = server._lookup_result_variable('greens_cohort2_sDW')

    assert result == {
        'name': 'greens_cohort2_sDW',
        'units': 'gDW m-3',
        'long_name': 'greens_cohort2_sDW',
        'dims': ['time', 'sigma', 'y', 'x'],
        'ndim': 4,
    }


def test_2d_endpoint_returns_companion_variable_metadata(tmp_path, monkeypatch):
    _case(tmp_path, monkeypatch)

    response = server.app.test_client().get(
        '/api/results/2d?var=greens_cohort2_sDW&time=0&level=0')

    assert response.status_code == 200, response.get_json()
    payload = response.get_json()
    assert payload['name'] == 'greens_cohort2_sDW'
    assert payload['units'] == 'gDW m-3'
