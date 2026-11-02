"""Case rows must agree with the result reader after native output archival."""
import ast
from collections import OrderedDict
from pathlib import Path
import threading

import netCDF4 as nc
import pytest
from flask import Flask, jsonify


def case_list(case_root):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    names = {'list_cases', 'find_output_files', '_nc_time_len', 'get_ntimesteps'}
    nodes = [node for node in ast.parse(source.read_text(encoding='utf-8')).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    for node in nodes:
        node.decorator_list = []
    scope = dict(Path=Path, CASE_DIR=case_root, LEGACY_CASE_DIR=case_root,
                 PROXY_CASE_DIR=case_root,
                 jsonify=jsonify, nc_open=nc.Dataset,
                 _proxy_case_fields=lambda _path: {},
                 is_system_drive=lambda _path: False,
                 _is_trusted_gotm_working_copy=lambda _path: False,
                 _load_external_cases=lambda: [],
                 _output_selection_cache=OrderedDict(),
                 _output_selection_cache_lock=threading.RLock(),
                 _is_gotm_result_dir=lambda _path: False)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), scope)
    app = Flask(__name__)
    with app.app_context():
        return scope['list_cases']().get_json()


@pytest.mark.parametrize('folder,records', [('', 2), ('', 0), ('output', 2), ('output', 0)])
def test_native_outputs_in_root_and_archive(tmp_path, folder, records):
    case = tmp_path / 'Lake'
    (case / folder).mkdir(parents=True)
    (case / 'getm.inp').write_text('&time\n/\n')
    for kind in ('2d', '3d'):
        with nc.Dataset(case / folder / f'lake.{kind}.nc', 'w') as ds:
            ds.createDimension('time', None)
            ds.createVariable('time', 'f8', ('time',))[:] = list(range(records))
    row = case_list(tmp_path)[0]
    assert row['has_2d_output'] is bool(records)
    assert row['has_3d_output'] is bool(records)


def test_flexout_only_is_visible_and_empty_root_shell_does_not_hide_archive(tmp_path):
    case = tmp_path / 'Lake'
    (case / 'output').mkdir(parents=True)
    (case / 'getm.inp').write_text('&time\n/\n')
    with nc.Dataset(case / 'output' / 'output.nc', 'w') as ds:
        ds.createDimension('time', 1)
        ds.createVariable('time', 'f8', ('time',))[:] = [60]
    (case / 'empty.3d.nc').write_bytes(b'')
    row = case_list(tmp_path)[0]
    assert row['has_3d_output'] is True
    assert row['has_2d_output'] is False
