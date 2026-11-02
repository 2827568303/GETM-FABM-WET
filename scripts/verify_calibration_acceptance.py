"""Real native Theoretical lake two-parameter optimization, never synthetic objectives.

The observations are from a separate reference solver run with changed parameters.
This proves engineering behavior with synthetic observations, not field accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

import netCDF4 as nc
import numpy as np
import yaml

from verify_builtin_cases import (ROOT, prepare_model, wait_for_service, run_case,
                                  isolated_launcher_environment)
from verify_external_workflow import APIProbe


def require(condition, message):
    """Keep acceptance failures actionable while preserving strict checks."""
    if not condition:
        raise AssertionError(message)


def record_failure(report, phase, error):
    report['failure_phase'] = phase
    report['error_type'] = type(error).__name__
    report['error_message'] = str(error)
    report['error'] = f'{type(error).__name__}: {error}'


MAX_SCIPY_SIMULATIONS = 500


def scipy_simulation_budget(iterations, params):
    """Bound finite-difference evaluations from iterations and candidate count."""
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise ValueError('SciPy iterations must be a positive integer')
    if not isinstance(params, (list, tuple)) or not params:
        raise ValueError('SciPy calibration requires at least one parameter candidate')
    return min(MAX_SCIPY_SIMULATIONS, iterations * (2 * len(params) + 1))


def complete_calibration_history(status):
    history = status['result']['history']
    require(status['history_len'] == len(history) == status['result']['n_iterations'],
            'Calibration history length disagrees with result metadata')
    public = status['history']
    require(len(public) == min(50, len(history)),
            'Public calibration history has an unexpected length')
    for actual, displayed in zip(history[-50:], public):
        require(all(actual[key] == displayed[key] for key in ('iteration','params','objective')),
                'Public history does not match the complete evaluation tail')
    return history


def validate_abc_evidence(result, history, params, baseline, population_size=4, populations=2, budget=80):
    """Check actual accepted distributions, not improvement over a random draw."""
    import pyabc
    require(np.isfinite(baseline) and baseline > 0, 'Fixed midpoint baseline must be informative')
    distances = np.asarray([row['objective'] for row in history], dtype=float)
    require(len(history) > 1 and np.isfinite(distances).all() and (distances >= 0).all() and (distances < 1e10).all(),
            'Calibration history must contain multiple finite, valid objective evaluations')
    require(result['n_iterations'] == len(history) <= budget,
            'Actual evaluation count disagrees with configured budget')
    require(np.isclose(result['best_objective'], distances.min(), rtol=1e-12, atol=1e-14),
            'Reported best objective is not the minimum actual evaluation')
    require(any(row['params'] == result['best_params'] and row['objective'] == result['best_objective']
                for row in history), 'Applied best parameters do not correspond to an actual best trial')
    database = Path(result['database_path'])
    require(database.is_file(), 'ABC evidence database is missing')
    stored = pyabc.History('sqlite:///' + database.resolve().as_posix())
    require(stored.n_populations == result['n_populations'] == populations,
            'ABC database population count disagrees with API result')
    require(stored.total_nr_simulations == len(history),
            'Database and actual evaluation history disagree')
    rows = stored.get_all_populations(); rows = rows[rows['t'] >= 0]
    require(len(rows) == populations and len(result['populations']) == populations,
            'ABC database/API does not contain the required populations')
    previous = float('inf'); evidence = []
    for (_, row), public in zip(rows.iterrows(), result['populations']):
        t = int(row['t']); epsilon = float(row['epsilon'])
        require(np.isfinite(epsilon) and 0 <= epsilon <= previous, 'ABC epsilon did not tighten')
        require(int(row['particles']) == population_size and public['population'] == t,
                f'Population {t} particle count or index disagrees with API')
        require(public['samples'] == int(row['samples']) and public['epsilon'] == epsilon,
                f'Population {t} samples/epsilon disagree with database')
        accepted = stored.get_weighted_distances(t=t)
        frame, weights = stored.get_distribution(m=0, t=t)
        weights = np.asarray(weights, dtype=float)
        require(len(frame) == len(weights) == len(accepted) == population_size,
                f'Population {t} accepted distribution does not contain {population_size} particles')
        require(np.isfinite(weights).all() and (weights > 0).all() and abs(weights.sum()-1) < 1e-10,
                f'Population {t} particle weights must be positive, finite, and normalized')
        accepted_distances = np.asarray(accepted['distance'], dtype=float)
        require(np.isfinite(accepted_distances).all() and (accepted_distances >= 0).all(),
                f'Population {t} accepted distances must be finite and nonnegative')
        require((accepted_distances <= epsilon + 1e-12).all(),
                f'Population {t} particle exceeds its acceptance epsilon')
        for k, param in enumerate(params):
            values = np.asarray(frame['p'+str(k)], dtype=float)
            require(np.isfinite(values).all() and (values >= param['min']).all() and (values <= param['max']).all(),
                    f'Population {t} parameter p{k} is outside its configured bounds')
        # pyabc's tidy pivot drops equal distance/weight rows before joining
        # parameters. Distinct accepted particles can legitimately share both.
        extended = stored.get_population_extended(m=0, t=t, tidy=False)
        particles = extended.groupby('particle_id')
        require(len(particles) == population_size,
                f'Population {t} raw database rows contain {len(particles)} distinct accepted particles; expected {population_size}')
        for _, particle in particles:
            distances_for_particle = particle['distance'].unique()
            require(len(distances_for_particle) == 1,
                    f'Population {t} contains a particle with inconsistent distances')
            parameters = particle[['par_name', 'par_val']].drop_duplicates()
            require(set(parameters['par_name']) == {'p'+str(k) for k in range(len(params))},
                    f'Population {t} particle parameter names do not match the configured parameters')
            require(len(parameters) == len(params), 'Particle has inconsistent parameter values')
            by_name = parameters.set_index('par_name')['par_val']
            values = tuple(float(by_name['p'+str(k)]) for k in range(len(params)))
            require(any(np.allclose(values, [p['value'] for p in trial['params']], rtol=1e-12, atol=1e-14)
                        and np.isclose(float(distances_for_particle[0]), trial['objective'], rtol=1e-12, atol=1e-14)
                        for trial in history), 'Accepted particle does not match an actual trial')
        evidence.append(dict(population=t, particles=len(frame), epsilon=epsilon,
                             weighted_distance=float(np.average(accepted_distances, weights=accepted['w'])),
                             effective_sample_size=float(1/np.sum(weights**2))))
        previous = epsilon
    frame, weights = stored.get_distribution(m=0, t=stored.max_t)
    posterior = result['posterior']
    require(len(posterior) == population_size, 'API posterior has an unexpected particle count')
    expected = sorted((tuple(float(row['p'+str(k)]) for k in range(len(params))),float(w))
                      for (_,row),w in zip(frame.iterrows(),weights))
    actual = []
    for particle in posterior:
        require([(p['module'],p['param']) for p in particle['params']] == [(p['module'],p['param']) for p in params],
                'API posterior parameter identities do not match configured parameters')
        actual.append((tuple(p['value'] for p in particle['params']),particle['weight']))
    for (p,w),(q,v) in zip(expected,sorted(actual)):
        require(np.allclose(p,q,rtol=1e-12,atol=1e-14) and np.isclose(w,v,rtol=1e-12,atol=1e-14),
                'API posterior differs from native-trial database')
    require(evidence[-1]['weighted_distance'] < baseline,
            'Final posterior did not improve on fixed midpoint baseline')
    return dict(fixed_midpoint_baseline=baseline, populations=evidence, database_matches_api=True,
                actual_model_evaluations=len(history))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--model-source',type=Path,default=ROOT/'3DWET')
    parser.add_argument('--case',default='Theoretical lake')
    parser.add_argument('--launcher',type=Path,default=ROOT/'3DWET/app/launcher.py')
    parser.add_argument('--method',choices=['scipy','pyabc'],default='scipy')
    parser.add_argument('--timeout',type=float,default=600)
    args=parser.parse_args();work=args.work.resolve()
    if work.exists():raise SystemExit('Use a fresh verification directory')
    prepare_model(work,[args.case],args.model_source,keep_defaults=True)
    case=work/'3DWET/case'/args.case
    original=(case/'fabm.yaml').read_bytes()
    environment,model_root,state_root=isolated_launcher_environment(work)
    environment['MPLBACKEND']='Agg'
    # Frozen verification must not borrow the developer Python installation.
    if args.launcher.suffix.lower()=='.exe':
        for name in ('PYTHONPATH','VIRTUAL_ENV'):environment.pop(name,None)
        environment['PYTHONHOME']=str(work/'no-development-python')
    command=([str(args.launcher)] if args.launcher.suffix.lower()=='.exe'
             else [sys.executable,str(args.launcher)])+['--web','--no-open','--port','0']
    stream=(work/'service.log').open('w',encoding='utf-8')
    process=subprocess.Popen(command,env=environment,stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT)
    report={'passed':False,'method':args.method,'scope':'Actual native solver, synthetic observations; not scientific validation or a complete five-workflow round.'}
    report['source_case']=str((args.model_source/'case'/args.case).resolve())
    report['solver_sha256']=hashlib.sha256((work/'3DWET/bin/getm_cartesian.exe').read_bytes()).hexdigest()
    probe=None;job=None;phase='service_startup'
    try:
        url=wait_for_service(work,process,timeout=120,state_root=state_root,model_root=model_root);opener=build_opener(ProxyHandler({}));probe=APIProbe(opener,url)
        phase='case_setup'
        probe.call('/api/case/load',{'case_name':case.name})
        params=[dict(module='diatoms',param='cMuMax',min=1.2,max=3.6),
                dict(module='POM',param='kDMinW',min=.0005,max=.0035)]
        for param,value in zip(params,[3.2,.003]):
            probe.call('/api/config/fabm/param',dict(module=param['module'],param=param['param'],value=value))
        phase='reference_run'
        report['reference_run']=run_case(opener,url,case.name,case,args.timeout,verify_features=False)
        require(report['reference_run']['passed'], f"Reference run failed: {report['reference_run']}")
        phase='reference_output_validation'
        with nc.Dataset(case/'bathymetry.nc') as grid:
            cells=np.argwhere(np.ma.filled(grid['bathymetry'][:]>0,False));j,i=map(int,cells[len(cells)//2])
        with nc.Dataset(case/'output/output.nc') as ds:
            variables=['diatoms_sDW','POM_sDW']
            require(all(v in ds.variables for v in variables),
                    f"Reference output is missing calibration variables; found {[v for v in ds.variables if v.startswith(('diatoms_','POM_'))]}")
            decoded=nc.num2date(ds['time'][:],ds['time'].units)
            series={v:np.asarray(ds[v][:,-1,j,i],float) for v in variables}
            require(all(np.isfinite(a).all() for a in series.values()),
                    'Reference output contains non-finite calibration observations')
        point=probe.call('/api/calibration/points',dict(name='Independent reference parameters',i=i,j=j,variables=variables))['point']
        for variable,values in series.items():
            observations=[dict(time=t.strftime('%Y-%m-%d %H:%M:%S'),value=float(value)) for t,value in zip(decoded,values)]
            probe.call('/api/calibration/data',dict(point_id=point['id'],variable=variable,values=observations))
        if args.method == 'pyabc':
            # Define and run the baseline before any random ABC draw. A lucky
            # first draw is not an optimization starting point for ABC-SMC.
            for param in params:
                probe.call('/api/config/fabm/param',dict(module=param['module'],param=param['param'],value=(param['min']+param['max'])/2))
            phase='midpoint_baseline_run'
            report['baseline_run']=run_case(opener,url,case.name,case,args.timeout,verify_features=False)
            require(report['baseline_run']['passed'], f"Fixed midpoint baseline run failed: {report['baseline_run']}")
            with nc.Dataset(case/'output/output.nc') as ds:
                mse=[float(np.mean(((np.asarray(ds[v][:,-1,j,i],float)-series[v])/max(float(np.std(series[v])),1e-5))**2)) for v in variables]
            report['fixed_midpoint_baseline']=float(np.sqrt(np.mean(mse)))
        phase='calibration_setup'
        (case/'fabm.yaml').write_bytes(original)
        probe.call('/api/case/load',{'case_name':case.name})
        before=hashlib.sha256((case/'fabm.yaml').read_bytes()).hexdigest()
        body=dict(method=args.method,iterations=10 if args.method=='scipy' else 2,objective='rmse',params=params,point_ids=[point['id']],
                  objective_weights=[dict(point_id=point['id'],variable=v,weight=1,scale=max(float(np.std(series[v])),1e-5)) for v in variables])
        if args.method=='scipy':body['max_simulations']=scipy_simulation_budget(body['iterations'],params)
        else:body.update(population_size=4,max_simulations=80,minimum_epsilon=0)
        phase='calibration_run'
        start=time.monotonic();job=probe.call('/api/calibration/auto/start',body)['job_id']
        while time.monotonic()-start<args.timeout:
            status=probe.call('/api/calibration/auto/status?'+urlencode(dict(job_id=job)))
            report.update(status=status,elapsed_seconds=time.monotonic()-start,phase=phase)
            (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            if status['status']!='running':break
            time.sleep(1)
        phase='history_validation'
        require(status['status']=='completed', f"Calibration job did not complete: {status}")
        result=status['result'];history=complete_calibration_history(status)
        require(len(history)>1 and result['success'], 'Calibration result must report success with multiple evaluations')
        require(hashlib.sha256((case/'fabm.yaml').read_bytes()).hexdigest()==before,
                'Calibration trials changed user parameters before apply')
        phase='optimizer_validation'
        if args.method=='scipy':
            evaluation_budget=scipy_simulation_budget(body['iterations'],params)
            require(result['max_evaluations']==evaluation_budget, f"Unexpected scipy evaluation budget: {result}")
            require(result['n_iterations']==len(history)<=evaluation_budget, f"Unexpected scipy iteration count: {result}")
            require(history[0]['objective']>0 and result['best_objective']<history[0]['objective'],
                    'Scipy calibration did not improve on its initial evaluation')
            require(status['engine']=='scipy-lbfgsb', f"Unexpected scipy engine: {status['engine']}")
            require(report['elapsed_seconds']<300,'Specified two-parameter performance exceeded five minutes')
        else:
            require(status['engine']=='pyabc-abcsmc', f"Unexpected ABC engine: {status['engine']}")
            phase='abc_evidence_validation'
            report['abc_evidence']=validate_abc_evidence(result,history,params,report['fixed_midpoint_baseline'])
        phase='apply_validation'
        report['apply']=probe.call('/api/calibration/auto/apply',dict(job_id=job))
        saved=yaml.safe_load((case/'fabm.yaml').read_text(encoding='utf-8'))['instances']
        require(all(saved[p['module']]['parameters'][p['param']]==p['value'] for p in report['apply']['applied']),
                'Applied calibration values do not match the saved case YAML')
        report['passed']=True
        report['phase']='complete'
    except Exception as error:
        record_failure(report, phase, error)
    finally:
        if probe:
            if job:
                try:probe.call('/api/calibration/auto/stop',dict(job_id=job))
                except Exception:pass
            report['api_calls']=probe.calls
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=30)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        stream.close()
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({key:report[key] for key in ('passed','method','elapsed_seconds','error') if key in report},ensure_ascii=False),flush=True)
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
