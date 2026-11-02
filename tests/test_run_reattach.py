"""Exercise the actual orphan watcher without launching a solver or backend."""
import ast
import os
import sys
import threading
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from run_metrics import RunMetrics
from solver_runtime import log_has_solver_failure

SERVER = Path(__file__).resolve().parents[1] / '3DWET' / 'app' / 'server.py'


@pytest.fixture
def orphan(tmp_path, monkeypatch):
    executable = tmp_path / 'bin' / 'getm_cartesian.exe'
    executable.parent.mkdir()
    executable.touch()
    case = tmp_path / 'case' / 'lake'
    case.mkdir(parents=True)
    (case / 'getm.inp').write_text('&time\n timestep=2\n/\n')
    started = time.time() - 10
    log = case / 'model_run.log'
    log.write_text('n = 42\ngetm: Completed on 20261009\n')
    processes, threads, health_calls, archives = [], [], [], []
    module = ModuleType('psutil')
    class NoSuchProcess(Exception):
        pass
    class AccessDenied(Exception):
        pass
    class Process:
        def __init__(self, pid=1, exe=executable, cwd=case, created=started):
            self.pid, self.path, self.directory, self.created = pid, exe, cwd, created
            self.info = dict(pid=pid, name='getm_cartesian.exe', exe=str(exe), cwd=str(cwd), create_time=created)
            self.running = True
        def exe(self): return str(self.path)
        def cwd(self): return str(self.directory)
        def create_time(self): return self.created
        def is_running(self): return self.running
        def status(self): return 'running' if self.running else 'dead'
        def terminate(self): self.running = False
        def wait(self, timeout=None): return 0
    process = Process()
    processes.append(process)
    def get_process(pid):
        for item in processes:
            if item.pid == pid and item.running:
                return item
        raise NoSuchProcess(pid)
    module.process_iter = lambda attrs=None: list(processes)
    module.Process = get_process
    module.NoSuchProcess, module.AccessDenied, module.STATUS_ZOMBIE = NoSuchProcess, AccessDenied, 'zombie'
    monkeypatch.setitem(sys.modules, 'psutil', module)
    class Thread:
        def __init__(self, target, args=(), **kwargs):
            self.target, self.args = target, args
            threads.append(self)
        def start(self): pass
        def is_alive(self): return False
    def sleep(seconds):
        assert seconds <= 1
        process.running = False
    ready = {'ready': True, 'errors': [], 'bad_variables': []}
    def validate(path, nc_open, **kwargs):
        health_calls.append((path, kwargs))
        return ready
    scope = dict(Path=Path, os=os, np=np, time=SimpleNamespace(time=time.time, sleep=sleep),
                 threading=SimpleNamespace(Thread=Thread), _NC_LOCK=threading.RLock(),
                 EXE_PATH=executable, CASE_DIR=case.parent, LEGACY_CASE_DIR=tmp_path / 'legacy-cases',
                 run_status='idle', run_case_path=None,
                 run_process=None, run_thread=None, run_start_time=None, run_logs=[], run_config={},
                 run_metrics=RunMetrics(), _load_external_cases=lambda: [],
                 parse_getm_inp=lambda path: {'time': {'timestep': 2}},
                 estimate_run_time=lambda path, config: {'nsteps': 100}, nc_open=object(),
                 _reset_run_repair_summary=lambda: None, _capture_run_repair_summary=lambda *args: None,
                 log_has_solver_failure=log_has_solver_failure, validate_current_run_outputs=validate,
                 _archive_run_outputs=lambda path, logs: archives.append(path))
    tree = ast.parse(SERVER.read_text(encoding='utf-8-sig'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_reattach_orphan_model')
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SERVER), 'exec'), scope)
    return SimpleNamespace(scope=scope, case=case, exe=executable, process=process, processes=processes,
                           threads=threads, health_calls=health_calls, archives=archives, ready=ready,
                           Process=Process, log=log, started=started)


def run_watcher(orphan):
    assert len(orphan.threads) == 1
    thread = orphan.threads[0]
    thread.target(*thread.args)


def test_attach_exact_executable_and_cwd_and_restore_metrics(orphan):
    orphan.scope['_reattach_orphan_model']()
    assert orphan.scope['run_process'] is orphan.process
    assert orphan.scope['run_case_path'] == orphan.case
    assert orphan.scope['run_start_time'] == orphan.started
    assert orphan.scope['run_metrics'].current == 42
    assert orphan.scope['run_config']['nsteps'] == 100
    run_watcher(orphan)
    assert orphan.scope['run_status'] == 'completed'
    assert orphan.archives == [orphan.case]
    assert orphan.health_calls == [(orphan.case, {'started_at': orphan.started})]
    assert orphan.scope['run_metrics'].finished is not None
    assert orphan.scope['run_case_path'] is None


@pytest.mark.parametrize('kind', ['other_executable', 'unknown_cwd'])
def test_unrelated_process_is_never_attached(orphan, kind):
    if kind == 'other_executable':
        orphan.process.path = orphan.exe.parent / 'unrelated' / orphan.exe.name
    else:
        orphan.process.directory = orphan.case.parent.parent / 'unregistered'
    orphan.scope['_reattach_orphan_model']()
    assert orphan.scope['run_status'] == 'idle'
    assert orphan.scope['run_process'] is None
    assert not orphan.threads


def test_registered_external_case_uses_real_cwd_not_newest_log(orphan, tmp_path):
    external = tmp_path / 'external'
    external.mkdir()
    (external / 'getm.inp').touch()
    (external / 'model_run.log').write_text('n = 12\ngetm: Completed on 20261009\n')
    orphan.process.directory = external
    orphan.scope['_load_external_cases'] = lambda: [str(external)]
    orphan.scope['_reattach_orphan_model']()
    assert orphan.scope['run_case_path'] == external
    assert orphan.scope['run_metrics'].current == 12


@pytest.mark.parametrize('failure', ['no_marker', 'fatal', 'nan_outputs', 'old_log'])
def test_exit_requires_fresh_completion_log_and_healthy_outputs(orphan, failure):
    if failure == 'no_marker': orphan.log.write_text('n = 42\n')
    if failure == 'fatal': orphan.log.write_text('n = 42\nSTOP 1\ngetm: Completed on 20261009\n')
    if failure == 'nan_outputs':
        orphan.ready.update(ready=False, bad_variables=[{'file': 'output.nc', 'variable': 'temp', 'reason': 'nonfinite'}])
    if failure == 'old_log': os.utime(orphan.log, (orphan.started - 100, orphan.started - 100))
    orphan.scope['_reattach_orphan_model']()
    run_watcher(orphan)
    assert orphan.scope['run_status'] == 'failed'
    assert not orphan.archives


def test_stopped_run_never_changes_to_completed(orphan):
    orphan.scope['_reattach_orphan_model']()
    orphan.scope['run_status'] = 'stopped'
    orphan.process.terminate()
    run_watcher(orphan)
    assert orphan.scope['run_status'] == 'stopped'
    assert not orphan.archives and not orphan.health_calls


def test_pid_reuse_does_not_monitor_unrelated_replacement(orphan):
    orphan.scope['_reattach_orphan_model']()
    replacement = orphan.Process(pid=1, created=orphan.started + 5)
    orphan.processes[:] = [replacement]
    orphan.scope['time'].sleep = lambda seconds: pytest.fail('Must detect changed process identity before waiting')
    run_watcher(orphan)
    assert orphan.scope['run_status'] == 'completed'
    assert replacement.running


def test_ownership_change_does_not_finish_or_clear_new_run(orphan):
    orphan.scope['_reattach_orphan_model']()
    replacement = orphan.Process(pid=2, created=orphan.started + 5)
    orphan.scope['run_process'] = replacement
    orphan.scope['run_metrics'].start({'nsteps': 200})
    orphan.scope['run_case_path'] = orphan.case.parent / 'different'
    run_watcher(orphan)
    assert orphan.scope['run_process'] is replacement
    assert orphan.scope['run_case_path'].name == 'different'
    assert orphan.scope['run_metrics'].finished is None
    assert not orphan.archives


def test_watcher_observes_appended_progress_before_exit(orphan):
    orphan.log.write_text('n = 2\n')
    orphan.scope['_reattach_orphan_model']()
    assert orphan.scope['run_metrics'].current == 2
    def append_and_exit(seconds):
        assert seconds == 1
        with orphan.log.open('a') as stream:
            stream.write('n = 99\ngetm: Completed on 20261009\n')
        orphan.process.running = False
    orphan.scope['time'].sleep = append_and_exit
    run_watcher(orphan)
    assert orphan.scope['run_metrics'].current == 99
    assert orphan.scope['run_status'] == 'completed'


def test_fatal_marker_remains_blocking_after_log_tail_truncation(orphan):
    orphan.log.write_text('STOP 1\n' + ('ordinary line\n' * 10000) + 'getm: Completed on 20261009\n')
    orphan.scope['_reattach_orphan_model']()
    assert not any('STOP 1' in line for line in orphan.scope['run_logs'])
    run_watcher(orphan)
    assert orphan.scope['run_status'] == 'failed'
    assert not orphan.archives
