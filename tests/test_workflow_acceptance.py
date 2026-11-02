"""Consecutive full runs cannot be replaced by partial or repeated evidence."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import workflow_acceptance
from workflow_acceptance import consecutive_count, review_ui, UI_CHECKS
import json
import shutil
import hashlib
from types import SimpleNamespace


def record(n,status='passed',version='v1'):
    return dict(seed=n,status=status,version=version,input_identity=f'data-{n}')


def test_five_distinct_complete_runs():
    assert consecutive_count([record(n) for n in range(5)]) == 5


def test_failure_resets_and_five_new_runs_are_required():
    records=[record(n) for n in range(3)]+[record(3,'failed')]
    assert consecutive_count(records)==0
    assert consecutive_count(records+[record(n) for n in range(4,9)])==5


def test_partial_run_does_not_increment():
    assert consecutive_count([record(1),record(2,'awaiting_ui')])==1


def test_reused_data_and_version_changes_cannot_form_a_streak():
    with pytest.raises(ValueError,match='Repeated'):
        consecutive_count([record(1),record(1)])
    assert consecutive_count([record(1),record(2),record(3,version='v2')])==1


def test_unknown_status_cannot_pass():
    with pytest.raises(ValueError,match='status'):
        consecutive_count([record(1,'probably_passed')])


def test_unfinished_round_cannot_be_skipped():
    with pytest.raises(ValueError,match='Unfinished'):
        consecutive_count([record(1,'awaiting_ui'),record(2)])


def test_ui_cannot_complete_round_without_all_backend_reports(tmp_path):
    evidence=tmp_path/'evidence.txt';evidence.write_text('observed browser state')
    path=tmp_path/'ui.json'
    path.write_text(json.dumps({'version':'v1','seed':1,'checks':{
        key:{'passed':True,'observed':'control returned expected result','evidence':['evidence.txt']}
        for key in UI_CHECKS}}))
    with pytest.raises(ValueError,match='Backend'):
        review_ui({'version':'v1','seed':1,'stages':{}},path)


def test_main_reviews_matching_ui_report_after_backend_stages(tmp_path,monkeypatch):
    work=tmp_path/'round'
    work.mkdir()
    ledger=tmp_path/'ledger.json'
    solver=tmp_path/'solver.exe'
    solver.write_bytes(b'solver')
    stages={}
    for name in workflow_acceptance.BACKEND_STAGES:
        evidence=work/f'{name}.json'
        evidence.write_text(json.dumps({'passed':True}),encoding='utf-8')
        stages[name]={'passed':True,'report':str(evidence),
                      'sha256':workflow_acceptance.digest(evidence)}
    ui_dir=work/'ui'
    ui_dir.mkdir()
    evidence=ui_dir/'observed.txt'
    evidence.write_text('observed UI state',encoding='utf-8')
    ui_report=ui_dir/'review.json'
    ui_report.write_text(json.dumps({
        'version':'matching-version','seed':73,
        'checks':{name:{'passed':True,'observed':'expected result',
                        'evidence':['observed.txt']} for name in UI_CHECKS},
    }),encoding='utf-8')
    report={'work':str(work),'seed':73,'version':'matching-version',
            'input_identity':'dataset-73','status':'awaiting_ui','stages':stages}
    (work/'round.json').write_text(json.dumps(report),encoding='utf-8')
    monkeypatch.setattr(workflow_acceptance,'source_version',
                        lambda _solver: ('matching-version',{}))
    monkeypatch.setattr(workflow_acceptance,'require_outside_c',lambda path,*_args:Path(path).resolve())
    monkeypatch.setattr(sys,'argv',['workflow_acceptance.py','--work',str(work),
        '--solver',str(solver),'--ledger',str(ledger),'--review-ui',str(ui_report)])

    assert workflow_acceptance.main()==0
    reviewed=json.loads((work/'round.json').read_text(encoding='utf-8'))
    assert reviewed['status']=='passed'
    assert reviewed['ui_report']['path']==str(ui_report.resolve())


def test_source_version_ignores_mutable_runtime_state_but_hashes_code(tmp_path,monkeypatch):
    for directory in ('3DWET/app/static','3DWET/app/templates','3DWET/model_builder/templates','scripts'):
        (tmp_path/directory).mkdir(parents=True,exist_ok=True)
    (tmp_path/'3DWET/app/server.py').write_text('source-v1')
    active=tmp_path/'3DWET/app/.active_case.json'
    active.write_text('{"case":"A"}')
    solver=tmp_path/'3DWET/bin/getm_cartesian.exe'
    solver.parent.mkdir(parents=True)
    solver.write_bytes(b'solver')
    for name in ('verify_external_workflow.py','verify_feature_matrix.py','verify_results_experience.py',
                 'verify_calibration_acceptance.py','verify_restart_acceptance.py','workflow_acceptance.py'):
        (tmp_path/'scripts'/name).write_text(name)
    monkeypatch.setattr(workflow_acceptance,'ROOT',tmp_path)
    first,_=workflow_acceptance.source_version(solver)
    active.write_text('{"case":"B"}')
    runtime_only,_=workflow_acceptance.source_version(solver)
    assert runtime_only==first
    (tmp_path/'3DWET/app/server.py').write_text('source-v2')
    changed,_=workflow_acceptance.source_version(solver)
    assert changed!=first


@pytest.mark.parametrize('explicit_source',[False,True])
def test_main_wires_model_source_and_records_provenance(tmp_path,monkeypatch,explicit_source):
    root=tmp_path/'repo'
    source=(tmp_path/'custom-source') if explicit_source else root/'3DWET'
    (source/'bin'/'runtime').mkdir(parents=True)
    (source/'bin'/'getm_cartesian.exe').write_bytes(b'source solver')
    case=source/'case'/'Lake Luoma'
    case.mkdir(parents=True)
    (case/'getm.inp').write_text('configuration identity',encoding='utf-8')
    templates=source/'model_builder'/'templates'
    templates.mkdir(parents=True)
    (templates/'fabm.yaml.template').write_text('template identity',encoding='utf-8')
    solver=tmp_path/'candidate.exe';solver.write_bytes(b'candidate solver')
    work=tmp_path/'round';ledger=tmp_path/'ledger.json'
    monkeypatch.setattr(workflow_acceptance,'ROOT',root)
    monkeypatch.setattr(workflow_acceptance,'source_version',lambda _solver:('version-1',{}))
    monkeypatch.setattr(workflow_acceptance,'require_outside_c',lambda path,*_args:Path(path).resolve())
    external_commands=[];feature_commands=[]

    def fake_run(command,**_kwargs):
        script=Path(command[1]).stem
        name={'verify_external_workflow':'external','verify_feature_matrix':'features',
              'verify_results_experience':'results','verify_calibration_acceptance':'scipy',
              'verify_restart_acceptance':'restart'}[script]
        if script=='verify_calibration_acceptance' and command[command.index('--method')+1]=='pyabc':
            name='abc'
        stage_work=Path(command[command.index('--work')+1])
        stage_work.mkdir(parents=True,exist_ok=True)
        report={'passed':True}
        if name=='external':
            external_commands.append(command)
            imported=stage_work/'case-storage'/'Imported Random Lake'
            imported.mkdir(parents=True)
            for filename,content in {'bathymetry.nc':b'bathy','meteo.nc':b'meteo',
                                     'output.yaml':b'output: {}'}.items():
                (imported/filename).write_bytes(content)
            report['data']={'sha256':{'bathymetry.nc':'fixture-hash'},
                            'imported_case':str(imported.resolve())}
        elif name=='features':
            feature_commands.append(command)
        (stage_work/'verification.json').write_text(json.dumps(report),encoding='utf-8')
        model=stage_work/'3DWET'/'bin'/'getm_cartesian.exe'
        model.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(solver,model)
        if name=='features':
            (stage_work/'synthetic_observations.csv').write_text('obs\n',encoding='utf-8')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(workflow_acceptance.subprocess,'run',fake_run)
    argv=['workflow_acceptance.py','--work',str(work),'--seed','71','--solver',str(solver),
          '--ledger',str(ledger)]
    if explicit_source:argv.extend(['--model-source',str(source)])
    monkeypatch.setattr(sys,'argv',argv)

    assert workflow_acceptance.main()==0
    report=json.loads((work/'round.json').read_text(encoding='utf-8'))
    external=external_commands[0]
    assert external[external.index('--model-source')+1]==str(source.resolve())
    assert report['model_source']['root']==str(source.resolve())
    expected=workflow_acceptance.model_source_provenance(source)
    assert report['model_source']['config_identity']==expected['config_identity']
    assert 'case/Lake Luoma/getm.inp' in report['model_source']['config_files']
    staged=work/'external'/'3DWET'/'case'/'Imported Random Lake'
    assert feature_commands[0][feature_commands[0].index('--source-case')+1]==str(staged.resolve())
    assert (staged/'bathymetry.nc').read_bytes()==b'bathy'
    assert (staged/'meteo.nc').read_bytes()==b'meteo'
    assert (staged/'output.yaml').read_bytes()==b'output: {}'
    assert report['staged_imported_case']['path']==str(staged.resolve())
    assert report['staged_imported_case']['files']['meteo.nc']==hashlib.sha256(b'meteo').hexdigest()
