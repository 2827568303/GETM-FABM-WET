"""Runtime monitor payload for the run page.

The numbers come from the solver log and process table. This module does not
start a model and does not read EFDC Explorer.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

_RANK = re.compile(r'(\d{4})\.(stderr|stdout)$', re.IGNORECASE)
_FATAL = re.compile(
    r'(?i)(\[ERROR\]|\bSTOP\s+[1-9]\d*\b|\bfatal\b|out-of-bound|IEEE_|Floating invalid|forrtl:)')


def _tail_lines(path: Path, max_bytes: int = 12000, max_lines: int = 40) -> list[str]:
    try:
        with path.open('rb') as stream:
            stream.seek(0, os.SEEK_END)
            size = stream.tell()
            stream.seek(max(0, size - max_bytes))
            text = stream.read().decode('utf-8', errors='replace')
    except OSError:
        return []
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return lines[-max_lines:]


def _cpu_percent(pid):
    if not pid:
        return None
    try:
        import psutil
        proc = psutil.Process(int(pid))
        # First call establishes a baseline; a later poll returns a real share.
        value = proc.cpu_percent(interval=None)
        if value < 0:
            return None
        return round(float(value), 1)
    except Exception:
        return None


def collect_consoles(case_path, *, include_serial_log=True) -> list[dict]:
    """One scrolling console per MPI rank, plus the launcher log."""
    case = Path(case_path) if case_path else None
    consoles = []
    if case is None or not case.is_dir():
        return consoles
    if include_serial_log:
        serial = case / 'model_run.log'
        if serial.is_file():
            lines = _tail_lines(serial)
            consoles.append({
                'id': 'solver',
                'label': '求解器',
                'file': serial.name,
                'lines': lines,
                'error': any(_FATAL.search(line) for line in lines),
            })
    ranks = []
    try:
        for path in case.iterdir():
            match = _RANK.search(path.name)
            if match and path.is_file():
                ranks.append((int(match.group(1)), path))
    except OSError:
        ranks = []
    for rank, path in sorted(ranks)[:64]:
        lines = _tail_lines(path)
        consoles.append({
            'id': f'rank-{rank}',
            'label': f'MPI {rank}',
            'file': path.name,
            'lines': lines,
            'error': any(_FATAL.search(line) for line in lines),
        })
    return consoles


def build_run_monitor(status, metrics, config, case_path, *, pid=None, stall_seconds=90):
    """Summarise one run for the monitor panel."""
    config = config or {}
    metrics = metrics or {}
    ranks = config.get('mpi_ranks') or 1
    try:
        ranks = max(1, int(ranks))
    except (TypeError, ValueError):
        ranks = 1
    threads = config.get('omp_threads')
    try:
        threads = int(threads) if threads is not None else None
    except (TypeError, ValueError):
        threads = None
    timestep = config.get('timestep')
    try:
        timestep = float(timestep) if timestep is not None else None
    except (TypeError, ValueError):
        timestep = None
    rate = metrics.get('steps_per_second')
    try:
        rate = float(rate) if rate is not None else None
    except (TypeError, ValueError):
        rate = None
    sim_days_per_hour = None
    if rate and rate > 0 and timestep and timestep > 0:
        sim_days_per_hour = rate * timestep * 3600.0 / 86400.0
    since = metrics.get('seconds_since_step')
    try:
        since = float(since) if since is not None else None
    except (TypeError, ValueError):
        since = None
    elapsed = metrics.get('elapsed') or 0
    stalled = (
        status == 'running'
        and config.get('phase') not in {'merging', 'compressing'}
        and (
            (since is not None and since >= stall_seconds)
            or (since is None and elapsed >= stall_seconds and not metrics.get('current_step'))
        )
    )
    consoles = collect_consoles(case_path)
    fatal = status == 'failed' or any(item.get('error') for item in consoles)
    if fatal:
        level = 'error'
        message = '求解器报错。请展开对应进程的输出，查看 STOP / FATAL 行。'
    elif stalled:
        level = 'warn'
        message = (
            f'已 {int(since or elapsed)} 秒没有新的步进。'
            '若进度停在某一百分比且输出不再增长，多半是日志刷屏、数值发散或进程卡住。'
        )
    else:
        level = 'ok'
        message = ''
    return {
        'mpi_ranks': ranks,
        'omp_threads': threads,
        'steps_per_second': rate,
        'sim_days_per_wall_hour': sim_days_per_hour,
        'timestep_seconds': timestep,
        'eta_seconds': metrics.get('eta_seconds'),
        'progress': metrics.get('progress'),
        'current_step': metrics.get('current_step'),
        'total_steps': metrics.get('total_steps'),
        'cpu_percent': _cpu_percent(pid) if status == 'running' else None,
        'seconds_since_step': since,
        'stalled': stalled,
        'level': level,
        'message': message,
        'consoles': consoles,
    }
