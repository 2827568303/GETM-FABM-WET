"""Run a complete backend round; count it only after recorded UI acceptance.

Partial reports never count. Each round uses fresh generated inputs. Every
subprocess writes its own evidence and logs; failed evidence is retained.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from output_paths import output_path, require_outside_c

ROOT=Path(__file__).resolve().parents[1]
UI_CHECKS=(
    'preprocess_upload_grid_save', 'parameters_initial_conditions_reload',
    'modules_network_lake_points', 'diagnostics_navigation_repair_run',
    'dashboard_all_result_modes', 'calibration_import_compare_scipy_abc',
    'result_files_duplicates_cleanup_restore', 'language_import_switch_persistence',
    'ctrl_zoom_resize_pan_fullscreen_export', 'eta_completion_failure_notifications',
)
BACKEND_STAGES=('external','features','results','scipy','abc','restart')


def consecutive_count(records):
    count=0;version=None;seeds=set();identities=set();pending=False
    for record in records:
        if pending:raise ValueError('Unfinished round precedes another round')
        if record['seed'] in seeds or record['input_identity'] in identities:
            raise ValueError('Repeated seed or input data cannot form independent rounds')
        seeds.add(record['seed']);identities.add(record['input_identity'])
        if record['version']!=version:count=0;version=record['version']
        status=record['status']
        if status=='failed':count=0
        elif status=='passed':count+=1
        elif status in ('running','awaiting_ui'):pending=True
        else:raise ValueError('Unknown round status')
    return count


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_version(solver):
    files=set()
    for folder in ('3DWET/app/static','3DWET/app/templates','3DWET/model_builder/templates'):
        files.update(p for p in (ROOT/folder).rglob('*') if p.is_file())
    files.update((ROOT/'3DWET/app').glob('*.py'))
    files.update(p for p in (ROOT/'3DWET/app').glob('*.json')
                 if p.name not in {'.active_case.json','.module_selection.json'})
    files.update(ROOT/'scripts'/name for name in (
        'verify_external_workflow.py','verify_feature_matrix.py','verify_results_experience.py',
        'verify_calibration_acceptance.py','verify_restart_acceptance.py','workflow_acceptance.py'))
    entries={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(files)}
    entries['actual_solver']=digest(solver)
    return hashlib.sha256(json.dumps(entries,sort_keys=True).encode()).hexdigest(),entries


def model_source_provenance(source):
    """Validate the external workflow source and identify its case config."""
    source=Path(source).expanduser().resolve()
    if not source.is_dir():
        raise ValueError(f'Model source root is not a directory: {source}')
    required=(source/'bin'/'getm_cartesian.exe',source/'bin'/'runtime',
              source/'case'/'Lake Luoma',source/'case'/'Lake Luoma'/'getm.inp')
    missing=[str(path) for path in required if not (path.is_file() if path.suffix else path.is_dir())]
    if missing:
        raise ValueError('Model source is incomplete: '+', '.join(missing))
    files=set(p for p in (source/'case'/'Lake Luoma').rglob('*') if p.is_file())
    templates=source/'model_builder'/'templates'
    if templates.is_dir():
        files.update(p for p in templates.rglob('*') if p.is_file())
    entries={p.relative_to(source).as_posix():digest(p) for p in sorted(files)}
    identity=hashlib.sha256(json.dumps(entries,sort_keys=True).encode()).hexdigest()
    return {'root':str(source),'case':'Lake Luoma','config_identity':identity,
            'config_files':entries}


def stage_imported_case(work, imported_case, case_name):
    """Copy the external stage's API-imported case into its isolated model tree."""
    work=Path(work).resolve()
    external_root=(work/'external').resolve()
    source=Path(imported_case).expanduser().resolve()
    if not source.is_dir() or not source.is_relative_to(external_root):
        raise ValueError(f'Imported case must be a directory inside this attempt external work tree: {source}')
    if source.name!=case_name:
        raise ValueError(f'Imported case name mismatch: expected {case_name!r}, got {source.name!r}')
    required=('bathymetry.nc','meteo.nc','output.yaml')
    missing=[name for name in required if not (source/name).is_file()]
    if missing:
        raise ValueError(f'Imported case is missing required run inputs: {missing}')
    target=external_root/'3DWET'/'case'/case_name
    if target.exists() or target.is_symlink():
        raise ValueError(f'Imported case staging target already exists: {target}')
    files={}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Imported case contains a symlink: {path}')
        if path.is_file():
            files[path.relative_to(source).as_posix()]=digest(path)
    shutil.copytree(source,target)
    copied={path.relative_to(target).as_posix():digest(path)
            for path in sorted(target.rglob('*')) if path.is_file()}
    if copied!=files:
        raise ValueError(f'Staged imported case does not preserve its input hashes: {source} -> {target}')
    identity=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
    return {'source_path':str(source),'path':str(target.resolve()),'files':files,
            'config_identity':identity}


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    temporary.replace(path)


def update_ledger(path,report):
    ledger=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'rounds':[]}
    records=ledger['rounds']
    entry={k:report[k] for k in ('work','seed','version','input_identity','status')}
    matches=[i for i,r in enumerate(records) if r['work']==entry['work']]
    if matches:records[matches[0]]=entry
    else:records.append(entry)
    ledger['consecutive_complete']=consecutive_count(records)
    ledger['required_complete']=5
    ledger['scope']='Full backend stages plus every required UI check; installation acceptance is separate.'
    write(path,ledger)


def review_ui(report,path):
    for name in BACKEND_STAGES:
        stage=report.get('stages',{}).get(name,{})
        evidence=Path(stage.get('report',''))
        if stage.get('passed') is not True or not evidence.is_file():
            raise ValueError('Backend evidence incomplete: '+name)
        if digest(evidence)!=stage.get('sha256') or json.loads(evidence.read_text(encoding='utf-8')).get('passed') is not True:
            raise ValueError('Backend evidence changed or failed: '+name)
    ui=json.loads(path.read_text(encoding='utf-8'))
    if ui.get('version')!=report['version'] or ui.get('seed')!=report['seed']:
        raise ValueError('UI evidence must match this exact version and dataset')
    checks=ui.get('checks',{})
    if set(UI_CHECKS)-set(checks):raise ValueError('UI checklist is incomplete; round remains pending')
    for name in UI_CHECKS:
        check=checks[name]
        if check.get('passed') is not True:
            report['status']='failed';report['error']='UI check failed: '+name;return
        if not check.get('observed') or not check.get('evidence'):
            raise ValueError('UI check needs actual observations and evidence: '+name)
        for item in check['evidence']:
            evidence=(path.parent/item).resolve()
            if not evidence.is_file():raise ValueError('Missing UI evidence: '+str(evidence))
    report['ui_report']={'path':str(path.resolve()),'sha256':digest(path)}
    report['status']='passed'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--solver',type=Path,required=True)
    parser.add_argument('--model-source',type=Path,default=ROOT/'3DWET',
                        help='Validated model root used to seed the external Lake Luoma stage (default: repository 3DWET root)')
    parser.add_argument('--bathymetry-kind',choices=('point','polygon'),default='point')
    parser.add_argument('--ledger',type=Path,default=output_path('build','workflow-acceptance','ledger.json'))
    parser.add_argument('--review-ui',type=Path)
    parser.add_argument('--fail-reason',help='Record an observed failure in a round awaiting UI; retain evidence and reset the streak')
    args=parser.parse_args()
    work=require_outside_c(args.work, '--work')
    ledger=require_outside_c(args.ledger, '--ledger')
    review_ui_path=require_outside_c(args.review_ui, '--review-ui') if args.review_ui else None
    args.work=work;args.ledger=ledger;args.review_ui=review_ui_path
    solver=args.solver.resolve()
    version,version_files=source_version(solver)
    report_path=work/'round.json'
    if args.review_ui or args.fail_reason:
        report=json.loads(report_path.read_text(encoding='utf-8'))
        if report['status']!='awaiting_ui':raise ValueError('Only a pending UI round can be reviewed')
        if args.fail_reason or report['version']!=version:
            report['status']='failed'
            report['error']=args.fail_reason or 'Source changed: round must be restarted with fresh data'
        else:review_ui(report,args.review_ui)
        write(report_path,report);update_ledger(args.ledger,report)
        return 0 if report['status']=='passed' else 1
    if args.seed is None:parser.error('--seed is required for a new round')
    if work.exists():parser.error('--work must be a fresh directory')
    if args.ledger.exists():
        records=json.loads(args.ledger.read_text(encoding='utf-8'))['rounds']
        if any(r['status'] in ('running','awaiting_ui') for r in records):
            parser.error('Finish or record failure of the pending round before starting another')
        if any(r['seed']==args.seed for r in records):parser.error('Every attempt requires a new seed')
    try:
        model_source=model_source_provenance(args.model_source)
    except ValueError as error:
        parser.error(str(error))
    model_source_root=Path(model_source['root'])
    work.mkdir(parents=True)
    report={'work':str(work),'seed':args.seed,'version':version,'version_files':version_files,
            'input_identity':'pending-'+str(args.seed),'status':'running','stages':{},
            'required_ui_checks':list(UI_CHECKS),'model_source':model_source}
    write(report_path,report);update_ledger(args.ledger,report)
    scripts=ROOT/'scripts';generated=work/'external/3DWET';case='Imported Random Lake'
    commands=[
        ('external',[str(scripts/'verify_external_workflow.py'),'--work',str(work/'external'),'--seed',str(args.seed),'--solver',str(solver),'--bathymetry-kind',args.bathymetry_kind,'--model-source',str(model_source_root)]),
        ('features',[str(scripts/'verify_feature_matrix.py'),'--work',str(work/'features'),'--source-case',str(generated/'case'/case),'--solver',str(solver)]),
        ('results',[str(scripts/'verify_results_experience.py'),'--work',str(work/'results'),'--model-source',str(generated),'--case',case]),
        ('scipy',[str(scripts/'verify_calibration_acceptance.py'),'--work',str(work/'scipy'),'--model-source',str(generated),'--case',case,'--method','scipy']),
        ('abc',[str(scripts/'verify_calibration_acceptance.py'),'--work',str(work/'abc'),'--model-source',str(generated),'--case',case,'--method','pyabc']),
        ('restart',[str(scripts/'verify_restart_acceptance.py'),'--work',str(work/'restart'),'--model-source',str(generated),'--case',case]),
    ]
    try:
        for name,command in commands:
            if source_version(solver)[0] != version:
                raise RuntimeError('Source changed during acceptance; restart with fresh data')
            print('START '+name,flush=True)
            with (work/(name+'.log')).open('w',encoding='utf-8') as log:
                process=subprocess.run([sys.executable]+command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            path=work/name/'verification.json'
            data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
            report['stages'][name]={'passed':process.returncode==0 and data.get('passed') is True,
                                    'report':str(path),'sha256':digest(path) if path.exists() else None}
            if not report['stages'][name]['passed']:raise RuntimeError(name+' failed; see '+str(work/(name+'.log')))
            actual=generated/'bin/getm_cartesian.exe' if name=='external' else work/name/'3DWET/bin/getm_cartesian.exe'
            if digest(actual)!=digest(solver):raise RuntimeError('Solver mismatch in '+name)
            if name=='external':
                staged_case=stage_imported_case(work,data.get('data',{}).get('imported_case'),case)
                report['staged_imported_case']=staged_case
                report['input_hashes']=data['data']['sha256']
                report['input_identity']=hashlib.sha256(json.dumps(report['input_hashes'],sort_keys=True).encode()).hexdigest()
            write(report_path,report);update_ledger(args.ledger,report)
            print('PASS '+name,flush=True)
        report['observations_sha256']=digest(work/'features/synthetic_observations.csv')
        if source_version(solver)[0]!=version:raise RuntimeError('Source changed during round')
        report['status']='awaiting_ui'
    except Exception as error:
        report['status']='failed';report['error']=str(error)
    write(report_path,report);update_ledger(args.ledger,report)
    print(json.dumps({'status':report['status'],'error':report.get('error'),'work':str(work)}),flush=True)
    return 1 if report['status']=='failed' else 0


if __name__=='__main__':raise SystemExit(main())
