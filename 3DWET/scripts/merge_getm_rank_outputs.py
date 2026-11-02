"""Safely assemble GETM/FABM rank NetCDF files on a reference grid.

Geographic shards are placed with lonc/latc. Cartesian GETM writes only the
1D xc/yc axes; those are placed on the reference xc/yc or bathymetry x/y.
"""
from __future__ import annotations
import argparse, os, tempfile
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

DEFAULT_MERGE_MEMORY_BUDGET_BYTES = 128 * 1024 * 1024


def _same(a, b):
    a, b = np.ma.asarray(a), np.ma.asarray(b)
    return a.shape == b.shape and np.array_equal(np.ma.getmaskarray(a), np.ma.getmaskarray(b)) and np.array_equal(a.filled(0), b.filled(0), equal_nan=True)


def _shape_signature(dimensions, shape):
    """Keep time/vertical extents strict while allowing rank-local x/y sizes."""
    return tuple(None if dim in ('xc', 'yc') else size
                 for dim, size in zip(dimensions, shape))


def _reference_axis(dataset, names):
    """Return a 1D coordinate from the first matching variable name."""
    for name in names:
        variable = dataset.variables.get(name)
        if variable is not None and variable.ndim == 1 and len(variable):
            values = np.ma.asarray(variable[:])
            if np.ma.getmaskarray(values).any():
                return None
            return np.asarray(np.ma.getdata(values), dtype=np.float64)
    return None


def _match_axis(axis, values, atol):
    """Index where values sit inside axis, or None when they do not."""
    values = np.ma.asarray(values, dtype=np.float64).reshape(-1)
    if values.size == 0 or np.ma.getmaskarray(values).any() or values.size > axis.size:
        return None
    values = np.asarray(np.ma.getdata(values), dtype=np.float64)
    index = int(np.argmin(np.abs(axis - values[0])))
    end = index + values.size
    if end > axis.size or abs(float(axis[index]) - float(values[0])) > atol:
        return None
    if not np.allclose(axis[index:end], values, atol=atol, rtol=0, equal_nan=True):
        return None
    return index


def _chunk_plan(dimensions, shape, dtype, nx, ny, requested_records, budget_bytes):
    """Conservatively bound one variable's working arrays in both time and space."""
    dims = tuple(dimensions)
    time_axis = dims.index('time') if 'time' in dims else None
    has_xy = 'yc' in dims and 'xc' in dims
    itemsize = np.dtype(dtype).itemsize
    extra = 1
    for dim, length in zip(dims, shape):
        if dim not in ('time', 'yc', 'xc'):
            extra *= int(length)
    # Account for output and incoming data copies, masks, overlap selections,
    # and comparisons. This is an array-workspace budget, excluding NetCDF's
    # own caches and the Python interpreter.
    bytes_per_cell = max(1, extra) * (8 * itemsize + 16)
    spatial_cells = ny * nx if has_xy else 1
    if has_xy:
        full_cells_per_record = spatial_cells
    else:
        full_cells_per_record = 1
        for dim, length in zip(dims, shape):
            if dim != 'time':
                full_cells_per_record *= int(length)
    bytes_per_record = max(1, full_cells_per_record) * bytes_per_cell
    records = max(1, min(int(requested_records), int(budget_bytes) // bytes_per_record))
    tile_cells = max(1, int(budget_bytes) // (records * bytes_per_cell))
    return time_axis, records, tile_cells, bytes_per_cell


def _spatial_tiles(nx, ny, max_cells):
    width = min(nx, max(1, int(max_cells)))
    height = min(ny, max(1, int(max_cells) // width))
    for y0 in range(0, ny, height):
        for x0 in range(0, nx, width):
            yield y0, min(ny, y0 + height), x0, min(nx, x0 + width)


def merge_rank_outputs(shards, reference, destination, *, atol=1e-5,
                       time_chunk_records=8,
                       max_chunk_bytes=DEFAULT_MERGE_MEMORY_BUDGET_BYTES):
    """Merge rank files with bounded temporal and spatial working arrays."""
    shards = sorted(map(Path, shards))
    reference, destination = Path(reference), Path(destination)
    if isinstance(time_chunk_records, bool) or int(time_chunk_records) < 1:
        raise ValueError('time_chunk_records must be a positive integer')
    time_chunk_records = int(time_chunk_records)
    if isinstance(max_chunk_bytes, bool) or int(max_chunk_bytes) < 1:
        raise ValueError('max_chunk_bytes must be a positive integer')
    max_chunk_bytes = int(max_chunk_bytes)
    if not shards:
        raise ValueError('No rank shards supplied')
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    sources = []
    try:
        with Dataset(reference) as ref:
            sources = [Dataset(path) for path in shards]
            first = sources[0]
            schema = {n: (v.dimensions, str(v.dtype), tuple(v.shape), v.ncattrs())
                      for n, v in first.variables.items()}
            shard_lonlat = {'lonc', 'latc'} <= set(schema)
            glon = glat = None
            ref_x = ref_y = None
            if shard_lonlat:
                if not {'lonc', 'latc'} <= set(ref.variables):
                    raise ValueError('Reference requires lonc and latc')
                glon, glat = np.asarray(ref['lonc'][:]), np.asarray(ref['latc'][:])
                if glon.ndim != 2 or glat.shape != glon.shape:
                    raise ValueError('Reference coordinates must be matching 2D arrays')
                ny, nx = glon.shape
            else:
                ref_x = _reference_axis(ref, ('xc', 'x'))
                ref_y = _reference_axis(ref, ('yc', 'y'))
                if ref_x is None or ref_y is None or 'xc' not in schema or 'yc' not in schema:
                    raise ValueError('Shards require lonc and latc')
                ny, nx = len(ref_y), len(ref_x)
            model = first.data_model
            globals_ = {n: first.getncattr(n) for n in first.ncattrs()}
            attrs = {n: {a: v.getncattr(a) for a in v.ncattrs() if a != '_FillValue'}
                     for n, v in first.variables.items()}
            fills = {n: v.getncattr('_FillValue') for n, v in first.variables.items()
                     if '_FillValue' in v.ncattrs()}
            tiles = []
            coverage = np.zeros((ny, nx), dtype=np.uint8)
            for path, src in zip(shards, sources):
                actual = {n: (v.dimensions, str(v.dtype), tuple(v.shape), v.ncattrs())
                          for n, v in src.variables.items()}
                if set(actual) != set(schema):
                    raise ValueError(f'Variable schema mismatch: {path}')
                for n, got in actual.items():
                    if got != schema[n] and (got[:2] != schema[n][:2]
                            or got[3] != schema[n][3]
                            or _shape_signature(got[0], got[2]) != _shape_signature(schema[n][0], schema[n][2])):
                        raise ValueError(f'Variable schema mismatch: {n} in {path}')
                if shard_lonlat:
                    lonvar, latvar = src['lonc'][:], src['latc'][:]
                    lon, lat = np.asarray(lonvar), np.asarray(latvar)
                    lonmask, latmask = np.ma.getmaskarray(lonvar), np.ma.getmaskarray(latvar)
                    h, w = lon.shape
                    valid = np.isfinite(lon) & np.isfinite(lat) & ~lonmask & ~latmask & (np.abs(lon) < 360) & (np.abs(lat) < 90)
                    if not valid.any():
                        raise ValueError(f'No valid coordinate pairs: {path}')
                    sy, sx = np.argwhere(valid)[0]
                    dist = np.hypot(glon - lon[sy, sx], glat - lat[sy, sx])
                    gy, gx = np.unravel_index(np.argmin(dist), dist.shape)
                    iy, ix = gy - sy, gx - sx
                    if iy < 0 or ix < 0:
                        raise ValueError(f'Coordinate block starts outside reference grid: {path}')
                    # GETM may write a fixed-size rank-local buffer at the last
                    # decomposition edge. Cells beyond the global grid are padding
                    # and must be masked in both coordinate arrays.
                    h_in, w_in = min(h, ny - iy), min(w, nx - ix)
                    if h_in <= 0 or w_in <= 0:
                        raise ValueError(f'Coordinate block outside reference grid: {path}')
                    outside = np.ones((h, w), dtype=bool)
                    outside[:h_in, :w_in] = False
                    if np.any(outside & (~lonmask | ~latmask)):
                        raise ValueError(f'Unmasked coordinate padding outside reference grid: {path}')
                    rlon = np.ma.asarray(ref['lonc'][iy:iy+h_in, ix:ix+w_in])
                    rlat = np.ma.asarray(ref['latc'][iy:iy+h_in, ix:ix+w_in])
                    if (not np.array_equal(np.ma.getmaskarray(rlon), lonmask[:h_in, :w_in])
                            or not np.array_equal(np.ma.getmaskarray(rlat), latmask[:h_in, :w_in])
                            or not np.allclose(np.asarray(rlon), lon[:h_in, :w_in], atol=atol, rtol=0, equal_nan=True)
                            or not np.allclose(np.asarray(rlat), lat[:h_in, :w_in], atol=atol, rtol=0, equal_nan=True)):
                        raise ValueError(f'Coordinate block mismatch: {path}')
                else:
                    ix = _match_axis(ref_x, src['xc'][:], atol)
                    iy = _match_axis(ref_y, src['yc'][:], atol)
                    if ix is None or iy is None:
                        raise ValueError(f'Coordinate block mismatch: {path}')
                    h_in, w_in = len(src.dimensions['yc']), len(src.dimensions['xc'])
                overlap = coverage[iy:iy+h_in, ix:ix+w_in].astype(bool)
                coverage[iy:iy+h_in, ix:ix+w_in] = 1
                tiles.append((iy, ix, h_in, w_in, overlap))
            if not coverage.all():
                raise ValueError(f'Incomplete coverage: {int((coverage == 0).sum())} cells missing')

            fd, tmpname = tempfile.mkstemp(prefix=f'.{destination.name}.', suffix='.tmp', dir=destination.parent)
            os.close(fd)
            tmp = Path(tmpname)
            with Dataset(tmp, 'w', format=model) as result:
                for n, value in globals_.items():
                    result.setncattr(n, value)
                for n, d in first.dimensions.items():
                    length = nx if n == 'xc' else ny if n == 'yc' else len(d)
                    result.createDimension(n, None if d.isunlimited() else length)
                for n, v in first.variables.items():
                    kwargs = {'fill_value': fills[n]} if n in fills else {}
                    filters = v.filters() or {}
                    if filters.get('zlib'):
                        kwargs.update(zlib=True, complevel=filters.get('complevel', 4), shuffle=filters.get('shuffle', True))
                    out = result.createVariable(n, v.dtype, v.dimensions, **kwargs)
                    for attr, value in attrs[n].items():
                        out.setncattr(attr, value)

                for name, template in first.variables.items():
                    dims = template.dimensions
                    time_axis, record_chunk, tile_cells, bytes_per_cell = _chunk_plan(
                        dims, template.shape, template.dtype, nx, ny,
                        time_chunk_records, max_chunk_bytes)
                    ntime = len(first.dimensions['time']) if time_axis is not None else 1
                    # The budget reduces temporal chunk size first. If one full
                    # record still exceeds it, spatial variables use bounded tiles.
                    time_blocks = [(t, min(t + record_chunk, ntime))
                                   for t in range(0, ntime, record_chunk)]
                    if time_axis is None:
                        time_blocks = [(None, None)]
                    for t0, t1 in time_blocks:
                        src_sl = [slice(None)] * template.ndim
                        out_sl = [slice(None)] * template.ndim
                        if time_axis is not None:
                            src_sl[time_axis] = slice(t0, t1)
                            out_sl[time_axis] = slice(t0, t1)
                        src_sl = tuple(src_sl) if template.ndim else Ellipsis
                        out_sl = tuple(out_sl) if template.ndim else Ellipsis
                        if name in ('ioff', 'joff') and template.ndim == 0:
                            result[name][...] = 0
                        elif dims == ('xc',) or dims == ('yc',):
                            length = nx if dims == ('xc',) else ny
                            axis_chunk = max(1, max_chunk_bytes // max(1, 8 * template.dtype.itemsize + 16))
                            for a0 in range(0, length, axis_chunk):
                                a1 = min(length, a0 + axis_chunk)
                                axis_values = np.ma.masked_all(a1 - a0, dtype=template.dtype)
                                for src, (iy, ix, h, w, overlap) in zip(sources, tiles):
                                    start, width, axis_overlap = (ix, w, np.any(overlap, axis=0)) if dims == ('xc',) else (iy, h, np.any(overlap, axis=1))
                                    lo, hi = max(start, a0), min(start + width, a1)
                                    if lo >= hi:
                                        continue
                                    local = slice(lo - start, hi - start)
                                    out_local = slice(lo - a0, hi - a0)
                                    ov = axis_overlap[local]
                                    prior = axis_values[out_local]
                                    incoming = np.ma.asarray(src[name][local])
                                    if ov.any() and not _same(prior[ov], incoming[ov]):
                                        raise ValueError(f'Conflicting overlap coordinate {name}: {src.filepath()}')
                                    axis_values[out_local] = np.ma.where(ov, prior, incoming) if ov.any() else incoming
                                result[name][a0:a1] = axis_values
                        elif 'yc' in dims and 'xc' in dims:
                            yi, xi = dims.index('yc'), dims.index('xc')
                            for gy0, gy1, gx0, gx1 in _spatial_tiles(nx, ny, tile_cells):
                                block_shape = tuple((t1-t0) if i == time_axis else gy1-gy0 if dim == 'yc' else gx1-gx0 if dim == 'xc' else length
                                                    for i, (dim, length) in enumerate(zip(dims, template.shape)))
                                data = np.zeros(block_shape, dtype=template.dtype)
                                mask = np.ones(block_shape, dtype=bool)
                                for src, (iy, ix, h, w, overlap) in zip(sources, tiles):
                                    gylo, gyhi = max(gy0, iy), min(gy1, iy+h)
                                    gxlo, gxhi = max(gx0, ix), min(gx1, ix+w)
                                    if gylo >= gyhi or gxlo >= gxhi:
                                        continue
                                    src_sl = [slice(None)] * len(dims)
                                    dst_sl = [slice(None)] * len(dims)
                                    if time_axis is not None:
                                        src_sl[time_axis] = slice(t0, t1)
                                        dst_sl[time_axis] = slice(None)
                                    src_sl[yi] = slice(gylo - iy, gyhi - iy)
                                    src_sl[xi] = slice(gxlo - ix, gxhi - ix)
                                    dst_sl[yi] = slice(gylo - gy0, gyhi - gy0)
                                    dst_sl[xi] = slice(gxlo - gx0, gxhi - gx0)
                                    src_sl, dst_sl = tuple(src_sl), tuple(dst_sl)
                                    new = np.ma.asarray(src[name][src_sl])
                                    overlap_slice = overlap[gylo - iy:gyhi - iy, gxlo - ix:gxhi - ix]
                                    ovshape = [1] * len(dims)
                                    ovshape[yi], ovshape[xi] = overlap_slice.shape
                                    ov = np.broadcast_to(overlap_slice.reshape(ovshape), new.shape)
                                    old_data, old_mask = data[dst_sl], mask[dst_sl]
                                    new_data = np.asarray(np.ma.filled(new, 0), dtype=template.dtype)
                                    new_mask = np.ma.getmaskarray(new)
                                    if ov.any():
                                        if not np.array_equal(old_mask[ov], new_mask[ov]):
                                            raise ValueError(f'Conflicting overlap masks for {name}: {src.filepath()}')
                                        comparable = ov & ~old_mask & ~new_mask
                                        if not np.allclose(old_data[comparable], new_data[comparable], atol=atol, rtol=0, equal_nan=True):
                                            raise ValueError(f'Conflicting overlap values for {name}: {src.filepath()}')
                                    assign = ~ov
                                    old_data[assign] = new_data[assign]
                                    old_mask[assign] = new_mask[assign]
                                    data[dst_sl], mask[dst_sl] = old_data, old_mask
                                result_sl = [slice(None)] * len(dims)
                                if time_axis is not None:
                                    result_sl[time_axis] = slice(t0, t1)
                                result_sl[yi], result_sl[xi] = slice(gy0, gy1), slice(gx0, gx1)
                                result[name][tuple(result_sl)] = np.ma.array(data, mask=mask, copy=False)
                        else:
                            baseline = np.ma.asarray(first[name][src_sl])
                            for src in sources[1:]:
                                if not _same(baseline, np.ma.asarray(src[name][src_sl])):
                                    raise ValueError(f'Rank-inconsistent non-spatial variable {name}: {src.filepath()}')
                            result[name][out_sl] = baseline
                result.sync()
        os.link(tmp, destination)
        tmp.unlink()
        tmp = None
        return destination
    finally:
        for src in sources:
            src.close()
        if tmp is not None:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('reference'); p.add_argument('destination'); p.add_argument('shards',nargs='+'); a=p.parse_args(); print(merge_rank_outputs(a.shards,a.reference,a.destination))
