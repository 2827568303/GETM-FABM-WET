"""Isolated calibration primitives for trusted one-column GOTM references.

This module deliberately does not invent candidate parameters or bounds. Callers
must supply a source hash for the official parameter metadata that defines them.
"""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import yaml

from gotm_working_copy import MANIFEST, validate_working_copy


TRAIN_START = datetime(1996, 1, 1)
HOLDOUT_START = datetime(2001, 1, 1)
HOLDOUT_STOP = datetime(2006, 1, 1)

_GENERATED_NAMES = {
    'output', 'out', 'outputs', 'results', 'logs', 'backups', 'backup',
    'cache', '__pycache__', '.studio-runtime',
}
_GENERATED_SUFFIXES = ('.2d.nc', '.3d.nc', '.log', '.bak')


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_official_default_archive(trusted_case, archive_path, *, prefix='Default/'):
    """Verify a signed working copy against the unmodified official setup ZIP.

    The application-generated native output sidecar is the only required file
    in the trusted manifest that is not part of the upstream setup archive.
    Mutable solver output/restart files are intentionally absent from the
    signed manifest and are never used as calibration inputs.
    """
    case = Path(trusted_case).resolve()
    archive = Path(archive_path).resolve()
    try:
        manifest = json.loads((case / MANIFEST).read_text(encoding='utf-8'))
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
            matched, derived = {}, []
            for relative, expected_hash in manifest['files'].items():
                if relative == 'native_variable_metadata.json':
                    derived.append(relative)
                    continue
                member = prefix + relative.replace('\\', '/')
                if member not in names:
                    raise ValueError(f'Official source archive is missing {member}')
                actual_hash = hashlib.sha256(bundle.read(member)).hexdigest()
                if actual_hash != expected_hash:
                    raise ValueError(f'Trusted working copy differs from official archive: {relative}')
                matched[relative] = actual_hash
    except (OSError, KeyError, TypeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        raise ValueError('Official default setup archive could not be verified') from exc
    required = {'fabm.yaml', 'gotm.yaml', 'gotm_release.exe'}
    if not required.issubset(matched):
        raise ValueError('Official archive verification did not cover the core GOTM/FABM inputs')
    return {'archive_path': str(archive), 'archive_sha256': sha256_file(archive),
            'prefix': prefix, 'matched_files': matched, 'derived_files': derived}


def partition_ravn_records(records):
    """Partition canonical records into the predeclared train/holdout windows.

    1990–1995 is warm-up and excluded; 1996–2000 is training; 2001–2005 is
    holdout. Naive source timestamps stay naive so they can pair with GOTM's
    native clock without an implicit local-time conversion.
    """
    training, holdout, excluded = [], [], []
    for index, record in enumerate(records):
        try:
            when = record.get('time')
            if not isinstance(when, datetime):
                when = datetime.fromisoformat(str(when).replace('Z', '+00:00'))
            if when.tzinfo is not None:
                # The original QWET observation time basis is not UTC. Do not
                # normalize or silently compare it to a naive GOTM clock.
                excluded.append({'index': index, 'reason': 'timezone_aware_time_requires_review'})
                continue
            if when < TRAIN_START:
                excluded.append({'index': index, 'reason': 'warmup_or_before_training'})
            elif when < HOLDOUT_START:
                training.append(record)
            elif when < HOLDOUT_STOP:
                holdout.append(record)
            else:
                excluded.append({'index': index, 'reason': 'after_holdout_window'})
        except (TypeError, ValueError):
            excluded.append({'index': index, 'reason': 'invalid_time'})
    return {'training': training, 'holdout': holdout, 'excluded': excluded,
            'windows': {'training': ['1996-01-01', '2000-12-31'],
                        'holdout': ['2001-01-01', '2005-12-31'],
                        'warmup_excluded': ['1990-01-01', '1995-12-31']}}


def _ignore_generated(directory, names):
    ignored = []
    for name in names:
        path = Path(directory) / name
        if (name == MANIFEST or name.lower() in _GENERATED_NAMES
                or name.lower() in {'output.nc', 'restart.nc', 'model_run.log', 'run.log'}
                or name.lower().endswith(_GENERATED_SUFFIXES)
                or path.is_symlink()):
            ignored.append(name)
    return ignored


def create_parameter_trial_copy(trusted_case, destination, key):
    """Create a clean parameter-evaluation copy from a signed GOTM working copy."""
    source, target = Path(trusted_case).resolve(), Path(destination).resolve()
    if not validate_working_copy(source, key):
        raise ValueError('Source is not a valid trusted GOTM working copy')
    if source == target or source in target.parents or target in source.parents:
        raise ValueError('Source and trial must be separate directory trees')
    if target.exists() and any(target.iterdir()):
        raise ValueError('Trial destination must be empty')
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=_ignore_generated)
    fabm = target / 'fabm.yaml'
    if not fabm.is_file():
        shutil.rmtree(target, ignore_errors=True)
        raise ValueError('Trusted GOTM working copy has no fabm.yaml')
    return {'source_case': str(source), 'trial_case': str(target),
            'source_fabm_sha256': sha256_file(source / 'fabm.yaml'),
            'trial_fabm_sha256': sha256_file(fabm),
            'source_manifest_sha256': sha256_file(source / MANIFEST)}


def validate_parameter_candidates(fabm_path, candidates, *, expected_bounds_source_sha256):
    """Validate externally sourced bounds against the default FABM parameters."""
    if not isinstance(expected_bounds_source_sha256, str) or len(expected_bounds_source_sha256) != 64:
        raise ValueError('An audited bounds-source SHA-256 is required')
    config = yaml.safe_load(Path(fabm_path).read_text(encoding='utf-8')) or {}
    instances = config.get('instances')
    if not isinstance(instances, dict):
        raise ValueError('fabm.yaml has no instances mapping')
    result, seen = [], set()
    for candidate in candidates:
        module, param = candidate.get('module'), candidate.get('param')
        key = (module, param)
        if not isinstance(module, str) or not isinstance(param, str) or key in seen:
            raise ValueError('Candidate references must name unique module/parameter pairs')
        seen.add(key)
        bounds_path = candidate.get('bounds_source_path')
        try:
            actual_bounds_hash = sha256_file(bounds_path)
        except (OSError, TypeError, ValueError):
            raise ValueError('Candidate bounds source file is missing or unreadable')
        if (candidate.get('bounds_source_sha256') != expected_bounds_source_sha256
                or actual_bounds_hash != expected_bounds_source_sha256):
            raise ValueError('Candidate bounds source hash does not match the audited source hash')
        if not str(candidate.get('bounds_source', '')).strip():
            raise ValueError('Candidate bounds source description is required')
        try:
            initial = float(instances[module]['parameters'][param])
            lower, upper = float(candidate['min']), float(candidate['max'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'Candidate/default parameter is missing or invalid: {module}.{param}') from exc
        if not all(math.isfinite(v) for v in (initial, lower, upper)) or lower > upper:
            raise ValueError(f'Candidate bounds/default must be finite and ordered: {module}.{param}')
        if not lower <= initial <= upper:
            raise ValueError(f'Candidate bounds do not include the official default value: {module}.{param}')
        result.append({**candidate, 'initial': initial, 'min': lower, 'max': upper})
    if not result:
        raise ValueError('At least one sourced parameter candidate is required')
    return result


def load_parsac_fabm_candidates(parsac_path, fabm_path):
    """Read FABM parameter ranges from the official ParSac XML.

    Only paths in FABM ``parameters`` are returned. Ranges that do not contain
    the fresh default value are skipped: they belong to a different staged
    calibration state and must not silently seed a default-configuration run.
    """
    parsac_path, fabm_path = Path(parsac_path).resolve(), Path(fabm_path).resolve()
    bounds_hash = sha256_file(parsac_path)
    try:
        root = ET.parse(parsac_path).getroot()
        config = yaml.safe_load(fabm_path.read_text(encoding='utf-8')) or {}
    except (OSError, ET.ParseError, yaml.YAMLError) as exc:
        raise ValueError('ParSac bounds or default FABM configuration could not be read') from exc
    instances = config.get('instances')
    candidates, skipped = [], []
    for row in root.findall('.//parameter'):
        if row.get('file', '').casefold() != 'fabm.yaml':
            continue
        parts = str(row.get('variable', '')).split('/')
        if len(parts) != 4 or parts[0] != 'instances' or parts[2] != 'parameters':
            continue
        try:
            module, param = parts[1], parts[3]
            initial = float(instances[module]['parameters'][param])
            lower, upper = float(row.attrib['minimum']), float(row.attrib['maximum'])
        except (KeyError, TypeError, ValueError):
            skipped.append({'variable': row.get('variable'), 'reason': 'missing_or_invalid_default_or_bounds'})
            continue
        if (not all(math.isfinite(value) for value in (initial, lower, upper))
                or lower > upper):
            skipped.append({'variable': row.get('variable'), 'reason': 'invalid_numeric_bounds'})
            continue
        if not lower <= initial <= upper:
            skipped.append({'variable': row.get('variable'), 'reason': 'default_outside_stage_bounds',
                            'default': initial, 'min': lower, 'max': upper})
            continue
        candidates.append({'module': module, 'param': param, 'min': lower, 'max': upper,
                           'bounds_source': str(parsac_path), 'bounds_source_path': str(parsac_path),
                           'bounds_source_sha256': bounds_hash})
    return {'source_path': str(parsac_path), 'source_sha256': bounds_hash,
            'candidates': candidates, 'skipped': skipped}


def apply_parameter_values(fabm_path, validated_candidates, values):
    """Atomically write candidate values into an isolated trial FABM config."""
    if len(validated_candidates) != len(values):
        raise ValueError('Candidate/value count differs')
    config_path = Path(fabm_path)
    config = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
    instances = config.get('instances', {})
    for candidate, raw_value in zip(validated_candidates, values):
        value = float(raw_value)
        if not math.isfinite(value) or not candidate['min'] <= value <= candidate['max']:
            raise ValueError(f'Parameter value is outside audited bounds: {candidate["module"]}.{candidate["param"]}')
        try:
            parameters = instances[candidate['module']]['parameters']
        except KeyError as exc:
            raise ValueError('Trial FABM config no longer matches validated candidates') from exc
        if candidate['param'] not in parameters:
            raise ValueError('Trial FABM config no longer matches validated candidates')
        parameters[candidate['param']] = value
    rendered = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=config_path.parent,
                                     delete=False, suffix='.tmp') as stream:
        temporary = Path(stream.name)
        stream.write(rendered)
        stream.flush()
    temporary.replace(config_path)
    return sha256_file(config_path)


def aggregate_pair_metrics(pairs):
    """Return auditable count/RMSE/bias for already matched observation pairs."""
    valid = []
    for pair in pairs:
        try:
            obs, sim = float(pair['obs']), float(pair['sim'])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(obs) and math.isfinite(sim):
            valid.append((obs, sim))
    if not valid:
        raise ValueError('No finite matched observation/model pairs')
    errors = [sim - obs for obs, sim in valid]
    return {'count': len(valid),
            'rmse': math.sqrt(sum(error * error for error in errors) / len(errors)),
            'bias': sum(errors) / len(errors)}


def pair_ravn_records(records, model_by_variable, max_time_gap_hours):
    """Pair a single time window's canonical Ravn rows with GOTM columns.

    ``model_by_variable`` values must be produced from the trial's native
    ``output.nc`` via the existing server native-observation model adapter.
    This keeps the same unit, time, depth, lake identity and exclusion rules
    used by comparison and calibration elsewhere in the application.
    """
    from observation_matching import pair_observations

    groups = {}
    for record in records:
        groups.setdefault(record.get('variable'), []).append(record)
    all_pairs, diagnostics, per_variable = [], [], {}
    for variable, rows in groups.items():
        model = model_by_variable.get(variable)
        if model is None:
            diagnostics.extend({'variable': variable, 'reason': 'model_variable_unavailable',
                                'source_line': row.get('source_line')} for row in rows)
            continue
        pairs, excluded = pair_observations(rows, model,
                                            max_time_gap_hours=max_time_gap_hours)
        all_pairs.extend(pairs)
        diagnostics.extend({'variable': variable, **row} for row in excluded)
        if pairs:
            per_variable[variable] = aggregate_pair_metrics(pairs)
    try:
        metrics = aggregate_pair_metrics(all_pairs)
    except ValueError:
        metrics = None
    return {'metrics': metrics, 'per_variable': per_variable,
            'pairs': all_pairs, 'diagnostics': diagnostics}


def match_ravn_split(records, model_by_variable, max_time_gap_hours):
    """Pair preregistered train and holdout sets, retaining all exclusions."""
    split = partition_ravn_records(records)
    result = {'windows': split['windows'], 'excluded_records': split['excluded']}
    for name in ('training', 'holdout'):
        result[name] = pair_ravn_records(split[name], model_by_variable, max_time_gap_hours)
    return result


def run_official_gotm_trial(trial_case, timeout=600):
    """Run the isolated trial with its bundled native release executable."""
    import subprocess
    import time

    from netcdf_io import open_dataset
    from gotm_working_copy import validate_gotm_output
    from solver_runtime import log_has_solver_failure, solver_environment

    case = Path(trial_case).resolve()
    executable, output = case / 'gotm_release.exe', case / 'output.nc'
    if not executable.is_file() or not (case / 'gotm.yaml').is_file():
        raise ValueError('GOTM trial requires gotm_release.exe and gotm.yaml in its isolated directory')
    if not (case / 'fabm.yaml').is_file():
        raise ValueError('GOTM trial has no fabm.yaml')
    input_hashes = {}
    for path in sorted(case.rglob('*')):
        if (not path.is_file() or path.is_symlink() or path.name == 'native_variable_metadata.json'
                or _ignore_generated(path.parent, [path.name])):
            continue
        input_hashes[path.relative_to(case).as_posix()] = sha256_file(path)
    try:
        gotm_config = yaml.safe_load((case / 'gotm.yaml').read_text(encoding='utf-8')) or {}
        time_config = gotm_config.get('time', {})
        expected_range = []
        for name in ('start', 'stop'):
            value = time_config[name]
            clock = value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
            expected_range.append(clock.strftime('%Y-%m-%d %H:%M:%S'))
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise ValueError('GOTM trial time range is missing or invalid') from exc
    for name in ('output.nc', 'restart.nc', 'model_run.log', 'run.log'):
        path = case / name
        if path.is_file():
            path.unlink()
    log_path = case / 'model_run.log'
    started_at = time.time()
    try:
        with log_path.open('w', encoding='utf-8', errors='replace') as log:
            result = subprocess.run([str(executable)], cwd=case,
                                    stdout=log, stderr=subprocess.STDOUT,
                                    env=solver_environment(executable), timeout=timeout,
                                    check=False)
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'GOTM trial timed out after {timeout}s',
                'log_sha256': sha256_file(log_path) if log_path.exists() else None}
    log_text = log_path.read_text(encoding='utf-8', errors='replace') if log_path.exists() else ''
    if result.returncode != 0 or log_has_solver_failure(log_text):
        return {'success': False, 'error': 'GOTM solver failed', 'returncode': result.returncode,
                'log_sha256': sha256_file(log_path), 'log_tail': log_text[-8192:]}
    validation = validate_gotm_output(case, open_dataset, started_at=started_at,
                                      expected_range=expected_range)
    if not validation['ready']:
        return {'success': False, 'error': 'GOTM output validation failed',
                'returncode': result.returncode, 'validation': validation,
                'log_sha256': sha256_file(log_path)}
    output_hash = sha256_file(output)
    sidecar = {'output_sha256': output_hash,
               'producer': 'wet_ravn_gotm_943d3c4',
               'run_log': 'model_run.log',
               'run_log_sha256': sha256_file(log_path)}
    (case / 'native_variable_metadata.json').write_text(
        json.dumps(sidecar, indent=2, sort_keys=True), encoding='utf-8')
    return {'success': True, 'returncode': result.returncode, 'validation': validation,
            'config_sha256': sha256_file(case / 'gotm.yaml'),
            'fabm_sha256': sha256_file(case / 'fabm.yaml'),
            'output_sha256': output_hash, 'log_sha256': sha256_file(log_path),
            'input_sha256': input_hashes,
            'input_manifest_sha256': hashlib.sha256(
                json.dumps(input_hashes, sort_keys=True, separators=(',', ':')).encode()
            ).hexdigest()}
