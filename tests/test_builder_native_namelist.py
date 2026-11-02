"""The builder's untouched output must be accepted by a real Fortran reader."""
import os
from pathlib import Path
import re
import subprocess
import sys

import netCDF4 as nc
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'3DWET/app'))
import server


@pytest.fixture(scope='module')
def native_fabm_reader(tmp_path_factory):
    tool_bin = ROOT/'build/native-toolchain/ucrt64/bin'
    compiler = tool_bin/'gfortran.exe'
    if not compiler.exists():
        pytest.skip('Portable native Fortran compiler is unavailable')
    work = tmp_path_factory.mktemp('native-engine-reader')
    source = work/'reader.f90'
    source.write_text("""program reader
implicit none
logical :: fabm
namelist /getm_fabm/ fabm
open(10,file='getm.inp',status='old')
read(10,nml=getm_fabm)
print *, fabm
end program
""")
    env = dict(os.environ, PATH=str(tool_bin)+os.pathsep+os.environ['PATH'])
    exe = work/'reader.exe'
    subprocess.run([str(compiler), str(source), '-o', str(exe)], env=env, check=True, capture_output=True)
    return exe, env


@pytest.mark.parametrize('route', ['/api/config/engines', '/api/config/modules'])
@pytest.mark.parametrize('enabled', [False, True])
def test_engine_switch_keeps_native_logical_type(tmp_path, monkeypatch, route, enabled, native_fabm_reader):
    (tmp_path/'getm.inp').write_text('&getm_fabm\n fabm = .true.\n/\n')
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    monkeypatch.setattr(server, 'active_case', 'Engine switch probe')
    monkeypatch.setattr(server, 'MODULE_SELECTION_FILE', tmp_path/'selection.json')
    payload = {'eco': enabled}
    if route == '/api/config/modules' and not enabled:
        # eco is now the ecology-network toggle; disable water quality too to
        # exercise the master FABM switch's native logical serialization.
        payload['water_quality'] = False
    response = server.app.test_client().post(route, json=payload)
    assert response.status_code == 200, response.get_json()
    assert response.get_json()['success']
    assert server.parse_getm_inp(tmp_path/'getm.inp')['getm_fabm']['fabm'] is enabled
    assert not re.search(r"=\s*['\"]\.(?:true|false)\.['\"]", (tmp_path/'getm.inp').read_text(), re.I)
    exe, env = native_fabm_reader
    result = subprocess.run([str(exe)], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == ('T' if enabled else 'F')


def test_disabling_ecology_keeps_water_quality_and_fabm_master_enabled(tmp_path, monkeypatch):
    (tmp_path/'getm.inp').write_text('&getm_fabm\n fabm = .true.\n/\n')
    (tmp_path/'fabm.yaml').write_text(
        'instances:\n  algae:\n    model: wet/phytoplankton\n'
        '  nutrients:\n    model: wet/abiotic_water\n', encoding='utf-8')
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    monkeypatch.setattr(server, 'active_case', 'Independent modules probe')
    monkeypatch.setattr(server, 'MODULE_SELECTION_FILE', tmp_path/'selection.json')
    monkeypatch.setattr(server, 'toggle_ghg_modules', lambda *_args: (True, []))
    monkeypatch.setattr(server, 'parse_fabm_yaml', lambda *_args: {})

    response = server.app.test_client().post('/api/config/modules', json={'eco': False})
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body['success']
    assert body['selection']['eco'] is False
    assert body['selection']['water_quality'] is True
    assert server.parse_getm_inp(tmp_path/'getm.inp')['getm_fabm']['fabm'] is True
    active = server.yaml.safe_load((tmp_path/'fabm.yaml').read_text())['instances']
    assert set(active) == {'nutrients'}


def test_start_rejects_legacy_quoted_logicals_before_launch(tmp_path,monkeypatch):
    (tmp_path/'getm.inp').write_text("&param\n dryrun = '.false.'\n/\n")
    monkeypatch.setattr(server,'active_case_path',tmp_path)
    monkeypatch.setattr(server,'run_thread',None)
    monkeypatch.setattr(server,'run_status','idle')
    monkeypatch.setattr(server,'EXE_PATH',tmp_path/'absent.exe')
    response=server.app.test_client().post('/api/run/start',json={})
    assert response.status_code==400
    assert '逻辑值' in response.get_json()['error']


@pytest.mark.parametrize('has_forcing',[False,True])
def test_build_writes_native_logical_literals(tmp_path,has_forcing):
    with nc.Dataset(tmp_path/'bathymetry.nc','w') as ds:
        ds.createDimension('x',7);ds.createDimension('y',5)
    server._build_getm_inp(tmp_path,'Namelist Probe','2020-01-01 00:00:00',
                           '2020-01-01 00:20:00',2,has_forcing,has_forcing,6)
    tool_bin=ROOT/'build/native-toolchain/ucrt64/bin'
    compiler=tool_bin/'gfortran.exe'
    if not compiler.exists():pytest.skip('Portable native Fortran compiler is unavailable')
    source=tmp_path/'reader.f90'
    source.write_text('''program reader
implicit none
logical :: dryrun,parallel,hotstart,use_epoch,save_initial
integer :: runtype
character(len=256) :: runid,title
namelist /param/ dryrun,runid,title,parallel,runtype,hotstart,use_epoch,save_initial
open(10,file='getm.inp',status='old')
read(10,nml=param)
close(10)
if(dryrun.or.parallel.or.hotstart.or.use_epoch.or.save_initial) stop 3
if(runtype/=4) stop 4
print *, 'PASS native namelist'
end program
''')
    env=dict(os.environ,PATH=str(tool_bin)+os.pathsep+os.environ['PATH'])
    exe=tmp_path/'reader.exe'
    subprocess.run([str(compiler),str(source),'-o',str(exe)],env=env,check=True,capture_output=True)
    result=subprocess.run([str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stdout+result.stderr
    text=(tmp_path/'getm.inp').read_text()
    assert not re.search(r"=\s*['\"]\.(?:true|false)\.['\"]",text,re.I)
    config=server.parse_getm_inp(tmp_path/'getm.inp')
    assert config['meteo']['metforcing'] is has_forcing
    assert config['rivers']['river_method']==(2 if has_forcing else 0)
    assert config['domain']['ih']==7 and config['domain']['jh']==5
    # A 20 minute model must save multiple frames without a later settings save.
    assert config['io_spec']['step_2d']==30
    assert config['io_spec']['step_3d']==30


def test_saving_meteo_enables_forcing_without_rewriting_other_settings(tmp_path):
    path = tmp_path / 'getm.inp'
    original = ('&param\r\n title = \'Keep this case\'\r\n runtype = 4\r\n/\r\n'
                '&meteo\r\n metforcing = .false. ! intentional old setting\r\n wind_method = 2\r\n/\r\n')
    path.write_bytes(original.encode('utf-8'))
    server._enable_getm_meteo_forcing(path)
    updated = path.read_bytes().decode('utf-8')
    assert 'metforcing = .true. ! intentional old setting' in updated
    assert '&param\r\n title = \'Keep this case\'\r\n runtype = 4\r\n/' in updated
    assert 'wind_method = 2' in updated
    assert server.parse_getm_inp(path)['meteo']['metforcing'] is True
    assert not list(tmp_path.glob('.getm.inp.meteo-*.tmp'))


def test_measured_swr_mode_is_restored_from_forcing_provenance(tmp_path):
    with nc.Dataset(tmp_path/'bathymetry.nc','w') as ds:
        ds.createDimension('x',2); ds.createDimension('y',2)
    (tmp_path/'meteo_provenance.json').write_text(
        '{"shortwave_mode":"measured_swr"}', encoding='utf-8')
    server._build_getm_inp(tmp_path,'Measured SWR','2020-01-01 00:00:00',
                           '2020-01-01 00:20:00',2,True,False,2)
    config = server.parse_getm_inp(tmp_path/'getm.inp')
    assert config['meteo']['use_measured_swr'] is True
    (tmp_path/'meteo_provenance.json').write_text(
        '{"shortwave_mode":"cloud_calculated"}', encoding='utf-8')
    server._build_getm_inp(tmp_path,'Cloud SWR','2020-01-01 00:00:00',
                           '2020-01-01 00:20:00',2,True,False,2)
    assert server.parse_getm_inp(tmp_path/'getm.inp')['meteo'].get('use_measured_swr', False) is False
