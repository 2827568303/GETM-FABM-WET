"""Map native GETM padding slots to the physical vertical result grid."""
from collections import OrderedDict
from pathlib import Path

import numpy as np

_padding_cache = OrderedDict()


def physical_vertical_grid(ds, var):
    """Return the first usable slot and its actual sigma coordinates.

    The native GETM writer reserves k=0 at sigma=-1, whereas flexout starts
    at k=1. Trim only this native boundary slot when it has no valid values.
    A finite boundary (including zero vertical velocity) remains an interface.
    Padding checks are cached by file revision and variable. Large histories
    use representative records, bounded to about one million grid values.
    """
    nlev = var.shape[1]
    sigma_var = ds.variables.get('sigma')
    sigma = (np.asarray(np.ma.filled(sigma_var[:], np.nan), dtype=float)
             if sigma_var is not None else np.array([]))
    start = 0
    native = ('GETM' in str(getattr(ds, 'model', '')).upper()
              and 'flexout' not in str(getattr(ds, 'comment', '')).lower())
    if (native and nlev > 1 and var.dimensions[1] == 'sigma'
            and sigma.size == nlev and np.isclose(sigma[0], -1)
            and np.isclose(sigma[-1], 0) and np.all(np.diff(sigma) > 0)
            and var.shape[0] > 0):
        path = Path(ds.filepath())
        stat = path.stat()
        key = (str(path.resolve()), stat.st_mtime_ns, stat.st_size, var.name, var.shape)
        if key in _padding_cache:
            start = _padding_cache[key]
            _padding_cache.move_to_end(key)
        else:
            ny, nx = var.shape[2:]
            count = max(2, min(var.shape[0], 3000, 1_000_000 // max(1, ny * nx)))
            records = np.unique(np.linspace(0, var.shape[0] - 1, count, dtype=int))
            # Read the same bounded representative slots together. Thousands
            # of individual NetCDF calls per inventory variable are expensive,
            # even when the total sample fits in a small buffer.
            boundary = np.ma.filled(var[records, 0, :, :], np.nan)
            valid = np.isfinite(boundary)
            # hn is a positive layer thickness. The native bottom boundary
            # can be stored as literal zero; it is not an extra water layer.
            if var.name == 'hn':
                valid &= boundary > 0
            start = 0 if valid.any() else 1
            _padding_cache[key] = start
            # Native outputs commonly expose several hundred 4D fields. Keep
            # one slot decision for the active file inventory so selecting a
            # variable again does not reread its boundary history after churn.
            while len(_padding_cache) > 1024:
                _padding_cache.popitem(last=False)
    if sigma.size == nlev:
        coords = sigma[start:]
    elif sigma.size == nlev + 1:
        coords = (0.5 * (sigma[:-1] + sigma[1:]))[start:]
    else:
        coords = np.array([-1 + (k + .5) / nlev for k in range(nlev)])[start:]
    return start, coords.tolist()


def physical_layer_index(level, start, nslots):
    """Resolve a clamped physical layer index and its native storage slot."""
    nlev = nslots - start
    logical = int(level) if int(level) >= 0 else nlev + int(level)
    logical = max(0, min(nlev - 1, logical))
    return logical, start + logical


def time_window_range(ds, var_name, start, end, max_values=2_000_000):
    """Return one stable scalar range and endpoint means for a selected time window.

    Read bounded time hyperslabs rather than loading an entire model history.
    Four-dimensional fields include every physical water layer and trim the
    native GETM boundary slot using the same rule as the 2D/3D renderers.
    """
    if var_name not in ds.variables:
        return None
    var = ds.variables[var_name]
    if var.ndim not in (3, 4) or not var.dimensions or 'time' not in var.dimensions[0].lower():
        raise ValueError(f"Variable {var_name} has no supported time axis")
    ntime = var.shape[0]
    if ntime <= 0:
        return None
    first = max(0, min(ntime - 1, int(start)))
    last = max(first, min(ntime - 1, int(end)))
    level_start = physical_vertical_grid(ds, var)[0] if var.ndim == 4 else 0
    values_per_record = max(1, int(np.prod(var.shape[1:])))
    if var.ndim == 4:
        values_per_record = max(1, int(np.prod(var.shape[2:]))) * max(1, var.shape[1] - level_start)
    block = max(1, min(32, max_values // values_per_record))
    minimum, maximum = np.inf, -np.inf
    endpoint_means = {}
    for lo in range(first, last + 1, block):
        hi = min(last + 1, lo + block)
        slab = var[lo:hi, level_start:, :, :] if var.ndim == 4 else var[lo:hi, :, :]
        slab = np.asarray(np.ma.filled(slab, np.nan), dtype=float)
        valid = np.isfinite(slab)
        if valid.any():
            minimum = min(minimum, float(np.min(slab[valid])))
            maximum = max(maximum, float(np.max(slab[valid])))
        for frame, key in ((first, 'first_mean'), (last, 'last_mean')):
            if lo <= frame < hi:
                values = slab[frame - lo]
                finite = values[np.isfinite(values)]
                endpoint_means[key] = float(np.mean(finite)) if finite.size else None
    if not np.isfinite(minimum) or not np.isfinite(maximum):
        return {'min': None, 'max': None, 'first_mean': None, 'last_mean': None,
                'start': first, 'end': last, 'frames': last - first + 1, 'no_data': True}
    return {'min': minimum, 'max': maximum,
            'first_mean': endpoint_means.get('first_mean'),
            'last_mean': endpoint_means.get('last_mean'),
            'start': first, 'end': last, 'frames': last - first + 1, 'no_data': False}


def depth_weighted_field(ds, var, timestep):
    """Read one record and average valid wet layers using their thickness.

    Prefer dynamic hn. Native GETM's trimmed sigma slots are upper layer
    interfaces; ordinary cell centres use midpoint interfaces. No history
    arrays are loaded, and missing values never contribute to the denominator.
    """
    start, coords = physical_vertical_grid(ds, var)
    hn = ds.variables.get('hn')
    source = None
    weights = None
    if (hn is not None and hn.ndim == 4 and hn.dimensions[0] == var.dimensions[0]
            and hn.dimensions[2:] == var.dimensions[2:]
            and hn.shape[0] > timestep):
        hstart, _ = physical_vertical_grid(ds, hn)
        # A finite field value at the native zero-thickness bottom slot does
        # not make that slot a physical water layer. Align fields to hn's
        # physical slots before applying the dynamic thickness weights.
        value_start = max(start, hstart)
        if hn.shape[1] - hstart == var.shape[1] - value_start:
            start = value_start
            coords = coords[start - physical_vertical_grid(ds, var)[0]:]
            values = np.asarray(np.ma.filled(var[timestep, start:, :, :], np.nan), dtype=float)
            weights = np.asarray(np.ma.filled(hn[timestep, hstart:, :, :], np.nan), dtype=float)
            source = 'hn'
    if weights is None:
        values = np.asarray(np.ma.filled(var[timestep, start:, :, :], np.nan), dtype=float)
    if source is None:
        sigma = np.asarray(coords, dtype=float)
        raw_sigma = ds.variables.get('sigma')
        if raw_sigma is None:
            raise ValueError('缺少实际层厚 hn 或 sigma 坐标，无法计算垂向平均')
        raw = np.asarray(np.ma.filled(raw_sigma[:], np.nan), dtype=float)
        if raw.size == var.shape[1] + 1:
            widths = np.diff(raw)[start:]
            source = 'sigma_interfaces'
        elif start == 1 and raw.size == var.shape[1]:
            widths = np.diff(raw)
            source = 'sigma_interfaces'
        else:
            if (sigma.size != values.shape[0] or not np.all(np.isfinite(sigma))
                    or np.any(np.diff(sigma) <= 0)):
                raise ValueError('sigma 坐标无效，无法计算垂向平均')
            lower, upper = ((0., 1.) if sigma.min() >= 0 else (-1., 0.))
            edges = np.r_[lower, (sigma[:-1] + sigma[1:]) / 2, upper]
            widths = np.diff(edges)
            source = 'sigma_midpoint_interfaces'
        if not np.all(np.isfinite(widths)) or np.any(widths <= 0):
            raise ValueError('sigma 层厚必须为有限正数')
        weights = np.broadcast_to(widths[:, None, None], values.shape)
    valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    bathy = ds.variables.get('bathymetry')
    if bathy is not None:
        depth = np.asarray(np.ma.filled(bathy[:], np.nan), dtype=float)
        valid &= np.isfinite(depth)[None, :, :] & (depth > 0)[None, :, :]
    mask = ds.variables.get('mask')
    if mask is not None and mask.ndim == 2 and mask.shape == values.shape[1:]:
        wet = np.asarray(np.ma.filled(mask[:], 0)) > 0
        valid &= wet[None, :, :]
    denominator = np.sum(np.where(valid, weights, 0), axis=0)
    numerator = np.sum(np.where(valid, values, 0) * np.where(valid, weights, 0), axis=0)
    field = np.full(values.shape[1:], np.nan)
    np.divide(numerator, denominator, out=field, where=denominator > 0)
    return field, source
