import sys
import threading
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))

# Start from the WET module validation fixture, then add only the integration
# structures exercised by these transaction tests. This stays independent of
# mutable lake cases and changes are written only below pytest's tmp_path.
WET_VALIDATION_FABM = (Path(__file__).resolve().parents[1] / '3DWET' / 'src' /
                       'wet' / 'testcases' / 'fabm-wet.yaml')


def transaction_fabm_document():
    from wet_instance_catalog import get_model_schema

    document = yaml.safe_load(WET_VALIDATION_FABM.read_bytes())
    instances = document['instances']
    phyto_states = get_model_schema('wet/phytoplankton')['states']
    instances['cyanobacteria']['initialization'] = {name: 0.1 for name in phyto_states}
    # Complete the currently registered sediment particulate-volume ports with
    # valid states from the validation fixture's dissolved organic matter pool.
    instances['cyanobacteria']['coupling'].update({
        'DOM_C_pool_sediment_PV': 'DOM/sCS_PV',
        'DOM_DW_pool_sediment_PV': 'DOM/sDS_PV',
        'DOM_N_pool_sediment_PV': 'DOM/sNS_PV',
        'DOM_P_pool_sediment_PV': 'DOM/sPS_PV',
    })
    instances['inorganic_carbon'] = {
        'model': 'wet/inorganic_carbon',
        'parameters': {'nPHYT': 3},
        'coupling': {
            **{f'CO2_uptake_water_{i}': f'{name}/wCO2UptW'
               for i, name in enumerate(('cyanobacteria', 'diatoms', 'greens'), 1)},
            **{f'CO2_respiration_water_{i}': f'{name}/wCO2RespW'
               for i, name in enumerate(('cyanobacteria', 'diatoms', 'greens'), 1)},
        },
    }
    return document


def transaction_fabm_bytes():
    return yaml.safe_dump(transaction_fabm_document(), sort_keys=False).encode('utf-8')


def transaction_client(path):
    from lake_points_api import register_lake_points_routes
    ctx = SimpleNamespace(active_case_path=path, _NC_LOCK=threading.RLock(), _case_in_use=lambda p: False)
    app = Flask(__name__)
    register_lake_points_routes(app, ctx)
    return app.test_client(), ctx


def test_fish_dynamic_dependency_unit_is_not_parsed_as_a_static_port():
    from wet_instance_catalog import get_model_schema, required_registered_dependencies

    schema = get_model_schema('wet/fish')
    assert 'DW/m3' not in schema['state_dependencies']
    assert 'DW/m3' not in required_registered_dependencies('wet/fish')


@pytest.fixture
def case(tmp_path):
    (tmp_path / 'fabm.yaml').write_bytes(
        b'\xef\xbb\xbf# preserve this comment\r\ninstances:\r\n  algae_a:\r\n    model: wet/phytoplankton\r\n'
        b'    long_name: Algae A\r\n    parameters:\r\n      k: 1.0 # keep this note\r\n')
    (tmp_path / 'initial_conditions.json').write_bytes(b'{"water_quality":{"old.x":1}}\n')
    (tmp_path / 'output.yaml').write_bytes(b'output: {variables: []}\n')
    return tmp_path


def test_replace_failure_restores_every_original_byte(case, monkeypatch):
    import case_model_transaction as tx

    before = {p.name: p.read_bytes() for p in (case / 'fabm.yaml', case / 'initial_conditions.json', case / 'output.yaml')}
    real_replace = tx.os.replace
    count = 0

    def fail_third(src, dst):
        nonlocal count
        count += 1
        if count == 4:  # journal, first file, second file, then injected third-file failure
            raise OSError('injected third replacement failure')
        return real_replace(src, dst)

    monkeypatch.setattr(tx.os, 'replace', fail_third)
    with pytest.raises(OSError, match='injected'):
        tx.commit_files(case, {'fabm.yaml': b'changed', 'initial_conditions.json': b'changed', 'output.yaml': b'changed'})
    assert {name: (case / name).read_bytes() for name in before} == before


def test_pending_journal_is_recovered_before_read(case):
    import case_model_transaction as tx

    original = (case / 'fabm.yaml').read_bytes()
    journal = case / '.studio-config' / 'transactions' / 'pending.json'
    journal.parent.mkdir(parents=True)
    backup = case / 'backups' / 'pending'
    backup.mkdir(parents=True)
    (case / 'fabm.yaml').write_bytes(b'half written')
    (backup / 'fabm.yaml').write_bytes(original)
    journal.write_text('{"state":"prepared","backup":"backups/pending","files":["fabm.yaml"],"exists":{"fabm.yaml":true}}', encoding='utf-8')
    tx.recover_pending(case)
    assert (case / 'fabm.yaml').read_bytes() == original
    assert not journal.exists()


def test_revision_stale_case_and_running_are_rejected_without_mutation(case):
    from case_model_transaction import case_revision

    client, ctx = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    before = (case / 'fabm.yaml').read_bytes()
    (case / 'initial_conditions.json').write_text('{"trophic":"custom"}', encoding='utf-8')
    stale = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'apply',
        'preview_hash': 'stale', 'operations': [{'op': 'update', 'name': 'algae_a', 'long_name': 'changed'}]})
    assert stale.status_code == 409
    assert (case / 'fabm.yaml').read_bytes() == before
    state = client.get('/api/model/instances').get_json()
    ctx._case_in_use = lambda p: True
    active = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'apply',
        'preview_hash': 'anything', 'operations': []})
    assert active.status_code == 409
    assert case_revision(case) == state['revision']


def test_preview_and_apply_preserve_unrelated_yaml_bytes(case):
    client, _ = transaction_client(case)
    original = (case / 'fabm.yaml').read_bytes()
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'update', 'name': 'algae_a', 'parameters': {'k': 2.5}, 'long_name': 'Algae A2'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    assert (case / 'fabm.yaml').read_bytes() == original
    applied = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    current = (case / 'fabm.yaml').read_bytes()
    assert current.startswith(b'\xef\xbb\xbf')
    assert b'# preserve this comment\r\n' in current
    assert b'# keep this note' in current
    assert (case / 'initial_conditions.json').read_bytes() == b'{"water_quality":{"old.x":1}}\n'
    assert yaml.safe_load(current)['instances']['algae_a']['parameters']['k'] == 2.5


def test_add_instance_is_previewed_and_committed_as_real_yaml(case):
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes() + b'\n# preserve this comment\r\n')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    template = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']['cyanobacteria']
    operations = [{'op': 'add', 'name': 'algae_b', 'model': 'wet/phytoplankton', 'long_name': '藻群乙'}]
    request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': operations}
    preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'apply',
        'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    document = yaml.safe_load((case / 'fabm.yaml').read_bytes())
    assert document['instances']['algae_b']['model'] == 'wet/phytoplankton'
    assert document['instances']['algae_b']['long_name'] == '藻群乙'
    for section in ('parameters', 'initialization', 'coupling'):
        assert document['instances']['algae_b'][section] == template[section]
    assert b'# preserve this comment\r\n' in (case / 'fabm.yaml').read_bytes()


@pytest.mark.parametrize(('family', 'template', 'name'), [
    ('phytoplankton', 'cyanobacteria', 'green_algae_probe'),
    ('zooplankton', 'cladocerans', 'zoo_probe'),
    ('fish', 'JuFish', 'fish_probe'),
])
def test_add_ecology_instance_copies_validated_family_configuration(tmp_path, family, template, name):
    case = tmp_path / family
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    client, _ = transaction_client(case)
    before = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances'][template]
    state = client.get('/api/model/instances').get_json()
    operation = {'op': 'add', 'name': name, 'model': f'wet/{family}'}
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [operation]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    after = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances'][name]
    assert after['model'] == f'wet/{family}'
    assert after['long_name'] == name
    for section in ('parameters', 'initialization', 'coupling'):
        assert after[section] == before[section], f'{family} add must retain template {section}'
    if family == 'phytoplankton':
        assert after['coupling']['PO4_pool_water'] == 'abiotic_water/sPO4W'
    elif family == 'zooplankton':
        assert after['coupling']['prey_model1'] == 'cyanobacteria'
    else:
        assert after['coupling']['PLANprey1'] == 'copepods'


def test_add_ecology_instance_without_family_template_is_rejected_before_apply(case):
    (case / 'fabm.yaml').write_text('instances:\n  water:\n    model: wet/abiotic_water\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'add', 'name': 'new_algae', 'model': 'wet/phytoplankton'}]})
    assert response.status_code == 400
    assert 'NO_COMPATIBLE_TEMPLATE' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


def test_add_ecology_instance_rejects_template_missing_registered_dependency(tmp_path):
    case = tmp_path / 'incomplete'
    case.mkdir()
    document = transaction_fabm_document()
    del document['instances']['cyanobacteria']['coupling']['PO4_pool_water']
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'add', 'name': 'new_algae', 'model': 'wet/phytoplankton'}]})
    assert response.status_code == 400
    assert 'PO4_pool_water' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


def test_clone_and_rename_are_schema_backed_and_keep_external_yaml_bytes(case):
    (case / 'fabm.yaml').write_bytes(
        b'instances:\r\n  algae_a:\r\n    model: wet/abiotic_water\r\n'
        b'    long_name: Algae A\r\n    initialization:\r\n      sPO4W: 0.1\r\n# keep this unrelated comment\r\n')
    client, _ = transaction_client(case)
    original = (case / 'fabm.yaml').read_bytes()
    state = client.get('/api/model/instances').get_json()
    operations = [
        {'op': 'clone', 'source': 'algae_a', 'name': 'algae_b', 'long_name': '藻群乙'},
        {'op': 'rename', 'name': 'algae_b', 'new_name': 'algae_green'},
    ]
    request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': operations}
    preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    assert (case / 'fabm.yaml').read_bytes() == original
    repeated_preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert repeated_preview.status_code == 200, repeated_preview.get_json()
    assert repeated_preview.get_json()['preview_hash'] == preview.get_json()['preview_hash']
    applied = client.post('/api/model/instances/transaction', json={
        **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    document = yaml.safe_load((case / 'fabm.yaml').read_bytes())
    assert document['instances']['algae_green']['model'] == 'wet/abiotic_water'
    assert document['instances']['algae_green']['long_name'] == '藻群乙'
    assert document['instances']['algae_green']['initialization']['sPO4W'] == 0.1
    assert 'algae_b' not in document['instances']
    assert b'# keep this unrelated comment\r\n' in (case / 'fabm.yaml').read_bytes()


def test_clone_rejects_coupling_to_unregistered_target_state_before_apply(tmp_path):
    case = tmp_path / 'invalid_state_target'
    case.mkdir()
    document = transaction_fabm_document()
    document['instances']['cyanobacteria']['coupling']['PO4_pool_water'] = 'abiotic_water/PO4_pool_water'
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cyanobacteria', 'name': 'green_algae_probe'}]})
    assert response.status_code == 400
    assert 'abiotic_water/PO4_pool_water' in response.get_json()['error']
    assert 'registered active state' in response.get_json()['error'].lower()
    assert (case / 'fabm.yaml').read_bytes() == original


def test_clone_rejects_missing_dynamic_prey_port_before_apply(tmp_path):
    case = tmp_path / 'missing_dynamic_port'
    case.mkdir()
    (case / 'fabm.yaml').write_text(
        'instances:\n  cladocerans:\n    model: wet/zooplankton\n'
        '    parameters:\n      nPrey: 1\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cladocerans', 'name': 'zoo_probe'}]})
    assert response.status_code == 400
    assert 'MISSING_REGISTERED_DEPENDENCY' in response.get_json()['error']
    assert 'prey_model1' in response.get_json()['error']


def test_cloning_phytoplankton_integrates_burial_and_carbon_without_changing_diets(tmp_path):
    case = tmp_path / 'phyto_integrations'
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    client, _ = transaction_client(case)
    before = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_competitor'}]}

    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    assert preview.get_json()['integrations'] == ['burial', 'inorganic_carbon']
    assert yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances'] == before

    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    result = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']
    assert result['burial']['parameters']['nPHYT'] == 4
    assert result['burial']['coupling']['POM_phytoplankton_update4'] == 'cyanobacteria_competitor/tDPOMS'
    assert result['inorganic_carbon']['parameters']['nPHYT'] == 4
    assert result['inorganic_carbon']['coupling']['CO2_uptake_water_4'] == 'cyanobacteria_competitor/wCO2UptW'
    assert result['inorganic_carbon']['coupling']['CO2_respiration_water_4'] == 'cyanobacteria_competitor/wCO2RespW'
    assert result['cladocerans']['coupling'] == before['cladocerans']['coupling']


def test_clone_copies_selected_output_variables_to_clone_prefix(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae_a:\n    model: wet/abiotic_water\n'
        '    initialization:\n      sPO4W: 0.1\n', encoding='utf-8')
    (case / 'output.yaml').write_text(
        'output:\n  time_step: 3600\n  variables:\n'
        '  - source: algae_a_sPO4W\n    name: parent phosphate\n'
        '  - source: temp\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'algae_a', 'name': 'algae_b'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    output = yaml.safe_load((case / 'output.yaml').read_bytes())
    assert output['output']['time_step'] == 3600
    selected = output['output']['variables']
    assert {'source': 'algae_a_sPO4W', 'name': 'parent phosphate'} in selected
    assert {'source': 'algae_b_sPO4W', 'name': 'algae_b_sPO4W'} in selected
    assert {'source': 'temp'} in selected


def test_clone_output_copy_is_limited_to_registered_states_owned_by_exact_instance(tmp_path):
    case = tmp_path / 'clone_output_owner'
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    (case / 'output.yaml').write_text(
        'output:\n  variables:\n'
        '  - source: cyanobacteria_sCW\n'
        '  - source: cyanobacteria_sCS\n'
        '  - source: cyanobacteria_sPW\n'
        '  - source: cyanobacteria_sDW\n'
        '  - source: cyanobacteria_oChla\n'
        '  - source: cyanobacteria_wNFix\n'
        '  - source: cyanobacteria_competitor_sDW\n'
        '  - source: cyanobacteria_competitor_sCW\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyano_probe'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    selected = {item['source'] for item in yaml.safe_load((case / 'output.yaml').read_bytes())['output']['variables']}
    assert {'cyano_probe_sCW', 'cyano_probe_sCS', 'cyano_probe_sPW', 'cyano_probe_sDW'} <= selected
    assert 'cyano_probe_oChla' not in selected
    assert 'cyano_probe_wNFix' not in selected
    assert 'cyano_probe_competitor_sDW' not in selected
    assert 'cyano_probe_competitor_sCW' not in selected


def test_clone_makes_output_alias_unique_when_source_alias_collides(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae_a:\n    model: wet/abiotic_water\n'
        '    initialization:\n      sPO4W: 0.1\n', encoding='utf-8')
    (case / 'output.yaml').write_text(
        'output:\n  variables:\n'
        '  - source: algae_a_sPO4W\n    name: phosphate\n'
        '  - source: temp\n    name: algae_b_sPO4W\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'algae_a', 'name': 'algae_b'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    selected = yaml.safe_load((case / 'output.yaml').read_bytes())['output']['variables']
    clone_entry = next(item for item in selected if item['source'] == 'algae_b_sPO4W')
    assert clone_entry['name'] != 'algae_b_sPO4W'
    assert clone_entry['name'] != 'phosphate'
    assert len([item['name'] for item in selected if 'name' in item]) == len(
        {item['name'] for item in selected if 'name' in item})


def test_clone_does_not_duplicate_existing_clone_output_selection(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae_a:\n    model: wet/abiotic_water\n'
        '    initialization:\n      sPO4W: 0.1\n', encoding='utf-8')
    (case / 'output.yaml').write_text(
        'output:\n  variables:\n  - source: algae_a_sPO4W\n'
        '  - source: algae_b_sPO4W\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'algae_a', 'name': 'algae_b'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    selected = yaml.safe_load((case / 'output.yaml').read_bytes())['output']['variables']
    assert [item['source'] for item in selected].count('algae_b_sPO4W') == 1


@pytest.mark.parametrize(('module', 'port'), [
    ('burial', 'POM_phytoplankton_update4'),
    ('inorganic_carbon', 'CO2_uptake_water_4'),
])
def test_cloning_phytoplankton_rejects_inconsistent_multiplexer_before_apply(tmp_path, module, port):
    case = tmp_path / f'inconsistent_{module}'
    case.mkdir()
    document = transaction_fabm_document()
    document['instances'][module]['parameters']['nPHYT'] = 2
    broken_port = 'POM_phytoplankton_update3' if module == 'burial' else 'CO2_uptake_water_3'
    del document['instances'][module]['coupling'][broken_port]
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_competitor'}]})
    assert response.status_code == 400
    assert 'nPHYT' in response.get_json()['error'] or 'coupling' in response.get_json()['error'].lower()
    assert (case / 'fabm.yaml').read_bytes() == original


@pytest.mark.parametrize(('module', 'broken_port'), [
    ('burial', 'POM_phytoplankton_update3'),
    ('inorganic_carbon', 'CO2_respiration_water_3'),
])
def test_cloning_phytoplankton_rejects_missing_indexed_port(tmp_path, module, broken_port):
    case = tmp_path / f'missing_{module}_port'
    case.mkdir()
    document = transaction_fabm_document()
    del document['instances'][module]['coupling'][broken_port]
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_competitor'}]})
    assert response.status_code == 400
    assert 'PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT' in response.get_json()['error']
    assert broken_port in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


def test_cloning_phytoplankton_preserves_valid_custom_multiplexer_order(tmp_path):
    case = tmp_path / 'custom_phyto_order'
    case.mkdir()
    document = transaction_fabm_document()
    for module, ports in {
        'burial': ['POM_phytoplankton_update1', 'POM_phytoplankton_update3'],
        'inorganic_carbon': ['CO2_uptake_water_1', 'CO2_uptake_water_3',
                             'CO2_respiration_water_1', 'CO2_respiration_water_3'],
    }.items():
        coupling = document['instances'][module]['coupling']
        for first, last in zip(ports[::2], ports[1::2]):
            coupling[first], coupling[last] = coupling[last], coupling[first]
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [
        {'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_competitor'}]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    result = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']
    assert result['burial']['coupling']['POM_phytoplankton_update1'] == 'greens/tDPOMS'
    assert result['burial']['coupling']['POM_phytoplankton_update3'] == 'cyanobacteria/tDPOMS'
    assert result['inorganic_carbon']['coupling']['CO2_uptake_water_4'] == 'cyanobacteria_competitor/wCO2UptW'


def test_rename_rewrites_exact_model_reference_in_consumers(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae_a:\n    model: wet/phytoplankton\n'
        '  zoo:\n    model: wet/zooplankton\n    parameters:\n      nPrey: 1\n'
        '    coupling:\n      prey_model1: algae_a\n# preserve outside the renamed graph\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    operations = [{'op': 'rename', 'name': 'algae_a', 'new_name': 'algae_green'}]
    request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': operations}
    preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    document = yaml.safe_load((case / 'fabm.yaml').read_bytes())
    assert 'algae_green' in document['instances']
    assert document['instances']['zoo']['coupling']['prey_model1'] == 'algae_green'
    assert b'# preserve outside the renamed graph' in (case / 'fabm.yaml').read_bytes()


def test_foodweb_and_stage_operations_compile_real_schema_ports(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n'
        '  algae_a:\n    model: wet/phytoplankton\n'
        '  fish_child:\n    model: wet/fish\n    parameters:\n      qStage: 1\n'
        '  fish_adult:\n    model: wet/fish\n    parameters:\n      qStage: 0\n'
        '    coupling:\n      NH4_pool_water: abiotic_water/sNH4W\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    operations = [
        {'op': 'set_foodweb', 'name': 'fish_adult', 'groups': {
            'PLAN': [{'target': 'algae_a', 'suffix': 'W', 'clearance': 0.2, 'gut_occupation': 1.0}],
            'BEN': [], 'PISC': []}},
        {'op': 'set_stage', 'name': 'fish_adult', 'qStage': 2, 'adult': 'fish_child',
         'parameters': {'cDinit': 0.1, 'cDfin': 1.0}},
    ]
    request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': operations}
    preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    document = yaml.safe_load((case / 'fabm.yaml').read_bytes())
    fish = document['instances']['fish_adult']
    assert fish['parameters']['nPLAN'] == 1
    assert fish['parameters']['qStage'] == 2
    assert fish['coupling']['PLANprey1'] == 'algae_a'
    assert fish['parameters']['PLANprey_suffix1'] == 'W'
    assert fish['coupling']['adult_D'] == 'fish_child/sD'
    assert fish['coupling']['adult_Siz'] == 'fish_child/sDSiz'
    assert fish['coupling']['NH4_pool_water'] == 'abiotic_water/sNH4W'


def test_foodweb_rejects_invalid_target_and_stage_type_without_writing(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  fish_a:\n    model: wet/fish\n    parameters:\n      qStage: 0\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    bad_operations = [
        [{'op': 'set_foodweb', 'name': 'fish_a', 'groups': {
            'PLAN': [{'target': 'missing', 'suffix': 'W', 'clearance': 1, 'gut_occupation': 1}],
            'BEN': [], 'PISC': []}}],
        [{'op': 'set_stage', 'name': 'fish_a', 'qStage': True}],
    ]
    for operations in bad_operations:
        response = client.post('/api/model/instances/transaction', json={
            'case_path': str(case), 'revision': state['revision'], 'mode': 'preview', 'operations': operations})
        assert response.status_code == 400
        assert (case / 'fabm.yaml').read_bytes() == original


def test_delete_and_restore_are_previewed_and_preserve_instance_identity(case):
    client, _ = transaction_client(case)

    def transact(operations):
        state = client.get('/api/model/instances').get_json()
        request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': operations}
        preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
        assert preview.status_code == 200, preview.get_json()
        repeated = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
        assert repeated.status_code == 200, repeated.get_json()
        assert repeated.get_json()['preview_hash'] == preview.get_json()['preview_hash']
        applied = client.post('/api/model/instances/transaction', json={
            **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
        assert applied.status_code == 200, applied.get_json()
        return applied.get_json()

    original_bytes = (case / 'fabm.yaml').read_bytes()
    before = client.get('/api/model/instances').get_json()
    transact([{'op': 'delete', 'name': 'algae_a'}])
    assert 'algae_a' not in yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']
    assert (case / 'fabm.yaml').read_bytes().startswith(b'\xef\xbb\xbf')
    assert b'# preserve this comment\r\n' in (case / 'fabm.yaml').read_bytes()
    assert original_bytes != (case / 'fabm.yaml').read_bytes()

    deleted_state = client.get('/api/model/instances').get_json()
    deleted = deleted_state['deleted']
    assert len(deleted) == 1
    assert deleted[0]['name'] == 'algae_a'
    assert deleted[0]['model'] == 'wet/phytoplankton'
    deleted_id = deleted[0]['id']

    collision = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': deleted_state['revision'], 'mode': 'preview',
        'operations': [{'op': 'add', 'name': 'algae_a', 'model': 'wet/phytoplankton'}]})
    assert collision.status_code == 400
    assert 'reserved' in collision.get_json()['error']

    restored = transact([{'op': 'restore', 'name': 'algae_a'}])
    document = yaml.safe_load((case / 'fabm.yaml').read_bytes())
    assert document['instances']['algae_a']['parameters']['k'] == 1.0
    after = client.get('/api/model/instances').get_json()
    assert after['deleted'] == []
    assert after['instances'][0]['name'] == 'algae_a'
    sidecar = json.loads((case / '.studio-config' / 'wet_instances.json').read_text())
    assert sidecar['instances']['algae_a']['id'] == deleted_id
    assert b'# keep this note' in (case / 'fabm.yaml').read_bytes()
    assert restored['revision'] == after['revision']
    assert before['instances'][0]['name'] == after['instances'][0]['name']


def test_restore_rejects_unknown_and_active_name_conflicts(case):
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    missing = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'restore', 'name': 'missing'}]})
    assert missing.status_code == 400
    assert 'deleted instance' in missing.get_json()['error']

    transaction = [{'op': 'delete', 'name': 'algae_a'},
                   {'op': 'add', 'name': 'algae_a', 'model': 'wet/phytoplankton'}]
    preview = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview', 'operations': transaction})
    assert preview.status_code == 400
    assert 'reserved' in preview.get_json()['error']
    assert 'algae_a' in yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']


def test_delete_preserves_a_list_config_exactly_for_restore(case):
    original = ('instances:\n  algae_a:\n    model: wet/phytoplankton\n'
                '    initialization:\n      custom_state: [1, 2, 3] # preserve exact block\n')
    (case / 'fabm.yaml').write_text(original, encoding='utf-8')
    client, _ = transaction_client(case)

    def apply(operation):
        state = client.get('/api/model/instances').get_json()
        request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': [operation]}
        preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
        assert preview.status_code == 200, preview.get_json()
        response = client.post('/api/model/instances/transaction', json={
            **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
        assert response.status_code == 200, response.get_json()

    apply({'op': 'delete', 'name': 'algae_a'})
    apply({'op': 'restore', 'name': 'algae_a'})
    restored = (case / 'fabm.yaml').read_text(encoding='utf-8')
    assert 'custom_state: [1, 2, 3] # preserve exact block' in restored
    assert yaml.safe_load(restored)['instances']['algae_a']['initialization']['custom_state'] == [1, 2, 3]


def test_delete_rejects_instance_with_live_incoming_couplings(case):
    (case / 'fabm.yaml').write_text(
        'instances:\n  algae_a:\n    model: wet/phytoplankton\n'
        '  zoo:\n    model: wet/zooplankton\n    parameters:\n      nPrey: 1\n'
        '    coupling:\n      prey_model1: algae_a\n', encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'delete', 'name': 'algae_a'}]})
    assert response.status_code == 400
    assert 'INSTANCE_IN_USE' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


def test_legacy_network_write_uses_shared_transaction(case, monkeypatch):
    import case_model_transaction as tx
    client, _ = transaction_client(case)
    state = client.get('/api/ecology/network').get_json()
    calls = []
    real = tx.commit_files

    def observed(path, candidates, **kwargs):
        calls.append(tuple(sorted(candidates)))
        return real(path, candidates, **kwargs)

    monkeypatch.setattr(tx, 'commit_files', observed)
    response = client.post('/api/ecology/network', json={**state, 'module': 'algae_a', 'parameters': {'k': 3.0}})
    assert response.status_code == 200, response.get_json()
    assert calls and calls[0] == ('fabm.yaml',)



@pytest.mark.parametrize(('fraction', 'source_value', 'clone_value'), [(0.25, 0.075, 0.025)])
def test_clone_equal_total_splits_explicit_registered_initial_states(tmp_path, fraction, source_value, clone_value):
    case = tmp_path / f'split_{fraction}'
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    source_before = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']['cyanobacteria']['initialization']
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    operation = {'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_competitor',
                 'initial_fraction': fraction}
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [operation]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    data = preview.get_json()
    assert data['initial_split']['fraction_to_clone'] == fraction
    assert 'sDW' in data['initial_split']['states']
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': data['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    instances = yaml.safe_load((case / 'fabm.yaml').read_bytes())['instances']
    schema_states = set(__import__('wet_instance_catalog').get_model_schema('wet/phytoplankton')['states'])
    source_after = instances['cyanobacteria']['initialization']
    clone_after = instances['cyanobacteria_competitor']['initialization']
    assert set(source_after) == set(clone_after) == schema_states
    for state in schema_states:
        assert float(source_after[state]) + float(clone_after[state]) == pytest.approx(float(source_before[state]))
    assert instances['cyanobacteria']['initialization']['sDW'] == pytest.approx(source_value)
    assert instances['cyanobacteria_competitor']['initialization']['sDW'] == pytest.approx(clone_value)
    assert instances['cyanobacteria']['parameters'] == instances['cyanobacteria_competitor']['parameters']
    assert instances['cyanobacteria']['coupling'] == instances['cyanobacteria_competitor']['coupling']


def test_clone_split_preserves_flexout_wildcard_when_copying_output_subscriptions(tmp_path):
    case = tmp_path / 'flexout_wildcard_split'
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    output = (b'output:\n  variables:\n'
              b'    - source: cyanobacteria_sDW\n      time_step: 1\n'
              b'    - source: *\n      time_step: 1\n')
    (case / 'output.yaml').write_bytes(output)
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    operation = {'op': 'clone', 'source': 'cyanobacteria', 'name': 'cyanobacteria_split_probe',
                 'initial_fraction': 0.5}
    payload = {'case_path': str(case), 'revision': state['revision'], 'operations': [operation]}
    preview = client.post('/api/model/instances/transaction', json={**payload, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    applied = client.post('/api/model/instances/transaction', json={
        **payload, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert applied.status_code == 200, applied.get_json()
    updated = (case / 'output.yaml').read_bytes()
    assert b'- source: *\n' in updated, 'preserve the WET Flexout wildcard syntax verbatim'
    assert b'cyanobacteria_split_probe_sDW' in updated, 'copy the selected output subscription to the clone'


def test_clone_split_is_unavailable_when_any_registered_initial_state_is_undeclared(tmp_path):
    case = tmp_path / 'incomplete_split'
    case.mkdir()
    document = transaction_fabm_document()
    del document['instances']['cyanobacteria']['initialization']['sPW']
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cyanobacteria', 'name': 'other', 'initial_fraction': 0.5}]})
    assert response.status_code == 400
    assert 'INITIAL_SPLIT_UNAVAILABLE' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


@pytest.mark.parametrize('bad_value', [float('nan'), float('inf'), 'unknown'])
def test_clone_split_rejects_nonfinite_or_unrecognized_initial_value(tmp_path, bad_value):
    case = tmp_path / 'invalid_initial_value'
    case.mkdir()
    document = transaction_fabm_document()
    document['instances']['cyanobacteria']['initialization']['sDW'] = bad_value
    (case / 'fabm.yaml').write_text(yaml.safe_dump(document, sort_keys=False), encoding='utf-8')
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'cyanobacteria', 'name': 'other', 'initial_fraction': 0.5}]})
    assert response.status_code == 400
    assert 'INITIAL_SPLIT_UNAVAILABLE' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original


def test_clone_split_apply_failure_restores_every_original_byte(tmp_path, monkeypatch):
    import case_model_transaction as tx
    case = tmp_path / 'split_rollback'
    case.mkdir()
    (case / 'fabm.yaml').write_bytes(transaction_fabm_bytes())
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    operation = {'op': 'clone', 'source': 'cyanobacteria', 'name': 'other', 'initial_fraction': 0.5}
    request_data = {'case_path': str(case), 'revision': state['revision'], 'operations': [operation]}
    preview = client.post('/api/model/instances/transaction', json={**request_data, 'mode': 'preview'})
    assert preview.status_code == 200, preview.get_json()
    real_replace = tx.os.replace
    count = 0
    def fail_first_commit_replace(src, dst):
        nonlocal count
        count += 1
        if count == 2:
            raise OSError('injected split commit failure')
        return real_replace(src, dst)
    monkeypatch.setattr(tx.os, 'replace', fail_first_commit_replace)
    response = client.post('/api/model/instances/transaction', json={
        **request_data, 'mode': 'apply', 'preview_hash': preview.get_json()['preview_hash']})
    assert response.status_code == 400
    assert (case / 'fabm.yaml').read_bytes() == original


@pytest.mark.parametrize('fraction', [-0.01, 0.0, 1.0, 1.01, float('nan'), float('inf'), '0.5', True])
def test_clone_split_rejects_invalid_fraction_without_mutation(case, fraction):
    client, _ = transaction_client(case)
    state = client.get('/api/model/instances').get_json()
    original = (case / 'fabm.yaml').read_bytes()
    response = client.post('/api/model/instances/transaction', json={
        'case_path': str(case), 'revision': state['revision'], 'mode': 'preview',
        'operations': [{'op': 'clone', 'source': 'algae_a', 'name': 'algae_b', 'initial_fraction': fraction}]})
    assert response.status_code == 400
    assert 'INVALID_INITIAL_FRACTION' in response.get_json()['error']
    assert (case / 'fabm.yaml').read_bytes() == original
