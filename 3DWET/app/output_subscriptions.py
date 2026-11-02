"""Resolve conceptual model output selections to native registered field names.

The native GETM field manager registers FABM states as instance_state, while
the ecological configuration uses instance/state paths. Reading this module
never changes a case or opens an output file for writing.
"""
from __future__ import annotations

import difflib
import json
from pathlib import Path
from collections.abc import Mapping

import yaml

HYDRO_CORE = ['temp', 'z', 'D', 'hn']
UNREGISTERED = {'u', 'v', 'elev'}


def _get(context, name, default=None):
    return context.get(name, default) if isinstance(context, Mapping) else getattr(context, name, default)


def _docs(context):
    supplied = _get(context, 'docs')
    if supplied is not None:
        return supplied
    provider = _get(context, '_fabm_docs')
    if callable(provider):
        return provider()
    app_dir = Path(_get(context, 'APP_DIR', Path(__file__).parent))
    try:
        return json.loads((app_dir / 'fabm_docs.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def _instances(case_path):
    path = Path(case_path) / 'fabm.yaml'
    if not path.exists():
        return {}
    try:
        raw = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f'无法读取 fabm.yaml: {exc}') from exc
    if not isinstance(raw, dict) or not isinstance(raw.get('instances', {}), dict):
        raise ValueError('fabm.yaml 的 instances 必须是模型映射')
    return {str(name): inst for name, inst in raw.get('instances', {}).items()
            if isinstance(inst, dict) and inst.get('enabled') is not False}


def _available(case_path, context):
    explicit = _get(context, 'available_sources', _get(context, 'registered_sources'))
    if explicit is not None:
        return list(dict.fromkeys(str(v) for v in explicit))
    in_use = _get(context, '_case_in_use')
    if (callable(in_use) and in_use(Path(case_path))) or _get(context, 'run_status') == 'running':
        return []
    finder = _get(context, 'find_output_files')
    paths = []
    if callable(finder):
        files = finder(Path(case_path)) or {}
        paths = [files.get('3d'), files.get('2d')]
    # Prefer the FABM output manager's output.nc over native hydro files.
    preferred = Path(case_path) / 'output.nc'
    if preferred.exists():
        paths.insert(0, preferred)
    if not paths:
        paths = sorted(Path(case_path).glob('*.3d.nc'))
    opener = _get(context, 'nc_open')
    if opener is None:
        from netcdf_io import open_dataset
        opener = open_dataset
    names = []
    for path in dict.fromkeys(p for p in paths if p):
        try:
            with opener(path) as ds:
                names.extend(ds.variables)
        except (OSError, RuntimeError, ValueError):
            # An old output may be absent, incomplete, or locked by a run.
            continue
    return list(dict.fromkeys(names))


def _inventory(case_path, context):
    available = _available(case_path, context)
    strict_registered = bool(_get(context, 'OUTPUT_SUBSCRIPTION_STRICT_REGISTERED',
                                  _get(context, 'strict_registered_sources', False)))
    docs = _docs(context)
    models = []
    for name, inst in _instances(case_path).items():
        model = str(inst.get('model', ''))
        documented = (docs.get(model) or {}).get('variables', {})
        initialization = inst.get('initialization') or {}
        variables = list(documented) if isinstance(documented, dict) else []
        if isinstance(initialization, dict):
            variables.extend(initialization)
        expected = list(dict.fromkeys(f'{name}_{v}' for v in variables))
        # Existing files may contain diagnostics absent from state docs. Their
        # omission of other fields does not prove those states unregistered:
        # an earlier run may itself have used a restricted subscription.
        observed = [v for v in available if v.startswith(name + '_')]
        # A previous successful output is the runtime's authoritative field
        # registration inventory. In strict server flows, don't expand a group
        # with documented-but-unobserved fields that may not exist in the
        # active solver build.
        sources = list(dict.fromkeys(observed if strict_registered and available
                                     else observed + expected))
        models.append({'name': name, 'model': model,
                       'long_name': inst.get('long_name', name),
                       'selector': f'{name}/*', 'sources': sources})
    known = set(HYDRO_CORE + ['salt'])
    known.update(available)
    known.update(v for model in models for v in model['sources'])
    known.difference_update(UNREGISTERED)
    return models, known, available


def _resolve(sources, models, known, available):
    if not isinstance(sources, (list, tuple)) or not sources:
        raise ValueError('sources 必须是非空字段数组')
    by_name = {m['name']: m for m in models}
    resolved = []
    for source in sources:
        if not isinstance(source, str) or not source.strip():
            raise ValueError('sources 中的每一项必须是非空字段名')
        source = source.strip()
        if source == '*':
            resolved.append(source)
            continue
        if source in UNREGISTERED:
            raise ValueError(f'输出字段 {source} 未在 FABM 输出管理器注册；请使用 temp、z、D、hn，流速由 GETM 原生输出提供')
        if source.endswith('/*'):
            selector = source[:-2]
            matches = [by_name[selector]] if selector in by_name else [m for m in models if m['model'] == selector]
            expanded = [v for model in matches for v in model['sources']]
            if not matches:
                # Retain native categories only when actual registered paths
                # provide evidence; fabricated instance categories are unsafe.
                expanded = [v for v in available if v.startswith(selector + '/')]
            if not expanded:
                raise ValueError(f'输出订阅 {source} 没有已注册字段；检查模型 {selector} 是否启用，或选择具体字段')
            resolved.extend(expanded)
            continue
        if source in known:
            resolved.append(source)
            continue
        if '/' in source:
            instance, variable = source.rsplit('/', 1)
            candidate = f'{instance}_{variable}'
            if instance in by_name and candidate in known:
                resolved.append(candidate)
                continue
        suggestions = difflib.get_close_matches(source, sorted(known), n=3, cutoff=0.45)
        hint = f'；可选字段：{", ".join(suggestions)}' if suggestions else '；请从已启用模型的输出字段中选择'
        raise ValueError(f'未知输出字段 {source}{hint}')
    return list(dict.fromkeys(resolved))


def resolve_sources(case_path, sources, context=None):
    """Expand active model selectors, validate explicit fields, deduplicate."""
    models, known, available = _inventory(case_path, context)
    return _resolve(sources, models, known, available)


def preset_sources(case_path, preset, context=None):
    """Return exact selected states for standard/hydro, or '*' for all."""
    if preset == 'all':
        return ['*']
    if preset not in {'standard', 'minimal', 'hydro'}:
        raise ValueError(f'未知输出 preset: {preset}')
    models, known, available = _inventory(case_path, context)
    result = list(HYDRO_CORE)
    if preset in {'minimal', 'hydro'}:
        if 'salt' in available:
            result.insert(1, 'salt')
        return result
    targets = {
        'wet/abiotic_water': ('sO2W', 'sNO3W', 'sNH4W', 'sPO4W'),
        'wet/phytoplankton': ('sDW',),
        'wet/inorganic_carbon': ('sDICW',),
        'wet/methane': ('sCH4W',),
    }
    for model in models:
        for variable in targets.get(model['model'], ()):
            field = f'{model["name"]}_{variable}'
            if field in known:
                result.append(field)
    return list(dict.fromkeys(result))


def model_sources(case_path, context=None, selected_sources=None):
    """Model checkbox metadata with exact sources and complete/partial state."""
    models, known, available = _inventory(case_path, context)
    selected = set(_resolve(selected_sources, models, known, available)) if selected_sources else set()
    for model in models:
        fields = set(model['sources'])
        count = len(fields & selected)
        model['selected'] = bool(fields) and ('*' in selected or count == len(fields))
        model['partially_selected'] = bool(count) and not model['selected']
    return models
