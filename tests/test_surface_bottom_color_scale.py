"""Surface and bottom stay distinct after the native k=0 padding trim.

The Dianchi flexout temperature field reaches a local surface-bottom
difference of about 5.46 C while the means stay within 0.3 C. k=0 padding
is a separate native-file slot and is not that difference.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from flask import Flask

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))
from netcdf_io import open_dataset

_spec = importlib.util.spec_from_file_location(
    'test_result_layers', Path(__file__).with_name('test_result_layers.py'))
_layers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_layers)


def _write_stratified(path):
    with open_dataset(path, 'w') as ds:
        ds.comment = 'file created by flexout'
        for name, size in [('time', 1), ('sigma', 2), ('yc', 2), ('xc', 2)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-0.5, 0.0]
        ds.createVariable('time', 'f8', ('time',))[:] = [0]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = [[5, 6], [7, 8]]
        temp = ds.createVariable('temp', 'f4', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        values = np.array([[[[10.0, 11.0], [12.0, 12.0]],
                             [[15.46, 16.0], [17.0, 17.46]]]], dtype='f4')
        temp[:] = values
        temp.units = 'degC'
        elev = ds.createVariable('elev', 'f4', ('time', 'yc', 'xc'))
        elev[:] = np.array([[[1.0, 2.0], [3.0, 4.0]]], dtype='f4')
    return values


def _write_native_padding(path):
    with open_dataset(path, 'w') as ds:
        ds.model = 'GETM - www.getm.eu'
        for name, size in [('time', 1), ('sigma', 3), ('yc', 2), ('xc', 2)]:
            ds.createDimension(name, size)
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-1.0, -0.5, 0.0]
        ds.createVariable('time', 'f8', ('time',))[:] = [0]
        ds.createVariable('bathymetry', 'f8', ('yc', 'xc'))[:] = [[5, 6], [7, 8]]
        temp = ds.createVariable('temp', 'f4', ('time', 'sigma', 'yc', 'xc'), fill_value=-9999)
        values = np.full((1, 3, 2, 2), -9999, dtype='f4')
        values[0, 1] = 10
        values[0, 2] = 15.46
        temp[:] = values


def test_api_returns_different_surface_and_bottom_and_skips_padding(tmp_path):
    path = tmp_path / 'stratified.nc'
    _write_stratified(path)
    scope = _layers.functions(tmp_path, path)
    bottom = scope['get_2d_field'](path, 'temp', level=0, include_bathymetry=False)
    surface = scope['get_2d_field'](path, 'temp', level=-1, include_bathymetry=False)
    assert bottom['level_applies'] is True and surface['level_applies'] is True
    assert bottom['level'] == 0 and surface['level'] == 1
    assert bottom['min'] == pytest.approx(10)
    assert surface['min'] == pytest.approx(15.46)
    assert surface['max'] - bottom['max'] > 5
    contrast = surface['layer_contrast']
    assert contrast['max_abs_diff'] == pytest.approx(5.46)
    assert contrast['surface_mean'] > contrast['bottom_mean']
    assert contrast['well_mixed'] is False

    flat = scope['get_2d_field'](path, 'elev', level=0, include_bathymetry=False)
    other = scope['get_2d_field'](path, 'elev', level=5, include_bathymetry=False)
    assert flat['level_applies'] is False and flat['level'] is None
    assert flat['data'] == other['data']
    assert flat['min'] == other['min'] and flat['max'] == other['max']
    assert flat['layer_contrast'] is None

    native = tmp_path / 'native.nc'
    _write_native_padding(native)
    native_scope = _layers.functions(tmp_path, native)
    physical_bottom = native_scope['get_2d_field'](native, 'temp', level=0, include_bathymetry=False)
    physical_surface = native_scope['get_2d_field'](native, 'temp', level=-1, include_bathymetry=False)
    assert physical_bottom['data'][0][0] == 10
    assert physical_surface['data'][0][0] == pytest.approx(15.46)
    assert physical_bottom['layer_contrast']['bottom_index'] == 1
    assert physical_bottom['layer_contrast']['max_abs_diff'] == pytest.approx(5.46)

    app = Flask(__name__)
    app.add_url_rule('/field', view_func=scope['results_2d'])
    app.add_url_rule('/volume', view_func=scope['results_3d_surface'])
    client = app.test_client()
    bed = client.get('/field?var=temp&time=0&level=0&include_bathymetry=0').get_json()
    top = client.get('/field?var=temp&time=0&level=-1&include_bathymetry=0').get_json()
    assert bed['min'] != top['min']
    assert top['layer_contrast']['max_abs_diff'] == pytest.approx(5.46)
    low = client.get('/volume?var=temp&time=0&level=0&layer_only=1&target=8').get_json()
    high = client.get('/volume?var=temp&time=0&level=-1&layer_only=1&target=8').get_json()
    assert low['min'] == pytest.approx(10)
    assert high['min'] == pytest.approx(15.46)
    assert low['max'] != high['max']
    assert low['layer_indices'] == [0] and high['layer_indices'] == [1]


def test_frontend_color_scale_follows_the_selected_layer():
    script = ROOT / '3DWET' / 'tests' / 'test_layer_color_scale.js'
    completed = subprocess.run(['node', '--test', str(script)], cwd=ROOT,
                               capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stdout + completed.stderr
