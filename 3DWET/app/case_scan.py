"""Bounded local scan for existing 3DWET, GETM and GOTM case folders.

The scan stays on this computer. It does not upload paths. A new scan
cancels the one already running. Depth, directory count and time are capped
so it cannot walk an entire disk.
"""
from __future__ import annotations

import os
from pathlib import Path
import threading
import time


MAX_DEPTH = 5
MAX_DIRS = 4000
MAX_SECONDS = 25
DRIVE_CHILD_DEPTH = 2
DRIVE_SKIP = {
    'Windows', 'Program Files', 'Program Files (x86)', '$Recycle.Bin',
    'System Volume Information', 'WinSxS', 'Recovery', '$WinREAgent',
    'PerfLogs', 'Documents and Settings',
}
CHILD_SKIP = {'.git', 'node_modules', '__pycache__', 'WinSxS', '.svn'}


def case_markers(path):
    path = Path(path)
    found = []
    for name in ('getm.inp', 'getm.dat', 'bathymetry.nc', 'fabm.yaml',
                 'gotm.yaml', 'output.nc', 'proxy_engineering.json'):
        try:
            if (path / name).is_file():
                found.append(name)
        except OSError:
            continue
    return found


def is_case_dir(path):
    """A case is a directory with a known marker, not a lone fabm.yaml."""
    path = Path(path)
    try:
        if not path.is_dir():
            return False
    except OSError:
        return False
    markers = set(case_markers(path))
    if markers & {'getm.inp', 'getm.dat', 'bathymetry.nc', 'proxy_engineering.json'}:
        return True
    if 'gotm.yaml' in markers and 'output.nc' in markers:
        return True
    if 'fabm.yaml' in markers and markers & {'bathymetry.nc', 'getm.inp', 'getm.dat', 'gotm.yaml'}:
        return True
    return False


def _add_root(roots, seen, path):
    path = Path(path)
    try:
        if not path.is_dir():
            return
        key = os.path.normcase(str(path.resolve()))
    except OSError:
        return
    if key in seen:
        return
    seen.add(key)
    roots.append(path)


def default_roots(extra_paths=None, home=None, local_app_data=None):
    """Documents, Desktop, Downloads, known case roots, and their drives."""
    home = Path(home or Path.home())
    roots = []
    seen = set()
    for name in ('Documents', 'Desktop', 'Downloads'):
        _add_root(roots, seen, home / name)
    for one_drive in ('OneDrive', 'OneDrive - Personal'):
        base = home / one_drive
        _add_root(roots, seen, base / 'Documents')
        _add_root(roots, seen, base / 'Desktop')
        _add_root(roots, seen, base / 'Downloads')
    if os.name == 'nt':
        base = local_app_data or os.environ.get('LOCALAPPDATA')
        if base:
            _add_root(roots, seen, Path(base) / '3DWET' / 'cases')
    _add_root(roots, seen, Path(r'D:\GETM-FABM-WET-outputs\cases'))
    for raw in extra_paths or []:
        if not raw:
            continue
        path = Path(raw)
        _add_root(roots, seen, path)
        _add_root(roots, seen, path.parent)
    drives = []
    drive_seen = set()
    for path in roots:
        drive = path.drive
        if not drive:
            continue
        root = drive + '\\'
        key = os.path.normcase(root)
        if key in drive_seen:
            continue
        drive_seen.add(key)
        drives.append(root)
    return roots, drives


def _describe(path, markers):
    return {'path': str(path), 'name': path.name, 'markers': list(markers)}


def scan_once(roots, drives=None, *, cancel=None, on_progress=None,
              max_dirs=MAX_DIRS, max_seconds=MAX_SECONDS, max_depth=MAX_DEPTH):
    """Walk the given roots. ``drives`` are only scanned two levels deep."""
    cancel = cancel or threading.Event()
    found = []
    seen_cases = set()
    visited = 0
    started = time.monotonic()
    stack = [(Path(root), 0, max_depth, False) for root in roots]
    for drive in drives or []:
        stack.append((Path(drive), 0, DRIVE_CHILD_DEPTH, True))
    stopped = False
    while stack:
        if cancel.is_set() or visited >= max_dirs or (time.monotonic() - started) >= max_seconds:
            stopped = cancel.is_set()
            break
        path, depth, limit, drive_mode = stack.pop()
        if depth > limit:
            continue
        visited += 1
        if on_progress is not None:
            on_progress(path, visited, found)
        try:
            is_dir = path.is_dir()
        except OSError:
            continue
        if not is_dir:
            continue
        if is_case_dir(path):
            key = os.path.normcase(str(path))
            if key not in seen_cases:
                seen_cases.add(key)
                found.append(_describe(path, case_markers(path)))
            continue
        try:
            children = list(path.iterdir())
        except OSError:
            continue
        for child in children:
            name = child.name
            if name in CHILD_SKIP or name.startswith('.'):
                continue
            if drive_mode and depth == 0 and name in DRIVE_SKIP:
                continue
            try:
                if child.is_dir():
                    stack.append((child, depth + 1, limit, drive_mode))
            except OSError:
                continue
    if on_progress is not None:
        on_progress('', visited, found)
    return {'found': found, 'visited': visited, 'cancelled': bool(cancel.is_set()),
            'truncated': visited >= max_dirs or (time.monotonic() - started) >= max_seconds}


class LocalCaseScan:
    """One scan at a time. Starting another cancels the previous scan."""

    def __init__(self):
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._thread = None
        self._state = {
            'running': False, 'done': True, 'progress': 0, 'current': '',
            'found': [], 'cancelled': False, 'error': '', 'visited': 0,
        }

    def status(self):
        with self._lock:
            return dict(self._state)

    def cancel(self):
        self._cancel.set()
        with self._lock:
            self._state['cancelled'] = True
        return self.status()

    def start(self, roots, drives=None):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                self._cancel.set()
            self._cancel = threading.Event()
            cancel = self._cancel
            self._state = {
                'running': True, 'done': False, 'progress': 0, 'current': '',
                'found': [], 'cancelled': False, 'error': '', 'visited': 0,
            }
        thread = threading.Thread(
            target=self._run, args=(list(roots), list(drives or []), cancel),
            name='3dwet-case-scan', daemon=True)
        with self._lock:
            self._thread = thread
        thread.start()
        return self.status()

    def _run(self, roots, drives, cancel):
        def on_progress(path, visited, found):
            progress = min(99, int(visited * 100 / MAX_DIRS)) if visited else 0
            with self._lock:
                if cancel.is_set() and self._cancel is not cancel:
                    return
                self._state['current'] = str(path) if path else self._state.get('current', '')
                self._state['visited'] = visited
                self._state['found'] = list(found)
                self._state['progress'] = progress
        try:
            result = scan_once(roots, drives, cancel=cancel, on_progress=on_progress)
            with self._lock:
                if self._cancel is not cancel and cancel.is_set():
                    return
                self._state.update(
                    running=False, done=True, progress=100,
                    found=result['found'], visited=result['visited'],
                    cancelled=result['cancelled'], error='')
        except Exception as exc:
            with self._lock:
                self._state.update(running=False, done=True, error=str(exc), progress=100)
