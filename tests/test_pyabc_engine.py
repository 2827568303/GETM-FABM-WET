"""Exercise real ABC-SMC populations, not a class-name proxy for SciPy."""
import builtins
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import calibration


def test_real_abc_smc_has_populations_posterior_and_database(tmp_path, monkeypatch):
    import pyabc
    np.random.seed(11011)
    def no_scipy(*args, **kwargs):
        raise AssertionError('ABC-SMC cannot execute SciPy')
    monkeypatch.setattr(calibration.ScipyEngine, 'calibrate', no_scipy)
    history = []
    result = calibration.PyabcEngine().calibrate(
        [dict(module='lake', param='rate', min=0, max=2)],
        lambda params: (params[0]['value'] - .7)**2,
        lambda n, p, obj: history.append(obj), max_iter=2, population_size=5,
        max_simulations=100, database_path=tmp_path/'abc.db')
    assert result['success'], result
    assert result['engine'] == 'pyabc-abcsmc'
    assert result['n_populations'] == 2
    assert result['posterior'] and len(result['posterior']) == 5
    assert sum(p['weight'] for p in result['posterior']) == pytest.approx(1)
    assert all(0 <= p['params'][0]['value'] <= 2 for p in result['posterior'])
    assert len(history) == result['n_iterations']
    assert result['best_objective'] == min(history)
    assert (tmp_path/'abc.db').is_file()
    stored = pyabc.History('sqlite:///'+(tmp_path/'abc.db').as_posix())
    assert stored.n_populations == 2


def test_abc_missing_package_has_explicit_scipy_fallback(monkeypatch):
    original = builtins.__import__
    def missing(name, *a, **kw):
        if name == 'pyabc':
            raise ImportError('missing')
        return original(name, *a, **kw)
    monkeypatch.setattr(builtins, '__import__', missing)
    scipy_calls = []
    monkeypatch.setattr(calibration.ScipyEngine, 'calibrate', lambda *a, **kw:
                        scipy_calls.append((a, kw)) or dict(success=True, best_params=[], best_objective=0))
    result = calibration.PyabcEngine().calibrate([], lambda p: 0, max_simulations=17)
    assert result['engine'] == 'scipy-lbfgsb'
    assert 'pyabc' in result['fallback']
    assert scipy_calls[0][1]['max_simulations'] == 17


def test_abc_missing_package_requires_explicit_cap_even_for_scipy_fallback(monkeypatch):
    original = builtins.__import__
    def missing(name, *a, **kw):
        if name == 'pyabc':
            raise ImportError('missing')
        return original(name, *a, **kw)
    monkeypatch.setattr(builtins, '__import__', missing)
    with pytest.raises(ValueError, match='评估次数'):
        calibration.PyabcEngine().calibrate([], lambda p: 0)


def test_abc_stop_propagates_without_scipy_or_success(tmp_path):
    def stopped(params):
        raise calibration.CalibrationStopped('用户停止')
    result = calibration.PyabcEngine().calibrate(
        [dict(module='x', param='rate', min=0, max=2)], stopped,
        max_iter=2, population_size=2, max_simulations=10, database_path=tmp_path/'stop.db')
    assert not result['success']
    assert '停止' in result['error']


def test_scipy_resolves_model_output_precision():
    result = calibration.ScipyEngine().calibrate(
        [dict(module='lake', param='rate', min=0, max=2)],
        lambda ps: (round(ps[0]['value'], 5) - .7)**2, max_iter=10)
    assert result['success'], result
    assert result['best_objective'] < 1e-5


def test_scipy_iteration_budget_caps_expensive_model_evaluations():
    calls = []

    def objective(params):
        x, y = (p['value'] for p in params)
        calls.append((x, y))
        return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

    result = calibration.ScipyEngine().calibrate(
        [dict(module='lake', param='a', min=-2, max=2),
         dict(module='lake', param='b', min=-1, max=3)],
        objective, max_iter=10)

    assert len(calls) <= 50, 'finite differences and line search must stay within the derived evaluation budget'
    assert result['n_iterations'] == len(result['history']) == len(calls)
    assert result['max_evaluations'] == 50
    assert result['success'], result
    assert result['message'] == 'Configured L-BFGS-B evaluation budget reached; returned the best observed trial.'
    assert result['best_objective'] == min(row['objective'] for row in result['history'])


def test_scipy_rmse_uses_smooth_equivalent_but_reports_original_distance():
    calls=[]
    def rmse(params):
        value=params[1]['value']
        distance=abs(round(value,7)-.003)
        calls.append(distance)
        return distance
    result=calibration.ScipyEngine().calibrate(
        [dict(module='diatoms',param='rate',min=1.2,max=3.6),
         dict(module='POM',param='rate',min=.0005,max=.0035)],
        rmse,max_iter=10,squared_distance=True)
    assert result['success'],result
    assert result['best_objective']<1e-7
    assert result['best_objective']==pytest.approx(abs(round(result['best_params'][1]['value'],7)-.003))
    assert len(calls)<=20,'Line search repeatedly runs the expensive native solver'
    assert result['history'][0]['objective']==calls[0]


def test_scipy_squared_distance_stops_at_verified_zero_without_more_trials():
    calls = []
    callbacks = []

    def distance(params):
        # A nonnegative distance with a flat exact-fit region, as occurs when
        # native float output quantizes nearby parameter values identically.
        value = max(0.0, abs(params[0]['value'] - .3) - .025)
        calls.append(value)
        return value

    result = calibration.ScipyEngine().calibrate(
        [dict(module='lake', param='rate', min=0, max=1)], distance,
        callback=lambda *args: callbacks.append(args), max_iter=10,
        squared_distance=True)
    assert result['success'], result
    assert result['best_objective'] == 0
    assert calls[-1] == 0
    assert calls.count(0) == 1, 'Zero distance is the known global minimum; do not run more models'
    assert result['n_iterations'] == len(calls) == len(callbacks)
    assert result['best_params'] == result['history'][-1]['params']


def test_scipy_generic_objective_zero_is_not_assumed_a_global_minimum():
    result = calibration.ScipyEngine().calibrate(
        [dict(module='lake', param='rate', min=0, max=1)],
        lambda ps: ps[0]['value'] - .5, max_iter=10)
    assert result['success'], result
    assert result['best_objective'] < 0


def test_abc_progress_is_not_population_count_divided_by_evaluations(tmp_path, monkeypatch):
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, [], {}, None, None))
    job = calibration.CalibrationJob('progress', 'pyabc', [], 'rmse', 2, tmp_path,
                                     engine_options={'population_size':10,'max_simulations':100})
    observed = []
    class Engine:
        def calibrate(self, params, fn, callback, **kw):
            callback(2, [], 1)
            observed.append(job.progress)
            return dict(success=True, best_objective=1, best_params=[], engine='pyabc-abcsmc')
    monkeypatch.setattr(calibration, 'PyabcEngine', Engine)
    job._run()
    assert 0 < observed[0] < 1
    assert job.progress == 1


def test_scipy_progress_uses_evaluation_budget_not_optimizer_iteration_limit(tmp_path, monkeypatch):
    points = [{'id': 'P1', 'variables': ['temp']}]
    data = {'P1': {'temp': [12.5]}}
    monkeypatch.setattr(calibration, '_server_helpers', lambda *a, **kw:
                        (None, None, None, None, points, data, None, None))
    params = [dict(module='lake', param='a', min=0, max=1),
              dict(module='lake', param='b', min=0, max=1)]
    job = calibration.CalibrationJob('scipy-progress', 'scipy', params, 'rmse', 2, tmp_path)
    observed = []

    class Engine:
        def calibrate(self, params, fn, callback, **kw):
            callback(2, [], 1)
            observed.append(job.progress)
            return dict(success=True, best_objective=1, best_params=[], engine='scipy.lbfgsb')

    monkeypatch.setattr(calibration, 'ScipyEngine', Engine)
    job._run()
    assert observed == [pytest.approx(.2)]
    assert job.progress == 1
