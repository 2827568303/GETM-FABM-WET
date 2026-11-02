import sys
import threading
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from project_api import register_project_routes


@pytest.fixture
def studio(tmp_path):
    source = tmp_path / 'original'
    source.mkdir()
    (source / 'getm.inp').write_bytes(b"&time\r\n timestep = 60, ! seconds\r\n title = 'a!b'\r\n enabled = .true.\r\n/\r\n")
    ctx = SimpleNamespace(CASE_DIR=tmp_path / 'cases', active_case_path=source,
                          _NC_LOCK=threading.RLock(), run_status='idle',
                          cached_getm_config={}, parse_getm_inp=lambda p: {'updated': True})
    app = Flask(__name__)
    register_project_routes(app, ctx)
    return app.test_client(), ctx, source


def test_import_copy_and_provenance(studio):
    client, ctx, source = studio
    (source / 'bathymetry.nc').write_bytes(b'input')
    (source / 'lake.3d.nc').write_bytes(b'output')
    (source / 'output').mkdir()
    (source / 'output' / 'history.nc').write_bytes(b'output')
    response = client.post('/api/projects/import', json={'source_path': str(source), 'name': 'My lake'})
    assert response.status_code == 200
    data = response.get_json()
    target = Path(data['case_path'])
    assert target == ctx.CASE_DIR / 'My lake'
    assert (target / 'bathymetry.nc').read_bytes() == b'input'
    assert not (target / 'lake.3d.nc').exists()
    assert not (target / 'output').exists()
    assert (source / 'lake.3d.nc').exists()
    item = next(x for x in data['manifest']['files'] if x['path'] == 'getm.inp')
    assert item['source_sha256'] == hashlib.sha256((source / 'getm.inp').read_bytes()).hexdigest()
    assert item['source_sha256'] == item['copied_sha256']
    assert client.post('/api/projects/import', json={'source_path': str(source), 'name': 'My lake'}).status_code == 400


def test_import_preflight_maps_relative_paths_and_reports_missing_and_external(studio, tmp_path):
    client, ctx, source = studio
    (source / 'data').mkdir()
    (source / 'data' / 'initial.nc').write_bytes(b'initial')
    (source / 'meteo.csv').write_text('time,temp\n0,10\n')
    (source / 'getm.inp').write_text(
        "&hotstart\n inifile = 'data/initial.nc'\n missing_path = 'absent/restart.nc'\n"
        " escaping_path = '../outside/restart.nc'\n"
        " absolute_source_file = '" + str(source / 'data' / 'initial.nc').replace('\\', '/') + "'\n"
        " externalfile = '" + str(tmp_path / 'outside.nc').replace('\\', '\\\\') + "'\n/\n"
        "! logfile = 'ignored.log'\n")
    (source / 'config.json').write_text('{"meteo_file":"meteo.csv","archive_path":"' +
                                        str(tmp_path / 'outside.json').replace('\\', '\\\\') + '"}')
    (source / 'grid.yaml').write_text('grid_path: "data/initial.nc"\nmissing_file: absent/grid.nc\n')
    original = {p.name: p.read_bytes() for p in source.iterdir() if p.is_file()}

    response = client.post('/api/projects/import', json={'source_path': str(source), 'name': 'audited'})
    assert response.status_code == 200
    data = response.get_json()
    target = Path(data['case_path'])
    audit = data['manifest']['path_reference_audit']
    refs = {(ref['file'], ref['key']): ref for ref in audit['references']}
    assert refs[('getm.inp', 'inifile')]['status'] == 'copied'
    assert refs[('getm.inp', 'inifile')]['target_relative_path'] == 'data/initial.nc'
    assert 'target_path' not in refs[('getm.inp', 'inifile')]
    assert refs[('config.json', 'meteo_file')]['status'] == 'copied'
    assert refs[('grid.yaml', 'grid_path')]['status'] == 'copied'
    assert refs[('getm.inp', 'missing_path')]['status'] == 'missing'
    assert refs[('getm.inp', 'escaping_path')]['status'] == 'outside_project'
    assert refs[('getm.inp', 'absolute_source_file')]['status'] == 'absolute_source'
    assert 'target_relative_path' not in refs[('getm.inp', 'absolute_source_file')]
    assert refs[('grid.yaml', 'missing_file')]['status'] == 'missing'
    assert refs[('getm.inp', 'externalfile')]['status'] == 'absolute_external'
    assert refs[('config.json', 'archive_path')]['status'] == 'absolute_external'
    assert audit['counts'] == {'copied': 3, 'missing': 2, 'absolute_source': 1,
                               'absolute_external': 2, 'outside_project': 1}
    assert all((source / name).read_bytes() == content for name, content in original.items())
    assert (target / 'getm.inp').read_bytes() == original['getm.inp'], 'preflight never rewrites inputs'


def test_import_invalid_and_legacy_metadata(studio):
    client, ctx, source = studio
    assert client.post('/api/projects/import', json={'source_path': str(source), 'name': '../oops'}).status_code == 400
    (source / 'getm.inp').unlink()
    (source / 'project.json').write_text('{"name":"old","hydro":{"depth":10}}')
    response = client.post('/api/projects/import', json={'source_path': str(source), 'name': 'legacy'})
    assert response.status_code == 200
    assert response.get_json()['needs_preprocessing'] is True
    assert (ctx.CASE_DIR / 'legacy' / 'project.json').exists()


def test_editor_preserves_comments_crlf_and_backup(studio):
    client, ctx, source = studio
    original = (source / 'getm.inp').read_bytes()
    data = client.get('/api/physics/config?file=getm.inp').get_json()
    assert len(data['parameters']) == 3
    response = client.post('/api/physics/config', json={**data, 'changes': [{'group': 'time', 'key': 'timestep', 'value': '30'}]})
    assert response.status_code == 200
    assert (source / 'getm.inp').read_bytes() == original.replace(b'= 60,', b'= 30,')
    assert Path(response.get_json()['backup']).read_bytes() == original
    assert ctx.cached_getm_config == {'updated': True}
    assert client.post('/api/physics/config', json={**data, 'changes': []}).status_code == 409


def test_editor_guards_types_case_and_running(studio):
    client, ctx, source = studio
    data = client.get('/api/physics/config').get_json()
    for value in ['1\n/', 'nan', '1.5', True]:
        response = client.post('/api/physics/config', json={**data, 'changes': [{'group': 'time', 'key': 'timestep', 'value': value}]})
        assert response.status_code == 400
    assert client.get('/api/physics/config?file=../outside').status_code == 400
    assert client.post('/api/physics/config', json={**data, 'case_path': str(source.parent), 'changes': []}).status_code == 409
    ctx.run_status = 'running'
    assert client.post('/api/physics/config', json={**data, 'changes': []}).status_code == 409


def test_multiple_assignments_and_arrays_are_not_editable(studio):
    client, ctx, source = studio
    (source / 'getm.inp').write_text('&x\n a = 1, b = 2\n arr = 1, 2, 3\n okay = 1.0d-3 ! note\n/\n')
    data = client.get('/api/physics/config').get_json()
    assert [p['key'] for p in data['parameters']] == ['okay']
    assert data['uneditable_lines'] == 2


def test_import_excludes_private_files_and_alternative_artifact_names(studio):
    client, ctx, source = studio
    for name in ('api_key.json', 'parameters.backup.json', 'credentials.yaml', 'model.log', 'output.nc'):
        (source / name).write_text('private or generated')
    (source / 'out').mkdir()
    (source / 'out' / 'generated.nc').write_bytes(b'generated')
    response = client.post('/api/projects/import', json={'source_path': str(source), 'name': 'clean'})
    assert response.status_code == 200
    target = Path(response.get_json()['case_path'])
    assert sorted(p.name for p in target.iterdir()) == ['getm.inp', 'import_manifest.json']


def test_editor_detects_external_edit_and_handles_quoted_comment(studio):
    client, ctx, source = studio
    data = client.get('/api/physics/config').get_json()
    result = client.post('/api/physics/config', json={**data, 'changes': [
        {'group': 'time', 'key': 'title', 'value': "'x!y'"},
        {'group': 'time', 'key': 'enabled', 'value': '.false.'},
    ]})
    assert result.status_code == 200
    assert b"title = 'x!y'\r\n enabled = .false." in (source / 'getm.inp').read_bytes()
    updated = result.get_json()
    (source / 'getm.inp').write_bytes((source / 'getm.inp').read_bytes() + b'! changed externally\r\n')
    assert client.post('/api/physics/config', json={**updated, 'changes': []}).status_code == 409


def test_gotm_settings_and_invalid_requests(studio):
    client, ctx, source = studio
    (source / 'gotmturb.nml').write_bytes(b'&turbulence\r\n coeff = 1.0d-3, ! keep\r\n/\r\n')
    data = client.get('/api/physics/config?file=gotmturb.nml').get_json()
    response = client.post('/api/physics/config', json={**data, 'changes': [
        {'group': 'turbulence', 'key': 'coeff', 'value': '2.0d-3'}]})
    assert response.status_code == 200
    assert (source / 'gotmturb.nml').read_bytes() == b'&turbulence\r\n coeff = 2.0d-3, ! keep\r\n/\r\n'
    assert ctx.cached_getm_config == {}
    for body in ([], None, {'changes': 'wrong'}):
        assert client.post('/api/physics/config', json=body).status_code in (400, 409)


def test_import_does_not_follow_symlinks(studio):
    client, ctx, source = studio
    private = source.parent / 'private.json'
    private.write_text('private')
    try:
        (source / 'linked.json').symlink_to(private)
    except OSError:
        pytest.skip('Creating symlinks requires Windows developer mode or administrator rights')
    response = client.post('/api/projects/import', json={'source_path': str(source), 'name': 'links'})
    assert response.status_code == 200
    assert not (ctx.CASE_DIR / 'links' / 'linked.json').exists()
