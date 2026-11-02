"""Physical layer indices must agree between native GETM and flexout results."""
import ast
import hashlib
import sys
import threading
from collections import OrderedDict
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest
from flask import Flask, jsonify, request

APP_DIR = Path(__file__).resolve().parents[1] / '3DWET/app'
sys.path.insert(0, str(APP_DIR))
from netcdf_io import open_dataset
from variable_api import metadata as _annotated_output


def functions(case_path, output):
    names = {'_get_2d_field_from_dataset', '_result_horizontal_geometry', 'get_2d_field', 'get_timeseries',
             'results_profile', 'results_3d_surface', 'results_2d', 'results_range'}
    nodes = [n for n in ast.parse((APP_DIR / 'server.py').read_text(encoding='utf-8')).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    for node in nodes:
        node.decorator_list = []
    scope = dict(_annotated_output=_annotated_output,Path=Path, np=np, nc=nc, nc_open=open_dataset, hashlib=hashlib, jsonify=jsonify,
                 request=request, active_case_path=case_path, _output_locked=lambda: False,
                 _add_authoritative_boundary=lambda payload, _case_path: payload,
                 find_output_files=lambda *_: {'3d': output, '2d': None}, _lookup_result_variable=lambda *_: None,
                 _result_window_range_cache=OrderedDict(), _result_horizontal_geometry_cache=OrderedDict(),
                 _result_horizontal_geometry_cache_lock=threading.RLock())
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'server.py', 'exec'), scope)
    return scope


def dataset(path, native=True, boundary_values=False, masked=False, layers=3):
    coords = np.linspace(-1, 0, layers) if native else np.linspace(-.9, 0, layers)
    with open_dataset(path, 'w') as ds:
        if native:
            ds.model = 'GETM - www.getm.eu'
        else:
            ds.comment = 'file created by flexout'
        for name, size in [('time', 2), ('sigma', layers), ('yc', 2), ('xc', 2)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = coords
        ds.createVariable('time', 'f8', ('time',))[:] = [0, 1]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = [[-10, 5], [6, 7]]
        v = ds.createVariable('w', 'f4', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        data = np.arange(2 * layers * 4, dtype=float).reshape(2, layers, 2, 2)
        data[:, :, 0, 0] = -9999
        if native and not boundary_values:
            data[:, 0] = -9999
        if masked:
            data[:] = -9999
        v[:] = data
    return coords, data


def test_legacy_level_zero_is_first_physical_layer(tmp_path):
    path = tmp_path / 'legacy.3d.nc'
    _, data = dataset(path)
    scope = functions(tmp_path, path)
    field = scope['get_2d_field'](path, 'w', level=0)
    assert field['data'][1][1] == data[0, 1, 1, 1]
    ts = scope['get_timeseries'](path, 'w', i=1, j=1, level=0)
    assert ts['values'] == data[:, 1, 1, 1].tolist()
    assert ts['layer'] == 0


def test_2d_field_rejects_unsupported_dimensions_before_read_and_preserves_supported_shapes(tmp_path):
    from types import SimpleNamespace
    path = tmp_path / 'field-dimensions.nc'
    with open_dataset(path, 'w') as ds:
        for name, size in [('time', 2), ('sigma', 3), ('y', 2), ('x', 3), ('aux', 4), ('z', 3)]:
            ds.createDimension(name, size)
        static = ds.createVariable('static_map', 'f4', ('y', 'x'))
        static[:] = np.arange(6, dtype='f4').reshape(2, 3)
        timed_2d = ds.createVariable('timed_map', 'f4', ('time', 'y', 'x'))
        timed_2d[:] = np.arange(12, dtype='f4').reshape(2, 2, 3)
        timed_3d = ds.createVariable('timed_volume', 'f4', ('time', 'sigma', 'y', 'x'))
        timed_3d[:] = np.arange(36, dtype='f4').reshape(2, 3, 2, 3)
        ds.createVariable('aux_field', 'f4', ('time', 'sigma', 'aux', 'y', 'x'))
        ds.createVariable('late_time', 'f4', ('z', 'time', 'y', 'x'))

    class TrackedVariable:
        def __init__(self, variable):
            self.variable = variable
            self.reads = []
        def __getattr__(self, name):
            return getattr(self.variable, name)
        def __getitem__(self, key):
            self.reads.append(key)
            return self.variable[key]

    with open_dataset(path) as ds:
        tracked = {name: TrackedVariable(variable) for name, variable in ds.variables.items()}
        view = SimpleNamespace(variables=tracked)
        get_field = functions(tmp_path, path)['_get_2d_field_from_dataset']

        static_result = get_field(view, 'static_map', include_bathymetry=False)
        assert static_result['data'] == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]
        static_read = tracked['static_map'].reads
        assert len(static_read) == 1 and (
            static_read[0] == slice(None) or
            static_read[0] == (slice(None), slice(None))
        )

        timed_result = get_field(view, 'timed_map', timestep=1, include_bathymetry=False)
        assert timed_result['data'] == [[6.0, 7.0, 8.0], [9.0, 10.0, 11.0]]
        assert tracked['timed_map'].reads == [(1, slice(None), slice(None))]

        volume_result = get_field(view, 'timed_volume', timestep=1, level=2,
                                  include_bathymetry=False)
        assert volume_result['data'] == [[30.0, 31.0, 32.0], [33.0, 34.0, 35.0]]
        assert tracked['timed_volume'].reads == [(1, 2, slice(None), slice(None))]

        for name in ('aux_field', 'late_time'):
            with pytest.raises(ValueError, match='不支持.*维度'):
                get_field(view, name, include_bathymetry=False)
            assert tracked[name].reads == [], f'{name} must be rejected before any data read'


def test_volume_distinguishes_explicit_dry_cells_from_unknown_bathymetry(tmp_path):
    path = tmp_path / 'legacy.3d.nc'
    dataset(path, native=False)
    with open_dataset(path, 'a') as ds:
        ds['bathymetry'][:] = [[-10, 5], [np.nan, 0]]
    scope = functions(tmp_path, path)
    app = Flask(__name__)
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    payload = app.test_client().get('/volume?var=w&time=0').get_json()
    assert payload['dry_mask'] == [[True, False], [False, True]]
    assert payload['bottom'] == [[None, 5], [None, None]]
    assert payload['land_elevation'] is None


def test_native_zero_thickness_boundary_is_not_a_physical_hn_layer(tmp_path):
    from result_layers import physical_vertical_grid
    path=tmp_path/'native-hn.nc';dataset(path,native=True)
    with open_dataset(path,'a') as ds:
        h=ds.createVariable('hn','f8',ds['w'].dimensions);h.units='m';h[:]=2;h[:,0]=0
    with open_dataset(path) as ds:
        assert physical_vertical_grid(ds,ds['hn'])[0]==1


@pytest.mark.parametrize('native,boundary_values,masked', [
    (True, False, False), (False, False, False),
    (True, True, False), (True, False, True),
])
def test_profiles_volume_and_heatmap_share_actual_coordinates(tmp_path, native, boundary_values, masked):
    path = tmp_path / 'output.nc'
    coords, data = dataset(path, native, boundary_values, masked)
    start = int(native and not boundary_values)
    scope = functions(tmp_path, path)
    app = Flask(__name__)
    app.add_url_rule('/profile', view_func=scope['results_profile'])
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    client = app.test_client()
    profile = client.get('/profile?var=w&i=1&j=1').get_json()
    assert profile['sigma'] == coords[start:].tolist()
    assert len(profile['profile']) == len(coords) - start
    volume = client.get('/volume?var=w').get_json()
    assert volume['sigma'] == coords[start:].tolist()
    assert volume['shape'][0] == len(coords) - start
    assert volume['data'][0][0][0] is None
    series = scope['get_timeseries'](path, 'w', i=1, j=1, per_layer=True)
    assert series['layers'] == coords[start:].tolist()
    assert series['n_layers'] == len(coords) - start
    if masked:
        assert all(v is None for v in profile['profile'])
        assert all(v is None for layer in series['series'] for v in layer)
    else:
        assert profile['profile'] == data[0, start:, 1, 1].tolist()
        assert series['series'] == data[:, start:, 1, 1].T.tolist()


def test_volume_vertical_stride_keeps_sigma_aligned(tmp_path):
    path = tmp_path / 'legacy.3d.nc'
    coords, _ = dataset(path, layers=21)
    scope = functions(tmp_path, path)
    app = Flask(__name__)
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    result = app.test_client().get('/volume?var=w&target=8').get_json()
    assert result['sigma'] == coords[sorted(set(range(1, 21, 3)) | {20})].tolist()
    assert result['layer_indices'][-1] == 19
    assert result['total_layers'] == 20
    assert len(result['sigma']) == result['shape'][0]


def test_volume_layer_only_returns_selected_physical_layer_and_range(tmp_path):
    path=tmp_path/'single-layer-volume.nc'
    coords,data=dataset(path,native=False,layers=3)
    scope=functions(tmp_path,path)
    app=Flask(__name__);app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    client=app.test_client()
    full=client.get('/volume?var=w&time=1&target=8&level=1').get_json()
    single_response=client.get('/volume?var=w&time=1&target=8&level=1&layer_only=1')
    assert single_response.status_code==200
    single=single_response.get_json()
    assert full['shape'][0]==3
    assert single['shape']==[1,2,2]
    assert single['layer_indices']==[1] and single['total_layers']==3
    assert single['sigma']==[coords[1]]
    expected=data[1,1].astype(float)
    expected[expected==-9999]=np.nan
    actual=np.asarray(single['data'][0],dtype=float)
    assert np.array_equal(actual,expected,equal_nan=True)
    assert single['min']==float(np.nanmin(expected)) and single['max']==float(np.nanmax(expected))


@pytest.mark.parametrize('level',[-2,3])
def test_volume_layer_only_rejects_invalid_physical_layer(tmp_path,level):
    path=tmp_path/'single-layer-invalid.nc';dataset(path,native=False,layers=3)
    scope=functions(tmp_path,path)
    app=Flask(__name__);app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    response=app.test_client().get(f'/volume?var=w&level={level}&layer_only=1')
    assert response.status_code==400
    assert '物理层索引越界' in response.get_json()['error']


def test_volume_layer_only_minus_one_selects_surface_physical_ordinal(tmp_path):
    path=tmp_path/'single-layer-surface.nc';coords,data=dataset(path,native=True,layers=4)
    scope=functions(tmp_path,path)
    app=Flask(__name__);app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    payload=app.test_client().get('/volume?var=w&level=-1&layer_only=true').get_json()
    assert payload['shape']==[1,2,2]
    assert payload['total_layers']==3
    assert payload['layer_indices']==[2]
    assert payload['sigma']==[coords[-1]]
    assert payload['data'][0][1][1]==data[0,-1,1,1]


def test_later_finite_boundary_is_preserved(tmp_path):
    path = tmp_path / 'legacy.3d.nc'
    coords, _ = dataset(path)
    with open_dataset(path, 'r+') as ds:
        ds['w'][1, 0, 1, 1] = 0.0
    scope = functions(tmp_path, path)
    result = scope['get_timeseries'](path, 'w', i=1, j=1, per_layer=True)
    assert result['layers'] == coords.tolist()
    assert result['series'][0] == [None, 0.0]


def test_padding_probe_batches_bounded_history_reads(tmp_path):
    from result_layers import physical_vertical_grid
    path = tmp_path / 'bounded-padding.nc'
    with open_dataset(path, 'w') as ds:
        ds.model = 'GETM'
        for name, size in [('time', 3000), ('sigma', 3), ('y', 2), ('x', 2)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-1, -.5, 0]
        v = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'), fill_value=-9999)
        v[:] = 12; v[:, 0] = -9999
    with open_dataset(path) as ds:
        class Probe:
            def __init__(self, variable): self.variable = variable; self.reads = 0
            def __getattr__(self, key): return getattr(self.variable, key)
            def __getitem__(self, key): self.reads += 1; return self.variable[key]
        probe = Probe(ds['temp'])
        assert physical_vertical_grid(ds, probe)[0] == 1
        assert probe.reads == 1, 'a bounded padding probe must not perform one hyperslab call per record'


@pytest.mark.parametrize('thickness,expected', [([2, 2], 20), ([1, 3], 25)])
def test_depth_mean_uses_actual_layer_thickness(tmp_path, thickness, expected):
    path = tmp_path / 'mean.nc'
    with open_dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 2), ('yc', 1), ('xc', 3)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-.75, -.25]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = [[4, 4, -10]]
        v = ds.createVariable('temp', 'f8', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        v[:] = [[[[10, -9999, 10]], [[30, 30, 30]]]]
        h = ds.createVariable('hn', 'f8', v.dimensions)
        h[:] = np.asarray(thickness)[None, :, None, None]
    field = functions(tmp_path, path)['get_2d_field'](path, 'temp', depth_average=True)
    assert field['data'][0][0] == pytest.approx(expected)
    assert field['data'][0][1] == 30  # missing layer excluded, weights renormalized
    assert field['data'][0][2] is None  # dry cell never appears as valid result
    assert field['aggregation'] == 'depth_weighted_mean'
    assert field['weight_source'] == 'hn'


def test_depth_mean_sigma_interfaces_and_native_padding(tmp_path):
    path = tmp_path / 'native.nc'
    dataset(path, native=True, layers=3)
    with open_dataset(path, 'r+') as ds:
        ds['sigma'][:] = [-1, -.75, 0]
        ds['w'][0, 1, :, :] = 10
        ds['w'][0, 2, :, :] = 30
    field = functions(tmp_path, path)['get_2d_field'](path, 'w', depth_average=True)
    assert field['data'][1][1] == pytest.approx(25)
    assert field['weight_source'] == 'sigma_interfaces'


def test_depth_mean_preserves_bottom_variable(tmp_path):
    path = tmp_path / 'bottom.nc'
    dataset(path, native=False)
    with open_dataset(path, 'r+') as ds:
        ds.createVariable('sediment', 'f8', ('time', 'yc', 'xc'))[:] = 7
    field = functions(tmp_path, path)['get_2d_field'](path, 'sediment', depth_average=True)
    assert field['data'][1][1] == 7
    assert field['aggregation'] == 'not_applicable'


def test_depth_mean_http_endpoint_and_invalid_mode(tmp_path):
    path = tmp_path / 'native.nc'
    dataset(path, native=True, layers=3)
    with open_dataset(path, 'r+') as ds:
        ds['w'][0, 1, :, :] = 10
        ds['w'][0, 2, :, :] = 30
    scope = functions(tmp_path, path)
    app = Flask(__name__)
    app.add_url_rule('/2d', view_func=scope['results_2d'])
    client = app.test_client()
    response = client.get('/2d?var=w&aggregation=depth_mean')
    assert response.status_code == 200
    assert response.get_json()['data'][1][1] == 20
    assert client.get('/2d?var=w&aggregation=bogus').status_code == 400


def test_depth_mean_does_not_invent_weights_without_coordinates(tmp_path):
    path = tmp_path / 'missing-coordinates.nc'
    with open_dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('level', 2), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        ds.createVariable('temp', 'f8', ('time', 'level', 'y', 'x'))[:] = 10
    with pytest.raises(ValueError, match='hn.*sigma'):
        functions(tmp_path, path)['get_2d_field'](path, 'temp', depth_average=True)

@pytest.mark.parametrize('mismatch', ['', 'axis', 'wet_depth', 'unknown'])
def test_masked_output_land_requires_matching_explicit_input_bathymetry(tmp_path, mismatch):
    path=tmp_path/'output.nc';dataset(path,native=False)
    # Native GETM output masks the domain land sentinel; the masked value alone
    # does not prove land. Use an independently verified input-grid contract.
    with open_dataset(path,'a') as ds:
        ds['bathymetry'].missing_value=-10
        ds['bathymetry'].units='m'
        ds['bathymetry'][:]=[[-10,5],[6,-10]]
        x=ds.createVariable('xc','f8',('xc',));x.units='m';x[:]=[100,200]
        y=ds.createVariable('yc','f8',('yc',));y.units='m';y[:]=[300,400]
    with open_dataset(tmp_path/'bathymetry.nc','w') as ds:
        ds.createDimension('x',2);ds.createDimension('y',2)
        x=ds.createVariable('x','f8',('x',));x.units='m';x[:]=[101,201] if mismatch=='axis' else [100,200]
        y=ds.createVariable('y','f8',('y',));y.units='m';y[:]=[300,400]
        b=ds.createVariable('bathymetry','f8',('y','x'),fill_value=99);b.units='m'
        b[:]=[[99 if mismatch=='unknown' else -10,50 if mismatch=='wet_depth' else 5],[6,-10]]
    scope=functions(tmp_path,path);app=Flask(__name__);app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    payload=app.test_client().get('/volume?var=w').get_json()
    expected=[[False,False],[False,False]] if mismatch in ['axis','wet_depth'] else [[mismatch!='unknown',False],[False,True]]
    assert payload['dry_mask']==expected
    assert payload['bottom']==[[None,5],[6,None]],'supplementing land must never rewrite result bathymetry'


def test_time_window_range_uses_only_selected_frames_and_all_physical_layers(tmp_path):
    from result_layers import time_window_range
    path=tmp_path/'window.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',5),('sigma',2),('y',1),('x',2)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.5,0]
        values=np.array([[[[100,101]],[[102,103]]],[[[1,2]],[[3,4]]],[[[5,6]],[[7,8]]],
                         [[[9,10]],[[11,12]]],[[[-100,-101]],[[-102,-103]]]],dtype='f4')
        ds.createVariable('temp','f4',('time','sigma','y','x'))[:]=values
    with open_dataset(path) as ds:
        result=time_window_range(ds,'temp',1,3)
    assert result=={'min':1.0,'max':12.0,'first_mean':2.5,'last_mean':10.5,
                    'start':1,'end':3,'frames':3,'no_data':False}


def test_time_window_range_endpoint_returns_and_caches_server_side_scan(tmp_path):
    path=tmp_path/'range-api.nc'
    dataset(path,native=False,layers=2)
    scope=functions(tmp_path,path)
    app=Flask(__name__);app.add_url_rule('/range',view_func=scope['results_range'])
    client=app.test_client()
    first=client.get('/range?var=w&start=1&end=1')
    assert first.status_code==200
    assert first.json['min']==9.0 and first.json['max']==15.0
    assert first.json['first_mean']==first.json['last_mean']==12.0
    assert first.json['cache_hit'] is False
    cached=client.get('/range?var=w&start=1&end=1')
    assert cached.status_code==200 and cached.json['cache_hit'] is True
    assert client.get('/range?var=w&start=bad&end=1').status_code==400
import re
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

from test_result_layers import functions
from netcdf_io import open_dataset


def test_depth_mean_hn_ignores_nonfinite_nonpositive_and_masked_layers(tmp_path):
    path = tmp_path / 'hn-validity.nc'
    with open_dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 2), ('y', 1), ('x', 3)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-0.75, -0.25]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[5, 5, 5]]
        values = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'), fill_value=-9999)
        values[:] = [[[[10, 10, 10]], [[30, 30, 30]]]]
        hn = ds.createVariable('hn', 'f8', values.dimensions, fill_value=-9999)
        hn[:] = [[[[np.nan, 2, 2]], [[3, 0, 3]]]]
        ds.createVariable('mask', 'i1', ('y', 'x'))[:] = [[1, 1, 0]]

    field = functions(tmp_path, path)['get_2d_field'](path, 'temp', depth_average=True)
    assert field['data'][0] == pytest.approx([30, 10, None], nan_ok=True)
    assert field['weight_source'] == 'hn'


def test_depth_mean_sigma_center_fallback_uses_interpolated_layer_widths(tmp_path):
    path = tmp_path / 'sigma-centres.nc'
    with open_dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 3), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-0.8, -0.4, -0.1]
        field = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'))
        field[:] = [[[[10]], [[20]], [[40]]]]

    result = functions(tmp_path, path)['get_2d_field'](path, 'temp', depth_average=True)
    # Midpoint interfaces are [-1, -.6, -.25, 0], giving widths .4, .35, .25.
    assert result['data'][0][0] == pytest.approx(21.0)
    assert result['weight_source'] == 'sigma_midpoint_interfaces'


def test_depth_mean_native_hn_padding_excludes_zero_thickness_boundary(tmp_path):
    path = tmp_path / 'native-hn-depth-mean.nc'
    from test_result_layers import dataset
    dataset(path, native=True, boundary_values=True, layers=3)
    with open_dataset(path, 'a') as ds:
        ds['sigma'][:] = [-1, -0.6, 0]
        ds['w'][0, 0, :, :] = 100
        ds['w'][0, 1, :, :] = 10
        ds['w'][0, 2, :, :] = 30
        hn = ds.createVariable('hn', 'f8', ds['w'].dimensions)
        hn[:] = 2
        hn[:, 0, :, :] = 0
        hn[:, 1, :, :] = 1
        hn[:, 2, :, :] = 3

    result = functions(tmp_path, path)['get_2d_field'](path, 'w', depth_average=True)
    assert result['data'][1][1] == pytest.approx(25)
    assert result['weight_source'] == 'hn'


def test_depth_mean_two_dimensional_input_is_not_aggregated(tmp_path):
    path = tmp_path / 'static-2d.nc'
    with open_dataset(path, 'w') as ds:
        ds.createDimension('y', 1)
        ds.createDimension('x', 2)
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[4, 8]]

    result = functions(tmp_path, path)['get_2d_field'](path, 'bathymetry', depth_average=True)
    assert result['data'] == [[4, 8]]
    assert result['aggregation'] == 'not_applicable'
    assert result['weight_source'] is None


def test_2d_depth_mean_panel_requests_depth_mean_aggregation():
    source = (Path(__file__).resolve().parents[1] / '3DWET/app/static/js/app.js').read_text(encoding='utf-8')
    match = re.search(r'async function updateViz3dAvg\(\) \{(?P<body>.*?)\n\}', source, re.S)
    assert match, 'depth-mean UI handler should exist'
    body = match.group('body')
    assert 'aggregation=depth_mean' in body
    assert 'level=0' not in body
