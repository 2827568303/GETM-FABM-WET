"""Run an isolated, one-parameter Ravn GOTM calibration from default inputs.

The research bounds come from the locally archived official config_parsac.xml.
This experiment intentionally uses only training DO pairs during optimization;
the predeclared 2001–2005 holdout is evaluated after selecting the parameter.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

from scipy.optimize import minimize_scalar
from output_paths import output_path, require_outside_c


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / '3DWET' / 'app'
sys.path.insert(0, str(APP))

from gotm_working_copy import validate_working_copy  # noqa: E402
from observations import parse_observations  # noqa: E402
from reference_gotm import (  # noqa: E402
    aggregate_pair_metrics, apply_parameter_values, create_parameter_trial_copy,
    load_parsac_fabm_candidates, pair_ravn_records, partition_ravn_records,
    run_official_gotm_trial, sha256_file, validate_parameter_candidates,
    verify_official_default_archive,
)


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat(sep=' ')
    raise TypeError(f'Not JSON serializable: {type(value).__name__}')


def _dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                     default=_json_default), encoding='utf-8')


def _mapping():
    return {'variable': 'abiotic_water_sO2W', 'unit': 'mg/L', 'mass_basis': 'O2',
            'lake_id': 'Ravn', 'point_id': 'Ravn-column', 'depth_sign': 'negative_down'}


def _model_for(output_path):
    import server
    target = {'lake_id': 'Ravn', 'point_id': 'Ravn-column',
              'representativeness': 'column', 'j': 0, 'i': 0}
    return server._native_observation_model(output_path, 'abiotic_water_sO2W', target)


def _evaluation(case_path, rows, max_gap_hours):
    result = run_official_gotm_trial(case_path)
    if not result['success']:
        return {'run': result, 'metrics': None, 'diagnostics': []}
    model = _model_for(Path(case_path) / 'output.nc')
    matched = pair_ravn_records(rows, {'abiotic_water_sO2W': model}, max_gap_hours)
    return {'run': result, 'metrics': matched['metrics'],
            'per_variable': matched['per_variable'],
            'pairs': matched['pairs'], 'diagnostics': matched['diagnostics']}


def run_calibration(args):
    """Execute the preregistered train/holdout experiment in isolated copies."""
    args.output = require_outside_c(args.output, '--output')
    key = args.manifest_key.read_bytes()
    if len(key) < 32 or not validate_working_copy(args.source_case, key):
        raise SystemExit('Blocked: source case is not a valid trusted GOTM working copy')
    archive_provenance = verify_official_default_archive(args.source_case, args.source_archive)
    source_hash = sha256_file(args.source_case / 'fabm.yaml')
    source_manifest_hash = sha256_file(args.source_case / '.wet-gotm-working-copy.json')
    args.output.mkdir(parents=True, exist_ok=False)

    candidates_doc = load_parsac_fabm_candidates(args.parsac, args.source_case / 'fabm.yaml')
    selected = [row for row in candidates_doc['candidates']
                if (row['module'], row['param']) == ('abiotic_water', 'kNitrW')]
    if len(selected) != 1:
        raise SystemExit('Blocked: official ParSac metadata has no unique default-compatible kNitrW candidate')
    candidates = validate_parameter_candidates(
        args.source_case / 'fabm.yaml', selected,
        expected_bounds_source_sha256=candidates_doc['source_sha256'])
    candidate = candidates[0]
    if candidate['min'] >= candidate['max']:
        raise SystemExit('Blocked: selected ParSac bounds do not define a searchable interval')

    parsed = parse_observations(args.observations, _mapping())
    split = partition_ravn_records(parsed['records'])
    if not split['training'] or not split['holdout']:
        raise SystemExit('Blocked: official DO observations have no records in both declared windows')
    input_bundle = {
        'source_case': str(args.source_case.resolve()),
        'source_fabm_sha256': source_hash,
        'source_manifest_sha256': source_manifest_hash,
        'official_setup_archive': archive_provenance,
        'parsac_path': str(args.parsac.resolve()),
        'parsac_sha256': candidates_doc['source_sha256'],
        'observations_path': str(args.observations.resolve()),
        'observations_sha256': parsed['source_sha256'],
        'observation_mapping': _mapping(),
        'observation_row_count': parsed['row_count'],
        'parsed_records': len(parsed['records']),
        'parser_diagnostic_count': len(parsed['diagnostics']),
        'parser_diagnostics': parsed['diagnostics'],
        'partition': split['windows'],
        'training_records': len(split['training']),
        'holdout_records': len(split['holdout']),
        'partition_excluded': split['excluded'],
        'max_nearest_output_gap_hours': args.max_time_gap_hours,
        'candidate': candidate,
        'parsac_default_compatible_candidates': candidates_doc['candidates'],
        'parsac_candidates_skipped': candidates_doc['skipped'],
        'objective': 'minimum matched training DO RMSE (mg O2/L); not the ParSAC likelihood/objective',
        'no_holdout_used_for_selection': True,
    }
    _dump(args.output / 'inputs_and_design.json', input_bundle)

    evaluations = []
    baseline_path = args.output / 'baseline_default'
    create_parameter_trial_copy(args.source_case, baseline_path, key)
    baseline_result = _evaluation(baseline_path, split['training'], args.max_time_gap_hours)
    if not baseline_result['run']['success'] or not baseline_result['metrics']:
        _dump(args.output / 'failed_run.json', baseline_result['run'])
        raise SystemExit('Blocked: fresh default solver run or training DO match failed')
    default_value = candidate['initial']
    evaluations.append({'parameter_value': default_value,
                        'trial_case': str(baseline_path), 'evaluation': baseline_result})

    cache = {default_value: baseline_result['metrics']['rmse']}
    def objective(value):
        value = float(value)
        key_value = round(value, 12)
        if key_value in cache:
            return cache[key_value]
        trial_path = args.output / f'evaluation_{len(evaluations):02d}'
        create_parameter_trial_copy(args.source_case, trial_path, key)
        apply_parameter_values(trial_path / 'fabm.yaml', candidates, [value])
        evaluation = _evaluation(trial_path, split['training'], args.max_time_gap_hours)
        if not evaluation['run']['success'] or not evaluation['metrics']:
            raise RuntimeError(f'GOTM evaluation failed for {value}: {evaluation["run"]}')
        score = evaluation['metrics']['rmse']
        evaluations.append({'parameter_value': value, 'trial_case': str(trial_path),
                            'evaluation': evaluation})
        cache[key_value] = score
        _dump(args.output / 'optimization_progress.json', {
            'objective': 'matched training DO RMSE (mg O2/L)',
            'objective_is_parsac_likelihood': False, 'minimize': True,
            'evaluation_count': len(evaluations),
            'evaluations': [{k: v for k, v in row.items() if k != 'evaluation'} |
                            {'training_metrics': row['evaluation']['metrics'],
                             'output_sha256': row['evaluation']['run'].get('output_sha256'),
                             'log_sha256': row['evaluation']['run'].get('log_sha256'),
                             'input_manifest_sha256': row['evaluation']['run'].get('input_manifest_sha256')}
                            for row in evaluations]})
        return score

    optimized = minimize_scalar(objective, bounds=(candidate['min'], candidate['max']),
                                method='bounded', options={'maxiter': args.max_iterations,
                                                           'xatol': 1e-4})
    best_row = min(evaluations, key=lambda row: row['evaluation']['metrics']['rmse'])
    best_value = float(best_row['parameter_value'])

    # Rerun a clean copy at the selected value. Only training rows are paired
    # here; holdout rows are first read after parameter selection is complete.
    best_path = args.output / 'best_parameter_rerun'
    create_parameter_trial_copy(args.source_case, best_path, key)
    apply_parameter_values(best_path / 'fabm.yaml', candidates, [best_value])
    final = _evaluation(best_path, split['training'], args.max_time_gap_hours)
    if not final['run']['success'] or not final['metrics']:
        raise SystemExit('Best-parameter training-window rerun failed')

    # Holdout scores are calculated only after the candidate has been selected
    # and the best-value rerun has completed successfully.
    final_model = _model_for(best_path / 'output.nc')
    final_split = pair_ravn_records(split['holdout'],
                                    {'abiotic_water_sO2W': final_model},
                                    args.max_time_gap_hours)
    default_model = _model_for(baseline_path / 'output.nc')
    default_holdout = pair_ravn_records(split['holdout'],
                                        {'abiotic_water_sO2W': default_model},
                                        args.max_time_gap_hours)

    rollback_path = args.output / 'rollback_check'
    rollback_meta = create_parameter_trial_copy(args.source_case, rollback_path, key)
    apply_parameter_values(rollback_path / 'fabm.yaml', candidates, [best_value])
    restore_bytes = (args.source_case / 'fabm.yaml').read_bytes()
    temp_restore = rollback_path / 'fabm.yaml.restore.tmp'
    temp_restore.write_bytes(restore_bytes)
    temp_restore.replace(rollback_path / 'fabm.yaml')
    rollback_hash = sha256_file(rollback_path / 'fabm.yaml')
    source_unchanged = (validate_working_copy(args.source_case, key)
                        and sha256_file(args.source_case / 'fabm.yaml') == source_hash
                        and sha256_file(args.source_case / '.wet-gotm-working-copy.json') == source_manifest_hash)

    pair_evidence = {
        'mapping': _mapping(), 'max_nearest_output_gap_hours': args.max_time_gap_hours,
        'training': final,
        'holdout': final_split,
        'default_holdout': default_holdout,
        'parser_diagnostics': parsed['diagnostics'],
        'partition_excluded': split['excluded'],
    }
    _dump(args.output / 'pairing_evidence.json', pair_evidence)
    summary = {
        'scope': 'fresh-default one-parameter official GOTM-WET experiment',
        'scientific_limit': 'One parameter and DO target only; not a reproduction of full ParSAC, not formal calibration, and not independent external validation. Original source remains unchanged.',
        'method': 'Bounded scalar minimization of matched training DO RMSE. Holdout rows are not used for parameter search; they are evaluated after parameter selection.',
        'candidate': candidate,
        'optimizer': {'success': bool(optimized.success), 'message': str(optimized.message),
                      'nfev': int(optimized.nfev), 'evaluations_completed': len(evaluations),
                      'selected_value': best_value,
                      'training_objective': final['metrics']['rmse'],
                      'default_training_objective': baseline_result['metrics']['rmse'],
                      'objective_name': 'matched training DO RMSE (mg O2/L)',
                      'objective_is_parsac_likelihood': False},
        'best_rerun': {'run': final['run'], 'training_metrics': final['metrics'],
                       'holdout_metrics': final_split['metrics'],
                       'default_holdout_metrics': default_holdout['metrics']},
        'evaluations': [{'value': row['parameter_value'],
                         'training_metrics': row['evaluation']['metrics'],
                         'output_sha256': row['evaluation']['run']['output_sha256'],
                         'log_sha256': row['evaluation']['run']['log_sha256'],
                         'input_manifest_sha256': row['evaluation']['run']['input_manifest_sha256'],
                         'trial_case': row['trial_case']} for row in evaluations],
        'source_integrity': {'fabm_sha256': source_hash,
                             'manifest_sha256': source_manifest_hash,
                             'working_copy_valid_after_runs': bool(source_unchanged)},
        'rollback_check': {'default_fabm_sha256': source_hash,
                           'restored_fabm_sha256': rollback_hash,
                           'matches_default': rollback_hash == source_hash,
                           'trial_copy_metadata': rollback_meta},
        'source_unchanged': bool(source_unchanged),
    }
    _dump(args.output / 'summary.json', summary)
    if not source_unchanged:
        raise SystemExit('Source working-copy integrity check failed after the experiment')
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-case', type=Path, default=output_path('build','ravn-official-working-copy-run-20261021-attempt01','case'))
    parser.add_argument('--source-archive', type=Path, default=output_path('build','ravn-calibration-research-20261016','default_lakeRavn_setup.zip'))
    parser.add_argument('--observations', type=Path, default=output_path('build','ravn-calibration-research-20261016','QWET_test_case_Lake_Ravn_workshop','OBSERVATIONS','DO.obs'))
    parser.add_argument('--parsac', type=Path, default=output_path('build','ravn-calibration-research-20261016','config_parsac.xml'))
    parser.add_argument('--output', type=Path, default=output_path('build','real-use-validation-20261022','ravn-default-calibration'))
    parser.add_argument('--manifest-key', type=Path, default=APP / '.gotm-working-copy.key')
    parser.add_argument('--max-time-gap-hours', type=float, default=12)
    parser.add_argument('--max-iterations', type=int, default=5)
    args = parser.parse_args(argv)
    summary = run_calibration(args)
    print(json.dumps({k: summary[k] for k in ('optimizer', 'best_rerun', 'rollback_check', 'source_unchanged')},
                     indent=2, default=_json_default))


if __name__ == '__main__':
    main()
