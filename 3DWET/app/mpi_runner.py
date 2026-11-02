"""Opt-in MPI process plumbing. Result merging is deliberately delegated.

This module does not make MPI available by itself: callers must supply an
enabled feature gate, validated MPI solver, launcher and result merger.
"""
from __future__ import annotations

import os
import subprocess
import threading
import tempfile
import shutil
import re
import sys
import functools
from pathlib import Path

from solver_runtime import inspect_runtime, solver_environment, log_has_solver_failure

MPI_RUN_ENABLED = os.environ.get("WET_ENABLE_MPI_RUN", "1").strip().lower() in {"1", "true", "yes"}
GETM_MPI_HALO_WIDTH = 2  # 3DWET/src/getm/include/cppdefs.h


def available_cpu_count():
    """Return logical CPUs available to this process, respecting affinity."""
    if os.name == "nt":
        try:
            import psutil
            affinity = psutil.Process().cpu_affinity()
            if affinity:
                return len(affinity)
        except Exception:
            pass
    process_count = getattr(os, "process_cpu_count", None)
    if process_count:
        try:
            count = process_count()
            if count:
                return max(1, int(count))
        except Exception:
            pass
    if hasattr(os, "sched_getaffinity"):
        try:
            affinity = os.sched_getaffinity(0)
            if affinity:
                return len(affinity)
        except Exception:
            pass
    return max(1, int(os.cpu_count() or 1))


_MSMPI_DIMS_PROBE = r'''
import ctypes
import sys

mpi = ctypes.WinDLL(sys.argv[1])
init = mpi.MPI_Init
init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
init.restype = ctypes.c_int
if init(None, None) != 0:
    raise SystemExit("MPI_Init failed")
dims_create = mpi.MPI_Dims_create
dims_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
dims_create.restype = ctypes.c_int
for count in (int(value) for value in sys.argv[2].split(",") if value):
    dims = (ctypes.c_int * 2)(0, 0)
    error = dims_create(count, 2, dims)
    if error != 0:
        raise SystemExit("MPI_Dims_create failed for " + str(count) + ": " + str(error))
    print(str(count) + ":" + str(dims[0]) + ":" + str(dims[1]))
finalize = mpi.MPI_Finalize
finalize.argtypes = []
finalize.restype = ctypes.c_int
if finalize() != 0:
    raise SystemExit("MPI_Finalize failed")
'''


@functools.lru_cache(maxsize=16)
def _query_mpi_dimensions_cached(python_executable, mpi_dll, runtime_dir, counts):
    if os.name != "nt":
        raise RuntimeError("MS-MPI decomposition probe is only supported on Windows")
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join([runtime_dir, env.get("PATH", "")])
    output_file = None
    if getattr(sys, "frozen", False):
        handle, output_file = tempfile.mkstemp(prefix="getm-mpi-dims-", suffix=".txt")
        os.close(handle)
        command = [python_executable, "--mpi-dims-probe", mpi_dll,
                   ",".join(str(count) for count in counts), output_file]
    else:
        command = [python_executable, "-c", _MSMPI_DIMS_PROBE, mpi_dll,
                   ",".join(str(count) for count in counts)]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=20, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), env=env)
        stdout = result.stdout or ""
        if output_file and Path(output_file).is_file():
            stdout = Path(output_file).read_text(encoding="utf-8", errors="replace")
        if result.returncode != 0:
            raise RuntimeError((result.stderr or stdout or
                                f"MS-MPI decomposition probe exited {result.returncode}").strip())
    finally:
        if output_file:
            try:
                Path(output_file).unlink(missing_ok=True)
            except OSError:
                pass
    parsed = {}
    for line in stdout.splitlines():
        fields = line.strip().split(":")
        if len(fields) == 3:
            parsed[int(fields[0])] = (int(fields[1]), int(fields[2]))
    if set(parsed) != set(counts):
        raise RuntimeError("MS-MPI decomposition probe returned incomplete dimensions")
    return parsed


def mpi_dimensions_for_counts(counts, launcher):
    """Ask the packaged MS-MPI library for its exact 2-D process grid."""
    mpi_dir = Path(launcher).resolve().parent
    mpi_dll = mpi_dir / "msmpi.dll"
    if not mpi_dll.is_file():
        raise FileNotFoundError(f"MS-MPI runtime DLL is missing: {mpi_dll}")
    counts = tuple(sorted({int(count) for count in counts if int(count) > 0}))
    if not counts:
        return {}
    if counts == (1,):
        return {1: (1, 1)}
    return _query_mpi_dimensions_cached(sys.executable, str(mpi_dll), str(mpi_dir), counts)


def mpi_process_counts_for_grid(ih, jh, *, cpu_count=None, launcher=None,
                                dimensions_for_counts=None):
    """Return rank counts whose 2-D layout fits GETM grid/halo dimensions.

    GETM maps MPI dimension 0 onto j and dimension 1 onto i. Its generated
    local block size is ceil(global_extent / partitions), with offsets formed
    as coordinate * local block size. Require each neighboring subdomain to
    own at least the configured halo width. In particular, check the actual
    remaining extent after the last offset, not only the nominal ceil-sized
    local array. This checks geometry only; it does not establish numerical
    equivalence for a rank count.
    """
    ih, jh = int(ih), int(jh)
    cpus = max(1, int(cpu_count if cpu_count is not None else available_cpu_count()))
    if ih < 1 or jh < 1:
        raise ValueError("GETM grid extents must be positive")
    counts = range(1, cpus + 1)
    if dimensions_for_counts is None:
        if launcher is None:
            raise ValueError("MPI launcher is required to inspect the exact decomposition")
        dimensions_for_counts = mpi_dimensions_for_counts(counts, launcher)

    def each_subdomain_intersects(extent, partitions):
        if partitions < 1:
            return False
        local_size = (extent + partitions - 1) // partitions
        last_start = (partitions - 1) * local_size
        last_size = extent - last_start
        return (last_size > 0 and (partitions == 1 or
                (local_size >= GETM_MPI_HALO_WIDTH
                 and last_size >= GETM_MPI_HALO_WIDTH)))

    valid = []
    for count in counts:
        dims = dimensions_for_counts.get(count)
        if not dims or len(dims) != 2:
            continue
        j_parts, i_parts = dims
        if (each_subdomain_intersects(jh, j_parts)
                and each_subdomain_intersects(ih, i_parts)):
            valid.append(count)
    return valid


def _packaged_model_root():
    """Locate the 3DWET payload in source and PyInstaller onedir layouts."""
    module_path = Path(__file__).resolve()
    # In source mode this is 3DWET/app/mpi_runner.py. In a PyInstaller onedir
    # build it is <install>/_internal/mpi_runner.py while model assets live in
    # <install>/3DWET. Locate the model root from the packaged parallel solver
    # instead of assuming the module and model share a parent directory.
    for candidate in (module_path.parent, *module_path.parents):
        if (candidate / "bin" / "getm_cartesian_parallel.exe").is_file():
            return candidate
        nested_model = candidate / "3DWET"
        if (nested_model / "bin" / "getm_cartesian_parallel.exe").is_file():
            return nested_model
    # Retain the conventional source layout so diagnostics report expected
    # packaged paths even when the solver has not yet been installed.
    return module_path.parents[1]


def discover_mpi_installation():
    """Resolve configured MPI binaries, preferring explicit paths then packaged files."""
    app_root = _packaged_model_root()
    package_bin = app_root / "bin"
    mpi_dir = package_bin / "mpi"
    solver = Path(os.environ["WET_MPI_SOLVER"]).expanduser() if os.environ.get("WET_MPI_SOLVER") else package_bin / "getm_cartesian_parallel.exe"
    launcher = Path(os.environ["WET_MPIEXEC"]).expanduser() if os.environ.get("WET_MPIEXEC") else mpi_dir / "mpiexec.exe"
    if "WET_MPI_RUNTIME_DIRS" in os.environ:
        runtime_dirs = [Path(p).expanduser() for p in os.environ["WET_MPI_RUNTIME_DIRS"].split(os.pathsep) if p]
    else:
        runtime_dirs = [package_bin / "runtime", mpi_dir]
    return {"solver": solver.resolve(), "launcher": launcher.resolve(),
            "runtime_dirs": [p.resolve() for p in runtime_dirs if p.is_dir()]}


def mpi_capabilities(*, launcher=None, solver=None, merger=None, feature_enabled=None,
                     grid_shape=None):
    """Evaluate availability from registered paths and merge callback."""
    enabled = MPI_RUN_ENABLED if feature_enabled is None else bool(feature_enabled)
    cpus = available_cpu_count()
    missing = []
    if not enabled:
        missing.append("feature flag")
    if not launcher or not Path(launcher).is_file():
        missing.append("MPI launcher")
    if not solver or not Path(solver).is_file():
        missing.append("parallel solver")
    if not callable(merger):
        missing.append("rank output merger")
    if launcher and Path(launcher).is_file():
        mpi_dir = Path(launcher).resolve().parent
        if not (mpi_dir / "msmpi.dll").is_file():
            missing.append("MS-MPI runtime DLL")
    if solver and Path(solver).is_file():
        if not inspect_runtime(solver).get("ready"):
            missing.append("solver runtime DLLs")
    allowed = list(range(1, cpus + 1))
    if grid_shape is not None and enabled and launcher and Path(launcher).is_file():
        try:
            allowed = mpi_process_counts_for_grid(*grid_shape, cpu_count=cpus, launcher=launcher)
            if not allowed:
                missing.append("no valid MPI decomposition for this GETM grid")
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            missing.append("MPI decomposition check: " + str(exc))
    return {"enabled": not missing, "max_processes": cpus,
            "allowed_processes": allowed,
            "recommended_processes": recommended_process_count(cpus, allowed),
            "reason": "" if not missing else "Unavailable: " + ", ".join(missing)}


def recommended_process_count(cpu_count=None, allowed_processes=None):
    """Estimate a conservative rank count near half the CPUs available to this process.

    This is a starting point, not a measured performance optimum. If a grid only
    permits other decompositions, choose the legal count nearest the target;
    ties prefer fewer ranks. Return None if no legal count is available.
    """
    cpus = max(1, int(cpu_count if cpu_count is not None else available_cpu_count()))
    source = range(1, cpus + 1) if allowed_processes is None else allowed_processes
    allowed = set()
    for value in source:
        if isinstance(value, bool):
            continue
        try:
            count = int(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if str(value).strip() not in {str(count), f"+{count}"}:
            continue
        if 1 <= count <= cpus:
            allowed.add(count)
    if not allowed:
        return None
    target = max(1, (cpus + 1) // 2)
    return min(allowed, key=lambda value: (abs(value - target), value))


def validate_process_count(value: object, *, cpu_count: int | None = None,
                           allowed_processes=None) -> int:
    """Accept only integer n in [1, available logical CPU count]."""
    cpus = max(1, int(cpu_count or available_cpu_count()))
    if isinstance(value, bool):
        raise ValueError("MPI process count must be an integer")
    try:
        n = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("MPI process count must be an integer") from exc
    if str(value).strip() not in {str(n), f"+{n}"}:
        raise ValueError("MPI process count must be an integer")
    if not 1 <= n <= cpus:
        raise ValueError(f"MPI process count must be between 1 and {cpus}")
    allowed = None if allowed_processes is None else {int(count) for count in allowed_processes}
    if allowed is not None and n not in allowed:
        choices = ", ".join(str(value) for value in sorted(allowed))
        raise ValueError(f"This GETM grid/halo layout does not support {n} MPI ranks; choose one of: {choices}")
    return n


def mpi_command(mpiexec: str | Path, solver: str | Path, n: int) -> list[str]:
    return [str(mpiexec), "-n", str(n), str(solver)]


def merge_case_rank_outputs(case, n, *, reference_name="bathymetry.nc"):
    """Merge every complete GETM output family; reject missing rank shards.

    The existing validated merger checks coordinate blocks, overlap and full
    coverage. A case is not publishable if any family fails to merge.
    """
    import sys
    from netCDF4 import Dataset
    case = Path(case)
    reference = case / reference_name
    if not reference.is_file():
        raise FileNotFoundError(f"Global-grid reference is missing: {reference}")
    scripts = case.parents[1] / "scripts" if case.parent.name == "case" else None
    # Standard workspace layout: .../3DWET/case/<case>; also support isolated copies.
    if scripts is None:
        candidates = [case.parent / "scripts", _packaged_model_root() / "scripts"]
        scripts = next((p for p in candidates if (p / "merge_getm_rank_outputs.py").is_file()), None)
    if scripts is None or not (scripts / "merge_getm_rank_outputs.py").is_file():
        raise RuntimeError("GETM rank merge implementation is unavailable")
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from merge_getm_rank_outputs import merge_rank_outputs
    families = {}
    for path in case.glob("*.????.nc"):
        match = re.fullmatch(r"(.+)\.(\d{4})\.nc", path.name)
        if match:
            families.setdefault(match.group(1), []).append(path)
    if not families:
        raise RuntimeError("MPI run produced no rank output shards")
    merged = []
    for stem, shards in sorted(families.items()):
        ranks = {int(p.stem.rsplit(".", 1)[1]) for p in shards}
        if ranks != set(range(n)):
            raise RuntimeError(f"Incomplete rank family {stem}: found {sorted(ranks)}, expected 0..{n-1}")
        lengths = []
        for shard in shards:
            with Dataset(shard) as ds:
                if "time" not in ds.dimensions:
                    raise RuntimeError(f"Rank output has no time dimension: {shard.name}")
                lengths.append(len(ds.dimensions["time"]))
        if all(length == 0 for length in lengths):
            continue
        if any(length == 0 for length in lengths):
            raise RuntimeError(f"Rank family {stem} has inconsistent empty/non-empty time records")
        # GETM family patterns are RUNID.2d / RUNID.3d / output.
        if stem.endswith(".2d"):
            destination = case / f"{stem[:-3]}.2d.nc"
        elif stem.endswith(".3d"):
            destination = case / f"{stem[:-3]}.3d.nc"
        else:
            destination = case / f"{stem}.nc"
        merged.append(merge_rank_outputs(shards, reference, destination))
    if not any(Path(path).name == "output.nc" for path in merged):
        raise RuntimeError("MPI run produced no time records in output rank files")
    return merged


def prepare_mpi_case(source, *, msg_method=3, process_count=1):
    """Create a disposable run copy and configure GETM parallel namelists there."""
    source = Path(source).resolve()
    if msg_method not in (1, 3):
        raise ValueError("MsgMethod must be 1 (1D halo exchange) or 3 (2D halo exchange)")
    if isinstance(process_count, bool) or int(process_count) < 1:
        raise ValueError("process_count must be a positive integer")
    process_count = int(process_count)
    inp = source / "getm.inp"
    if not inp.is_file():
        raise FileNotFoundError(inp)
    work = Path(tempfile.mkdtemp(prefix=f".{source.name}.mpi-", dir=source.parent))

    def ignore(directory, names):
        ignored = set()
        for name in names:
            path = Path(directory) / name
            if name == "output" and path.is_dir():
                ignored.add(name)
            elif name in {"model_run.log", "run.log", "restart.out", "restart.in.previous",
                          "output.nc"} or name.endswith((".2d.nc", ".3d.nc")):
                ignored.add(name)
            elif re.fullmatch(r".+\.\d{4}\.(?:stdout|stderr)", name, re.IGNORECASE):
                # Rank logs belong to a prior run; never seed current progress with them.
                ignored.add(name)
            elif re.fullmatch(r".+\.(?:2d|3d)\.\d{4}\.nc", name) or re.fullmatch(r"output\.\d{4}\.nc", name):
                ignored.add(name)
        return ignored

    try:
        for item in source.iterdir():
            dest = work / item.name
            if item.name in ignore(source, [item.name]):
                continue
            if item.is_dir():
                shutil.copytree(item, dest, ignore=ignore)
            elif item.is_file():
                shutil.copy2(item, dest)
        text = (work / "getm.inp").read_text(encoding="utf-8-sig")
        hotstart_match = re.search(r"(?im)^\s*hotstart\s*=\s*\.true\.", text)
        if hotstart_match:
            raise ValueError(mpi_hotstart_error({"param": {"hotstart": True}}))
        match = re.search(r"(?im)^(\s*parallel\s*=\s*)(?:\.true\.|\.false\.)", text)
        if not match:
            raise ValueError("getm.inp has no parallel logical in &getm_nml")
        text = text[:match.start()] + match.group(1) + ".true." + text[match.end():]
        (work / "getm.inp").write_text(text, encoding="utf-8")
        (work / "parallel.inp").write_text(
            "&nampar\n MeshMethod=1, reorder=.false., MsgMethod=" + str(msg_method) + "\n/\n",
            encoding="ascii")
        return work
    except Exception:
        shutil.rmtree(work, ignore_errors=True)
        raise


def mpi_hotstart_error(config):
    """Return the user-facing preflight error for unsupported MPI hotstarts."""
    if bool((config.get("param", {}) or {}).get("hotstart", False)):
        return ("MPI hotstart is currently unsupported: reading the serial checkpoint fails at the "
                "FABM temporal checkpoint. Use a cold MPI start or a serial run.")
    return None


def stop_process_tree(process: subprocess.Popen, *, windows: bool | None = None,
                      run=subprocess.run) -> None:
    """Stop launcher and descendants; taskkill /T handles Windows MPI children."""
    windows = os.name == "nt" if windows is None else windows
    if process.poll() is not None:
        return
    if windows:
        run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(process.pid, 15)
        except (OSError, ProcessLookupError):
            process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        if windows:
            run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            process.kill()
        process.wait(timeout=5)


class MpiRun:
    """Own one launcher, rank log files, and a caller-provided merge hook."""
    def __init__(self, *, launcher, solver, n, case, cpu_count=None, runtime_dirs=None,
                 merger=None, feature_enabled=None, popen=subprocess.Popen,
                 omp_threads=None):
        enabled = MPI_RUN_ENABLED if feature_enabled is None else bool(feature_enabled)
        if not enabled:
            raise RuntimeError("MPI run feature is disabled")
        if not Path(launcher).is_file() or not Path(solver).is_file():
            raise FileNotFoundError("MPI launcher and solver must both exist")
        if merger is None:
            raise RuntimeError("MPI results merger is unavailable")
        self.launcher, self.solver = str(launcher), str(solver)
        self.n = validate_process_count(n, cpu_count=cpu_count)
        self.omp_threads = omp_threads
        self.case = Path(case)
        self.merger = merger
        self.runtime_dirs = [Path(p).resolve() for p in (runtime_dirs or [])]
        self.popen = popen
        self.process = None
        self._log = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self.process is not None and self.process.poll() is None:
                raise RuntimeError("MPI run already active")
            self.case.mkdir(parents=True, exist_ok=True)
            self._log = (self.case / "model_run.log").open("w", encoding="utf-8", errors="replace")
            # Keep the model's packaged DLLs first and the MPI runtime next.
            env = solver_environment(self.solver, threads=self.omp_threads)
            mpi_runtime = str(Path(self.launcher).resolve().parent)
            paths = [p for p in env.get("PATH", "").split(os.pathsep) if p]
            extras = [str(p) for p in self.runtime_dirs]
            if not extras:
                extras = [str(Path(p).resolve()) for p in
                          os.environ.get("WET_MPI_RUNTIME_DIRS", "").split(os.pathsep) if p]
            # Deterministic ABI order: application runtime, matching MS-MPI
            # runtime, UCRT64 support DLLs, then ambient PATH last.
            solver_runtime = [str(Path(__file__).resolve().parents[1] / "bin" / "runtime")]
            configured = extras[:1] + [mpi_runtime] + extras[1:] + solver_runtime
            unique_configured = []
            for path in configured:
                key = os.path.normcase(os.path.normpath(path))
                if key not in {os.path.normcase(os.path.normpath(p)) for p in unique_configured}:
                    unique_configured.append(path)
            configured = unique_configured
            seen = {os.path.normcase(os.path.normpath(p)) for p in configured}
            ambient = [p for p in paths if os.path.normcase(os.path.normpath(p)) not in seen]
            env["PATH"] = os.pathsep.join(configured + ambient)
            kwargs = {"cwd": str(self.case), "stdout": self._log,
                      "stderr": subprocess.STDOUT, "env": env}
            if os.name == "nt":
                kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                kwargs["start_new_session"] = True
            self.process = self.popen(mpi_command(self.launcher, self.solver, self.n), **kwargs)
            return self.process

    def stop(self):
        if self.process is not None:
            stop_process_tree(self.process)

    def finish(self):
        """Report solver diagnostics before handling launcher exit status."""
        if self.process is None:
            raise RuntimeError("MPI run was not started")
        code = self.process.wait()
        if self._log:
            self._log.flush()
            self._log.close()
            self._log = None
        log_path = self.case / "model_run.log"
        text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        failures = []
        if log_has_solver_failure(text):
            lines = [line.strip() for line in text.splitlines()
                     if log_has_solver_failure(line)]
            detail = " | ".join(line[:200] for line in lines[:3])
            failures.append(f"model_run.log: {detail or 'solver fatal/numerical diagnostic'}")
        for pattern in ("*.stderr", "*.stdout"):
            for rank_log in self.case.glob(pattern):
                rank_text = rank_log.read_text(encoding="utf-8", errors="replace")
                if log_has_solver_failure(rank_text):
                    lines = [line.strip() for line in rank_text.splitlines()
                             if log_has_solver_failure(line)]
                    detail = " | ".join(line[:200] for line in lines[:3])
                    failures.append(f"{rank_log.name}: {detail or 'solver fatal/numerical diagnostic'}")
        if failures:
            exit_detail = (f" (MPI launcher exit code {code})" if code != 0
                           else " despite MPI launcher exit 0")
            raise RuntimeError("MPI solver failure detected" + exit_detail + ": "
                               + "; ".join(failures[:3]))
        if code != 0:
            raise subprocess.CalledProcessError(code, self.process.args)
        return self.merger(self.case, self.n)
