"""Result cleanup only touches temporary fixture cases, never model cases."""
import importlib.util
from pathlib import Path
import threading
import os
import pytest
from flask import Flask

MODULE = Path(__file__).resolve().parents[1] / '3DWET/app/result_files.py'

@pytest.fixture
def setup(tmp_path):
    spec = importlib.util.spec_from_file_location('result_files', MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = Flask(__name__)
    ctx = dict(case_path=tmp_path, busy=False, lock=threading.RLock())
    module.register_result_file_routes(app, lambda: ctx)
    return tmp_path, app.test_client(), ctx, module

def put(case, name, data=b'abc'):
    p = case / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p

def inventory(client):
    response = client.get('/api/results/files')
    assert response.status_code == 200
    return response.get_json()

def cleanup(client, paths, revision):
    return client.post('/api/results/files/cleanup', json=dict(paths=paths, revision=revision))

def test_inventory_exact_locations_and_input_protection(setup):
    case, client, _, _ = setup
    for name in ['output.nc', 'output/lake.3d.nc', 'model_run.log', 'output/run_20261011/output.nc',
                 'output/meteo.3d.nc', 'output/bathymetry.2d.nc', 'output/initial.3d.nc',
                 'input/output.nc', 'output/arbitrary.txt', 'output/unknown/output.nc']:
        put(case, name)
    result = inventory(client)
    assert {f['relative_path'] for f in result['files']} == {
        'output.nc', 'output/lake.3d.nc', 'model_run.log', 'output/run_20261011/output.nc'}
    assert result['output_path'] == str(case / 'output')
    assert all(Path(f['absolute_path']).is_absolute() for f in result['files'])

def test_cleanup_revision_busy_and_all_prevalidation(setup):
    case, client, ctx, _ = setup
    file = put(case, 'output.nc')
    rev = inventory(client)['revision']
    ctx['busy'] = True
    assert cleanup(client, ['output.nc'], rev).status_code == 409
    ctx['busy'] = False
    assert cleanup(client, ['output.nc', '../output.nc'], rev).status_code == 400
    assert file.exists()
    file.write_bytes(b'changed')
    assert cleanup(client, ['output.nc'], rev).status_code == 409
    assert file.exists()

def test_cleanup_restore_and_explicit_empty(setup):
    case, client, _, _ = setup
    file = put(case, 'output/output.nc')
    response = cleanup(client, ['output/output.nc'], inventory(client)['revision'])
    assert response.status_code == 200
    assert not file.exists()
    trash = inventory(client)['trash']
    assert trash['count'] == 1 and trash['bytes'] == 3
    assert client.post('/api/results/files/restore', json={}).status_code == 200
    assert file.read_bytes() == b'abc'
    cleanup(client, ['output/output.nc'], inventory(client)['revision'])
    rev = inventory(client)['trash']['revision']
    assert client.post('/api/results/files/empty-trash', json={'revision': 'stale'}).status_code == 409
    assert client.post('/api/results/files/empty-trash', json={'revision': rev}).status_code == 200
    assert inventory(client)['trash']['count'] == 0

def test_restore_conflict_preserves_all_trashed_files(setup):
    case, client, _, _ = setup
    put(case, 'output.nc'); put(case, 'restart.nc')
    cleanup(client, ['output.nc', 'restart.nc'], inventory(client)['revision'])
    put(case, 'restart.nc', b'new')
    assert client.post('/api/results/files/restore', json={}).status_code == 409
    assert not (case / 'output.nc').exists()
    assert inventory(client)['trash']['count'] == 2

def test_duplicates_only_byte_identical_keep_newest(setup):
    case, client, _, _ = setup
    older = put(case, 'output.nc', b'abc')
    newer = put(case, 'output/output.nc', b'abc')
    put(case, 'output/lake.3d.nc', b'abd')
    os.utime(older, (100, 100)); os.utime(newer, (200, 200))
    data = inventory(client)
    assert all(f['duplicate_group'] is None for f in data['files'])
    scan = client.post('/api/results/files/duplicates', json={'revision': data['revision']}).get_json()
    assert scan['duplicate_paths'] == ['output.nc']
    assert scan['groups'][0]['keep'] == 'output/output.nc'

def test_duplicate_scan_does_not_wait_for_shared_netcdf_lock_but_keeps_busy_gate(setup):
    case, client, ctx, _ = setup
    older = put(case, 'output.nc', b'abc')
    newer = put(case, 'output/output.nc', b'abc')
    os.utime(older, (100, 100)); os.utime(newer, (200, 200))

    class NetCDFLockUnavailable:
        def __enter__(self):
            raise RuntimeError('shared NetCDF lock is held')
        def __exit__(self, *args):
            return False

    revision = inventory(client)['revision']
    ctx['lock'] = NetCDFLockUnavailable()

    response = client.post('/api/results/files/duplicates', json={'revision': revision})
    assert response.status_code == 200
    assert response.get_json()['duplicate_paths'] == ['output.nc']

    ctx['busy'] = True
    response = client.post('/api/results/files/duplicates', json={'revision': revision})
    assert response.status_code == 409

def test_symlink_and_replaced_inventory_rejected(setup):
    case, client, _, _ = setup
    real = put(case, 'output.nc')
    rev = inventory(client)['revision']
    target = put(case, 'input.nc', b'keep')
    real.unlink()
    try:
        real.symlink_to(target)
    except OSError:
        pytest.skip('Creating symlinks requires OS privilege')
    assert not inventory(client)['files']
    assert cleanup(client, ['output.nc'], rev).status_code == 409
    assert target.read_bytes() == b'keep'

def test_trash_symlink_does_not_escape_case(setup):
    case, client, _, _ = setup
    outside = case.parent / (case.name + '-outside')
    outside.mkdir()
    sentinel = put(outside, 'sentinel.txt')
    try:
        (case / '.studio-trash').symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip('Creating symlinks requires OS privilege')
    put(case, 'output.nc')
    assert cleanup(client, ['output.nc'], inventory(client)['revision']).status_code == 400
    assert sentinel.exists() and (case / 'output.nc').exists()

def test_same_output_in_new_case_cannot_reuse_old_revision(setup):
    case, client, ctx, _ = setup
    put(case, 'output.nc')
    rev = inventory(client)['revision']
    second = case / 'second-case'
    other = put(second, 'output.nc')
    first_stat = (case / 'output.nc').stat()
    os.utime(other, ns=(first_stat.st_atime_ns, first_stat.st_mtime_ns))
    ctx['case_path'] = second
    assert cleanup(client, ['output.nc'], rev).status_code == 409
    assert other.exists()

def test_reparse_attribute_rejected_without_symlink_privilege(setup, monkeypatch):
    case, client, _, module = setup
    target = put(case, 'output.nc')
    original = Path.lstat
    class Reparse:
        st_mode = 0o100644
        st_file_attributes = 0x400
    def attributes(path):
        if path == target:
            return Reparse()
        return original(path)
    monkeypatch.setattr(Path, 'lstat', attributes)
    assert inventory(client)['files'] == []
    assert target.read_bytes() == b'abc'

def test_changed_file_between_validation_and_move_rolls_back(setup, monkeypatch):
    case, client, _, module = setup
    first = put(case, 'output.nc')
    second = put(case, 'restart.nc')
    revision = inventory(client)['revision']
    original = module._write_manifest
    def change_after_prevalidation(directory, data):
        original(directory, data)
        second.write_bytes(b'concurrent change')
    monkeypatch.setattr(module, '_write_manifest', change_after_prevalidation)
    assert cleanup(client, ['output.nc', 'restart.nc'], revision).status_code == 409
    assert first.read_bytes() == b'abc'
    assert second.read_bytes() == b'concurrent change'
    assert inventory(client)['trash']['count'] == 0

def test_trash_manifest_traversal_never_restored_or_deleted(setup):
    import json
    case, client, _, _ = setup
    put(case, 'output.nc')
    cleanup(client, ['output.nc'], inventory(client)['revision'])
    manifest_path = next((case / '.studio-trash').glob('*/manifest.json'))
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['files'][0]['relative_path'] = '../../input.nc'
    manifest_path.write_text(json.dumps(data), encoding='utf-8')
    sentinel = put(case, 'input.nc')
    assert client.post('/api/results/files/restore', json={}).status_code == 400
    assert client.post('/api/results/files/empty-trash', json={'revision': 'anything'}).status_code == 400
    assert sentinel.read_bytes() == b'abc'

def test_hardlinked_outputs_across_cases_do_not_share_revision(setup):
    case, client, ctx, _ = setup
    file = put(case, 'output.nc')
    second = case / 'second-case'
    second.mkdir()
    os.link(file, second / 'output.nc')
    revision = inventory(client)['revision']
    ctx['case_path'] = second
    assert cleanup(client, ['output.nc'], revision).status_code == 409
    assert (second / 'output.nc').exists()
