"""Preserve case-local FABM reset values independently of saved YAML edits.

Call with an explicit case directory and ``persist=True`` on actual case load.
Ordinary configuration reads can pass ``persist=False`` to consume the snapshot
without writing it. Passing ``None`` never touches the filesystem.
"""
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import tempfile


class ParameterDefaultsError(ValueError):
    """A snapshot cannot be read, validated or safely written."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate key: {key}')
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f'non-finite JSON number: {value}')


def _validate_value(value):
    # YAML parameters normally are scalars; preserve all JSON-compatible types
    # in case a model also declares a structured parameter.
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    if isinstance(value, list):
        for item in value:
            _validate_value(item)
        return
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        for item in value.values():
            _validate_value(item)
        return
    raise ValueError('parameter default must be a finite JSON-compatible value')


def _read_snapshot(path):
    try:
        text = path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return {'version': 1, 'defaults': {}}, False
    data = json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant)
    if (not isinstance(data, dict) or type(data.get('version')) is not int
            or data['version'] != 1 or not isinstance(data.get('defaults'), dict)):
        raise ValueError('expected version 1 snapshot with defaults object')
    for module, parameters in data['defaults'].items():
        if not module or not isinstance(parameters, dict):
            raise ValueError('each module must contain a parameter defaults object')
        for name, value in parameters.items():
            if not name:
                raise ValueError('parameter name cannot be empty')
            _validate_value(value)
    return data, True


def _write_snapshot(path, snapshot):
    """Replace a complete fsynced file; leave the old file intact on failure."""
    encoded = json.dumps(snapshot, ensure_ascii=False, indent=2,
                         allow_nan=False) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                prefix='.fabm-defaults-', suffix='.tmp', dir=path.parent,
                delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def annotate_defaults(case_path, modules, *, persist=True):
    """Annotate and return ``modules`` with immutable defaults and saved values.

    The first load uses an inline comment's ``default_value`` when available,
    otherwise the parameter's current ``value``. Later loads keep the recorded
    baseline, extend it only for newly discovered parameters, and retain removed
    modules so re-enabling them does not reset their defaults. ``saved_value``
    always reflects the current parsed YAML value, including bool/string types.

    Invalid snapshots raise :class:`ParameterDefaultsError` before any mutation
    of the snapshot or supplied modules. The caller should surface that error.
    """
    path = (Path(case_path) / '.studio-config' / 'fabm_defaults.json'
            if case_path is not None else None)
    try:
        data, exists = (_read_snapshot(path) if path is not None
                        else ({'version': 1, 'defaults': {}}, False))
        changed = not exists
        annotations = []
        for module in modules:
            module_name = module['name']
            if not isinstance(module_name, str) or not module_name:
                raise ValueError('module name must be a non-empty string')
            defaults = data['defaults'].setdefault(module_name, {})
            for parameter in module.get('parameters', []):
                name = parameter['name']
                if not isinstance(name, str) or not name:
                    raise ValueError('parameter name must be a non-empty string')
                saved = parameter['value']
                _validate_value(saved)
                if name not in defaults:
                    default = parameter.get('default_value')
                    if default is None:
                        default = saved
                    _validate_value(default)
                    defaults[name] = deepcopy(default)
                    changed = True
                annotations.append((parameter, deepcopy(defaults[name]),
                                    deepcopy(saved)))
        if path is not None and persist and changed:
            _write_snapshot(path, data)
        for parameter, default, saved in annotations:
            parameter['default_value'] = default
            parameter['saved_value'] = saved
        return modules
    except (OSError, ValueError, TypeError, KeyError) as exc:
        location = str(path) if path is not None else 'FABM parameter defaults'
        raise ParameterDefaultsError(f'{location}: {exc}') from exc
