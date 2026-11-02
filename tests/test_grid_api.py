import sys
from pathlib import Path
from types import SimpleNamespace
import threading
import netCDF4 as nc
import numpy as np
import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from grid_api import register_grid_routes


@pytest.fixture
def grid(tmp_path):
    with nc.Dataset(tmp_path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('y', 2); ds.createDimension('x', 3)
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[1, 2, -10], [3, 4, 5]]
        ds.createVariable('extra', 'f8', ('x',))[:] = [7, 8, 9]
        ds.title = 'preserve me'
    (tmp_path / 'riverinfo.dat').write_text('1\n1 1 INLET -1 -1\n')
    context = SimpleNamespace(active_case_path=tmp_path, _NC_LOCK=threading.RLock(),
                              _case_in_use=lambda p: False, parse_getm_inp=lambda p: {})
    app = Flask(__name__)
    register_grid_routes(app, context)
    return app.test_client(), context, tmp_path


def change(client, state, **action):
    return client.post('/api/grid/edit', json=dict(case_path=state['case_path'], revision=state['revision'], **action))


def test_edit_undo_redo_save_preserves_file(grid):
    client, ctx, path = grid
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='depth', cells=[[0, 0]], value=7).get_json()
    assert s['depth'][0][0] == 7
    s = change(client, s, action='undo').get_json()
    assert s['depth'][0][0] == 1
    s = change(client, s, action='redo').get_json()
    assert s['depth'][0][0] == 7
    r = change(client, s, action='save')
    assert r.status_code == 200
    assert r.get_json()['backup']
    with nc.Dataset(path / 'bathymetry.nc') as ds:
        assert ds['bathymetry'][0, 0] == 7
        np.testing.assert_array_equal(ds['extra'][:], [7, 8, 9])
        assert ds.title == 'preserve me'


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -2, 'abc'])
def test_invalid_depth_rejected_without_change(grid, value):
    client, _, _ = grid
    s = client.get('/api/grid/editor').get_json()
    assert change(client, s, action='depth', cells=[[0, 0]], value=value).status_code == 400
    assert client.get('/api/grid/editor').get_json()['depth'][0][0] == 1


def test_stale_revision_and_running_case_block_writes(grid):
    client, ctx, _ = grid
    s = client.get('/api/grid/editor').get_json()
    assert change(client, s, action='depth', cells=[[0, 0]], value=6).status_code == 200
    assert change(client, s, action='depth', cells=[[0, 0]], value=8).status_code == 409
    s = client.get('/api/grid/editor').get_json()
    ctx._case_in_use = lambda p: True
    assert change(client, s, action='save').status_code == 409


def test_invalid_cell_and_external_modification(grid):
    client, _, path = grid
    s = client.get('/api/grid/editor').get_json()
    assert change(client, s, action='depth', cells=[[100, 0]], value=3).status_code == 400
    with nc.Dataset(path / 'bathymetry.nc', 'r+') as ds:
        ds['bathymetry'][0, 0] = 11
    assert change(client, s, action='save').status_code == 409


def test_river_move_undo_and_save(grid):
    client, _, path = grid
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='river', cells=[[1, 1]], river_index=0).get_json()
    assert s['rivers'][0]['i'] == 2 and s['rivers'][0]['j'] == 2
    assert change(client, s, action='save').status_code == 200
    assert '2 2 INLET -1 -1' in (path / 'riverinfo.dat').read_text()


def test_unchanged_mask_survives_save(grid):
    client, _, path = grid
    with nc.Dataset(path / 'bathymetry.nc', 'r+') as ds:
        ds['bathymetry'].missing_value = -9999.0
        ds['bathymetry'][0, 2] = -9999
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='depth', cells=[[1, 0]], value=9).get_json()
    assert change(client, s, action='save').status_code == 200
    with nc.Dataset(path / 'bathymetry.nc') as ds:
        assert np.ma.is_masked(ds['bathymetry'][0, 2])


def test_configuration_changed_requires_reload(grid):
    client, _, path = grid
    s = client.get('/api/grid/editor').get_json()
    (path / 'getm.inp').write_text('&domain\n bathymetry="other.nc"\n/\n')
    assert change(client, s, action='save').status_code == 409
