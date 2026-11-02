import ast
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask, jsonify

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from run_metrics import IncrementalLogReader, RunMetrics, read_rank_zero_stderr
from solver_runtime import log_has_solver_failure


@pytest.fixture
def worker(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'run_model_thread','run_stop'}]
    for function in functions:
        function.decorator_list = []
    scope = dict(Path=Path, datetime=datetime, os=SimpleNamespace(name='posix'),
                 time=SimpleNamespace(time=lambda:100.,sleep=lambda _:None),
                 run_status='running',run_process=None,run_logs=[],run_start_time=100.,run_case_path=tmp_path,
                 run_metrics=RunMetrics(),_NC_LOCK=threading.RLock(),
                 _capture_run_repair_summary=lambda *_args:None,
                 solver_environment=lambda _: {}, log_has_solver_failure=log_has_solver_failure,
                 explain_exit_code=lambda _: 'bad exit',nc_open=None,jsonify=jsonify,
                 _archive_run_outputs=lambda *_:None, subprocess=subprocess,
                 validate_current_run_outputs=lambda *_a,**_k: dict(ready=True,duration_seconds=0),
                 ProcessTimeoutExpired=TimeoutError)
    scope['run_metrics'].start({'nsteps':600},now=100)
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),scope)
    return tmp_path,scope


def test_stop_before_launch_cancels_without_spawning(worker):
    path,scope=worker
    scope['run_status']='stopped'
    scope['run_model_thread'](path,'solver.exe')
    assert scope['run_process'] is None
    assert not (path/'model_run.log').exists()
    assert scope['run_status']=='stopped'


def test_early_fatal_is_not_lost_when_log_tail_is_trimmed(worker):
    path,scope=worker
    process=SimpleNamespace(returncode=0)
    polls=iter([None,0])
    process.poll=lambda:next(polls)
    def launch(*_a,**kwargs):
        kwargs['stdout'].write('FATAL ERROR: invalid configuration\n'+('diagnostic line\n'*6000)+'getm: Completed on 20261009\n')
        kwargs['stdout'].flush()
        return process
    scope['subprocess']=SimpleNamespace(Popen=launch,DEVNULL=subprocess.DEVNULL,STDOUT=subprocess.STDOUT)
    scope['run_model_thread'](path,'solver.exe')
    assert len(scope['run_logs']) < 3000
    assert not any('FATAL ERROR:' in line for line in scope['run_logs'])
    assert any('getm: Completed on' in line for line in scope['run_logs'])
    assert scope['run_status']=='failed'


def test_healthy_exit_with_invalid_numeric_results_fails_without_archive(worker):
    path,scope=worker
    process=SimpleNamespace(returncode=0,poll=lambda:0)
    scope['subprocess']=SimpleNamespace(Popen=lambda *_a,**_k:process,DEVNULL=subprocess.DEVNULL,STDOUT=subprocess.STDOUT)
    scope['validate_current_run_outputs']=lambda *_a,**_k:dict(ready=False,errors=['NaN output'],bad_variables=[])
    archived=[]
    scope['_archive_run_outputs']=lambda *_:archived.append(True)
    scope['run_model_thread'](path,'solver.exe')
    assert scope['run_status']=='failed' and not archived
    assert any('NaN output' in line for line in scope['run_logs']), scope['run_logs']


def test_stop_handles_launch_gap(worker):
    _,scope=worker
    with Flask(__name__).app_context():
        result=scope['run_stop']().get_json()
    assert result['success'] and scope['run_status']=='stopped'


def test_native_stdout_numerical_failure_is_logged_and_never_archived(worker):
    path,scope=worker
    root=Path(__file__).resolve().parents[1]
    compiler=root/'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():pytest.skip('Portable native Fortran compiler is unavailable')
    source=path/'stdout_failure.f90'
    source.write_text('''program diagnostic
print *, '11:10:00.123 n=         100'
print *, 'Error: state variable 25 is zero and has negative derivative!'
call sleep(10)
write(0,*) 'getm: Completed on 20261014'
end program
''')
    exe=path/'stdout_failure.exe'
    import os
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    compiled=subprocess.run([str(compiler),str(source),'-o',str(exe)],env=env,capture_output=True,text=True)
    assert compiled.returncode==0,compiled.stdout+compiled.stderr
    scope['solver_environment']=lambda _:env
    archived=[];scope['_archive_run_outputs']=lambda *_:archived.append(True)
    import time
    started=time.monotonic()
    scope['run_model_thread'](path,str(exe))
    assert time.monotonic()-started<5, 'Recognized numerical errors must stop the active native process'
    assert scope['run_status']=='failed' and not archived
    assert 'is zero and has negative derivative!' in (path/'model_run.log').read_text()
    assert scope['run_metrics'].snapshot('failed',now=101)['current_step']==100


def test_mpi_worker_observes_delayed_rank_zero_progress_and_final_partial_line(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_mpi_model_thread')
    function.decorator_list = []

    original = tmp_path / 'original'; original.mkdir()
    isolated = tmp_path / 'mpi-case'; isolated.mkdir()
    rank_log = isolated / 'LAKE.0000.stderr'
    ticks = {'sleep': 0, 'poll': 0}

    class Process:
        args = ['mpiexec.exe', '-n', '2', 'solver.exe']
        returncode = 0
        def poll(self):
            ticks['poll'] += 1
            return None if ticks['poll'] <= 2 else 0

    process = Process()

    class FakeMpiRun:
        _log = None
        def __init__(self, *, case, **_kwargs): self.case = Path(case)
        def start(self):
            (self.case / 'model_run.log').write_text('', encoding='utf-8')
            return process
        def finish(self):
            assert scope['run_config']['phase'] == 'merging'
            assert scope['run_status'] == 'running'
            output = self.case / 'output.nc'; output.write_bytes(b'valid output')
            (self.case / 'restart.0000.out').write_bytes(b'rank checkpoint')
            return [output]

    def fake_prepare(_source, **_kwargs):
        return isolated

    def fake_sleep(_seconds):
        ticks['sleep'] += 1
        if ticks['sleep'] == 1:
            rank_log.write_text('n = 100\nn = 1', encoding='utf-8')
        elif ticks['sleep'] == 2:
            with rank_log.open('a', encoding='utf-8') as stream:
                stream.write('500\nn = 2000')

    import os, shutil, subprocess, tempfile, types
    fake_mpi = types.ModuleType('mpi_runner')
    fake_mpi.MpiRun = FakeMpiRun
    fake_mpi.merge_case_rank_outputs = lambda *_: None
    fake_mpi.prepare_mpi_case = fake_prepare
    monkeypatch.setitem(sys.modules, 'mpi_runner', fake_mpi)

    metrics = RunMetrics(); metrics.start({'nsteps': 3000}, now=100)
    observe = metrics.observe
    observation_clock = {'value': 100}
    def observe_at_deterministic_time(text, now=None, source='solver_log'):
        observation_clock['value'] += 1
        return observe(text, now=observation_clock['value'], source=source)
    metrics.observe = observe_at_deterministic_time
    scope = {
        'Path': Path, 'time': SimpleNamespace(time=lambda: 101., sleep=fake_sleep),
        'run_status': 'running', 'run_process': None, 'run_logs': [],
        'run_start_time': 100., 'run_case_path': original, 'run_metrics': metrics,
        'run_config': {'solver_mode': 'MPI (2 ranks)', 'phase': 'solving'},
        '_NC_LOCK': threading.RLock(),
        'validate_current_run_outputs': lambda *_a, **_k: {'ready': True},
        '_archive_run_outputs': lambda *_a: None, 'nc_open': None,
        'subprocess': subprocess, 'shutil': shutil, 'tempfile': tempfile, 'os': os,
        'IncrementalLogReader': IncrementalLogReader,
        'read_rank_zero_stderr': read_rank_zero_stderr,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    scope['run_mpi_model_thread'](original, 'mpiexec.exe', 'solver.exe', 2, [])

    assert scope['run_status'] == 'completed'
    assert (original / 'output' / 'restart.0000.out').read_bytes() == b'rank checkpoint'
    report = metrics.snapshot('running')
    assert report['current_step'] == 1999
    assert report['progress'] > 0 and report['eta_seconds'] > 0
    assert any(line == 'n = 100' for line in scope['run_logs'])
    assert any(line == 'n = 1500' for line in scope['run_logs'])
    assert any(line == 'n = 2000' for line in scope['run_logs'])
    assert scope['run_config']['phase'] == 'completed'


def test_run_status_reports_merge_phase_without_solver_eta(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_status_api')
    function.decorator_list = []
    metrics = RunMetrics(); metrics.start({'nsteps': 3456}, now=10)
    metrics.observe('n = 3400\n', now=50)
    scope = {
        'run_status': 'running', 'run_config': {'solver_mode': 'MPI (4 ranks)', 'phase': 'merging'},
        'run_case_path': tmp_path, 'active_case_path': tmp_path, 'run_logs': [],
        '_run_identity': 'test-run', '_run_log_case_path': tmp_path,
        'run_metrics': metrics, '_run_repair_summary_payload': lambda: None,
        'Path': Path, 'jsonify': jsonify, 'request': SimpleNamespace(args={}),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    with Flask(__name__).app_context():
        report = scope['run_status_api']().get_json()
    assert report['status'] == 'running'
    assert report['phase'] == 'merging'
    assert report['performance']['solver_mode'] == 'MPI (4 ranks)'
    assert report['progress'] < 100
    assert report['eta_seconds'] is None
    assert report['eta_minutes'] is None
    scope['run_status'] = 'failed'
    with Flask(__name__).app_context():
        failed = scope['run_status_api']().get_json()
    assert failed['phase'] == 'failed'
    assert failed['eta_seconds'] is None


def test_run_status_normalizes_terminal_serial_phase(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_status_api')
    function.decorator_list = []
    metrics = RunMetrics(); metrics.start({'nsteps': 100}, now=10)
    scope = {
        'run_status': 'completed', 'run_config': {'solver_mode': 'serial', 'phase': 'compressing'},
        'run_case_path': tmp_path, 'active_case_path': tmp_path, 'run_logs': [],
        '_run_identity': 'test-run', '_run_log_case_path': tmp_path,
        'run_metrics': metrics, '_run_repair_summary_payload': lambda: None,
        'Path': Path, 'jsonify': jsonify, 'request': SimpleNamespace(args={}),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    for status in ('completed', 'failed', 'stopped'):
        scope['run_status'] = status
        with Flask(__name__).app_context():
            report = scope['run_status_api']().get_json()
        assert report['phase'] == status


def test_serial_compressing_phase_keeps_progress_below_complete_and_suppresses_solver_eta(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_status_api')
    function.decorator_list = []
    metrics = RunMetrics(); metrics.start({'nsteps': 10}, now=0)
    metrics.observe('n=2\n', now=1); metrics.observe('n=4\n', now=2)
    scope = {
        'run_status': 'running', 'run_config': {'solver_mode': 'serial', 'phase': 'compressing'},
        'run_case_path': tmp_path, 'active_case_path': tmp_path, 'run_logs': [],
        '_run_identity': 'test-compressing', '_run_log_case_path': tmp_path,
        'run_metrics': metrics, '_run_repair_summary_payload': lambda: None,
        'Path': Path, 'jsonify': jsonify, 'request': SimpleNamespace(args={}),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    with Flask(__name__).app_context():
        report = scope['run_status_api']().get_json()
    assert report['phase'] == 'compressing'
    assert report['progress'] < 100
    assert report['eta_seconds'] is None
    assert report['eta_minutes'] is None


def test_run_status_log_window_is_bounded_and_defaults_to_tail(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_status_api')
    function.decorator_list = []
    request = SimpleNamespace(args={})
    metrics = RunMetrics(); metrics.start({'nsteps': 100}, now=10)
    scope = {
        'run_status': 'running', 'run_config': {}, 'run_case_path': tmp_path,
        'active_case_path': tmp_path, 'run_logs': [f'line {n}' for n in range(6000)],
        '_run_identity': 'test-run', '_run_log_case_path': tmp_path,
        'run_metrics': metrics, '_run_repair_summary_payload': lambda: None,
        'Path': Path, 'jsonify': jsonify, 'request': request,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    with Flask(__name__).app_context():
        default = scope['run_status_api']().get_json()
    assert default['logs'] == [f'line {n}' for n in range(5920, 6000)]
    assert default['total_logs'] == 6000
    request.args = {'log_limit': '250'}
    with Flask(__name__).app_context():
        expanded = scope['run_status_api']().get_json()
    assert len(expanded['logs']) == 250
    assert expanded['logs'][0] == 'line 5750'
    request.args = {'log_limit': '99999'}
    with Flask(__name__).app_context():
        capped = scope['run_status_api']().get_json()
    assert len(capped['logs']) == 5000
    request.args = {'log_limit': '-1'}
    with Flask(__name__).app_context():
        minimum = scope['run_status_api']().get_json()
    assert len(minimum['logs']) == 80


def test_mpi_stop_during_launcher_spawn_stops_the_new_process_tree(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_mpi_model_thread')
    function.decorator_list = []
    original = tmp_path / 'original'; original.mkdir()
    isolated = tmp_path / 'working'; isolated.mkdir()
    stopped = []

    class Process:
        args = ['mpiexec.exe', '-n', '2', 'solver.exe']

    class FakeMpiRun:
        _log = None
        def __init__(self, *, case, **_kwargs): self.case = Path(case)
        def start(self):
            (self.case / 'model_run.log').write_text('launcher started', encoding='utf-8')
            # Model run_stop setting stopped before run_process receives the
            # just-spawned handle. The worker must stop it after start returns.
            scope['run_status'] = 'stopped'
            return Process()
        def stop(self): stopped.append(True)
        def finish(self): pytest.fail('stopped run must not merge outputs')

    import os, shutil, subprocess, tempfile, types
    fake_mpi = types.ModuleType('mpi_runner')
    fake_mpi.MpiRun = FakeMpiRun
    fake_mpi.merge_case_rank_outputs = lambda *_: None
    fake_mpi.prepare_mpi_case = lambda *_a, **_k: isolated
    monkeypatch.setitem(sys.modules, 'mpi_runner', fake_mpi)
    metrics = RunMetrics(); metrics.start({'nsteps': 10}, now=100)
    scope = {
        'Path': Path, 'time': SimpleNamespace(time=lambda: 101., sleep=lambda _: None),
        'run_status': 'running', 'run_process': None, 'run_logs': [],
        'run_start_time': 100., 'run_case_path': original, 'run_metrics': metrics,
        'run_config': {'solver_mode': 'MPI (2 ranks)', 'phase': 'solving'},
        'validate_current_run_outputs': lambda *_a, **_k: {'ready': True},
        '_archive_run_outputs': lambda *_a: pytest.fail('stopped run cannot archive'),
        'nc_open': None, 'subprocess': subprocess, 'shutil': shutil, 'tempfile': tempfile,
        'os': os, '_NC_LOCK': threading.RLock(),
        'IncrementalLogReader': IncrementalLogReader,
        'read_rank_zero_stderr': read_rank_zero_stderr,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    scope['run_mpi_model_thread'](original, 'mpiexec.exe', 'solver.exe', 2, [])

    assert stopped == [True]
    assert scope['run_status'] == 'stopped'
    assert scope['run_config']['phase'] == 'stopped'
    assert scope['run_process'] is None


def test_mpi_failed_merge_preserves_existing_user_outputs(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_mpi_model_thread')
    function.decorator_list = []

    original = tmp_path / 'original'; original.mkdir()
    sentinel = {'output.nc': b'user output', 'model_run.log': b'user log'}
    for name, data in sentinel.items():
        (original / name).write_bytes(data)
    isolated = tmp_path / 'working'; isolated.mkdir()

    class Process:
        args = ['mpiexec.exe', '-n', '2', 'solver.exe']
        returncode = 0
        def poll(self): return 0

    class FakeMpiRun:
        _log = None
        def __init__(self, *, case, **_kwargs): self.case = Path(case)
        def start(self):
            (self.case / 'model_run.log').write_text('new mpi log', encoding='utf-8')
            return Process()
        def finish(self): raise RuntimeError('fixture merge failure')

    import os, shutil, subprocess, tempfile, types
    fake_mpi = types.ModuleType('mpi_runner')
    fake_mpi.MpiRun = FakeMpiRun
    fake_mpi.merge_case_rank_outputs = lambda *_: None
    fake_mpi.prepare_mpi_case = lambda *_a, **_k: isolated
    monkeypatch.setitem(sys.modules, 'mpi_runner', fake_mpi)
    metrics = RunMetrics(); metrics.start({'nsteps': 10}, now=100)
    scope = {
        'Path': Path, 'time': SimpleNamespace(time=lambda: 101., sleep=lambda _: None),
        'run_status': 'running', 'run_process': None, 'run_logs': [],
        'run_start_time': 100., 'run_case_path': original, 'run_metrics': metrics,
        'run_config': {'solver_mode': 'MPI (2 ranks)', 'phase': 'solving'},
        '_NC_LOCK': threading.RLock(),
        'validate_current_run_outputs': lambda *_a, **_k: {'ready': True},
        '_archive_run_outputs': lambda *_a: pytest.fail('failed merge cannot archive'),
        'nc_open': None, 'subprocess': subprocess, 'shutil': shutil,
        'tempfile': tempfile, 'os': os,
        'IncrementalLogReader': IncrementalLogReader,
        'read_rank_zero_stderr': read_rank_zero_stderr,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    scope['run_mpi_model_thread'](original, 'mpiexec.exe', 'solver.exe', 2, [])

    assert scope['run_status'] == 'failed'
    assert scope['run_config']['phase'] == 'failed'
    assert {name: (original / name).read_bytes() for name in sentinel} == sentinel


def test_mpi_publish_backup_failure_restores_already_moved_user_output(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'run_mpi_model_thread')
    function.decorator_list = []

    original = tmp_path / 'original'; original.mkdir()
    sentinel = {'output.nc': b'user output', 'model_run.log': b'user log'}
    for name, data in sentinel.items():
        (original / name).write_bytes(data)
    isolated = tmp_path / 'working'; isolated.mkdir()

    class Process:
        args = ['mpiexec.exe', '-n', '2', 'solver.exe']
        returncode = 0
        def poll(self): return 0

    class FakeMpiRun:
        _log = None
        def __init__(self, *, case, **_kwargs): self.case = Path(case)
        def start(self):
            (self.case / 'model_run.log').write_text('new mpi log', encoding='utf-8')
            return Process()
        def finish(self):
            output = self.case / 'output.nc'; output.write_bytes(b'new merged output')
            return [output]

    import os, shutil, subprocess, tempfile, types
    fake_mpi = types.ModuleType('mpi_runner')
    fake_mpi.MpiRun = FakeMpiRun
    fake_mpi.merge_case_rank_outputs = lambda *_: None
    fake_mpi.prepare_mpi_case = lambda *_a, **_k: isolated
    monkeypatch.setitem(sys.modules, 'mpi_runner', fake_mpi)
    real_replace = os.replace
    calls = {'count': 0}
    def fail_second_replace(source_path, target_path):
        calls['count'] += 1
        if calls['count'] == 2:
            raise OSError('injected backup failure')
        return real_replace(source_path, target_path)

    metrics = RunMetrics(); metrics.start({'nsteps': 10}, now=100)
    scope = {
        'Path': Path, 'time': SimpleNamespace(time=lambda: 101., sleep=lambda _: None),
        'run_status': 'running', 'run_process': None, 'run_logs': [],
        'run_start_time': 100., 'run_case_path': original, 'run_metrics': metrics,
        'run_config': {'solver_mode': 'MPI (2 ranks)', 'phase': 'solving'},
        '_NC_LOCK': threading.RLock(),
        'validate_current_run_outputs': lambda *_a, **_k: {'ready': True},
        '_archive_run_outputs': lambda *_a: None, 'nc_open': None,
        'subprocess': subprocess, 'shutil': shutil, 'tempfile': tempfile,
        'os': SimpleNamespace(replace=fail_second_replace),
        'IncrementalLogReader': IncrementalLogReader,
        'read_rank_zero_stderr': read_rank_zero_stderr,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    scope['run_mpi_model_thread'](original, 'mpiexec.exe', 'solver.exe', 2, [])

    assert calls['count'] == 3  # two backup attempts, then rollback of output.nc
    assert scope['run_status'] == 'failed'
    assert {name: (original / name).read_bytes() for name in sentinel} == sentinel
