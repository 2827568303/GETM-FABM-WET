"""HTTP calibration configuration must reach the engine without silent loss."""
import ast
import sys
from datetime import datetime
from pathlib import Path

import pytest
from flask import Flask, request, jsonify

APP_DIR = Path(__file__).resolve().parents[1] / '3DWET/app'
sys.path.insert(0, str(APP_DIR))
import calibration


@pytest.fixture
def service(tmp_path, monkeypatch):
    nodes = [n for n in ast.parse((APP_DIR/'server.py').read_text(encoding='utf-8')).body
             if isinstance(n, ast.FunctionDef) and n.name == 'calibration_auto_start']
    nodes[0].decorator_list = []
    calls = []
    monkeypatch.setattr(calibration, 'start_calibration_job', lambda *a, **kw: calls.append((a, kw)) or 'test-job')
    scope = dict(active_case_path=tmp_path, DATA_DIR=tmp_path, request=request, jsonify=jsonify,
                 save_json=lambda *a: None, datetime=datetime, np=__import__('numpy'))
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'server.py', 'exec'), scope)
    app = Flask(__name__)
    app.add_url_rule('/start', view_func=scope['calibration_auto_start'], methods=['POST'])
    return app.test_client(), calls


def body():
    return dict(method='pyabc', iterations=2, objective='rmse', point_ids=['a'],
                params=[dict(module='POM', param='kDMinW', min=.01, max=.1)],
                objective_weights=[dict(point_id='a', variable='temp', weight=2, scale=5)],
                population_size=3, max_simulations=30, minimum_epsilon=.01)


def test_request_preserves_weights_and_abc_controls(service):
    client, calls = service
    response = client.post('/start', json=body())
    assert response.status_code == 200, response.get_json()
    _, options = calls[0]
    assert options['objective_weights'] == body()['objective_weights']
    assert options['engine_options'] == dict(population_size=3, max_simulations=30, minimum_epsilon=.01)


@pytest.mark.parametrize('key,value', [('iterations', 'oops'), ('iterations', 0),
    ('iterations', 1.5), ('population_size', 1), ('population_size', 2.5),
    ('minimum_epsilon', -1), ('max_simulations', 1), ('method', 'nonexistent'),
    ('objective', 'unrecognized')])
def test_invalid_configuration_never_starts_job(service, key, value):
    client, calls = service
    data = body(); data[key] = value
    response = client.post('/start', json=data)
    assert response.status_code == 400
    assert not calls


def test_pyabc_budget_must_be_explicit(service):
    client, calls = service
    data = body(); data.pop('max_simulations')
    response = client.post('/start', json=data)
    assert response.status_code == 400
    assert 'max_simulations' in response.get_json()['error']
    assert not calls


def test_pyabc_budget_must_cover_two_particles_per_population(service):
    client, calls = service
    data = body(); data['max_simulations'] = data['population_size'] * 2 - 1
    response = client.post('/start', json=data)
    assert response.status_code == 400
    assert not calls


def test_scipy_budget_must_be_explicit(service):
    client, calls = service
    data = body(); data['method'] = 'scipy'; data.pop('max_simulations')
    response = client.post('/start', json=data)
    assert response.status_code == 400
    assert 'max_simulations' in response.get_json()['error']
    assert not calls


def test_scipy_budget_is_passed_as_the_model_evaluation_cap(service):
    client, calls = service
    data = body(); data['method'] = 'scipy'; data['max_simulations'] = 23
    response = client.post('/start', json=data)
    assert response.status_code == 200, response.get_json()
    _, options = calls[0]
    assert options['engine_options'] == {'max_simulations': 23}
