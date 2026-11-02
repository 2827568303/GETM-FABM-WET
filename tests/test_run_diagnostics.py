import importlib
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import netCDF4 as nc
import pytest
import yaml
from flask import Flask, jsonify

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))


@pytest.fixture
def diagnostics(tmp_path):
    assert importlib.util.find_spec('run_diagnostics'), 'Diagnostic action module is missing'
    module = importlib.import_module('run_diagnostics')
    case = tmp_path / 'case'
    case.mkdir()
    (case / 'getm.inp').write_bytes(b'&time\r\n timestep = 10, ! step\r\n start = \'2020-01-01 00:00:00\'\r\n stop = \'2020-01-03 00:00:00\'\r\n/\r\n&domain\r\n check_cfl = .false. ! guard\r\n/\r\n')
    (case / 'output.yaml').write_text('output:\n   time_unit: day\n   time_step: 1\n   sync_interval: 0\n   variables:\n      - source: *\n')
    ctx = SimpleNamespace(active_case_path=case, run_status='idle', _NC_LOCK=threading.RLock(),
                          cached_getm_config={}, _OUTPUT_UNREGISTERED={'u': 'unregistered', 'v': 'unregistered'},
                          _cfl_max_timestep=lambda _: (5, 5),
                          _preset_sources=lambda *args: ['temp', 'salt', 'real_module/*'])
    ctx.parse_getm_inp = lambda p: {'time': {'timestep': 10, 'start': '2020-01-01 00:00:00', 'stop': '2020-01-03 00:00:00'}}

    @contextmanager
    def nc_open(path):
        with ctx._NC_LOCK, nc.Dataset(path) as ds:
            yield ds
    ctx.nc_open = nc_open
    app = Flask(__name__)

    @app.get('/api/run/check')
    def run_check():
        warnings = module.inspect_forcing_coverage(case, ctx.parse_getm_inp(case / 'getm.inp'), ctx)
        checks = [{'level': 'warn', 'title': 'check_cfl 已关闭', 'detail': 'disabled'},
                  {'level': 'error', 'title': 'sync_interval = 0', 'detail': 'no records'},
                  {'level': 'error', 'title': '时间步长超过重力波 CFL 估计上限', 'detail': 'too large'},
                  {'level': 'warn', 'title': '输出全部变量', 'detail': 'many'}]
        checks += [{'level': 'warn', 'title': '驱动数据覆盖不足', 'detail': w} for w in warnings]
        return jsonify(checks=checks, ok=False, blocking=2)

    module.register_run_diagnostic_routes(app, ctx)
    return app, ctx, case, module


def request_data(app, action):
    with app.test_client() as client:
        data = client.get('/api/run/check').get_json()
    return dict(case_path=data['case_path'], revision=data['revision'], action=action)


def test_quoted_logicals_block_and_repair_preserves_other_text(diagnostics):
    app, ctx, case, _ = diagnostics
    path=case/'getm.inp'
    original=path.read_bytes()+b"&param\r\n dryrun = '.false.', ! preserve\r\n title = '.true.'\r\n/\r\n"
    path.write_bytes(original)
    client=app.test_client()
    data=client.get('/api/run/check').get_json()
    issue=next(c for c in data['checks'] if c['id']=='quoted-logicals')
    assert issue['level']=='error' and data['ok'] is False
    assert issue['repair']['id']=='unquote_logicals'
    assert path.read_bytes()==original
    result=client.post('/api/run/repair',json=request_data(app,'unquote_logicals'))
    assert result.status_code==200,result.get_json()
    assert path.read_bytes()==original.replace(b"dryrun = '.false.'",b'dryrun = .false.')
    assert any(p.read_bytes()==original for p in (case/'backups').glob('*.bak'))
    assert all(c['id']!='quoted-logicals' for c in client.get('/api/run/check').get_json()['checks'])


def test_checks_have_concrete_targets_and_stable_ids(diagnostics):
    app, ctx, case, _ = diagnostics
    data = app.test_client().get('/api/run/check').get_json()
    ids = [c['id'] for c in data['checks']]
    assert len(ids) == len(set(ids))
    assert data['case_path'] == str(case.resolve())
    assert data['revision']
    assert all(c['target']['page'] and c['target']['control'] and c['source_file'] for c in data['checks'])
    assert ids == [c['id'] for c in app.test_client().get('/api/run/check').get_json()['checks']]


def test_legacy_module_sources_convert_with_backup(diagnostics):
    app, ctx, case, module = diagnostics
    ctx._resolve_output_sources = lambda path,sources,context: ['temp','abiotic_water_sO2W']
    file = case / 'output.yaml'
    file.write_text('output:\n   sync_interval: 1\n   variables:\n      - source: temp\n      - source: abiotic_water/*\n')
    original = file.read_bytes()
    response = app.test_client().post('/api/run/repair', json=request_data(app, 'resolve_output_sources'))
    assert response.status_code == 200, response.get_json()
    assert 'abiotic_water_sO2W' in file.read_text() and '/*' not in file.read_text()
    assert any(p.read_bytes()==original for p in (case / 'backups').glob('*.bak'))
    check = module._check_action({'title':'输出订阅需要转换','detail':'legacy','level':'error'}, case,ctx)
    assert check['repair']['id'] == 'resolve_output_sources'


@pytest.mark.parametrize('action,file,old,new', [
    ('enable_cfl', 'getm.inp', b'.false.', b'.true.'),
    ('fix_sync_interval', 'output.yaml', b'sync_interval: 0', b'sync_interval: 1'),
    ('conservative_timestep', 'getm.inp', b'timestep = 10', b'timestep = 2'),
])
def test_repair_backs_up_and_preserves_format(diagnostics, action, file, old, new):
    app, ctx, case, _ = diagnostics
    original = (case / file).read_bytes()
    data = request_data(app, action)
    response = app.test_client().post('/api/run/repair', json=data)
    assert response.status_code == 200
    assert Path(response.get_json()['backup']).read_bytes() == original
    assert (case / file).read_bytes() == original.replace(old, new)
    assert response.get_json()['revision'] != data['revision']


def test_stale_revision_case_and_running_refuse_without_backup(diagnostics):
    app, ctx, case, _ = diagnostics
    data = request_data(app, 'enable_cfl')
    original = (case / 'getm.inp').read_bytes()
    for override in [{'revision': 'stale'}, {'case_path': str(case.parent)}, {'action': 'not_supported'}]:
        response = app.test_client().post('/api/run/repair', json={**data, **override})
        assert response.status_code in (400, 409)
    ctx.run_status = 'running'
    assert app.test_client().post('/api/run/repair', json=data).status_code == 409
    assert (case / 'getm.inp').read_bytes() == original
    assert not (case / 'backups').exists()


def test_config_change_invalidates_snapshot(diagnostics):
    app, ctx, case, _ = diagnostics
    data = request_data(app, 'enable_cfl')
    (case / 'output.yaml').write_text('changed')
    assert app.test_client().post('/api/run/repair', json=data).status_code == 409
    assert not (case / 'backups').exists()


def test_two_repairs_share_lock_and_only_one_snapshot_wins(diagnostics):
    app, ctx, case, _ = diagnostics
    data = request_data(app, 'enable_cfl')
    gate = threading.Barrier(2)
    statuses = []
    def repair():
        with app.test_client() as client:
            gate.wait()
            statuses.append(client.post('/api/run/repair', json=data).status_code)
    threads = [threading.Thread(target=repair) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert sorted(statuses) == [200, 409]
    assert len(list((case / 'backups').glob('*'))) == 1


def test_coverage_check_never_rewrites_forcing_and_supports_hour_units(diagnostics):
    app, ctx, case, module = diagnostics
    with nc.Dataset(case / 'meteo.nc', 'w') as ds:
        ds.createDimension('time', 2)
        time = ds.createVariable('time', 'f8', ('time',))
        time.units = 'hours since 2020-01-01 00:00:00'
        time[:] = [0, 24]
    original = (case / 'meteo.nc').read_bytes()
    for _ in range(2):
        data = app.test_client().get('/api/run/check').get_json()
        assert any('meteo.nc' in c['detail'] and '2020-01-02' in c['detail'] for c in data['checks'])
    assert (case / 'meteo.nc').read_bytes() == original
    assert not (case / 'backups').exists()


def test_stable_small_timestep_cannot_be_increased(diagnostics):
    app, ctx, case, module = diagnostics
    ctx.parse_getm_inp = lambda p: {'time': {'timestep': .5}}
    (case / 'getm.inp').write_text('&time\n timestep = 0.5\n/\n')
    original = (case / 'getm.inp').read_bytes()
    assert app.test_client().post('/api/run/repair', json=request_data(app, 'conservative_timestep')).status_code == 400
    assert (case / 'getm.inp').read_bytes() == original


def test_output_standard_uses_registered_case_sources(diagnostics):
    app, ctx, case, module = diagnostics
    response = app.test_client().post('/api/run/repair', json=request_data(app, 'standard_output'))
    assert response.status_code == 200
    text = (case / 'output.yaml').read_text()
    assert 'real_module/*' in text and 'source: *' not in text and 'sync_interval: 0' in text


def test_remove_unregistered_preserves_good_entry_metadata(diagnostics):
    app, ctx, case, module = diagnostics
    (case / 'output.yaml').write_text('output:\n   sync_interval: 1\n   variables:\n      - source: u\n        name: velocity\n      - source: temp\n        name: temperature\n      - source: v\n')
    response = app.test_client().post('/api/run/repair', json=request_data(app, 'remove_unregistered_sources'))
    assert response.status_code == 200
    text = (case / 'output.yaml').read_text()
    assert 'source: u' not in text and 'source: v' not in text
    assert 'source: temp\n        name: temperature' in text


@pytest.mark.parametrize('action,expected_sources', [
    ('standard_output', ['temp', 'salt', 'real_module/*']),
    ('remove_unregistered_sources', ['temp']),
    ('resolve_output_sources', ['resolved_u', 'resolved_temp']),
])
def test_output_repairs_preserve_legal_configuration_after_variables(diagnostics, action, expected_sources):
    app, ctx, case, _ = diagnostics
    path = case / 'output.yaml'
    suffix = ('   # preserve comment and following output settings\n   custom:\n'
              '      enabled: true\n      order: [first, second]\n'
              '      source_list:\n         - source: preserve_this_value\n')
    original = ('output:\n   time_unit: second\n   sync_interval: 1\n   variables:\n'
                '      - source: u\n        name: invalid\n'
                '      - source: temp\n        name: temperature\n' + suffix)
    path.write_text(original, encoding='utf-8')
    if action == 'resolve_output_sources':
        ctx._resolve_output_sources = lambda _path, sources, _context: ['resolved_' + source for source in sources]

    response = app.test_client().post('/api/run/repair', json=request_data(app, action))

    assert response.status_code == 200, response.get_json()
    repaired = path.read_text(encoding='utf-8')
    assert repaired.endswith(suffix)
    parsed = yaml.safe_load(repaired)
    assert parsed['output']['custom'] == {
        'enabled': True, 'order': ['first', 'second'],
        'source_list': [{'source': 'preserve_this_value'}],
    }
    assert [item['source'] for item in parsed['output']['variables']] == expected_sources
    if action == 'remove_unregistered_sources':
        assert parsed['output']['variables'][0]['name'] == 'temperature'


def test_output_rewrite_still_rejects_unlocatable_variable_list(diagnostics):
    _app, _ctx, _case, module = diagnostics
    malformed_lists = [
        ('output:\n   variables:\n      - source: temp\n'
         '      - other: ambiguous\n   custom: preserved\n'),
        ('output:\n   variables:\n      format: legacy\n'
         '         - source: temp\n   custom: preserved\n'),
    ]
    for text in malformed_lists:
        with pytest.raises(ValueError):
            module._source_entries(text)


def test_atomic_replace_failure_keeps_original_and_backup(diagnostics, monkeypatch):
    app, ctx, case, module = diagnostics
    data = request_data(app, 'enable_cfl')
    original = (case / 'getm.inp').read_bytes()
    def fail(*args):
        raise OSError('locked file')
    monkeypatch.setattr(module.os, 'replace', fail)
    response = app.test_client().post('/api/run/repair', json=data)
    assert response.status_code == 400
    assert (case / 'getm.inp').read_bytes() == original
    assert next((case / 'backups').glob('*')).read_bytes() == original
    assert not list(case.glob('*.tmp'))


def test_case_switch_during_staging_refuses_commit(diagnostics):
    app, ctx, case, module = diagnostics
    data = request_data(app, 'enable_cfl')
    original = (case / 'getm.inp').read_bytes()
    def switch_case(path):
        ctx.active_case_path = case.parent
        return {'time': {}}
    ctx.parse_getm_inp = switch_case
    assert app.test_client().post('/api/run/repair', json=data).status_code == 409
    assert (case / 'getm.inp').read_bytes() == original


def test_shorten_stop_preserves_forcing_file_and_requires_valid_period(diagnostics):
    app, ctx, case, module = diagnostics
    with nc.Dataset(case / 'meteo.nc', 'w') as ds:
        ds.createDimension('time', 2)
        tv = ds.createVariable('time', 'f8', ('time',))
        tv.units = 'days since 2020-01-01 00:00:00'
        tv[:] = [0, 2]
    original = (case / 'meteo.nc').read_bytes()
    data = request_data(app, 'shorten_stop_to_coverage')
    response = app.test_client().post('/api/run/repair', json=data)
    assert response.status_code == 200
    assert "stop = '2020-01-02 00:00:00'" in (case / 'getm.inp').read_text()
    assert (case / 'meteo.nc').read_bytes() == original


def test_invalid_time_coordinate_is_read_only_error(diagnostics):
    app, ctx, case, module = diagnostics
    with nc.Dataset(case / 'rivers.nc', 'w') as ds:
        ds.createDimension('time', 2)
        tv = ds.createVariable('time', 'f8', ('time',))
        tv.units = 'seconds since 2020-01-01 00:00:00'
        tv[:] = [10, 0]
    original = (case / 'rivers.nc').read_bytes()
    with pytest.raises(ValueError, match='rivers.nc'):
        module.inspect_forcing_coverage(case, ctx.parse_getm_inp(case / 'getm.inp'), ctx)
    assert (case / 'rivers.nc').read_bytes() == original
