import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))

from wet_foodweb import (  # noqa: E402
    compile_fish_diet, compile_stage_coupling, compile_zooplankton_diet,
)


def _prey(i):
    return {'target': f'algae_{i}', 'suffix': 'W', 'clearance': 0.2, 'gut_occupation': 1.0}


def test_dynamic_plan_family_is_not_limited_to_three_and_reduction_cleans_exact_family():
    inst = {'model': 'wet/fish', 'parameters': {'nPLAN': 1},
            'coupling': {'NH4_pool_water': 'abiotic_water/sNH4W', 'PLANprey1': 'old'}}
    graph = {f'algae_{i}': {'model': 'wet/phytoplankton', 'states': ['sDW', 'sNW', 'sPW', 'sCW'],
                            'state_units': {'sDW': 'gDW/m3', 'sNW': 'gN/m3', 'sPW': 'gP/m3', 'sCW': 'gC/m3'}} for i in range(5)}
    compiled = compile_fish_diet(inst, {'PLAN': [_prey(i) for i in range(5)], 'BEN': [], 'PISC': []}, graph)
    assert compiled['parameters']['nPLAN'] == 5
    assert compiled['coupling']['PLANprey5'] == 'algae_4'
    assert compiled['parameters']['PLANprey_suffix5'] == 'W'
    assert compiled['coupling']['NH4_pool_water'] == 'abiotic_water/sNH4W'
    reduced = compile_fish_diet(compiled, {'PLAN': [_prey(0)], 'BEN': [], 'PISC': []}, graph)
    assert 'PLANprey5' not in reduced['coupling']
    assert 'cClearPlan5' not in reduced['parameters']
    assert 'PLANprey2' not in reduced['coupling']


def test_native_catalog_compile_snapshot_has_five_plan_two_ben_four_pisc_and_two_zoo_prey():
    graph = {}
    plan = []
    for i in range(5):
        name = f'algae_{i}'
        graph[name] = {'model': 'wet/phytoplankton', 'states': ['sDW','sNW','sPW','sCW'],
                       'state_units': {'sDW':'gDW/m3','sNW':'gN/m3','sPW':'gP/m3','sCW':'gC/m3'}}
        plan.append({'target': name, 'suffix': 'W', 'clearance': 0.2, 'gut_occupation': 1.0})
    bent = []
    ben_states = ['sD','sN','sP','sC','sD_PV','sN_PV','sP_PV','sC_PV']
    ben_units = {'sD':'gDW/m2','sN':'gN/m2','sP':'gP/m2','sC':'gC/m2','sD_PV':'gDW/m2','sN_PV':'gN/m2','sP_PV':'gP/m2','sC_PV':'gC/m2'}
    for i in range(2):
        name = f'benthos_{i}'
        graph[name] = {'model':'wet/zoobenthos', 'states':ben_states, 'state_units':ben_units}
        bent.append({'target':name,'suffix':'','clearance':0.06,'gut_occupation':1.0})
    pisc = []
    fish_states = ['sD','sN','sP','sC','fVul','pred_dummy']
    fish_units = {'sD':'gDW/m3','sN':'gN/m3','sP':'gP/m3','sC':'gC/m3','fVul':'-','pred_dummy':'-'}
    for i in range(4):
        name = f'fish_{i}'
        graph[name] = {'model':'wet/fish','states':fish_states,'state_units':fish_units}
        pisc.append({'target':name,'clearance':0.021,'gut_occupation':1.0})
    pisc_compiled = compile_fish_diet({'model':'wet/fish','name':'consumer','parameters':{},'coupling':{}},
                                      {'PLAN':plan,'BEN':bent,'PISC':pisc}, graph)
    assert pisc_compiled['parameters']['nPISC'] == 4
    assert pisc_compiled['coupling']['PISCprey4'] == 'fish_3'
    compiled = compile_fish_diet({'model':'wet/fish','name':'consumer','parameters':{},'coupling':{}},
                                 {'PLAN':plan,'BEN':bent,'PISC':[]}, graph)
    assert [compiled['parameters'][name] for name in ('nPLAN','nBEN','nPISC')] == [5,2,0]
    assert compiled['coupling']['PLANprey5'] == 'algae_4'
    assert compiled['coupling']['BENTprey2'] == 'benthos_1'
    zoo = compile_zooplankton_diet(
        {'model':'wet/zooplankton','parameters':{},'coupling':{}},
        [{'target':'algae_0','suffix':'W','clearance':0.3,'gut_occupation':1.0},
         {'target':'algae_1','suffix':'W','clearance':0.4,'gut_occupation':1.0}], graph)
    assert zoo['parameters']['nPrey'] == 2
    assert zoo['coupling']['prey_model2'] == 'algae_1'


def test_ben_pisc_and_zooplankton_dynamic_ports_validate_target_contracts():
    fish = {'model': 'wet/fish', 'parameters': {}, 'coupling': {'NH4_pool_water': 'abiotic_water/sNH4W'}}
    graph = {
        'algae_a': {'model': 'wet/phytoplankton', 'states': ['sDW', 'sNW', 'sPW', 'sCW'], 'state_units': {'sDW':'gDW/m3','sNW':'gN/m3','sPW':'gP/m3','sCW':'gC/m3'}},
        'algae': {'model': 'wet/phytoplankton', 'states': ['sDW', 'sNW', 'sPW', 'sCW'], 'state_units': {'sDW':'gDW/m3','sNW':'gN/m3','sPW':'gP/m3','sCW':'gC/m3'}},
        'benthos': {'model': 'wet/zoobenthos', 'states': ['sD', 'sN', 'sP', 'sC', 'sD_PV', 'sN_PV', 'sP_PV', 'sC_PV'], 'state_units': {s:u for s,u in zip(['sD','sN','sP','sC','sD_PV','sN_PV','sP_PV','sC_PV'], ['gDW/m2','gN/m2','gP/m2','gC/m2','gDW/m2','gN/m2','gP/m2','gC/m2'])}},
        'fish_b': {'model': 'wet/fish', 'states': ['sD', 'sN', 'sP', 'sC', 'fVul', 'pred_dummy'], 'state_units': {'sD':'gDW/m3','sN':'gN/m3','sP':'gP/m3','sC':'gC/m3','fVul':'-','pred_dummy':'DW/m3'}},
    }
    with pytest.raises(ValueError, match='UNIT_MISMATCH.*fish_b/pred_dummy requires -'):
        compile_fish_diet(fish, {
        'PLAN': [{'target': 'algae_a', 'suffix': 'W', 'clearance': 0.2, 'gut_occupation': 1.0}],
        'BEN': [{'target': 'benthos', 'suffix': '', 'clearance': 0.1, 'gut_occupation': 1.0}],
        'PISC': [{'target': 'fish_b', 'clearance': 0.02, 'gut_occupation': 1.0}],
        }, graph)
    compiled = compile_fish_diet(fish, {
        'PLAN': [{'target': 'algae_a', 'suffix': 'W', 'clearance': 0.2, 'gut_occupation': 1.0}],
        'BEN': [{'target': 'benthos', 'suffix': '', 'clearance': 0.1, 'gut_occupation': 1.0}],
        'PISC': [],
    }, graph)
    assert compiled['coupling']['BENTprey1'] == 'benthos'
    assert compiled['parameters']['nPISC'] == 0
    assert 'BENprey_suffix1' not in compiled['parameters']
    zoo = compile_zooplankton_diet(
        {'model': 'wet/zooplankton', 'parameters': {}, 'coupling': {}},
        [{'target': 'algae', 'suffix': 'W', 'clearance': 0.3, 'gut_occupation': 1.0, 'lSi': False}],
        graph,
    )
    assert zoo['parameters']['nPrey'] == 1
    assert zoo['coupling']['prey_model1'] == 'algae'
    zoo2 = compile_zooplankton_diet(zoo, [], graph)
    assert zoo2['parameters']['nPrey'] == 0
    assert 'prey_model1' not in zoo2['coupling']
    assert 'cClearPrey1' not in zoo2['parameters']


def test_typed_targets_numeric_domain_and_units_are_strict():
    fish = {'model': 'wet/fish', 'parameters': {}, 'coupling': {}}
    with pytest.raises(ValueError, match='INVALID_TARGET'):
        compile_fish_diet(fish, {'PLAN': [{'target': 'algae/sDW', **_prey(0)}], 'BEN': [], 'PISC': []})
    graph = {'algae_0': {'model': 'wet/phytoplankton', 'states': ['sDW', 'sNW', 'sPW', 'sCW'], 'state_units': {'sDW':'gDW/m3','sNW':'gN/m3','sPW':'gP/m3','sCW':'gC/m3'}}}
    bad = {**_prey(0), 'clearance': float('nan')}
    with pytest.raises(ValueError, match='NONFINITE_VALUE'):
        compile_fish_diet(fish, {'PLAN': [bad], 'BEN': [], 'PISC': []}, graph)
    graph = {'water_state': {'model': 'wet/abiotic_water', 'states': ['sNH4W']}, **graph}
    with pytest.raises(ValueError, match='DOMAIN_MISMATCH'):
        compile_fish_diet(fish, {'PLAN': [{**_prey(0), 'target': 'water_state'}], 'BEN': [], 'PISC': []}, graph)


def test_stage_maps_all_six_registered_state_dependencies_and_clears_when_disabled():
    fish_a = {'model': 'wet/fish', 'parameters': {'qStage': 0}, 'coupling': {'NH4_pool_water': 'abiotic_water/sNH4W'}}
    graph = {'fish_b': {'model': 'wet/fish', 'parameters': {'qStage': 3}, 'states': ['sD', 'sN', 'sP', 'sC', 'sFRes', 'sDSiz'], 'state_units': {'sD':'gDW/m3','sN':'gN/m3','sP':'gP/m3','sC':'gC/m3','sFRes':'gDW/m3','sDSiz':'gDW/ind'}}}
    result = compile_stage_coupling(fish_a, {'qStage': 1, 'juvenile': 'fish_b', 'adult': None,
                                            'parameters': {'cDinit': 0.1, 'cDfin': 1.0, 'cDegg': 0.02}}, graph)
    assert result['parameters']['qStage'] == 1
    assert result['coupling']['juvenile_C'] == 'fish_b/sC'
    assert result['coupling']['juvenile_Res'] == 'fish_b/sFRes'
    assert 'juvenile_C' not in compile_stage_coupling(result, {'qStage': 0}, graph)['coupling']


def test_stage_refuses_incomplete_state_target_and_invalid_stage_parameters():
    fish = {'model': 'wet/fish', 'parameters': {}, 'coupling': {}}
    graph = {'fish_b': {'model': 'wet/fish', 'parameters': {'qStage': 2}, 'states': ['sD', 'sN', 'sP', 'sFRes', 'sDSiz'], 'state_units': {'sD':'gDW/m3','sN':'gN/m3','sP':'gP/m3','sFRes':'gDW/m3','sDSiz':'gDW/ind'}}}
    with pytest.raises(ValueError, match='UNKNOWN_PORT'):
        compile_stage_coupling(fish, {'qStage': 1, 'juvenile': 'fish_b', 'parameters': {'cDinit':0.1,'cDfin':1.0,'cDegg':0.02}}, graph)
    with pytest.raises(ValueError, match='INVALID_STAGE'):
        compile_stage_coupling(fish, {'qStage': 4}, graph)
    with pytest.raises(ValueError, match='cDfin must be greater'):
        compile_stage_coupling(fish, {'qStage': 1, 'parameters': {'cDinit': 2, 'cDfin': 1, 'cDegg':0.02}}, graph)
    with pytest.raises(ValueError, match='reserve fractions'):
        compile_stage_coupling(fish, {'qStage': 2, 'parameters': {'cDinit':0.1,'cDfin':1.0,'fResMin': 0.8, 'fResMax': 0.5}}, graph)
    with pytest.raises(ValueError, match='cDegg'):
        compile_stage_coupling(fish, {'qStage': 1, 'parameters': {'cDinit':0.1,'cDfin':1.0,'cDegg': 0}}, graph)


def test_stage_cycle_is_allowed_and_stage_off_clears_conditioned_parameters():
    first = {'model': 'wet/fish', 'name': 'fish_a', 'parameters': {'qStage': 3, 'fResMin': 0.2, 'fResMax': 0.5, 'cDayReprFish': 120,
            'cDinit':0.1,'cDfin':1.0,'cDegg':0.02},
             'coupling': {'juvenile_C': 'fish_b/sC', 'adult_C': 'fish_b/sC', 'NH4_pool_water': 'abiotic_water/sNH4W'}}
    fish_states = ['sD', 'sN', 'sP', 'sC', 'sFRes', 'sDSiz']
    units = {'sD':'gDW/m3','sN':'gN/m3','sP':'gP/m3','sC':'gC/m3','sFRes':'gDW/m3','sDSiz':'gDW/ind'}
    graph = {
        'fish_a': {'model': 'wet/fish', 'name': 'fish_a', 'parameters': {'qStage': 3}, 'states': fish_states, 'state_units': units},
        'fish_b': {'model': 'wet/fish', 'name': 'fish_b', 'parameters': {'qStage': 3}, 'states': fish_states, 'state_units': units},
    }
    result = compile_stage_coupling(first, {'qStage': 3, 'juvenile': 'fish_b', 'adult': 'fish_b',
                                           'parameters': {'cDinit':0.1,'cDfin':1.0,'cDegg':0.02}}, graph)
    assert result['coupling']['juvenile_C'] == 'fish_b/sC'
    assert result['coupling']['adult_C'] == 'fish_b/sC'
    second = compile_stage_coupling(
        {'model': 'wet/fish', 'name': 'fish_b', 'parameters': {}, 'coupling': {}},
        {'qStage': 1, 'juvenile': 'fish_a', 'parameters': {'cDinit':0.1,'cDfin':1.0,'cDegg':0.02}}, graph,
    )
    assert second['coupling']['juvenile_C'] == 'fish_a/sC'
    off = compile_stage_coupling(result, {'qStage': 0}, graph)
    assert 'juvenile_C' not in off['coupling'] and 'adult_C' not in off['coupling']
    assert 'fResMin' not in off['parameters'] and 'cDayReprFish' not in off['parameters']
    assert off['coupling']['NH4_pool_water'] == 'abiotic_water/sNH4W'


def test_hand_authored_fish_prey_overrides_require_exact_explicit_removal():
    fish = {'model': 'wet/fish', 'parameters': {},
            'coupling': {'plankton_D_Food1': 'algae_0/sDW', 'NH4_pool_water': 'abiotic_water/sNH4W'}}
    graph = {'algae_0': {'model': 'wet/phytoplankton', 'states': ['sDW','sNW','sPW','sCW'],
                         'state_units': {'sDW':'gDW/m3','sNW':'gN/m3','sPW':'gP/m3','sCW':'gC/m3'}}}
    groups = {'PLAN': [_prey(0)], 'BEN': [], 'PISC': []}
    with pytest.raises(ValueError, match='MANUAL_OVERRIDE_CONFLICT'):
        compile_fish_diet(fish, groups, graph)
    compiled = compile_fish_diet(fish, groups, graph, remove_overrides=['plankton_D_Food1'])
    assert 'plankton_D_Food1' not in compiled['coupling']
    assert compiled['coupling']['NH4_pool_water'] == 'abiotic_water/sNH4W'


@pytest.mark.parametrize('compiler,instance', [
    (compile_zooplankton_diet, {'model': 'wet/zooplankton', 'parameters': {}, 'coupling': {}}),
    (compile_fish_diet, {'model': 'wet/fish', 'parameters': {}, 'coupling': {}}),
])
def test_pelagic_consumers_reject_area_based_suffix_without_verified_conversion(compiler, instance):
    states = ['sD', 'sP', 'sN', 'sC', 'sDS', 'sPS', 'sNS', 'sCS']
    units = {'sD':'gDW/m3', 'sP':'gP/m3', 'sN':'gN/m3', 'sC':'gC/m3',
             'sDS':'gDW/m2', 'sPS':'gP/m2', 'sNS':'gN/m2', 'sCS':'gC/m2'}
    graph = {'pelagic': {'model': 'wet/phytoplankton', 'states': states, 'state_units': units}}
    with pytest.raises(ValueError, match='INVALID_SUFFIX'):
        if compiler is compile_zooplankton_diet:
            compiler(instance, [{'target': 'pelagic', 'suffix': 'S', 'clearance': 0.2, 'gut_occupation': 1}], graph)
        else:
            compiler(instance, {'PLAN': [{'target': 'pelagic', 'suffix': 'S', 'clearance': 0.2, 'gut_occupation': 1}], 'BEN': [], 'PISC': []}, graph)


@pytest.mark.parametrize('compiler,document', [
    (compile_fish_diet, {'PLAN': [], 'BEN': [], 'PISC': []}),
    (compile_stage_coupling, {'qStage': 0}),
])
def test_fish_only_compilers_reject_zooplankton_consumers(compiler, document):
    zoo = {'model': 'wet/zooplankton', 'parameters': {}, 'coupling': {}}
    with pytest.raises(ValueError, match='INVALID_MODEL.*wet/fish'):
        compiler(zoo, document)


def test_ben_suffix_s_uses_native_ds_pv_port_spelling():
    fish = {'model': 'wet/fish', 'parameters': {}, 'coupling': {}}
    states = ['sDS', 'sPS', 'sNS', 'sCS', 'sDS_PV', 'sPS_PV', 'sNS_PV', 'sCS_PV']
    units = {'sDS':'gDW/m2', 'sPS':'gP/m2', 'sNS':'gN/m2', 'sCS':'gC/m2',
             'sDS_PV':'gDW/m2', 'sPS_PV':'gP/m2', 'sNS_PV':'gN/m2', 'sCS_PV':'gC/m2'}
    graph = {'benthic': {'model': 'wet/macrophytes', 'states': states, 'state_units': units}}
    # Force compilation to resolve each native registration; typo sD_PVS must fail.
    result = compile_fish_diet(fish, {
        'PLAN': [], 'PISC': [],
        'BEN': [{'target': 'benthic', 'suffix': 'S', 'clearance': 0.1, 'gut_occupation': 1}],
    }, graph)
    assert result['parameters']['BENprey_suffix1'] == 'S'
    typo_states = [state.replace('_PV', '') + '_PVS' if state.endswith('_PV') else state for state in states]
    typo_graph = {'benthic': {'model': 'wet/macrophytes', 'states': typo_states,
                              'state_units': {state: units[state.replace('_PVS', '_PV')] for state in typo_states}}}
    with pytest.raises(ValueError, match='UNKNOWN_PORT.*sDS_PV'):
        compile_fish_diet(fish, {
            'PLAN': [], 'PISC': [],
            'BEN': [{'target': 'benthic', 'suffix': 'S', 'clearance': 0.1, 'gut_occupation': 1}],
        }, typo_graph)
