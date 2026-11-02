"""Ordinary result time series only read selected frames and bounded spatial slabs."""
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

APP_DIR = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP_DIR))
import server


class RecordingVariable:
    def __init__(self, variable):
        self.variable = variable
        self.reads = []

    def __getattr__(self, name):
        return getattr(self.variable, name)

    def __getitem__(self, key):
        self.reads.append(key)
        return self.variable[key]


class RecordingDataset:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.context = server.nc_open_original(self.path)
        self.dataset = self.context.__enter__()
        self.variables = {name: RecordingVariable(variable)
                          for name, variable in self.dataset.variables.items()}
        return self

    def __exit__(self, *args):
        return self.context.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.dataset, name)


@pytest.fixture
def timeseries_file(tmp_path, monkeypatch):
    path = tmp_path / 'sample.3d.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.comment = 'file created by flexout'
        for name, size in [('time', None), ('sigma', 2), ('yc', 3), ('xc', 4)]:
            ds.createDimension(name, size)
        time = ds.createVariable('time', 'f8', ('time',))
        time[:] = np.arange(8)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-0.5, 0.0]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = 5

        surface_data = np.arange(8 * 3 * 4, dtype='f8').reshape(8, 3, 4)
        surface_data[3, 1, 1] = np.nan
        surface_data[6, 2, 3] = -9999
        surface = ds.createVariable('surface', 'f8', ('time', 'yc', 'xc'), fill_value=-9999)
        surface[:] = surface_data

        volume_data = np.arange(8 * 2 * 3 * 4, dtype='f8').reshape(8, 2, 3, 4)
        volume_data[3, 1, 1, 1] = np.nan
        volume_data[6, 0, 2, 3] = -9999
        volume = ds.createVariable('volume', 'f8', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        volume[:] = volume_data

    original_nc_open = server.nc_open
    monkeypatch.setattr(server, 'nc_open_original', original_nc_open, raising=False)
    readers = {}

    def recording_open(open_path, mode='r'):
        reader = RecordingDataset(open_path)
        readers[str(open_path)] = reader
        return reader

    monkeypatch.setattr(server, 'nc_open', recording_open)
    return path, readers, surface_data, volume_data


@pytest.mark.parametrize(
    'var_name,kwargs,source,expected',
    [
        ('surface', {'lake_avg': True}, 'surface', 'all'),
        ('surface', {'lake_avg': True, 'region': (1, 4, 0, 2), 'i': 0, 'j': 0}, 'surface', 'all'),
        ('surface', {'region': (1, 4, 0, 2)}, 'surface', 'region'),
        ('volume', {'level': 1}, 'volume', 'all'),
        ('volume', {'i': 2, 'j': 1, 'level': 1}, 'volume', 'point'),
        ('volume', {'i': 1, 'j': 1, 'level': 1}, 'volume', 'point'),
        ('volume', {'i': 3, 'j': 2, 'level': 0}, 'volume', 'point'),
        ('volume', {'region': (1, 4, 0, 2), 'level': 0}, 'volume', 'region'),
    ],
)
def test_ordinary_series_reads_only_sampled_times_and_preserves_aggregation(
        timeseries_file, var_name, kwargs, source, expected):
    path, readers, surface_data, volume_data = timeseries_file
    original_open = server.nc_open

    def recording_open(open_path, mode='r'):
        reader = RecordingDataset(open_path)
        readers[str(open_path)] = reader
        return reader

    server.nc_open = recording_open
    try:
        result = server.get_timeseries(path, var_name, tstride=3, **kwargs)
    finally:
        server.nc_open = original_open
    reader = readers[str(path)]
    data = surface_data if source == 'surface' else volume_data
    times = [0, 3, 6]
    if expected == 'point':
        values = [data[t, kwargs['level'], kwargs['j'], kwargs['i']] for t in times]
        values = [None if not np.isfinite(v) or v == -9999 else float(v) for v in values]
    else:
        level = kwargs.get('level', 0) if data.ndim == 4 else None
        region = None if kwargs.get('lake_avg') else kwargs.get('region')
        y0, y1, x0, x1 = (region[2], region[3], region[0], region[1]) if region else (0, data.shape[-2], 0, data.shape[-1])
        values = []
        for t in times:
            frame = data[t, level, y0:y1, x0:x1] if data.ndim == 4 else data[t, y0:y1, x0:x1]
            valid = frame[np.isfinite(frame) & (frame != -9999)]
            values.append(float(valid.mean()) if valid.size else None)

    assert result['values'] == values
    assert result['times'] == [0.0, 3.0, 6.0]
    assert reader.variables['time'].reads == [slice(None, None, 3)]
    assert len(reader.variables[var_name].reads) > 0
    for key in reader.variables[var_name].reads:
        assert isinstance(key, tuple)
        assert isinstance(key[0], (int, np.integer)), 'the value variable must be read one sampled timestep at a time'
        assert key[0] in times, 'unsampled records must never be read'
        if expected != 'point':
            assert all(isinstance(axis, slice) for axis in key[-2:])
            assert all(len(range(*axis.indices(data.shape[-2 + offset]))) <= 128
                       for offset, axis in enumerate(key[-2:]))


def test_default_stride_keeps_series_at_or_below_3000_points(timeseries_file):
    path, readers, _surface_data, _volume_data = timeseries_file
    with nc.Dataset(path, 'a') as ds:
        ds.variables['time'][:] = np.arange(6001)
    original_open = server.nc_open

    def recording_open(open_path, mode='r'):
        reader = RecordingDataset(open_path)
        readers[str(open_path)] = reader
        return reader

    server.nc_open = recording_open
    try:
        result = server.get_timeseries(path, 'surface', lake_avg=True)
    finally:
        server.nc_open = original_open
    assert len(result['values']) <= 3000
    assert result['tstride'] == 3
    reader = readers[str(path)]
    reads = reader.variables['surface'].reads
    assert len(reads) == len(result['values'])
    assert all(isinstance(key[0], (int, np.integer)) for key in reads)
    assert reader.variables['time'].reads == [slice(None, None, 3)]


def test_per_layer_lake_average_bounds_data_and_dynamic_geometry_reads(tmp_path, monkeypatch):
    """A per-layer full-grid request streams selected frames and geometry tiles."""
    path = tmp_path / 'wide-dynamic.3d.nc'
    nt, nz, ny, nx = 5, 3, 257, 259
    yy, xx = np.indices((ny, nx))
    with nc.Dataset(path, 'w') as ds:
        ds.comment = 'file created by flexout'
        for name, size in [('time', nt), ('sigma', nz), ('yc', ny), ('xc', nx)]:
            ds.createDimension(name, size)
        ds.createVariable('time', 'f8', ('time',))[:] = np.arange(nt)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-1, -0.5, 0]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = 10 + yy * 0.01 + xx * 0.001
        values = ds.createVariable('temp', 'f4', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        hn = ds.createVariable('hn', 'f4', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        hn.units = 'm'
        for t in range(nt):
            for k in range(nz):
                values[t, k] = t * 10 + k + yy * 0.001
                hn[t, k] = (k + 1) * (1 + t * 0.01)

    original_open = server.nc_open
    monkeypatch.setattr(server, 'nc_open_original', original_open, raising=False)
    readers = {}

    def recording_open(open_path, mode='r'):
        reader = RecordingDataset(open_path)
        readers[str(open_path)] = reader
        return reader

    monkeypatch.setattr(server, 'nc_open', recording_open)
    result = server.get_timeseries(path, 'temp', lake_avg=True, per_layer=True, tstride=2)
    assert 'series' in result, result

    expected_series = [[float(np.mean(t * 10 + k + yy * 0.001)) for t in (0, 2, 4)]
                       for k in range(nz)]
    assert np.allclose(np.asarray(result['series'], dtype=float), expected_series)
    assert result['times'] == [0.0, 2.0, 4.0]
    expected_centers = []
    for k in range(nz):
        row = []
        for t in (0, 2, 4):
            thickness = np.array([(level + 1) * (1 + t * 0.01) for level in range(nz)])
            edges = np.r_[np.cumsum(thickness[::-1])[::-1], 0.0]
            row.append(float(np.mean((edges[k] + edges[k + 1]) / 2)))
        expected_centers.append(row)
    assert np.allclose(np.asarray(result['layer_center_depth_m'], dtype=float), expected_centers)

    for name in ('temp', 'hn', 'bathymetry'):
        for key in readers[str(path)].variables[name].reads:
            # Geometry and values are read by one time/layer record and spatial tiles.
            if name != 'bathymetry':
                assert isinstance(key[0], (int, np.integer)), (name, key)
            assert all(isinstance(axis, slice) for axis in key[-2:]), (name, key)
            assert all(len(range(*axis.indices((ny, nx)[offset]))) <= 128
                       for offset, axis in enumerate(key[-2:])), (name, key)


@pytest.mark.parametrize('route,method,kwargs', [
    ('/api/results/timeseries_polygon', 'post', {'json': {
        'var': 'surface', 'polygon': [[0, 0], [4, 0], [4, 3], [0, 3]]}}),
    ('/api/results/timeseries_cell?var=surface&i=1&j=1', 'get', {}),
])
def test_result_routes_read_time_in_bounded_chunks(timeseries_file, monkeypatch, route, method, kwargs):
    path, readers, surface_data, _volume_data = timeseries_file
    monkeypatch.setattr(server, 'active_case_path', path.parent)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'find_output_files', lambda *_: {'3d': path, '2d': None})
    monkeypatch.setattr(server, '_annotated_output', lambda item, *_: {'zh_name': item['name']})
    original_open = server.nc_open

    def recording_open(open_path, mode='r'):
        reader = RecordingDataset(open_path)
        readers[str(open_path)] = reader
        return reader

    monkeypatch.setattr(server, 'nc_open', recording_open)
    client = server.app.test_client()
    response = getattr(client, method)(route, **kwargs)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['times'] == list(map(float, range(8)))
    if method == 'post':
        expected = []
        for frame in surface_data:
            valid = frame[np.isfinite(frame) & (frame != -9999)]
            expected.append(float(valid.mean()))
        assert payload['values'] == expected
        assert payload['n_cells'] == 12
    else:
        expected = [float(v) if np.isfinite(v) and v != -9999 else None
                    for v in surface_data[:, 1, 1]]
        assert payload['values'] == expected
    reads = readers[str(path)].variables['surface'].reads
    assert reads
    assert all(isinstance(key[0], slice) for key in reads), 'routes must read a bounded time chunk'
    assert all(key[0].start is not None and key[0].stop is not None for key in reads)
    assert all(key[0].stop - key[0].start <= 256 for key in reads)
    if method == 'post':
        assert all(all(isinstance(axis, slice) for axis in key[-2:]) for key in reads)
        assert all(all(axis.stop - axis.start <= 128 for axis in key[-2:]) for key in reads)

