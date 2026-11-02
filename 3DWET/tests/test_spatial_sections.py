import sys
from pathlib import Path
from types import SimpleNamespace

import netCDF4
import numpy as np
import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))


@pytest.fixture
def output(tmp_path):
    path = tmp_path / 'output.nc'
    with netCDF4.Dataset(path, 'w') as ds:
        for dim, size in [('time', 2), ('sigma', 2), ('y', 2), ('x', 3)]:
            ds.createDimension(dim, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-.75, -.25]
        x = ds.createVariable('xc', 'f8', ('x',)); x.units = 'm'; x[:] = [10, 20, 40]
        y = ds.createVariable('yc', 'f8', ('y',)); y.units = 'm'; y[:] = [100, 200]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[10, -10, 8], [10, 10, 8]]
        ds.createVariable('mask', 'i4', ('y', 'x'))[:] = [[1, 1, 1], [1, 0, 1]]
        v = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'), fill_value=-9999)
        v[:] = np.arange(24).reshape(2, 2, 2, 3)
        v[1, 1, 0, 2] = -9999
        ds.createVariable('hn', 'f8', v.dimensions)[:] = [[[ [6, 6, 2], [6, 6, 2]], [[4, 4, 6], [4, 4, 6]]]] * 2
        ds.createVariable('bottom', 'f8', ('time', 'y', 'x'))[:] = 1
    return path


def test_xz_uses_selected_time_dynamic_thickness_and_missing(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 1, 'xz', 0)
    assert result['horizontal'] == [10, 20, 40]
    assert result['data'] == [[12, None, 14], [18, None, None]]
    assert result['depth'] == [[7, None, 7], [2, None, 3]]
    assert result['depth_edges'] == [[10, None, 8], [4, None, 6], [0, None, 0]]
    assert result['depth_source'] == 'hn'
    assert result['fixed_coordinate'] == 100
    assert result['fixed_coordinate_units'] == 'm'


def test_yz_and_mask(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'yz', 1)
    assert result['horizontal'] == [100, 200]
    assert result['data'] == [[None, None], [None, None]]
    assert result['shape'] == [2, 2]


def test_sigma_fallback_keeps_actual_nonuniform_coordinates(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output, 'a') as ds:
        ds.renameVariable('hn', 'unused_hn')
        ds.variables['sigma'][:] = [-.8, -.1]
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'xz', 1)
    assert result['depth'][0][0] == 8
    assert result['depth'][1][0] == 1
    assert result['depth_source'] == 'sigma'


def test_native_padding(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output, 'a') as ds:
        ds.model = 'GETM'
        ds.variables['sigma'][:] = [-1, 0]
        ds.variables['temp'][:, 0] = -9999
        ds.variables['hn'][:, 0] = 0
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'xz', 0)
    assert result['shape'] == [1, 3]
    assert result['data'][0][0] == 6
    assert result['depth'][0][0] == 2


def test_native_section_keeps_boundary_valid_elsewhere(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output, 'a') as ds:
        ds.model = 'GETM'; ds['sigma'][:] = [-1, 0]
        ds['temp'][:, 0] = -9999
        ds['temp'][0, 0, 1, 2] = 0
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'xz', 0)
    assert result['shape'][0] == 2, 'physical layer identity cannot change with the selected row'
    assert result['data'][0] == [None, None, None]


def test_section_unknown_coordinate_units_fall_back_to_indices(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output, 'a') as ds:
        ds['xc'].delncattr('units'); ds['yc'].units = 'degrees_north'
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'xz', 1)
    assert result['horizontal'] == [0, 1, 2]
    assert result['coordinate_units'] == 'index'
    assert result['fixed_coordinate'] == 1
    assert result['fixed_coordinate_units'] == 'index'


def test_endpoint_errors_and_metadata(output):
    from spatial_sections import register
    app = Flask(__name__)
    context = SimpleNamespace(active_case_path=output.parent, _output_locked=lambda: False,
        find_output_files=lambda *args: {'3d': output}, nc_open=netCDF4.Dataset,
        _annotated_output=lambda item, case: dict(item, long_name_en='temperature'))
    register(app, context)
    client = app.test_client()
    assert client.get('/api/results/section?var=temp').json['long_name_en'] == 'temperature'
    for query in ['axis=xy', 'time=-1', 'time=2', 'index=2', 'time=abc', 'var=bottom', 'var=missing']:
        assert client.get('/api/results/section?' + query).status_code == 400
    context._output_locked = lambda: True
    assert client.get('/api/results/section').status_code == 409
    context._output_locked = lambda: False
    context.find_output_files = lambda *args: {}
    assert client.get('/api/results/section').status_code == 404


def test_endpoint_uses_input_axes_when_output_has_bathymetry_without_axes(output):
    from spatial_sections import register
    with netCDF4.Dataset(output, 'a') as ds:
        ds.renameVariable('xc', 'unused_xc'); ds.renameVariable('yc', 'unused_yc')
    with netCDF4.Dataset(output.parent / 'bathymetry.nc', 'w') as grid:
        grid.createDimension('x', 3); grid.createDimension('y', 2)
        x = grid.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [100, 200, 300]
        y = grid.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [1000, 2000]
        grid.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = 99
    app = Flask(__name__)
    context = SimpleNamespace(active_case_path=output.parent, _output_locked=lambda: False,
        find_output_files=lambda *args: {'3d': output}, nc_open=netCDF4.Dataset,
        _annotated_output=lambda item, case: item)
    register(app, context)
    result = app.test_client().get('/api/results/section?var=temp&axis=xz&index=0').json
    assert result['coordinate_mode'] == 'projected'
    assert result['horizontal'] == [100, 200, 300]
    assert result['fixed_coordinate'] == 1000
    assert result['bottom'] == [10, None, 8], 'output bathymetry remains preferred over input fallback'


def test_no_geometry_fabrication_or_invalid_thickness(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output, 'a') as ds:
        ds.variables['hn'][0, 0, 1, 0] = 0
    with netCDF4.Dataset(output) as ds:
        result = read_section(ds, 'temp', 0, 'xz', 1)
        assert result['data'][0][0] is None
        assert result['depth'][0][0] is None
    with netCDF4.Dataset(output, 'a') as ds:
        ds.renameVariable('hn', 'unused_hn')
        ds.renameVariable('sigma', 'unused_sigma')
    with netCDF4.Dataset(output) as ds:
        with pytest.raises(ValueError, match='sigma'):
            read_section(ds, 'temp', 0, 'xz', 0)


def test_reads_only_requested_spatial_hyperslab(output):
    from spatial_sections import read_section
    accesses = []
    class TrackedVariable:
        def __init__(self, var):
            self.var = var
        def __getattr__(self, name):
            return getattr(self.var, name)
        def __getitem__(self, key):
            accesses.append((self.var.name, key))
            return self.var[key]
    with netCDF4.Dataset(output) as ds:
        proxy = SimpleNamespace(variables={name: TrackedVariable(v) for name, v in ds.variables.items()})
        read_section(proxy, 'temp', 1, 'yz', 2)
    for name, key in accesses:
        if name in ('temp', 'hn'):
            assert key[0] == 1, 'only the selected time record is read'
            assert key[-1] == 2, 'only one fixed grid column is read'
        if name in ('bathymetry', 'mask'):
            assert key[-1] == 2, 'geometry is a section, never a full domain'


def test_section_and_volume_share_actual_zc_not_assumed_half_thickness(output):
    from spatial_sections import read_section
    with netCDF4.Dataset(output,'a') as ds:
        zc=ds.createVariable('zc','f8',ds['temp'].dimensions);zc.units='m'
        zc[:,0]=[[-7.2,-7.2,-7.1],[-7.2,-7.2,-7.1]]
        zc[:,1]=[[-2.2,-2.2,-3.1],[-2.2,-2.2,-3.1]]
    with netCDF4.Dataset(output) as ds:result=read_section(ds,'temp',1,'xz',0)
    assert result['depth'][0][0]==7.2
    assert result['depth'][1][0]==2.2
    assert result['geometry_source']=='hn+zc'
    assert result['depth_reference']=='below native 3D geometry surface'
