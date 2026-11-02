from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_native_basis_is_source_backed_and_requires_attested_producer():
    from native_variable_metadata import describe_native_variable

    oxygen = describe_native_variable('abiotic_water_sO2W', 'g/m3', producer='wet_getm_native')
    assert oxygen['mass_basis'] == 'O2'
    assert oxygen['unit'] == 'gO2/m3'
    assert oxygen['provenance']['source_file'] == '3DWET/src/wet/src/abiotic_water.F90'
    assert describe_native_variable('abiotic_water_sO2W', 'g/m3', producer=None) is None
    assert describe_native_variable('abiotic_water_sO2W', 'mg/L', producer='wet_getm_native') is None


def test_pairing_uses_explicit_observation_and_model_basis_not_variable_name():
    from observation_matching import pair_observations

    obs = {'time': '2020-01-01', 'value': 1, 'depth_m': 1, 'unit': 'mg/L',
           'mass_basis': 'N', 'variable': 'abiotic_water_sNH4W', 'lake_id': 'L', 'station_id': 'S'}
    model = {'times': ['2020-01-01'], 'values': [[1]], 'center_depth': [[1]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified',
             'unit': 'gN/m3', 'mass_basis': 'N', 'variable': 'abiotic_water_sNH4W',
             'representativeness': 'station'}
    pairs, diagnostics = pair_observations([obs], model, max_time_gap_hours=1)
    assert diagnostics == []
    assert len(pairs) == 1

    bad_model = dict(model, mass_basis='P')
    pairs, diagnostics = pair_observations([obs], bad_model, max_time_gap_hours=1)
    assert pairs == []
    assert diagnostics[0]['reason'] == 'mass_basis_conflict'


def test_unannotated_external_model_does_not_get_basis_from_observation_name():
    from observation_matching import pair_observations

    obs = {'time': '2020-01-01', 'value': 1, 'depth_m': 1, 'unit': 'mg/L',
           'mass_basis': 'N', 'variable': 'abiotic_water_sNH4W', 'lake_id': 'L', 'station_id': 'S'}
    model = {'times': ['2020-01-01'], 'values': [[1]], 'center_depth': [[1]],
             'lake_id': 'L', 'station_id': 'S', 'spatial_mapping': 'verified',
             'unit': 'g/m3', 'variable': 'abiotic_water_sNH4W', 'representativeness': 'station'}
    pairs, diagnostics = pair_observations([obs], model, max_time_gap_hours=1)
    assert pairs == []
    assert diagnostics[0]['reason'] == 'mass_basis_metadata_missing'

