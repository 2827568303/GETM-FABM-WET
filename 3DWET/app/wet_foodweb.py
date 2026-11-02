"""Compile typed WET prey and stage relations into native FABM ports."""
from __future__ import annotations

from copy import deepcopy
import math
import re
from typing import Any

from wet_instance_catalog import get_model_schema

FISH_FAMILIES = {
    'PLAN': ('nPLAN', 'PLANprey', 'PLANprey_suffix', 'cClearPlan', 'fGutOccPlan'),
    'BEN': ('nBEN', 'BENTprey', 'BENprey_suffix', 'cClearBent', 'fGutOccBent'),
    'PISC': ('nPISC', 'PISCprey', None, 'cClearPisc', 'fGutOccPisc'),
}
STAGE_PORTS = {
    'D': ('sD', 'gDW/m3'), 'N': ('sN', 'gN/m3'), 'P': ('sP', 'gP/m3'),
    'C': ('sC', 'gC/m3'), 'Res': ('sFRes', 'gDW/m3'), 'Siz': ('sDSiz', 'gDW/ind'),
}
_FLOAT_TYPES = (int, float)


def _mapping(instance: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(instance, dict) or instance.get('model') not in ('wet/fish', 'wet/zooplankton'):
        raise ValueError('INVALID_MODEL: expected wet/fish or wet/zooplankton')
    params = instance.setdefault('parameters', {})
    coupling = instance.setdefault('coupling', {})
    if not isinstance(params, dict) or not isinstance(coupling, dict):
        raise ValueError('INVALID_DOCUMENT: parameters and coupling must be mappings')
    return params, coupling


def _finite_number(value: Any, label: str, *, minimum: float | None = None, strict_minimum: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, _FLOAT_TYPES):
        raise ValueError(f'INVALID_VALUE: {label} must be numeric')
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f'NONFINITE_VALUE: {label}')
    if minimum is not None and (number <= minimum if strict_minimum else number < minimum):
        raise ValueError(f'INVALID_VALUE: {label} outside allowed range')
    return number


def _target_info(target: str, group: str, target_catalog: dict[str, Any] | None, *, allow_out_of_family: bool = False) -> dict[str, Any]:
    if not isinstance(target, str) or not target or '/' in target or '\\' in target:
        raise ValueError(f'INVALID_TARGET: {target!r} must be a bare model instance reference')
    if target_catalog is None or target not in target_catalog:
        raise ValueError(f'INVALID_TARGET: {target!r} is not present in the typed target catalog')
    info = target_catalog[target]
    if not isinstance(info, dict) or not isinstance(info.get('model'), str):
        raise ValueError(f'INVALID_TARGET: {target!r} has no model contract')
    family = info['model'].removeprefix('wet/')
    states = set(info.get('states') or ()) | set((info.get('diagnostics') or {}).keys()) | set((info.get('ports') or {}).keys())
    combined_units = dict(info.get('state_units') or {})
    combined_units.update({name: value.get('units') for name, value in (info.get('diagnostics') or {}).items() if isinstance(value, dict)})
    combined_units.update(info.get('port_units') or {})
    if group == 'PLAN':
        valid_families = {'phytoplankton', 'zooplankton'}
    elif group == 'BEN':
        valid_families = {'zoobenthos', 'bivalves', 'macrophytes', 'fish_pclake'}
    else:
        valid_families = {'fish'}
    if not info['model'].startswith('wet/') or (family not in valid_families and not allow_out_of_family):
        raise ValueError(f'DOMAIN_MISMATCH: {target} model {info["model"]} cannot be a {group} prey')
    return {'family': family, 'states': states, 'state_units': combined_units,
            'parameters': info.get('parameters', {})}


def _validate_prey(row: dict[str, Any], group: str, catalog: dict[str, Any], seen: set[tuple[str, str]]) -> tuple[str, str, float, float]:
    if not isinstance(row, dict):
        raise ValueError(f'INVALID_TARGET: {group} prey entries must be mappings')
    target = row.get('target')
    info = _target_info(target, group, catalog)
    suffix = row.get('suffix', '')
    if not isinstance(suffix, str) or suffix not in get_model_schema('wet/fish')['dynamic_families'][group]['allowed_suffixes']:
        raise ValueError(f'INVALID_SUFFIX: {group} suffix {suffix!r}')
    # Pelagic producers expose volumetric ports (optionally suffixed W). An
    # area-based S suffix is not valid for fish or zooplankton pelagic diets.
    if group == 'PLAN' and suffix not in ('', 'W'):
        raise ValueError(f'INVALID_SUFFIX: {group} supports only volumetric suffixes W or empty')
    required = get_model_schema('wet/fish')['dynamic_families'][group]['required_states']
    if group == 'BEN' and suffix == 'S':
        # fish.F90 asks for sD<S>_PV, e.g. sDS_PV. The native names place
        # S before _PV; appending S to the complete registered name is wrong.
        resolved = [state[:-3] + suffix + '_PV' if state.endswith('_PV') else state + suffix
                    for state in required]
    else:
        resolved = [state + suffix for state in required]
    missing = [state for state in resolved if state not in info['states']]
    if missing:
        raise ValueError(f'UNKNOWN_PORT: {target} missing required states {missing}')
    units = info.get('state_units')
    if not isinstance(units, dict) or any(state not in units for state in resolved):
        raise ValueError(f'INVALID_TARGET: {target} lacks registered units for required states')
    expected_element_units = {'D': 'gDW', 'N': 'gN', 'P': 'gP', 'C': 'gC'}
    expected_area = '/m2' if group == 'BEN' or suffix == 'S' else '/m3'
    for state in resolved:
        base = state[:-len(suffix)] if suffix else state
        element = next((element for element in expected_element_units if base.startswith('s' + element)), None)
        if element and units[state] != expected_element_units[element] + expected_area:
            raise ValueError(f'UNIT_MISMATCH: {target}/{state} requires {expected_element_units[element] + expected_area}, got {units[state]}')
    if group == 'PISC':
        expected = get_model_schema('wet/fish')['dynamic_state_families']['PISC']['consumer_units']['pred_dummyN']
        producer_units = get_model_schema('wet/fish')['diagnostics']['pred_dummy']['units']
        if producer_units != expected:
            raise ValueError(f'UNIT_MISMATCH: fish/PISC dependency requires {expected}, but native pred_dummy producer registers {producer_units}')
        target_units = units.get('pred_dummy')
        if target_units != producer_units:
            raise ValueError(f'UNIT_MISMATCH: {target}/pred_dummy requires {producer_units}, got {target_units}')
    if group == 'BEN' and info['family'] not in {'zoobenthos', 'bivalves', 'macrophytes', 'fish_pclake'}:
        raise ValueError(f'DOMAIN_MISMATCH: {target} has no benthic domain')
    identity = (target, suffix)
    if identity in seen:
        raise ValueError(f'DUPLICATE_TARGET: {group} repeats {target}{suffix}')
    seen.add(identity)
    clearance = _finite_number(row.get('clearance'), f'{group} clearance', minimum=0)
    gut = _finite_number(row.get('gut_occupation'), f'{group} gut_occupation', minimum=0, strict_minimum=True)
    expected_units = 'm2/gDW/d' if group == 'BEN' else 'm3/gDW/d'
    if row.get('clearance_units', expected_units) != expected_units:
        raise ValueError(f'UNIT_MISMATCH: {group} clearance must use {expected_units}')
    return target, suffix, clearance, gut


def _clear_family(params: dict[str, Any], coupling: dict[str, Any], group: str) -> None:
    count, port, suffix, clearance, gut = FISH_FAMILIES[group]
    params.pop(count, None)
    for mapping, prefixes in ((coupling, (port,)), (params, tuple(p for p in (suffix, clearance, gut) if p))):
        for key in list(mapping):
            if any(re.fullmatch(re.escape(prefix) + r'\d+', key) for prefix in prefixes):
                mapping.pop(key)


_MANUAL_PREY_OVERRIDE = re.compile(r'^(?:plankton|benthos|fish)_[DNPC]_Food\d+$')


def compile_fish_diet(instance: dict[str, Any], groups: dict[str, list[dict[str, Any]]], target_catalog: dict[str, Any] | None = None, *, remove_overrides: list[str] | tuple[str, ...] = ()) -> dict[str, Any]:
    """Compile fish diets. target_catalog maps instance names to actual model/state/unit contracts."""
    result = deepcopy(instance)
    if result.get('model') != 'wet/fish':
        raise ValueError('INVALID_MODEL: fish diet configuration requires wet/fish consumer')
    params, coupling = _mapping(result)
    if not isinstance(groups, dict) or set(groups) != set(FISH_FAMILIES):
        raise ValueError('INVALID_DOCUMENT: groups must contain PLAN, BEN and PISC')
    if not isinstance(remove_overrides, (list, tuple)) or any(not isinstance(key, str) for key in remove_overrides):
        raise ValueError('INVALID_DOCUMENT: remove_overrides must list exact coupling keys')
    requested_removals = set(remove_overrides)
    overrides = {key for key in coupling if _MANUAL_PREY_OVERRIDE.fullmatch(key)}
    unapproved = overrides - requested_removals
    if unapproved:
        raise ValueError('MANUAL_OVERRIDE_CONFLICT: ' + ', '.join(sorted(unapproved)))
    for key in requested_removals:
        if key not in overrides:
            raise ValueError(f'UNKNOWN_PORT: requested override removal {key} is not a known fish prey override')
        coupling.pop(key)
    own_name = result.get('name')
    for group, (count_name, model_port, suffix_param, clearance_param, gut_param) in FISH_FAMILIES.items():
        rows = groups[group]
        if not isinstance(rows, list):
            raise ValueError(f'INVALID_DOCUMENT: {group} must be a list')
        _clear_family(params, coupling, group)
        params[count_name] = len(rows)
        seen: set[tuple[str, str]] = set()
        for index, row in enumerate(rows, 1):
            target, suffix, clearance, gut = _validate_prey(row, group, target_catalog or {}, seen)
            if own_name and target == own_name:
                raise ValueError(f'DUPLICATE_TARGET: {group} cannot target itself')
            coupling[f'{model_port}{index}'] = target
            params[f'{clearance_param}{index}'] = clearance
            params[f'{gut_param}{index}'] = gut
            if suffix_param and suffix:
                params[f'{suffix_param}{index}'] = suffix
    return result


def compile_zooplankton_diet(instance: dict[str, Any], prey: list[dict[str, Any]], target_catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    result = deepcopy(instance)
    params, coupling = _mapping(result)
    if result.get('model') != 'wet/zooplankton':
        raise ValueError('INVALID_MODEL: zooplankton diet requires wet/zooplankton')
    if not isinstance(prey, list):
        raise ValueError('INVALID_DOCUMENT: prey must be a list')
    original_params = deepcopy(params)
    original_coupling = deepcopy(coupling)
    for mapping, prefixes in ((coupling, ('prey_model',)), (params, ('prey_suffix', 'cClearPrey', 'fGutOccPrey', 'lSi'))):
        for key in list(mapping):
            if any(re.fullmatch(re.escape(prefix) + r'\d+', key) for prefix in prefixes):
                mapping.pop(key)
    params['nPrey'] = len(prey)
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(prey, 1):
        if not isinstance(row, dict):
            raise ValueError('INVALID_TARGET: prey entries must be mappings')
        target = row.get('target')
        suffix = row.get('suffix', '')
        existing_target = original_coupling.get(f'prey_model{index}')
        existing_suffix = original_params.get(f'prey_suffix{index}', '')
        unchanged_out_of_family_target = target == existing_target and suffix == existing_suffix
        info = _target_info(target, 'PLAN', target_catalog or {},
                            allow_out_of_family=unchanged_out_of_family_target)
        if not isinstance(suffix, str) or suffix not in ('', 'W'):
            raise ValueError(f'INVALID_SUFFIX: {suffix!r}')
        identity = (target, suffix)
        if identity in seen:
            raise ValueError(f'DUPLICATE_TARGET: repeated zooplankton prey {target}{suffix}')
        seen.add(identity)
        required = [f's{element}{suffix}' for element in ('D', 'P', 'N', 'C')]
        missing = [state for state in required if state not in info['states']]
        units = info.get('state_units')
        if not isinstance(units, dict) or any(state not in units for state in required):
            raise ValueError(f'INVALID_TARGET: {target} lacks registered units for required states')
        area = '/m2' if suffix == 'S' else '/m3'
        expected_units = {'D': f'gDW{area}', 'P': f'gP{area}', 'N': f'gN{area}', 'C': f'gC{area}'}
        for element, unit in expected_units.items():
            state = f's{element}{suffix}'
            if state in units and units[state] != unit:
                raise ValueError(f'UNIT_MISMATCH: {target}/{state} requires {unit}, got {units[state]}')
        silica = row.get('lSi', False)
        if not isinstance(silica, bool):
            raise ValueError('INVALID_VALUE: lSi must be boolean')
        if silica and f'oSi{suffix}' not in info['states']:
            raise ValueError(f'UNKNOWN_PORT: {target} lacks oSi{suffix} required by lSi{index}')
        if missing:
            raise ValueError(f'UNKNOWN_PORT: {target} missing required states {missing}')
        if row.get('clearance_units', 'm3/gDW/d') != 'm3/gDW/d':
            raise ValueError('UNIT_MISMATCH: zooplankton clearance must use m3/gDW/d')
        params[f'cClearPrey{index}'] = _finite_number(row.get('clearance'), 'zooplankton clearance', minimum=0)
        params[f'fGutOccPrey{index}'] = _finite_number(row.get('gut_occupation'), 'zooplankton gut_occupation', minimum=0, strict_minimum=True)
        params[f'lSi{index}'] = silica
        coupling[f'prey_model{index}'] = target
        if suffix:
            params[f'prey_suffix{index}'] = suffix
    return result


def _validate_stage_parameters(stage: dict[str, Any], q_stage: int) -> dict[str, Any]:
    values = stage.get('parameters', {})
    if not isinstance(values, dict):
        raise ValueError('INVALID_STAGE: parameters must be a mapping')
    allowed = {'cDinit', 'cDfin', 'fResMin', 'fResMax', 'cMortStarv'}
    if q_stage in (1, 3):
        allowed.update({'cDayReprFish', 'fReproFish', 'fGonad', 'cDegg'})
    unknown = set(values) - allowed
    if unknown:
        raise ValueError('INVALID_STAGE: unsupported stage parameters: ' + ', '.join(sorted(unknown)))
    size_keys = {'cDinit', 'cDfin'}
    if q_stage > 0 and not size_keys <= values.keys():
        raise ValueError('INVALID_STAGE: cDinit and cDfin are required for stage coupling')
    if size_keys & values.keys():
        if not size_keys <= values.keys():
            raise ValueError('INVALID_STAGE: cDinit and cDfin must be provided together')
        initial = _finite_number(values['cDinit'], 'cDinit', minimum=0, strict_minimum=True)
        final = _finite_number(values['cDfin'], 'cDfin', minimum=0, strict_minimum=True)
        if final <= initial:
            raise ValueError('INVALID_STAGE: cDfin must be greater than cDinit')
    reserve_keys = {'fResMin', 'fResMax'}
    if reserve_keys & values.keys():
        if not reserve_keys <= values.keys():
            raise ValueError('INVALID_STAGE: fResMin and fResMax must be provided together')
        minimum = _finite_number(values['fResMin'], 'fResMin', minimum=0)
        maximum = _finite_number(values['fResMax'], 'fResMax', minimum=0)
        if maximum > 1 or minimum > 1 or minimum > maximum:
            raise ValueError('INVALID_STAGE: reserve fractions must satisfy 0 <= fResMin <= fResMax <= 1')
    if q_stage in (1, 3):
        if 'cDegg' not in values:
            raise ValueError('INVALID_STAGE: positive cDegg is required for reproductive stages')
        _finite_number(values['cDegg'], 'cDegg', minimum=0, strict_minimum=True)
    return values


def compile_stage_coupling(instance: dict[str, Any], stage: dict[str, Any], target_catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    result = deepcopy(instance)
    if result.get('model') != 'wet/fish':
        raise ValueError('INVALID_MODEL: stage coupling requires wet/fish consumer')
    params, coupling = _mapping(result)
    q_stage = stage.get('qStage')
    if isinstance(q_stage, bool) or not isinstance(q_stage, int) or q_stage not in (0, 1, 2, 3):
        raise ValueError(f'INVALID_STAGE: qStage must be integer 0, 1, 2 or 3')
    stage_parameters = _validate_stage_parameters(stage, q_stage)
    for port in ('juvenile_', 'adult_'):
        for key in list(coupling):
            if key.startswith(port) and key[len(port):] in STAGE_PORTS:
                coupling.pop(key)
    params['qStage'] = q_stage
    stage_parameter_names = ('fResMax', 'fResMin', 'cMortStarv', 'cDinit', 'cDfin',
                             'cDayReprFish', 'fReproFish', 'fGonad', 'cDegg')
    allowed_stage_parameters = set(stage_parameter_names[:5])
    if q_stage in (1, 3):
        allowed_stage_parameters.update(stage_parameter_names[5:])
    if q_stage == 0:
        for key in stage_parameter_names:
            params.pop(key, None)
    else:
        for key in stage_parameter_names:
            if key not in allowed_stage_parameters:
                params.pop(key, None)
    params.update(stage_parameters)
    if q_stage == 0:
        return result
    stages = []
    if q_stage in (1, 3):
        stages.append(('juvenile', stage.get('juvenile')))
    if q_stage in (2, 3):
        stages.append(('adult', stage.get('adult')))
    for prefix, target in stages:
        if not isinstance(target, str) or target == result.get('name') or '/' in target or '\\' in target:
            raise ValueError(f'INVALID_TARGET: {prefix} must be a distinct fish instance model reference')
        info = (target_catalog or {}).get(target)
        if not isinstance(info, dict) or info.get('model') != 'wet/fish':
            raise ValueError(f'INVALID_TARGET: {target} is not a typed wet/fish target')
        target_qstage = info.get('parameters', {}).get('qStage')
        if isinstance(target_qstage, bool) or not isinstance(target_qstage, int) or target_qstage == 0:
            raise ValueError(f'DOMAIN_MISMATCH: {target} must have qStage > 0')
        for suffix, (state, unit) in STAGE_PORTS.items():
            if state not in set(info.get('states') or ()):
                raise ValueError(f'UNKNOWN_PORT: {target} missing required stage state {state}')
            actual_unit = (info.get('state_units') or {}).get(state)
            if actual_unit is None:
                raise ValueError(f'INVALID_TARGET: {target} has no registered unit for {state}')
            if actual_unit != unit:
                raise ValueError(f'UNIT_MISMATCH: {target}/{state} requires {unit}, got {actual_unit}')
            coupling[f'{prefix}_{suffix}'] = f'{target}/{state}'
    return result
