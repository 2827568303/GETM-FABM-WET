"""WET model capability catalogue derived from the checked-in Fortran registrations."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
SOURCE_DIR = APP_DIR.parent / 'src' / 'wet' / 'src'
ECOLOGY = frozenset(('phytoplankton', 'zooplankton', 'zoobenthos', 'bivalves', 'macrophytes', 'fish', 'fish_pclake'))
WATER_QUALITY = frozenset(('abiotic_water', 'abiotic_sediment', 'om_pool', 'sediment_exchange', 'burial', 'bot_pel_interface', 'inorganic_carbon', 'methane'))
SOURCE_BY_FAMILY = {
    'phytoplankton': 'phytoplankton.F90', 'zooplankton': 'zooplankton.F90',
    'fish': 'fish.F90', 'zoobenthos': 'zoobenthos.F90', 'bivalves': 'bivalves.F90',
    'macrophytes': 'macrophytes.F90', 'fish_pclake': 'fish_pclake.F90',
    'abiotic_water': 'abiotic_water.F90', 'abiotic_sediment': 'abiotic_sediment.F90',
    'om_pool': 'om_pool.F90', 'sediment_exchange': 'sediment_exchange.F90',
    'burial': 'burial.F90', 'bot_pel_interface': 'bot_pel_interface.F90',
    'inorganic_carbon': 'inorganic_carbon.F90', 'methane': 'methane.F90',
}
_STATE_RE = re.compile(r"register_state_variable\s*\([^\n]*?,\s*'([^']+)'\s*,\s*'([^']+)'", re.I)
_DIAG_RE = re.compile(r"register_diagnostic_variable\s*\([^\n]*?,\s*'([^']+)'\s*,\s*'([^']+)'", re.I)
_PARAM_RE = re.compile(r"get_parameter\s*\([^\n]*?,\s*'([^']+)'\s*,\s*'([^']+)'[^\n]*?default\s*=\s*([^,)]+)", re.I)
_MODEL_DEP_RE = re.compile(r"register_model_dependency\s*\([^\n]*?,\s*'([^']+)'", re.I)
_STATE_DEP_RE = re.compile(
    r"register_state_dependency\s*\([^,\n]+,\s*'([^']+)'(?!\s*//)\s*,\s*'([^']+)'", re.I)


def classify_model(model: str) -> tuple[str, str]:
    family = model.removeprefix('wet/')
    if model.startswith('wet/') and family in ECOLOGY:
        return 'ecology', family
    if model.startswith('wet/') and family in WATER_QUALITY:
        return 'water_quality', family
    return 'other', model


def validate_new_name(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}', name):
        raise ValueError(f'INVALID_NAME: {name!r}')
    return name


def validate_display_name(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 120 or '\n' in value or '\r' in value:
        raise ValueError('INVALID_DISPLAY_NAME: expected non-empty single-line text of at most 120 characters')
    # Keep parity with the shipped native YAML reader; avoid a duplicate, looser encoder.
    try:
        from lake_points_api import native_yaml_scalar
        native_yaml_scalar(value)
    except ImportError as error:
        raise RuntimeError('native_yaml_scalar is unavailable; display names cannot be validated safely') from error
    except ValueError as error:
        raise ValueError(f'INVALID_DISPLAY_NAME: {error}') from error
    return value


def validate_existing_document(instances: dict[str, Any]) -> None:
    """Validate that legacy YAML is structurally readable without migrating its names."""
    if not isinstance(instances, dict):
        raise ValueError('INVALID_DOCUMENT: instances must be a mapping')
    for name, config in instances.items():
        if not isinstance(name, str) or not name or not isinstance(config, dict):
            raise ValueError(f'INVALID_DOCUMENT: invalid instance entry {name!r}')
        model = config.get('model')
        if not isinstance(model, str) or not model:
            raise ValueError(f'INVALID_DOCUMENT: {name} has no model')


def validate_names(instances: dict[str, Any], disabled: dict[str, Any] | list[str] | set[str], tombstones: dict[str, Any] | list[str] | set[str] | None = None) -> None:
    """Validate proposed new names globally, including disabled/deleted identities."""
    names = set(instances)
    disabled_names = set(disabled)
    tombstone_names = set(tombstones or ())
    overlap = names & (disabled_names | tombstone_names)
    if overlap:
        raise ValueError('DUPLICATE_NAME: ' + ', '.join(sorted(overlap)))
    for name in names:
        validate_new_name(name)


def validate_native_field_names(fields: list[str] | tuple[str, ...]) -> None:
    seen: set[str] = set()
    for field in fields:
        if field in seen:
            raise ValueError(f'NATIVE_FIELD_COLLISION: {field}')
        seen.add(field)


def _canonical_condition(raw: str) -> str:
    value = raw.lower().replace('self%', '').replace('.true.', 'true').strip()
    if 'qstage' in value:
        if 'qstage > 0' in value or 'qstage .gt. 0' in value:
            return 'qStage > 0'
        if ('qstage == 1' in value or 'qstage .eq. 1' in value) and ('qstage == 3' in value or 'qstage .eq. 3' in value):
            return 'qStage in {1,3}'
        if ('qstage == 2' in value or 'qstage .eq. 2' in value) and ('qstage == 3' in value or 'qstage .eq. 3' in value):
            return 'qStage in {2,3}'
        if 'qstage' in value:
            return raw.strip()
    if 'diagnostics' in value:
        return 'diagnostics'
    if 'lsi' in value:
        return 'lSi'
    return raw.strip()


def _active_conditions(source: str) -> dict[int, list[str]]:
    stack: list[str] = []
    result: dict[int, list[str]] = {}
    for line_number, line in enumerate(source.splitlines(), 1):
        code = line.split('!', 1)[0]
        result[line_number] = list(stack)
        match = re.search(r'\bif\s*\((.*?)\)\s*then\b', code, re.I)
        if match:
            stack.append(_canonical_condition(match.group(1)))
        if re.search(r'\bendif\b', code, re.I):
            if stack:
                stack.pop()
    return result


def _condition_at(source: str, offset: int, active: dict[int, list[str]]) -> str | None:
    line_number = source.count('\n', 0, offset) + 1
    conditions = active.get(line_number, [])
    # Report semantic gates that change registered capability; unrelated process branches are omitted.
    for gate in ('qStage > 0', 'qStage in {1,3}', 'qStage in {2,3}', 'diagnostics', 'lSi'):
        if gate in conditions:
            return gate
    return None


def _call_domain(source: str, offset: int, units: str | None = None) -> str:
    opening = source.find('(', offset)
    if opening < 0:
        return 'pelagic'
    depth = 0
    quote = False
    for index in range(opening, len(source)):
        char = source[index]
        if char == "'":
            quote = not quote
        elif not quote and char == '(':
            depth += 1
        elif not quote and char == ')':
            depth -= 1
            if depth == 0:
                call = source[opening:index + 1]
                return 'bottom' if re.search(r'domain\s*=\s*domain_bottom', call, re.I) or (units or '').endswith('/m2') else 'pelagic'
    return 'pelagic'


def _parse_registrations(family: str) -> dict[str, Any]:
    filename = SOURCE_BY_FAMILY.get(family)
    if not filename:
        raise KeyError(f'Unknown WET model family: {family}')
    path = SOURCE_DIR / filename
    if not path.is_file():
        raise RuntimeError(f'Fortran registration source unavailable: {path}')
    source = path.read_text(encoding='utf-8', errors='replace')
    active = _active_conditions(source)
    states: dict[str, Any] = {}
    diagnostics: dict[str, Any] = {}
    for regex, target, kind in ((_STATE_RE, states, 'state'), (_DIAG_RE, diagnostics, 'diagnostic')):
        for match in regex.finditer(source):
            name, units = match.groups()
            target[name] = {
                'units': units.strip(), 'kind': kind,
                'condition': _condition_at(source, match.start(), active),
                'domain': _call_domain(source, match.start(), units.strip()),
                'source': f'3DWET/src/wet/src/{filename}:{source.count(chr(10), 0, match.start()) + 1}',
            }
    parameters = {}
    for match in _PARAM_RE.finditer(source):
        name, units, default = match.groups()
        token = default.replace('_rk', '').strip()
        if token.lower() in ('.true.', '.false.'):
            normalized: Any = token.lower() == '.true.'
        else:
            try:
                normalized = float(token)
                if normalized.is_integer():
                    normalized = int(normalized)
            except ValueError:
                normalized = token
        call_start = source.rfind('get_parameter', 0, match.start())
        call_end = source.find('\n', match.end())
        call_text = source[call_start:call_end if call_end >= 0 else len(source)]
        parameter = {'units': units.strip(), 'default': normalized,
                     'condition': _condition_at(source, match.start(), active),
                     'source': f'3DWET/src/wet/src/{filename}:{source.count(chr(10), 0, match.start()) + 1}'}
        for bound in ('minimum', 'maximum'):
            bound_match = re.search(r'\b' + bound + r'\s*=\s*([^,)]+)', call_text, re.I)
            if bound_match:
                raw = bound_match.group(1).strip().replace('_rk', '')
                try:
                    parameter[bound] = float(raw)
                except ValueError:
                    parameter[bound] = raw
        parameters[name] = parameter
    model_dependencies = sorted(set(_MODEL_DEP_RE.findall(source)))
    state_dependencies = {}
    for match in _STATE_DEP_RE.finditer(source):
        name, units = match.groups()
        state_dependencies[name] = {
            'units': units.strip(),
            'source': f'3DWET/src/wet/src/{filename}:{source.count(chr(10), 0, match.start()) + 1}',
        }
    # True dynamic dependency names are assembled from index strings in Fortran.
    if family == 'fish':
        model_dependencies += ['PLANpreyN', 'BENTpreyN', 'PISCpreyN']
        state_dependencies.update({f'{stage}_{suffix}': {'units': 'g/m3' if suffix != 'Siz' else 'g/ind'}
                                   for stage in ('juvenile', 'adult')
                                   for suffix in ('D', 'N', 'P', 'C', 'Res', 'Siz')})
    if family == 'zooplankton':
        model_dependencies.append('prey_modelN')
    # Registration domain is attached directly to each call, rather than guessed from a variable name.
    for match in _STATE_RE.finditer(source):
        name = match.group(1)
        if name in states:
            states[name]['domain'] = _call_domain(source, match.start(), states[name]['units'])
    return {
        'model': f'wet/{family}', 'family': family, 'source': f'3DWET/src/wet/src/{filename}',
        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'states': states, 'diagnostics': diagnostics, 'parameters': parameters,
        'model_dependencies': sorted(set(model_dependencies)), 'state_dependencies': state_dependencies,
        'dynamic_state_families': _dynamic_state_families(family),
        'stage_coupling': _stage_coupling() if family == 'fish' else None,
        'dynamic_families': _dynamic_families(family),
        'diagnostic_families': _diagnostic_families(family),
    }


def _dynamic_families(family: str) -> dict[str, Any]:
    if family == 'fish':
        return {
            'PLAN': {'count_parameter': 'nPLAN', 'model_port': 'PLANpreyN', 'suffix_parameter': 'PLANprey_suffixN',
                     'clearance_parameter': 'cClearPlanN', 'clearance_units': 'm3/gDW/d', 'gut_parameter': 'fGutOccPlanN',
                     'required_states': ['sD', 'sP', 'sN', 'sC'], 'target_kind': 'model', 'allowed_suffixes': ['W', 'S', '']},
            'BEN': {'count_parameter': 'nBEN', 'model_port': 'BENTpreyN', 'suffix_parameter': 'BENprey_suffixN',
                    'clearance_parameter': 'cClearBentN', 'clearance_units': 'm2/gDW/d', 'gut_parameter': 'fGutOccBentN',
                    'required_states': ['sD', 'sP', 'sN', 'sC', 'sD_PV', 'sP_PV', 'sN_PV', 'sC_PV'],
                    'target_kind': 'model', 'allowed_suffixes': ['S', '']},
            'PISC': {'count_parameter': 'nPISC', 'model_port': 'PISCpreyN', 'suffix_parameter': None,
                     'clearance_parameter': 'cClearPiscN', 'clearance_units': 'm3/gDW/d', 'gut_parameter': 'fGutOccPiscN',
                     'required_states': ['sD', 'sN', 'sP', 'sC', 'fVul', 'pred_dummy'], 'target_kind': 'model', 'allowed_suffixes': ['']},
        }
    if family == 'zooplankton':
        return {'prey': {'count_parameter': 'nPrey', 'model_port': 'prey_modelN', 'suffix_parameter': 'prey_suffixN',
                         'clearance_parameter': 'cClearPreyN', 'clearance_units': 'm3/gDW/d', 'gut_parameter': 'fGutOccPreyN',
                         'silica_parameter': 'lSiN', 'required_states': ['sD', 'sP', 'sN', 'sC'],
                         'silica_state': 'oSi', 'target_kind': 'model', 'allowed_suffixes': ['W', 'S', '']}}
    return {}


def _diagnostic_families(family: str) -> dict[str, Any]:
    if family == 'fish':
        return {
            'PLAN': {'name_pattern': 't{D,P,N,C}ConsFiPlan_N', 'condition': 'diagnostics and nPLAN >= N', 'domain': 'pelagic'},
            'BEN': {'name_pattern': 't{D,P,N,C}ConsFiBent_N', 'condition': 'nBEN >= N', 'domain': 'bottom'},
            'PISC': {'name_pattern': 't{D,P,N,C}ConsFiPisc_N', 'condition': 'diagnostics and nPISC >= N', 'domain': 'pelagic'},
        }
    if family == 'zooplankton':
        return {'prey': {'name_pattern': 'w{D,P,N,C}ConsZoo_N', 'condition': 'diagnostics and nPrey >= N', 'domain': 'pelagic'}}
    return {}


def _dynamic_state_families(family: str) -> dict[str, Any]:
    if family == 'fish':
        return {
            'PLAN': {'consumer_ports': ['plankton_D_FoodN', 'plankton_N_FoodN', 'plankton_P_FoodN', 'plankton_C_FoodN'],
                     'target_ports': ['sD+PLANprey_suffixN', 'sN+PLANprey_suffixN', 'sP+PLANprey_suffixN', 'sC+PLANprey_suffixN'],
                     'source': '3DWET/src/wet/src/fish.F90:256-259'},
            'BEN': {'consumer_ports': ['benthos_D_FoodN', 'benthos_N_FoodN', 'benthos_P_FoodN', 'benthos_C_FoodN',
                                       'benthos_D_FoodN_PV', 'benthos_N_FoodN_PV', 'benthos_P_FoodN_PV', 'benthos_C_FoodN_PV'],
                    'target_ports': ['sD+BENprey_suffixN', 'sN+BENprey_suffixN', 'sP+BENprey_suffixN', 'sC+BENprey_suffixN',
                                     'sD+BENprey_suffixN+_PV', 'sN+BENprey_suffixN+_PV', 'sP+BENprey_suffixN+_PV', 'sC+BENprey_suffixN+_PV'],
                    'source': '3DWET/src/wet/src/fish.F90:295-306'},
            'PISC': {'consumer_ports': ['fish_D_FoodN', 'fish_N_FoodN', 'fish_P_FoodN', 'fish_C_FoodN', 'fVulPiscN', 'pred_dummyN'],
                     'target_ports': ['sD', 'sN', 'sP', 'sC', 'fVul', 'pred_dummy'],
                     'consumer_units': {'pred_dummyN': '-'},
                     'target_units': {'pred_dummy': '-'},
                     'unit_contract_status': 'compatible-native-registration',
                     'source': '3DWET/src/wet/src/fish.F90:339-352'},
        }
    if family == 'zooplankton':
        return {'prey': {'consumer_ports': ['Prey_D_N', 'Prey_N_N', 'Prey_P_N', 'Prey_C_N', 'Prey_Si_N'],
                         'target_ports': ['sD+prey_suffixN', 'sN+prey_suffixN', 'sP+prey_suffixN', 'sC+prey_suffixN', 'oSi+prey_suffixN'],
                         'silica_condition': 'lSiN', 'source': '3DWET/src/wet/src/zooplankton.F90:142-156'}}
    return {}


def _stage_coupling() -> dict[str, Any]:
    return {
        'parameter': 'qStage', 'values': {'0': [], '1': ['juvenile'], '2': ['adult'], '3': ['juvenile', 'adult']},
        'states': {'D': 'sD', 'N': 'sN', 'P': 'sP', 'C': 'sC', 'Res': 'sFRes', 'Siz': 'sDSiz'},
        'units': {'D': 'g/m3', 'N': 'g/m3', 'P': 'g/m3', 'C': 'g/m3', 'Res': 'g/m3', 'Siz': 'g/ind'},
        'source': '3DWET/src/wet/src/fish.F90:363-384',
        'note': 'State dependencies are manually coupled; no juvenile_target/adult_target model port is registered because automatic model coupling is circular.',
    }


_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def get_model_schema(model: str) -> dict[str, Any]:
    domain, family = classify_model(model)
    if domain == 'other':
        raise KeyError(f'No WET schema for model: {model}')
    key = f'wet/{family}'
    if key not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[key] = _parse_registrations(family)
    return _SCHEMA_CACHE[key]


def required_registered_dependencies(model: str, parameters: dict[str, Any] | None = None) -> set[str]:
    """Return statically registered state ports active for this model configuration."""
    domain, family = classify_model(model)
    if domain == 'other':
        return set()
    path = SOURCE_DIR / SOURCE_BY_FAMILY[family]
    source = path.read_text(encoding='utf-8', errors='replace')
    active = _active_conditions(source)
    parameters = parameters or {}
    required: set[str] = set()
    offset = 0
    for line_number, line in enumerate(source.splitlines(keepends=True), 1):
        code = line.split('!', 1)[0]
        for match in _STATE_DEP_RE.finditer(code):
            name, units = match.groups()
            # Dynamic indexed registrations have a units literal where a fixed port name
            # would normally appear; their model-specific families are validated elsewhere.
            if name in {'g/m3', 'g/m2', 'g/ind', '-'}:
                continue
            condition = _condition_at(source, offset + match.start(), active)
            enabled = True
            if condition == 'lSi':
                enabled = parameters.get('lSi') is True
            elif condition == 'qStage > 0':
                enabled = isinstance(parameters.get('qStage'), int) and parameters['qStage'] > 0
            elif condition == 'qStage in {1,3}':
                enabled = parameters.get('qStage') in (1, 3)
            elif condition == 'qStage in {2,3}':
                enabled = parameters.get('qStage') in (2, 3)
            if enabled:
                required.add(name)
        offset += len(line)
    return required


def registered_models() -> list[str]:
    return [f'wet/{family}' for family in sorted(ECOLOGY | WATER_QUALITY)]
