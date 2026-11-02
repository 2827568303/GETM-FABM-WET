"""Verify remaining Studio features against an isolated copy of real native output.

The required --source-case must be an already verified short native case. All
mutations occur in a fresh --work directory. Synthetic observations test plumbing,
not predictive accuracy. OS folder/browser launch routes are deliberately omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import urlencode
from urllib.request import build_opener, ProxyHandler

import netCDF4 as nc
import numpy as np
import yaml

from verify_builtin_cases import ROOT, wait_for_service, isolated_launcher_environment
from verify_external_workflow import APIProbe, coverage_report, exercise_repair


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_preprocess_help(help_info):
    """Accept the supported boundary geometry labels exposed by the API."""
    geometry = help_info.get('boundary', {}).get('geometry')
    supported_boundaries = {'Polygon', 'MultiPolygon', 'Polygon or MultiPolygon'}
    require(geometry in supported_boundaries and
            help_info.get('bathymetry_point', {}).get('geometry') == 'Point',
            'Preprocess help metadata incorrect')
    return True


def calibration_start_payload(config, iterations=2, point_ids=None):
    """Build a valid small auto-start request for only supplied observation points."""
    params=config.get('parameters') if isinstance(config,dict) else None
    if not isinstance(params,list) or not params:
        raise ValueError('Calibration config must contain at least one parameter candidate')
    if isinstance(iterations,bool) or not isinstance(iterations,int) or iterations<1:
        raise ValueError('Calibration iterations must be a positive integer')
    payload=dict(method='parsac',params=params,iterations=iterations,objective='rmse',
                 max_simulations=max(iterations,len(params)))
    if point_ids is not None:
        if not isinstance(point_ids,(list,tuple)) or not point_ids:
            raise ValueError('Calibration point_ids must be a non-empty list when supplied')
        payload['point_ids']=list(point_ids)
    return payload


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-case', required=True, type=Path)
    parser.add_argument('--work', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=900)
    parser.add_argument('--launcher', type=Path, default=ROOT/'3DWET/app/launcher.py')
    parser.add_argument('--solver', type=Path,
                        help='Copy this solver into the isolated tree and record its hash')
    args = parser.parse_args()
    work, source = args.work.resolve(), args.source_case.resolve()
    require(not work.exists(), '--work must be fresh; this verifier never deletes existing work')
    require((source/'getm.inp').is_file() and (source/'output'/'output.nc').is_file(), 'Source requires native output')
    work.mkdir(parents=True)
    model = work/'3DWET'
    model.mkdir()
    shutil.copytree(ROOT/'3DWET'/'bin', model/'bin')
    if args.solver:
        require(args.solver.is_file(), 'Candidate solver does not exist')
        shutil.copy2(args.solver, model/'bin/getm_cartesian.exe')
    shutil.copytree(ROOT/'3DWET'/'model_builder'/'templates',model/'model_builder'/'templates')
    case = model/'case'/'Feature Lake'
    shutil.copytree(source, case, ignore=shutil.ignore_patterns('backups', '*.log'))
    # Calibration starts from input-only copy: no result can be mistaken for a
    # newly computed objective. The source 20-minute, 2-second timing is retained.
    calibration_case = model/'case'/'Calibration Lake'
    shutil.copytree(source, calibration_case, ignore=shutil.ignore_patterns(
        'output', 'out', 'backups', '*.log', '*.2d.nc', '*.3d.nc', 'output.nc'))
    env,model_root,state_root = isolated_launcher_environment(work)
    stdout = (work/'launcher.stdout.log').open('w', encoding='utf-8')
    stderr = (work/'launcher.stderr.log').open('w', encoding='utf-8')
    launcher = args.launcher.resolve()
    command = ([sys.executable, str(launcher)] if launcher.suffix == '.py' else [str(launcher)])
    process = subprocess.Popen(command + ['--web', '--no-open', '--port', '0'],
                               cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    report = dict(passed=False, source_case=str(source), work=str(work), features={},
        scope='Native short-run feature integration with synthetic observations; not scientific accuracy, annual stability, or complete browser UX validation.')
    report['solver_sha256'] = digest(model/'bin/getm_cartesian.exe')
    probe = None

    def check(name, fn):
        started = time.monotonic()
        try:
            details = fn()
            report['features'][name] = dict(status='passed', seconds=round(time.monotonic()-started, 3), details=details)
        except Exception as error:
            report['features'][name] = dict(status='failed', seconds=round(time.monotonic()-started, 3), error=f'{type(error).__name__}: {error}')
        (work/'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(name, report['features'][name]['status'], flush=True)

    try:
        url = wait_for_service(work, process, timeout=180,
                               state_root=state_root, model_root=model_root)
        probe = APIProbe(build_opener(ProxyHandler({})), url)
        probe.call('/api/case/load', dict(case_name=case.name))
        with nc.Dataset(case/'bathymetry.nc') as ds:
            wet = np.ma.filled(ds['bathymetry'][:] > 0, False)
        cells = np.argwhere(wet)
        j, i = map(int, cells[len(cells)//2])
        j2, i2 = map(int, cells[len(cells)//2+1])

        def inventory():
            listed = probe.call('/api/cases')
            require(any(c['name'] == case.name for c in listed), 'Copied case absent')
            files = probe.call('/api/case/inputs')['files']
            require(all(x['exists'] for x in files), 'Expected inputs missing')
            require(all(x['size_bytes'] > 0 for x in files), 'Empty input')
            listing = probe.call('/api/system/list_dir?'+urlencode(dict(path=str(model/'case'))))
            require(listing, 'Directory listing empty')
            return dict(inputs=len(files), cases=len(listed), directory_listing=listing)
        check('case_inventory_directory', inventory)

        def save_roundtrip():
            exported = work/'exports'/'Saved renamed lake'
            original = digest(case/'getm.inp')
            result = probe.call('/api/case/save_as', dict(source_path=str(case), dest_path=str(exported), include_results=False))
            require(result['n_files'] > 10 and digest(exported/'getm.inp') == original, 'Save-as lost model input')
            require(not (exported/'output'/'output.nc').exists(), 'Save-as included excluded output')
            opened = probe.call('/api/case/open', dict(path=str(exported)))
            require(opened.get('success'), 'Saved case failed opening')
            imported = probe.call('/api/projects/import', dict(source_path=str(exported), name='Roundtrip import'))
            target = Path(imported['case_path'])
            require(not imported['needs_preprocessing'] and digest(target/'getm.inp') == original, 'Project roundtrip changed inputs')
            entries = imported['manifest']['files']
            require(entries and all(e['source_sha256'] == e['copied_sha256'] for e in entries), 'Import hashes disagree')
            rejection = probe.call('/api/projects/import', dict(source_path=str(exported), name='Roundtrip import'), expected=400)
            probe.call('/api/case/delete', dict(path=str(target)))
            probe.call('/api/case/delete', dict(path=str(exported)))
            require(not target.exists() and not exported.exists(), 'Delete did not remove created cases')
            probe.call('/api/case/load', dict(case_name=case.name))
            return dict(manifest_files=len(entries), input_sha256=original, duplicate_rejected=rejection, created_cases_deleted=True)
        check('case_save_as_open_project_import_delete_roundtrip', save_roundtrip)

        def points():
            point = probe.call('/api/calibration/points', dict(name='Synthetic station', i=i, j=j, variables=['temp']))['point']
            state = probe.call('/api/grid/editor')
            def edit(action, expected=200, **extra):
                nonlocal state
                result = probe.call('/api/grid/edit', dict(case_path=state['case_path'], revision=state['revision'], action=action, **extra), expected=expected)
                if expected == 200: state=result
                return result
            edit('point', cells=[[i,j]], name='Linked station', kind='monitor', calibration_id=point['id'])
            identifier = state['points'][-1]['id']
            edit('point', cells=[[i2,j2]], name='Moved station', kind='source', point_id=identifier)
            require(state['points'][-1]['i'] == i2+1, 'Point drag coordinate mismatch')
            edit('undo'); require(state['points'][-1]['name'] == 'Linked station', 'Undo failed')
            edit('redo'); require(state['points'][-1]['name'] == 'Moved station', 'Redo failed')
            edit('save'); require(Path(state['backup']).is_dir(), 'Grid backup missing')
            stored = json.loads((case/'lake_points.json').read_text())['points'][-1]
            require((stored['i'], stored['j']) == (i2+1,j2+1), 'Saved point coordinates wrong')
            actual = probe.call('/api/calibration/points')
            mapped = next(p for p in actual if p['id'] == point['id'])
            require((mapped['i'],mapped['j']) == (i2,j2), 'Calibration mapping did not follow saved point')
            landj, landi = map(int,np.argwhere(~wet)[0])
            edit('point', cells=[[landi,landj]], name='Illegal land', expected=400)
            edit('point_delete', point_id=identifier); edit('save'); edit('reload')
            require(not any(p['id'] == identifier for p in state['points']), 'Point deletion not persisted')
            probe.call('/api/calibration/points?'+urlencode(dict(id=point['id'])), method='DELETE')
            require(not any(p['id'] == point['id'] for p in probe.call('/api/calibration/points')), 'Registry deletion failed')
            return dict(created_dragged_saved_deleted=True, undo_redo=True, land_rejected=True, mapping=[i2,j2])
        check('points_drag_crud_undo_redo_calibration_mapping', points)

        def network():
            state = probe.call('/api/ecology/network')
            require(len(state['nodes']) > 10 and len(state['edges']) > 10, 'Network lacks real modules/couplings')
            module = next(n for n in state['nodes'] if n['name'] == 'abiotic_water')
            old = module['parameters']['kNitrW']
            original = (case/'fabm.yaml').read_bytes()
            updated = probe.call('/api/ecology/network', dict(**state, module='abiotic_water', parameters=dict(kNitrW=old+0.001)))
            require(yaml.safe_load((case/'fabm.yaml').read_text())['instances']['abiotic_water']['parameters']['kNitrW'] == old+0.001, 'Network parameter not persisted')
            require((Path(updated['backup'])/'fabm.yaml').read_bytes() == original, 'Network backup wrong')
            probe.call('/api/ecology/network', dict(**state, module='abiotic_water', parameters=dict(kNitrW=old)), expected=409)
            before = (case/'fabm.yaml').read_bytes()
            probe.call('/api/ecology/network', dict(**updated, module='abiotic_water', coupling={'nonexistent':'bad/ref'}), expected=400)
            require((case/'fabm.yaml').read_bytes() == before, 'Rejected network edit mutated config')
            probe.call('/api/ecology/network', dict(**updated, module='abiotic_water', parameters=dict(kNitrW=old)))
            return dict(nodes=len(state['nodes']), edges=len(state['edges']), scalar_persisted=True, stale_rejected=True, invalid_coupling_rejected=True)
        check('ecology_network_real_edges_scalar_edit_guards', network)

        def physics():
            state = probe.call('/api/physics/config')
            parameter = next(p for p in state['parameters'] if p['key'] == 'timestep')
            original = (case/'getm.inp').read_bytes()
            edited = probe.call('/api/physics/config', dict(**state, changes=[dict(group=parameter['group'],key='timestep',value='1.0' if parameter['type']=='real' else '1')]))
            require(Path(edited['backup']).read_bytes() == original, 'Physics backup differs')
            require(next(p for p in edited['parameters'] if p['key']=='timestep')['value'] in ('1','1.0'), 'Physics edit absent')
            probe.call('/api/physics/config', dict(**state, changes=[]), expected=409)
            probe.call('/api/physics/config', dict(**edited, changes=[dict(group=parameter['group'],key='timestep',value='bad\n/')]), expected=400)
            probe.call('/api/physics/config', dict(**edited,changes=[dict(group=parameter['group'],key='timestep',value=parameter['value'])]))
            require((case/'getm.inp').read_bytes() == original, 'Physics restore not exact')
            probe.call('/api/physics/config?file=../outside', expected=400)
            return dict(edit_backup_restore=True, stale_type_path_guards=True, parameters=len(state['parameters']))
        check('physics_namelist_scalar_persistence_guards', physics)

        def diagnostics():
            checked = probe.call('/api/run/check')
            require(checked['checks'] and checked['revision'], 'No diagnostic checks/revision')
            actions = [a for c in checked['checks'] for a in c.get('actions',[])]
            require(actions, 'Diagnostics provide no navigation actions')
            repair = exercise_repair(probe, case)
            # A revision taken before a repair can equal the restored content;
            # use an explicitly stale revision to exercise this guard.
            probe.call('/api/run/repair',dict(case_path=checked['case_path'],revision='stale-revision',action='output_sync'), expected=409)
            final = probe.call('/api/run/check')
            require(final['ok'], 'Autofix did not leave runnable configuration')
            return dict(checks=len(checked['checks']), actions=actions, repair=repair, final_ok=final['ok'])
        check('diagnostic_navigation_safe_repair_stale_guard', diagnostics)

        def modules():
            original = (case/'fabm.yaml').read_bytes()
            side = case/'fabm_disabled.yaml'
            original_side = side.read_bytes() if side.exists() else None
            state = probe.call('/api/config/modules')
            selection = state['selection']
            try:
                ensured = probe.call('/api/config/modules',dict(eco=True,fish=True,ghg=True))
                require(ensured['success'],f'Enabling fish/GHG failed: {ensured}')
                off = probe.call('/api/config/modules', dict(fish=False))
                require(off['success'] and not probe.call('/api/config/modules')['selection']['fish'], 'Fish disable did not persist')
                on = probe.call('/api/config/modules', dict(fish=True))
                require(on['success'] and probe.call('/api/config/modules')['selection']['fish'], 'Fish enable did not persist')
                ghg = probe.call('/api/config/ghg')
                require(ghg['enabled'] and ghg['exe_has_ghg'], 'GHG enabled/executable readiness missing')
                disabled = probe.call('/api/config/ghg',dict(enabled=False))
                require(not disabled['enabled'] and not probe.call('/api/config/ghg')['enabled'], 'GHG disable failed')
                enabled = probe.call('/api/config/ghg',dict(enabled=True))
                require(enabled['enabled'] and not enabled['build_started'], 'GHG enable unexpectedly needs build')
                return dict(fish_off_on=True, ghg_off_on=True, executable_ready=True, draft_persisted=(model/'app'/'.module_selection.json').exists())
            finally:
                (case/'fabm.yaml').write_bytes(original)
                if original_side is None: side.unlink(missing_ok=True)
                else: side.write_bytes(original_side)
                probe.call('/api/case/load',dict(case_name=case.name))
        check('fish_ghg_module_switches_persist_and_native_ready', modules)

        def engine_switch():
            original = (case/'getm.inp').read_bytes()
            fabm = case/'fabm.yaml'
            original_fabm = fabm.read_bytes() if fabm.exists() else None
            side = case/'fabm_disabled.yaml'
            original_side = side.read_bytes() if side.exists() else None
            try:
                # Keep coverage of the legacy coarse GETM FABM master switch.
                probe.call('/api/config/engines',dict(eco=False))
                require(probe.call('/api/config/engines')['eco']['enabled'] is False, 'Eco engine direct disable failed')
                probe.call('/api/config/engines',dict(eco=True))
                require(probe.call('/api/config/engines')['eco']['enabled'] is True, 'Eco engine direct enable failed')

                # The module API controls ecological-network and water-quality
                # instances independently. Turning ecology off alone must keep
                # the GETM FABM master enabled while water quality remains on.
                probe.call('/api/config/modules',dict(eco=False))
                selected = probe.call('/api/config/modules')['selection']
                require(selected['eco'] is False and selected['water_quality'] is True,
                        'Module ecology off did not persist independently of water quality')
                require(probe.call('/api/config/engines')['eco']['enabled'] is True,
                        'GETM FABM master should remain enabled while water quality is on')

                probe.call('/api/config/modules',dict(water_quality=False))
                selected = probe.call('/api/config/modules')['selection']
                require(selected['eco'] is False and selected['water_quality'] is False,
                        'Module ecology/water-quality off selection did not persist')
                require(probe.call('/api/config/engines')['eco']['enabled'] is False,
                        'GETM FABM master should turn off when both domains are disabled')
                return dict(direct_off_on=True,eco_off_water_quality_on_master_on=True,
                            both_domains_off_master_off=True)
            finally:
                (case/'getm.inp').write_bytes(original)
                if original_fabm is not None: fabm.write_bytes(original_fabm)
                if original_side is None: side.unlink(missing_ok=True)
                else: side.write_bytes(original_side)
                probe.call('/api/case/load',dict(case_name=case.name))
        check('eco_engine_switches_persist',engine_switch)

        def configuration():
            old = probe.call('/api/config/time')
            before = (case/'getm.inp').read_bytes()
            probe.call('/api/config/time',dict(timestep=-1),expected=400)
            require((case/'getm.inp').read_bytes() == before,'Rejected negative dt mutated input')
            probe.call('/api/config/time',dict(timestep=2))
            require(float(probe.call('/api/config/time')['timestep'])==2,'Time settings did not persist')
            hot = probe.call('/api/config/hotstart')
            before_hot = (case/'getm.inp').read_bytes()
            probe.call('/api/config/hotstart',dict(enabled=True,file='test_restart.nc'),expected=400)
            require((case/'getm.inp').read_bytes()==before_hot,'Invalid restart changed configuration')
            probe.call('/api/config/hotstart',dict(enabled=False,save=True))
            require(probe.call('/api/config/hotstart')['save'] is True,'Checkpoint saving missing')
            probe.call('/api/config/hotstart',dict(enabled=hot['enabled'],file=hot['file'],save=hot['save']))
            output = probe.call('/api/config/output')
            raw=(case/'output.yaml').read_bytes()
            probe.call('/api/config/output',dict(sync_interval=0),expected=400)
            probe.call('/api/config/output',dict(sources=['v']),expected=400)
            require((case/'output.yaml').read_bytes()==raw,'Rejected subscription altered output')
            probe.call('/api/config/output',dict(sources=['temp','salt'],sync_interval=1))
            require(probe.call('/api/config/output')['sources']==['temp','salt'],'Output subscription missing')
            (case/'output.yaml').write_bytes(raw)
            (case/'getm.inp').write_bytes(before)
            return dict(time=old,checkpoint_configuration=True,missing_restart_rejected=True,
                        restart_continuation='Requires separate native consistency acceptance',
                        output_subscription=True,rejected_negative_dt_zero_sync_unregistered_v=True)
        check('time_hotstart_output_configuration_validation',configuration)

        def remaining_configuration_routes():
            help_info=probe.call('/api/preprocess/help')
            validate_preprocess_help(help_info)
            estimate=probe.call('/api/run/estimate')
            require(estimate and any(isinstance(v,(int,float)) and v>0 for v in estimate.values()),'No numeric run estimate')
            picker=probe.call('/api/system/pick_folder_result')
            require(picker==dict(path=None,done=False),'Fresh root unexpectedly has picker result')
            inventory=probe.call('/api/input/rivers')
            require(inventory['has_rivers_nc'] and len(inventory['rivers'])>=2,'River input inventory incomplete')
            probe.call('/api/input/rivers/add',dict(name='TEMP_RIVER',i=i+1,j=j+1))
            require(any(r['name']=='TEMP_RIVER' for r in probe.call('/api/input/rivers')['rivers']),'New river not persisted')
            probe.call('/api/input/rivers/add',dict(name='TEMP_RIVER',i=i+1,j=j+1),expected=400)
            probe.call('/api/input/rivers/delete',dict(name='TEMP_RIVER'))
            require(not any(r['name']=='TEMP_RIVER' for r in probe.call('/api/input/rivers')['rivers']),'River deletion not persisted')
            original=(case/'fabm.yaml').read_bytes()
            side=case/'fabm_disabled.yaml'
            side_original=side.read_bytes() if side.exists() else None
            try:
                info=probe.call('/api/config/fabm')
                require(len(info['modules'])>10,'FABM metadata empty')
                probe.call('/api/config/fabm/param',dict(module='abiotic_water',param='kNitrW',value=.301))
                require(yaml.safe_load((case/'fabm.yaml').read_text())['instances']['abiotic_water']['parameters']['kNitrW']==.301,'FABM parameter edit did not persist')
                instances=yaml.safe_load((case/'fabm.yaml').read_text())['instances']
                candidate='methane' if 'methane' in instances else next(iter(instances))
                disabled=probe.call('/api/config/fabm/module',dict(module=candidate,enabled=False,force=True))
                require(disabled['success'] and candidate not in yaml.safe_load((case/'fabm.yaml').read_text())['instances'],'Module disable not persisted')
                require(side.is_file() and candidate in yaml.safe_load(side.read_text()),'Disabled module lost from sidecar')
                enabled=probe.call('/api/config/fabm/module',dict(module=candidate,enabled=True))
                require(enabled['success'] and candidate in yaml.safe_load((case/'fabm.yaml').read_text())['instances'],'Module re-enable not persisted')
            finally:
                (case/'fabm.yaml').write_bytes(original)
                if side_original is None: side.unlink(missing_ok=True)
                else: side.write_bytes(side_original)
                probe.call('/api/case/load',dict(case_name=case.name))
            return dict(help_shapes=True,estimate=estimate,river_add_duplicate_delete=True,fabm_parameter_toggle_sidecar=True,picker_poll_without_OS_dialog=True)
        check('remaining_help_estimate_river_crud_fabm_config',remaining_configuration_routes)

        def observations_and_calibration():
            probe.call('/api/case/load',dict(case_name=calibration_case.name))
            require(not list(calibration_case.rglob('output.nc')),'Calibration source already has output')
            point=probe.call('/api/calibration/points',dict(name='Synthetic temperature reference',i=i,j=j,variables=['temp']))['point']
            with nc.Dataset(case/'output'/'output.nc') as ds:
                times=nc.num2date(ds['time'][:],ds['time'].units)
                values=np.asarray(ds['temp'][:,-1,j,i],dtype=float)
            observations=[dict(time=t.strftime('%Y-%m-%d %H:%M:%S'),value=float(v)) for t,v in zip(times,values)]
            probe.call('/api/calibration/data',dict(point_id=point['id'],variable='temp',values=observations))
            stored=probe.call('/api/calibration/data?'+urlencode(dict(point_id=point['id'],variable='temp')))
            require(stored==observations,'Observation data did not persist')
            csv=work/'synthetic_observations.csv'
            csv.write_text('time,value,variable\n'+ '\n'.join(f"{o['time']},{o['value']},temp" for o in observations[:2])+'\n',encoding='utf-8')
            uploaded=probe.call('/api/calibration/upload',files=[('file',csv)],form=dict(point_id=point['id']))
            require(uploaded['total_rows']==2 and uploaded['stored']['temp']==2,'CSV observations lost')
            config=dict(method='parsac',parameters=[dict(module='abiotic_water',param='kNitrW',min=.299,max=.301)],n_iterations=2,objective_function='rmse')
            probe.call('/api/calibration/auto/config',config)
            require(probe.call('/api/calibration/auto/config')==config,'Calibration configuration not persisted')
            probe.call('/api/calibration/auto/start',dict(params=[]),expected=400)
            probe.call('/api/calibration/auto/status',expected=400)
            started=probe.call('/api/calibration/auto/start',
                               calibration_start_payload(config,point_ids=[point['id']]))
            job_id=started['job_id']
            report['calibration_job_id']=job_id
            deadline=time.monotonic()+args.timeout
            while time.monotonic()<deadline:
                status=probe.call('/api/calibration/auto/status?'+urlencode(dict(job_id=job_id)))
                if status['status'] not in ('running',): break
                time.sleep(2)
            require(status['status']=='completed',f'Calibration not completed: {status}')
            result=status['result']
            require(status['history_len']>=1 and result['engine']=='scipy.lbfgsb','No actual scipy evaluations')
            if status['history_len']==1:
                # These temperature observations use this case's initial
                # parameters. A fresh native trial may already fit exactly;
                # requiring a redundant second trial rejects correct stopping.
                # Nonzero-distance optimization and improvement are required
                # separately by verify_calibration_acceptance.py.
                require(status['history'][0]['objective']==0.0 and
                        result['best_objective']==0.0 and
                        result.get('message','').startswith('Exact zero distance reached'),
                        'A single trial is valid only at a verified exact fit')
            require(math.isfinite(result['best_objective']) and result['best_objective']<1e9,'Penalty/no-pair calibration objective')
            applied=probe.call('/api/calibration/auto/apply',dict(job_id=job_id))
            value=applied['applied'][0]['value']
            require(yaml.safe_load((calibration_case/'fabm.yaml').read_text())['instances']['abiotic_water']['parameters']['kNitrW']==value,'Best parameter not persisted')
            probe.call('/api/case/load',dict(case_name=case.name))
            comparison=probe.call('/api/calibration/comparison?'+urlencode(dict(point_id=point['id'],variable='temp')))
            require(len(comparison['scatter_pairs'])==len(observations)+2,'Observation/simulation pairing count wrong')
            require(all(math.isfinite(p['sim']) for p in comparison['scatter_pairs']),'Comparison contains nonfinite simulated values')
            probe.call('/api/calibration/points?'+urlencode(dict(id=point['id'])),method='DELETE')
            return dict(status=status,apply=applied,observations=len(observations),csv_rows=2,scatter_pairs=len(comparison['scatter_pairs']),native_input_only_source=True,scientific_accuracy_claim=False)
        check('synthetic_observations_native_optimization_apply_comparison',observations_and_calibration)

        def calibration_stop():
            probe.call('/api/case/load',dict(case_name=calibration_case.name))
            stop_point=probe.call('/api/calibration/points',dict(
                name='Synthetic stop-status reference',i=i,j=j,variables=['temp']))['point']
            with nc.Dataset(case/'output'/'output.nc') as ds:
                times=nc.num2date(ds['time'][:],ds['time'].units)
                values=np.asarray(ds['temp'][:,-1,j,i],dtype=float)
            require(values.size>0 and np.isfinite(values).all(),
                    'Stop-status reference needs finite values from the verified native output')
            observations=[dict(time=t.strftime('%Y-%m-%d %H:%M:%S'),value=float(value))
                          for t,value in zip(times,values)]
            probe.call('/api/calibration/data',dict(point_id=stop_point['id'],variable='temp',values=observations))
            config=probe.call('/api/calibration/auto/config')
            job=probe.call('/api/calibration/auto/start',
                           calibration_start_payload(config,point_ids=[stop_point['id']]))
            identifier=job['job_id']
            try:
                initial=probe.call('/api/calibration/auto/status?'+urlencode(dict(job_id=identifier)))
                require(initial['status']=='running','Calibration not running before stop')
                probe.call('/api/calibration/auto/stop',dict(job_id=identifier))
                deadline=time.monotonic()+60
                while time.monotonic()<deadline:
                    status=probe.call('/api/calibration/auto/status?'+urlencode(dict(job_id=identifier)))
                    if status['end_time']: break
                    time.sleep(.5)
                require(status['status']=='stopped' and status['end_time'],'Stopped calibration worker overwrote status or never ended')
                return dict(status=status['status'],worker_ended=True,history_len=status['history_len'],
                            scoped_point_id=stop_point['id'],observations=len(observations))
            finally:
                probe.call('/api/calibration/points?'+urlencode(dict(id=stop_point['id'])),method='DELETE')
        check('native_calibration_stop_status_persists_after_worker',calibration_stop)

        def run_stop():
            probe.call('/api/case/load',dict(case_name=calibration_case.name))
            probe.call('/api/run/start',{})
            status=probe.call('/api/run/status')
            require(status['status']=='running','Run did not enter running state')
            probe.call('/api/run/start',{},expected=409)
            probe.call('/api/physics/config',dict(case_path=str(calibration_case),revision='none',changes=[]),expected=409)
            probe.call('/api/run/stop',{})
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                status=probe.call('/api/run/status')
                if status['status']!='running': break
                time.sleep(.2)
            require(status['status']=='stopped','Run stop state not persisted')
            return dict(status=status['status'],duplicate_start_rejected=True,editing_while_running_rejected=True)
        check('native_run_start_status_duplicate_guard_stop',run_stop)
        report['passed']=all(f['status']=='passed' for f in report['features'].values())
    except Exception as error:
        report['error']=f'{type(error).__name__}: {error}'
    finally:
        if probe:
            try: probe.call('/api/run/stop',{})
            except Exception: pass
            report['api_calls']=probe.calls
            report['expected_validation_rejections']=[dict(method=c['method'],path=c['path'],http_status=c['http_status'])
                for c in probe.calls if c.get('passed') and c.get('http_status',0)>=400]
            report['route_coverage']=coverage_report(probe)
        if process.poll() is None: process.terminate()
        try: process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=10)
        stdout.close(); stderr.close()
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k in ('passed','error','features')},ensure_ascii=False,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
