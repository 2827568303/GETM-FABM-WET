"""Run every built-in case in disposable short-run copies.

The source cases are never modified. Only the canonical input files are copied
to a fresh verification model tree; existing multi-gigabyte result files are
intentionally omitted so each case exercises a new solver run.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener

import netCDF4
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODEL_SOURCE = ROOT / "3DWET"
CASE_SOURCE = MODEL_SOURCE / "case"
INPUT_NAMES = {
    "bathymetry.nc", "fabm_init.nc", "fabm.yaml", "getm_fabm.inp",
    "getm.inp", "gotm_fabm.yaml", "gotmturb.nml", "initial_conditions.json",
    "lake_mask.txt", "meteo_input.txt", "meteo.nc", "output.yaml",
    "riverinfo.dat", "rivers.nc", "empty_stdin.txt",
}


def patch_case(source: Path, destination: Path, duration_seconds=1200,
               timestep=2, output_interval=60, keep_defaults=False) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        if item.is_file() and (item.name in INPUT_NAMES or item.suffix.lower() in {'.inp', '.yaml', '.nml'}):
            shutil.copy2(item, destination / item.name)
    if keep_defaults:
        return

    inp = destination / "getm.inp"
    text = inp.read_text(encoding="utf-8")
    start = datetime.strptime(re.search(r"(?im)^\s*start\s*=\s*['\"]([^'\"]+)", text)[1], "%Y-%m-%d %H:%M:%S")
    stop = start + timedelta(seconds=duration_seconds)
    replacements = {
        "timestep": str(timestep),
        "stop": repr(stop.strftime("%Y-%m-%d %H:%M:%S")),
        "step_2d": str(output_interval // timestep),
        "sync_2d": str(output_interval // timestep),
        "step_3d": str(output_interval // timestep),
        "sync_3d": str(output_interval // timestep),
        "save_3d": ".true.",
        "hotstart": ".false.",
        "save_initial": ".true.",
    }
    if os.environ.get("VERIFY_DISABLE_SAVE3D"):
        replacements["save_3d"] = ".false."
    for key, value in replacements.items():
        text = re.sub(r"(?im)^(\s*" + re.escape(key) + r"\s*=\s*)[^\r\n!]+",
                      lambda match, value=value: match.group(1) + value, text)
    inp.write_text(text, encoding="utf-8")

    # Preserve the scientific output subscription, including ecology/fish.
    # Only cadence changes in this disposable copy.
    output = destination / 'output.yaml'
    output_text = output.read_text(encoding='utf-8') if output.exists() else (
        'output:\n   time_unit: second\n   time_step: 60\n   sync_interval: 1\n   variables:\n      - source: *\n')
    for key, value in {'time_unit': 'second', 'time_step': output_interval, 'sync_interval': 1}.items():
        output_text = re.sub(r'(?m)^(\s*' + key + r'\s*:\s*)[^\r\n]+',
                             lambda m, value=value: m[1] + str(value), output_text)
    output.write_text(output_text, encoding='utf-8')


def prepare_model(work: Path, names: list[str], model_source: Path,
                  duration_seconds=1200, timestep=2, output_interval=60, keep_defaults=False) -> None:
    model = work / "3DWET"
    (model / "case").mkdir(parents=True)
    (model / "bin").mkdir(parents=True)
    shutil.copy2(model_source / "bin" / "getm_cartesian.exe", model / "bin")
    shutil.copytree(model_source / "bin" / "runtime", model / "bin" / "runtime")
    templates = model_source / 'model_builder' / 'templates'
    if templates.is_dir():
        shutil.copytree(templates, model / 'model_builder' / 'templates')
    for name in names:
        patch_case(model_source / "case" / name, model / "case" / name,
                   duration_seconds, timestep, output_interval, keep_defaults)


def api(opener, url: str, path: str, data=None, timeout=60):
    body = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(url + path, data=body, headers={"Content-Type": "application/json"})
    with opener.open(request, timeout=timeout) as response:
        raw = response.read()
        return json.loads(raw)


def model_scoped_registry_path(state_root: Path, model_root: Path) -> Path:
    """Match ModelRootLease._model_key() from the app runtime."""
    root=Path(model_root).resolve()
    identity=os.path.normcase(str(root))
    key=hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]
    return Path(state_root).resolve()/'.studio-runtime'/'models'/key/'service.json'


def isolated_launcher_environment(work: Path, environ=None):
    """Give a verifier attempt private model, case, and runtime-state roots."""
    base=os.environ if environ is None else environ
    work=Path(work).resolve()
    model_root=(work/'3DWET').resolve()
    case_root=(work/'case-storage').resolve()
    state_root=(work/'case-state').resolve()
    env=dict(base,WET_MODEL_ROOT=str(model_root),WET_CASE_DIR=str(case_root),
             WET_CASE_STATE_DIR=str(state_root))
    return env,model_root,state_root


def wait_for_service(work: Path, process: subprocess.Popen, timeout: float = 60,
                     state_root: Path | None = None, model_root: Path | None = None) -> str:
    expected_root=Path(model_root or (work/'3DWET')).resolve()
    if state_root is None:
        registries=[work/'3DWET'/'.studio-runtime'/'service.json']
    else:
        scoped=model_scoped_registry_path(state_root,expected_root)
        # Runtime first uses the shared state registry, then moves to the
        # model-scoped path when that registry is owned by a different root.
        registries=[scoped,Path(state_root).resolve()/'.studio-runtime'/'service.json']
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"launcher stopped with exit code {process.returncode}")
        try:
            record=next((json.loads(registry.read_text(encoding='utf-8'))
                         for registry in registries if registry.is_file()),None)
            if record is None:
                raise FileNotFoundError('service registry was not published')
            if os.path.normcase(str(Path(record.get('model_root','')).resolve())) != os.path.normcase(str(expected_root)):
                raise ValueError('Registry model root does not match this isolated work tree')
            # A Windows venv redirector / frozen bootstrap may launch a child
            # with a different PID. Check actual readiness and instance ID;
            # a stale service.json alone is never sufficient.
            opener = build_opener(ProxyHandler({}))
            with opener.open(record['url'] + '/api/system/health', timeout=1) as response:
                health = json.load(response)
            if health.get('instance_id') != record.get('instance_id') or not health.get('ready'):
                raise ValueError('Registry instance is not ready')
            return record["url"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError, URLError, HTTPError, ValueError):
            time.sleep(.1)
    raise TimeoutError("service registry was not published")


def finite_output(path: Path, wet=None, expected_stop=None) -> dict:
    result = {"path": path.name, "time_records": 0, "variables": 0, "nonfinite": []}
    with netCDF4.Dataset(path) as dataset:
        if "time" in dataset.dimensions:
            result["time_records"] = len(dataset.dimensions["time"])
        result["variables"] = len(dataset.variables)
        if result["time_records"] and "time" in dataset.variables:
            t = dataset.variables['time']
            if not hasattr(t, 'units'):
                raise ValueError(f'{path.name}: time units missing')
            decoded = netCDF4.num2date(t[:], t.units, calendar=getattr(t, 'calendar', 'standard'))
            if not np.all(np.diff(np.asarray(t[:], dtype=float)) > 0):
                raise ValueError(f'{path.name}: non-increasing time coordinate')
            last = datetime.strptime(decoded[-1].strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            result['final_time'] = last.strftime('%Y-%m-%d %H:%M:%S')
            if expected_stop and abs((last - expected_stop).total_seconds()) > 1:
                raise ValueError(f'{path.name}: final time {last} != expected stop {expected_stop}')
        result['fields'] = {}
        for name, variable in dataset.variables.items():
            if not np.issubdtype(variable.dtype, np.number):
                continue
            # Scan every record in bounded slabs: early divergence must not be
            # hidden by a finite final frame, and no entire year is loaded.
            if not variable.dimensions or variable.dimensions[0] != 'time':
                continue
            valid_count = 0
            wet_count = 0
            masked_wet = 0
            for t_index in range(variable.shape[0]):
                slab = np.ma.asarray(variable[t_index])
                values = slab.compressed()
                valid_count += int(values.size)
                if values.size and not np.isfinite(values).all():
                    result['nonfinite'].append(name)
                if wet is not None and slab.ndim >= 2 and slab.shape[-2:] == wet.shape:
                    # Native legacy .3d.nc has an additional fully masked
                    # vertical boundary index; it is not a physical layer.
                    if path.name.endswith('.3d.nc') and slab.ndim == 3:
                        keep = ~np.ma.getmaskarray(slab).all(axis=(-2, -1))
                        slab = slab[keep]
                    on_water = slab[..., wet]
                    wet_count += int(on_water.compressed().size)
                    masked_wet += int(np.count_nonzero(np.ma.getmaskarray(on_water)))
            result['fields'][name] = dict(finite_values=valid_count, wet_values=wet_count,
                                          masked_wet_values=masked_wet, ndim=variable.ndim)
            if name in {'temp', 'hn', 'D', 'z'} and (wet_count == 0 or masked_wet):
                raise ValueError(f'{path.name}: {name} lacks valid values at {masked_wet} wet cells')
    return result


def validate_case_outputs(case_path, expected_stop):
    candidates = sorted({p for directory in (case_path, case_path / 'output')
                         for p in directory.glob('*.nc')
                         if p.name == 'output.nc' or p.name.endswith(('.2d.nc', '.3d.nc'))})
    if not candidates:
        raise ValueError('No model output files were produced in root or output/')
    with netCDF4.Dataset(case_path / 'bathymetry.nc') as ds:
        wet = np.ma.filled(ds.variables['bathymetry'][:] > 0, False)
    if not wet.any():
        raise ValueError('Input bathymetry has no wet cells')
    reports, skipped, fields = {}, [], set()
    for path in candidates:
        with netCDF4.Dataset(path) as ds:
            records = len(ds.dimensions.get('time', []))
        if records == 0:
            skipped.append(str(path.relative_to(case_path)))
            continue
        item = finite_output(path, wet, expected_stop)
        if item['nonfinite']:
            raise ValueError(f'{path.name}: nonfinite output variables {item["nonfinite"]}')
        if item['time_records'] < 2:
            raise ValueError(f'{path.name}: fewer than two output frames')
        reports[str(path.relative_to(case_path)).replace('\\', '/')] = item
        fields.update(item['fields'])
    if not reports or not {'temp', 'hn', 'D', 'z'}.issubset(fields):
        raise ValueError(f'Missing meaningful hydro output fields: {sorted(fields)}')
    return dict(files=reports, skipped_empty_shells=skipped, wet_cells=int(wet.sum()))


def run_all_cases(names, runner):
    results = []
    for name in names:
        try:
            results.append(runner(name))
        except Exception as error:
            results.append(dict(case=name, passed=False, error=f'{type(error).__name__}: {error}'))
        print(json.dumps({'case': name, 'passed': results[-1]['passed'],
                          'error': results[-1].get('error')}, ensure_ascii=False), flush=True)
    return results


def run_case(opener, url: str, name: str, case_path: Path, timeout: float,
             poll_interval: float = 0.5, results_only=False, verify_features=True) -> dict:
    report = {"case": name, "passed": False}
    loaded = api(opener, url, "/api/case/load", {"case_name": name})
    if not loaded.get("success"):
        raise RuntimeError(f"load failed: {loaded}")
    report["inputs"] = api(opener, url, "/api/case/inputs")
    report["grid"] = api(opener, url, "/api/geo/grid")
    report["network"] = api(opener, url, "/api/ecology/network")
    report["points"] = api(opener, url, "/api/calibration/points")
    report["preflight"] = api(opener, url, "/api/run/check")
    if not results_only and not report["preflight"].get("ok"):
        raise RuntimeError(f"preflight blocked: {report['preflight']}")
    if results_only:
        report['run'] = dict(status='existing_results', reason='Native process was not launched in this results-only pass')
    else:
        started = api(opener, url, "/api/run/start", {})
        if not started.get("success"):
            raise RuntimeError(f"start failed: {started}")
        deadline = time.monotonic() + timeout
        status = None
        while time.monotonic() < deadline:
            status = api(opener, url, "/api/run/status")
            if status.get("status") != "running":
                break
            time.sleep(poll_interval)
        report["run"] = status
        if not status or status.get("status") != "completed":
            api(opener, url, '/api/run/stop', {})
            raise RuntimeError(f"run did not complete: {status}")

    text = (case_path / 'getm.inp').read_text(encoding='utf-8')
    expected = datetime.strptime(re.search(r"(?im)^\s*stop\s*=\s*['\"]([^'\"]+)", text)[1], '%Y-%m-%d %H:%M:%S')
    report["outputs"] = validate_case_outputs(case_path, expected)
    report["variables"] = api(opener, url, "/api/results/variables")
    report["dashboard"] = api(opener, url, "/api/dashboard/summary")
    report["surface"] = api(opener, url, "/api/results/3d_surface?var=temp&target=16")
    if not report["surface"].get("bottom") or not report["surface"].get("shape"):
        raise RuntimeError("3D surface response did not contain lake geometry")
    if verify_features:
        from verify_external_workflow import APIProbe, verify_result_features, coverage_report
        probe = APIProbe(opener, url)
        report['result_features'] = verify_result_features(probe, case_path)
        report['api_calls'] = probe.calls
        report['route_coverage'] = coverage_report(probe)
        if not report['result_features']['passed']:
            report['error'] = 'Result features failed: ' + ', '.join(report['result_features']['failed'])
            return report
    report["passed"] = True
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument('--duration-seconds', type=int, default=1200,
                        help='Model duration per case, default 20 minutes; use 3600 for one hour')
    parser.add_argument('--timestep', type=int, default=2)
    parser.add_argument('--output-interval', type=int, default=60)
    parser.add_argument('--repetitions', type=int, default=1)
    parser.add_argument('--keep-defaults', action='store_true',
                        help='Copy built-in input configurations byte-for-byte and verify their configured run periods')
    parser.add_argument('--results-only', action='store_true',
                        help='Validate existing isolated --work/3DWET outputs and APIs without rerunning the solver')
    parser.add_argument("--model-source", type=Path, default=MODEL_SOURCE,
                        help="Model root containing bin/ and case/; defaults to the source tree")
    parser.add_argument('--solver',type=Path,help='Candidate solver copied only into the isolated verification tree')
    parser.add_argument("--launcher", type=Path, default=ROOT / "3DWET" / "app" / "launcher.py",
                        help="Launcher script/executable; defaults to the source launcher")
    parser.add_argument("--case", action="append", dest="selected_cases",
                        help="Only verify this case (repeat the option for multiple cases)")
    parser.add_argument("--poll-interval", type=float, default=0.5,
                        help="Seconds between run status polls")
    args = parser.parse_args()
    if args.duration_seconds < 1200 or args.repetitions < 1 or args.timestep < 1 or args.output_interval < args.timestep or args.output_interval % args.timestep or args.duration_seconds % args.output_interval:
        parser.error('Require duration >=1200 divisible by output interval, interval divisible by timestep, and repetitions >=1')
    work = args.work.resolve()
    if work.exists() and not args.results_only:
        raise SystemExit("Use a fresh --work directory; existing data is never removed.")
    if args.results_only and not (work / '3DWET' / 'case').is_dir():
        parser.error('--results-only requires an existing verification work tree')
    work.mkdir(parents=True, exist_ok=args.results_only)
    model_source = (work / '3DWET') if args.results_only else args.model_source.resolve()
    case_source = model_source / "case"
    names = sorted(path.name for path in case_source.iterdir()
                   if path.is_dir() and (path / "getm.inp").exists())
    if args.selected_cases:
        unknown = sorted(set(args.selected_cases) - set(names))
        if unknown:
            raise SystemExit(f"Unknown case(s): {', '.join(unknown)}")
        names = [name for name in names if name in set(args.selected_cases)]
    if not args.results_only:
        prepare_model(work, names, model_source, args.duration_seconds, args.timestep, args.output_interval, args.keep_defaults)
        if args.solver:shutil.copy2(args.solver,work/'3DWET/bin/getm_cartesian.exe')
    report_path = work / ('verification.results.json' if args.results_only else 'verification.json')
    env,model_root,state_root = isolated_launcher_environment(work)
    stdout = (work / "launcher.stdout.log").open("w", encoding="utf-8")
    stderr = (work / "launcher.stderr.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        ([sys.executable, str(args.launcher)] if args.launcher.suffix.lower() == ".py"
         else [str(args.launcher)]) + ["--web", "--no-open", "--port", "0"],
        cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
    )
    opener = build_opener(ProxyHandler({}))
    report = {"cases": names, "results": [], "passed": False,
              'duration_seconds': args.duration_seconds, 'repetitions': args.repetitions,
              'results_only': args.results_only, 'keep_defaults': args.keep_defaults,
              'scope': 'Short native integration and numerical-finiteness checks; not scientific accuracy or annual stability validation.'}
    url = None
    try:
        url = wait_for_service(work, process, state_root=state_root, model_root=model_root)
        health = api(opener, url, "/api/system/health")
        report["health"] = health
        listed = api(opener, url, "/api/cases")
        report["listed_cases"] = [item["name"] for item in listed]
        if not set(names).issubset(set(report['listed_cases'])):
            raise RuntimeError(f"case listing mismatch: {report['listed_cases']} != {names}")
        for repetition in range(args.repetitions):
            results = run_all_cases(names, lambda name: run_case(opener, url, name,
                work / '3DWET' / 'case' / name, args.timeout, args.poll_interval,
                results_only=args.results_only))
            for result in results:
                result['repetition'] = repetition + 1
            report['results'].extend(results)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        report["passed"] = bool(report['results']) and all(x['passed'] for x in report['results'])
    except Exception as error:
        report["error"] = str(error)
    finally:
        if url and process.poll() is None:
            try:
                api(opener, url, "/api/run/stop", {}, timeout=15)
            except Exception:
                pass
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        stdout.close()
        stderr.close()
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps({"passed": report.get("passed"), "cases": report.get("cases"),
                          "results": [{"case": x.get("case"), "passed": x.get("passed"),
                                       "status": x.get("run", {}).get("status")}
                                      for x in report.get("results", [])],
                          "error": report.get("error")}, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == "__main__":
    raise SystemExit(main())
