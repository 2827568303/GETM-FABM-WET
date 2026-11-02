"""Regression checks for native calibration input isolation and result integrity."""
import sys
import os
import time
from pathlib import Path
from types import SimpleNamespace

import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'3DWET'/'app'))
import calibration
import server


def emit(path, *, bad=False, final=1200):
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 2), ('level', 1), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        coordinate = ds.createVariable('time', 'f8', ('time',))
        coordinate.units='seconds since 2020-01-01 00:00:00'
        coordinate[:]=[0,final]
        temp=ds.createVariable('temp','f8',('time','level','y','x'))
        temp[:]=np.nan if bad else 15.
    # An instantaneous fake solver can hit a Windows file-clock rounding edge
    # (observed mtime 0.24 microseconds before its start). Stamp after the write
    # using the same clock; keep production stale-output rejection strict.
    stamp=time.time_ns()
    os.utime(path,ns=(stamp,stamp))


@pytest.fixture
def model(tmp_path, monkeypatch):
    source=tmp_path/'source'; source.mkdir()
    (source/'fabm.yaml').write_text('instances: {}\n')
    (source/'getm.inp').write_text("&time\n start = '2020-01-01 00:00:00'\n stop = '2020-01-01 00:20:00'\n timestep = 2.\n/\n")
    with nc.Dataset(source/'bathymetry.nc','w') as ds:
        ds.createDimension('y',1); ds.createDimension('x',1)
        ds.createVariable('bathymetry','f8',('y','x'))[:]=2
    target=tmp_path/'trial'; target.mkdir()
    monkeypatch.setattr(calibration.tempfile,'mkdtemp',lambda **kw:str(target))
    monkeypatch.setattr(calibration,'_server_helpers',lambda *a,**kw:(
        str,lambda p:{'3d':str(p/'output.nc') if (p/'output.nc').exists() else None,'2d':None},
        lambda *a,**kw:{'times':['2020-01-01 00:20:00'],'values':[15.]},
        lambda:None,[dict(id='p',i=0,j=0,variables=['temp'])],{},lambda *a:None,'fake_solver'))
    def run(*a,**kw):
        emit(target/'output.nc')
        (target/'calib_run.log').write_text('getm: Completed on 2020-01-01\n')
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(calibration.subprocess,'run',run)
    return source,target,run


def test_calibration_copies_referenced_inputs_but_never_previous_outputs(model):
    source,target,_=model
    for folder in ('output','out','backups','cache'):
        (source/folder).mkdir(); (source/folder/'history.nc').write_bytes(b'old')
    emit(source/'old.3d.nc'); emit(source/'output.nc')
    (source/'model_run.log').write_text('old')
    (source/'inputs').mkdir(); (source/'inputs'/'custom-forcing.nc').write_bytes(b'needed')
    result=calibration.run_model_in_temp(source,[],keep_temp=True)
    assert result['success'],result
    assert (target/'inputs'/'custom-forcing.nc').read_bytes()==b'needed'
    assert not any((target/f).exists() for f in ('output','out','backups','cache','old.3d.nc','model_run.log'))


def test_calibration_missing_new_output_cannot_reuse_source_results(model,monkeypatch):
    source,target,_=model
    emit(source/'output.nc')
    monkeypatch.setattr(calibration.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0))
    result=calibration.run_model_in_temp(source,[],keep_temp=True)
    assert not result['success'],result


@pytest.mark.parametrize('failure',['nonzero','fatal','nan','early_stop'])
def test_calibration_rejects_bad_current_run_even_when_result_exists(model,monkeypatch,failure):
    source,target,run=model
    def broken(*a,**kw):
        result=run()
        if failure=='nonzero': result.returncode=1
        if failure=='fatal': (target/'calib_run.log').write_text('FATAL GETM ERROR\nSTOP 1\n')
        if failure=='nan': emit(target/'output.nc',bad=True)
        if failure=='early_stop': emit(target/'output.nc',final=60)
        return result
    monkeypatch.setattr(calibration.subprocess,'run',broken)
    result=calibration.run_model_in_temp(source,[],keep_temp=True)
    assert not result['success'],result
    assert result.get('error')


def test_calibration_stopped_job_keeps_stopped_status_after_worker_finishes(monkeypatch,tmp_path):
    monkeypatch.setattr(calibration,'_server_helpers',lambda *a,**kw:(None,None,None,None,[],{},None,None))
    job=calibration.CalibrationJob('stop','parsac',[],'rmse',2,tmp_path)
    class Engine:
        def calibrate(self,*a,**kw):
            job.stop()
            return dict(success=True,best_objective=0,best_params=[])
    monkeypatch.setattr(calibration,'ScipyEngine',Engine)
    job._run()
    assert job.status=='stopped'


def test_calibration_all_failed_trials_cannot_be_reported_completed(monkeypatch,tmp_path):
    monkeypatch.setattr(calibration,'_server_helpers',lambda *a,**kw:(None,None,None,None,
                        [dict(id='p',variables=['temp'])],{'p':{'temp':[dict(time='2020-01-01',value=1)]}},None,None))
    monkeypatch.setattr(calibration,'run_model_in_temp',lambda *a,**kw:dict(success=False,error='solver produced NaN'))
    job=calibration.CalibrationJob('bad','parsac',[dict(module='x',param='rate',min=1,max=2)],'rmse',2,tmp_path)
    job._run()
    assert job.status=='failed'
    assert not job.result['success']
    assert 'solver produced NaN' in job.error


def test_calibration_rejects_selected_point_without_observation_before_job(monkeypatch, tmp_path):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='p', variables=['temp'])], {}, None, None))
    with pytest.raises(ValueError, match='观测数据'):
        calibration.CalibrationJob('no-data', 'scipy',
                                   [dict(module='x', param='rate', min=1, max=2)],
                                   'rmse', 2, tmp_path)


def test_calibration_preflight_accepts_matching_legacy_observation(monkeypatch, tmp_path):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='p', variables=['temp'])],
                         {'p': {'temp': [dict(time='2020-01-01', value=1.0)]}}, None, None))
    job = calibration.CalibrationJob('legacy-data', 'scipy',
                                    [dict(module='x', param='rate', min=1, max=2)],
                                    'rmse', 2, tmp_path)
    assert job.point_ids == ['p']


@pytest.mark.parametrize('method', ['scipy', 'pest', 'parsac', 'bayesian', 'sensitivity'])
def test_calibration_reports_the_actual_engine_and_legacy_compatibility(monkeypatch, tmp_path, method):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [], {}, None, None))
    class Engine:
        def calibrate(self, *a, **kw):
            return dict(success=True, best_objective=0, best_params=[])
    monkeypatch.setattr(calibration, 'ScipyEngine', Engine)
    job = calibration.CalibrationJob('engine', method, [], 'rmse', 2, tmp_path)
    job._run()
    assert job.status == 'completed'
    assert job.to_dict()['engine'] == 'scipy-lbfgsb'
    if method == 'scipy':
        assert job.fallback is None
    else:
        assert method in job.fallback and 'L-BFGS-B' in job.fallback


def test_selected_points_are_isolated_in_trial_and_objective(monkeypatch, tmp_path):
    points = [dict(id='chosen', variables=['temp']), dict(id='ignored', variables=['temp'])]
    observations = {'chosen': {'temp': [1]}, 'ignored': {'temp': [999]}}
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, points, observations, None, None))
    job = calibration.CalibrationJob('selection', 'scipy', [], 'rmse', 2, tmp_path,
                                     point_ids=['chosen'])
    points[0]['variables'].append('mutated-after-start')
    observations['chosen']['temp'][0] = 500
    seen = []
    def trial(*a, **kw):
        assert kw['points_snapshot'] == [dict(id='chosen', variables=['temp'])]
        return dict(success=True, outputs={})
    def objective(*a, **kw):
        seen.append(kw)
        assert kw['data_snapshot'] == {'chosen': {'temp': [1]}}
        return 0
    class Engine:
        def calibrate(self, params, objective_fn, callback, **kw):
            return dict(success=True, best_objective=objective_fn([]), best_params=[])
    monkeypatch.setattr(calibration, 'run_model_in_temp', trial)
    monkeypatch.setattr(calibration, 'compute_objective', objective)
    monkeypatch.setattr(calibration, 'ScipyEngine', Engine)
    job._run()
    assert job.status == 'completed'
    assert len(seen) == 1
    assert job.to_dict()['point_ids'] == ['chosen']


def test_objective_scores_only_native_pairs_from_observation_snapshot(monkeypatch):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='P', variables=['temp'])], {}, None, None))
    outputs = {'P/temp': {'observation_pairs': [
        {'sim': 3.0, 'obs': 1.0}, {'sim': 2.0, 'obs': 2.0}], 'diagnostics': []}}
    score = calibration.compute_objective(
        outputs, points_snapshot=[dict(id='P', variables=['temp'])],
        observations_snapshot={'records': [{'point_id': 'P', 'variable': 'temp'}]},
        objective_name='rmse')
    assert score == pytest.approx(2 ** .5)


def test_objective_does_not_fall_back_to_legacy_data_when_native_pairs_missing(monkeypatch):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='P', variables=['temp'])],
                         {'P': {'temp': [{'time': '2020-01-01', 'value': 0}]}}, None, None))
    score = calibration.compute_objective(
        {'P/temp': {'times': ['2020-01-01'], 'values': [0]}},
        points_snapshot=[dict(id='P', variables=['temp'])],
        observations_snapshot={'records': [{'point_id': 'P', 'variable': 'temp'}]},
        objective_name='rmse')
    assert score >= 1e10


def test_calibration_job_freezes_case_observations_and_gap_policy(monkeypatch, tmp_path):
    from observation_store import ObservationStore
    points = [dict(id='P', variables=['temp'], lake_id='L', station_id='S',
                   spatial_mapping='verified', x_m=1, y_m=2, coordinate_crs='EPSG:25832')]
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, points, {}, None, None))
    ObservationStore(tmp_path.parent).save(tmp_path.name, {
        'version': 1, 'case_id': tmp_path.name, 'max_time_gap_hours': 2,
        'records': [{'point_id': 'P', 'variable': 'temp', 'value': 1,
                     'source_sha256': 'source-hash'}], 'manifest': [{'sha256': 'input-hash'}]})
    job = calibration.CalibrationJob('obs-snapshot', 'scipy', [], 'rmse', 2, tmp_path)
    assert job.max_time_gap_hours == 2
    assert job._observations_snapshot['records'][0]['source_sha256'] == 'source-hash'
    assert job.to_dict()['observation_manifest'][0]['sha256'] == 'input-hash'


def test_calibration_job_rejects_invalid_explicit_gap_for_official_observations(monkeypatch, tmp_path):
    from observation_store import ObservationStore
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='P', variables=['temp'])], {}, None, None))
    ObservationStore(tmp_path.parent).save(tmp_path.name, {
        'version': 1, 'case_id': tmp_path.name, 'max_time_gap_hours': None,
        'records': [{'point_id': 'P', 'variable': 'temp', 'value': 1}], 'manifest': []})
    with pytest.raises(ValueError, match='max_time_gap_hours'):
        calibration.CalibrationJob('obs-gap', 'scipy', [], 'rmse', 2, tmp_path)


def test_trial_pairs_imported_observations_using_native_model_adapter(model, monkeypatch):
    source, _, _ = model
    called = []
    monkeypatch.setattr(server, '_native_observation_model', lambda path, var, target: (
        called.append((var, target['id'])) or {
            'times': ['2020-01-01 00:00:00'], 'values': [[3.0]], 'center_depth': [[2.0]],
            'variable': var, 'unit': 'degC', 'lake_id': 'L', 'station_id': 'S',
            'point_id': 'p', 'spatial_mapping': 'verified'}))
    records = [{'point_id': 'p', 'lake_id': 'L', 'station_id': 'S', 'variable': 'temp',
                'time': '2020-01-01 00:00:00', 'depth_m': 2, 'unit': 'degC',
                'value': 1, 'quality': [], 'quality_flags': []}]
    result = calibration.run_model_in_temp(
        source, [], keep_temp=True, observations_snapshot={'records': records},
        max_time_gap_hours=1)
    assert result['success'], result
    assert called == [('temp', 'p')]
    pairs = result['outputs']['p/temp']['observation_pairs']
    assert len(pairs) == 1 and pairs[0]['obs'] == 1 and pairs[0]['sim'] == 3
    assert result['outputs']['p/temp']['downsampled'] is False


@pytest.mark.parametrize('selection', [[], ['unknown'], 'chosen', [1], ['chosen', 'chosen']])
def test_invalid_explicit_point_selection_is_rejected(monkeypatch, tmp_path, selection):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [dict(id='chosen')], {}, None, None))
    with pytest.raises(ValueError):
        calibration.CalibrationJob('bad-selection', 'scipy', [], 'rmse', 2, tmp_path,
                                   point_ids=selection)


def test_legitimate_stop_between_output_intervals_is_valid(model, monkeypatch):
    source, target, run = model
    (source/'getm.inp').write_text("&time\n start = '2020-01-01 00:00:00'\n stop = '2020-01-01 00:20:50'\n timestep = 2.\n/\n")
    (source/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n sync_interval: 1\n')
    result = calibration.run_model_in_temp(source, [], keep_temp=True)
    assert result['success'], result


@pytest.mark.parametrize('settings,final', [
    ('time_unit: second\n time_step: 60\n time_stop: 2020-01-01 00:10:00',600),
    ('time_unit: second\n time_step: 60\n time_start: 2020-01-01 00:01:10',1150),
    # type_file.first_index defaults to 0, including when save_initial=false.
    ('time_unit: dt\n time_step: 7',1190),
])
def test_configured_output_window_and_dt_are_valid(model,monkeypatch,settings,final):
    source,target,run=model
    (source/'output.yaml').write_text('output:\n '+settings+'\n variables:\n  - source: *\n')
    def finish(*args,**kw):
        result=run();emit(target/'output.nc',final=final);return result
    monkeypatch.setattr(calibration.subprocess,'run',finish)
    result=calibration.run_model_in_temp(source,[],keep_temp=True)
    assert result['success'],result


def test_fractional_complete_trial_preserves_actual_final_microseconds(model,monkeypatch):
    source,target,run=model
    (source/'getm.inp').write_text("&time\n start = '2020-01-01 00:00:00'\n stop = '2020-01-01 00:20:00'\n timestep = 1.9060091\n/\n")
    (source/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n')
    def finish(*args,**kw):
        result=run();emit(target/'output.nc',final=1200.785733);return result
    monkeypatch.setattr(calibration.subprocess,'run',finish)
    result=calibration.run_model_in_temp(source,[],keep_temp=True)
    assert result['success'],result
    output=result['output_health']['files'][0]
    assert output['final_time'] == output['scheduled_final_time'] == '2020-01-01T00:20:00.785733'
