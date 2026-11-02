"""Full-resolution wet topology for scientific scalar views, without map tiles."""
import hashlib
import threading
from collections import OrderedDict
from pathlib import Path
import numpy as np


class Static3DGeometryCache:
    """Small LRU for static 3D grid products keyed by source-file revisions."""
    def __init__(self, max_entries=4):
        self.max_entries = max(1, int(max_entries))
        self._entries = OrderedDict()
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get_or_build(self, key, builder):
        with self._lock:
            cached = self._entries.get(key)
            if cached is not None:
                self.hits += 1
                self._entries.move_to_end(key)
                return cached
            # Build while holding the lock so concurrent frame requests do not
            # reopen and rescan the same native grid at the same time.
            result = builder()
            self.misses += 1
            self._entries[key] = result
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
            return result

    def clear(self):
        with self._lock:
            self._entries.clear()
            self.hits = self.misses = 0

    def info(self):
        with self._lock:
            return {'entries': len(self._entries), 'max_entries': self.max_entries,
                    'hits': self.hits, 'misses': self.misses}


static_3d_geometry_cache = Static3DGeometryCache(max_entries=4)


def file_revision(path):
    """Return a cheap file identity/version token, or None for a missing source."""
    if path is None:
        return None
    try:
        source = Path(path).resolve()
        stat = source.stat()
        return (str(source), int(stat.st_size), int(stat.st_mtime_ns), int(stat.st_ino))
    except (OSError, ValueError):
        return None


def static_3d_geometry_key(case_path, output_path, bathymetry_path, shape, strides, target):
    """Build a case-scoped key from source revisions and display sampling.

    Revisions use resolved path, size, mtime_ns, and inode so warm requests do
    not hash large NetCDF files. A filesystem that preserves all four fields
    across an in-place rewrite cannot signal that rewrite to this cache.
    """
    return (str(Path(case_path).resolve()), file_revision(output_path),
            file_revision(bathymetry_path), tuple(int(value) for value in shape),
            tuple(int(value) for value in strides), int(target))


def metre_axes(dataset, rows, cols, x_name='x', y_name='y'):
    """Accept only finite, monotone one-dimensional axes with explicit units."""
    def axis(name, size):
        variable = dataset.variables.get(name)
        if variable is None or str(getattr(variable, 'units', '')).strip().lower() not in {
                'm', 'meter', 'meters', 'metre', 'metres'}:
            return None
        values = np.ma.asarray(variable[:], dtype='f8')
        if values.ndim != 1 or values.size != size or np.ma.getmaskarray(values).any():
            return None
        values = np.asarray(values)
        if not np.isfinite(values).all():
            return None
        differences = np.diff(values)
        if size > 1 and not (np.all(differences > 0) or np.all(differences < 0)):
            return None
        return values.tolist()
    x, y = axis(x_name, cols), axis(y_name, rows)
    return (x, y) if x is not None and y is not None else (None, None)


def sampled_display_topology(depth, y_indices, x_indices, *, verified_dry_mask=None,
                             x_axis=None, y_axis=None):
    """Build a conservative sampled-cell topology from the complete native grid.

    Each sampled scalar is displayed over the native-cell block beginning at
    its sample index and ending at the next sample index (the final block ends
    at the native domain edge). A block is drawable as water or land only when
    every native cell in it is known and has that same classification. Mixed
    and unknown blocks stay open, so downsampling cannot bridge dry cells or
    turn an incomplete mask into evidence of land.
    """
    source = np.ma.asarray(depth, dtype='f8')
    if source.ndim != 2:
        raise ValueError('display topology depth must be a 2D grid')
    values = np.asarray(np.ma.filled(np.ma.masked_invalid(source), np.nan), dtype='f8')
    rows, cols = values.shape
    wet = np.isfinite(values) & (values > 0)
    dry = np.isfinite(values) & (values <= 0)
    known = wet | dry
    if verified_dry_mask is not None:
        verified_dry = np.asarray(verified_dry_mask, dtype=bool)
        if verified_dry.shape != values.shape:
            raise ValueError('verified dry mask must match the full native grid')
        dry |= verified_dry
        known |= verified_dry

    def starts(indices, size, name):
        result = [int(i) for i in indices]
        if (not result or result[0] != 0 or any(i < 0 or i >= size for i in result)
                or any(b <= a for a, b in zip(result, result[1:]))):
            raise ValueError(f'{name} sample indices must start at zero and increase within the native grid')
        return result

    ys, xs = starts(y_indices, rows, 'y'), starts(x_indices, cols, 'x')
    y_ranges = list(zip(ys, ys[1:] + [rows]))
    x_ranges = list(zip(xs, xs[1:] + [cols]))
    statuses = []
    for y0, y1 in y_ranges:
        row = []
        for x0, x1 in x_ranges:
            block_known = known[y0:y1, x0:x1]
            block_wet, block_dry = wet[y0:y1, x0:x1], dry[y0:y1, x0:x1]
            if not block_known.all():
                status = 'unknown'
            elif block_wet.all():
                status = 'wet'
            elif block_dry.all():
                status = 'dry'
            else:
                status = 'mixed'
            row.append(status)
        statuses.append(row)
    wet_cells = [[status == 'wet' for status in row] for row in statuses]
    land_cells = [[status == 'dry' for status in row] for row in statuses]
    # Side order matches the renderer's quad order: north, east, south, west.
    wall_sides = []
    for j, row in enumerate(statuses):
        walls = []
        for i, status in enumerate(row):
            neighbors = [
                statuses[j-1][i] if j > 0 else None,
                row[i+1] if i+1 < len(row) else None,
                statuses[j+1][i] if j+1 < len(statuses) else None,
                row[i-1] if i > 0 else None,
            ]
            walls.append([status == 'wet' and neighbor == 'dry' for neighbor in neighbors])
        wall_sides.append(walls)

    def selected_edges(axis, size, selected):
        centers = np.arange(size, dtype='f8') if axis is None else np.asarray(axis, dtype='f8')
        if centers.ndim != 1 or centers.size != size or not np.isfinite(centers).all():
            raise ValueError('native display coordinates must be finite 1D axes matching the mask')
        if size > 1:
            diff = np.diff(centers)
            if not (np.all(diff > 0) or np.all(diff < 0)):
                raise ValueError('native display coordinates must be strictly monotone')
            edge = np.concatenate(([centers[0] - diff[0] / 2],
                                   (centers[:-1] + centers[1:]) / 2,
                                   [centers[-1] + diff[-1] / 2]))
        else:
            edge = np.array([centers[0] - .5, centers[0] + .5])
        return edge[np.asarray(selected + [size], dtype=int)].tolist()

    packed = np.stack([wet, dry, known]).astype(np.uint8)
    digest = hashlib.sha256()
    digest.update(np.asarray(values.shape, dtype='<i8').tobytes())
    digest.update(packed.tobytes(order='C'))
    for axis in (x_axis, y_axis):
        if axis is not None:
            digest.update(np.asarray(axis, dtype='<f8').tobytes())
    return {
        'contract': 'sampled-wet-topology-v1',
        'source_shape': [rows, cols],
        'x_indices': xs, 'y_indices': ys,
        'sampling_stride': [ys[1] - ys[0] if len(ys) > 1 else 1,
                            xs[1] - xs[0] if len(xs) > 1 else 1],
        'grid_hash': 'sha256:' + digest.hexdigest(),
        'cell_status': statuses, 'wet_mask': wet_cells, 'land_mask': land_cells,
        'wall_sides': wall_sides,
        'x_edges': selected_edges(x_axis, cols, xs),
        'y_edges': selected_edges(y_axis, rows, ys),
        'mixed_or_unknown_cells': sum(status in ('mixed', 'unknown')
                                      for row in statuses for status in row),
        # The server has already checked every native cell. Keep the number of
        # examined cells as provenance; never serialize three native boolean
        # matrices into every timestep response.
        'mask_cells_examined': int(rows * cols),
    }


def read_scientific_geometry(dataset):
    depth = np.ma.masked_invalid(np.ma.asarray(dataset.variables['bathymetry'][:], dtype='f8'))
    if depth.ndim != 2:
        raise ValueError('bathymetry must be a two-dimensional grid')
    wet = np.ma.filled(depth > 0, False)
    rows, cols = depth.shape

    x, y = metre_axes(dataset, rows, cols)
    projected = x is not None and y is not None
    topology = sampled_display_topology(depth, range(rows), range(cols),
                                        x_axis=x if projected else None,
                                        y_axis=y if projected else None)
    return {'shape': [rows, cols], 'wetMask': wet.tolist(), 'stride': 1,
            'dry_mask': np.ma.filled(depth <= 0, False).tolist(),
            'land_elevation': None,
            'depth': [[float(depth[j, i]) if wet[j, i] else None for i in range(cols)]
                      for j in range(rows)],
            'display_topology': topology,
            'coordinate_mode': 'projected' if projected else 'index',
            'coordinate_units': 'm' if projected else 'index',
            'xc': x if projected else None, 'yc': y if projected else None}


def matching_input_dry_mask(output, grid, shape, ys=slice(None), xs=slice(None)):
    """Supplement masked output land only from the same verified input grid.

    Output fill values are unknown, including negative fill sentinels. A finite
    nonpositive input depth proves dry topology only after axes, wet topology,
    bathymetry values, shape and metre units have been checked independently.
    No input value replaces output bathymetry or scientific fields.
    """
    source = output.variables.get('bathymetry')
    reference = grid.variables.get('bathymetry')
    if source is None or reference is None or source.shape != tuple(shape) or reference.shape != tuple(shape):
        return None
    metre_units = {'m', 'meter', 'meters', 'metre', 'metres'}
    if any(str(getattr(v, 'units', '')).strip().lower() not in metre_units for v in (source, reference)):
        return None
    rows, cols = shape
    ox, oy = metre_axes(output, rows, cols, 'xc', 'yc')
    gx, gy = metre_axes(grid, rows, cols)
    if ox is None or gx is None or not np.array_equal(ox, gx) or not np.array_equal(oy, gy):
        return None
    # Compare every native cell, but keep the two float grids and comparison
    # masks bounded to a row block. The full result mask is the only native
    # sized allocation needed by callers; sampling this check could hide a
    # one-cell channel or stale wet/dry topology.
    rows_per_block = 128
    dry_mask = np.zeros((rows, cols), dtype=bool)
    has_wet = False
    for y0 in range(0, rows, rows_per_block):
        y1 = min(rows, y0 + rows_per_block)
        a = np.ma.filled(np.ma.masked_invalid(
            np.ma.asarray(source[y0:y1, :], dtype='f8')), np.nan)
        b = np.ma.filled(np.ma.masked_invalid(
            np.ma.asarray(reference[y0:y1, :], dtype='f8')), np.nan)
        wet_a = np.isfinite(a) & (a > 0)
        wet_b = np.isfinite(b) & (b > 0)
        if not np.array_equal(wet_a, wet_b):
            return None
        if wet_a.any():
            # Match the prior full-array allclose contract exactly: compare
            # finite wet depths only with the same relative/absolute tolerances.
            if not np.allclose(a[wet_a], b[wet_a], rtol=1e-6, atol=1e-8):
                return None
            has_wet = True
        dry_mask[y0:y1, :] = np.isfinite(b) & (b <= 0)
    if not has_wet:
        return None
    return dry_mask[ys, xs]
