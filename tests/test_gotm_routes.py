import hashlib
import os
import sys
import threading
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))
import server
from gotm_working_copy import create_working_copy


def fixture_case(path, executable=True):
    path.mkdir(parents=True, exist_ok=True)
    (path / 'gotm.yaml').write_text('time:\n  start: 2000-01-01 00:00:00\n  stop: 2000-01-02 00:00:00\n  dt: 3600\n', encoding='utf-8')
    (path / 'fabm.yaml').write_text('instances: {}\n', encoding='utf-8')
    (path / 'input.dat').write_text('forcing\n', encoding='utf-8')
    if executable:
        (path / 'gotm_release.exe').write_bytes(b'MZfixture exe')
    with nc.Dataset(path / 'output.nc', 'w') as ds:
        ds.createDimension('time', 2); ds.createDimension('z', 2)
        ds.createDimension('lat', 1); ds.createDimension('lon', 1)
        t = ds.createVariable('time', 'f8', ('time',)); t.units='days since 2000-01-01 00:00:00'; t[:]=[0,1]
        ds.comment='GOTM native'
        for name, vals in [('h',[-10,-2]),('z',[-8,-1]),('temp',[10,9])]:
            var=ds.createVariable(name,'f8',('time','z','lat','lon'))
            var.units='m' if name in ('h','z') else 'degree_Celsius'
            var[:]=np.array(vals)[None,:,None,None].repeat(2,axis=0)


def configured_server(monkeypatch, path):
    monkeypatch.setattr(server, 'CASE_DIR', path.parent / 'cases')
    monkeypatch.setattr(server, 'EXTERNAL_CASES_FILE', path.parent / 'external.json')
    server.CASE_DIR.mkdir(exist_ok=True)
    return server.CASE_DIR


def test_save_as_gotm_marks_working_copy_and_keeps_reference_byte_identical(tmp_path, monkeypatch):
    ref=tmp_path/'reference'; fixture_case(ref)
    case_root=configured_server(monkeypatch, ref)
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ref.iterdir() if p.is_file()}
    response=server.app.test_client().post('/api/case/save_as',json={
        'source_path':str(ref),'dest_path':str(case_root/'copy'),'include_results':True})
    assert response.status_code==200,response.get_json()
    rows=server.app.test_client().get('/api/cases').get_json()
    copy=next(row for row in rows if row['path']==str(case_root/'copy'))
    assert copy['case_type']=='gotm_working_copy' and copy['model_dimension']=='single_column'
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ref.iterdir() if p.is_file()}
    assert before==after


def test_save_as_rejects_gotm_without_explicit_results(tmp_path, monkeypatch):
    ref=tmp_path/'reference'; fixture_case(ref); configured_server(monkeypatch, ref)
    response=server.app.test_client().post('/api/case/save_as',json={
        'source_path':str(ref),'dest_path':str(tmp_path/'copy'),'include_results':False})
    assert response.status_code==400 and '必须包含' in response.get_json()['error']


def test_read_only_reference_cannot_start_and_working_copy_uses_local_release(tmp_path, monkeypatch):
    ref=tmp_path/'reference'; fixture_case(ref)
    client=server.app.test_client()
    assert client.post('/api/case/open',json={'path':str(ref)}).status_code==200
    assert client.post('/api/run/start',json={}).status_code==403
    copy=tmp_path/'copy'; copy.mkdir(); create_working_copy(ref,copy,server._GOTM_MANIFEST_KEY)
    loaded=client.post('/api/case/open',json={'path':str(copy)}).get_json()
    assert loaded['case_type']=='gotm_working_copy' and loaded['model_dimension']=='single_column'
    assert loaded['native_column_variables'] and loaded['has_gotm_output']
    assert loaded['has_2d_output'] is False and loaded['has_3d_output'] is False
    preflight=client.get('/api/run/check').get_json()
    assert preflight['ok'] and preflight['model_dimension']=='single_column'
    spawned=[]
    class Thread:
        def __init__(self,**kwargs): spawned.append(kwargs)
        def start(self): pass
    monkeypatch.setattr(threading,'Thread',Thread)
    result=client.post('/api/run/start',json={})
    if os.name != 'nt':
        assert result.status_code==400, result.get_json()
        assert 'Windows' in result.get_json()['error']
        assert spawned == []
    else:
        assert result.status_code==200,result.get_json()
        assert spawned[0]['args']==(copy,copy/'gotm_release.exe')
    server.run_status='idle'; server.run_thread=None; server.run_process=None; server.run_case_path=None


def test_missing_copy_executable_is_rejected_explicitly(tmp_path, monkeypatch):
    ref=tmp_path/'reference'; fixture_case(ref)
    copy=tmp_path/'copy'; copy.mkdir(); create_working_copy(ref,copy,server._GOTM_MANIFEST_KEY)
    (copy/'gotm_release.exe').unlink()
    client=server.app.test_client(); client.post('/api/case/open',json={'path':str(copy)})
    response=client.post('/api/run/start',json={})
    assert response.status_code==400 and 'gotm_release.exe' in response.get_json()['error']





