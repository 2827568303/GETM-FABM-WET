from datetime import datetime
import hashlib
import json
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET' / 'app'))
from gotm_working_copy import create_working_copy
from reference_gotm import (
    create_parameter_trial_copy, partition_ravn_records,
    validate_parameter_candidates, apply_parameter_values, aggregate_pair_metrics,
    match_ravn_split, load_parsac_fabm_candidates, verify_official_default_archive,
)


def _reference_case(path):
    path.mkdir()
    (path / 'gotm.yaml').write_text('time:\n  start: 1990-01-01 00:00:00\n  stop: 2005-12-31 00:00:00\n', encoding='utf-8')
    (path / 'fabm.yaml').write_text(
        'instances:\n  abiotic_water:\n    parameters:\n      kNitrW: 0.3\n', encoding='utf-8')
    (path / 'meteo_file.dat').write_text('trusted forcing\n', encoding='utf-8')
    (path / 'gotm_release.exe').write_bytes(b'MZtest executable')
    with nc.Dataset(path / 'output.nc', 'w') as ds:
        ds.createDimension('time', 2); ds.createDimension('z', 2)
        ds.createDimension('lat', 1); ds.createDimension('lon', 1)
        t = ds.createVariable('time', 'f8', ('time',)); t.units = 'days since 2000-01-01'; t[:] = [0, 1]
        for name in ('h', 'z', 'temp'):
            v = ds.createVariable(name, 'f8', ('time', 'z', 'lat', 'lon'))
            v[:] = 1.0


def test_partition_uses_preregistered_train_holdout_and_reports_warmup(tmp_path):
    records = [
        {'time': '1995-12-31T23:00:00', 'value': 1},
        {'time': '1996-01-01T00:00:00', 'value': 2},
        {'time': '2000-12-31T23:00:00', 'value': 3},
        {'time': '2001-01-01T00:00:00', 'value': 4},
        {'time': '2005-12-31T23:00:00', 'value': 5},
        {'time': '2006-01-01T00:00:00', 'value': 6},
    ]
    split = partition_ravn_records(records)
    assert [r['value'] for r in split['training']] == [2, 3]
    assert [r['value'] for r in split['holdout']] == [4, 5]
    assert split['excluded'] == [
        {'index': 0, 'reason': 'warmup_or_before_training'},
        {'index': 5, 'reason': 'after_holdout_window'},
    ]


def test_matching_reuses_strict_observation_matcher_for_both_splits():
    records = [
        {'time': '1996-01-01T00:00:00', 'value': 2.0, 'depth_m': 5.0, 'unit': 'degC',
         'variable': 'temp', 'lake_id': 'Ravn', 'station_id': None, 'source_line': 1},
        {'time': '2001-01-01T00:00:00', 'value': 4.0, 'depth_m': 5.0, 'unit': 'degC',
         'variable': 'temp', 'lake_id': 'Other lake', 'station_id': None, 'source_line': 2},
    ]
    model = {'times': ['1996-01-01T00:00:00', '2001-01-01T00:00:00'],
             'values': [[1.0, 3.0], [3.0, 5.0]], 'center_depth': [[2.0, 8.0], [2.0, 8.0]],
             'unit': 'degC', 'variable': 'temp', 'lake_id': 'Ravn', 'station_id': None,
             'representativeness': 'column', 'calendar': 'standard'}
    result = match_ravn_split(records, {'temp': model}, max_time_gap_hours=1)
    assert result['training']['metrics']['count'] == 1
    assert result['training']['metrics']['rmse'] == pytest.approx(0.0)
    assert result['holdout']['metrics'] is None
    assert result['holdout']['diagnostics'][0]['reason'] == 'lake_mismatch'


def test_candidate_bounds_must_be_hashed_and_enclose_official_default(tmp_path):
    fabm = tmp_path / 'fabm.yaml'
    fabm.write_text('instances:\n  abiotic_water:\n    parameters:\n      kNitrW: 0.3\n', encoding='utf-8')
    default_hash = hashlib.sha256(fabm.read_bytes()).hexdigest()
    bounds_file = tmp_path / 'official-calibrated-metadata.json'
    bounds_file.write_text('{"kNitrW":{"min":0.1,"max":0.8}}', encoding='utf-8')
    bounds_hash = hashlib.sha256(bounds_file.read_bytes()).hexdigest()
    spec = {'module': 'abiotic_water', 'param': 'kNitrW', 'min': 0.1, 'max': 0.8,
            'bounds_source': 'QWET calibrated/default parameter metadata',
            'bounds_source_path': str(bounds_file), 'bounds_source_sha256': bounds_hash}
    validated = validate_parameter_candidates(fabm, [spec], expected_bounds_source_sha256=bounds_hash)
    assert validated[0]['initial'] == pytest.approx(0.3)
    with pytest.raises(ValueError, match='source hash'):
        validate_parameter_candidates(fabm, [{**spec, 'bounds_source_sha256': '0' * 64}],
                                      expected_bounds_source_sha256=bounds_hash)
    with pytest.raises(ValueError, match='default value'):
        validate_parameter_candidates(fabm, [{**spec, 'min': 0.4}],
                                      expected_bounds_source_sha256=bounds_hash)


def test_parsac_candidate_loader_keeps_only_bounds_compatible_with_default(tmp_path):
    fabm = tmp_path / 'fabm.yaml'
    fabm.write_text('instances:\n  abiotic_water:\n    parameters:\n      kNitrW: 0.3\n      kDMinPOMW: 0.001\n', encoding='utf-8')
    parsac = tmp_path / 'config_parsac.xml'
    parsac.write_text('''<config><parameters>
      <parameter file="fabm.yaml" variable="instances/abiotic_water/parameters/kNitrW" minimum="0.1" maximum="0.5"/>
      <parameter file="fabm.yaml" variable="instances/abiotic_water/parameters/kDMinPOMW" minimum="0.04" maximum="0.09"/>
      <parameter file="gotm.yaml" variable="surface/meteo/u10/scale_factor" minimum="1.05" maximum="1.17"/>
    </parameters></config>''', encoding='utf-8')
    loaded = load_parsac_fabm_candidates(parsac, fabm)
    assert [(row['module'], row['param']) for row in loaded['candidates']] == [('abiotic_water', 'kNitrW')]
    assert loaded['candidates'][0]['bounds_source_sha256'] == hashlib.sha256(parsac.read_bytes()).hexdigest()
    assert loaded['skipped'][0]['reason'] == 'default_outside_stage_bounds'


def test_parameter_trial_copy_isolated_and_default_restored_on_source(tmp_path):
    source = tmp_path / 'official-reference'; _reference_case(source)
    trusted = tmp_path / 'trusted-copy'; trusted.mkdir()
    create_working_copy(source, trusted, b'test-key')
    before = hashlib.sha256((trusted / 'fabm.yaml').read_bytes()).hexdigest()
    trial = tmp_path / 'trial'
    metadata = create_parameter_trial_copy(trusted, trial, b'test-key')
    assert metadata['source_fabm_sha256'] == before
    assert not (trial / 'output.nc').exists()
    assert (trial / 'gotm_release.exe').is_file()
    assert hashlib.sha256((trusted / 'fabm.yaml').read_bytes()).hexdigest() == before
    bounds_file = tmp_path / 'official-bounds.json'
    bounds_file.write_text('{"kNitrW":{"min":0.1,"max":0.8}}', encoding='utf-8')
    bounds_hash = hashlib.sha256(bounds_file.read_bytes()).hexdigest()
    spec = validate_parameter_candidates(
        trial / 'fabm.yaml', [{'module': 'abiotic_water', 'param': 'kNitrW', 'min': 0.1,
                               'max': 0.8, 'bounds_source': 'official metadata',
                               'bounds_source_path': str(bounds_file),
                               'bounds_source_sha256': bounds_hash}],
        expected_bounds_source_sha256=bounds_hash)
    apply_parameter_values(trial / 'fabm.yaml', spec, [0.5])
    assert 'kNitrW: 0.5' in (trial / 'fabm.yaml').read_text(encoding='utf-8')
    assert hashlib.sha256((trusted / 'fabm.yaml').read_bytes()).hexdigest() == before


def test_signed_copy_matches_official_archive_files_and_records_generated_sidecar(tmp_path):
    from zipfile import ZipFile

    source = tmp_path / 'official-source'; _reference_case(source)
    (source / 'native_variable_metadata.json').write_text('{"generated":true}', encoding='utf-8')
    trusted = tmp_path / 'trusted-copy'; trusted.mkdir()
    create_working_copy(source, trusted, b'test-key')
    archive = tmp_path / 'official-default.zip'
    with ZipFile(archive, 'w') as bundle:
        for path in trusted.iterdir():
            if path.is_file() and path.name not in {'.wet-gotm-working-copy.json', 'output.nc'}:
                bundle.write(path, f'Default/{path.name}')
    report = verify_official_default_archive(trusted, archive)
    assert {'fabm.yaml', 'gotm.yaml', 'gotm_release.exe'}.issubset(report['matched_files'])
    assert report['derived_files'] == ['native_variable_metadata.json']
    assert len(report['archive_sha256']) == 64
    altered = tmp_path / 'altered.zip'
    with ZipFile(archive) as original, ZipFile(altered, 'w') as bundle:
        for name in original.namelist():
            data = original.read(name)
            if name == 'Default/fabm.yaml':
                data = data.replace(b'kNitrW: 0.3', b'kNitrW: 0.4')
            bundle.writestr(name, data)
    with pytest.raises(ValueError, match='differs from official archive'):
        verify_official_default_archive(trusted, altered)


def test_pair_metrics_requires_finite_pairs_and_reports_count():
    result = aggregate_pair_metrics([
        {'obs': 2.0, 'sim': 1.0}, {'obs': 3.0, 'sim': 4.0},
    ])
    assert result == {'count': 2, 'rmse': pytest.approx(1.0), 'bias': 0.0}
    with pytest.raises(ValueError, match='finite matched'):
        aggregate_pair_metrics([{'obs': float('nan'), 'sim': 1.0}])


def test_ravn_workflow_selects_on_training_only_and_reruns_selected_default_start(tmp_path, monkeypatch):
    import importlib.util
    from types import SimpleNamespace
    import yaml

    script_path = ROOT / 'scripts' / 'run_ravn_default_calibration.py'
    spec = importlib.util.spec_from_file_location('run_ravn_default_calibration_test', script_path)
    workflow = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow)

    source = tmp_path / 'trusted-default'
    source.mkdir()
    fabm = source / 'fabm.yaml'
    fabm.write_text('instances:\n  abiotic_water:\n    parameters:\n      kNitrW: 0.3\n', encoding='utf-8')
    (source / '.wet-gotm-working-copy.json').write_text('{"trusted":true}', encoding='utf-8')
    key_path = tmp_path / 'key'; key_path.write_bytes(b'x' * 32)
    parsac = tmp_path / 'config_parsac.xml'
    parsac.write_text('''<config><parameters>
      <parameter file="fabm.yaml" variable="instances/abiotic_water/parameters/kNitrW" minimum="0.1" maximum="0.5"/>
    </parameters></config>''', encoding='utf-8')
    observations = tmp_path / 'DO.obs'; observations.write_text('fixture', encoding='utf-8')
    output = tmp_path / 'evidence'
    records = [
        {'time': '1996-04-01T12:00:00', 'value': 1, 'source_line': 1},
        {'time': '2001-04-01T12:00:00', 'value': 2, 'source_line': 2},
    ]
    monkeypatch.setattr(workflow, 'validate_working_copy', lambda path, key: True)
    monkeypatch.setattr(workflow, 'verify_official_default_archive', lambda path, archive: {
        'archive_path': str(archive), 'archive_sha256': 'archive-hash', 'matched_files': {}, 'derived_files': []})
    monkeypatch.setattr(workflow, 'parse_observations', lambda path, mapping: {
        'records': records, 'row_count': 2, 'diagnostics': [], 'source_sha256': 'obs-hash'})

    def make_copy(source_case, trial_case, key):
        trial_case.mkdir()
        (trial_case / 'fabm.yaml').write_bytes((source_case / 'fabm.yaml').read_bytes())
        return {'source_fabm_sha256': workflow.sha256_file(source_case / 'fabm.yaml')}

    monkeypatch.setattr(workflow, 'create_parameter_trial_copy', make_copy)
    run_count = 0

    def run_trial(case):
        nonlocal run_count
        run_count += 1
        value = yaml.safe_load((Path(case) / 'fabm.yaml').read_text(encoding='utf-8'))['instances']['abiotic_water']['parameters']['kNitrW']
        (Path(case) / 'output.nc').write_text(f'run-{run_count}-{value}', encoding='utf-8')
        output_hash = workflow.sha256_file(Path(case) / 'output.nc')
        return {'success': True, 'returncode': 0, 'output_sha256': output_hash,
                'log_sha256': f'log-{run_count}', 'input_manifest_sha256': f'inputs-{run_count}'}

    monkeypatch.setattr(workflow, 'run_official_gotm_trial', run_trial)
    monkeypatch.setattr(workflow, '_model_for', lambda output_path: {
        'value': yaml.safe_load((Path(output_path).parent / 'fabm.yaml').read_text(encoding='utf-8'))['instances']['abiotic_water']['parameters']['kNitrW']})
    pair_calls = []

    def pair(rows, models, max_gap):
        row_years = sorted({int(row['time'][:4]) for row in rows})
        value = models['abiotic_water_sO2W']['value']
        pair_calls.append(row_years)
        error = abs(value - (0.4 if row_years == [1996] else 0.45))
        return {'metrics': {'count': len(rows), 'rmse': error, 'bias': error},
                'per_variable': {}, 'pairs': [], 'diagnostics': []}

    monkeypatch.setattr(workflow, 'pair_ravn_records', pair)
    optimizer_finished = []

    def deterministic_search(objective, **kwargs):
        assert objective(0.2) == pytest.approx(0.2)
        assert objective(0.4) == pytest.approx(0.0)
        optimizer_finished.append(True)
        return SimpleNamespace(success=True, message='deterministic test', nfev=2)

    monkeypatch.setattr(workflow, 'minimize_scalar', deterministic_search)
    args = SimpleNamespace(source_case=source, source_archive=tmp_path / 'official.zip', observations=observations, parsac=parsac,
                           output=output, manifest_key=key_path, max_time_gap_hours=12,
                           max_iterations=2)
    summary = workflow.run_calibration(args)

    assert summary['optimizer']['selected_value'] == pytest.approx(0.4)
    assert summary['optimizer']['training_objective'] == pytest.approx(0.0)
    assert summary['optimizer']['objective_is_parsac_likelihood'] is False
    assert summary['best_rerun']['holdout_metrics']['rmse'] == pytest.approx(0.05)
    assert summary['source_unchanged'] is True
    assert summary['rollback_check']['matches_default'] is True
    assert optimizer_finished
    assert pair_calls == [[1996], [1996], [1996], [1996], [2001], [2001]], \
        'every trial and the best-value rerun use training rows; holdout is paired only after selection'
    design = json.loads((output / 'inputs_and_design.json').read_text(encoding='utf-8'))
    assert design['no_holdout_used_for_selection'] is True
    assert 'not the ParSAC likelihood/objective' in design['objective']
