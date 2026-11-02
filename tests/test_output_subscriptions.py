import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
from output_subscriptions import resolve_sources, preset_sources, model_sources


@pytest.fixture
def case(tmp_path):
    instances = {
        'abiotic_water': {'model': 'wet/abiotic_water', 'initialization': {'sO2W': 8}},
        'diatoms': {'model': 'wet/phytoplankton', 'initialization': {'sDW': 1}},
        'carbon': {'model': 'wet/inorganic_carbon'},
        'methane': {'model': 'wet/methane'},
    }
    (tmp_path / 'fabm.yaml').write_text(yaml.safe_dump({'instances': instances}), encoding='utf-8')
    (tmp_path / 'fabm_disabled.yaml').write_text('instances:\n  unused:\n    model: wet/phytoplankton\n', encoding='utf-8')
    return tmp_path


@pytest.fixture
def context():
    return {'docs': {
        'wet/abiotic_water': {'variables': {k: {} for k in ('sO2W','sNO3W','sNH4W','sPO4W','sDIMW')}},
        'wet/phytoplankton': {'variables': {'sDW': {}, 'sPW': {}}},
        'wet/inorganic_carbon': {'variables': {'sDICW': {}, 'sAlkW': {}}},
        'wet/methane': {'variables': {'sCH4W': {}}},
    }, 'available_sources': ['temp','z','D','hn','abiotic_water_sO2W','diatoms_sDW']}


def test_known_model_selectors_expand_to_flat_fields(case, context):
    result = resolve_sources(case, ['temp','abiotic_water/*','diatoms/*','abiotic_water/sO2W'], context)
    assert 'abiotic_water_sO2W' in result and 'abiotic_water_sDIMW' in result
    assert 'diatoms_sDW' in result and len(result) == len(set(result))
    assert all('/' not in field for field in result)


def test_standard_contains_target_states_for_active_model_types(case, context):
    result = preset_sources(case, 'standard', context)
    assert result[:4] == ['temp','z','D','hn']
    assert set(result[4:]) == {'abiotic_water_sO2W','abiotic_water_sNO3W','abiotic_water_sNH4W','abiotic_water_sPO4W','diatoms_sDW','carbon_sDICW','methane_sCH4W'}
    assert 'salt' not in result and 'carbon_sAlkW' not in result
    assert preset_sources(case, 'all', context) == ['*']


def test_hydro_only_adds_observed_registered_salt(case, context):
    assert preset_sources(case, 'hydro', context) == ['temp','z','D','hn']
    context['available_sources'].append('salt')
    assert 'salt' in preset_sources(case, 'minimal', context)


def test_unknown_explicit_field_and_category_fail_helpfully(case, context):
    with pytest.raises(ValueError, match='abiotic_water_sO2W'):
        resolve_sources(case, ['abiotic_water_sO2X'], context)
    with pytest.raises(ValueError, match='unknown_model'):
        resolve_sources(case, ['unknown_model/*'], context)
    with pytest.raises(ValueError, match='unused'):
        resolve_sources(case, ['unused/*'], context)


def test_inventory_adds_model_diagnostics_without_renaming(case, context):
    context['available_sources'].append('abiotic_water_nitrification')
    result=resolve_sources(case,['abiotic_water/*'],context)
    assert 'abiotic_water_nitrification' in result
    assert resolve_sources(case,['abiotic_water_nitrification'],context)==['abiotic_water_nitrification']


def test_real_slash_inventory_is_respected_only_when_registered(case, context):
    context['available_sources'].append('registered_category/foo')
    assert resolve_sources(case,['registered_category/*'],context)==['registered_category/foo']
    assert resolve_sources(case,['registered_category/foo'],context)==['registered_category/foo']


def test_model_info_exposes_expanded_checkbox_selection(case, context):
    models=model_sources(case,context,['diatoms/*'])
    by_name={m['name']:m for m in models}
    assert by_name['diatoms']['selected'] is True
    assert by_name['abiotic_water']['selected'] is False
    assert 'unused' not in by_name
    assert all(not field.endswith('/*') for m in models for field in m['sources'])


def test_instance_renaming_and_missing_docs_use_actual_initialization(tmp_path):
    (tmp_path/'fabm.yaml').write_text('instances:\n  custom_instance:\n    model: external/model\n    initialization:\n      tracer: 1\n',encoding='utf-8')
    assert resolve_sources(tmp_path,['custom_instance/*'],{'docs':{},'available_sources':[]})==['custom_instance_tracer']


def test_invalid_and_unsafe_inputs_are_not_silently_discarded(case,context):
    for sources in ([],[''],['temp',None],['u'],['v'],['elev'],['*','missing']):
        with pytest.raises(ValueError): resolve_sources(case,sources,context)
    with pytest.raises(ValueError,match='preset'): preset_sources(case,'invented',context)


def test_running_case_never_opens_native_output(case,context):
    context.pop('available_sources')
    context['_case_in_use']=lambda path: True
    context['find_output_files']=lambda path: (_ for _ in ()).throw(AssertionError('must not inspect active output'))
    assert 'abiotic_water_sO2W' in preset_sources(case,'standard',context)
    context.pop('_case_in_use')
    context['run_status']='running'
    assert 'abiotic_water_sO2W' in preset_sources(case,'standard',context)

def test_full_active_module_selection_excludes_fields_not_observed_as_registered(tmp_path):
    active = {
        'abiotic_water': {'model': 'wet/abiotic_water'},
        'cyanobacteria': {'model': 'wet/phytoplankton'},
        'JuFish': {'model': 'wet/fish'},
        'AdFish': {'model': 'wet/fish'},
        'PiscFish': {'model': 'wet/fish'},
    }
    (tmp_path / 'fabm.yaml').write_text(yaml.safe_dump({'instances': active}), encoding='utf-8')
    docs = {
        'wet/abiotic_water': {'variables': {'sO2W': {}, 'sNO3W': {}}},
        'wet/phytoplankton': {'variables': {'sDW': {}, 'sPW': {}}},
        'wet/fish': {'variables': {'sD': {}, 'sN': {}, 'sP': {}, 'sC': {}, 'sDSiz': {}}},
    }
    registered = ['temp', 'z', 'D', 'hn', 'abiotic_water_sO2W',
                  'cyanobacteria_sDW', 'JuFish_sD', 'AdFish_sD', 'PiscFish_sD']
    context = {'docs': docs, 'available_sources': registered, 'strict_registered_sources': True}

    selected = resolve_sources(tmp_path, [
        'abiotic_water/*', 'cyanobacteria/*', 'JuFish/*', 'AdFish/*', 'PiscFish/*',
    ], context)

    assert 'PiscFish_sDSiz' not in selected
    assert set(selected) == set(registered[4:])
    persisted_output = '\n'.join(f'      - source: {source}' for source in selected)
    assert 'PiscFish_sDSiz' not in persisted_output
    with pytest.raises(ValueError, match='PiscFish_sDSiz'):
        resolve_sources(tmp_path, ['PiscFish_sDSiz'], context)

