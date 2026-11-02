"""Semantic metadata and reference values must preserve chemical comparability."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))
import variable_reference as vr


@pytest.fixture
def case(tmp_path):
    (tmp_path / 'fabm.yaml').write_text('''instances:
  abiotic_water:
    model: wet/abiotic_water
    initialization:
      sO2W: 9
      sPO4W: 0.03
  abiotic_sediment:
    model: wet/abiotic_sediment
    initialization:
      sPO4S: 0.2
  greens:
    model: wet/phytoplankton
    initialization:
      sDW: 2
''', encoding='utf-8')
    (tmp_path / 'getm.inp').write_text('&temp\n temp_method=1, temp_const=12.0\n/\n&hotstart\n elev_const=0.0\n/\n', encoding='utf-8')
    return tmp_path


def test_exact_dissolved_oxygen_and_unit_conversion(case):
    ref = vr.describe_variable('abiotic_water_sO2W', 'g/m3', '', case)['reference']
    assert ref['kind'] == 'standard' and ref['lower'] == 5
    assert '3838' in ref['source'] and ref['source_url'].startswith('https://www.mee.gov.cn/')
    assert vr.describe_variable('abiotic_water_sO2W', 'mg/m3', '', case)['reference']['lower'] == 5000
    for units in ('mmol/m3', 'gN/m3', 'g/m2', 'g/m3/s', ''):
        assert vr.describe_variable('abiotic_water_sO2W', units, '', case)['reference']['kind'] == 'unset'


def test_phosphate_and_sediment_are_never_total_phosphorus_standards(case):
    for name, units, expected in [('abiotic_water_sPO4W', 'g/m3', .03), ('abiotic_sediment_sPO4S', 'g/m2', .2)]:
        result = vr.describe_variable(name, units, '', case)
        assert result['reference']['kind'] == 'initial'
        assert result['reference']['value'] == expected
        assert '初始' in result['reference']['label']
        assert '正常' not in result['reference']['label']
    assert vr.describe_variable('abiotic_water_sNH4W', 'g/m3', 'ammonium', case)['reference']['kind'] == 'unset'


def test_true_water_total_phosphorus_and_ph_have_narrow_standards(case):
    assert vr.describe_variable('total_phosphorus', 'mgP/L', 'total phosphorus in water', case)['reference']['upper'] == .05
    assert vr.describe_variable('sediment_total_phosphorus', 'mgP/L', 'total phosphorus in sediment', case)['reference']['kind'] == 'unset'
    assert vr.describe_variable('total_phosphorus', 'mmol/m3', 'total phosphorus in water', case)['reference']['kind'] == 'unset'
    ph = vr.describe_variable('inorganic_carbon_pH', '-', '', case)['reference']
    assert ph['kind'] == 'standard' and ph['lower'] == 6 and ph['upper'] == 9


def test_state_compartment_and_signed_flux_have_distinct_chinese_meaning(case):
    state = vr.describe_variable('greens_sDW', 'gDW/m3', '', case)
    assert '绿藻' in state['zh_name'] and '干重' in state['meaning'] and '水体' in state['meaning']
    assert state['reference']['value'] == 2
    flux = vr.describe_variable('sediment_exchange_tNDifNO3', 'g/m2/s', 'rate NO3 diffusion', case)
    assert '扩散' in flux['meaning'] and '硝' in flux['meaning']
    assert flux['reference']['kind'] == 'unset'
    assert '符号' in flux['meaning'] and '零' in flux['reference']['note']


def test_overrides_are_finite_ordered_and_units_matched(case):
    saved = vr.save_reference(case, 'abiotic_water_sO2W', {'lower': 7, 'upper': 10, 'unit': 'g/m3', 'label': '本湖监测目标'})
    assert saved['kind'] == 'custom'
    assert vr.describe_variable('abiotic_water_sO2W', 'g/m3', '', case)['reference']['lower'] == 7
    assert vr.describe_variable('abiotic_water_sO2W', 'mmol/m3', '', case)['reference']['kind'] == 'unset'
    for data in ({'value': float('nan'), 'unit': 'g/m3'}, {'lower': 3, 'upper': 2, 'unit': 'g/m3'}, {'value': 1, 'unit': 'gN/m3'}, {'unit': 'g/m3'}):
        with pytest.raises(ValueError):
            vr.save_reference(case, 'abiotic_water_sO2W', data)


def test_getm_initial_and_unknown_definition_are_honest(case):
    assert vr.describe_variable('temp', 'Celsius', 'temperature', case)['reference']['value'] == 12
    result = vr.describe_variable('unmapped_q777', 'mol/m2', 'opaque external diagnostic', case)
    assert '未收录' in result['zh_name']
    assert 'opaque external diagnostic' in result['meaning']
    assert result['reference']['kind'] == 'unset'


def test_inventory_annotations_preserve_input_and_have_chinese_fields():
    evidence = ROOT / 'docs/audit/2026-10-11-evidence/source-final-defaults-all5-20261010/verification.json'
    data = json.loads(evidence.read_text(encoding='utf-8'))
    for result in data['results']:
        for kind in ('2d', '3d'):
            items = result['variables'][kind]
            annotated = vr.annotate_variables(items, ROOT / '3DWET/case' / result['case'])
            assert len(annotated) == len(items)
            for original, item in zip(items, annotated):
                assert all(item[key] == value for key, value in original.items())
                assert any('\u4e00' <= c <= '\u9fff' for c in item['zh_name'])
                assert item['meaning'] and item['category'] and item['reference']['kind']
                assert 'reference' not in original


def test_reset_removes_custom_reference_and_restores_standard(case):
    vr.save_reference(case, 'abiotic_water_sO2W', {'value': 8, 'units': 'g/m3'})
    vr.save_reference(case, 'abiotic_water_sO2W', {'reset': True})
    assert vr.describe_variable('abiotic_water_sO2W', 'g/m3', '', case)['reference']['kind'] == 'standard'


def test_inventory_all_existing_variables_have_resolved_chinese_semantics():
    evidence = ROOT / 'docs/audit/2026-10-11-evidence/source-final-defaults-all5-20261010/verification.json'
    data = json.loads(evidence.read_text(encoding='utf-8'))
    unknown = []
    for result in data['results']:
        for kind in ('2d', '3d'):
            for item in vr.annotate_variables(result['variables'][kind], ROOT / '3DWET/case' / result['case']):
                if '未收录' in item['zh_name']:
                    unknown.append(item['name'])
    assert not unknown, sorted(set(unknown))


def test_all_source_registered_quantities_have_a_specific_semantic_description():
    registry = json.loads((ROOT / '3DWET/app/variable_registry.json').read_text(encoding='utf-8'))
    missing = [(model, name) for model, items in registry.items() for name, record in items.items()
               if not vr._semantic(name, record, model.split('/')[-1], record['units'])]
    assert not missing


def test_exact_initial_json_and_untrusted_preset_are_distinguished(case):
    (case / 'initial_conditions.json').write_text(json.dumps({'abiotic_water_sNH4W': .7, 'trophic': 'eutrophic', 'greens': 9}), encoding='utf-8')
    assert vr.describe_variable('abiotic_water_sNH4W', 'g/m3', '', case)['reference']['value'] == .7
    assert vr.describe_variable('greens_sPW', 'g/m3', '', case)['reference']['kind'] == 'unset'


def test_earlier_source_inventory_hydrodynamic_diagnostics_are_named():
    for name, phrase in [('hcc', '静水'), ('tke', '湍动能'), ('num', '黏性'), ('nuh', '扩散'), ('diss', '耗散')]:
        result = vr.describe_variable(name, '', name)
        assert phrase in result['meaning']
        assert result['reference']['kind'] == 'unset'


def test_reference_can_use_trusted_actual_output_units(case):
    saved = vr.save_reference(case, 'abiotic_water_sO2W', {'units': 'mgO2/L', 'value': 7}, expected_units='mgO2/L')
    assert saved['unit'] == 'mgO2/L' and saved['value'] == 7
    assert vr.describe_variable('abiotic_water_sO2W', 'mgO2/L', '', case)['reference']['kind'] == 'custom'
    with pytest.raises(ValueError):
        vr.save_reference(case, 'abiotic_water_sO2W', {'units': 'g/m3', 'value': 7}, expected_units='mgO2/L')
    saved = vr.save_reference(case, 'external_dimensionless', {'units': '', 'value': 1}, expected_units='')
    assert saved['unit'] == ''
    with pytest.raises(ValueError):
        vr.save_reference(case, 'external_dimensionless', {'units': 'm', 'value': 1}, expected_units='')


def test_english_variable_metadata_is_independent_and_source_backed(case):
    state = vr.describe_variable('greens_sDW', 'gDW/m3', 'green phytoplankton DW', case)
    assert state['en_name'] and 'DW' in state['en_name']
    assert 'water column' in state['meaning_en']
    assert 'gDW/m3' in state['meaning_en']
    assert 'temperature' in vr.describe_variable('temp', 'Celsius', '', case)['en_name'].lower()
    flux = vr.describe_variable('sediment_exchange_tNDifNO3', 'g/m2/s', '', case)
    assert 'diffusion' in flux['meaning_en'] and 'sign' in flux['meaning_en']
    assert 'sediment' in flux['meaning_en']
    unknown = vr.describe_variable('q_external', 'mol/m2', 'external obscure quantity', case)
    assert unknown['en_name'] == 'external obscure quantity'
    assert 'unknown' in unknown['meaning_en'].lower()


def test_all_reference_kinds_provide_english_only_metadata(case):
    variables = [('abiotic_water_sO2W', 'g/m3'), ('greens_sDW', 'gDW/m3'), ('sediment_exchange_tNDifNO3', 'g/m2/s')]
    outputs = [vr.describe_variable(name, unit, '', case) for name, unit in variables]
    vr.save_reference(case, 'abiotic_water_sO2W', {'unit': 'g/m3', 'value': 7, 'label': '本湖目标', 'source': '本湖监测', 'note': '自定义比较'})
    outputs.append(vr.describe_variable('abiotic_water_sO2W', 'g/m3', '', case))
    assert {output['reference']['kind'] for output in outputs} == {'standard', 'initial', 'unset', 'custom'}
    for output in outputs:
        for field in ('en_name', 'meaning_en'):
            assert output[field] and not any('\u4e00' <= char <= '\u9fff' for char in output[field])
        for field in ('label_en', 'source_en', 'note_en'):
            assert output['reference'][field] and not any('\u4e00' <= char <= '\u9fff' for char in output['reference'][field])
