"""Dashboard must recognize the native chlorophyll diagnostic name."""
import ast
from pathlib import Path

import netCDF4 as nc
import numpy as np
from flask import Flask, jsonify, request
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'3DWET/app'))
from variable_api import metadata


def test_six_native_dashboard_variables(tmp_path):
    path = tmp_path / 'output.nc'
    names = ['temp', 'abiotic_water_sO2W', 'abiotic_water_sNO3W',
             'abiotic_water_sPO4W', 'wet_chla_calculator_result', 'POM_sDW']
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 2), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        for i, name in enumerate(names):
            ds.createVariable(name, 'f8', ('time', 'sigma', 'y', 'x'))[:] = i + 1
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'results_state_vars_surface')
    node.decorator_list = []
    scope = dict(np=np, nc_open=nc.Dataset, request=request, jsonify=jsonify,
                 active_case_path=tmp_path, _output_locked=lambda: False,
                 find_output_files=lambda *a: {'3d': path, '2d': None}, get_ntimesteps=lambda *a: 1,
                 _annotated_output=metadata)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    app = Flask(__name__)
    app.add_url_rule('/dashboard', view_func=scope['results_state_vars_surface'])
    response = app.test_client().get('/dashboard')
    assert response.status_code == 200
    fields = response.get_json()
    assert set(fields) == set(names)
    assert fields['wet_chla_calculator_result']['mean'] == 5
    assert fields['temp']['zh_name'] and fields['temp']['en_name']
