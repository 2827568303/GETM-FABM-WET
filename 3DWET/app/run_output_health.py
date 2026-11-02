"""Check newly emitted model output before declaring or archiving a successful run.

Only the final record is scanned, in bounded tiles. This detects numerical
failure; it does not establish scientific accuracy or long-term stability.
"""
from contextlib import ExitStack
from datetime import datetime
from itertools import product
import math
from pathlib import Path
import time

import numpy as np


_CRITICAL = {'z', 'temp', 'hn', 'd'}


def _tiles(shape, limit):
    sizes, remaining = [1] * len(shape), limit
    for index in range(len(shape) - 1, -1, -1):
        sizes[index] = min(shape[index], remaining)
        if sizes[index] == 0:
            return
        remaining = max(1, remaining // sizes[index])
    for starts in product(*(range(0, size, step) for size, step in zip(shape, sizes))):
        yield tuple(slice(start, min(start + step, size))
                    for start, step, size in zip(starts, sizes, shape))


def _grid_axes(variable, time_axis, bathymetry):
    if bathymetry is None or bathymetry.ndim != 2:
        return None
    dimensions = [dimension for index, dimension in enumerate(variable.dimensions) if index != time_axis]
    shape = [size for index, size in enumerate(variable.shape) if index != time_axis]
    if all(d in dimensions for d in bathymetry.dimensions):
        axes = [dimensions.index(d) for d in bathymetry.dimensions]
        if all(shape[axis] == size for axis, size in zip(axes, bathymetry.shape)):
            return axes
    # flexout names horizontal axes lat/lon, while input grids use y/x.
    if len(shape) >= 2 and tuple(shape[-2:]) == tuple(bathymetry.shape):
        return [len(shape) - 2, len(shape) - 1]
    return None


def _scan_variable(variable, record, time_axis, bathymetry, summary, limit):
    shape = tuple(size for index, size in enumerate(variable.shape) if index != time_axis)
    axes = _grid_axes(variable, time_axis, bathymetry)
    finite_count, unmasked_count, bad_count, finite_wet_count = 0, 0, 0, 0
    critical = variable.name.lower() in _CRITICAL
    for tile in _tiles(shape, limit):
        selection = list(tile)
        selection.insert(time_axis, record)
        values = np.ma.asarray(variable[tuple(selection)])
        data = np.asarray(values.data)
        valid = ~np.ma.getmaskarray(values)
        finite = np.isfinite(data)
        unmasked_count += int(np.count_nonzero(valid))
        finite_count += int(np.count_nonzero(valid & finite))
        bad_count += int(np.count_nonzero(valid & ~finite))
        summary['bytes_read'] += data.nbytes
        summary['max_chunk_elements_read'] = max(summary['max_chunk_elements_read'], data.size)
        if critical and axes is not None:
            depth = np.ma.asarray(bathymetry[tuple(tile[axis] for axis in axes)])
            wet = np.ma.filled(np.isfinite(depth) & (depth > 0), False)
            summary['bytes_read'] += depth.data.nbytes
            summary['max_chunk_elements_read'] = max(summary['max_chunk_elements_read'], depth.size)
            if axes[0] > axes[1]:
                wet = wet.T
            broadcast_shape = [1] * len(shape)
            for axis in axes:
                broadcast_shape[axis] = data.shape[axis]
            wet = wet.reshape(broadcast_shape)
            finite_wet_count += int(np.count_nonzero(valid & finite & wet))
        elif critical and bathymetry is None:
            # Without a grid, still reject completely masked critical output.
            finite_wet_count += int(np.count_nonzero(valid & finite))
    reasons = []
    if bad_count:
        reasons.append(f'{bad_count} nonfinite unmasked values in latest record')
    if critical and finite_wet_count == 0:
        reason = 'no finite unmasked values on the active wet grid'
        if bathymetry is not None and axes is None:
            reason += ' (horizontal dimensions cannot be aligned)'
        reasons.append(reason)
    return dict(variable=variable.name, unmasked_values=unmasked_count,
                finite_values=finite_count, finite_wet_values=finite_wet_count if critical else None,
                reason='; '.join(reasons))


def validate_current_run_outputs(case_path, nc_open, *, started_at=None, max_chunk_elements=262144):
    """Return health of root output.nc and legacy *.2d.nc / *.3d.nc only.

    Pass the process start wall-clock timestamp (or datetime) as started_at to
    ignore stale root files. The caller must hold its run/NetCDF lock and call
    this after the process exits, before archiving. It never reads output/.
    Masked land and completely masked optional diagnostic variables are valid.
    Present critical water fields must have finite, nonmasked wet values.
    """
    begin = time.perf_counter()
    report = dict(ready=False, files=[], skipped=[], bad_variables=[], errors=[], bytes_read=0,
                  max_chunk_elements_read=0, duration_seconds=0.)
    case = Path(case_path).resolve()
    try:
        limit = int(max_chunk_elements)
        if isinstance(max_chunk_elements, bool) or limit < 1:
            raise ValueError('max_chunk_elements must be positive')
        cutoff = started_at.timestamp() if isinstance(started_at, datetime) else started_at
        if cutoff is not None and not math.isfinite(float(cutoff)):
            raise ValueError('started_at must be a finite timestamp')
        candidates = sorted(set(case.glob('*.2d.nc')) | set(case.glob('*.3d.nc')))
        primary = case / 'output.nc'
        if primary.exists():
            candidates.insert(0, primary)
        paths = []
        for path in candidates:
            if path.is_symlink() or not path.is_file() or path.resolve().parent != case:
                report['errors'].append(f'{path.name}: output must be a regular file inside the case')
                continue
            # time.time() divides an integer clock tick by a float billion.
            # Windows stat.st_mtime assembles seconds + a fractional part,
            # which can round the very same FILETIME tick one ULP lower.
            # Use the process clock's conversion for both sides, without a
            # tolerance that would admit genuinely stale output files.
            modified = path.stat().st_mtime_ns / 1e9
            if cutoff is not None and modified < float(cutoff):
                report['skipped'].append(dict(file=path.name, reason='older than current process start'))
                continue
            paths.append(path)
        if not paths:
            report['errors'].append('No current-run output files with model results were produced')
        primary_positive = False
        with ExitStack() as stack:
            grid_path = case / 'bathymetry.nc'
            bathymetry = None
            if grid_path.is_file():
                if grid_path.is_symlink() or grid_path.resolve().parent != case:
                    raise ValueError('bathymetry.nc must be a regular file inside the case')
                grid = stack.enter_context(nc_open(grid_path))
                bathymetry = grid.variables.get('bathymetry')
                if bathymetry is None or bathymetry.ndim != 2:
                    raise ValueError('bathymetry.nc lacks a two-dimensional bathymetry grid')
            for path in paths:
                try:
                    with nc_open(path) as ds:
                        dimension = next((name for name in ds.dimensions if name.lower() == 'time'), None)
                        records = len(ds.dimensions[dimension]) if dimension else 0
                        if path == primary and records > 0:
                            primary_positive = True
                        if records == 0:
                            if path != primary and primary_positive:
                                report['skipped'].append(dict(file=path.name, reason='empty legacy shell; output.nc has records'))
                            else:
                                report['files'].append(dict(file=path.name, records=0, variables=[], bytes_read=0))
                                report['errors'].append(f'{path.name}: no time records')
                            continue
                        file_report = dict(file=path.name, records=records, variables=[], bytes_read=0)
                        report['files'].append(file_report)
                        bytes_before = report['bytes_read']
                        fields = 0
                        grid_variable = bathymetry
                        if grid_variable is None:
                            candidate_grid = ds.variables.get('bathymetry')
                            if candidate_grid is not None and candidate_grid.ndim == 2:
                                grid_variable = candidate_grid
                        for variable in ds.variables.values():
                            if dimension not in variable.dimensions:
                                continue
                            try:
                                numeric = np.issubdtype(variable.dtype, np.number)
                            except TypeError:
                                numeric = False
                            if not numeric:
                                continue
                            if variable.name != dimension:
                                fields += 1
                            health = _scan_variable(variable, records - 1, variable.dimensions.index(dimension),
                                                    grid_variable, report, limit)
                            file_report['variables'].append(health)
                            if health['reason']:
                                report['bad_variables'].append(dict(file=path.name, variable=variable.name,
                                                                    reason=health['reason']))
                        file_report['bytes_read'] = report['bytes_read'] - bytes_before
                        if fields == 0:
                            report['errors'].append(f'{path.name}: no numeric model fields were emitted')
                except (OSError, RuntimeError, ValueError, IndexError, TypeError, OverflowError) as exc:
                    report['errors'].append(f'{path.name}: {exc}')
        report['ready'] = bool(report['files']) and not report['errors'] and not report['bad_variables']
    except (OSError, RuntimeError, ValueError, TypeError, OverflowError) as exc:
        report['errors'].append(str(exc))
    report['duration_seconds'] = round(time.perf_counter() - begin, 6)
    return report
