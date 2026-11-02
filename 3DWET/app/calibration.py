"""3DWET Auto-calibration engines.

Provides:
- patch_fabm_parameters: write a list of {module, param, value} into a fabm.yaml
- run_model_in_temp: run the model with patched parameters in a temp copy
- CalibrationEngine (ABC), ScipyEngine (L-BFGS-B), PyabcEngine (ABC-SMC, lazy)
- CalibrationJob: background-thread job tracker with status/progress/history

The objective function aggregates RMSE across all calibration points and
their declared variables (lower is better). The model runs via WSL just like
the normal run endpoint, but in an isolated temp directory so the original
case files are untouched.
"""
import os
import json
import time
import shutil
import subprocess
import tempfile
import threading
import traceback
import copy
import re
from abc import ABC, abstractmethod
from contextlib import nullcontext
from pathlib import Path
from datetime import datetime

import numpy as np
import yaml
import netCDF4 as nc
from netcdf_io import open_dataset
from run_output_health import validate_current_run_outputs
from solver_runtime import log_has_solver_failure


def _calibration_copy_ignore(directory, names):
    """Keep arbitrary nested inputs while excluding generated run artifacts."""
    generated = {'output', 'out', 'outputs', 'results', 'logs', 'log', 'backups',
                 'backup', 'cache', '__pycache__', '.studio-runtime'}
    return [name for name in names if name.lower() in generated
            or name.lower() == 'output.nc'
            or name.lower().endswith(('.2d.nc', '.3d.nc', '.log', '.bak'))
            or (Path(directory) / name).is_symlink()]


def _validate_trial_output(case_path, started_at):
    # Use the same lock as API NetCDF readers: separate files still share the
    # non-thread-safe native library. Standalone tests do not need a server.
    import sys
    context = sys.modules.get('server')
    lock = getattr(context, '_NC_LOCK', None)
    with lock if lock is not None else nullcontext():
        health = validate_current_run_outputs(case_path, open_dataset, started_at=started_at)
        if not health['ready']:
            return health
        text = (case_path / 'getm.inp').read_text(encoding='utf-8-sig')
        stop = re.search(r"(?im)^\s*stop\s*=\s*['\"]([^'\"]+)", text)
        if stop:
            expected = datetime.strptime(stop[1], '%Y-%m-%d %H:%M:%S')
            # A file with finite values can still be an early/incomplete run.
            for item in health['files']:
                with open_dataset(case_path / item['file']) as ds:
                    coordinate = ds.variables.get('time')
                    if coordinate is None or not getattr(coordinate, 'units', None):
                        health['errors'].append(f"{item['file']}: time coordinate/units missing")
                        continue
                    final = nc.num2date(coordinate[-1], coordinate.units,
                                       calendar=getattr(coordinate, 'calendar', 'standard'))
                    actual = datetime(final.year, final.month, final.day, final.hour,
                                      final.minute, final.second, final.microsecond)
                    item['final_time'] = actual.isoformat()
                    from output_schedule import last_output_time
                    scheduled = last_output_time(case_path, item['file'], text, expected)
                    item['scheduled_final_time'] = scheduled.isoformat()
                    if abs((actual - scheduled).total_seconds()) > 1:
                        health['errors'].append(f"{item['file']}: final time {actual} differs from scheduled final time {scheduled} (configured stop {expected})")
            health['ready'] = not health['errors'] and not health['bad_variables']
        return health

# Late imports from server (avoids circular import at module load)
def _server_helpers(case_path=None, reload_calibration=False):
    import server as context
    from lake_points_api import effective_calibration_points
    with context._NC_LOCK:
        def matching_case():
            return (context.active_case_path and
                    Path(context.active_case_path).resolve() == Path(case_path).resolve())
        if case_path is not None and not matching_case():
            raise ValueError('案例已切换，无法创建自动率定测站快照')
        if reload_calibration:
            context.load_calibration()
        points = effective_calibration_points(context)
        data = copy.deepcopy(context.calibration_data)
        if case_path is not None and not matching_case():
            raise ValueError('案例已切换，请重新创建自动率定任务')
    return (context.wsl_path, context.find_output_files, context.get_timeseries,
            context.load_calibration, points, data,
            context._pair_obs_sim, context.EXE_PATH)


def patch_fabm_parameters(fabm_path, params):
    """Patch a list of {module, param, value} into a fabm.yaml file."""
    with open(fabm_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    instances = raw.get("instances", {})
    for p in params:
        m = p["module"]; k = p["param"]; v = p["value"]
        if m in instances and isinstance(instances[m], dict):
            if "parameters" not in instances[m] or not isinstance(instances[m]["parameters"], dict):
                instances[m]["parameters"] = {}
            instances[m]["parameters"][k] = v
    with open(fabm_path, "w", encoding="utf-8") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def run_model_in_temp(case_path, params, timeout=600, keep_temp=False, points_snapshot=None,
                     observations_snapshot=None, max_time_gap_hours=None):
    """Run the model with patched parameters in a temp copy of the case dir.

    Returns dict:
      success: bool
      outputs: {f"{point_id}/{var}": {times, values, ...}} (when success)
      returncode: int (when subprocess ran)
      error: str (on failure)
      temp_dir: str (when keep_temp=True)
    """
    (wsl_path, find_output_files, get_timeseries,
     load_calibration, calibration_points, calibration_data,
     _pair_obs_sim, EXE_PATH) = _server_helpers(case_path if points_snapshot is None else None)
    if points_snapshot is not None:
        calibration_points = copy.deepcopy(points_snapshot)

    case_path = Path(case_path)
    tmp_dir = tempfile.mkdtemp(prefix="3dwet_calib_")
    try:
        # Copy case files to temp dir (inputs + bathymetry + getm.inp + fabm.yaml etc.)
        excluded = set(_calibration_copy_ignore(case_path, [p.name for p in case_path.iterdir()]))
        for item in case_path.iterdir():
            if item.name in excluded:
                continue
            target = Path(tmp_dir) / item.name
            if item.is_file():
                shutil.copy2(item, target)
            elif item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True, ignore=_calibration_copy_ignore)

        fabm_path = Path(tmp_dir) / "fabm.yaml"
        if not fabm_path.exists():
            return {"success": False, "error": "fabm.yaml 不存在于案例目录"}
        patch_fabm_parameters(fabm_path, params)

        tmp_path = Path(tmp_dir)
        calib_log = tmp_path / "calib_run.log"
        is_native = str(EXE_PATH).lower().endswith(".exe")
        started_at = time.time()
        finished_by_watchdog = False
        try:
            if is_native:
                # Native Windows exe: run directly with MinGW runtime DLLs on PATH.
                # Popen + CPU watchdog instead of subprocess.run: the MinGW exe
                # can freeze in its exit path after the run finished (output is
                # already flushed), which would otherwise burn the whole timeout
                # in every calibration iteration.
                from server import MSYS_UCRT_BIN, get_process_cpu_seconds
                from solver_runtime import solver_environment
                env = solver_environment(EXE_PATH)
                log_fh = open(calib_log, "w", encoding="utf-8", errors="replace")
                try:
                    proc = subprocess.Popen(
                        [str(EXE_PATH)], cwd=str(tmp_path),
                        stdout=log_fh, stderr=subprocess.STDOUT, env=env)
                    last_cpu, cpu_stall = None, 0
                    t0 = time.time()
                    while proc.poll() is None:
                        time.sleep(1.0)
                        if time.time() - t0 > timeout:
                            proc.kill()
                            proc.wait(timeout=10)
                            raise subprocess.TimeoutExpired(cmd=str(EXE_PATH),
                                                            timeout=timeout)
                        cpu = get_process_cpu_seconds(proc)
                        if cpu is not None:
                            if last_cpu is not None and (cpu - last_cpu) < 0.05:
                                cpu_stall += 1
                            else:
                                cpu_stall = 0
                            last_cpu = cpu
                            if cpu_stall >= 90 and (time.time() - t0) > 60:
                                # Simulation finished; reclaim the hung process.
                                proc.terminate()
                                finished_by_watchdog = True
                                try:
                                    proc.wait(timeout=30)
                                except Exception:
                                    proc.kill()
                                break

                    class _Result:
                        pass
                    result = _Result()
                    result.returncode = proc.returncode
                finally:
                    log_fh.close()
            else:
                case_wsl = wsl_path(tmp_path)
                exe_wsl = wsl_path(str(EXE_PATH))
                log_wsl = wsl_path(str(calib_log))
                cmd = ["wsl.exe", "bash", "-c",
                       f"cd '{case_wsl}' && '{exe_wsl}' > '{log_wsl}' 2>&1"]
                result = subprocess.run(cmd, timeout=timeout,
                                        capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"模型运行超时 ({timeout}s)",
                    "temp_dir": tmp_dir if keep_temp else None}
        except Exception as e:
            return {"success": False, "error": f"subprocess 调用失败: {e}",
                    "temp_dir": tmp_dir if keep_temp else None}

        log_text = calib_log.read_text(encoding='utf-8', errors='replace') if calib_log.exists() else ''
        completed_watchdog = finished_by_watchdog and 'getm: Completed on' in log_text
        if log_has_solver_failure(log_text) or (result.returncode != 0 and not completed_watchdog):
            return {'success': False, 'error': 'Calibration solver failed; see calib_run.log',
                    'returncode': result.returncode, 'log_tail': log_text[-8192:],
                    'temp_dir': tmp_dir if keep_temp else None}
        try:
            health = _validate_trial_output(tmp_path, started_at)
        except (OSError, ValueError, RuntimeError, KeyError, IndexError) as error:
            return {'success': False, 'error': f'Calibration output validation failed: {error}',
                    'temp_dir': tmp_dir if keep_temp else None}
        if not health['ready']:
            return {'success': False, 'error': 'Calibration outputs failed current-run integrity checks',
                    'output_health': health, 'temp_dir': tmp_dir if keep_temp else None}
        files = find_output_files(tmp_path)
        nc_path = files["3d"] or files["2d"]
        if not nc_path:
            tail = ""
            try:
                with open(tmp_path / "calib_run.log", "r", encoding="utf-8", errors="replace") as fh:
                    tail = "".join(fh.readlines()[-30:])
            except Exception:
                pass
            return {"success": False,
                    "error": "模型未生成输出文件 (检查 calib_run.log)",
                    "log_tail": tail,
                    "temp_dir": tmp_dir if keep_temp else None}

        outputs = {}
        strict_records = (observations_snapshot or {}).get('records', [])
        if strict_records:
            from observation_matching import pair_observations
            import server as context
            for point in calibration_points:
                for var in point.get('variables', []):
                    observation_point_id = point.get('point_id', point['id'])
                    rows = [row for row in strict_records
                            if row.get('point_id') == observation_point_id and row.get('variable') == var]
                    if not rows:
                        continue
                    key = f"{point['id']}/{var}"
                    try:
                        target = dict(point)
                        target.setdefault('point_id', observation_point_id)
                        model = context._native_observation_model(nc_path, var, target)
                        model['mass_basis'] = point.get('mass_basis', model.get('mass_basis'))
                        pairs, diagnostics = pair_observations(rows, model,
                                                              max_time_gap_hours=max_time_gap_hours)
                        outputs[key] = {'observation_pairs': pairs, 'diagnostics': diagnostics,
                                        'native_model': model, 'downsampled': False}
                    except (OSError, ValueError, KeyError, IndexError) as exc:
                        outputs[key] = {'observation_pairs': [],
                                        'diagnostics': [{'reason': str(exc)}],
                                        'downsampled': False}
        else:
            for point in calibration_points:
                for var in point.get("variables", []):
                    ts = get_timeseries(nc_path, var, i=point["i"], j=point["j"])
                    if ts:
                        outputs[f"{point['id']}/{var}"] = ts
        resp = {"success": True, "outputs": outputs, "output_health": health,
                "returncode": result.returncode}
        if keep_temp:
            resp["temp_dir"] = tmp_dir
        return resp
    finally:
        if not keep_temp:
            try:
                shutil.rmtree(tmp_dir)
            except Exception:
                pass


def validate_objective_weights(points, weights):
    """Validate explicit station-variable weights and residual scales."""
    if weights is None:
        return []
    if not isinstance(weights, list):
        raise ValueError('率定权重必须为列表')
    available = {(p['id'], var) for p in points for var in p.get('variables', [])}
    seen, result = set(), []
    for row in weights:
        if not isinstance(row, dict):
            raise ValueError('率定权重条目格式错误')
        pair = (row.get('point_id'), row.get('variable'))
        if any(not isinstance(x, str) for x in pair) or pair not in available or pair in seen:
            raise ValueError('权重引用未知、未选择或重复的点位/变量')
        try:
            weight, scale = float(row.get('weight', 1)), float(row.get('scale', 1))
        except (ValueError, TypeError) as exc:
            raise ValueError('权重及尺度必须为数值') from exc
        if not np.isfinite(weight) or weight < 0 or not np.isfinite(scale) or scale <= 0:
            raise ValueError('权重必须非负，尺度必须为有限正数')
        seen.add(pair)
        result.append(dict(point_id=pair[0], variable=pair[1], weight=weight, scale=scale))
    if available and len(seen) == len(available) and not any(r['weight'] > 0 for r in result):
        raise ValueError('至少一个点位/变量权重必须大于零')
    return result


def validate_calibration_observations(points, data, observations, weights, objective):
    """Fail before solver work when selected objective series have no usable observations."""
    weight_map = {(row['point_id'], row['variable']): row['weight'] for row in weights}
    records = (observations or {}).get('records', [])
    values_for_objective = []
    uncovered = []
    for point in points:
        point_id = point.get('point_id', point.get('id'))
        for variable in point.get('variables', []):
            key = (point['id'], variable)
            if weight_map.get(key, 1) <= 0:
                continue
            if records:
                values = [record.get('value') for record in records
                          if record.get('point_id') == point_id and record.get('variable') == variable]
            else:
                values = [row.get('value') if isinstance(row, dict) else row
                          for row in (data.get(point['id'], {}).get(variable, []) or [])]
            usable = []
            for value in values:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                if np.isfinite(value):
                    usable.append(value)
            if not usable:
                uncovered.append(f"{point['id']}/{variable}")
            values_for_objective.extend(usable)
    if uncovered:
        raise ValueError('所选率定目标缺少可用观测数据: ' + ', '.join(uncovered))
    if not values_for_objective:
        raise ValueError('所选点位与变量没有可用观测数据')
    if objective in ('nse', 'r2') and (len(values_for_objective) < 2 or
                                       max(values_for_objective) == min(values_for_objective)):
        raise ValueError(f'{objective.upper()} 至少需要两个不同的有效观测值')


def compute_objective(outputs, objective_name="rmse", points_snapshot=None, data_snapshot=None,
                      objective_weights=None, observations_snapshot=None):
    """Aggregate objective across all calibration points/variables.

    outputs: dict from run_model_in_temp (keyed by "point_id/var")
    Reads calibration_data from server for observed series.
    Returns float (lower is better). Returns 1e10 on no pairs.
    """
    (_, _, _, load_calibration, calibration_points, calibration_data,
     _pair_obs_sim, _EXE) = _server_helpers(reload_calibration=points_snapshot is None or data_snapshot is None)
    if points_snapshot is not None:
        calibration_points = points_snapshot
    if data_snapshot is not None:
        calibration_data = data_snapshot

    weights = validate_objective_weights(calibration_points, objective_weights)
    if weights and objective_name != 'rmse':
        raise ValueError('显式权重及尺度目前仅适用于 RMSE')
    weight_map = {(row['point_id'], row['variable']): row for row in weights}
    series_mse, series_weights = [], []

    all_sim = []
    all_obs = []
    strict_records = (observations_snapshot or {}).get('records', [])
    if strict_records:
        # Once an official observation snapshot is selected, only the exact
        # native time/depth pairs produced for that snapshot may be scored.
        # Never fall back to the legacy nearest-time point data.
        for point in calibration_points:
            for var in point.get('variables', []):
                key = f"{point['id']}/{var}"
                observation_point_id = point.get('point_id', point['id'])
                row = weight_map.get((point['id'], var), {'weight': 1, 'scale': 1})
                selected = [record for record in strict_records
                            if record.get('point_id') == observation_point_id and record.get('variable') == var]
                if row['weight'] == 0 or (not selected and (point['id'], var) not in weight_map):
                    continue
                if key not in outputs or not selected:
                    return 1e10
                pairs = outputs[key].get('observation_pairs', [])
                if not pairs:
                    return 1e10
                residuals = np.array([float(pr['sim']) - float(pr['obs']) for pr in pairs], dtype=float)
                if not np.isfinite(residuals).all():
                    return 1e10
                if row['weight'] > 0:
                    series_mse.append(float(np.mean((residuals / row['scale']) ** 2)))
                    series_weights.append(row['weight'])
                all_sim.extend(float(pr['sim']) for pr in pairs)
                all_obs.extend(float(pr['obs']) for pr in pairs)
        n = len(all_sim)
        if n == 0:
            return 1e10
        sim = np.asarray(all_sim); obs = np.asarray(all_obs)
        err = sim - obs
        if objective_name == 'rmse':
            return float(np.sqrt(np.average(series_mse, weights=series_weights))) if series_weights else 1e10
        if objective_name == 'mae':
            return float(np.mean(np.abs(err)))
        if objective_name == 'nse':
            denom = np.sum((obs - obs.mean()) ** 2)
            return float(np.sum(err ** 2) / denom) if denom > 0 else 1e10
        if objective_name == 'r2':
            if obs.std() == 0 or sim.std() == 0:
                return 1e10
            corr = np.corrcoef(obs, sim)[0, 1]
            return float(1 - corr * corr) if np.isfinite(corr) else 1e10
        return float(np.sqrt(np.mean(err ** 2)))

    for point in calibration_points:
        for var in point.get("variables", []):
            key = f"{point['id']}/{var}"
            row = weight_map.get((point['id'], var), {'weight': 1, 'scale': 1})
            obs = calibration_data.get(point["id"], {}).get(var, [])
            if row['weight'] == 0 or (not obs and (point['id'], var) not in weight_map):
                continue
            if key not in outputs:
                return 1e10
            sim = outputs[key]
            pairs, _ = _pair_obs_sim(obs, sim)
            pairs = [pr for pr in pairs if np.isfinite(pr['sim']) and np.isfinite(pr['obs'])]
            if not pairs:
                return 1e10
            if pairs and row['weight'] > 0:
                residuals = np.array([pr['sim'] - pr['obs'] for pr in pairs], dtype=float) / row['scale']
                series_mse.append(float(np.mean(residuals ** 2)))
                series_weights.append(row['weight'])
            for pr in pairs:
                all_sim.append(pr["sim"])
                all_obs.append(pr["obs"])
    n = len(all_sim)
    if n == 0:
        return 1e10
    sim = np.array(all_sim); obs = np.array(all_obs)
    err = sim - obs
    if objective_name in ("rmse",):
        return float(np.sqrt(np.average(series_mse, weights=series_weights))) if series_weights else 1e10
    if objective_name == "mae":
        return float(np.mean(np.abs(err)))
    if objective_name == "nse":
        obs_mean = obs.mean()
        denom = np.sum((obs - obs_mean) ** 2)
        if denom <= 0:
            return 1e10
        # NSE: higher is better; convert to minimization form
        return float(1 - (1 - np.sum(err ** 2) / denom)) if False else float(np.sum(err ** 2) / denom)
    if objective_name == "r2":
        # Use 1 - R² (lower is better)
        if obs.std() == 0 or sim.std() == 0:
            return 1e10
        r = np.corrcoef(obs, sim)[0, 1]
        return float(1 - r * r) if not np.isnan(r) else 1e10
    # Default: RMSE
    return float(np.sqrt(np.mean(err ** 2)))


class CalibrationEngine(ABC):
    """Abstract calibration engine interface."""

    @abstractmethod
    def calibrate(self, params, objective_fn, callback=None, max_iter=100, squared_distance=False,
                  max_simulations=None):
        """Run calibration.

        params: list of {module, param, min, max}
        objective_fn: callable(param_list_with_value) -> float (lower = better)
        callback: optional callable(iteration, param_list, objective_value)
        Returns dict with success/best_params/best_objective/history[/error].
        """
        pass


class CalibrationStopped(RuntimeError):
    """Stop optimization immediately rather than interpreting it as bad data."""


def scipy_evaluation_budget(max_iter, parameter_count):
    """Bound model evaluations for finite-difference gradients and line search.

    One L-BFGS-B iteration may need up to two objective evaluations per
    parameter for a 3-point gradient, plus a new point for the line search.
    """
    return max(1, int(max_iter)) * (2 * max(1, int(parameter_count)) + 1)


class ScipyEngine(CalibrationEngine):
    """scipy.optimize.minimize with L-BFGS-B and parameter bounds."""

    def calibrate(self, params, objective_fn, callback=None, max_iter=100, squared_distance=False,
                  max_simulations=None):
        from scipy.optimize import minimize
        x0 = [(p["min"] + p["max"]) / 2.0 for p in params]
        bounds = [(p["min"], p["max"]) for p in params]
        max_evaluations = (scipy_evaluation_budget(max_iter, len(params))
                           if max_simulations is None else int(max_simulations))
        if max_evaluations < 1:
            raise ValueError('SciPy 最大模型评估次数必须为正整数')
        history = []
        iter_count = [0]

        class ExactDistanceFit(Exception):
            """A verified nonnegative distance reached its exact lower bound."""

        class EvaluationBudgetReached(Exception):
            """The configured budget counts costly model evaluations."""

        def _obj(x):
            # L-BFGS-B's maxiter counts optimizer steps, not calls to _obj.
            # Numerical finite differences and line searches can therefore
            # run many model simulations for one configured iteration. Enforce
            # the public calibration budget at the objective boundary.
            if iter_count[0] >= max_evaluations:
                raise EvaluationBudgetReached()
            ps = [{"module": p["module"], "param": p["param"], "value": float(v)}
                  for p, v in zip(params, x)]
            try:
                obj = float(objective_fn(ps))
                if not np.isfinite(obj):
                    obj = 1e10
            except CalibrationStopped:
                raise
            except Exception:
                obj = 1e10
            iter_count[0] += 1
            history.append({"iteration": iter_count[0], "params": ps, "objective": obj})
            if callback:
                try:
                    callback(iter_count[0], ps, obj)
                except Exception:
                    pass
            # Squared RMSE has the same minimizer and avoids the norm's cusp
            # near a perfect fit. Histories and public values retain RMSE.
            if squared_distance and obj == 0.0:
                raise ExactDistanceFit()
            return obj * obj if squared_distance else obj

        try:
            result = minimize(_obj, x0, method="L-BFGS-B", jac='3-point', bounds=bounds,
                              options={"maxiter": max_iter, "maxfun": max_evaluations,
                                       "finite_diff_rel_step": 1e-3})
            return {
                "success": bool(result.success),
                "best_params": [{"module": p["module"], "param": p["param"], "value": float(v)}
                                for p, v in zip(params, result.x)],
                "best_objective": float(np.sqrt(result.fun) if squared_distance else result.fun),
                "history": history,
                "n_iterations": iter_count[0],
                "max_evaluations": max_evaluations,
                "message": str(result.message),
                "engine": "scipy.lbfgsb",
            }
        except ExactDistanceFit:
            return {
                "success": True,
                "best_params": history[-1]['params'],
                "best_objective": 0.0,
                "history": history,
                "n_iterations": iter_count[0],
                "max_evaluations": max_evaluations,
                "message": "Exact zero distance reached; no further model evaluations required.",
                "engine": "scipy.lbfgsb",
            }
        except EvaluationBudgetReached:
            best = min(history, key=lambda item: item['objective'])
            return {
                "success": True,
                "budget_exhausted": True,
                "converged": False,
                "best_params": best['params'],
                "best_objective": best['objective'],
                "history": history,
                "n_iterations": iter_count[0],
                "max_evaluations": max_evaluations,
                "message": "Configured L-BFGS-B evaluation budget reached; returned the best observed trial.",
                "engine": "scipy.lbfgsb",
            }
        except Exception as e:
            return {"success": False, "error": str(e),
                    "history": history, "n_iterations": iter_count[0],
                    "max_evaluations": max_evaluations,
                    "engine": "scipy.lbfgsb"}


class PyabcEngine(CalibrationEngine):
    """pyABC ABC-SMC engine.

    pyabc is lazy-loaded. If unavailable, falls back to ScipyEngine and
    annotates the result so the UI can warn the user.
    """

    def calibrate(self, params, objective_fn, callback=None, max_iter=100,
                  population_size=10, max_simulations=None, minimum_epsilon=0,
                  database_path=None):
        try:
            import pyabc
            available = True
        except ImportError:
            available = False

        if not available:
            if max_simulations is None:
                raise ValueError('ABC-SMC 必须显式设置最大模型评估次数；降级运行也会遵守此上限')
            scipy_engine = ScipyEngine()
            result = scipy_engine.calibrate(params, objective_fn, callback, max_iter,
                                            max_simulations=max_simulations)
            result["fallback"] = "scipy (pyabc 未安装，已自动降级)"
            result["engine"] = "scipy-lbfgsb"
            return result

        from pyabc.sampler import SingleCoreSampler
        history = []
        best = {'params': [], 'objective': float('inf')}
        if max_simulations is None:
            raise ValueError('ABC-SMC 必须显式设置最大模型评估次数；每次评估都会运行一次完整模型')
        budget = int(max_simulations)
        if not params or population_size < 2 or max_iter < 1 or budget < 2 * population_size:
            raise ValueError('ABC-SMC 需要参数、至少两粒子及足够的求解预算')
        if not np.isfinite(minimum_epsilon) or minimum_epsilon < 0:
            raise ValueError('ABC-SMC 最小距离必须为有限非负数')
        names = [f'p{k}' for k in range(len(params))]
        prior = pyabc.Distribution(**{name: pyabc.RV('uniform', p['min'], p['max'] - p['min'])
                                      for name, p in zip(names, params)})

        def parameter_list(sample):
            return [dict(module=p['module'], param=p['param'], value=float(sample[name]))
                    for name, p in zip(names, params)]

        def model(sample):
            if len(history) >= budget:
                raise CalibrationStopped('达到 ABC-SMC 求解预算，当前种群未完成')
            ps = parameter_list(sample)
            value = float(objective_fn(ps))
            value = value if np.isfinite(value) and value >= 0 else 1e10
            history.append(dict(iteration=len(history)+1, params=ps, objective=value))
            if value < best['objective']:
                best.update(params=copy.deepcopy(ps), objective=value)
            if callback:
                callback(len(history), ps, value)
            return {'objective': value}

        base = dict(success=False, engine='pyabc-abcsmc', history=history,
                    n_iterations=0, posterior=[], populations=[])
        try:
            # Serial sampling keeps NetCDF access and native solver runs isolated.
            abc = pyabc.ABCSMC(model, prior, lambda x, y: x['objective'],
                               population_size=population_size,
                               sampler=SingleCoreSampler(check_max_eval=True))
            if database_path is not None:
                database_path = Path(database_path).resolve()
                database_path.parent.mkdir(parents=True, exist_ok=True)
            database = 'sqlite:///' + database_path.as_posix() if database_path else 'sqlite://'
            abc.new(database, {'objective': 0.0})
            stored = abc.run(minimum_epsilon=minimum_epsilon, max_nr_populations=max_iter,
                             max_total_nr_simulations=budget)
            frame, weights = stored.get_distribution(m=0)
            posterior = [dict(params=parameter_list(row), weight=float(weight))
                         for (_, row), weight in zip(frame.iterrows(), weights)]
            populations = [dict(population=int(row['t']), epsilon=float(row['epsilon']),
                                samples=int(row['samples']))
                           for _, row in stored.get_all_populations().iterrows() if row['t'] >= 0]
            base.update(success=bool(posterior) and best['objective'] < 1e10,
                        best_params=best['params'], best_objective=best['objective'],
                        posterior=posterior, populations=populations,
                        n_populations=int(stored.n_populations),
                        database_path=str(database_path) if database_path else None,
                        message='ABC-SMC 已完成；后验为接受粒子的归一化权重分布')
        except Exception as exc:
            base.update(error=str(exc), best_params=best['params'],
                        best_objective=best['objective'] if np.isfinite(best['objective']) else None)
        base['n_iterations'] = len(history)
        return base


# ── Job tracking ─────────────────────────────────────────────────────

calibration_jobs = {}  # job_id -> CalibrationJob
_job_lock = threading.Lock()


class CalibrationJob:
    """Tracks a single calibration run in a background thread."""

    def __init__(self, job_id, method, params, objective, max_iter, case_path, point_ids=None,
                 objective_weights=None, engine_options=None, max_time_gap_hours=None):
        self.job_id = job_id
        self.method = method            # parsac | pest | bayesian | sensitivity
        self.params = params            # list of {module, param, min, max}
        self.objective = objective      # rmse | nse | r2 | mae
        self.max_iter = max_iter
        self.case_path = Path(case_path)
        (_, _, _, _, self._points_snapshot, self._data_snapshot, _, _) = _server_helpers(
            self.case_path, reload_calibration=True)
        from observation_store import ObservationStore
        self._observations_snapshot = ObservationStore(self.case_path.parent).load(self.case_path.name)
        for record in self._observations_snapshot.get('records', []):
            source_row = record.get('source_row')
            if not record.get('point_id') and isinstance(source_row, dict) and source_row.get('point_id') not in (None, ''):
                record['point_id'] = str(source_row['point_id']).strip()
        self._observations_snapshot = copy.deepcopy(self._observations_snapshot)
        self.max_time_gap_hours = max_time_gap_hours
        if self._observations_snapshot.get('records'):
            if self.max_time_gap_hours is None:
                self.max_time_gap_hours = self._observations_snapshot.get('max_time_gap_hours')
            try:
                gap = float(self.max_time_gap_hours)
            except (TypeError, ValueError):
                gap = float('nan')
            if not np.isfinite(gap) or gap <= 0:
                raise ValueError('官方观测率定必须提供显式有限正数 max_time_gap_hours')
            self.max_time_gap_hours = gap
        available = {p['id'] for p in self._points_snapshot}
        if point_ids is not None:
            if (not isinstance(point_ids, list) or not point_ids
                    or any(not isinstance(pid, str) for pid in point_ids)
                    or len(set(point_ids)) != len(point_ids)):
                raise ValueError('请至少选择一个有效且不重复的率定点位')
            if set(point_ids) - available:
                raise ValueError('所选率定点位不存在，请刷新点位列表')
            selected = set(point_ids)
            self._points_snapshot = [p for p in self._points_snapshot if p['id'] in selected]
        self._points_snapshot = copy.deepcopy(self._points_snapshot)
        self.point_ids = [p['id'] for p in self._points_snapshot]
        self._data_snapshot = copy.deepcopy({pid: self._data_snapshot.get(pid, {})
                                            for pid in self.point_ids})
        self.objective_weights = validate_objective_weights(self._points_snapshot, objective_weights)
        if self.objective_weights and objective != 'rmse':
            raise ValueError('显式权重及尺度目前仅适用于 RMSE')
        if self.params:
            validate_calibration_observations(self._points_snapshot, self._data_snapshot,
                                               self._observations_snapshot,
                                               self.objective_weights, objective)
        self.engine_options = dict(engine_options or {})
        self.status = "running"         # running | completed | failed | stopped
        self.progress = 0.0             # 0..1
        self.history = []
        self.result = None
        self.error = None
        self.fallback = None
        self.engine_name = 'pyabc-abcsmc' if method == 'pyabc' else 'scipy-lbfgsb'
        self.start_time = datetime.now().isoformat()
        self.end_time = None
        self._thread = None
        self._stop_flag = False

    def _run(self):
        try:
            trial_errors = []
            engine = PyabcEngine() if self.method == 'pyabc' else ScipyEngine()
            if self.method == 'pyabc':
                try:
                    import pyabc
                except ImportError:
                    engine = ScipyEngine()
                    self.engine_name = 'scipy-lbfgsb'
                    self.fallback = 'scipy (pyabc 未安装，已自动降级)'
            if self.method not in ('scipy', 'pyabc'):
                self.fallback = f"旧配置 {self.method} 使用 SciPy L-BFGS-B 有界优化；未执行 PEST、GLUE 或 MCMC。"

            def objective_fn(param_list):
                if self._stop_flag:
                    raise CalibrationStopped("用户停止")
                res = run_model_in_temp(self.case_path, param_list, timeout=600,
                                        points_snapshot=self._points_snapshot,
                                        observations_snapshot=self._observations_snapshot,
                                        max_time_gap_hours=self.max_time_gap_hours)
                if not res.get("success"):
                    trial_errors.append(str(res.get('error', 'Calibration model run failed')))
                    return 1e10
                return compute_objective(res["outputs"], self.objective,
                                         points_snapshot=self._points_snapshot,
                                         data_snapshot=self._data_snapshot,
                                         objective_weights=self.objective_weights,
                                         observations_snapshot=self._observations_snapshot)

            def callback(iteration, params, obj):
                if self.max_iter > 0:
                    if self.engine_name == 'pyabc-abcsmc':
                        population = self.engine_options.get('population_size', 10)
                        budget = self.engine_options['max_simulations']
                        self.progress = min(.95, iteration / budget)
                    else:
                        budget = self.engine_options.get('max_simulations',
                                                         scipy_evaluation_budget(self.max_iter, len(self.params)))
                        self.progress = min(.95, iteration / budget)
                self.history.append({
                    "iteration": iteration,
                    "params": params,
                    "objective": obj,
                    "timestamp": datetime.now().isoformat(),
                })

            if self.engine_name == 'pyabc-abcsmc':
                options = dict(self.engine_options)
                options['database_path'] = self.case_path / 'output' / 'calibration' / self.job_id / 'abc.db'
            else:
                options = {'max_simulations': self.engine_options.get(
                    'max_simulations', scipy_evaluation_budget(self.max_iter, len(self.params)))}
                if self.objective == 'rmse':
                    options['squared_distance'] = True
            self.result = engine.calibrate(
                self.params, objective_fn, callback, max_iter=self.max_iter, **options)
            best_objective = self.result.get('best_objective')
            if not self._stop_flag and (best_objective is None or not np.isfinite(best_objective) or best_objective >= 1e10):
                self.result['success'] = False
                self.error = trial_errors[-1] if trial_errors else 'No valid observation/model pairs produced a calibration objective'
                self.result['error'] = self.error
            if self.result.get("fallback"):
                self.fallback = self.result["fallback"]
            self.status = "stopped" if self._stop_flag else ("completed" if self.result.get("success") else "failed")
        except Exception as e:
            self.error = f"{e}\n{traceback.format_exc()}"
            self.status = "stopped" if self._stop_flag else "failed"
        finally:
            self.end_time = datetime.now().isoformat()
            if self.progress < 1.0 and self.status == "completed":
                self.progress = 1.0

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_flag = True
        self.status = "stopped"

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "method": self.method,
            "engine": (self.result or {}).get('engine', self.engine_name).replace('scipy.lbfgsb', 'scipy-lbfgsb'),
            "objective": self.objective,
            "max_iter": self.max_iter,
            "status": self.status,
            "progress": self.progress,
            "history": self.history[-50:],   # last 50 entries to limit payload
            "history_len": len(self.history),
            "result": self.result,
            "error": self.error,
            "fallback": self.fallback,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "params": self.params,
            "point_ids": self.point_ids,
            "objective_weights": self.objective_weights,
            "observation_manifest": self._observations_snapshot.get('manifest', []),
            "max_time_gap_hours": self.max_time_gap_hours,
        }


def start_calibration_job(method, params, objective, max_iter, case_path, point_ids=None,
                          objective_weights=None, engine_options=None, max_time_gap_hours=None):
    """Create and start a CalibrationJob. Returns the job_id."""
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + os.urandom(3).hex()
    job = CalibrationJob(job_id, method, params, objective, max_iter, case_path, point_ids=point_ids,
                         objective_weights=objective_weights, engine_options=engine_options,
                         max_time_gap_hours=max_time_gap_hours)
    with _job_lock:
        calibration_jobs[job_id] = job
    job.start()
    return job_id


def get_calibration_job(job_id):
    with _job_lock:
        return calibration_jobs.get(job_id)


def list_calibration_jobs():
    with _job_lock:
        return list(calibration_jobs.keys())
