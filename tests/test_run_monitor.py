import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from run_monitor import _cpu_percent, build_run_monitor


def test_monitor_reports_speed_and_stall(tmp_path):
    log = tmp_path / 'model_run.log'
    log.write_text('12:00:00 n=         100\n', encoding='utf-8')
    (tmp_path / 'dianchi.0000.stderr').write_text('rank0 ok\n', encoding='utf-8')
    (tmp_path / 'dianchi.0001.stderr').write_text('STOP 1\n', encoding='utf-8')
    report = build_run_monitor(
        'running',
        {'steps_per_second': 20, 'seconds_since_step': 120, 'elapsed': 130,
         'eta_seconds': 50, 'progress': 10, 'current_step': 100, 'total_steps': 1000},
        {'mpi_ranks': 2, 'omp_threads': 1, 'timestep': 15, 'phase': 'integrating'},
        tmp_path,
        pid=None,
    )
    assert report['mpi_ranks'] == 2
    assert report['omp_threads'] == 1
    assert report['stalled'] is True
    assert report['level'] == 'error'  # STOP 1 in a rank log outranks the stall
    assert abs(report['sim_days_per_wall_hour'] - (20 * 15 * 3600 / 86400)) < 1e-6
    labels = [item['label'] for item in report['consoles']]
    assert '求解器' in labels and 'MPI 0' in labels and 'MPI 1' in labels


def test_cpu_percent_is_nonzero_after_the_baseline_poll():
    proc = subprocess.Popen([sys.executable, '-c', 'while True: pass'])
    try:
        assert _cpu_percent(proc.pid) is None
        time.sleep(0.4)
        value = _cpu_percent(proc.pid)
        assert value is not None and value > 0
    finally:
        proc.kill()
        proc.wait(timeout=5)
