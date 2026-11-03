"""Weekly ext_wq.nc is selected only from the fabm/<instance> category."""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from flexout_output import (
    OUTPUT_LEVEL_DEBUG,
    OUTPUT_LEVEL_DEFAULT,
    WEEKLY_CHLOROPHYLL,
    WEEKLY_INSTANCES,
    case_output_yaml,
    fields_for_source,
    weekly_variable_names,
)

ROOT = Path(__file__).resolve().parents[1]
DIANCHI_YAMLS = (
    ROOT / '3DWET/case/Lake Dianchi/output.yaml',
    ROOT / 'GETM-FABM-WET/3DWET/case/Lake Dianchi/output.yaml',
)


def _sources(text):
    groups = yaml.safe_load(text)
    found = []
    for name, block in groups.items():
        if not isinstance(block, dict):
            continue
        for item in block.get('variables') or []:
            found.append((name, item['source'], int(item.get('output_level', OUTPUT_LEVEL_DEFAULT))))
    return found


def test_builder_lists_state_variables_and_not_diagnostic_wildcards():
    text = case_output_yaml(86400)
    sources = _sources(text)
    weekly = [item for item in sources if item[0] == 'ext_wq']
    assert [name for _file, name, _level in weekly] == list(weekly_variable_names())
    assert all(not source.startswith('fabm/') for _file, source, _level in weekly)
    assert '\nsource: *' not in text
    assert ('output', 'abiotic_water_sO2W', OUTPUT_LEVEL_DEFAULT) in sources
    assert 'source: abiotic_water/*' not in text
    assert 'abiotic_water/sO2W' not in text
    assert 'cyanobacteria_oChla' in text
    assert 'wet_chla_calculator_result' in text


def test_registered_state_is_kept_and_the_old_category_is_empty():
    fields = [
        ('abiotic_water_sO2W', 'fabm/abiotic_water', OUTPUT_LEVEL_DEFAULT),
        ('abiotic_water_sNH4W', 'fabm/abiotic_water', OUTPUT_LEVEL_DEFAULT),
        ('abiotic_water_BTdummy', 'fabm/abiotic_water', OUTPUT_LEVEL_DEBUG),
        ('cyanobacteria_sDW', 'fabm/cyanobacteria', OUTPUT_LEVEL_DEFAULT),
    ]
    assert fields_for_source(fields, 'abiotic_water/*') == []
    assert fields_for_source(fields, 'fabm/abiotic_water/*') == [
        'abiotic_water_sO2W', 'abiotic_water_sNH4W']
    assert fields_for_source(fields, 'fabm/cyanobacteria/*') == ['cyanobacteria_sDW']


def test_dianchi_cases_would_create_ext_wq():
    fabm = yaml.safe_load((ROOT / '3DWET/case/Lake Dianchi/fabm.yaml').read_text(encoding='utf-8'))
    instances = fabm['instances']
    expected_states = []
    for instance in WEEKLY_INSTANCES:
        keys = tuple((instances[instance].get('initialization') or {}).keys())
        expected_states.extend(f'{instance}_{key}' for key in keys)
    assert expected_states == [name for name in weekly_variable_names() if name not in WEEKLY_CHLOROPHYLL]
    for path in DIANCHI_YAMLS:
        text = path.read_text(encoding='utf-8')
        sources = _sources(text)
        weekly = [item for item in sources if item[0] == 'ext_wq']
        assert [name for _file, name, _level in weekly] == list(weekly_variable_names()), path
        assert all(not source.startswith('fabm/') for _file, source, _level in weekly)
        selected = []
        for _file, source, level in weekly:
            fields = [(source, f'fabm/{source.split("_", 1)[0]}', OUTPUT_LEVEL_DEFAULT)]
            fields.append((f'{source}_dummy', 'fabm/abiotic_water', OUTPUT_LEVEL_DEBUG))
            selected.extend(fields_for_source(fields, source, level))
        assert 'abiotic_water_sO2W' in selected
        assert 'abiotic_water_sNH4W' in selected
        assert 'abiotic_water_sNO3W' in selected
        assert 'abiotic_water_sPO4W' in selected
        assert 'cyanobacteria_sDW' in selected
        assert 'cyanobacteria_oChla' in selected
        assert 'wet_chla_calculator_result' in selected
        assert not any(name.endswith('_dummy') for name in selected)
