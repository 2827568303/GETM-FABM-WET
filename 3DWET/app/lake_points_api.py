"""Case-scoped point helpers and conservative FABM network editing."""
import copy
import hashlib
import json
import math
import os
import re
import shutil
import uuid
from pathlib import Path

import netCDF4 as nc
from netcdf_io import open_dataset
import numpy as np
import yaml
from flask import jsonify, request
import case_model_transaction as case_transactions
from wet_instance_catalog import (classify_model, get_model_schema, required_registered_dependencies,
                                  validate_display_name, validate_new_name)
from wet_foodweb import compile_fish_diet, compile_stage_coupling, compile_zooplankton_diet


POINT_FILES = ('lake_points.json', 'rivers_setup.json', 'rivers.nc')


def native_yaml_scalar(value):
    """Write scalars understood by both PyYAML and the shipped Fortran reader."""
    if isinstance(value, str):
        # The native reader rejects quotes/flow delimiters anywhere on a line.
        # Never save a display name or coupling reference that it cannot read.
        if (not value or value != value.strip() or
                any(ord(char) < 32 or ord(char) == 127 or char in '\"\'[]{}' for char in value)):
            raise ValueError('当前求解器不支持空白边界、换行、控制字符、引号、方括号或花括号，请使用普通单行文本')
        try:
            parsed = yaml.safe_load('value: ' + value + '\n')
        except yaml.YAMLError as error:
            raise ValueError('文本不能直接写入模型配置，请避免注释或映射符号') from error
        if parsed != {'value': value}:
            raise ValueError('文本会被识别为注释、数字、布尔值或映射，请使用普通名称')
        return value
    scalar = json.dumps(value, ensure_ascii=False, allow_nan=False)
    # PyYAML requires a decimal point for an exponent to remain a real scalar.
    if type(value) is float and 'e' in scalar.lower():
        mantissa, exponent = scalar.lower().split('e')
        scalar = (mantissa if '.' in mantissa else mantissa + '.0') + 'e' + exponent
    return scalar


def read_points(path):
    file = path / 'lake_points.json'
    data = json.loads(file.read_text(encoding='utf-8-sig')) if file.exists() else {}
    points = data.get('points', [])
    if not isinstance(points, list):
        raise ValueError('lake_points.json 点位格式无效')
    return points


def effective_calibration_points(context):
    """Return registry clones with saved active-case coordinates (zero based).

    Invalid, ambiguous or missing overrides leave the original registry point
    unchanged. No case switch or unsaved editor session can mutate the registry.
    """
    originals = copy.deepcopy(getattr(context, 'calibration_points', []))
    if not context.active_case_path: return originals
    path = Path(context.active_case_path).resolve()
    try:
        with context._NC_LOCK:
            points = read_points(path)
            grouped = {}
            for point in points:
                if isinstance(point, dict) and point.get('calibration_id'):
                    grouped.setdefault(point['calibration_id'], []).append(point)
            if not grouped: return originals
            config = context.parse_getm_inp(path / 'getm.inp') if (path / 'getm.inp').exists() else {}
            filename = str(config.get('domain', {}).get('bathymetry', 'bathymetry.nc')).strip("'\"")
            file = (path / filename).resolve()
            if not file.is_relative_to(path): return originals
            overrides = {}
            with open_dataset(file) as ds:
                depth = ds['bathymetry']
                if len(depth.shape) != 2: return originals
                ny, nx = depth.shape
                x_axis, y_axis = ds.variables.get('x'), ds.variables.get('y')
                axes_ready = (x_axis is not None and y_axis is not None and
                              x_axis.ndim == y_axis.ndim == 1 and
                              x_axis.shape[0] == nx and y_axis.shape[0] == ny and
                              str(getattr(x_axis, 'units', '')).strip().lower() in {'m', 'meter', 'meters', 'metre', 'metres'} and
                              str(getattr(y_axis, 'units', '')).strip().lower() in {'m', 'meter', 'meters', 'metre', 'metres'})
                for identifier, mappings in grouped.items():
                    if len(mappings) != 1: continue
                    point = mappings[0]
                    i, j = point.get('i'), point.get('j')
                    if type(i) is not int or type(j) is not int or not (1 <= i <= nx and 1 <= j <= ny): continue
                    value = depth[j-1, i-1]
                    if np.ma.is_masked(value) or not math.isfinite(float(value)) or float(value) <= 0: continue
                    x_m = float(x_axis[i-1]) if axes_ready else None
                    y_m = float(y_axis[j-1]) if axes_ready else None
                    if axes_ready and math.isfinite(x_m) and math.isfinite(y_m):
                        overrides[identifier] = (i-1, j-1, point, x_m, y_m)
                    else:
                        overrides[identifier] = (i-1, j-1, point, None, None)
            if not context.active_case_path or Path(context.active_case_path).resolve() != path: return originals
            for point in originals:
                if point.get('id') in overrides:
                    i, j, local, x_m, y_m = overrides[point['id']]
                    point['i'], point['j'] = i, j
                    identity = (local.get('lake_id'), local.get('station_id'),
                                local.get('observation_point_id'))
                    if x_m is not None and y_m is not None and all(isinstance(value, str) and value.strip() for value in identity):
                        point.update(lake_id=identity[0].strip(), station_id=identity[1].strip(),
                                     point_id=identity[2].strip(), spatial_mapping='explicit_cell',
                                     mapping_source='gridstudio_explicit_cell', x_m=x_m, y_m=y_m)
            return originals
    except (ValueError, TypeError, OSError, KeyError, IndexError):
        return originals


def point_command(s, d, calibration):
    """Validate fully before touching the session; coordinates are one based."""
    action = d['action']
    rivers = action.startswith('river_')
    collection = s['rivers'] if rivers else s['points']
    index = d.get('river_index') if rivers else next((i for i, p in enumerate(collection) if p['id'] == d.get('point_id')), None)
    if action.endswith('delete'):
        if type(index) is not int or not 0 <= index < len(collection):
            raise ValueError('请选择一个现有点位')
        return collection, index, None
    cells = d.get('cells')
    ny, nx = s['depth'].shape
    if (not isinstance(cells, list) or len(cells) != 1 or not isinstance(cells[0], list) or len(cells[0]) != 2 or
            any(type(v) is not int for v in cells[0])):
        raise ValueError('点位操作必须选择一个水格')
    i, j = cells[0]
    if not (0 <= i < nx and 0 <= j < ny and s['depth'][j, i] > 0):
        raise ValueError('点位必须位于有效水格')
    if rivers and action == 'river_update' and (type(index) is not int or not 0 <= index < len(collection)):
        raise ValueError('请选择一个现有河流点')
    if not rivers and d.get('point_id') and index is None:
        raise ValueError('点位已不存在，请重新加载')
    name = str(d.get('name', '')).strip()
    if not name or len(name) > 80 or (rivers and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}', name)):
        raise ValueError('名称不能为空；河流名称须以英文字母开头，仅含字母、数字及下划线，最多40字符')
    if any(p['name'].casefold() == name.casefold() for k, p in enumerate(collection) if k != index):
        raise ValueError('点位名称重复')
    kind = d.get('kind', 'signed' if rivers else 'monitor')
    if kind not in (('inflow', 'outflow', 'signed') if rivers else ('monitor', 'source')):
        raise ValueError('未知点位类型')
    item = copy.deepcopy(collection[index]) if index is not None else {}
    item.update(i=i+1, j=j+1, name=name.upper() if rivers else name, kind=kind)
    if rivers:
        item.setdefault('tail', ['-1', '-1'])
        item.setdefault('original_name', None)
    else:
        item.setdefault('id', uuid.uuid4().hex[:12])
        linked = d.get('calibration_id', item.get('calibration_id')) or None
        if linked and not any(p.get('id') == linked for p in calibration):
            raise ValueError('关联的校准点不存在')
        item['calibration_id'] = linked
        for key in ('lake_id', 'station_id', 'observation_point_id'):
            value = d.get(key, item.get(key, ''))
            if not isinstance(value, str) or len(value.strip()) > 200:
                raise ValueError('观测映射身份必须为不超过200字符的文本')
            if value.strip(): item[key] = value.strip()
            else: item.pop(key, None)
    return collection, index, item


def prepare_point_files(path, s, backup_dir):
    """Prepare all ancillary files before replacing any original."""
    temps = {}
    def write_json(name, data):
        temp = backup_dir / (name + '.new')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        temps[path / name] = temp
    write_json('lake_points.json', {'version': 1, 'case_path': str(path), 'points': s['points']})
    meta_file = path / 'rivers_setup.json'
    meta = json.loads(meta_file.read_text(encoding='utf-8-sig')) if meta_file.exists() else {}
    meta['rivers'] = [{k: r[k] for k in ('i', 'j', 'name', 'kind')} for r in s['rivers']]
    write_json('rivers_setup.json', meta)
    forcing = path / 'rivers.nc'
    if forcing.exists():
        temp = backup_dir / 'rivers.new.nc'
        shutil.copy2(forcing, temp)
        with open_dataset(temp, 'r+') as ds:
            # Rename through temporary names, supporting swaps without collisions.
            renames = []
            for river in s['rivers']:
                old, new = river.get('original_name'), river['name']
                if old and old != new:
                    for variable in list(ds.variables):
                        if variable == old or variable.startswith(old + '_'):
                            renames.append((variable, new + variable[len(old):]))
            originals = {old for old, _ in renames}
            if any(new in ds.variables and new not in originals for _, new in renames):
                raise ValueError('河流新名称与已有流量列冲突')
            stages = []
            for old, new in renames:
                stage = 'rename_' + uuid.uuid4().hex
                ds.renameVariable(old, stage); stages.append((stage, new))
            for stage, new in stages:
                ds.renameVariable(stage, new)
            for river in s['rivers']:
                if river['name'] in ds.variables and river['kind'] != 'signed':
                    var = ds[river['name']]
                    values = var[:]
                    var[:] = np.ma.abs(values) * (-1 if river['kind'] == 'outflow' else 1)
        temps[forcing] = temp
    for river in s['rivers']:
        old = river.get('original_name')
        if old:
            draft = path / 'river_drafts' / (old + '.json')
            if draft.exists():
                data = json.loads(draft.read_text(encoding='utf-8-sig'))
                if river['kind'] != 'signed' and 'Q' in data:
                    data['Q'] = [abs(float(q)) * (-1 if river['kind'] == 'outflow' else 1) for q in data['Q']]
                target = draft.with_name(river['name'] + '.json')
                if target != draft and target.exists():
                    raise ValueError('河流新名称与已有流量草稿冲突')
                temp = backup_dir / ('draft-' + uuid.uuid4().hex + '.new')
                temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                temps[target] = temp
                if target != draft: temps[draft] = None
    return temps


def register_lake_points_routes(app, context):
    def active():
        if not context.active_case_path:
            raise ValueError('请先打开案例')
        return Path(context.active_case_path).resolve()

    def load(path, *, recover_pending=True):
        if recover_pending:
            case_transactions.recover_pending(path)
        file = path / 'fabm.yaml'
        source_bytes = file.read_bytes()
        text = source_bytes.decode('utf-8-sig')
        raw = yaml.safe_load(text)
        if not isinstance(raw, dict) or not isinstance(raw.get('instances'), dict):
            raise ValueError('fabm.yaml 缺少有效 instances')
        disabled_file = path / 'fabm_disabled.yaml'
        disabled_text = disabled_file.read_bytes().decode('utf-8-sig') if disabled_file.exists() else ''
        disabled = yaml.safe_load(disabled_text) or {}
        if not isinstance(disabled, dict): raise ValueError('禁用模块文件必须为对象')
        # The sidecar is an instance-name mapping, not a FABM root configuration.
        disabled = disabled.get('instances', disabled)
        if isinstance(raw.get('_disabled'), dict):
            disabled = {**raw['_disabled'], **disabled}
        revision = case_transactions.case_revision(path)
        nodes, edges, targets = [], [], set()
        for name, inst in raw['instances'].items():
            if not isinstance(inst, dict): continue
            for section in ('initialization',):
                targets.update(f'{name}/{p}' for p in (inst.get(section) or {}))
            for port, reference in (inst.get('coupling') or {}).items():
                if isinstance(reference, str):
                    targets.add(reference)
                    source = reference.split('/')[0]
                    if source in raw['instances']:
                        edges.append(dict(source=source, target=name, port=port, reference=reference))
            nodes.append(dict(name=name, long_name=inst.get('long_name', name), model=inst.get('model', ''),
                              enabled=True, parameters=inst.get('parameters') or {}, coupling=inst.get('coupling') or {}))
        for name, inst in disabled.items():
            if isinstance(inst, dict) and name not in raw['instances']:
                nodes.append(dict(name=name, long_name=inst.get('long_name', name), model=inst.get('model', ''), enabled=False, parameters={}, coupling={}))
        result = dict(case_path=str(path), revision=revision, nodes=nodes, edges=edges,
                      targets=sorted(t for t in targets if '/' in t and t.split('/')[0] in raw['instances']))
        return file, text, raw, result

    def node_at(root, keys):
        for key in keys:
            if not isinstance(root, yaml.MappingNode): raise ValueError('只支持现有标量字段')
            matches = [v for k, v in root.value if k.value == key]
            if len(matches) != 1: raise ValueError('字段不存在或重复')
            root = matches[0]
        if not isinstance(root, yaml.ScalarNode) or root.style in ('|', '>'):
            raise ValueError('只支持现有的单行标量字段')
        return root

    def update_candidates(path, raw, text, operations, revision):
        """Build previewable instance edits while preserving bytes outside edited instances."""
        root = yaml.compose(text)
        expected = copy.deepcopy(raw)
        changes = []
        touched = set()
        candidates_to_validate = set()
        initial_splits = []
        output_clone_pairs = []
        sidecar_path = path / '.studio-config' / 'wet_instances.json'
        sidecar = json.loads(sidecar_path.read_text(encoding='utf-8')) if sidecar_path.exists() else {
            'version': 1, 'instances': {}, 'deleted': []}
        newline = '\r\n' if '\r\n' in text else '\n'
        if not isinstance(sidecar, dict) or not isinstance(sidecar.get('instances', {}), dict):
            raise ValueError('INVALID_DOCUMENT: wet_instances sidecar is invalid')
        if not isinstance(sidecar.get('deleted', []), list):
            raise ValueError('INVALID_DOCUMENT: wet_instances deleted records must be a list')

        def assert_available(name):
            if name in expected['instances']:
                raise ValueError(f'DUPLICATE_NAME: {name}')
            disabled_path = path / 'fabm_disabled.yaml'
            if disabled_path.exists():
                disabled_doc = yaml.safe_load(disabled_path.read_bytes().decode('utf-8-sig')) or {}
                disabled_instances = disabled_doc.get('instances', disabled_doc) if isinstance(disabled_doc, dict) else {}
                if isinstance(disabled_instances, dict) and name in disabled_instances:
                    raise ValueError(f'DUPLICATE_NAME: {name} is disabled')
            deleted = sidecar.get('deleted', [])
            if (name in (sidecar.get('instances') or {}) or
                    any(isinstance(item, dict) and item.get('name') == name for item in deleted)):
                raise ValueError(f'DUPLICATE_NAME: {name} is reserved by an instance identity')

        def make_target_catalog():
            catalog = {}
            for target_name, target_config in expected['instances'].items():
                if not isinstance(target_config, dict) or not isinstance(target_config.get('model'), str):
                    continue
                try:
                    schema = get_model_schema(target_config['model'])
                except KeyError:
                    continue
                params = target_config.get('parameters') or {}
                states = {}
                for state_name, state_info in schema.get('states', {}).items():
                    condition = state_info.get('condition')
                    if condition and 'qStage > 0' in condition and not (isinstance(params.get('qStage'), int) and not isinstance(params.get('qStage'), bool) and params['qStage'] > 0):
                        continue
                    states[state_name] = state_info
                catalog[target_name] = {
                    'model': target_config['model'], 'family': schema.get('family'),
                    'parameters': params, 'states': list(states),
                    'state_units': {state: info.get('units') for state, info in states.items()},
                }
            return catalog

        def state_is_active(schema, parameters, state_name):
            # A few registered model ports consumed by other WET modules are
            # exposed as diagnostics rather than prognostic state variables.
            state = schema.get('states', {}).get(state_name) or schema.get('diagnostics', {}).get(state_name)
            if not state:
                return False
            condition = state.get('condition')
            if condition == 'qStage > 0':
                return isinstance(parameters.get('qStage'), int) and not isinstance(parameters.get('qStage'), bool) and parameters['qStage'] > 0
            if condition == 'qStage in {1,3}':
                return parameters.get('qStage') in (1, 3)
            if condition == 'qStage in {2,3}':
                return parameters.get('qStage') in (2, 3)
            if condition == 'lSi':
                return parameters.get('lSi') is True
            return True

        def validate_candidate_instance(instance_name):
            config = expected['instances'].get(instance_name)
            if not isinstance(config, dict) or not isinstance(config.get('model'), str):
                raise ValueError(f'INVALID_TARGET: candidate instance {instance_name!r} has no registered model')
            schema = get_model_schema(config['model'])
            parameters = config.get('parameters') or {}
            coupling = config.get('coupling') or {}
            if not isinstance(parameters, dict) or not isinstance(coupling, dict):
                raise ValueError(f'INVALID_DOCUMENT: {instance_name} parameters and coupling must be mappings')
            required = required_registered_dependencies(config['model'], parameters)
            for group in schema.get('dynamic_families', {}).values():
                count = parameters.get(group.get('count_parameter'), 0)
                model_port = group.get('model_port')
                if isinstance(count, int) and not isinstance(count, bool) and count > 0 and model_port:
                    for index in range(1, count + 1):
                        required.add(model_port[:-1] + str(index) if model_port.endswith('N') else f'{model_port}{index}')
            missing = required - set(coupling)
            if missing:
                raise ValueError(f'MISSING_REGISTERED_DEPENDENCY: {instance_name} is missing required coupling port(s): '
                                 + ', '.join(sorted(missing)) + '; configure each port before running')
            for port, reference in coupling.items():
                if not isinstance(reference, str) or not reference.strip():
                    raise ValueError(f'INVALID_TARGET: {instance_name}/{port} must reference a registered instance or state')
                target_name, separator, state_name = reference.partition('/')
                target = expected['instances'].get(target_name)
                if not isinstance(target, dict):
                    raise ValueError(f'INVALID_TARGET: {instance_name}/{port} references missing instance {target_name!r}')
                if separator:
                    try:
                        target_schema = get_model_schema(target.get('model'))
                    except (KeyError, TypeError):
                        raise ValueError(f'UNVERIFIABLE_TARGET_STATE: {instance_name}/{port} references {reference}; '
                                         'the target model has no local WET state registry')
                    if not state_is_active(target_schema, target.get('parameters') or {}, state_name):
                        raise ValueError(f'UNKNOWN_TARGET_STATE: {instance_name}/{port} references {reference}, but '
                                         f'{state_name!r} is not a registered active state or diagnostic of {target_name}; '
                                         'choose a registered port listed for that target instance')

        def emit_block(name, config):
            lines = []

            def emit_mapping(mapping, indent):
                for key, value in mapping.items():
                    key_scalar = native_yaml_scalar(str(key))
                    pad = ' ' * indent
                    if isinstance(value, dict):
                        if not value:
                            raise ValueError('NATIVE_YAML_UNSUPPORTED: empty generated mappings are not supported')
                        lines.append(f'{pad}{key_scalar}:')
                        emit_mapping(value, indent + 2)
                    elif isinstance(value, (list, tuple)):
                        raise ValueError('NATIVE_YAML_UNSUPPORTED: generated sequences are not supported')
                    else:
                        lines.append(f'{pad}{key_scalar}: {native_yaml_scalar(value)}')

            emit_mapping({name: config}, 2)
            return newline.join(lines)

        def existing_instance_block(name):
            """Retain the exact original block for lossless delete/restore cycles."""
            instance_nodes = [value for key, value in root.value if key.value == 'instances']
            if len(instance_nodes) != 1 or not isinstance(instance_nodes[0], yaml.MappingNode):
                return None
            matches = [(key, value) for key, value in instance_nodes[0].value if key.value == name]
            if len(matches) != 1:
                return None
            key_node, value_node = matches[0]
            start = text.rfind('\n', 0, key_node.start_mark.index) + 1
            end = value_node.end_mark.index
            while end > key_node.start_mark.index and text[end - 1].isspace():
                end -= 1
            return text[start:end]

        raw_new_blocks = {}
        automatic_integrations = []

        def integrate_phytoplankton_clone(clone_name):
            phytoplankton = [name for name, config in expected['instances'].items()
                             if isinstance(config, dict) and config.get('model') == 'wet/phytoplankton']
            for module_name, module_config in list(expected['instances'].items()):
                if not isinstance(module_config, dict):
                    continue
                model = module_config.get('model')
                if model not in ('wet/burial', 'wet/inorganic_carbon'):
                    continue
                family = model.removeprefix('wet/')
                parameters = module_config.get('parameters') or {}
                coupling = module_config.get('coupling') or {}
                if not isinstance(parameters, dict) or not isinstance(coupling, dict):
                    raise ValueError(
                        f'PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT: {family} instance {module_name!r} '
                        'must have mapping-valued parameters and coupling; repair it before cloning')
                count = parameters.get('nPHYT')
                indexed_prefixes = ('POM_phytoplankton_update',) if family == 'burial' else (
                    'CO2_uptake_water_', 'CO2_respiration_water_')
                if type(count) is not int or count != len(phytoplankton):
                    raise ValueError(
                        f'PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT: {family} instance {module_name!r} '
                        f'has nPHYT={count!r}, but the case has {len(phytoplankton)} active phytoplankton '
                        'instances; reconcile nPHYT and the active algae before cloning')
                if count >= 9:
                    raise ValueError(
                        f'PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT: {family} instance {module_name!r} '
                        'already uses all nine indexed phytoplankton ports supported by the WET Fortran registration')
                if family == 'burial':
                    indexed_groups = {'POM_phytoplankton_update': 'tDPOMS'}
                else:
                    indexed_groups = {'CO2_uptake_water_': 'wCO2UptW',
                                      'CO2_respiration_water_': 'wCO2RespW'}
                malformed = []
                for prefix, state in indexed_groups.items():
                    valid_references = {f'{name}/{state}' for name in phytoplankton}
                    references = [coupling.get(f'{prefix}{index}') for index in range(1, count + 1)]
                    if any(reference not in valid_references for reference in references) or len(set(references)) != count:
                        malformed.extend((f'{prefix}{index}', references[index - 1])
                                         for index in range(1, count + 1))
                extra = []
                for port in coupling:
                    for prefix in indexed_prefixes:
                        suffix = port[len(prefix):] if port.startswith(prefix) else ''
                        if suffix.isdigit() and int(suffix) > count:
                            extra.append(port)
                            break
                if malformed or extra:
                    details = ', '.join(f'{port} references {reference!r}' for port, reference in malformed)
                    if extra:
                        details += ('; ' if details else '') + 'unexpected indexed port(s): ' + ', '.join(sorted(extra))
                    raise ValueError(
                        f'PHYTOPLANKTON_MULTIPLEXER_INCONSISTENT: {family} instance {module_name!r} '
                        f'has inconsistent nPHYT couplings ({details}); repair the indexed couplings before cloning')
                next_index = count + 1
                parameters['nPHYT'] = next_index
                if family == 'burial':
                    coupling[f'POM_phytoplankton_update{next_index}'] = f'{clone_name}/tDPOMS'
                else:
                    coupling[f'CO2_uptake_water_{next_index}'] = f'{clone_name}/wCO2UptW'
                    coupling[f'CO2_respiration_water_{next_index}'] = f'{clone_name}/wCO2RespW'
                module_config['parameters'] = parameters
                module_config['coupling'] = coupling
                touched.add(module_name)
                automatic_integrations.append(family)

        for operation in operations:
            if not isinstance(operation, dict):
                raise ValueError('INVALID_DOCUMENT: each operation must be an object')
            op = operation.get('op')
            if op == 'add':
                unknown = set(operation) - {'op', 'name', 'model', 'long_name', 'parameters', 'initialization', 'coupling'}
                if unknown:
                    raise ValueError('INVALID_DOCUMENT: unsupported add fields ' + ', '.join(sorted(unknown)))
                name = validate_new_name(operation.get('name'))
                assert_available(name)
                model = operation.get('model')
                domain, _ = classify_model(model) if isinstance(model, str) else ('other', '')
                if domain == 'other':
                    raise ValueError(f'INVALID_MODEL: {model!r}')
                schema = get_model_schema(model)
                template = next((value for value in expected['instances'].values()
                                 if isinstance(value, dict) and value.get('model') == model), None)
                if template is None:
                    raise ValueError(
                        f'NO_COMPATIBLE_TEMPLATE: no configured instance of {model} exists in this case; '
                        'add a validated instance of this model family first, then use it as the template')
                if schema.get('state_dependencies') and not template.get('coupling'):
                    raise ValueError(
                        f'NO_COMPATIBLE_TEMPLATE: the existing {model} instance has no registered dependencies; '
                        'configure a complete instance of this model family before adding another')
                config = copy.deepcopy(template)
                config['model'] = model
                config['long_name'] = validate_display_name(operation.get('long_name', name))
                parameters = operation.get('parameters', {})
                initialization = operation.get('initialization', {})
                coupling = operation.get('coupling', {})
                if not all(isinstance(value, dict) for value in (parameters, initialization, coupling)):
                    raise ValueError('INVALID_DOCUMENT: parameters, initialization and coupling must be objects')
                unknown_parameters = set(parameters) - set(schema.get('parameters', {}))
                unknown_states = set(initialization) - set(schema.get('states', {}))
                if unknown_parameters:
                    raise ValueError('UNKNOWN_PORT: unknown parameters ' + ', '.join(sorted(unknown_parameters)))
                if unknown_states:
                    raise ValueError('UNKNOWN_PORT: unknown initialization states ' + ', '.join(sorted(unknown_states)))
                for section, values in (('parameters', parameters), ('initialization', initialization), ('coupling', coupling)):
                    if values:
                        config[section] = {**copy.deepcopy(config.get(section) or {}), **copy.deepcopy(values)}
                final_parameters = config.get('parameters') or {}
                final_coupling = config.get('coupling') or {}
                missing_dependencies = required_registered_dependencies(model, final_parameters) - set(final_coupling)
                for group in schema.get('dynamic_families', {}).values():
                    count_parameter = group.get('count_parameter')
                    count = final_parameters.get(count_parameter, 0)
                    model_port = group.get('model_port')
                    if isinstance(count, int) and not isinstance(count, bool) and count > 0 and model_port:
                        for index in range(1, count + 1):
                            port = model_port[:-1] + str(index) if model_port.endswith('N') else f'{model_port}{index}'
                            if port not in final_coupling:
                                missing_dependencies.add(port)
                if missing_dependencies:
                    raise ValueError('INVALID_TEMPLATE: configured model is missing registered dependencies: '
                                     + ', '.join(sorted(missing_dependencies)))
                # A template must still resolve every existing external dependency in the proposed case.
                for port, reference in (config.get('coupling') or {}).items():
                    if not isinstance(reference, str) or not reference:
                        raise ValueError(f'INVALID_TEMPLATE: {model} coupling {port} is empty or invalid')
                    target_name = reference.split('/', 1)[0]
                    if target_name not in expected['instances']:
                        raise ValueError(f'INVALID_TEMPLATE: {model} coupling {port} references missing instance {target_name}')
                expected['instances'][name] = config
                candidates_to_validate.add(name)
                sidecar.setdefault('instances', {})[name] = {
                    'id': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{revision}:{name}')), 'template': model}
                continue
            name = operation.get('name')
            if op == 'clone':
                unknown = set(operation) - {'op', 'source', 'name', 'long_name', 'initial_fraction'}
                if unknown:
                    raise ValueError('INVALID_DOCUMENT: unsupported clone fields ' + ', '.join(sorted(unknown)))
                source = operation.get('source')
                source_config = expected['instances'].get(source)
                if not isinstance(source_config, dict):
                    raise ValueError(f'INVALID_TARGET: unknown clone source {source!r}')
                new_name = validate_new_name(operation.get('name'))
                assert_available(new_name)
                clone = copy.deepcopy(source_config)
                fraction = operation.get('initial_fraction')
                if 'initial_fraction' in operation and (isinstance(fraction, bool) or
                        not isinstance(fraction, (int, float)) or not math.isfinite(fraction) or not 0 < fraction < 1):
                    raise ValueError('INVALID_INITIAL_FRACTION: fraction must be finite and strictly between 0 and 1 so both cohorts receive a positive share')
                try:
                    clone_schema = get_model_schema(clone.get('model'))
                except (KeyError, TypeError) as error:
                    raise ValueError(f'INVALID_MODEL: clone source {source!r} has no registered WET schema') from error
                if not isinstance(clone.get('parameters', {}), dict) or not isinstance(clone.get('initialization', {}), dict):
                    raise ValueError('INVALID_DOCUMENT: clone source parameters and initialization must be mappings')
                unknown_parameters = set(clone.get('parameters', {})) - set(clone_schema.get('parameters', {}))
                unknown_states = set(clone.get('initialization', {})) - set(clone_schema.get('states', {}))
                if unknown_parameters:
                    raise ValueError('UNKNOWN_PORT: clone source has unregistered parameters ' + ', '.join(sorted(unknown_parameters)))
                if unknown_states:
                    raise ValueError('UNKNOWN_PORT: clone source has unregistered initialization states ' + ', '.join(sorted(unknown_states)))
                if 'initial_fraction' in operation:
                    initialization = clone.get('initialization') or {}
                    states = clone_schema.get('states', {})
                    if not states or set(initialization) != set(states):
                        missing = sorted(set(states) - set(initialization))
                        extra = sorted(set(initialization) - set(states))
                        raise ValueError('INITIAL_SPLIT_UNAVAILABLE: every registered state must have an explicitly declared initial value; '
                                         f'missing={missing}, extra={extra}')
                    split_values = {}
                    for state_name, original_value in initialization.items():
                        state = states[state_name]
                        if state.get('condition') is not None or state.get('units') not in ('gDW/m3', 'gN/m3', 'gP/m3', 'gC/m3',
                                                                                          'gDW/m2', 'gN/m2', 'gP/m2', 'gC/m2'):
                            raise ValueError(f'INITIAL_SPLIT_UNAVAILABLE: {state_name} has conditional or unsupported units '
                                             f'{state.get("units")!r}; only registered mass concentrations can be split')
                        try:
                            if isinstance(original_value, bool) or not isinstance(original_value, (int, float, str)) or not str(original_value).strip():
                                raise ValueError
                            numeric_value = float(original_value)
                            if not math.isfinite(numeric_value):
                                raise ValueError
                        except (ValueError, TypeError, OverflowError):
                            raise ValueError(f'INITIAL_SPLIT_UNAVAILABLE: {state_name} is not a finite numeric initialization value')
                        clone_value = numeric_value * float(fraction)
                        source_value = numeric_value - clone_value
                        if not math.isfinite(clone_value) or not math.isfinite(source_value):
                            raise ValueError(f'INITIAL_SPLIT_UNAVAILABLE: split of {state_name} is not finite')
                        split_values[state_name] = clone_value
                        expected['instances'][source].setdefault('initialization', {})[state_name] = source_value
                        changes.append((['instances', source, 'initialization', state_name], source_value))
                    clone['initialization'] = split_values
                    initial_splits.append({'source': source, 'clone': new_name,
                                           'fraction_to_clone': float(fraction), 'states': sorted(split_values)})
                if 'long_name' in operation:
                    clone['long_name'] = validate_display_name(operation['long_name'])
                # A clone's self-references point to the clone; external edges stay intact.
                for section in ('coupling',):
                    for key, value in list((clone.get(section) or {}).items()):
                        if value == source:
                            clone[section][key] = new_name
                        elif isinstance(value, str) and value.startswith(source + '/'):
                            clone[section][key] = new_name + value[len(source):]
                if clone.get('model') == 'wet/phytoplankton':
                    integrate_phytoplankton_clone(new_name)
                expected['instances'][new_name] = clone
                output_clone_pairs.append((source, new_name, set(clone_schema.get('states', {}))))
                candidates_to_validate.add(new_name)
                sidecar.setdefault('instances', {})[new_name] = {
                    'id': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{revision}:{new_name}')),
                    'template': clone.get('model')}
                continue
            if op == 'rename':
                unknown = set(operation) - {'op', 'name', 'new_name'}
                if unknown:
                    raise ValueError('INVALID_DOCUMENT: unsupported rename fields ' + ', '.join(sorted(unknown)))
                old_name = operation.get('name')
                new_name = validate_new_name(operation.get('new_name'))
                config = expected['instances'].get(old_name)
                if not isinstance(config, dict):
                    raise ValueError(f'INVALID_TARGET: unknown enabled instance {old_name!r}')
                if new_name != old_name:
                    assert_available(new_name)
                    expected['instances'][new_name] = expected['instances'].pop(old_name)
                    if old_name in candidates_to_validate:
                        candidates_to_validate.discard(old_name)
                        candidates_to_validate.add(new_name)
                    for consumer_name, consumer in expected['instances'].items():
                        if not isinstance(consumer, dict):
                            continue
                        coupling = consumer.get('coupling') or {}
                        for port, reference in list(coupling.items()):
                            if reference == old_name:
                                coupling[port] = new_name
                                if consumer_name in raw['instances']:
                                    changes.append((['instances', consumer_name, 'coupling', port], new_name))
                            elif isinstance(reference, str) and reference.startswith(old_name + '/'):
                                coupling[port] = new_name + reference[len(old_name):]
                                if consumer_name in raw['instances']:
                                    changes.append((['instances', consumer_name, 'coupling', port], coupling[port]))
                    identity = sidecar.setdefault('instances', {}).pop(old_name, None)
                    if identity is not None:
                        sidecar['instances'][new_name] = identity
                continue
            if op == 'delete':
                unknown = set(operation) - {'op', 'name'}
                if unknown:
                    raise ValueError('INVALID_DOCUMENT: unsupported delete fields ' + ', '.join(sorted(unknown)))
                target_name = operation.get('name')
                config = expected['instances'].get(target_name)
                if not isinstance(config, dict):
                    raise ValueError(f'INVALID_TARGET: unknown enabled instance {target_name!r}')
                incoming = [(consumer_name, port) for consumer_name, consumer in expected['instances'].items()
                            if consumer_name != target_name and isinstance(consumer, dict)
                            for port, reference in (consumer.get('coupling') or {}).items()
                            if isinstance(reference, str) and
                            (reference == target_name or reference.startswith(target_name + '/'))]
                if incoming:
                    references = ', '.join(f'{consumer}/{port}' for consumer, port in incoming)
                    raise ValueError(f'INSTANCE_IN_USE: {target_name!r} is referenced by {references}; remove or rewire those couplings first')
                identity = sidecar.setdefault('instances', {}).pop(target_name, None)
                if identity is not None and not isinstance(identity, dict):
                    raise ValueError(f'INVALID_DOCUMENT: instance identity for {target_name!r} is invalid')
                if identity is None:
                    identity = {'id': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{revision}:{target_name}')),
                                'template': config.get('model')}
                sidecar['deleted'].append({
                    'id': identity.get('id') or str(uuid.uuid5(uuid.NAMESPACE_URL, f'{revision}:{target_name}')),
                    'name': target_name,
                    'template': identity.get('template', config.get('model')),
                    'config': copy.deepcopy(config),
                    'yaml_block': existing_instance_block(target_name) or emit_block(target_name, config),
                })
                del expected['instances'][target_name]
                continue
            if op == 'restore':
                unknown = set(operation) - {'op', 'name'}
                if unknown:
                    raise ValueError('INVALID_DOCUMENT: unsupported restore fields ' + ', '.join(sorted(unknown)))
                target_name = operation.get('name')
                if target_name in expected['instances']:
                    raise ValueError(f'DUPLICATE_NAME: {target_name} is already enabled')
                disabled_path = path / 'fabm_disabled.yaml'
                if disabled_path.exists():
                    disabled_doc = yaml.safe_load(disabled_path.read_bytes().decode('utf-8-sig')) or {}
                    disabled_instances = disabled_doc.get('instances', disabled_doc) if isinstance(disabled_doc, dict) else {}
                    if isinstance(disabled_instances, dict) and target_name in disabled_instances:
                        raise ValueError(f'DUPLICATE_NAME: {target_name} is disabled')
                record_index = next((index for index, record in enumerate(sidecar['deleted'])
                                     if isinstance(record, dict) and record.get('name') == target_name), None)
                if record_index is None:
                    raise ValueError(f'INVALID_TARGET: no deleted instance named {target_name!r}')
                record = sidecar['deleted'][record_index]
                config = record.get('config')
                if not isinstance(config, dict) or not isinstance(config.get('model'), str):
                    raise ValueError(f'INVALID_DOCUMENT: deleted instance {target_name!r} has no restorable model config')
                expected['instances'][target_name] = copy.deepcopy(config)
                sidecar.setdefault('instances', {})[target_name] = {
                    'id': record.get('id'), 'template': record.get('template', config.get('model'))}
                raw_block = record.get('yaml_block')
                if isinstance(raw_block, str) and raw_block:
                    raw_new_blocks[target_name] = raw_block
                del sidecar['deleted'][record_index]
                continue
            if op in ('set_foodweb', 'set_stage'):
                allowed_fields = ({'op', 'name', 'groups', 'prey', 'remove_overrides'} if op == 'set_foodweb'
                                  else {'op', 'name', 'qStage', 'juvenile', 'adult', 'parameters'})
                unknown = set(operation) - allowed_fields
                if unknown:
                    raise ValueError(f'INVALID_DOCUMENT: unsupported {op} fields ' + ', '.join(sorted(unknown)))
                target_name = operation.get('name')
                config = expected['instances'].get(target_name)
                if not isinstance(config, dict):
                    raise ValueError(f'INVALID_TARGET: unknown enabled instance {target_name!r}')
                compiler_config = copy.deepcopy(config)
                compiler_config['name'] = target_name
                targets = make_target_catalog()
                if op == 'set_foodweb':
                    if config.get('model') == 'wet/fish':
                        updated = compile_fish_diet(compiler_config, operation.get('groups'), targets,
                                                    remove_overrides=operation.get('remove_overrides', ()))
                    elif config.get('model') == 'wet/zooplankton':
                        updated = compile_zooplankton_diet(compiler_config, operation.get('prey'), targets)
                    else:
                        raise ValueError('INVALID_MODEL: set_foodweb supports wet/fish or wet/zooplankton consumers')
                else:
                    stage = {key: operation[key] for key in ('qStage', 'juvenile', 'adult', 'parameters') if key in operation}
                    updated = compile_stage_coupling(compiler_config, stage, targets)
                updated.pop('name', None)
                expected['instances'][target_name] = updated
                touched.add(target_name)
                continue
            if op != 'update':
                raise ValueError('UNSUPPORTED_OPERATION: supported operations are add, clone, rename, delete, restore, update, set_foodweb and set_stage')
            unknown = set(operation) - {'op', 'name', 'long_name', 'parameters', 'coupling', 'initialization'}
            if unknown:
                raise ValueError('INVALID_DOCUMENT: unsupported update fields ' + ', '.join(sorted(unknown)))
            inst = expected['instances'].get(name)
            if not isinstance(inst, dict):
                raise ValueError(f'INVALID_TARGET: unknown enabled instance {name!r}')
            if 'long_name' in operation:
                value = operation['long_name']
                if not isinstance(value, str) or not value.strip() or len(value) > 120:
                    raise ValueError('INVALID_DISPLAY_NAME: expected 1–120 characters')
                changes.append((['instances', name, 'long_name'], value))
                expected['instances'][name]['long_name'] = value
            for section in ('parameters', 'coupling', 'initialization'):
                values = operation.get(section, {})
                if not isinstance(values, dict):
                    raise ValueError(f'INVALID_DOCUMENT: {section} must be an object')
                for key, value in values.items():
                    original = (inst.get(section) or {}).get(key)
                    if key not in (inst.get(section) or {}):
                        raise ValueError(f'UNKNOWN_PORT: only existing {section} fields can be edited by update')
                    if section == 'coupling':
                        if not isinstance(value, str) or not value:
                            raise ValueError('INVALID_TARGET: coupling must be a non-empty model reference')
                    elif section == 'initialization' or section == 'parameters':
                        if isinstance(original, bool):
                            valid = isinstance(value, bool)
                        elif isinstance(original, (int, float)) and not isinstance(original, bool):
                            valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                        else:
                            valid = isinstance(value, str) and isinstance(original, str)
                        if not valid:
                            raise ValueError('INVALID_VALUE: value must match the existing scalar type and be finite')
                    changes.append((['instances', name, section, key], value))
                    expected['instances'][name][section][key] = value
                    if section == 'coupling' or (section == 'parameters' and key in {
                            'qStage', 'lSi', 'nPrey', 'nPLAN', 'nBEN', 'nPISC'}):
                        candidates_to_validate.add(name)
        for candidate_name in sorted(candidates_to_validate):
            validate_candidate_instance(candidate_name)
        edits = []
        for keys, value in changes:
            if len(keys) >= 2 and keys[1] in touched:
                continue
            node = node_at(root, keys)
            edits.append((node.start_mark.index, node.end_mark.index, native_yaml_scalar(value)))
        if not isinstance(root, yaml.MappingNode):
            raise ValueError('NATIVE_YAML_UNSUPPORTED: root must be a block mapping')
        instance_nodes = [value for key, value in root.value if key.value == 'instances']
        if len(instance_nodes) != 1 or not isinstance(instance_nodes[0], yaml.MappingNode):
            raise ValueError('NATIVE_YAML_UNSUPPORTED: instances key is absent, duplicated or not a block mapping')
        instances_node = instance_nodes[0]
        current_keys = {key.value: (key, value) for key, value in instances_node.value}
        structural = []
        rendered_names = set()
        for old_name, (key_node, value_node) in current_keys.items():
            # PyYAML block-node end marks can include the next sibling's
            # indentation. Stop at the last actual value character so deleting
            # or replacing this node leaves the following mapping level intact.
            value_end = value_node.end_mark.index
            while value_end > key_node.start_mark.index and text[value_end - 1].isspace():
                value_end -= 1
            if old_name not in expected['instances']:
                line_start = text.rfind('\n', 0, key_node.start_mark.index) + 1
                structural.append((line_start, value_end, ''))
            elif old_name in touched:
                line_start = text.rfind('\n', 0, key_node.start_mark.index) + 1
                structural.append((line_start, value_end,
                                   emit_block(old_name, expected['instances'][old_name])))
                rendered_names.add(old_name)
        edited = text
        edits.extend(structural)
        for start, end, replacement in sorted(edits, reverse=True):
            edited = edited[:start] + replacement + edited[end:]
        if not expected['instances']:
            parsed = yaml.safe_load(edited) or {}
            if isinstance(parsed, dict) and parsed.get('instances') is None:
                parsed_root = yaml.compose(edited)
                key_node = next((key for key, _ in parsed_root.value if key.value == 'instances'), None)
                if key_node is not None:
                    colon = edited.find(':', key_node.end_mark.index)
                    if colon >= 0:
                        edited = edited[:colon + 1] + ' {}' + edited[colon + 1:]
        new_names = [name for name in expected['instances'] if name not in current_keys and name not in rendered_names]
        if new_names:
            reparsed = yaml.compose(edited)
            instance_nodes = [value for key, value in reparsed.value if key.value == 'instances']
            instances_node = instance_nodes[0]
            blocks = [raw_new_blocks[name] if name in raw_new_blocks else emit_block(name, expected['instances'][name])
                      for name in new_names]
            # Insert against the structurally edited text, whose offsets may differ.
            if instances_node.flow_style:
                prefix, suffix = edited[:instances_node.start_mark.index], edited[instances_node.end_mark.index:]
                edited = prefix.rstrip() + newline + newline.join(blocks) + suffix
            else:
                insertion = instances_node.end_mark.index
                prefix, suffix = edited[:insertion], edited[insertion:]
                separator = '' if prefix.endswith(('\n', '\r')) else newline
                edited = prefix + separator + newline.join(blocks) + suffix
        if yaml.safe_load(edited) != expected:
            raise ValueError('NATIVE_YAML_UNSUPPORTED: document structure cannot be safely edited')
        bom = b'\xef\xbb\xbf' if (path / 'fabm.yaml').read_bytes().startswith(b'\xef\xbb\xbf') else b''
        candidates = {'fabm.yaml': bom + edited.encode('utf-8')}
        output_path = path / 'output.yaml'
        if output_clone_pairs and output_path.is_file():
            output_text = output_path.read_text(encoding='utf-8-sig')
            # GETM-FABM-WET Flexout permits a bare `source: *` wildcard,
            # which its reader treats as a literal but PyYAML parses as an
            # invalid alias. Replace only for parsing with a same-length
            # placeholder so source marks still index the original text.
            wildcard_positions = set()
            wildcard_pattern = re.compile(
                r'(?m)^([ \t]*-[ \t]*source[ \t]*:[ \t]*)\*(?=[ \t]*(?:\#[^\r\n]*)?\r?$)')

            def preserve_flexout_wildcard(match):
                wildcard_positions.add(match.start() + len(match.group(1)))
                return match.group(1) + 'x'

            output_parse_text = wildcard_pattern.sub(preserve_flexout_wildcard, output_text)
            output_root = yaml.compose(output_parse_text)
            output_nodes = [(value, output_text) for key, value in output_root.value
                            if isinstance(key, yaml.ScalarNode) and key.value == 'output'] if isinstance(output_root, yaml.MappingNode) else []
            variables_node = None
            if len(output_nodes) == 1 and isinstance(output_nodes[0][0], yaml.MappingNode):
                variables_nodes = [value for key, value in output_nodes[0][0].value
                                   if isinstance(key, yaml.ScalarNode) and key.value == 'variables']
                if len(variables_nodes) == 1 and isinstance(variables_nodes[0], yaml.SequenceNode):
                    variables_node = variables_nodes[0]
            if variables_node is not None and not variables_node.flow_style:
                for item in variables_node.value:
                    if isinstance(item, yaml.MappingNode):
                        for key, value in item.value:
                            if (isinstance(key, yaml.ScalarNode) and key.value == 'source' and
                                    isinstance(value, yaml.ScalarNode) and value.start_mark.index in wildcard_positions):
                                value.value = '*'
                selected_names = {value.value for item in variables_node.value
                                  if isinstance(item, yaml.MappingNode)
                                  for key, value in item.value
                                  if isinstance(key, yaml.ScalarNode) and key.value == 'source'
                                  and isinstance(value, yaml.ScalarNode)}
                occupied_output_names = set()
                for item in variables_node.value:
                    if not isinstance(item, yaml.MappingNode):
                        continue
                    source_nodes = [value for key, value in item.value
                                    if isinstance(key, yaml.ScalarNode) and key.value == 'source']
                    name_nodes = [value for key, value in item.value
                                  if isinstance(key, yaml.ScalarNode) and key.value == 'name']
                    if len(source_nodes) == 1 and isinstance(source_nodes[0], yaml.ScalarNode):
                        # For direct variables, `name` is the NetCDF variable
                        # name; wildcard entries use it only as a category label.
                        if not source_nodes[0].value.endswith('*'):
                            output_name = (name_nodes[0].value if len(name_nodes) == 1 and
                                           isinstance(name_nodes[0], yaml.ScalarNode)
                                           else source_nodes[0].value)
                            occupied_output_names.add(output_name)
                additions = []
                for item in variables_node.value:
                    if not isinstance(item, yaml.MappingNode):
                        continue
                    sources = [value for key, value in item.value
                               if isinstance(key, yaml.ScalarNode) and key.value == 'source']
                    if len(sources) != 1 or not isinstance(sources[0], yaml.ScalarNode):
                        continue
                    source_value = sources[0].value
                    for old_name, new_name, state_names in output_clone_pairs:
                        prefix = old_name + '_'
                        if (source_value.startswith(prefix) and
                                source_value[len(prefix):] in state_names):
                            clone_value = new_name + source_value[len(old_name):]
                            if clone_value in selected_names:
                                continue
                            selected_names.add(clone_value)
                            name_nodes = [value for key, value in item.value
                                          if isinstance(key, yaml.ScalarNode) and key.value == 'name']
                            alias_value = None
                            if not source_value.endswith('*'):
                                alias_value = clone_value
                                suffix = 2
                                while alias_value in occupied_output_names:
                                    alias_value = f'{clone_value}_{suffix}'
                                    suffix += 1
                                occupied_output_names.add(alias_value)
                            item_start = output_text.rfind('\n', 0, item.start_mark.index) + 1
                            item_end = item.end_mark.index
                            while item_end > item_start and output_text[item_end - 1].isspace():
                                item_end -= 1
                            block = output_text[item_start:item_end]
                            value_start = sources[0].start_mark.index - item_start
                            value_end = sources[0].end_mark.index - item_start
                            block = block[:value_start] + native_yaml_scalar(clone_value) + block[value_end:]
                            if alias_value is not None and len(name_nodes) == 1 and isinstance(name_nodes[0], yaml.ScalarNode):
                                alias_start = name_nodes[0].start_mark.index - item_start
                                alias_end = name_nodes[0].end_mark.index - item_start
                                block = block[:alias_start] + native_yaml_scalar(alias_value) + block[alias_end:]
                            additions.append(block)
                if additions:
                    insertion = variables_node.end_mark.index
                    prefix, suffix = output_text[:insertion], output_text[insertion:]
                    separator = '' if prefix.endswith(('\n', '\r')) else ('\r\n' if '\r\n' in output_text else '\n')
                    newline = '\r\n' if '\r\n' in output_text else '\n'
                    edited_output = prefix + separator + newline.join(additions) + newline + suffix
                    output_bom = b'\xef\xbb\xbf' if output_path.read_bytes().startswith(b'\xef\xbb\xbf') else b''
                    candidates['output.yaml'] = output_bom + edited_output.encode('utf-8')
        if sidecar != (json.loads(sidecar_path.read_text(encoding='utf-8')) if sidecar_path.exists() else {'version': 1, 'instances': {}, 'deleted': []}):
            candidates['.studio-config/wet_instances.json'] = (json.dumps(sidecar, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        return candidates, automatic_integrations, initial_splits

    @app.get('/api/model/instances')
    def model_instances():
        with context._NC_LOCK:
            try:
                path = active()
                _, _, raw, _ = load(path)
                domain = request.args.get('domain', 'all')
                if domain not in ('all', 'ecology', 'water_quality'):
                    return jsonify(error='INVALID_DOMAIN'), 400
                instances = []
                for name, config in raw['instances'].items():
                    if not isinstance(config, dict):
                        continue
                    actual_domain, family = classify_model(config.get('model', ''))
                    if domain not in ('all', actual_domain):
                        continue
                    instances.append({'name': name, 'long_name': config.get('long_name', name),
                                      'model': config.get('model'), 'family': family,
                                      'domain': actual_domain, 'enabled': True,
                                      'parameters': config.get('parameters') or {},
                                      'initialization': config.get('initialization') or {},
                                      'coupling': config.get('coupling') or {}})
                sidecar_path = path / '.studio-config' / 'wet_instances.json'
                sidecar = json.loads(sidecar_path.read_text(encoding='utf-8')) if sidecar_path.exists() else {}
                deleted = []
                for record in sidecar.get('deleted', []):
                    if not isinstance(record, dict) or not isinstance(record.get('config'), dict):
                        continue
                    config = record['config']
                    actual_domain, family = classify_model(config.get('model', ''))
                    deleted.append({'id': record.get('id'), 'name': record.get('name'),
                                    'long_name': config.get('long_name', record.get('name')),
                                    'model': config.get('model'), 'family': family,
                                    'domain': actual_domain, 'enabled': False})
                deleted_records = sidecar.get('deleted', [])
                if not isinstance(deleted_records, list):
                    raise ValueError('INVALID_DOCUMENT: wet_instances deleted records must be a list')
                return jsonify(case_path=str(path), revision=case_transactions.case_revision(path), instances=instances,
                               edges=[], templates=[], deleted=deleted, targets=[])
            except (ValueError, TypeError, OSError, yaml.YAMLError) as error:
                return jsonify(error=str(error)), 400

    @app.post('/api/model/instances/transaction')
    def model_instances_transaction():
        with context._NC_LOCK:
            try:
                path = active()
                data = request.get_json() or {}
                if data.get('case_path') != str(path):
                    return jsonify(error='CASE_CHANGED'), 409
                if context._case_in_use(path):
                    return jsonify(error='CASE_RUNNING'), 409
                _, text, raw, _ = load(path)
                current_revision = case_transactions.case_revision(path)
                if data.get('revision') != current_revision:
                    return jsonify(error='STALE_REVISION', revision=current_revision), 409
                operations = data.get('operations')
                if not isinstance(operations, list) or not operations:
                    return jsonify(error='INVALID_DOCUMENT: operations must be a non-empty list'), 400
                candidates, integrations, initial_splits = update_candidates(path, raw, text, operations, current_revision)
                solver_path = getattr(context, 'EXE_PATH', None)
                solver_hash = hashlib.sha256(Path(solver_path).read_bytes()).hexdigest() if solver_path and Path(solver_path).is_file() else ''
                preview = case_transactions.preview_hash(current_revision, operations, candidates, solver_hash)
                if data.get('mode') == 'preview':
                    return jsonify(case_path=str(path), revision=current_revision, preview_hash=preview,
                                   changes=operations, warnings=[], solver_sha256=solver_hash,
                                   candidate_validation='source_registry', integrations=integrations,
                                   initial_split=initial_splits[0] if initial_splits else None)
                if data.get('mode') != 'apply':
                    return jsonify(error='INVALID_MODE'), 400
                if data.get('preview_hash') != preview:
                    return jsonify(error='PREVIEW_MISMATCH', preview_hash=preview), 409
                backup = case_transactions.commit_files(path, candidates, operations=operations, expected_revision=current_revision)
                _, _, _, result = load(path)
                if hasattr(context, 'cached_fabm_info') and hasattr(context, 'parse_fabm_yaml'):
                    context.cached_fabm_info = context.parse_fabm_yaml(path / 'fabm.yaml')
                return jsonify(**result, backup=backup, preview_hash=preview, changes=operations,
                               solver_sha256=solver_hash,
                               warnings=[], candidate_validation='source_registry', integrations=integrations,
                               initial_split=initial_splits[0] if initial_splits else None)
            except RuntimeError as error:
                return jsonify(error=str(error)), 409
            except (ValueError, TypeError, OSError, KeyError, yaml.YAMLError) as error:
                return jsonify(error=str(error)), 400

    @app.route('/api/ecology/network', methods=['GET', 'POST'])
    def network():
        with context._NC_LOCK:
            try:
                reference_source = request.args.get('source')
                if reference_source is not None:
                    if request.method != 'GET':
                        return jsonify(error='Erken 配置示例为只读来源'), 405
                    if reference_source != 'erken_reference':
                        return jsonify(error='未知网络示例来源'), 404
                    case_root = Path(getattr(context, 'CASE_DIR', '')).resolve()
                    path = (case_root / 'Erken_real_20200101_24h_stage').resolve()
                    if path.parent != case_root or not path.is_dir() or not (path / 'fabm.yaml').is_file():
                        return jsonify(error='固定 Erken 配置示例不可用'), 404
                    pending = path / case_transactions.TRANSACTION_ROOT / 'pending.json'
                    if pending.is_file():
                        return jsonify(error='Erken 配置示例存在未完成事务，拒绝只读显示'), 409
                    _, _, _, result = load(path, recover_pending=False)
                    result['read_only_example'] = 'erken_reference'
                    return jsonify(result)

                path = active()
                file, text, raw, result = load(path)
                if request.method == 'GET': return jsonify(result)
                d = request.get_json() or {}
                if d.get('case_path') != str(path) or context._case_in_use(path) or d.get('revision') != result['revision']:
                    return jsonify(error='案例已切换、配置已更新或模型正在运行，请刷新网络'), 409
                if raw.get('_disabled'):
                    raise ValueError('此配置仍有旧版禁用模块结构，请先在模块配置页面迁移后快捷编辑')
                name = d.get('module')
                inst = raw['instances'].get(name)
                if not isinstance(inst, dict): raise ValueError('只能编辑已启用的现有模块')
                root = yaml.compose(text)
                replacements = []
                expected = copy.deepcopy(raw)
                changes = []
                for section in ('parameters', 'coupling'):
                    values = d.get(section, {})
                    if not isinstance(values, dict): raise ValueError('编辑字段必须为对象')
                    for key, value in values.items():
                        original = (inst.get(section) or {}).get(key)
                        if key not in (inst.get(section) or {}): raise ValueError('仅可编辑现有参数和耦合端口')
                        if section == 'coupling':
                            if value not in result['targets']: raise ValueError('耦合目标必须是当前配置中已登记的有效引用')
                        elif (type(original) is bool and type(value) is not bool or
                              type(original) is int and type(value) is not int or
                              type(original) is float and (type(value) not in (int, float) or not math.isfinite(value)) or
                              type(original) is str and type(value) is not str or
                              type(original) not in (bool, int, float, str)):
                            raise ValueError('参数类型必须匹配，数值必须有限')
                        changes.append((['instances', name, section, key], value))
                        expected['instances'][name][section][key] = value
                if 'long_name' in d:
                    value = d['long_name']
                    if not isinstance(value, str) or not value.strip() or len(value) > 120: raise ValueError('显示名称不能为空且最多120字符')
                    changes.append((['instances', name, 'long_name'], value))
                    expected['instances'][name]['long_name'] = value
                if not changes: raise ValueError('没有可保存的字段')
                for keys, value in changes:
                    node = node_at(root, keys)
                    scalar = native_yaml_scalar(value)
                    replacements.append((node.start_mark.index, node.end_mark.index, scalar))
                edited = text
                for start, end, scalar in sorted(replacements, reverse=True): edited = edited[:start] + scalar + edited[end:]
                if yaml.safe_load(edited) != expected: raise ValueError('配置含共享别名或重复字段，无法安全快捷修改，请使用配置页面')
                bom = b'\xef\xbb\xbf' if file.read_bytes().startswith(b'\xef\xbb\xbf') else b''
                backup = case_transactions.commit_files(path, {'fabm.yaml': bom + edited.encode('utf-8')},
                                      operations=[{'op': 'legacy_network_update', 'module': name}],
                                      expected_revision=result['revision'])
                _, _, _, result = load(path)
                if hasattr(context, 'cached_fabm_info') and hasattr(context, 'parse_fabm_yaml'):
                    context.cached_fabm_info = context.parse_fabm_yaml(file)
                return jsonify(**result, backup=str(backup))
            except RuntimeError as e:
                return jsonify(error=str(e)), 409
            except (ValueError, TypeError, OSError, KeyError, yaml.YAMLError) as e:
                return jsonify(error=str(e)), 400
