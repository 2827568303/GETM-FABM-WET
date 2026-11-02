"""Spatial vertical sections: one time record and one grid row/column."""
from pathlib import Path

import numpy as np
from flask import jsonify, request

from result_layers import physical_vertical_grid
from scientific_geometry import metre_axes


def _array(value):
    return np.asarray(np.ma.filled(np.ma.asarray(value, dtype=float), np.nan), dtype=float)


def _json(value):
    value = np.asarray(value)
    return np.where(np.isfinite(value), value, None).tolist()


def _line(var, axis, index, time=None, start=None):
    horizontal = (index, slice(None)) if axis == 'xz' else (slice(None), index)
    key = horizontal if time is None else (time,) + horizontal
    if start is not None:
        key = (time, slice(start, None)) + horizontal
    return _array(var[key])


def read_section(ds, name, time, axis, index, grid=None):
    """Return bottom-to-surface values, positive-down depths and cell edges.

    hn gives actual moving layer thickness at the selected time. In its absence
    only explicit sigma coordinates and positive bathymetry can define depths;
    missing geometry is an error, never a fabricated layer-number depth axis.
    """
    if axis not in ('xz', 'yz'):
        raise ValueError('axis 必须是 xz 或 yz')
    var = ds.variables.get(name)
    if var is None:
        raise ValueError('当前结果中不存在该变量')
    if var.ndim != 4 or 'sigma' not in var.dimensions[1].lower():
        raise ValueError('空间垂向剖面仅支持水柱三维变量；底部/二维变量不支持')
    nt, _, ny, nx = var.shape
    size = ny if axis == 'xz' else nx
    if time < 0 or time >= nt:
        raise ValueError(f'time 超出范围 0–{nt - 1}')
    if index < 0 or index >= size:
        raise ValueError(f'index 超出范围 0–{size - 1}')
    # A physical boundary slot cannot disappear just because this particular
    # row has missing values. Share the bounded whole-variable decision with
    # the volume and layer selectors (normally already cached by inventory).
    start, sigma = physical_vertical_grid(ds, var)
    values = _line(var, axis, index, time, start)
    nz, n = values.shape
    sources = [ds] + ([grid] if grid is not None else [])
    bathy = next((s.variables['bathymetry'] for s in sources
                  if 'bathymetry' in s.variables and s.variables['bathymetry'].shape == (ny, nx)), None)
    if bathy is None:
        raise ValueError('缺少与结果网格一致的 bathymetry，无法确定真实湿网格')
    bottom = _line(bathy, axis, index)
    wet = np.isfinite(bottom) & (bottom > 0)
    for s in sources:
        mask = s.variables.get('mask')
        if mask is not None and mask.shape == (ny, nx):
            wet &= _line(mask, axis, index) > 0
    coord_name = 'xc' if axis == 'xz' else 'yc'
    x, y = metre_axes(ds, ny, nx, 'xc', 'yc')
    if x is None and grid is not None:
        x, y = metre_axes(grid, ny, nx)
    projected = x is not None
    if not projected:
        x, y = list(range(nx)), list(range(ny))
    horizontal = np.asarray(x if axis == 'xz' else y, dtype=float)
    fixed_coordinate = (y if axis == 'xz' else x)[index]
    horizontal_edges = (np.r_[horizontal[0] - .5, horizontal[0] + .5] if n == 1 else
                        np.r_[horizontal[0] - (horizontal[1] - horizontal[0]) / 2,
                              (horizontal[:-1] + horizontal[1:]) / 2,
                              horizontal[-1] + (horizontal[-1] - horizontal[-2]) / 2])
    from vertical_geometry import read_vertical_geometry
    geometry = read_vertical_geometry(ds, var, time, bottom,
        ys=index if axis == 'xz' else slice(None),
        xs=slice(None) if axis == 'xz' else index,
        bottom_units=getattr(bathy, 'units', ''))
    if geometry['position'] != 'center':
        raise ValueError('界面变量不支持层单元剖面，请选择层中心变量或三维点云')
    depths, edges = geometry['center_depth'], geometry['depth_edges']
    valid_column = wet & geometry['valid']
    depth_source = 'hn' if geometry['source'].startswith('hn') else 'sigma'
    values[:, ~valid_column] = np.nan
    depths[:, ~valid_column] = np.nan
    edges[:, ~valid_column] = np.nan
    finite = values[np.isfinite(values)]
    return dict(name=name, axis=axis, index=index, time=time, shape=[nz, n], grid_shape=[ny, nx],
                data=_json(values), depth=_json(depths), depth_edges=_json(edges),
                horizontal=horizontal.tolist(), horizontal_edges=horizontal_edges.tolist(),
                coordinate_name=coord_name, coordinate_units='m' if projected else 'index',
                coordinate_mode='projected' if projected else 'index',
                fixed_coordinate=fixed_coordinate, fixed_coordinate_units='m' if projected else 'index',
                bottom=_json(np.where(wet, bottom, np.nan)), wet=valid_column.tolist(),
                depth_source=depth_source, geometry_source=geometry['source'],
                depth_reference=geometry['depth_reference'], elevation=_json(geometry['center_elevation']),
                units=getattr(var, 'units', ''), long_name=getattr(var, 'long_name', name),
                min=float(finite.min()) if finite.size else None,
                max=float(finite.max()) if finite.size else None)


def register(app, server):
    def section():
        if not server.active_case_path:
            return jsonify(error='未加载案例'), 400
        if server._output_locked():
            return jsonify(error='模型运行中，输出文件正在写入，暂不能读取'), 409
        name = request.args.get('var', 'temp')
        axis = request.args.get('axis', 'xz')
        try:
            time = int(request.args.get('time', '0'))
            index = int(request.args.get('index', '0'))
            if axis not in ('xz', 'yz') or time < 0 or index < 0:
                raise ValueError('axis 必须为 xz/yz，time/index 必须为非负整数')
            files = server.find_output_files(server.active_case_path, name)
            path = files.get('3d') or files.get('2d')
            if not path:
                return jsonify(error='没有输出文件'), 404
            with server.nc_open(path) as ds:
                grid_path = Path(server.active_case_path) / 'bathymetry.nc'
                if grid_path.is_file():
                    with server.nc_open(grid_path) as grid:
                        result = read_section(ds, name, time, axis, index, grid)
                else:
                    result = read_section(ds, name, time, axis, index)
            result.update(server._annotated_output(dict(name=name, units=result['units'],
                                                       long_name=result['long_name']), server.active_case_path))
            return jsonify(result)
        except (ValueError, TypeError, IndexError) as exc:
            return jsonify(error=str(exc)), 400
        except OSError as exc:
            return jsonify(error=f'无法读取剖面输出: {exc}'), 500
    app.add_url_rule('/api/results/section', 'results_spatial_section', section, methods=['GET'])
