from test_grid_api import grid, change
import json
import netCDF4 as nc
import pytest


def test_points_require_one_water_cell_and_preserve_calibration(grid):
    client, ctx, path = grid
    ctx.calibration_points = [{'id': 'global1', 'name': 'station', 'i': 1, 'j': 1}]
    s = client.get('/api/grid/editor').get_json()
    assert change(client, s, action='point', cells=[[2, 0]], name='monitor', kind='monitor').status_code == 400
    assert change(client, s, action='point', cells=[[0, 0], [1, 1]], name='monitor', kind='monitor').status_code == 400
    s = change(client, s, action='point', cells=[[1, 1]], name='monitor', kind='monitor', calibration_id='global1').get_json()
    assert s['points'][0]['calibration_id'] == 'global1'
    assert not (path / 'lake_points.json').exists()
    s = change(client, s, action='undo').get_json()
    assert s['points'] == []
    s = change(client, s, action='redo').get_json()
    assert change(client, s, action='save').status_code == 200
    assert json.loads((path / 'lake_points.json').read_text())['points'][0]['i'] == 2
    assert ctx.calibration_points[0]['i'] == 1


def test_river_rename_and_direction_preserve_forcing(grid):
    client, _, path = grid
    with nc.Dataset(path / 'rivers.nc', 'w') as ds:
        ds.createDimension('time', 2)
        ds.createVariable('INLET', 'f8', ('time',))[:] = [4, 6]
        ds.createVariable('INLET_temp', 'f8', ('time',))[:] = [20, 21]
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='river_update', river_index=0, cells=[[1, 1]], name='OUTLET', kind='outflow').get_json()
    assert not s.get('error')
    s = change(client, s, action='save').get_json()
    assert s.get('backup')
    with nc.Dataset(path / 'rivers.nc') as ds:
        assert list(ds['OUTLET'][:]) == [-4, -6]
        assert list(ds['OUTLET_temp'][:]) == [20, 21]
    assert '2 2 OUTLET' in (path / 'riverinfo.dat').read_text()
    assert json.loads((path / 'rivers_setup.json').read_text())['rivers'][0]['name'] == 'OUTLET'


def test_point_external_change_and_land_save_block(grid):
    client, _, path = grid
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='point', cells=[[1, 1]], name='sample', kind='source').get_json()
    s = change(client, s, action='land', cells=[[1, 1]]).get_json()
    assert change(client, s, action='save').status_code == 400
    (path / 'lake_points.json').write_text('{}')
    assert change(client, s, action='save').status_code == 409


def test_new_river_direction_survives_reload(grid):
    client, _, _ = grid
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='river_add', cells=[[1, 1]], name='EXIT', kind='outflow').get_json()
    s = change(client, s, action='save').get_json()
    s = change(client, s, action='reload').get_json()
    assert s['rivers'][1]['kind'] == 'outflow'


def test_undo_saved_river_rename_updates_forcing_again(grid):
    client, _, path = grid
    with nc.Dataset(path / 'rivers.nc', 'w') as ds:
        ds.createDimension('time', 1)
        ds.createVariable('INLET', 'f8', ('time',))[:] = [4]
    (path / 'river_drafts').mkdir()
    (path / 'river_drafts' / 'INLET.json').write_text(json.dumps({'dates': ['2026-10-01'], 'Q': [4], 'temp': [20]}))
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='river_update', river_index=0, cells=[[1, 1]], name='RENAMED', kind='inflow').get_json()
    s = change(client, s, action='save').get_json()
    assert (path / 'river_drafts' / 'RENAMED.json').exists()
    assert not (path / 'river_drafts' / 'INLET.json').exists()
    s = change(client, s, action='undo').get_json()
    assert change(client, s, action='save').status_code == 200
    assert (path / 'river_drafts' / 'INLET.json').exists()
    assert not (path / 'river_drafts' / 'RENAMED.json').exists()
    with nc.Dataset(path / 'rivers.nc') as ds:
        assert 'INLET' in ds.variables
        assert list(ds['INLET'][:]) == [4]


def test_save_rolls_back_all_files_if_replacement_fails(grid, monkeypatch):
    import grid_api
    client, _, path = grid
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='point', cells=[[1, 1]], name='sample', kind='monitor').get_json()
    s = change(client, s, action='depth', cells=[[1, 1]], value=9).get_json()
    replace = grid_api.os.replace
    def fail_once(source, target):
        if Path(target).name == 'bathymetry.nc':
            raise OSError('simulate file lock')
        return replace(source, target)
    from pathlib import Path
    monkeypatch.setattr(grid_api.os, 'replace', fail_once)
    assert change(client, s, action='save').status_code == 400
    assert not (path / 'lake_points.json').exists()
    assert not (path / 'rivers_setup.json').exists()
    with nc.Dataset(path / 'bathymetry.nc') as ds:
        assert ds['bathymetry'][1, 1] == 4


def test_saved_calibration_mapping_overrides_only_active_case_clone(grid):
    from lake_points_api import effective_calibration_points
    client, ctx, path = grid
    ctx.calibration_points = [{'id': 'linked', 'name': 'existing', 'i': 0, 'j': 0, 'variables': ['temp']}]
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='point', cells=[[1, 1]], name='local', kind='monitor', calibration_id='linked').get_json()
    assert effective_calibration_points(ctx)[0]['i'] == 0  # unsaved edits do not affect extraction
    change(client, s, action='save')
    actual = effective_calibration_points(ctx)
    assert (actual[0]['i'], actual[0]['j']) == (1, 1)
    actual[0]['variables'].append('chla')
    assert ctx.calibration_points == [{'id': 'linked', 'name': 'existing', 'i': 0, 'j': 0, 'variables': ['temp']}]
    ctx.active_case_path = path / 'other'
    ctx.active_case_path.mkdir()
    assert effective_calibration_points(ctx)[0]['i'] == 0
    ctx.active_case_path = None
    assert effective_calibration_points(ctx)[0]['i'] == 0


@pytest.mark.parametrize('mapping', [
    {'i': 3, 'j': 1}, {'i': 100, 'j': 1}, {'i': 1.5, 'j': 1}, {'i': True, 'j': 1},
    {'i': 1, 'j': 0}, {'i': '2', 'j': 1},
])
def test_invalid_calibration_mapping_keeps_original_coordinates(grid, mapping):
    from lake_points_api import effective_calibration_points
    _, ctx, path = grid
    ctx.calibration_points = [{'id': 'linked', 'i': 0, 'j': 0}]
    (path / 'lake_points.json').write_text(json.dumps({'points': [{'id': 'local', 'calibration_id': 'linked', **mapping}]}))
    assert effective_calibration_points(ctx)[0] == ctx.calibration_points[0]


def calibration_server(grid, monkeypatch):
    import sys
    from types import ModuleType
    _, ctx, path = grid
    ctx.calibration_points = [{'id': 'linked', 'name': 'station', 'i': 0, 'j': 0, 'variables': ['temp']}]
    ctx.calibration_data = {'linked': {'temp': [{'value': 10}]}}
    (path / 'lake_points.json').write_text(json.dumps({'points': [{'id': 'local', 'calibration_id': 'linked', 'i': 2, 'j': 2}]}))
    (path / 'fabm.yaml').write_text('instances: {}\n')
    module = ModuleType('server')
    module.__dict__.update(vars(ctx))
    module.load_calibration = lambda: None
    module.wsl_path = lambda value: str(value)
    module.find_output_files = lambda tmp: {'3d': str(tmp / 'result.nc'), '2d': None}
    module.get_timeseries = lambda file, variable, i, j: {'values': [i+j]}
    module._pair_obs_sim = lambda obs, sim: ([{'obs': obs[0]['value'], 'sim': sim['values'][0]}], [])
    module.EXE_PATH = 'fake_solver'
    monkeypatch.setitem(sys.modules, 'server', module)
    return module, path


def test_temp_calibration_reads_saved_case_snapshot_before_copy(grid, monkeypatch):
    import calibration
    from types import SimpleNamespace
    module, path = calibration_server(grid, monkeypatch)
    # This test isolates the point snapshot. Native output integrity has its own
    # tests; the intentionally fake subprocess here emits no model files.
    monkeypatch.setattr(calibration, '_validate_trial_output', lambda *args: {'ready': True})
    monkeypatch.setattr(calibration.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0))
    original_copy = calibration.shutil.copy2
    def switch_during_copy(*args, **kwargs):
        module.active_case_path = path / 'different_case'
        module.calibration_points[0].update(i=100, j=100)
        return original_copy(*args, **kwargs)
    monkeypatch.setattr(calibration.shutil, 'copy2', switch_during_copy)
    result = calibration.run_model_in_temp(path, [])
    assert result['outputs']['linked/temp']['values'] == [2]


def test_calibration_job_freezes_case_points_and_observations(grid, monkeypatch):
    import calibration
    module, path = calibration_server(grid, monkeypatch)
    job = calibration.CalibrationJob('test', 'parsac', [], 'rmse', 2, path)
    module.active_case_path = path / 'different_case'
    module.calibration_points[0].update(i=100, j=100)
    module.calibration_data['linked']['temp'][0]['value'] = 100
    recorded = []
    def model(case, params, **kwargs):
        recorded.append(kwargs.get('points_snapshot'))
        return {'success': True, 'outputs': {'linked/temp': {'values': [8]}}}
    class Engine:
        def calibrate(self, params, objective, callback, max_iter, squared_distance=False,
                      max_simulations=None):
            assert squared_distance, 'RMSE jobs must use the equivalent smooth optimization objective'
            values = [objective([]), objective([])]
            return {'success': True, 'best_objective': values[-1]}
    monkeypatch.setattr(calibration, 'run_model_in_temp', model)
    monkeypatch.setattr(calibration, 'ScipyEngine', Engine)
    job._run()
    assert job.status == 'completed'
    assert job.result['best_objective'] == 2
    assert len(recorded) == 2
    assert all((points[0]['i'], points[0]['j']) == (1, 1) for points in recorded)


def test_auto_calibration_rejects_snapshot_for_switched_case(grid, monkeypatch):
    import calibration
    module, path = calibration_server(grid, monkeypatch)
    module.active_case_path = path / 'different_case'
    with pytest.raises(ValueError, match='案例'):
        calibration.CalibrationJob('test', 'parsac', [], 'rmse', 2, path)


def test_saved_ui_cell_binding_enriches_calibration_identity_without_claiming_crs(grid):
    from lake_points_api import effective_calibration_points
    client, ctx, path = grid
    with nc.Dataset(path / 'bathymetry.nc', 'r+') as ds:
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [10, 20, 30]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [40, 50]
    ctx.calibration_points = [{'id': 'cal-1', 'name': 'Station A', 'i': 0, 'j': 0,
                              'variables': ['temp']}]
    s = client.get('/api/grid/editor').get_json()
    s = change(client, s, action='point', cells=[[1, 1]], name='Station A', kind='monitor',
               calibration_id='cal-1', lake_id='Lake-X', station_id='Station-A',
               observation_point_id='obs-A').get_json()
    assert change(client, s, action='save').status_code == 200
    actual = effective_calibration_points(ctx)[0]
    assert (actual['i'], actual['j']) == (1, 1)
    assert (actual['lake_id'], actual['station_id'], actual['point_id']) == ('Lake-X', 'Station-A', 'obs-A')
    assert actual['spatial_mapping'] == 'explicit_cell'
    assert actual['mapping_source'] == 'gridstudio_explicit_cell'
    assert (actual['x_m'], actual['y_m']) == (20, 50)
    assert 'coordinate_crs' not in actual
