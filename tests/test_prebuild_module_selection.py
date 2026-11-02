"""A new bathymetry-only case must retain the other selected engines."""
from pathlib import Path
import json
import sys

import pytest
import netCDF4 as nc
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import server


@pytest.fixture
def module_client(tmp_path, monkeypatch):
    case = tmp_path / 'new-case'
    case.mkdir()
    selection = tmp_path / 'module-selection.json'
    monkeypatch.setattr(server, 'MODULE_SELECTION_FILE', selection)
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, 'active_case', 'New bathymetry-only case')
    monkeypatch.setattr(server, 'cached_getm_config', {})
    monkeypatch.setattr(server, 'cached_fabm_info', {})
    monkeypatch.setattr(server, '_ghg_exe_is_stale', lambda: False)
    return server.app.test_client(), case, selection


@pytest.mark.parametrize('draft,patch,expected', [
    ({'fish': True, 'ghg': False}, {'ghg': True}, {'fish': True, 'ghg': True}),
    ({'fish': False, 'ghg': True}, {'fish': True}, {'fish': True, 'ghg': True}),
])
def test_toggle_one_prebuild_engine_preserves_other_selected_engine(module_client, draft, patch, expected):
    client, case, selection = module_client
    selection.write_text(json.dumps({'hydro': True, 'eco': True, **draft}))
    before = client.get('/api/config/modules').get_json()['selection']
    assert {key: before[key] for key in draft} == draft
    assert not (case / 'fabm.yaml').exists()

    response = client.post('/api/config/modules', json=patch)
    assert response.status_code == 200
    assert response.get_json()['success']
    actual = response.get_json()['selection']
    assert {key: actual[key] for key in expected} == expected
    after = client.get('/api/config/modules').get_json()['selection']
    assert after == actual
    assert json.loads(selection.read_text()) == actual


def test_legacy_combined_eco_selection_keeps_combined_off_state(module_client):
    client, _, selection = module_client
    selection.write_text(json.dumps({'hydro': True, 'eco': False, 'fish': False, 'ghg': False}))
    result = client.get('/api/config/modules').get_json()
    assert result['selection']['eco'] is False
    assert result['selection']['water_quality'] is False
    assert any(engine['key'] == 'water_quality' for engine in result['engines'])


def test_domain_toggle_moves_only_selected_wet_family(module_client, monkeypatch):
    client, case, selection = module_client
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae:\n    model: wet/phytoplankton\n'
        '  nutrients:\n    model: wet/abiotic_water\n', encoding='utf-8')
    (case / 'getm.inp').write_text('placeholder', encoding='utf-8')
    current = {'getm_fabm': {'fabm': True}}
    monkeypatch.setattr(server, 'parse_getm_inp', lambda _path: json.loads(json.dumps(current)))
    monkeypatch.setattr(server, 'write_getm_inp', lambda _path, cfg: current.update(cfg))

    response = client.post('/api/config/modules', json={'eco': False})
    assert response.status_code == 200
    assert response.get_json()['success']
    active = yaml.safe_load((case / 'fabm.yaml').read_text())['instances']
    disabled = yaml.safe_load((case / 'fabm_disabled.yaml').read_text())['instances']
    assert set(active) == {'nutrients'}
    assert set(disabled) == {'algae'}
    assert current['getm_fabm']['fabm'] is True

    response = client.post('/api/config/modules', json={'eco': True})
    assert response.status_code == 200
    active = yaml.safe_load((case / 'fabm.yaml').read_text())['instances']
    assert set(active) == {'algae', 'nutrients'}


def test_built_case_still_uses_real_modules_instead_of_stale_draft(module_client):
    client, case, selection = module_client
    selection.write_text(json.dumps({'hydro': True, 'eco': True, 'fish': True, 'ghg': True}))
    (case / 'fabm.yaml').write_text('instances: {}\n')
    response = client.post('/api/config/modules', json={'eco': True})
    assert response.status_code == 200
    actual = response.get_json()['selection']
    assert actual['fish'] is False
    assert actual['ghg'] is False


def test_prebuild_ghg_toggle_keeps_fish_in_the_generated_model(module_client):
    client, case, selection = module_client
    selection.write_text(json.dumps({'hydro': True, 'eco': True, 'fish': True, 'ghg': False}))
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 3)
        ds.createDimension('y', 2)
        ds.createVariable('x', 'f8', ('x',))[:] = [500000, 500050, 500100]
        ds.createVariable('y', 'f8', ('y',))[:] = [3300000, 3300050]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[-10, 3, 5], [-10, 3, 5]]
        ds.createVariable('lonc', 'f8', ('y', 'x'))[:] = 117
        ds.createVariable('latc', 'f8', ('y', 'x'))[:] = 30
    toggled = client.post('/api/config/modules', json={'ghg': True}).get_json()
    response = client.post('/api/case/build', json={
        'preset': 'mesotrophic', 'start': '2020-DOY001 00:00:00',
        'stop': '2020-DOY001 00:20:00', 'timestep': 2, 'nlev': 6,
        'engines': toggled['selection'],
    })
    assert response.status_code == 200, response.get_json()
    assert response.get_json()['success']
    instances = yaml.safe_load((case / 'fabm.yaml').read_text(encoding='utf-8'))['instances']
    assert {'JuFish', 'AdFish', 'PiscFish', 'inorganic_carbon', 'methane'} <= instances.keys()


def test_disabling_fish_refreshes_existing_ghg_fish_coupling(module_client):
    client, case, _ = module_client
    instances = {
        'algae': {'model': 'wet/phytoplankton'},
        'zoo': {'model': 'wet/zooplankton'},
        'DOM': {'model': 'wet/om_pool'},
        'macrophytes': {'model': 'wet/macrophytes'},
        'benthos': {'model': 'wet/zoobenthos'},
        'abiotic_water': {'model': 'wet/abiotic_water'},
        'abiotic_sediment': {'model': 'wet/abiotic_sediment'},
        'bot_pel_interface': {'model': 'wet/bot_pel_interface'},
        'JuFish': {'model': 'wet/fish', 'parameters': {'diagnostics': True}},
        'AdFish': {'model': 'wet/fish', 'parameters': {'diagnostics': True}},
        'PiscFish': {'model': 'wet/fish', 'parameters': {'diagnostics': True}},
        'inorganic_carbon': {
            'model': 'wet/inorganic_carbon',
            'parameters': {'lFish': True, 'cPco2Atm': 525.0},
            'initialization': {'sDICW': 35.0},
            'coupling': {'C_respiration_fish': 'JuFish/tCRespFi'},
        },
        'methane': {'model': 'wet/methane', 'parameters': {'fMeth': 0.72}},
    }
    (case / 'fabm.yaml').write_text(yaml.safe_dump({'instances': instances}), encoding='utf-8')

    response = client.post('/api/config/modules', json={'fish': False})

    assert response.status_code == 200
    updated = yaml.safe_load((case / 'fabm.yaml').read_text(encoding='utf-8'))['instances']
    assert not {'JuFish', 'AdFish', 'PiscFish'} & updated.keys()
    assert updated['inorganic_carbon']['parameters']['lFish'] is False
    assert updated['inorganic_carbon']['parameters']['cPco2Atm'] == 525.0
    assert updated['inorganic_carbon']['initialization']['sDICW'] == 35.0
    assert updated['methane']['parameters']['fMeth'] == 0.72
    assert 'C_respiration_fish' not in updated['inorganic_carbon']['coupling']
