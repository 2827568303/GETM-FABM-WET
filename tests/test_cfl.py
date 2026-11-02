"""Verify real server CFL and preflight bodies without starting background workers."""
import ast
import re
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import netCDF4 as nc
import numpy as np
import pytest
import yaml
from flask import Flask, jsonify, request


SERVER = Path(__file__).resolve().parents[1] / '3DWET' / 'app' / 'server.py'


@pytest.fixture
def cfl_api(tmp_path, monkeypatch):
    names = {'_cfl_max_timestep', '_parse_gotm_time_interval', 'config_time', 'run_check', 'run_start',
             'parse_getm_inp', 'get_time_settings', 'write_getm_inp', 'estimate_run_time', 'run_estimate'}
    tree = ast.parse(SERVER.read_text(encoding='utf-8-sig'))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    for function in functions:
        function.decorator_list = []
    monkeypatch.syspath_prepend(str(SERVER.parent))
    app = Flask(__name__)
    executable = tmp_path / 'solver'
    executable.touch()
    scope = dict(Path=Path, np=np, nc_open=nc.Dataset, app=app, request=request,
                 jsonify=jsonify, datetime=datetime, active_case_path=tmp_path,
                 run_status='idle', run_thread=None, EXE_PATH=executable, run_logs=[],
                 _mpi_tuning_state={'status': 'idle', 'progress': None, 'result': None,
                                    'error': None, 'cancel': None, 'signature': None},
                 _case_in_use=lambda _:False,
                 _water_cells=lambda _: 4, _ensure_forcing_coverage=lambda *_: [],
                 inspect_forcing_coverage=lambda *_: [], __name__='test-context',
                 yaml=yaml, _active_case_is_read_only_gotm=lambda:False,
                 _is_trusted_gotm_working_copy=lambda _:False,
                 sys=SimpleNamespace(modules={'test-context':SimpleNamespace()}),
                 find_output_files=lambda _: {}, _ghg_case_enabled=lambda _: False)
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SERVER), 'exec'), scope)
    app.add_url_rule('/api/config/time', view_func=scope['config_time'], methods=['GET', 'POST'])
    app.add_url_rule('/api/run/check', view_func=scope['run_check'])
    app.add_url_rule('/api/run/estimate', view_func=scope['run_estimate'])
    app.add_url_rule('/api/run/start', view_func=scope['run_start'], methods=['POST'])
    (tmp_path / 'getm.inp').write_text('&time\n timestep = 2\n/\n')
    return SimpleNamespace(path=tmp_path, scope=scope, client=app.test_client())


def grid(path, x=None, y=None, dx=None, dy=None, depth=10):
    with nc.Dataset(path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 3)
        ds.createDimension('y', 3)
        b = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
        b[:] = depth
        for name, values in (('x', x), ('y', y)):
            if values is not None:
                ds.createVariable(name, 'f8', (name,))[:] = values
        for name, value in (('dx', dx), ('dy', dy)):
            if value is not None:
                ds.createVariable(name, 'f8', ())[:] = value


@pytest.mark.parametrize('x,y,expected_dx,expected_dy', [
    ([0, 100, 200], [0, 100, 200], 100, 100),
    ([0, 100, 200], [0, 500, 1000], 100, 500),
    ([0, 20, 200], [0, 30, 300], 20, 30),
    ([0, 0, 50], [100, 60, 0], 50, 40),
])
def test_cfl_matches_getm_formula_and_minimum_spacing(cfl_api, x, y, expected_dx, expected_dy):
    grid(cfl_api.path, x=x, y=y)
    maximum, cfl = cfl_api.scope['_cfl_max_timestep'](cfl_api.path)
    expected = expected_dx * expected_dy / (np.sqrt(2) * np.sqrt(9.81 * 10) * np.hypot(expected_dx, expected_dy))
    assert cfl == pytest.approx(expected)
    assert maximum == pytest.approx(expected)


def test_scalar_cell_spacing_overrides_coordinate_spacing(cfl_api):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200], dx=40, dy=80)
    maximum, cfl = cfl_api.scope['_cfl_max_timestep'](cfl_api.path)
    assert maximum == cfl == pytest.approx(40 * 80 / (np.sqrt(2 * 9.81 * 10) * np.hypot(40, 80)))


@pytest.mark.parametrize('values', [
    {}, {'dx': np.nan, 'dy': 100}, {'dx': 100, 'dy': np.inf},
    {'x': [np.nan, np.nan, np.nan], 'y': [0, 100, 200]},
    {'x': [0, 100, 200], 'y': [0, 100, 200], 'depth': np.nan},
])
def test_missing_or_invalid_grid_returns_unknown(cfl_api, values):
    grid(cfl_api.path, **values)
    assert cfl_api.scope['_cfl_max_timestep'](cfl_api.path) == (None, None)
    response = cfl_api.client.get('/api/run/check')
    assert response.status_code == 200
    checks = response.get_json()['checks']
    assert any(check['level'] == 'warn' and 'CFL' in check['title'] for check in checks)


def test_absolute_altitude_mistaken_for_relative_water_level_is_flagged(cfl_api):
    grid(cfl_api.path, x=[0,100,200], y=[0,100,200])
    (cfl_api.path / 'getm.inp').write_text(
        '&time\n timestep = 2\n/\n&domain\n maxdepth = 11.2\n/\n'
        '&m2d\n elev_method = 1\n elev_const = 1880\n/\n')
    checks = cfl_api.client.get('/api/run/check').get_json()['checks']
    assert any(c['title'] == '水位基准可疑' for c in checks)


@pytest.mark.parametrize('value', [0, -1, 'nan', 'inf', '-inf', 'wrong', None])
def test_invalid_timestep_blocks_all_preflight_paths(cfl_api, value):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200])
    assert cfl_api.client.post('/api/config/time', json={'timestep': value}).status_code == 400
    (cfl_api.path / 'getm.inp').write_text(f'&time\n timestep = {value}\n/\n')
    response = cfl_api.client.get('/api/run/check')
    assert response.status_code == 200
    assert response.get_json()['ok'] is False
    assert any(check['level'] == 'error' and '时间步长' in check['title'] for check in response.get_json()['checks'])
    assert cfl_api.client.post('/api/run/start').status_code == 400


def test_timestep_above_estimate_is_rejected_without_fifteen_fold_allowance(cfl_api):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200])
    response = cfl_api.client.post('/api/config/time', json={'timestep': 6})
    assert response.status_code == 400
    assert 'CFL' in response.get_json()['error']
    (cfl_api.path / 'getm.inp').write_text('&time\n timestep = 6\n/\n')
    assert cfl_api.client.get('/api/run/check').get_json()['ok'] is False
    assert cfl_api.client.post('/api/run/start').status_code == 400


def test_pre_run_runtime_is_not_presented_as_calibrated_from_a_fixed_coefficient(cfl_api):
    grid(cfl_api.path)
    estimate = cfl_api.scope['estimate_run_time'](cfl_api.path, {
        'time': {'start': '2000-01-01 00:00:00', 'stop': '2000-01-02 00:00:00', 'timestep': 60},
        'm3d': {'M': 20},
    })

    assert estimate['nsteps'] == 1440
    assert estimate['nwater'] == 9
    assert estimate['grid'] == '3x3'
    assert estimate['nlev'] == 20
    assert estimate['runtime_estimate'] is None
    assert estimate['runtime_estimate_status'] == 'uncalibrated'
    assert '代表性' in estimate['pilot_guidance']
    assert 'estimated_seconds' not in estimate
    assert 'estimated_minutes' not in estimate


def test_getm_pre_run_estimate_api_exposes_workload_and_uncalibrated_status(cfl_api):
    grid(cfl_api.path)
    response = cfl_api.client.get('/api/run/estimate')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['runtime_estimate'] is None
    assert payload['runtime_estimate_status'] == 'uncalibrated'
    assert payload['nwater'] == 9 and payload['nsteps'] > 0


def test_gotm_pre_run_estimate_does_not_return_null_runtime_fields(cfl_api):
    cfl_api.scope['_is_trusted_gotm_working_copy'] = lambda _: True
    (cfl_api.path / 'gotm.yaml').write_text(
        'time:\n  start: 2000-01-01\n  stop: 2000-01-02\n  dt: 60\n', encoding='utf-8')
    response = cfl_api.client.get('/api/run/estimate')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['runtime_estimate'] is None
    assert payload['runtime_estimate_status'] == 'uncalibrated'
    assert payload['nlev'] == 1
    assert 'estimated_minutes' not in payload


def test_pre_run_panel_uses_workload_and_pilot_guidance_instead_of_fake_runtime():
    app_js = (SERVER.parent / 'static' / 'js' / 'app.js').read_text(encoding='utf-8')
    panel = app_js[app_js.index('async function loadTimeSettings'):app_js.index('async function saveTimeSettings')]

    assert 'est.estimated_minutes' not in panel
    assert 'est.pilot_guidance' in panel
    assert 'est.nsteps.toLocaleString()' in panel
    assert 'est.nwater' in panel


def test_homepage_cache_bust_serves_current_app_script():
    template = (SERVER.parent / 'templates' / 'index.html').read_text(encoding='utf-8')
    match = re.search(r'/static/js/app\.js\?v=(\d+)', template)
    assert match and int(match.group(1)) >= 82


def test_cfl_passing_message_does_not_guarantee_ecosystem_stability(cfl_api):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200])
    response = cfl_api.client.get('/api/run/check')
    check = next(item for item in response.get_json()['checks'] if item['title'] == '时间步长')
    assert check['level'] == 'ok'
    assert '不保证' in check['detail'] and '生态' in check['detail']


def test_forcing_shortage_is_blocking_before_start(cfl_api):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200])
    cfl_api.scope['inspect_forcing_coverage'] = lambda *_: ['meteo.nc 覆盖不足']
    result = cfl_api.client.get('/api/run/check').get_json()
    assert result['ok'] is False
    assert any(c['title'] == '驱动数据覆盖不足' and c['level'] == 'error' for c in result['checks'])


@pytest.mark.parametrize('meteo_file,metforcing,should_block', [
    (True, False, True),   # stale imported forcing must never be silently ignored
    (False, True, True),   # enabled forcing without its configured input is invalid
    (False, False, False), # builtin no-forcing cases remain runnable
    (True, True, False),
])
def test_meteo_file_and_getm_setting_must_agree(cfl_api, meteo_file, metforcing, should_block):
    grid(cfl_api.path, x=[0, 100, 200], y=[0, 100, 200])
    (cfl_api.path / 'getm.inp').write_text(
        f'&time\n timestep = 2\n/\n&meteo\n metforcing = {".true." if metforcing else ".false."}\n/\n')
    if meteo_file:
        (cfl_api.path / 'meteo.nc').touch()
    result = cfl_api.client.get('/api/run/check').get_json()
    meteo_checks = [item for item in result['checks'] if item['title'] == '气象强迫配置不一致']
    assert bool(meteo_checks) is should_block
    assert result['ok'] is (not should_block)
    if should_block:
        assert meteo_checks[0]['level'] == 'error'
        assert meteo_checks[0]['fix']


def test_run_start_rejects_existing_meteo_file_when_forcing_is_disabled(cfl_api):
    (cfl_api.path / 'getm.inp').write_text(
        '&time\n timestep = 2\n/\n&meteo\n metforcing = .false.\n/\n')
    (cfl_api.path / 'meteo.nc').touch()
    response = cfl_api.client.post('/api/run/start')
    assert response.status_code == 400
    assert 'GETM 会忽略该气象数据' in response.get_json()['error']


def test_stop_restart_waits_for_previous_worker_cleanup(cfl_api):
    cfl_api.scope['run_status'] = 'stopped'
    cfl_api.scope['run_thread'] = SimpleNamespace(is_alive=lambda: True)
    response = cfl_api.client.post('/api/run/start')
    assert response.status_code == 409
    assert '结束' in response.get_json()['error']
