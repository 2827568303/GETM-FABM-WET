"""Restored active-case metadata must initialize dashboard statistics."""
import ast
from pathlib import Path
from flask import Flask, jsonify


def test_current_case_identity_includes_dashboard_context(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    node = next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == 'current_case_identity')
    node.decorator_list = []
    case = tmp_path / 'restored'
    case.mkdir()
    (case / 'fabm.yaml').write_text('instances: {}', encoding='utf-8')
    scope = {
        'Path': Path, 'jsonify': jsonify,
        '_proxy_case_fields': lambda _path: {},
        '_active_case_snapshot': lambda: (case, 4),
        '_active_case_is_read_only_gotm': lambda: False,
        '_native_output_time_range': lambda _path: None,
        '_is_trusted_gotm_working_copy': lambda _path: False,
        '_is_gotm_result_dir': lambda _path: False,
        'cached_getm_config': None, 'cached_fabm_info': None,
        'parse_getm_inp': lambda path: {'source': str(path)},
        'get_run_info': lambda config: {'nlev': 8},
        'parse_fabm_yaml': lambda path, persist_defaults: {'total_modules': 3, 'modules': []},
        'find_output_files': lambda path: {'2d': path / 'lake.2d.nc', '3d': None},
        'get_ntimesteps': lambda path: 24,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), scope)
    app = Flask(__name__)
    app.add_url_rule('/current', view_func=scope['current_case_identity'])
    response = app.test_client().get('/current')
    assert response.status_code == 200
    data = response.get_json()
    assert data['run_info']['nlev'] == 8
    assert data['fabm']['total_modules'] == 3
    assert data['has_results'] is True
    assert data['output_ntimesteps'] == 24
