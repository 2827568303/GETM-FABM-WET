"""Focused FABM output still needs the real input grid for rendering."""
import ast
import hashlib
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
from flask import Flask, jsonify, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from netcdf_io import open_dataset
from variable_api import metadata as _annotated_output


def test_volume_uses_input_coordinates_bathymetry_and_masks_land(tmp_path):
    with open_dataset(tmp_path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 3)
        ds.createDimension('y', 2)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [100, 300, 500]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [1000, 1200]
        ds.createVariable('bathymetry', 'f8', ('y','x'))[:] = [[-10,5,6],[4,7,-10]]
    output = tmp_path / 'output.nc'
    with open_dataset(output, 'w') as ds:
        for name,size in [('time',1),('z',2),('y',2),('x',3)]:
            ds.createDimension(name,size)
        v = ds.createVariable('temp','f4',('time','z','y','x'))
        v[:] = [[[[999,12,14],[10,11,999]],[[999,13,15],[12,13,999]]]]
    path = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    function = next(n for n in ast.parse(path.read_text(encoding='utf-8')).body
                    if isinstance(n,ast.FunctionDef) and n.name=='results_3d_surface')
    function.decorator_list=[]
    app=Flask(__name__)
    scope=dict(_annotated_output=_annotated_output,Path=Path,np=np,hashlib=hashlib,request=request,jsonify=jsonify,active_case_path=tmp_path,
               _output_locked=lambda:False,_add_authoritative_boundary=lambda payload,_case_path:payload,
               find_output_files=lambda *_: {'3d':output},nc_open=open_dataset)
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(path),'exec'),scope)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    result=app.test_client().get('/volume?var=temp').get_json()
    assert result['xc']==[100,300,500] and result['yc']==[1000,1200]
    assert result['bottom']==[[None,5,6],[4,7,None]]
    assert result['data'][0][0][0] is None
    assert result['min']==10 and result['max']==15
    assert result['sigma']==[-.75,-.25]
    assert result['coordinate_mode'] == 'projected'
    assert result['coordinate_units'] == 'm'


def test_volume_includes_saved_projected_boundary_without_changing_scientific_payload(tmp_path):
    import json
    import server
    from test_result_layers import functions

    polygon = {
        'outer': [[100.0, 1000.0], [500.0, 1000.0], [500.0, 1200.0], [100.0, 1200.0]],
        'holes': [[[200.0, 1050.0], [250.0, 1050.0], [250.0, 1100.0]]],
    }
    (tmp_path / 'rivers_setup.json').write_text(json.dumps({
        'boundary_geometry': {
            'projected_polygons': [polygon],
            'coordinate_space': 'bathymetry_projected_grid_coordinates',
            'projected_crs': {'epsg': 32633},
            'source_crs': {'wkt': 'PROJCRS["test"]'},
            'provenance': {'source': 'uploaded-boundary-shapefile'},
        }
    }), encoding='utf-8')
    output = tmp_path / 'output.nc'
    with open_dataset(output, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 2), ('yc', 2), ('xc', 3)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-.75, -.25]
        ds.createVariable('xc', 'f8', ('xc',))[:] = [100, 300, 500]
        ds.createVariable('yc', 'f8', ('yc',))[:] = [1000, 1200]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = [[-10, 5, 6], [4, 7, -10]]
        ds.createVariable('temp', 'f4', ('time', 'sigma', 'yc', 'xc'))[:] = [
            [[[999, 12, 14], [10, 11, 999]], [[999, 13, 15], [12, 13, 999]]]
        ]

    scope = functions(tmp_path, output)
    scope['_add_authoritative_boundary'] = server._add_authoritative_boundary
    app = Flask(__name__)
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    result = app.test_client().get('/volume?var=temp').get_json()

    assert result['authoritative_boundary']['projected_polygons'] == [polygon]
    assert result['authoritative_boundary']['projected_crs'] == {'epsg': 32633}
    assert result['authoritative_boundary']['source_crs'] == {'wkt': 'PROJCRS["test"]'}
    assert result['authoritative_boundary']['coordinate_space'] == 'bathymetry_projected_grid_coordinates'
    assert result['authoritative_boundary']['provenance']['source'] == 'uploaded-boundary-shapefile'
    assert len(result['authoritative_boundary']['provenance']['identity']) == 64
    assert result['bottom'] == [[None, 5, 6], [4, 7, None]]
    assert result['data'][0][0] == [None, 12.0, 14.0]
    assert result['display_topology']['wet_mask'] == [[False, True, True], [True, True, False]]


def test_volume_contract_uses_full_resolution_mask_before_coarse_sampling(tmp_path):
    from test_result_layers import functions

    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',2),('yc',3),('xc',57)]:ds.createDimension(name,size)
        ds.comment='file created by flexout'
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,-.25]
        depth=np.full((3,57),5.0);depth[:,1]=0.0
        ds.createVariable('bathymetry','f8',('yc','xc'))[:]=depth
        ds.createVariable('temp','f4',('time','sigma','yc','xc'))[:]=1

    scope=functions(tmp_path,path);app=Flask(__name__)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    payload=app.test_client().get('/volume?var=temp&target=8').get_json()
    topology=payload['display_topology']
    assert payload['sampling_stride'][2]==8
    assert topology['source_shape']==[3,57]
    assert topology['x_indices']==payload['x']==[0,8,16,24,32,40,48,56]
    assert payload['display_topology_status'] == 'ready'
    assert 'full_dry_mask' not in topology
    assert topology['mask_cells_examined'] == 3 * 57
    assert topology['cell_status'][0][0]=='mixed'
    assert topology['wet_mask'][0][0] is False
    assert topology['x_edges']==[-.5,7.5,15.5,23.5,31.5,39.5,47.5,55.5,56.5]


def test_volume_reports_unavailable_topology_when_native_mask_shape_is_ambiguous(tmp_path):
    from test_result_layers import functions
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',2),('y',2),('x',2)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,-.25]
        ds.createVariable('temp','f4',('time','sigma','y','x'))[:]=1
    grid=tmp_path/'bathymetry.nc'
    with open_dataset(grid,'w') as ds:
        ds.createDimension('y',3);ds.createDimension('x',3)
        ds.createVariable('bathymetry','f8',('y','x'))[:]=5
    scope=functions(tmp_path,path);app=Flask(__name__)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    result=app.test_client().get('/volume?target=8').get_json()
    assert result['display_topology'] is None
    assert result['display_topology_status']=='unavailable'
    assert '尺寸' in result['display_topology_error']


def test_volume_without_verified_metre_axes_uses_original_indices(tmp_path):
    from test_result_layers import dataset, functions
    path = tmp_path / 'output.nc'
    dataset(path, native=False, layers=21)
    with open_dataset(path, 'r+') as ds:
        x = ds.createVariable('xc', 'f8', ('xc',)); x.units = 'degrees_east'; x[:] = [100, 101]
        y = ds.createVariable('yc', 'f8', ('yc',)); y.units = 'degrees_north'; y[:] = [20, 21]
    scope = functions(tmp_path, path)
    app = Flask(__name__)
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    result = app.test_client().get('/volume?var=w&target=8&level=7').get_json()
    assert result['coordinate_mode'] == 'index'
    assert result['coordinate_units'] == 'index'
    assert result['xc'] == [0, 1] and result['yc'] == [0, 1]
    assert result['layer_indices'] == [0, 3, 6, 7, 9, 12, 15, 18, 20]
    assert result['total_layers'] == 21
    assert result['sigma'][-1] == 0
    assert result['data'][result['layer_indices'].index(7)][1][1] == 31


def test_volume_depths_follow_native_thickness_before_vertical_sampling(tmp_path):
    from test_result_layers import functions
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',2),('sigma',21),('yc',19),('xc',20)]:ds.createDimension(name,size)
        ds.comment='file created by flexout'
        ds.createVariable('sigma','f8',('sigma',))[:]=-1+(np.arange(21)+.5)/21
        ds.createVariable('bathymetry','f8',('yc','xc'))[:]=231
        var=ds.createVariable('temp','f4',('time','sigma','yc','xc'));var.units='Celsius'
        hn=ds.createVariable('hn','f8',var.dimensions);hn.units='m'
        for t in range(2):
            for k in range(21):var[t,k]=k;hn[t,k]=(k+1)*(t+1)
        hn[1,0,0,0]=0
    app=Flask(__name__);scope=functions(tmp_path,path)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    client=app.test_client()
    first=client.get('/volume?var=temp&target=8&level=7&time=0').get_json()
    last=client.get('/volume?var=temp&target=8&level=7&time=1').get_json()
    slot=first['layer_indices'].index(7)
    assert first['depth_source']=='hn' and first['depth_position']=='center'
    assert np.asarray(first['depth']).shape==tuple(first['shape'])
    assert first['depth'][slot][1][1]==199
    assert last['depth'][slot][1][1]==398
    assert first['elevation'][slot][1][1]==-199
    assert last['elevation'][slot][1][1]==-167
    assert first['water_depth'][1][1]==231
    assert last['water_depth'][1][1]==462
    assert last['valid_geometry'][0][0] is False
    assert last['depth'][slot][0][0] is None
    assert last['data'][slot][0][0]==7,'raw scalar values are not rewritten by missing geometry'


def test_volume_reports_unavailable_geometry_instead_of_claiming_real_depth(tmp_path):
    from test_result_layers import functions
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('z',2),('y',2),('x',2)]:ds.createDimension(name,size)
        ds.createVariable('bathymetry','f8',('y','x'))[:]=5
        ds.createVariable('temp','f4',('time','z','y','x'))[:]=20
    scope=functions(tmp_path,path);app=Flask(__name__)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    data=app.test_client().get('/volume').get_json()
    assert data['depth'] is None
    assert 'sigma' in data['depth_geometry_error']


def test_volume_reads_full_bathymetry_for_topology_but_samples_scalar_fields(tmp_path):
    from test_result_layers import functions
    from contextlib import contextmanager
    from types import SimpleNamespace
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',2),('yc',40),('xc',41)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,-.25]
        ds.createVariable('bathymetry','f8',('yc','xc'))[:]=10
        ds.createVariable('temp','f8',('time','sigma','yc','xc'))[:]=1
    accesses=[]
    class Tracked:
        def __init__(self,var):self.var=var
        def __getattr__(self,name):return getattr(self.var,name)
        def __getitem__(self,key):accesses.append((self.var.name,key));return self.var[key]
    @contextmanager
    def opened(*args,**kwargs):
        with open_dataset(*args,**kwargs) as ds:
            yield SimpleNamespace(variables={k:Tracked(v) for k,v in ds.variables.items()},**{})
    scope=functions(tmp_path,path);scope['nc_open']=opened
    app=Flask(__name__);app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    response=app.test_client().get('/volume?target=8')
    assert response.status_code==200,response.get_json()
    full_bathymetry=False
    for name,key in accesses:
        if name=='temp':
            assert key[-2:]==(slice(None,None,5),slice(None,None,6)),(name,key)
        elif name=='bathymetry':
            if key[-2:]==(slice(None,None,None),slice(None,None,None)):
                full_bathymetry=True
            else:
                assert key[-2:]==(slice(None,None,5),slice(None,None,6)),(name,key)
    assert full_bathymetry,'wet/dry topology must be read before sampling, not inferred from sampled bathymetry'


def test_volume_reuses_static_21x14_grid_between_dynamic_frames_and_reports_cold_warm_time(tmp_path):
    from contextlib import contextmanager
    from time import perf_counter
    from test_result_layers import functions
    from scientific_geometry import static_3d_geometry_cache

    static_3d_geometry_cache.clear()
    output = tmp_path / 'output.nc'
    grid_path = tmp_path / 'bathymetry.nc'
    rows, cols = 14, 21
    depth = np.full((rows, cols), 8.0)
    depth[:, 0] = -10.0
    with open_dataset(grid_path, 'w') as ds:
        ds.createDimension('y', rows); ds.createDimension('x', cols)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = np.arange(cols) * 50.0
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = np.arange(rows) * 50.0
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy.units = 'm'; bathy[:] = depth
    with open_dataset(output, 'w') as ds:
        for name, size in [('time', 2), ('sigma', 2), ('yc', rows), ('xc', cols)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-.75, -.25]
        x = ds.createVariable('xc', 'f8', ('xc',)); x.units = 'm'; x[:] = np.arange(cols) * 50.0
        y = ds.createVariable('yc', 'f8', ('yc',)); y.units = 'm'; y[:] = np.arange(rows) * 50.0
        bathy = ds.createVariable('bathymetry', 'f8', ('yc', 'xc')); bathy.units = 'm'; bathy[:] = depth
        temp = ds.createVariable('temp', 'f8', ('time', 'sigma', 'yc', 'xc'))
        temp[0] = 1.0; temp[1] = 2.0

    static_reads = []
    opened = []
    class TrackedVariable:
        def __init__(self, variable): self.variable = variable
        def __getattr__(self, name): return getattr(self.variable, name)
        def __getitem__(self, key):
            if self.variable.name in {'bathymetry', 'xc', 'yc', 'x', 'y'}:
                static_reads.append((self.variable.name, key))
            return self.variable[key]
    class TrackedDataset:
        def __init__(self, dataset):
            self.dataset = dataset
            self.variables = {name: TrackedVariable(value) for name, value in dataset.variables.items()}
        def __getattr__(self, name): return getattr(self.dataset, name)
    @contextmanager
    def tracked_open(path, *args, **kwargs):
        opened.append(Path(path).resolve())
        with open_dataset(path, *args, **kwargs) as dataset:
            yield TrackedDataset(dataset)

    scope = functions(tmp_path, output); scope['nc_open'] = tracked_open
    app = Flask(__name__); app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    client = app.test_client()
    cold_start = perf_counter(); first_response = client.get('/volume?var=temp&target=8&time=0'); cold_ms = (perf_counter() - cold_start) * 1000
    assert first_response.status_code == 200, first_response.get_json()
    first = first_response.get_json()
    reads_after_cold = len(static_reads)
    input_opens_after_cold = opened.count(grid_path.resolve())
    warm_start = perf_counter(); last_response = client.get('/volume?var=temp&target=8&time=1'); warm_ms = (perf_counter() - warm_start) * 1000
    assert last_response.status_code == 200, last_response.get_json()
    last = last_response.get_json()
    assert len(static_reads) == reads_after_cold, 'warm frame must not reread bathymetry or coordinate arrays'
    assert opened.count(grid_path.resolve()) == input_opens_after_cold, 'warm frame must not reopen the static input grid'
    assert first['display_topology']['grid_hash'] == last['display_topology']['grid_hash']
    assert first['min'] == 1.0 and last['min'] == 2.0
    print(f'21x14 /api 3d_surface cold={cold_ms:.2f}ms warm={warm_ms:.2f}ms static_reads={reads_after_cold} input_grid_opens={input_opens_after_cold}')


def test_finite_hn_does_not_allow_nonfinite_sigma_in_json(tmp_path):
    from test_result_layers import functions
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',2),('y',2),('x',2)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,np.nan]
        ds.createVariable('bathymetry','f8',('y','x'))[:]=12
        v=ds.createVariable('temp','f8',('time','sigma','y','x'));v[:]=20
        h=ds.createVariable('hn','f8',v.dimensions);h.units='m';h[:]=6
    scope=functions(tmp_path,path);app=Flask(__name__)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    response=app.test_client().get('/volume')
    assert b'NaN' not in response.data and b'Infinity' not in response.data
    assert response.get_json()['sigma']==[-.75,None]
    assert response.get_json()['depth'][1][0][0]==3


def test_render_range_excludes_unpositioned_values_but_keeps_raw_data(tmp_path):
    from test_result_layers import functions
    path=tmp_path/'output.nc'
    with open_dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',2),('y',2),('x',2)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,-.25]
        ds.createVariable('bathymetry','f8',('y','x'))[:]=10
        v=ds.createVariable('temp','f8',('time','sigma','y','x'));v[:]=np.arange(8).reshape(1,2,2,2);v[:,:,0,0]=1000
        h=ds.createVariable('hn','f8',v.dimensions);h.units='m';h[:]=5;h[0,0,0,0]=0
    scope=functions(tmp_path,path);app=Flask(__name__)
    app.add_url_rule('/volume',view_func=scope['results_3d_surface'])
    data=app.test_client().get('/volume').get_json()
    assert data['min']==1 and data['max']==7
    assert data['data_min']==1 and data['data_max']==1000
    assert data['data'][0][0][0]==1000 and not data['valid_geometry'][0][0]
