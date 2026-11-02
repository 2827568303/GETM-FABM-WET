"""Saved initial conditions must survive the real create/build/rebuild routes."""
from pathlib import Path
import re
import shutil
import sys

import netCDF4 as nc
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import server


@pytest.fixture
def initial_client(tmp_path, monkeypatch):
    source_luoma = server.CASE_DIR / 'Lake Luoma'
    case_root = tmp_path / 'case-storage'
    luoma_fixture = case_root / 'Lake Luoma'
    luoma_fixture.mkdir(parents=True)
    for filename in ('fabm.yaml', 'gotmturb.nml'):
        shutil.copy2(source_luoma / filename, luoma_fixture / filename)
    with nc.Dataset(tmp_path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 3)
        ds.createDimension('y', 2)
        ds.createVariable('x', 'f8', ('x',))[:] = [500000, 500050, 500100]
        ds.createVariable('y', 'f8', ('y',))[:] = [3300000, 3300050]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[-10, 3, 5], [-10, 3, 5]]
        ds.createVariable('lonc', 'f8', ('y', 'x'))[:] = 117
        ds.createVariable('latc', 'f8', ('y', 'x'))[:] = 30
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    monkeypatch.setattr(server, 'active_case', 'Initial conditions rebuild test')
    monkeypatch.setattr(server, 'CASE_DIR', case_root)
    return server.app.test_client(), tmp_path


def build(client, eco=True):
    response = client.post('/api/case/build', json={
        'preset': 'eutrophic', 'start': '2020-01-01 00:00:00',
        'stop': '2020-01-01 00:20:00', 'timestep': 2, 'nlev': 6,
        'engines': {'eco': eco, 'fish': False, 'ghg': False},
    })
    assert response.status_code == 200, response.get_json()
    assert response.get_json()['success']


def test_build_falls_back_to_case_storage_luoma_templates(initial_client, monkeypatch):
    client, path = initial_client
    copied_sources = []
    copy2 = shutil.copy2
    def record_copy(source, destination, *args, **kwargs):
        copied_sources.append(Path(source).resolve())
        return copy2(source, destination, *args, **kwargs)
    monkeypatch.setattr(server.shutil, 'copy2', record_copy)
    build(client)
    expected = (server.CASE_DIR / 'Lake Luoma').resolve()
    assert expected / 'fabm.yaml' in copied_sources
    assert expected / 'gotmturb.nml' in copied_sources


def test_app_luoma_templates_precede_case_storage_templates(initial_client, tmp_path, monkeypatch):
    client, _ = initial_client
    app_luoma = tmp_path / 'app' / 'case' / 'Lake Luoma'
    app_luoma.mkdir(parents=True)
    case_luoma = server.CASE_DIR / 'Lake Luoma'
    for filename in ('fabm.yaml', 'gotmturb.nml'):
        shutil.copy2(case_luoma / filename, app_luoma / filename)
    monkeypatch.setattr(server, 'BASE_DIR', tmp_path / 'app')
    copied_sources = []
    copy2 = shutil.copy2
    def record_copy(source, destination, *args, **kwargs):
        copied_sources.append(Path(source).resolve())
        return copy2(source, destination, *args, **kwargs)
    monkeypatch.setattr(server.shutil, 'copy2', record_copy)
    build(client)
    assert app_luoma.resolve() / 'fabm.yaml' in copied_sources
    assert app_luoma.resolve() / 'gotmturb.nml' in copied_sources


def test_build_physics_only_writes_native_false(initial_client):
    client, path = initial_client
    build(client, eco=False)
    text = (path / 'getm.inp').read_text()
    assert 'fabm = .false.' in text
    assert "fabm = '.false.'" not in text


def test_prebuild_hydro_saved_reloaded_and_built(initial_client):
    client, path = initial_client
    saved = client.post('/api/case/init_conditions', json={
        'hydro': {'elev_const': 0.25, 'temp_const': 16.404}, 'trophic': 'eutrophic',
    })
    assert saved.get_json()['success']
    before = client.get('/api/case/init_conditions').get_json()['hydro']
    assert before['temp_const'] == 16.404
    assert before['elev_const'] == 0.25
    for _ in range(2):
        build(client)
        cfg = server.parse_getm_inp(path / 'getm.inp')
        assert cfg['temp']['temp_const'] == 16.404
        assert cfg['m2d']['elev_const'] == 0.25


def test_explicit_water_quality_and_macro_survive_rebuild(initial_client):
    client, path = initial_client
    build(client)
    saved = client.post('/api/case/init_conditions', json={
        'hydro': {'temp_const': 17.875},
        'water_quality': {'DOM.sDW': 6.404, 'POM.sDW': 7.404},
        'macrophytes': {'sD_max': 11.404}, 'trophic': 'eutrophic',
    })
    assert saved.get_json()['success']
    build(client)
    cfg = server.parse_getm_inp(path / 'getm.inp')
    assert cfg['temp']['temp_const'] == 17.875
    raw = yaml.safe_load((path / 'fabm.yaml').read_text(encoding='utf-8'))['instances']
    assert raw['DOM']['initialization']['sDW'] == 6.404
    assert raw['POM']['initialization']['sDW'] == 7.404
    with nc.Dataset(path / 'fabm_init.nc') as ds:
        assert ds['macrophytes_sD'][:].max() == pytest.approx(11.404)


def test_build_uses_captured_case_when_active_case_changes(initial_client, monkeypatch):
    client, path = initial_client
    client.post('/api/case/init_conditions', json={'hydro': {'temp_const': 16.404}})
    other = path / 'other-case'
    other.mkdir()
    (other / 'initial_conditions.json').write_text('{"hydro":{"temp_const":22.5}}')
    original = server._build_getm_inp

    def build_and_switch(*args, **kwargs):
        result = original(*args, **kwargs)
        monkeypatch.setattr(server, 'active_case_path', other)
        return result

    monkeypatch.setattr(server, '_build_getm_inp', build_and_switch)
    build(client)
    cfg = server.parse_getm_inp(path / 'getm.inp')
    assert cfg['temp']['temp_const'] == 16.404


@pytest.mark.parametrize('timestep',[.5,1.9060091,'0.5'])
def test_build_preserves_fractional_timestep(initial_client,timestep):
    client,path=initial_client
    response=client.post('/api/case/build',json={
        'preset':'mesotrophic','start':'2020-01-01 00:00:00',
        'stop':'2020-01-01 00:20:00','timestep':timestep,'nlev':6,
        'engines':{'eco':True,'fish':False,'ghg':False}})
    assert response.status_code==200,response.get_json()
    config=server.parse_getm_inp(path/'getm.inp')
    assert config['time']['timestep']==pytest.approx(float(timestep),rel=0,abs=1e-12)
    assert config['io_spec']['step_3d']>=1


def test_build_serializes_integral_output_interval_as_yaml_integer(initial_client):
    client, path = initial_client
    response = client.post('/api/case/build', json={
        'preset': 'mesotrophic', 'start': '2020-01-01 00:00:00',
        'stop': '2020-01-01 02:00:00', 'timestep': 5.0, 'nlev': 6,
        'engines': {'eco': True, 'fish': False, 'ghg': False},
    })
    assert response.status_code == 200, response.get_json()
    output_text = (path / 'output.yaml').read_text(encoding='utf-8')
    assert re.search(r'^\s*time_step:\s*360\s*$', output_text, re.MULTILINE)


def test_custom_preset_builds_safe_baseline_and_preserves_overrides(initial_client):
    client, path = initial_client
    saved = client.post('/api/case/init_conditions', json={
        'water_quality': {'DOM.sDW': 6.404, 'POM.sDW': 7.404},
    })
    assert saved.get_json()['success']
    response = client.post('/api/case/build', json={
        'preset': 'custom', 'start': '2020-01-01 00:00:00',
        'stop': '2020-01-01 00:20:00', 'timestep': 2, 'nlev': 6,
        'engines': {'eco': False, 'water_quality': True, 'fish': True, 'ghg': False},
    })
    assert response.status_code == 200, response.get_json()
    payload = response.get_json()
    assert payload['preset'] == 'custom'
    assert any('custom' in note.lower() and 'safe baseline' in note.lower() for note in payload['notes'])
    assert payload['engines'] == {'hydro': True, 'eco': False, 'fish': False, 'ghg': False}
    raw = yaml.safe_load((path / 'fabm.yaml').read_text(encoding='utf-8'))['instances']
    assert raw['DOM']['initialization']['sDW'] == 6.404
    assert raw['POM']['initialization']['sDW'] == 7.404
    assert raw['abiotic_water']['initialization']['sNH4W'] == server.TROPHIC_PRESETS['eutrophic']['sNH4W']
    assert server.parse_getm_inp(path / 'getm.inp')['getm_fabm']['fabm'] is True


def test_custom_preset_preserves_yaml_initialization_without_sidecar(initial_client):
    client, path = initial_client
    template = server.CASE_DIR / 'Lake Luoma' / 'fabm.yaml'
    raw = yaml.safe_load(template.read_text(encoding='utf-8'))
    raw['instances']['DOM']['initialization']['sDW'] = 6.404
    raw['instances']['POM']['initialization']['sDW'] = 7.404
    (path / 'fabm.yaml').write_text(yaml.safe_dump(raw, sort_keys=False), encoding='utf-8')
    assert not (path / server.INIT_COND_FILE).exists()
    assert client.get('/api/case/init_conditions').get_json()['trophic'] == 'custom'

    response = client.post('/api/case/build', json={
        'preset': 'custom', 'start': '2020-01-01 00:00:00',
        'stop': '2020-01-01 00:20:00', 'timestep': 2, 'nlev': 6,
        'engines': {'eco': True, 'water_quality': True, 'fish': False, 'ghg': False},
    })
    assert response.status_code == 200, response.get_json()
    rebuilt = yaml.safe_load((path / 'fabm.yaml').read_text(encoding='utf-8'))['instances']
    assert rebuilt['DOM']['initialization']['sDW'] == 6.404
    assert rebuilt['POM']['initialization']['sDW'] == 7.404


def test_unknown_build_preset_remains_rejected(initial_client):
    client, path = initial_client
    before = {p.name: p.read_bytes() for p in path.iterdir() if p.is_file()}
    response = client.post('/api/case/build', json={
        'preset': 'not-a-preset', 'start': '2020-01-01 00:00:00',
        'stop': '2020-01-01 00:20:00', 'timestep': 2, 'nlev': 6,
    })
    assert response.status_code == 400
    assert response.get_json()['error'] == '未知预设 not-a-preset'
    assert {p.name: p.read_bytes() for p in path.iterdir() if p.is_file()} == before


@pytest.mark.parametrize('timestep',[0,-.1,'bad',float('nan'),float('inf'),True,1201])
def test_invalid_build_timestep_returns_json_without_writing_inputs(initial_client,timestep):
    client,path=initial_client
    before={p.name:p.read_bytes() for p in path.iterdir() if p.is_file()}
    response=client.post('/api/case/build',json={
        'preset':'mesotrophic','start':'2020-01-01 00:00:00',
        'stop':'2020-01-01 00:20:00','timestep':timestep,'nlev':6,
        'engines':{'eco':True,'fish':False,'ghg':False}})
    assert response.status_code==400,response.get_json()
    assert response.get_json()['error']
    assert {p.name:p.read_bytes() for p in path.iterdir() if p.is_file()}==before
