"""Track solver progress independently of its bounded diagnostic log tail."""
import re
import math
import threading
import time
from pathlib import Path

_STEP = re.compile(r'^\s*(?:\d{2}:\d{2}:\d{2}(?:\.\d+)?\s+)?n\s*=\s*(\d+)\b', re.M)
_PHYSICS_DIAG = re.compile(
    r'^GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=(?P<step>\d+) '
    r'sim_time=(?P<time>\S+) global_i=(?P<i>\d+) global_j=(?P<j>\d+) '
    r'(?:owner_rank=(?P<owner>\d+) )?'
    r'z_surface_m=(?P<z>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'H_static_m=(?P<h>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'D_total_m=(?P<d>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?)'
    r'(?: velocity_status=available surface_k=(?P<surface_k>\d+) bottom_k=(?P<bottom_k>\d+) '
    r'u_surface_grid_m_s=(?P<us>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'v_surface_grid_m_s=(?P<vs>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'speed_surface_m_s=(?P<ss>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'u_bottom_grid_m_s=(?P<ub>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'v_bottom_grid_m_s=(?P<vb>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?) '
    r'speed_bottom_m_s=(?P<sb>[+-]?[\d.]+(?:[EeDd][+-]?\d+)?)'
    r'| velocity_status=unavailable reason=(?P<velocity_reason>[A-Za-z0-9_.-]+))?\s*$', re.M)
_PHYSICS_STATE = re.compile(
    r'^GETM_PHYSICS_DIAG status=(?P<status>unsupported|unavailable) '
    r'reason=(?P<reason>[A-Za-z0-9_.-]+)(?: completed_step=(?P<step>\d+))?\s*$', re.M)


class IncrementalLogReader:
    """Read appended text without losing delayed, partial, or rewritten log data."""

    def __init__(self, encoding='utf-8', anchor_size=128):
        self.encoding = encoding
        self.anchor_size = max(1, int(anchor_size))
        self.path = None
        self.position = 0
        self.anchor = b''
        self.pending = ''
        self.last_error = None

    def _reset(self, path=None):
        self.path = path
        self.position = 0
        self.anchor = b''
        self.pending = ''

    def read(self, path=None, *, final=False):
        """Return complete appended lines; flush an unterminated final line at EOF."""
        resolved = Path(path).resolve() if path is not None else None
        if resolved is not None and resolved != self.path:
            self._reset(resolved)

        raw = b''
        if resolved is not None:
            try:
                with resolved.open('rb') as stream:
                    size = stream.seek(0, 2)
                    if size < self.position:
                        self.position = 0
                        self.anchor = b''
                        self.pending = ''
                    elif self.position and self.anchor:
                        anchor_start = self.position - len(self.anchor)
                        stream.seek(anchor_start)
                        if stream.read(len(self.anchor)) != self.anchor:
                            # The file was replaced or rewritten past the last read point.
                            self.position = 0
                            self.anchor = b''
                            self.pending = ''
                    stream.seek(self.position)
                    raw = stream.read()
                    self.position = stream.tell()
                self.anchor = (self.anchor + raw)[-self.anchor_size:]
                self.last_error = None
            except OSError as error:
                self.last_error = str(error)

        text = self.pending + raw.decode(self.encoding, errors='replace')
        if final:
            self.pending = ''
            return text
        last_newline = max(text.rfind('\n'), text.rfind('\r'))
        if last_newline < 0:
            self.pending = text
            return ''
        complete = text[:last_newline + 1]
        self.pending = text[last_newline + 1:]
        return complete


def read_rank_zero_stderr(case, reader, *, final=False):
    """Poll the MPI rank-0 stderr log, tolerating its late creation and I/O errors."""
    try:
        candidates = sorted(Path(case).glob('*.0000.stderr'))
    except OSError as error:
        reader.last_error = str(error)
        return reader.read(None, final=final)
    return reader.read(candidates[0] if candidates else None, final=final)


class RunMetrics:
    def __init__(self):
        self.lock = threading.RLock()
        self.started = None
        self.finished = None
        self.current = None
        self.estimate = {}
        self.supports_getm_progress = False
        self.supports_physics_diag = False
        self.last_observed_at = None
        self.steps_per_second = None
        self.physics_diagnostic = None

    def start(self, estimate, now=None):
        with self.lock:
            self.started = time.time() if now is None else now
            self.finished = None
            self.current = None
            self.estimate = dict(estimate)
            self.supports_getm_progress = bool(self.estimate.get('nsteps')) and self.estimate.get('engine') != 'official_gotm_reference_working_copy'
            # GETM's MPI worker reads rank-zero stderr and can consume the same
            # complete, solver-owned point record as the serial worker. GOTM
            # reference runs remain excluded by supports_getm_progress above.
            self.supports_physics_diag = self.supports_getm_progress
            self.last_observed_at = None
            self.steps_per_second = None
            self.physics_diagnostic = None

    def observe(self, text, now=None, source='solver_log'):
        if not self.supports_getm_progress:
            return
        steps = [int(match) for match in _STEP.findall(text)]
        diagnostics = list(_PHYSICS_DIAG.finditer(text)) if self.supports_physics_diag else []
        state_records = list(_PHYSICS_STATE.finditer(text)) if self.supports_physics_diag else []
        if self.supports_physics_diag:
            available_match = diagnostics[-1] if diagnostics else None
            state_match = state_records[-1] if state_records else None
            latest_match = max(
                (match for match in (available_match, state_match) if match is not None),
                key=lambda match: match.start(), default=None)
            is_mpi = str(self.estimate.get('solver_mode', '')).startswith('MPI')
            trusted_source = source == 'rank0_stderr' if is_mpi else source == 'solver_log'
            if latest_match is not None and trusted_source:
                if latest_match.re is _PHYSICS_DIAG:
                    diagnostic = latest_match
                    try:
                        values = [float(diagnostic.group(key).replace('D', 'E').replace('d', 'e'))
                                  for key in ('z', 'h', 'd')]
                        completed_step = int(diagnostic.group('step'))
                        owner_value = diagnostic.group('owner')
                        owner_rank = int(owner_value) if owner_value is not None else None
                    except (TypeError, ValueError):
                        values = []
                        owner_rank = None
                    if ((not is_mpi or owner_rank is not None) and len(values) == 3
                            and all(math.isfinite(value) for value in values)):
                        entry = {
                            'status': 'available', 'source': source,
                            'kind': 'center_wet_T', 'completed_step': completed_step,
                            'sim_time': diagnostic.group('time'),
                            'global_i': int(diagnostic.group('i')),
                            'global_j': int(diagnostic.group('j')),
                            'z_surface_m': values[0], 'H_static_m': values[1],
                            'D_total_m': values[2],
                        }
                        if owner_rank is not None:
                            entry['owner_rank'] = owner_rank
                        velocity_status = diagnostic.group('velocity_reason')
                        if velocity_status is not None:
                            entry['velocity_status'] = 'unavailable'
                            entry['velocity_reason'] = velocity_status
                        elif diagnostic.group('surface_k') is not None:
                            try:
                                velocity_values = [float(diagnostic.group(key).replace('D', 'E').replace('d', 'e'))
                                                   for key in ('us', 'vs', 'ss', 'ub', 'vb', 'sb')]
                                surface_k = int(diagnostic.group('surface_k'))
                                bottom_k = int(diagnostic.group('bottom_k'))
                            except (TypeError, ValueError):
                                velocity_values = []
                                surface_k = bottom_k = 0
                            speed_tol_s = max(1e-6, abs(velocity_values[2]) * 2e-6) if len(velocity_values) == 6 else 0
                            speed_tol_b = max(1e-6, abs(velocity_values[5]) * 2e-6) if len(velocity_values) == 6 else 0
                            velocity_valid = (
                                len(velocity_values) == 6 and all(math.isfinite(value) for value in velocity_values)
                                and surface_k > 0 and bottom_k > 0 and surface_k >= bottom_k
                                and abs(math.hypot(velocity_values[0], velocity_values[1]) - velocity_values[2]) <= speed_tol_s
                                and abs(math.hypot(velocity_values[3], velocity_values[4]) - velocity_values[5]) <= speed_tol_b
                            )
                            if velocity_valid:
                                entry.update({
                                    'velocity_status': 'available', 'surface_k': surface_k, 'bottom_k': bottom_k,
                                    'u_surface_grid_m_s': velocity_values[0], 'v_surface_grid_m_s': velocity_values[1],
                                    'speed_surface_m_s': velocity_values[2], 'u_bottom_grid_m_s': velocity_values[3],
                                    'v_bottom_grid_m_s': velocity_values[4], 'speed_bottom_m_s': velocity_values[5],
                                })
                            else:
                                entry = None
                        depth_tolerance = max(1e-5, abs(values[2]) * 2e-6)
                        if (entry is not None and completed_step >= 0 and entry['global_i'] >= 1 and entry['global_j'] >= 1
                                and entry['H_static_m'] > 0 and entry['D_total_m'] > 0
                                and abs(entry['D_total_m'] - (entry['z_surface_m'] + entry['H_static_m'])) <= depth_tolerance):
                            with self.lock:
                                self.physics_diagnostic = entry
                            steps.append(completed_step + 1)
                else:
                    state = latest_match.group('status')
                    entry = {'status': state, 'source': source, 'reason': latest_match.group('reason')}
                    if latest_match.group('step') is not None:
                        entry['completed_step'] = int(latest_match.group('step'))
                    with self.lock:
                        self.physics_diagnostic = entry
        if steps:
            observed_at = time.time() if now is None else now
            with self.lock:
                # GETM writes n immediately before doing that step. GOTM has
                # a separate log format and therefore leaves progress unknown.
                completed = max(0, max(steps) - 1)
                if self.current is not None and completed <= self.current:
                    return
                if self.current is not None and self.last_observed_at is not None:
                    interval = observed_at - self.last_observed_at
                    if interval > 0:
                        self.steps_per_second = (completed - self.current) / interval
                self.current = completed
                self.last_observed_at = observed_at

    def finish(self, now=None):
        with self.lock:
            self.finished = time.time() if now is None else now

    def snapshot(self, status, now=None):
        with self.lock:
            now = time.time() if now is None else now
            elapsed = max(0, (self.finished if self.finished is not None else now) - self.started) if self.started is not None else 0
            try:
                total = int(self.estimate.get('nsteps') or 0)
            except (TypeError, ValueError):
                total = 0
            total = total if total > 0 else None
            current = total if status == 'completed' and total is not None else self.current
            progress = min(99.9, 100 * current / total) if total and current is not None else None
            if status == 'completed':
                progress = 100
            rate = self.steps_per_second
            eta = max(0, (total - current) / rate) if status == 'running' and total and current is not None and rate and rate > 0 else None
            since_step = (now - self.last_observed_at) if self.last_observed_at is not None else None
            return dict(elapsed=elapsed, current_step=current, total_steps=total, progress=progress,
                        steps_per_second=rate, eta_seconds=eta, eta_minutes=eta / 60 if eta is not None else None,
                        seconds_since_step=since_step,
                        physics_diagnostic=dict(self.physics_diagnostic) if self.physics_diagnostic else None)
