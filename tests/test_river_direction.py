"""Exercise the real endpoint function without starting server discovery."""
import ast
import json
import threading
from pathlib import Path
import sys

import numpy as np
import pytest
from flask import Flask, jsonify

APP_DIR = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP_DIR))
from netcdf_io import open_dataset


@pytest.mark.parametrize('kind, expected', [('outflow', [-3, -4]), ('inflow', [3, 4]), ('signed', [-3, 4]), (None, [-3, 4])])
def test_input_save_honors_explicit_direction_preserves_legacy(tmp_path, kind, expected):
    source = ast.parse((APP_DIR / 'server.py').read_text(encoding='utf-8-sig'))
    function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'input_rivers_save')
    function.decorator_list = []
    module = ast.Module(body=[function], type_ignores=[])
    river = {'i': 1, 'j': 1, 'name': 'TEST'}
    if kind: river['kind'] = kind
    (tmp_path / 'river_drafts').mkdir()
    (tmp_path / 'river_drafts' / 'TEST.json').write_text(json.dumps({'dates': ['2026-10-01', '2026-10-02'], 'Q': [-3, 4], 'temp': [20, 20], 'nh4': [0, 0], 'no3': [0, 0], 'po4': [0, 0]}))
    from datetime import datetime
    namespace = {'active_case_path': tmp_path, '_load_case_meta': lambda: {'rivers': [river]},
                 '_river_cell_problems': lambda *a: ([], []), '_current_case_start': lambda d: d,
                 '_NC_LOCK': threading.RLock(), 'jsonify': jsonify, 'json': json, 'np': np,
                 'datetime': datetime, 'open_dataset': open_dataset, 'nc_open': open_dataset}
    exec(compile(module, 'server.py', 'exec'), namespace)
    with Flask(__name__).test_request_context():
        response = namespace['input_rivers_save']()
        assert response.get_json()['success']
    with open_dataset(tmp_path / 'rivers.nc') as ds:
        assert list(ds['TEST'][:]) == expected
