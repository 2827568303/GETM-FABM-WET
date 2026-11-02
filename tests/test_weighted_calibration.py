"""Weights apply to station-variable series, not to their sampling frequency."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import calibration


@pytest.fixture
def observations(monkeypatch):
    points = [{'id': 'a', 'variables': ['temp']}, {'id': 'b', 'variables': ['oxygen']}]
    def pair(obs, sim):
        return ([{'obs': o, 'sim': s} for o, s in zip(obs, sim)], {})
    monkeypatch.setattr(calibration, '_server_helpers', lambda **kw:
                        (None, None, None, None, points, {}, pair, None))
    data = {'a': {'temp': [0]}, 'b': {'oxygen': [0, 0, 0]}}
    outputs = {'a/temp': [2], 'b/oxygen': [4, 4, 4]}
    return points, data, outputs


def test_default_rmse_gives_each_series_equal_weight(observations):
    points, data, outputs = observations
    assert calibration.compute_objective(outputs, points_snapshot=points, data_snapshot=data) == pytest.approx(np.sqrt(10))


def test_explicit_scale_and_weights_use_normalized_series_mse(observations):
    points, data, outputs = observations
    weights = [{'point_id': 'a', 'variable': 'temp', 'weight': 3, 'scale': 2},
               {'point_id': 'b', 'variable': 'oxygen', 'weight': 1, 'scale': 4}]
    assert calibration.compute_objective(outputs, points_snapshot=points, data_snapshot=data,
                                         objective_weights=weights) == 1
    weights[1]['weight'] = 0
    outputs['b/oxygen'] = [1e9] * 3
    assert calibration.compute_objective(outputs, points_snapshot=points, data_snapshot=data,
                                         objective_weights=weights) == 1


@pytest.mark.parametrize('row', [
    {'point_id': 'unknown', 'variable': 'temp', 'weight': 1, 'scale': 1},
    {'point_id': 'a', 'variable': 'wrong', 'weight': 1, 'scale': 1},
    {'point_id': 'a', 'variable': 'temp', 'weight': -1, 'scale': 1},
    {'point_id': 'a', 'variable': 'temp', 'weight': 1, 'scale': 0},
    {'point_id': 'a', 'variable': 'temp', 'weight': float('nan'), 'scale': 1},
])
def test_invalid_weights_rejected(observations, row):
    points, _, _ = observations
    with pytest.raises(ValueError):
        calibration.validate_objective_weights(points, [row])


def test_duplicate_weights_rejected(observations):
    points, _, _ = observations
    row = dict(point_id='a', variable='temp', weight=1, scale=1)
    with pytest.raises(ValueError):
        calibration.validate_objective_weights(points, [row, row])


def test_missing_positive_weight_series_cannot_improve_score(observations):
    points, data, outputs = observations
    del outputs['b/oxygen']
    assert calibration.compute_objective(outputs, points_snapshot=points, data_snapshot=data) >= 1e10


def test_zero_weight_series_can_be_absent(observations):
    points, data, outputs = observations
    del outputs['b/oxygen']
    weights = [dict(point_id='b', variable='oxygen', weight=0, scale=1)]
    assert calibration.compute_objective(outputs, points_snapshot=points, data_snapshot=data,
                                         objective_weights=weights) == 2
