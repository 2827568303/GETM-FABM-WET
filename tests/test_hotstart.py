"""Native GETM restart files, rather than unsupported hotstart_file namelists."""
import sys
from pathlib import Path
import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'3DWET/app'))
from hotstart import prepare_restart, restart_settings


@pytest.fixture
def case(tmp_path):
    with nc.Dataset(tmp_path/'bathymetry.nc','w') as ds:
        for name,n in [('x',3),('y',2)]:
            ds.createDimension(name,n)
            ds.createVariable(name,'f8',(name,))[:]=np.arange(n)*100
        ds.createVariable('bathymetry','f8',('y','x'))[:]=5
    with nc.Dataset(tmp_path/'restart.out','w') as ds:
        for name,n in [('xax',3),('yax',2),('zax',3)]:
            ds.createDimension(name,n)
            ds.createVariable(name,'f8',(name,))[:]=np.arange(n)*(100 if name!='zax' else 1)
        for name,value in [('julianday',2458850),('secondsofday',600),('timestep',2),('loop',300)]:
            ds.createVariable(name,'f8')[:]=value
        for name in ['z','U','V']:
            ds.createVariable(name,'f8',('yax','xax'))[:]=0
        ds.createVariable('T','f8',('zax','yax','xax'))[:]=15
    config={'param':{'runtype':4,'hotstart_file':'old.nc'},'m3d':{'M':2},'domain':{'kdum':2},
            'time':{'start':'2020-01-01 00:00:00','stop':'2020-01-01 00:20:00'},
            'io_spec':{}}
    return tmp_path,config


def test_checkpoint_installed_where_native_solver_reads(case):
    path,config=case
    info=prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
    assert (path/'restart.in').read_bytes()==(path/'restart.out').read_bytes()
    assert config['param']['hotstart'] is True and 'hotstart_file' not in config['param']
    assert config['time']['start']=='2020-01-01 00:10:00'
    assert config['io_spec']['hotout(1)']==0
    assert config['io_spec']['hotin_fmt']==2
    assert info['time']==config['time']['start']
    assert restart_settings(path,config)['file']=='restart.out'


@pytest.mark.parametrize('filename',['missing.out','bathymetry.nc','../restart.out'])
def test_invalid_checkpoint_never_changes_configuration(case,filename):
    path,config=case
    import copy
    before=copy.deepcopy(config)
    with pytest.raises(ValueError):prepare_restart(path,config,enabled=True,filename=filename,save=True)
    assert config==before and not (path/'restart.in').exists()


def test_checkpoint_after_stop_rejected(case):
    path,config=case;config['time']['stop']='2020-01-01 00:05:00'
    with pytest.raises(ValueError,match='结束|stop'):
        prepare_restart(path,config,enabled=True,filename='restart.out',save=True)


def test_wrong_vertical_grid_rejected(case):
    path,config=case;config['domain']['kdum']=4
    with pytest.raises(ValueError,match='网格|grid'):
        prepare_restart(path,config,enabled=True,filename='restart.out',save=True)


def test_vertical_layers_are_independent_of_time_splitting(case):
    path,config=case;config['m3d']['M']=4
    prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
    assert (path/'restart.in').exists()


def test_cold_run_can_save_checkpoint_without_input(case):
    path,config=case
    prepare_restart(path,config,enabled=False,filename='',save=True)
    assert config['param']['hotstart'] is False
    assert 'hotstart_file' not in config['param']
    assert config['io_spec']['hotout(1)']==0


def test_ecology_restored_from_checkpoint_and_cold_mode_can_be_restored(case):
    path,config=case
    (path/'getm_fabm.inp').write_text('&getm_fabm_nml\n fabm_init_method = 2,\n/\n')
    with nc.Dataset(path/'restart.out','a') as ds:
        ds.createVariable('fabm_pel','f8',('zax','yax','xax'))[:]=2
    prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
    assert 'fabm_init_method = 0,' in (path/'getm_fabm.inp').read_text()
    prepare_restart(path,config,enabled=False,filename='',save=True)
    assert 'fabm_init_method = 2,' in (path/'getm_fabm.inp').read_text()


def test_legacy_phytoplankton_checkpoint_rejected_before_mutation(case):
    import copy
    path,config=case
    (path/'getm_fabm.inp').write_text('&getm_fabm_nml\n fabm_init_method = 2,\n/\n')
    (path/'fabm.yaml').write_text('instances:\n  cyanobacteria:\n    model: wet/phytoplankton\n')
    with nc.Dataset(path/'restart.out','a') as ds:
        ds.createVariable('fabm_pel','f8',('zax','yax','xax'))[:]=2
    original=(path/'getm_fabm.inp').read_bytes();before=copy.deepcopy(config)
    with pytest.raises(ValueError,match='历史|history'):
        prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
    assert config==before and (path/'getm_fabm.inp').read_bytes()==original
    assert not (path/'restart.in').exists()


@pytest.mark.parametrize('corruption',['none','nan','missing','oldest','version','timebase','unwritten','partial'])
def test_temporal_checkpoint_schema_checked_before_staging(case,corruption):
    path,config=case
    (path/'getm_fabm.inp').write_text('&getm_fabm_nml\n fabm_init_method = 2,\n/\n')
    (path/'fabm.yaml').write_text('instances:\n  cyanobacteria:\n    model: wet/phytoplankton\n')
    with nc.Dataset(path/'restart.out','a') as ds:
        ds.createVariable('fabm_pel','f8',('zax','yax','xax'))[:]=2
        ds.fabm_memory_version=2 if corruption!='version' else 9
        ds.fabm_memory_count=1
        ds.fabm_diagnostic_memory_count=0
        ds.fabm_memory_timebase='GETM Julian-day seconds' if corruption!='timebase' else 'year seconds'
        ds.createDimension('levels',2);ds.createDimension('slots',27)
        prefix='fabm_memory_0001'
        hist=ds.createVariable(prefix+'_history','f8',('slots','levels','yax','xax'))
        if corruption!='unwritten':hist[:]=0
        hist.expression='cyanobacteria_meanpar';hist.kind=1;hist.n=24;hist.period=86400.;hist.expression_missing_value=0.
        if corruption=='nan':hist[0,0,0,0]=np.nan
        if corruption=='partial':hist[0,0,0,0]=nc.default_fillvals['f8']
        for suffix,value in [('last',212444640600.),('next',212444644200.),('oldest',1),('valid',0)]:
            if corruption=='missing' and suffix=='next':continue
            ds.createVariable(prefix+'_'+suffix,'f8',('yax','xax'))[:]=value
        if corruption=='oldest':ds[prefix+'_oldest'][:]=0
    if corruption=='none':
        info=prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
        assert info['temporal_memory_count']==1
    else:
        with pytest.raises(ValueError,match='历史|history'):
            prepare_restart(path,config,enabled=True,filename='restart.out',save=True)
        assert not (path/'restart.in').exists()
