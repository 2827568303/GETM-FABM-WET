"""Choose how many cores a run uses, and whether they are threads or ranks.

There is no upper bound. A laptop offers its own logical cores; a cluster
job may ask for more ranks than one node has. The first look at a machine
and grid times a short GETM window and remembers the fastest mode. The
number in the run control is only a starting point until that trial
finishes, and the user can override it.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from solver_runtime import recommended_openmp_threads

_STEP_LINE = re.compile(
    r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2}\.\d+)\s+n=\s*(?P<n>\d+)")
_MODES = {"auto", "serial", "threads", "mpi", "hybrid"}


def parse_core_count(value):
    """Accept any integer >= 1. There is no hardware ceiling."""
    if isinstance(value, bool):
        raise ValueError("使用核数必须是正整数")
    try:
        cores = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("使用核数必须是正整数") from exc
    if str(value).strip() not in {str(cores), f"+{cores}"}:
        raise ValueError("使用核数必须是正整数")
    if cores < 1:
        raise ValueError("使用核数必须是正整数")
    return cores


def _linux_topology():
    cpu_root = Path("/sys/devices/system/cpu")
    packages = set()
    cores = set()
    if not cpu_root.is_dir():
        return None, None, None
    for cpu in cpu_root.glob("cpu[0-9]*"):
        core_file = cpu / "topology" / "core_id"
        package_file = cpu / "topology" / "physical_package_id"
        if not core_file.is_file():
            continue
        core = core_file.read_text(encoding="utf-8").strip()
        package = package_file.read_text(encoding="utf-8").strip() if package_file.is_file() else "0"
        cores.add((package, core))
        packages.add(package)
    node_root = Path("/sys/devices/system/node")
    numa = len(list(node_root.glob("node[0-9]*"))) if node_root.is_dir() else None
    return (len(cores) or None), (len(packages) or None), (numa or None)


def _which(names):
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def detect_hardware(logical=None):
    """Logical and physical cores, sockets, NUMA, and MPI launchers."""
    from mpi_runner import available_cpu_count, discover_mpi_installation

    if logical is None:
        logical = available_cpu_count()
    logical = max(1, int(logical))
    physical = sockets = numa = None
    if os.name != "nt":
        physical, sockets, numa = _linux_topology()
    else:
        try:
            import psutil
            physical = psutil.cpu_count(logical=False) or None
        except Exception:
            physical = None
    if not physical:
        physical = logical
    installation = discover_mpi_installation()
    packaged_solver = installation.get("solver")
    packaged_launcher = installation.get("launcher")
    srun = _which(("srun",))
    mpiexec = _which(("mpiexec", "mpirun"))
    if packaged_launcher and Path(packaged_launcher).is_file() and not mpiexec:
        mpiexec = str(packaged_launcher)
    parallel_solver = None
    candidates = []
    if os.environ.get("WET_MPI_SOLVER"):
        candidates.append(Path(os.environ["WET_MPI_SOLVER"]).expanduser())
    if packaged_solver:
        candidates.append(Path(packaged_solver))
        no_suffix = Path(packaged_solver).with_suffix("")
        if no_suffix != Path(packaged_solver):
            candidates.append(no_suffix)
    app_root = Path(__file__).resolve().parents[1]
    candidates.extend((
        app_root / "bin" / "getm_cartesian_parallel",
        app_root / "bin" / "getm_cartesian_parallel.exe",
        app_root / "build-linux" / "getm" / "getm_cartesian_parallel",
    ))
    for candidate in candidates:
        if candidate.is_file():
            parallel_solver = str(candidate)
            break
    return {
        "logical": logical,
        "physical": int(physical),
        "sockets": sockets,
        "numa_nodes": numa,
        "system": platform.system(),
        "machine": platform.machine(),
        "mpi_launcher": mpiexec,
        "srun": srun,
        "parallel_solver": parallel_solver,
        "mpi_available": bool((srun or mpiexec) and parallel_solver),
    }


def hardware_fingerprint(hardware):
    payload = {key: hardware.get(key) for key in (
        "logical", "physical", "sockets", "numa_nodes", "system", "machine",
        "mpi_launcher", "srun", "parallel_solver")}
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def read_case_grid(case_path):
    case = Path(case_path)
    grid = {"nx": None, "ny": None, "layers": None, "wet_columns": None}
    bathy = case / "bathymetry.nc"
    if bathy.is_file():
        try:
            from netCDF4 import Dataset
            import numpy as np
            with Dataset(bathy) as ds:
                values = np.asarray(ds.variables["bathymetry"][:])
            grid["ny"], grid["nx"] = int(values.shape[-2]), int(values.shape[-1])
            grid["wet_columns"] = int((values > 0).sum())
        except Exception:
            pass
    inp = case / "getm.inp"
    if inp.is_file():
        text = inp.read_text(encoding="utf-8", errors="replace")
        found = re.search(r"(?im)^\s*(?:kdum|M)\s*=\s*(\d+)", text)
        if found:
            grid["layers"] = int(found.group(1))
    return grid


def benchmark_thread_counts(logical):
    """Sparse thread counts from 1 through every logical core. No fixed cap."""
    logical = max(1, int(logical))
    values = {1, logical}
    power = 2
    while power < logical and power <= 16:
        values.add(power)
        power *= 2
    if logical > 16:
        values.add(max(1, logical // 2))
    return sorted(value for value in values if 1 <= value <= logical)


def heuristic_plan(hardware, grid):
    threads = recommended_openmp_threads(
        hardware.get("logical"), grid.get("wet_columns") if grid else None)
    mode = "serial" if threads <= 1 else "threads"
    return {"mode": mode, "threads": threads, "ranks": 1, "cores": threads,
            "source": "heuristic"}


def cache_path():
    override = os.environ.get("WET_CORE_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".3dwet" / "core_calibration.json"


def cache_key(hardware, grid, exe_path):
    exe = Path(exe_path)
    try:
        size = exe.stat().st_size
    except OSError:
        size = 0
    wet = None if not grid else grid.get("wet_columns")
    shape = "x".join(str(grid.get(name) or 0) for name in ("nx", "ny", "layers")) if grid else "0x0x0"
    return f"{hardware_fingerprint(hardware)}|{shape}|{wet}|{size}"


def load_cache():
    path = cache_path()
    if not path.is_file():
        return {"entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"entries": {}}
    if not isinstance(data, dict) or not isinstance(data.get("entries"), dict):
        return {"entries": {}}
    return data


def save_cache(data):
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def lookup_choice(hardware, grid, exe_path):
    entry = load_cache()["entries"].get(cache_key(hardware, grid, exe_path))
    if not entry:
        return None
    choice = entry.get("choice")
    if not isinstance(choice, dict):
        return None
    choice = dict(choice)
    choice["source"] = "measured"
    return choice


def choose_fastest(results):
    """Pick the highest integration rate. Ties prefer fewer cores."""
    usable = []
    for item in results:
        if not item.get("ok"):
            continue
        rate = item.get("steps_per_second")
        try:
            rate = float(rate)
        except (TypeError, ValueError):
            continue
        if rate <= 0:
            continue
        usable.append(item)
    if not usable:
        return None
    winner = min(usable, key=lambda item: (
        -float(item["steps_per_second"]),
        int(item.get("ranks") or 1) * int(item.get("threads") or 1),
        int(item.get("threads") or 1),
    ))
    threads = int(winner.get("threads") or 1)
    ranks = int(winner.get("ranks") or 1)
    mode = winner.get("mode") or ("serial" if threads <= 1 and ranks <= 1 else "threads")
    return {"mode": mode, "threads": threads, "ranks": ranks,
            "cores": threads * ranks, "source": "measured",
            "steps_per_second": float(winner["steps_per_second"])}


def integration_rate(log_text):
    """Steps per second between the first and last progress lines."""
    samples = []
    for line in log_text.splitlines():
        match = _STEP_LINE.search(line)
        if not match:
            continue
        seconds = (int(match.group("h")) * 3600 + int(match.group("m")) * 60
                   + float(match.group("s")))
        samples.append((int(match.group("n")), seconds))
    if len(samples) < 2:
        return None
    dn = samples[-1][0] - samples[0][0]
    dt = samples[-1][1] - samples[0][1]
    if dn <= 0 or dt <= 0:
        return None
    return dn / dt


def shorten_getm_inp(path, steps=300):
    """Point a disposable getm.inp at a short window. GETM logs every 100 steps."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    timestep = re.search(r"(?im)^\s*timestep\s*=\s*([0-9.eE+-]+)", text)
    start = re.search(r"(?im)^(\s*start\s*=\s*)'([^']+)'", text)
    stop = re.search(r"(?im)^(\s*stop\s*=\s*)'([^']+)'", text)
    if not (timestep and start and stop):
        raise ValueError("getm.inp 缺少 timestep/start/stop")
    dt = float(timestep.group(1))
    if dt <= 0:
        raise ValueError("timestep 必须为正")
    start_at = datetime.strptime(start.group(2), "%Y-%m-%d %H:%M:%S")
    stop_at = start_at + timedelta(seconds=dt * int(steps))
    text = text[:stop.start()] + stop.group(1) + "'" + stop_at.strftime("%Y-%m-%d %H:%M:%S") + "'" + text[stop.end():]
    path.write_text(text, encoding="utf-8")
    return stop_at


def describe_plan(hardware, grid, plan, *, cached=False, calibrating=False):
    logical = hardware.get("logical")
    physical = hardware.get("physical")
    sockets = hardware.get("sockets")
    numa = hardware.get("numa_nodes")
    parts = [f"本机 {logical} 个逻辑核，{physical} 个物理核"]
    if sockets:
        parts.append(f"{sockets} 个插槽")
    if numa:
        parts.append(f"{numa} 个 NUMA")
    if hardware.get("srun"):
        parts.append("已发现 srun")
    elif hardware.get("mpi_launcher") and hardware.get("parallel_solver"):
        parts.append("已发现 MPI")
    else:
        parts.append("未发现可用的 MPI 求解器")
    wet = None if not grid else grid.get("wet_columns")
    if wet:
        parts.append(f"当前网格约 {wet} 个水格")
    if calibrating:
        parts.append("正在用约 300 步测定最快的核数，完成后会更新建议")
    elif plan:
        label = {"serial": "串行", "threads": "OpenMP 线程", "mpi": "MPI 进程",
                 "hybrid": "MPI × OpenMP"}.get(plan.get("mode"), plan.get("mode"))
        origin = "已测定" if cached or plan.get("source") == "measured" else "按网格估算"
        parts.append(f"{origin}：{plan.get('cores')} 核，{label}")
    return "。".join(parts) + "。"


def resolve_plan(hardware, grid, exe_path, *, requested_cores=None, mode="auto"):
    """Turn the selector into threads and ranks. Auto uses a cached trial."""
    mode = (mode or "auto").strip().lower()
    if mode not in _MODES:
        raise ValueError("并行方式必须是自动、串行、线程、MPI 或混合")
    measured = lookup_choice(hardware, grid, exe_path)
    if mode == "auto":
        return dict(measured or heuristic_plan(hardware, grid))
    if mode == "serial":
        return {"mode": "serial", "threads": 1, "ranks": 1, "cores": 1, "source": "user"}
    cores = requested_cores
    if cores is None:
        guess = measured or heuristic_plan(hardware, grid)
        cores = int(guess["cores"])
    cores = parse_core_count(cores)
    if mode == "threads":
        return {"mode": "serial" if cores == 1 else "threads", "threads": cores,
                "ranks": 1, "cores": cores, "source": "user"}
    if mode == "mpi":
        if not hardware.get("mpi_available"):
            raise ValueError(
                "这台机器没有可用的 MPI 启动器和并行求解器。"
                "集群上请先编 GETM_USE_PARALLEL，并用 srun 或 mpiexec 启动；说明见使用说明。")
        return {"mode": "mpi", "threads": 1, "ranks": cores, "cores": cores, "source": "user"}
    threads, ranks = _split_hybrid(cores, int(hardware.get("logical") or 1))
    if not hardware.get("mpi_available"):
        return {"mode": "serial" if cores == 1 else "threads", "threads": cores,
                "ranks": 1, "cores": cores, "source": "user",
                "note": "没有 MPI 求解器，混合模式已改成 OpenMP 线程"}
    return {"mode": "hybrid", "threads": threads, "ranks": ranks,
            "cores": threads * ranks, "source": "user"}


def _split_hybrid(cores, logical):
    logical = max(1, int(logical))
    threads = 1
    while threads * 2 <= logical and (cores // (threads * 2)) >= 1 and threads * 2 <= max(1, int(cores ** 0.5)):
        threads *= 2
    ranks = max(1, cores // threads)
    return threads, ranks


def _copy_case(source, destination):
    source = Path(source)
    destination = Path(destination)
    destination.mkdir(parents=True)
    skip_dirs = {"output", "analysis"}
    for item in source.iterdir():
        if item.name in skip_dirs:
            continue
        if item.is_dir():
            shutil.copytree(item, destination / item.name, ignore=shutil.ignore_patterns(
                "*.2d.nc", "*.3d.nc", "output.nc", "ext_wq.nc", "model_run.log"))
        elif item.is_file() and item.suffix != ".nc" or item.name in {
                "bathymetry.nc", "meteo.nc", "rivers.nc", "fabm_init.nc"}:
            if item.name.endswith((".2d.nc", ".3d.nc")) or item.name in {"output.nc", "ext_wq.nc"}:
                continue
            shutil.copy2(item, destination / item.name)


def _clean_outputs(case):
    case = Path(case)
    for pattern in ("*.2d.nc", "*.3d.nc", "output.nc", "ext_wq.nc", "model_run.log", "run.log"):
        for path in case.glob(pattern):
            if path.name == "bathymetry.nc":
                continue
            path.unlink(missing_ok=True)


def probe_threads(exe, case, threads, *, timeout=180):
    """Run one short window and return the integration rate."""
    from solver_runtime import solver_environment
    log_path = Path(case) / "model_run.log"
    _clean_outputs(case)
    env = solver_environment(exe, threads=threads)
    started = time.perf_counter()
    with log_path.open("w", encoding="utf-8", errors="replace") as handle:
        process = subprocess.Popen(
            [str(exe)], cwd=str(case), stdout=handle, stderr=subprocess.STDOUT, env=env)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
            code = None
    wall = time.perf_counter() - started
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    rate = integration_rate(text)
    hung = code is None
    return {"ok": code == 0 and rate is not None and not hung,
            "exit_code": code, "wall_seconds": wall, "steps_per_second": rate,
            "hung": hung, "mode": "serial" if int(threads) <= 1 else "threads",
            "threads": int(threads), "ranks": 1}


def calibrate(case_path, exe_path, *, steps=300, timeout=180, thread_counts=None, log=None):
    """Time a short window at several thread counts and cache the fastest."""
    case_path = Path(case_path)
    exe_path = Path(exe_path)
    hardware = detect_hardware()
    grid = read_case_grid(case_path)
    counts = thread_counts or benchmark_thread_counts(hardware["logical"])
    work_parent = Path(os.environ.get("TMPDIR", "/tmp"))
    work = work_parent / f"3dwet-core-{os.getpid()}"
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)
    results = []
    try:
        _copy_case(case_path, work)
        shorten_getm_inp(work / "getm.inp", steps=steps)
        for threads in counts:
            if log:
                log(f"[INFO] 测定 {threads} 个 OpenMP 线程（约 {steps} 步）")
            results.append(probe_threads(exe_path, work, threads, timeout=timeout))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    choice = choose_fastest(results) or heuristic_plan(hardware, grid)
    data = load_cache()
    data["entries"][cache_key(hardware, grid, exe_path)] = {
        "fingerprint": hardware_fingerprint(hardware),
        "grid": grid,
        "results": results,
        "choice": choice,
        "measured_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_cache(data)
    return {"hardware": hardware, "grid": grid, "results": results, "choice": choice}
