"""Short, isolated MPI trials for hardware- and case-specific rank selection."""
from __future__ import annotations

from datetime import datetime, timedelta
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import time


def minimum_trial_duration(case_path) -> int:
    """Return a window long enough to reach each configured output family."""
    case = Path(case_path)
    output = case / "output.yaml"
    interval = 0.0
    margin = 60
    try:
        if output.is_file():
            text = output.read_text(encoding="utf-8-sig")
            step_match = re.search(r"(?im)^\s*time_step\s*:\s*['\"]?([\d.eE+-]+)", text)
            unit_match = re.search(r"(?im)^\s*time_unit\s*:\s*['\"]?([a-z]+)", text)
            if step_match:
                value = float(step_match.group(1))
                unit = unit_match.group(1).lower() if unit_match else "second"
                factors = {"s": 1, "sec": 1, "second": 1, "seconds": 1,
                           "min": 60, "minute": 60, "minutes": 60,
                           "h": 3600, "hour": 3600, "hours": 3600,
                           "d": 86400, "day": 86400, "days": 86400}
                if math.isfinite(value) and value > 0 and unit in factors:
                    interval = value * factors[unit]
        text = (case / "getm.inp").read_text(encoding="utf-8-sig")
        dt_match = re.search(r"(?im)^\s*timestep\s*=\s*([\d.eE+-]+)", text)
        dt = float(dt_match.group(1)) if dt_match else 0
        margin = max(60, math.ceil(dt * 2)) if dt > 0 else 60
        if dt > 0:
            for enabled, step_name in (("save_2d", "step_2d"),
                                       ("save_3d", "step_3d")):
                save_match = re.search(r"(?im)^\s*" + enabled + r"\s*=\s*([.a-z]+)", text)
                step_match = re.search(r"(?im)^\s*" + step_name + r"\s*=\s*(\d+)", text)
                enabled_value = save_match.group(1).strip(".").lower() if save_match else "true"
                if step_match and enabled_value in {"true", "t"}:
                    interval = max(interval, int(step_match.group(1)) * dt)
    except (OSError, TypeError, ValueError, AttributeError):
        pass
    return max(3600, math.ceil(interval) + margin if interval else 3600)


def physical_cpu_count() -> int:
    """Return the machine's physical core count, bounded by process affinity."""
    logical = max(1, int(os.cpu_count() or 1))
    try:
        import psutil
        physical = psutil.cpu_count(logical=False) or logical
        try:
            affinity = len(psutil.Process().cpu_affinity())
        except Exception:
            affinity = logical
        # When the process is restricted, scale physical cores to the portion
        # of logical CPUs it can actually use; never promise more than affinity.
        return max(1, min(affinity, math.ceil(physical * affinity / logical)))
    except Exception:
        return logical


def choose_tuning_candidates(allowed_processes, physical_cores: int,
                             *, logical_cores=None, max_candidates: int = 5) -> list[int]:
    """Choose a small spread of legal rank counts for real case trials.

    Trials include counts near quarter, half, all physical cores, and the
    highest available logical count. The decomposition gate remains authoritative.
    """
    physical = max(1, int(physical_cores))
    limit = max(1, int(max_candidates))
    legal = {int(value) for value in allowed_processes
             if not isinstance(value, bool) and str(value).strip().isdigit()
             and int(value) > 0}
    logical = max(physical, int(logical_cores or max(legal, default=physical)))
    allowed = sorted(value for value in legal if value <= logical)
    if not allowed:
        return []
    targets = [1, max(1, round(physical / 4)),
               max(1, round(physical / 2)), physical, logical]
    selected = []
    for target in targets:
        choice = min(allowed, key=lambda value: (abs(value - target), value))
        if choice not in selected:
            selected.append(choice)
    if len(allowed) <= limit:
        selected = list(allowed)
    # If the legal decomposition leaves a sparse set, test the available
    # endpoints too, retaining the requested upper bound.
    if len(selected) > limit:
        indexes = {round(i * (len(selected) - 1) / (limit - 1))
                   for i in range(limit)} if limit > 1 else {0}
        selected = [value for i, value in enumerate(selected) if i in indexes]
    return sorted(selected)


def rank_count_from_measurements(measurements, *, tie_tolerance: float = 0.05):
    """Select the measured fastest rank count; favor fewer ranks within noise."""
    if not 0 <= float(tie_tolerance) < 1:
        raise ValueError("tie_tolerance must be between 0 and 1")
    valid = {}
    for ranks, samples in (measurements or {}).items():
        try:
            count = int(ranks)
        except (TypeError, ValueError, OverflowError):
            continue
        if count < 1:
            continue
        values = []
        for sample in samples or ():
            try:
                seconds = float(sample)
            except (TypeError, ValueError, OverflowError):
                continue
            if math.isfinite(seconds) and seconds > 0:
                values.append(seconds)
        if values:
            valid[count] = statistics.median(values)
    if not valid:
        return None
    best = min(valid.values())
    near_best = [count for count, seconds in valid.items()
                 if seconds <= best * (1 + float(tie_tolerance))]
    return min(near_best)


def _shortened_getm_case(case: Path, duration_seconds: int) -> None:
    """Restrict only the disposable trial to at most the requested duration."""
    inp = case / "getm.inp"
    text = inp.read_text(encoding="utf-8-sig")
    start_match = re.search(r"(?im)^\s*start\s*=\s*['\"]([^'\"]+)['\"]", text)
    stop_match = re.search(r"(?im)^\s*stop\s*=\s*['\"]([^'\"]+)['\"]", text)
    if not start_match or not stop_match:
        raise ValueError("MPI tuning requires explicit start and stop dates")
    start = datetime.strptime(start_match.group(1), "%Y-%m-%d %H:%M:%S")
    stop = datetime.strptime(stop_match.group(1), "%Y-%m-%d %H:%M:%S")
    trial_stop = min(stop, start + timedelta(seconds=max(1, int(duration_seconds))))
    if trial_stop <= start:
        raise ValueError("MPI tuning case has no positive run duration")
    text = text[:stop_match.start(1)] + trial_stop.strftime("%Y-%m-%d %H:%M:%S") + text[stop_match.end(1):]
    inp.write_text(text, encoding="utf-8")


def benchmark_mpi_case(case_path, *, launcher, solver, runtime_dirs,
                       allowed_processes, physical_cores=None,
                       duration_seconds=21600, repetitions=1,
                       cancelled=None, progress=None):
    """Measure solver plus rank-output merge on disposable copies of one case.

    Each candidate runs the same cold-start segment and output schedule. The
    original case is only read. Temporary MPI copies are removed in ``finally``
    even when a solver, merge, cancellation, or measurement fails.
    """
    from mpi_runner import (MpiRun, merge_case_rank_outputs,
                            prepare_mpi_case)

    source = Path(case_path).resolve()
    if not source.is_dir():
        raise FileNotFoundError(source)
    duration_seconds = max(int(duration_seconds), minimum_trial_duration(source))
    candidates = choose_tuning_candidates(
        allowed_processes, physical_cores or physical_cpu_count(),
        logical_cores=max((int(value) for value in allowed_processes), default=1))
    if not candidates:
        raise ValueError("No legal MPI process counts are available for this grid")
    repetitions = max(1, min(3, int(repetitions)))
    results = {count: [] for count in candidates}
    trials = []
    tuning_started = time.perf_counter()
    for repeat in range(repetitions):
        round_candidates = candidates if repeat % 2 == 0 else list(reversed(candidates))
        for count in round_candidates:
            if cancelled is not None and cancelled():
                raise InterruptedError("MPI tuning was cancelled")
            work = prepare_mpi_case(source, msg_method=3, process_count=count)
            runner = None
            try:
                _shortened_getm_case(work, duration_seconds)
                runner = MpiRun(launcher=launcher, solver=solver, n=count,
                                case=work, runtime_dirs=runtime_dirs,
                                merger=merge_case_rank_outputs)
                if progress is not None:
                    progress({"candidate": count, "repeat": repeat + 1,
                              "repetitions": repetitions, "phase": "running",
                              "elapsed_seconds": time.perf_counter() - tuning_started,
                              "candidate_count": len(candidates)})
                started = time.perf_counter()
                started_at = time.time()
                runner.start()
                last_progress = started
                while runner.process.poll() is None:
                    if cancelled is not None and cancelled():
                        runner.stop()
                        raise InterruptedError("MPI tuning was cancelled")
                    time.sleep(0.1)
                    now = time.perf_counter()
                    if progress is not None and now - last_progress >= 1:
                        progress({"candidate": count, "repeat": repeat + 1,
                                  "repetitions": repetitions, "phase": "running",
                                  "elapsed_seconds": now - tuning_started,
                                  "current_trial_seconds": now - started,
                                  "candidate_count": len(candidates)})
                        last_progress = now
                # finish() validates rank logs and includes complete file merges.
                merged = runner.finish()
                from run_output_health import validate_current_run_outputs
                from netCDF4 import Dataset
                health = validate_current_run_outputs(work, Dataset, started_at=started_at)
                if not health.get("ready"):
                    raise RuntimeError("trial output failed numerical validation: "
                                       + "; ".join(health.get("errors", [])[:3]))
                elapsed = time.perf_counter() - started
                if not merged:
                    raise RuntimeError("MPI trial produced no merged outputs")
                results[count].append(elapsed)
                trials.append({"processes": count, "repeat": repeat + 1,
                               "elapsed_seconds": elapsed,
                               "merged_files": [Path(path).name for path in merged]})
            except InterruptedError:
                raise
            except Exception as exc:
                trials.append({"processes": count, "repeat": repeat + 1,
                               "error": str(exc)[:500]})
            finally:
                if runner is not None and runner.process is not None and runner.process.poll() is None:
                    runner.stop()
                shutil.rmtree(work, ignore_errors=True)
    selected = rank_count_from_measurements(results)
    return {"candidate_processes": candidates,
            "measurements": {str(count): values for count, values in results.items()},
            "selected_processes": selected, "tie_tolerance": 0.05,
            "duration_seconds": int(duration_seconds),
            "repetitions": repetitions, "trials": trials}
