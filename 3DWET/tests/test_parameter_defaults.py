"""Case-local reset defaults remain independent of current saved YAML values."""
import importlib.util
from pathlib import Path

import pytest


def helper():
    path = Path(__file__).resolve().parents[1] / 'app' / 'parameter_defaults.py'
    assert path.exists(), 'case-local first-load default snapshot helper must exist'
    spec = importlib.util.spec_from_file_location('parameter_defaults_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def modules(value=3, comment_default=None):
    return [{'name': 'POM', 'parameters': [
        {'name': 'kDMinW', 'value': value, 'default_value': comment_default},
        {'name': 'enabled', 'value': False, 'default_value': None},
        {'name': 'mode', 'value': 'mixed', 'default_value': None},
    ]}]


def snapshot(case):
    return case / '.studio-config' / 'fabm_defaults.json'


def test_first_load_snapshots_comment_defaults_and_commentless_values(tmp_path):
    implementation = helper()
    yaml = tmp_path / 'fabm.yaml'
    yaml.write_bytes(b'instances:\n  POM:\n    parameters:\n      kDMinW: 3\n')
    before = yaml.read_bytes()
    data = modules(comment_default=0.02)
    assert implementation.annotate_defaults(tmp_path, data) is data
    params = data[0]['parameters']
    assert params[0]['default_value'] == 0.02
    assert params[0]['saved_value'] == 3
    assert params[1]['default_value'] is False
    assert params[2]['default_value'] == 'mixed'
    assert snapshot(tmp_path).exists()
    assert yaml.read_bytes() == before


def test_saved_edits_never_replace_original_defaults_or_rewrite_snapshot(tmp_path):
    implementation = helper()
    implementation.annotate_defaults(tmp_path, modules())
    before = snapshot(tmp_path).read_bytes()
    edited = modules(value=8, comment_default=99)
    implementation.annotate_defaults(tmp_path, edited)
    assert edited[0]['parameters'][0]['default_value'] == 3
    assert edited[0]['parameters'][0]['saved_value'] == 8
    assert snapshot(tmp_path).read_bytes() == before


def test_new_parameters_extend_snapshot_and_removed_modules_survive(tmp_path):
    implementation = helper()
    implementation.annotate_defaults(tmp_path, modules())
    added = [{'name': 'DOM', 'parameters': [{'name': 'rate', 'value': 5.5, 'default_value': None}]}]
    implementation.annotate_defaults(tmp_path, added)
    removed_then_restored = modules(value=30)
    implementation.annotate_defaults(tmp_path, removed_then_restored)
    assert removed_then_restored[0]['parameters'][0]['default_value'] == 3
    added[0]['parameters'][0]['value'] = 9
    implementation.annotate_defaults(tmp_path, added)
    assert added[0]['parameters'][0]['default_value'] == 5.5


def test_case_snapshots_are_independent_and_readonly_parse_does_not_create(tmp_path):
    implementation = helper()
    a, b, readonly = [tmp_path / name for name in ['a', 'b', 'readonly']]
    for path in [a, b, readonly]:
        path.mkdir()
    implementation.annotate_defaults(a, modules(3))
    implementation.annotate_defaults(b, modules(4))
    check = modules(9)
    implementation.annotate_defaults(a, check, persist=False)
    assert check[0]['parameters'][0]['default_value'] == 3
    fresh = modules(7)
    implementation.annotate_defaults(readonly, fresh, persist=False)
    assert fresh[0]['parameters'][0]['saved_value'] == 7
    assert not snapshot(readonly).exists()
    implementation.annotate_defaults(None, modules())


@pytest.mark.parametrize('raw', [b'{broken', b'[]', b'{"version":999,"defaults":{}}',
    b'{"version":1,"defaults":{"POM":[]}}', b'{"version":1,"defaults":{"POM":{"rate":NaN}}}',
    b'{"version":1,"defaults":{"POM":{"rate":1e999}}}',
    b'{"version":1,"defaults":{"POM":{"rate":1,"rate":2}}}'])
def test_malformed_snapshot_is_reported_and_preserved(tmp_path, raw):
    implementation = helper()
    path = snapshot(tmp_path)
    path.parent.mkdir()
    path.write_bytes(raw)
    data = modules()
    with pytest.raises(implementation.ParameterDefaultsError, match='fabm_defaults.json'):
        implementation.annotate_defaults(tmp_path, data)
    assert path.read_bytes() == raw
    assert data[0]['parameters'][0]['default_value'] is None


def test_failed_atomic_replace_preserves_previous_snapshot_and_cleans_temp(tmp_path, monkeypatch):
    implementation = helper()
    implementation.annotate_defaults(tmp_path, modules())
    path = snapshot(tmp_path)
    before = path.read_bytes()
    def fail(*args):
        raise OSError('simulated replace failure')
    monkeypatch.setattr(implementation.os, 'replace', fail)
    added = [{'name': 'new', 'parameters': [{'name': 'rate', 'value': 2}]}]
    with pytest.raises(implementation.ParameterDefaultsError, match='simulated replace failure'):
        implementation.annotate_defaults(tmp_path, added)
    assert path.read_bytes() == before
    assert list(path.parent.iterdir()) == [path]
    assert 'saved_value' not in added[0]['parameters'][0]


def test_zero_false_empty_string_comment_defaults_preserve_types(tmp_path):
    implementation = helper()
    data = [{'name': 'typed', 'parameters': [
        {'name': 'zero', 'value': 8, 'default_value': 0},
        {'name': 'bool', 'value': True, 'default_value': False},
        {'name': 'string', 'value': 'saved', 'default_value': ''},
    ]}]
    implementation.annotate_defaults(tmp_path, data)
    parameters = data[0]['parameters']
    assert type(parameters[0]['default_value']) is int
    assert parameters[0]['default_value'] == 0
    assert parameters[1]['default_value'] is False
    assert parameters[1]['saved_value'] is True
    assert parameters[2]['default_value'] == ''
    before = snapshot(tmp_path).read_bytes()
    data[0]['parameters'].append({'name': 'read_only_new', 'value': 1})
    implementation.annotate_defaults(tmp_path, data, persist=False)
    assert data[0]['parameters'][-1]['default_value'] == 1
    assert snapshot(tmp_path).read_bytes() == before
