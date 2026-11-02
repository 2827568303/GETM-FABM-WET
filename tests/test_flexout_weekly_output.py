"""Weekly ext_wq.nc is selected only from the fabm/<instance> category."""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from flexout_output import (
    OUTPUT_LEVEL_DEBUG,
    OUTPUT_LEVEL_DEFAULT,
    WEEKLY_INSTANCES,
    case_output_yaml,
    fields_for_source,
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


def test_builder_uses_fabm_categories_at_the_default_level():
    text = case_output_yaml(86400)
    sources = _sources(text)
    weekly = [item for item in sources if item[0] == 'ext_wq']
    assert [name for _file, name, _level in weekly] == [f'fabm/{name}/*' for name in WEEKLY_INSTANCES]
    assert {level for _file, _name, level in weekly} == {OUTPUT_LEVEL_DEFAULT}
    assert ('output', 'abiotic_water_sO2W', OUTPUT_LEVEL_DEFAULT) in sources
    assert 'source: abiotic_water/*' not in text
    assert 'abiotic_water/sO2W' not in text


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
    for path in DIANCHI_YAMLS:
        text = path.read_text(encoding='utf-8')
        sources = _sources(text)
        weekly = [item for item in sources if item[0] == 'ext_wq']
        assert weekly, path
        selected = []
        for _file, source, level in weekly:
            instance = source.removeprefix('fabm/').removesuffix('/*')
            assert instance in instances, source
            fields = [
                (f'{instance}_{name}', f'fabm/{instance}', OUTPUT_LEVEL_DEFAULT)
                for name in (instances[instance].get('initialization') or {})
            ]
            # output_none diagnostics stay at the debug level and are not required.
            fields.append((f'{instance}_dummy', f'fabm/{instance}', OUTPUT_LEVEL_DEBUG))
            selected.extend(fields_for_source(fields, source, level))
        assert 'abiotic_water_sO2W' in selected
        assert 'abiotic_water_sNH4W' in selected
        assert any(name.startswith('cyanobacteria_') for name in selected)
        assert not any(name.endswith('_dummy') for name in selected)
