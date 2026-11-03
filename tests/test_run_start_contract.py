import ast
import threading
from pathlib import Path

from flask import Flask, jsonify, request


def _run_start_client(tmp_path):
    source = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'run_start')
    function.decorator_list = []
    scope = {
        'request': request,
        'jsonify': jsonify,
        '_mpi_tuning_state': {'status': 'idle'},
        '_core_calibration_lock': threading.Lock(),
        '_core_calibration': {'status': 'idle', 'error': None},
        'run_thread': None,
        'run_status': 'running',
        'active_case_path': tmp_path,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), 'exec'), scope)
    app = Flask(__name__)
    app.add_url_rule('/api/run/start', view_func=scope['run_start'], methods=['POST'])
    return app.test_client()


def test_run_start_rejects_non_object_json_with_400_without_changing_empty_or_object_requests(tmp_path):
    client = _run_start_client(tmp_path)

    for body in ('"not-an-object"', '[1, 2]', 'null'):
        response = client.post('/api/run/start', data=body, content_type='application/json')
        assert response.status_code == 400
        assert 'JSON 对象' in response.get_json()['error']

    empty = client.post('/api/run/start')
    assert empty.status_code == 400
    assert empty.get_json()['error'] == '模型正在运行中'

    normal = client.post('/api/run/start', json={'compress_results': False})
    assert normal.status_code == 400
    assert normal.get_json()['error'] == '模型正在运行中'
