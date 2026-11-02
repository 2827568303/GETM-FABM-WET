from pathlib import Path
import sys

import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_pairing_interpolates_native_time_depth_and_known_units():
    from observation_matching import pair_observations
    obs = [{'time': '2020-01-01 00:30:00', 'time_basis': 'source_naive', 'value': 5,
            'depth_m': 5, 'unit': 'mg/L', 'mass_basis': 'O2', 'variable': 'DO', 'lake_id': 'L', 'station_id': 'S', 'source_line': 1}]
    model = {'times': ['2020-01-01 00:00:00', '2020-01-01 01:00:00'],
             'center_depth': [[2, 8], [2, 8]], 'values': [[[0, 10]], [[10, 20]]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified', 'unit': 'g/m3', 'mass_basis': 'O2', 'variable': 'DO', 'representativeness': 'station'}
    pairs, diagnostics = pair_observations(obs, model, max_time_gap_hours=2)
    assert not diagnostics
    assert len(pairs) == 1 and pairs[0]['sim'] == pytest.approx(10)
    assert pairs[0]['time_weight'] == pytest.approx(.5)
    assert pairs[0]['depth_weight'] == pytest.approx(.5)


def test_max_time_gap_limits_distance_to_nearest_model_sample_not_bracket_width():
    from observation_matching import pair_observations
    model = {'times': ['2020-01-01 00:00:00', '2020-01-02 00:00:00'],
             'center_depth': [[1], [1]], 'values': [[0], [24]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified',
             'unit': 'degC', 'variable': 'T', 'representativeness': 'station'}
    midpoint = {'time': '2020-01-01 12:00:00', 'value': 12, 'depth_m': 1,
                'unit': 'degC', 'variable': 'T', 'lake_id': 'L', 'station_id': 'S'}
    pairs, diagnostics = pair_observations([midpoint], model, max_time_gap_hours=12)
    assert diagnostics == []
    assert len(pairs) == 1 and pairs[0]['sim'] == pytest.approx(12)
    assert pairs[0]['model_times'] == model['times']
    assert pairs[0]['time_weight'] == pytest.approx(.5)

    farther = dict(midpoint, time='2020-01-01 12:30:00')
    pairs, diagnostics = pair_observations([farther], model, max_time_gap_hours=11.4)
    assert pairs == [] and diagnostics[0]['reason'] == 'time_gap_exceeds_limit'


@pytest.mark.parametrize('model,reason', [
    ({'lake_id': 'B'}, 'lake_mismatch'),
    ({'lake_id': 'A', 'station_id': None}, 'unknown_station'),
    ({'lake_id': 'A', 'station_id': 'S'}, 'no_time_overlap'),
])
def test_pairing_refuses_unjustified_mapping(model, reason):
    from observation_matching import pair_observations
    obs = [{'time': '2020-01-01 00:00:00', 'value': 1, 'depth_m': 1, 'unit': 'degC', 'variable': 'T', 'lake_id': 'A', 'station_id': 'S'}]
    base = {'times': ['2021-01-01 00:00:00'], 'values': [[[1]]], 'center_depth': [[1]],
            'lake_id': 'A', 'station_id': 'S', 'spatial_mapping': 'verified', 'unit': 'degC', 'variable': 'T', 'representativeness': 'station'}
    base.update(model)
    pairs, diagnostics = pair_observations(obs, base, max_time_gap_hours=2)
    assert pairs == [] and diagnostics[0]['reason'] == reason


def test_matching_requires_known_units_basis_and_explicit_gap_and_excludes_quality():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01 00:30:00', 'value': 2, 'depth_m': 1, 'unit': 'mg/L',
           'mass_basis': 'N', 'variable': 'NH4', 'lake_id': 'L', 'station_id': 'S'}
    model = {'times': ['2020-01-01 00:00:00', '2020-01-01 01:00:00'], 'values': [[1], [3]],
             'center_depth': [[1], [1]], 'lake_id': 'L', 'station_id': 'S', 'unit': 'g/m3',
             'mass_basis': 'N', 'variable': 'NH4', 'spatial_mapping': 'verified', 'representativeness': 'station'}
    pairs, diag = pair_observations([obs], model)
    assert pairs == [] and diag[0]['reason'] == 'explicit_positive_max_time_gap_required'
    pairs, diag = pair_observations([dict(obs, mass_basis=None)], model, max_time_gap_hours=2)
    assert pairs == [] and diag[0]['reason'] == 'mass_basis_requires_explicit_N'
    pairs, diag = pair_observations([dict(obs, unit='')], model, max_time_gap_hours=2)
    assert pairs == [] and diag[0]['reason'] == 'unknown_or_missing_unit'
    pairs, diag = pair_observations([dict(obs, quality=['physical_range_review'])], model, max_time_gap_hours=2)
    assert pairs == [] and diag[0]['reason'] == 'observation_quality_review'


def test_same_source_row_is_not_reused_and_moving_layers_interpolate_each_time():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01 00:30:00', 'value': 5, 'depth_m': 5, 'unit': 'degC',
           'variable': 'T', 'lake_id': 'L', 'station_id': 'S', 'source_sha256': 'abc', 'source_line': 7}
    model = {'times': ['2020-01-01 00:00:00', '2020-01-01 01:00:00'],
             'values': [[0, 10], [12, 18]], 'center_depth': [[2, 8], [4, 10]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified', 'unit': 'degC', 'variable': 'T', 'representativeness': 'station'}
    pairs, diagnostics = pair_observations([obs, dict(obs)], model, max_time_gap_hours=2)
    assert pairs[0]['sim'] == pytest.approx(9)
    assert pairs[0]['depth_weights'] == pytest.approx([0.5, 1/6])
    assert pairs[0]['time_weight'] == pytest.approx(0.5)
    assert diagnostics[0]['reason'] == 'observation_reused'


def test_unknown_station_coordinates_and_extrapolation_are_rejected():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01 00:00:00', 'value': 2, 'depth_m': 10, 'unit': 'degC',
           'variable': 'T', 'lake_id': 'L', 'station_id': 'S'}
    model = {'times': ['2020-01-01 00:00:00'], 'values': [[1, 3]], 'center_depth': [[1, 5]],
             'lake_id': 'L', 'station_id': 'S', 'unit': 'degC', 'variable': 'T',
             'representativeness': 'station'}
    pairs, diag = pair_observations([obs], model, max_time_gap_hours=1)
    assert not pairs and diag[0]['reason'] == 'unknown_station_coordinates'
    model['spatial_mapping'] = 'verified'
    pairs, diag = pair_observations([obs], model, max_time_gap_hours=1)
    assert not pairs and diag[0]['reason'] == 'depth_outside_model_centers'


def test_mass_basis_requires_explicit_basis_for_nutrient():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01', 'value': 1, 'depth_m': 1, 'unit': 'mg/L', 'mass_basis': 'N',
           'variable': 'NH4', 'lake_id': 'L', 'station_id': 'S'}
    model = {'times': ['2020-01-01'], 'values': [[1]], 'center_depth': [[1]], 'lake_id': 'L',
             'station_id': 'S', 'spatial_mapping': 'verified', 'unit': 'g/m3',
             'variable': 'NH4', 'representativeness': 'station'}
    pairs, diag = pair_observations([obs], model, max_time_gap_hours=1)
    assert not pairs and diag[0]['reason'] == 'mass_basis_metadata_missing'


def test_generic_mass_concentration_matches_element_unit_only_with_same_explicit_basis():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01', 'value': 2, 'depth_m': 1, 'unit': 'g/m3', 'mass_basis': 'N',
           'variable': 'NO3', 'lake_id': 'L', 'point_id': 'P'}
    model = {'times': ['2020-01-01'], 'values': [[2]], 'center_depth': [[1]], 'lake_id': 'L',
             'unit': 'gN/m3', 'mass_basis': 'N', 'variable': 'NO3', 'representativeness': 'column'}
    pairs, diagnostics = pair_observations([obs], model, max_time_gap_hours=1)
    assert diagnostics == [] and len(pairs) == 1 and pairs[0]['obs'] == pytest.approx(2)
    pairs, diagnostics = pair_observations([dict(obs, mass_basis=None)], model, max_time_gap_hours=1)
    assert pairs == [] and diagnostics[0]['reason'] == 'mass_basis_requires_explicit_N'


def test_same_dry_weight_units_match_but_do_not_convert_to_element_or_mass_units():
    from observation_matching import pair_observations
    obs = {'time': '2020-01-01 00:00:00', 'value': 2.5, 'depth_m': 1,
           'unit': 'gDW/m3', 'variable': 'diatoms_sDW', 'lake_id': 'L',
           'station_id': 'S', 'source_line': 1}
    model = {'times': ['2020-01-01 00:00:00'], 'values': [[2.5]], 'center_depth': [[1]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified',
             'unit': 'gDW/m3', 'variable': 'diatoms_sDW', 'representativeness': 'station'}
    pairs, diagnostics = pair_observations([obs], model, max_time_gap_hours=1)
    assert diagnostics == []
    assert len(pairs) == 1
    assert pairs[0]['sim'] == pytest.approx(2.5)
    assert pairs[0]['obs'] == pytest.approx(2.5)
    assert pairs[0]['unit_factor'] == pytest.approx(1.0)

    for incompatible in ('g/m3', 'gC/m3', 'gN/m3', 'gP/m3', 'mystery-unit'):
        bad_model = dict(model, unit=incompatible)
        pairs, diagnostics = pair_observations([obs], bad_model, max_time_gap_hours=1)
        assert pairs == []
        assert diagnostics[0]['reason'] in {'unknown_or_missing_unit', 'incompatible_or_unknown_unit'}
