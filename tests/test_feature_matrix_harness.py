"""Regression checks for feature-matrix expectations against current help API."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import verify_feature_matrix as feature_matrix


def test_preprocess_help_accepts_polygon_or_multipolygon_boundary_label():
    payload = {
        'boundary': {'geometry': 'Polygon or MultiPolygon'},
        'bathymetry_point': {'geometry': 'Point'},
    }
    validator = getattr(feature_matrix, 'validate_preprocess_help', None)
    assert callable(validator), 'feature harness must accept the API documented geometry labels'
    assert validator(payload) is True


def test_preprocess_help_still_rejects_unexpected_geometry():
    payload = {
        'boundary': {'geometry': 'LineString'},
        'bathymetry_point': {'geometry': 'Point'},
    }
    validator = getattr(feature_matrix, 'validate_preprocess_help', None)
    assert callable(validator), 'feature harness must validate help metadata explicitly'
    with pytest.raises(AssertionError, match='Preprocess help metadata incorrect'):
        validator(payload)


@pytest.mark.parametrize(('candidate_count','iterations'),[(1,2),(4,2)])
def test_calibration_start_payload_sets_explicit_budget_for_all_candidates(candidate_count,iterations):
    builder=getattr(feature_matrix,'calibration_start_payload',None)
    assert callable(builder),'feature verifier must follow the auto-start max_simulations contract'
    config={'parameters':[{'module':'abiotic_water','param':f'p{i}','min':0,'max':1}
                          for i in range(candidate_count)]}
    payload=builder(config,iterations=iterations,point_ids=['synthetic-point'])
    assert payload['point_ids']==['synthetic-point']
    assert payload['max_simulations']>=candidate_count
    assert payload['max_simulations']>=iterations
    assert payload['params']==config['parameters']


def test_calibration_start_payload_rejects_empty_explicit_point_scope():
    builder=feature_matrix.calibration_start_payload
    with pytest.raises(ValueError,match='point_ids must be a non-empty list'):
        builder({'parameters':[{'module':'m','param':'p','min':0,'max':1}]},point_ids=[])
