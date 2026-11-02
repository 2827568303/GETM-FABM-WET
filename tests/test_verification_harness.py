"""Guard against integration-verifier false successes using tiny actual NetCDF files."""
import importlib.util
import ast
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'verify_builtin_cases.py'
spec = importlib.util.spec_from_file_location('verification_harness', SOURCE)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
sys.path.insert(0, str(SOURCE.parent))


def make_case(path, end=1200, masked=False, bad=False):
    path.mkdir(exist_ok=True)
    with nc.Dataset(path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('y', 2)
        ds.createDimension('x', 3)
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[-10, 2, 3], [-10, 2, 3]]
    archive = path / 'output'
    archive.mkdir()
    with nc.Dataset(archive / 'output.nc', 'w') as ds:
        for name, size in [('time', 3), ('z', 2), ('y', 2), ('x', 3)]:
            ds.createDimension(name, size)
        t = ds.createVariable('time', 'f8', ('time',))
        t.units = 'seconds since 2020-01-01 00:00:00'
        t[:] = [0, 600, end]
        for name in ['temp', 'hn', 'D', 'z']:
            v = ds.createVariable(name, 'f8', ('time', 'z', 'y', 'x'), fill_value=-9999.)
            a = np.ones((3, 2, 2, 3))
            a[..., 0] = -9999.
            if masked and name == 'temp':
                a[..., 1:] = -9999.
            if bad and name == 'temp':
                a[0, 0, 0, 1] = np.nan
            v[:] = a


def test_archived_outputs_are_discovered_and_required(tmp_path):
    with pytest.raises(ValueError, match='output'):
        harness.validate_case_outputs(tmp_path, datetime(2020, 1, 1, 0, 20))
    make_case(tmp_path)
    report = harness.validate_case_outputs(tmp_path, datetime(2020, 1, 1, 0, 20))
    assert report['files']['output/output.nc']['final_time'] == '2020-01-01 00:20:00'


@pytest.mark.parametrize('kwargs', [{'end': 600}, {'masked': True}, {'bad': True}])
def test_incomplete_or_invalid_wet_values_fail(tmp_path, kwargs):
    make_case(tmp_path, **kwargs)
    with pytest.raises(ValueError):
        harness.validate_case_outputs(tmp_path, datetime(2020, 1, 1, 0, 20))


def test_patch_uses_case_start_and_sufficient_duration(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    original = "&time\n start = '2022-03-04 06:00:00'\n stop = '2023-01-01 00:00:00'\n timestep = 60\n/\n&m2d\n MM = 480\n/\n&io\n step_2d = 1\n step_3d = 1\n/\n"
    (source / 'getm.inp').write_text(original)
    target = tmp_path / 'copy'
    harness.patch_case(source, target, duration_seconds=1200)
    assert "2022-03-04 06:20:00" in (target / 'getm.inp').read_text()
    assert (source / 'getm.inp').read_text() == original


def test_case_failures_do_not_skip_remaining_cases():
    called = []

    def runner(name):
        called.append(name)
        if name == 'bad':
            raise RuntimeError('broken')
        return {'case': name, 'passed': True}

    results = harness.run_all_cases(['bad', 'good'], runner)
    assert called == ['bad', 'good']
    assert [r['passed'] for r in results] == [False, True]
    assert 'broken' in results[0]['error']


def test_external_source_data_is_reproducible_and_seeded(tmp_path):
    from verify_external_workflow import generate_external_data
    a = generate_external_data(tmp_path / 'a', seed=42)
    b = generate_external_data(tmp_path / 'b', seed=42)
    c = generate_external_data(tmp_path / 'c', seed=43)
    assert a['sha256'] == b['sha256']
    assert a['sha256']['depth.csv'] != c['sha256']['depth.csv']
    assert a['sha256']['meteo.csv'] != c['sha256']['meteo.csv']
    assert 'not observations' in a['description']


def test_route_inventory_includes_import_repair_results_and_network():
    from verify_external_workflow import route_inventory
    inventory = route_inventory(SOURCE.parent.parent / '3DWET' / 'app')
    assert ('POST', '/api/projects/import') in inventory
    assert ('POST', '/api/run/repair') in inventory
    assert ('GET', '/api/results/3d_surface') in inventory
    assert ('POST', '/api/ecology/network') in inventory


def test_keep_defaults_is_exact_copy(tmp_path):
    source = tmp_path / 'original'
    source.mkdir()
    inp = b'&time\r\n timestep = 2\r\n/\r\n'
    output = b'output:\n   time_unit: second\n   time_step: 60\n'
    (source / 'getm.inp').write_bytes(inp)
    (source / 'output.yaml').write_bytes(output)
    target = tmp_path / 'copy'
    harness.patch_case(source, target, keep_defaults=True)
    assert (target / 'getm.inp').read_bytes() == inp
    assert (target / 'output.yaml').read_bytes() == output


def test_wait_for_service_reads_model_scoped_state_registry(tmp_path,monkeypatch):
    model_root=tmp_path/'external'/'3DWET'
    state_root=tmp_path/'case-state'
    identity=os.path.normcase(str(model_root.resolve()))
    expected_key=hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]
    registry=state_root/'.studio-runtime'/'models'/expected_key/'service.json'
    registry.parent.mkdir(parents=True)
    record={'url':'http://127.0.0.1:45123','instance_id':'instance-1',
            'model_root':str(model_root.resolve())}
    registry.write_text(json.dumps(record),encoding='utf-8')

    class Response:
        def __enter__(self):return self
        def __exit__(self,*_args):return False
        def read(self):return json.dumps({'ready':True,'instance_id':'instance-1'}).encode()

    class Opener:
        def open(self,url,timeout):
            assert url=='http://127.0.0.1:45123/api/system/health'
            assert timeout==1
            return Response()

    monkeypatch.setattr(harness,'build_opener',lambda *_args:Opener())
    process=type('Process',(),{'poll':lambda _self:None,'returncode':None})()
    assert harness.model_scoped_registry_path(state_root,model_root)==registry
    assert harness.wait_for_service(tmp_path/'external',process,state_root=state_root,
                                    model_root=model_root,timeout=1)==record['url']


def test_external_launcher_storage_is_scoped_to_work_tree(tmp_path):
    from verify_external_workflow import isolated_launcher_environment
    work=tmp_path/'external'
    env,model_root,state_root=isolated_launcher_environment(work,{
        'WET_CASE_DIR':r'D:\global\cases','WET_CASE_STATE_DIR':r'D:\global\state'})
    assert Path(env['WET_CASE_DIR'])==(work/'case-storage').resolve()
    assert Path(env['WET_CASE_STATE_DIR'])==state_root==(work/'case-state').resolve()
    assert model_root==(work/'3DWET').resolve()


def test_all_verifier_launchers_share_isolated_case_and_state_roots(tmp_path):
    from verify_builtin_cases import isolated_launcher_environment
    work=tmp_path/'feature-attempt'
    env,model_root,state_root=isolated_launcher_environment(work,{
        'WET_MODEL_ROOT':r'D:\global\model','WET_CASE_DIR':r'D:\global\cases',
        'WET_CASE_STATE_DIR':r'D:\global\state'})
    assert model_root==(work/'3DWET').resolve()
    assert Path(env['WET_CASE_DIR'])==(work/'case-storage').resolve()
    assert Path(env['WET_CASE_STATE_DIR'])==state_root==(work/'case-state').resolve()


@pytest.mark.parametrize('filename',[
    'verify_builtin_cases.py','verify_feature_matrix.py','verify_results_experience.py',
    'verify_calibration_acceptance.py','verify_restart_acceptance.py',
])
def test_workflow_verifiers_use_isolated_roots_for_service_lookup(filename):
    scripts=SOURCE.parent
    tree=ast.parse((scripts/filename).read_text(encoding='utf-8'))
    wait_calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)
                and isinstance(node.func,ast.Name) and node.func.id=='wait_for_service']
    assert wait_calls, f'{filename} must wait for its local service'
    for call in wait_calls:
        keywords={item.arg for item in call.keywords}
        assert {'state_root','model_root'}<=keywords, f'{filename} must resolve its state-root-scoped service registry'
    assert any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
               and node.func.id=='isolated_launcher_environment' for node in ast.walk(tree)), filename


def test_preprocess_save_path_is_authoritative_case_storage_not_model_root(tmp_path):
    from verify_external_workflow import case_path_from_bathymetry_save
    work=tmp_path/'external'
    case_storage=work/'case-storage'/'External Seed Lake'
    bathymetry=case_storage/'bathymetry.nc'
    bathymetry.parent.mkdir(parents=True)
    bathymetry.write_bytes(b'netcdf')
    model_root=work/'3DWET'
    wrong_case=model_root/'case'/'External Seed Lake'
    assert case_path_from_bathymetry_save({'success':True,'path':str(bathymetry)})==case_storage.resolve()
    assert case_path_from_bathymetry_save({'success':True,'path':str(bathymetry)})!=wrong_case.resolve()
