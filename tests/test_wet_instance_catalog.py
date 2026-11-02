import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))

from wet_instance_catalog import (  # noqa: E402
    classify_model, get_model_schema, validate_existing_document, validate_names,
    validate_display_name, validate_native_field_names, validate_new_name,
)


def test_arbitrary_names_use_real_model_family_and_unique_across_disabled():
    assert classify_model('wet/phytoplankton') == ('ecology', 'phytoplankton')
    assert classify_model('wet/fish') == ('ecology', 'fish')
    assert classify_model('wet/abiotic_water') == ('water_quality', 'abiotic_water')
    instances = {
        'algae_a': {'model': 'wet/phytoplankton'},
        'algae_b': {'model': 'wet/phytoplankton'},
        'fish_grazer': {'model': 'wet/fish'},
        'fish_predator': {'model': 'wet/fish'},
    }
    validate_names(instances, {'archived_fish': {'model': 'wet/fish'}})
    with pytest.raises(ValueError, match='DUPLICATE_NAME'):
        validate_names(instances, {'algae_a': {'model': 'wet/phytoplankton'}})


def test_new_name_restrictions_and_legacy_read_compatibility():
    assert validate_new_name('algae_variant_2') == 'algae_variant_2'
    with pytest.raises(ValueError, match='INVALID_NAME'):
        validate_new_name('legacy.algae')
    legacy = {'a historically long legacy instance name': {'model': 'wet/fish'}}
    validate_existing_document(legacy)


def test_display_name_uses_native_yaml_scalar_contract_and_length_limit():
    assert validate_display_name('藻群甲') == '藻群甲'
    with pytest.raises(ValueError, match='INVALID_DISPLAY_NAME'):
        validate_display_name('first\nsecond')
    with pytest.raises(ValueError, match='INVALID_DISPLAY_NAME'):
        validate_display_name('x' * 121)


def test_schema_comes_from_registered_source_and_marks_conditional_ports():
    fish = get_model_schema('wet/fish')
    assert fish['states']['sD']['units'] == 'gDW/m3'
    assert fish['states']['sFRes']['condition'] == 'qStage > 0'
    assert fish['parameters']['qStage']['default'] == 0
    assert fish['parameters']['diagnostics']['default'] is False
    assert fish['parameters']['fResMax']['condition'] == 'qStage > 0'
    assert fish['parameters']['cDayReprFish']['condition'] == 'qStage in {1,3}'
    assert fish['diagnostics']['tDAssFiTot']['condition'] == 'diagnostics'
    assert fish['dynamic_families']['PLAN']['target_kind'] == 'model'
    assert fish['diagnostic_families']['PLAN']['condition'] == 'diagnostics and nPLAN >= N'
    assert fish['dynamic_families']['PISC']['required_states'] == ['sD', 'sN', 'sP', 'sC', 'fVul', 'pred_dummy']
    assert fish['diagnostics']['pred_dummy']['units'] == '-'
    assert fish['dynamic_state_families']['PISC']['consumer_units']['pred_dummyN'] == '-'
    assert fish['dynamic_state_families']['PISC']['unit_contract_status'] == 'compatible-native-registration'
    phyto = get_model_schema('wet/phytoplankton')
    assert phyto['states']['sCW']['units'] == 'gC/m3'
    assert phyto['diagnostics']['oSiW']['condition'] == 'lSi'


def test_flattened_native_field_collisions_are_rejected():
    with pytest.raises(ValueError, match='NATIVE_FIELD_COLLISION'):
        validate_native_field_names(['fish_sD', 'fish_sD'])


def test_manifest_distinguishes_release_master_and_local_hybrid():
    manifest = json.loads((ROOT / '3DWET' / 'app' / 'wet_upstream_manifest.json').read_text(encoding='utf-8'))
    assert manifest['upstream']['release_commit'] == '89e172cd6f113bff2ffe9e9680cbbeb7e0dd92a6'
    assert manifest['upstream']['master_commit'] == 'd2eee4419ab6762c092e07dc79316feff9efec5c'
    assert manifest['adoption']['status'] == 'local-getm-compatible-hybrid'
    assert manifest['probe']['status'] == 'not-run'
    incompatibility = manifest['known_registration_incompatibilities'][0]
    assert incompatibility['producer_registration']['units'] == '-'
    assert incompatibility['consumer_registration']['units'] == 'DW/m3'
