import subprocess
import os
import re
from pathlib import Path
import sys

import pytest

APP_DIR = Path(__file__).resolve().parents[1] / "3DWET" / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from mpi_runner import (MpiRun, discover_mpi_installation, merge_case_rank_outputs,
                        available_cpu_count, mpi_capabilities, mpi_command,
                        mpi_dimensions_for_counts, mpi_process_counts_for_grid,
                        mpi_hotstart_error, prepare_mpi_case,
                        recommended_process_count, stop_process_tree,
                        validate_process_count, windows_mpi_status)


def test_process_count_is_bounded_by_logical_cpu_count():
    assert validate_process_count("4", cpu_count=8) == 4
    for value in (0, 9, "2.5", True, None):
        with pytest.raises(ValueError):
            validate_process_count(value, cpu_count=8)


def test_available_cpu_count_respects_windows_process_affinity(monkeypatch):
    if os.name != "nt":
        pytest.skip("Windows process affinity check")
    import psutil
    monkeypatch.setattr(psutil.Process, "cpu_affinity", lambda _self: [2, 5, 7])
    assert available_cpu_count() == 3
    assert recommended_process_count(available_cpu_count()) == 2


def test_process_count_rejects_grid_unsafe_layouts():
    with pytest.raises(ValueError, match="does not support 10 MPI ranks"):
        validate_process_count(10, cpu_count=32, allowed_processes=[1, 2, 4, 8, 12, 16])
    assert validate_process_count(16, cpu_count=32,
                                  allowed_processes=[1, 2, 4, 8, 12, 16]) == 16


def test_grid_partition_validation_uses_actual_mpi_dimensions():
    source_root = Path(__file__).resolve().parents[1]
    cppdefs = (source_root / "3DWET" / "src" / "getm" / "include" / "cppdefs.h").read_text()
    assert re.search(r"(?m)^#define\s+HALO\s+2\s*$", cppdefs)
    dimensions = {
        1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 5: (5, 1),
        6: (3, 2), 7: (7, 1), 8: (4, 2), 9: (3, 3), 10: (5, 2),
        11: (11, 1), 12: (4, 3), 13: (13, 1), 14: (7, 2), 15: (5, 3),
        16: (4, 4), 17: (17, 1), 18: (6, 3), 19: (19, 1), 20: (5, 4),
        21: (7, 3), 22: (11, 2), 23: (23, 1), 24: (6, 4), 25: (5, 5),
        26: (13, 2), 27: (9, 3), 28: (7, 4), 29: (29, 1), 30: (6, 5),
        31: (31, 1), 32: (8, 4),
    }
    assert mpi_process_counts_for_grid(10, 4, cpu_count=32,
                                       dimensions_for_counts=dimensions) == [1, 2, 4]
    assert mpi_process_counts_for_grid(10, 2, cpu_count=32,
                                       dimensions_for_counts=dimensions) == [1]
    large = mpi_process_counts_for_grid(41, 82, cpu_count=32,
                                        dimensions_for_counts=dimensions)
    assert 16 in large and 32 in large and 13 not in large


def test_grid_partition_validation_checks_actual_last_block_width():
    # MPI_Dims_create(3, 2) returns 3x1. For extent 7, GETM uses local=ceil(7/3)=3
    # and offsets 0, 3, 6, leaving only one global cell in the last subdomain.
    dims = {1: (1, 1), 2: (2, 1), 3: (3, 1)}
    assert mpi_process_counts_for_grid(10, 7, cpu_count=3,
                                       dimensions_for_counts=dims) == [1, 2]
    # Extent 8 leaves two actual cells after the final offset, meeting HALO=2.
    assert mpi_process_counts_for_grid(10, 8, cpu_count=3,
                                       dimensions_for_counts=dims) == [1, 2, 3]


def test_packaged_msmpi_dimensions_probe_matches_runtime_when_available():
    import mpi_runner
    package_launcher = Path(mpi_runner.__file__).resolve().parents[1] / "bin" / "mpi" / "mpiexec.exe"
    if os.name != "nt" or not (package_launcher.parent / "msmpi.dll").is_file():
        pytest.skip("Packaged Windows MS-MPI runtime is unavailable")
    dims = mpi_dimensions_for_counts(range(1, 33), package_launcher)
    assert dims[8] == (4, 2)
    assert dims[16] == (4, 4)
    assert dims[32] == (8, 4)


def test_frozen_dimensions_probe_uses_hidden_exe_mode_not_python_dash_c(monkeypatch, tmp_path):
    import types
    import mpi_runner
    import os as real_os
    monkeypatch.setattr(mpi_runner, "os", types.SimpleNamespace(
        name="nt", environ=real_os.environ, pathsep=real_os.pathsep,
        close=real_os.close))
    monkeypatch.setattr(mpi_runner.sys, "frozen", True, raising=False)
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        Path(command[-1]).write_text("2:2:1\n4:2:2\n", encoding="utf-8")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(mpi_runner.subprocess, "run", fake_run)
    mpi_runner._query_mpi_dimensions_cached.cache_clear()
    try:
        result = mpi_runner._query_mpi_dimensions_cached("studio.exe", "msmpi.dll",
                                                          str(tmp_path), (2, 4))
    finally:
        mpi_runner._query_mpi_dimensions_cached.cache_clear()
    assert result == {2: (2, 1), 4: (2, 2)}
    assert calls[0][:2] == ["studio.exe", "--mpi-dims-probe"]
    assert "-c" not in calls[0]


@pytest.mark.parametrize("logical_cpus,expected", [
    (1, 1), (2, 1), (8, 4), (16, 8), (32, 16), (64, 32), (128, 64),
])
def test_recommended_process_count_scales_with_half_available_cpus(logical_cpus, expected):
    assert recommended_process_count(logical_cpus) == expected


@pytest.mark.parametrize("cpus,allowed,expected", [
    (32, [1, 2, 4, 8, 12, 16, 24, 32], 16),
    (32, [1, 2, 4, 8, 12], 12),
    (32, [20, 32], 20),
    (4, [3, 4], 3),
])
def test_recommendation_selects_nearest_legal_decomposition(cpus, allowed, expected):
    assert recommended_process_count(cpus, allowed) == expected


def test_recommendation_returns_none_when_no_legal_decomposition_exists():
    assert recommended_process_count(8, []) is None
    assert recommended_process_count(8, [0, 9, "bad"]) is None


def test_capabilities_turn_on_only_when_all_dependencies_are_registered(tmp_path, monkeypatch):
    launcher, solver = tmp_path / "mpiexec.exe", tmp_path / "solver.exe"
    launcher.touch()
    solver.touch()
    (tmp_path / "msmpi.dll").touch()
    import mpi_runner
    monkeypatch.setattr(mpi_runner, "inspect_runtime", lambda _: {"ready": True})
    result = mpi_capabilities(launcher=launcher, solver=solver, merger=lambda *_: None,
                              feature_enabled=True)
    assert result["enabled"]
    assert result["recommended_processes"] == max(1, (result["max_processes"] + 1) // 2)
    result = mpi_capabilities(launcher=launcher, solver=solver, merger=None,
                              feature_enabled=True)
    assert result["enabled"] is False
    assert "rank output merger" in result["reason"]


def test_discover_mpi_installation_uses_packaged_paths_unless_overridden(tmp_path, monkeypatch):
    import mpi_runner
    app_bin = tmp_path / "bin"
    (app_bin / "mpi").mkdir(parents=True)
    (app_bin / "runtime").mkdir()
    (app_bin / "mpi" / "mpiexec.exe").touch()
    (app_bin / "getm_cartesian_parallel.exe").touch()
    monkeypatch.setattr(mpi_runner, "__file__", str(tmp_path / "app" / "mpi_runner.py"))
    result = discover_mpi_installation()
    assert result["launcher"] == (app_bin / "mpi" / "mpiexec.exe").resolve()
    assert result["solver"] == (app_bin / "getm_cartesian_parallel.exe").resolve()
    monkeypatch.setenv("WET_MPIEXEC", str(tmp_path / "custom-mpiexec.exe"))
    monkeypatch.setenv("WET_MPI_SOLVER", str(tmp_path / "custom-solver.exe"))
    custom = discover_mpi_installation()
    assert custom["launcher"] == (tmp_path / "custom-mpiexec.exe").resolve()
    assert custom["solver"] == (tmp_path / "custom-solver.exe").resolve()


def test_discover_mpi_installation_finds_assets_next_to_frozen_bundle(tmp_path, monkeypatch):
    import mpi_runner
    install = tmp_path / "3DWETStudio"
    internal = install / "_internal"
    model_bin = install / "3DWET" / "bin"
    mpi_dir = model_bin / "mpi"
    (internal).mkdir(parents=True)
    (mpi_dir).mkdir(parents=True)
    (model_bin / "getm_cartesian_parallel.exe").touch()
    (model_bin / "runtime").mkdir()
    (mpi_dir / "mpiexec.exe").touch()
    (mpi_dir / "msmpi.dll").touch()
    monkeypatch.setattr(mpi_runner, "__file__", str(internal / "mpi_runner.py"))

    result = discover_mpi_installation()

    assert result["solver"] == (model_bin / "getm_cartesian_parallel.exe").resolve()
    assert result["launcher"] == (mpi_dir / "mpiexec.exe").resolve()
    assert result["runtime_dirs"] == [(model_bin / "runtime").resolve(), mpi_dir.resolve()]


def test_mpi_command_keeps_launcher_arguments_separate():
    assert mpi_command("C:/mpi/mpiexec.exe", "C:/solver/getm.exe", 3) == [
        "C:/mpi/mpiexec.exe", "-n", "3", "C:/solver/getm.exe"]


def test_feature_gate_and_required_merger(tmp_path):
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "getm.exe"
    launcher.touch()
    solver.touch()
    with pytest.raises(RuntimeError, match="disabled"):
        MpiRun(launcher=launcher, solver=solver, n=2, case=tmp_path,
               feature_enabled=False, merger=lambda *_: None)
    with pytest.raises(RuntimeError, match="merger"):
        MpiRun(launcher=launcher, solver=solver, n=2, case=tmp_path,
               feature_enabled=True)


def test_successful_run_calls_reserved_merge_hook(tmp_path):
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "getm.exe"
    launcher.touch()
    solver.touch()
    calls = []

    class Process:
        args = [str(launcher), "-n", "2", str(solver)]
        returncode = 0
        def poll(self): return 0
        def wait(self, *args, **kwargs): return 0

    captured = {}
    def fake_popen(*args, **kwargs):
        captured["env"] = kwargs["env"]
        return Process()
    runtime = tmp_path / "app-runtime"
    ucrt = tmp_path / "ucrt64"
    runtime.mkdir(); ucrt.mkdir()
    run = MpiRun(launcher=launcher, solver=solver, n=2, case=tmp_path,
                 merger=lambda case, n: calls.append((case, n)) or "merged",
                 feature_enabled=True, runtime_dirs=[runtime, ucrt], popen=fake_popen)
    run.start()
    path = captured["env"]["PATH"].split(os.pathsep)
    assert path[:3] == [str(runtime.resolve()), str(launcher.resolve().parent), str(ucrt.resolve())]
    assert run.finish() == "merged"
    assert calls == [(tmp_path, 2)]


def test_windows_stop_terminates_whole_process_tree():
    calls = []

    class Process:
        pid = 123
        def poll(self): return None
        def wait(self, timeout=None): calls.append(("wait", timeout)); return 0

    def fake_run(command, **kwargs): calls.append(command)
    stop_process_tree(Process(), windows=True, run=fake_run)
    assert calls[0] == ["taskkill", "/PID", "123", "/T", "/F"]


def test_exit_zero_with_rank_fatal_never_calls_merger(tmp_path):
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "getm.exe"
    launcher.touch()
    solver.touch()

    class Process:
        args = [str(launcher), "-n", "2", str(solver)]
        returncode = 0
        def poll(self): return 0
        def wait(self, *args, **kwargs): return 0

    run = MpiRun(launcher=launcher, solver=solver, n=2, case=tmp_path,
                 merger=lambda *_: pytest.fail("merge must not run after rank fatal"),
                 feature_enabled=True, popen=lambda *a, **k: Process())
    run.start()
    (tmp_path / "model_run.log").write_text("FATAL GETM ERROR: bad rank\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match=r"MPI solver failure detected despite MPI launcher exit 0.*model_run\.log"):
        run.finish()


def test_prepare_mpi_case_isolated_configuration_and_ignores_stale_outputs(tmp_path):
    source = tmp_path / "case"
    source.mkdir()
    (source / "getm.inp").write_text("&param\n parallel = .false.\n hotstart = .false.\n/\n", encoding="utf-8")
    (source / "bathymetry.nc").write_bytes(b"grid")
    (source / "restart.in").write_bytes(b"checkpoint")
    (source / "LAKE.2d.0000.nc").write_bytes(b"stale shard")
    (source / "LAKE.0000.stderr").write_text("stale progress n = 999\n", encoding="utf-8")
    (source / "LAKE.0000.stdout").write_text("stale stdout\n", encoding="utf-8")
    (source / "output.nc").write_bytes(b"old result")
    (source / "output").mkdir()
    (source / "output" / "old.nc").write_bytes(b"archived result")
    work = prepare_mpi_case(source, msg_method=3, process_count=2)
    try:
        assert "parallel = .false." in (source / "getm.inp").read_text(encoding="utf-8")
        assert (source / "output.nc").read_bytes() == b"old result"
        assert "parallel = .true." in (work / "getm.inp").read_text(encoding="utf-8")
        assert "MeshMethod=1" in (work / "parallel.inp").read_text(encoding="ascii")
        assert "MsgMethod=3" in (work / "parallel.inp").read_text(encoding="ascii")
        assert (work / "restart.in").read_bytes() == b"checkpoint"
        assert not (work / "LAKE.2d.0000.nc").exists()
        assert not (work / "LAKE.0000.stderr").exists()
        assert not (work / "LAKE.0000.stdout").exists()
        assert not (work / "output.nc").exists()
        assert not (work / "output").exists()
    finally:
        import shutil
        shutil.rmtree(work)


def test_prepare_mpi_case_rejects_serial_fabm_hotstart(tmp_path):
    source = tmp_path / "case"
    source.mkdir()
    (source / "getm.inp").write_text(
        "&param\n parallel = .false.\n hotstart = .true.\n/\n", encoding="utf-8")
    (source / "restart.in").write_bytes(b"global checkpoint")
    with pytest.raises(ValueError, match="MPI hotstart is currently unsupported"):
        prepare_mpi_case(source, msg_method=3, process_count=2)
    assert (source / "restart.in").read_bytes() == b"global checkpoint"
    assert not list(tmp_path.glob(".case.mpi-*"))


def test_prepare_mpi_case_can_disable_fabm_hotstart_without_editing_the_source(tmp_path):
    source = tmp_path / "case"
    source.mkdir()
    (source / "getm.inp").write_text(
        "&param\n parallel = .false.\n hotstart = .true.\n/\n", encoding="utf-8")
    work = prepare_mpi_case(source, msg_method=3, process_count=2, disable_hotstart=True)
    try:
        copied = (work / "getm.inp").read_text(encoding="utf-8")
        assert "hotstart = .false." in copied
        assert "parallel = .true." in copied
        assert "hotstart = .true." in (source / "getm.inp").read_text(encoding="utf-8")
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)


def test_mpi_hotstart_preflight_error_is_specific_and_cold_runs_are_allowed():
    assert mpi_hotstart_error({"param": {"hotstart": True}}) == (
        "MPI hotstart is currently unsupported: reading the serial checkpoint fails at the "
        "FABM temporal checkpoint. Use a cold MPI start or a serial run."
    )
    assert mpi_hotstart_error({"param": {"hotstart": False}}) is None
    assert mpi_hotstart_error({}) is None


def test_empty_2d_3d_families_are_skipped_but_output_family_is_merged(tmp_path, monkeypatch):
    from netCDF4 import Dataset
    import sys
    import types

    (tmp_path / "bathymetry.nc").touch()
    calls = []
    def fake_merge(shards, reference, destination):
        calls.append((list(shards), reference, destination))
        destination.touch()
        return destination
    fake_module = types.ModuleType("merge_getm_rank_outputs")
    fake_module.merge_rank_outputs = fake_merge
    monkeypatch.setitem(sys.modules, "merge_getm_rank_outputs", fake_module)

    for family, length in (("LAKE.2d", 0), ("LAKE.3d", 0), ("output", 1)):
        for rank in range(2):
            with Dataset(tmp_path / f"{family}.{rank:04d}.nc", "w") as ds:
                ds.createDimension("time", None)
                if length:
                    time = ds.createVariable("time", "f8", ("time",))
                    time[:] = [0.0]

    result = merge_case_rank_outputs(tmp_path, 2)
    assert len(calls) == 1
    assert calls[0][2].name == "output.nc"
    assert [Path(path).name for path in result] == ["output.nc"]


def test_empty_output_family_is_not_reported_as_a_complete_result(tmp_path, monkeypatch):
    from netCDF4 import Dataset
    import sys
    import types

    (tmp_path / "bathymetry.nc").touch()
    fake_module = types.ModuleType("merge_getm_rank_outputs")
    fake_module.merge_rank_outputs = lambda *_: pytest.fail("empty families must not merge")
    monkeypatch.setitem(sys.modules, "merge_getm_rank_outputs", fake_module)
    for family in ("LAKE.2d", "LAKE.3d", "output"):
        for rank in range(2):
            with Dataset(tmp_path / f"{family}.{rank:04d}.nc", "w") as ds:
                ds.createDimension("time", None)
    with pytest.raises(RuntimeError, match="no time records in output"):
        merge_case_rank_outputs(tmp_path, 2)


def test_mixed_empty_and_nonempty_rank_family_is_rejected(tmp_path, monkeypatch):
    from netCDF4 import Dataset
    import sys
    import types

    (tmp_path / "bathymetry.nc").touch()
    fake_module = types.ModuleType("merge_getm_rank_outputs")
    fake_module.merge_rank_outputs = lambda *_: pytest.fail("inconsistent rank family must not merge")
    monkeypatch.setitem(sys.modules, "merge_getm_rank_outputs", fake_module)
    for rank, length in enumerate((0, 1)):
        with Dataset(tmp_path / f"output.{rank:04d}.nc", "w") as ds:
            ds.createDimension("time", None)
            if length:
                var = ds.createVariable("time", "f8", ("time",))
                var[:] = [0.0]
    with pytest.raises(RuntimeError, match="inconsistent empty/non-empty"):
        merge_case_rank_outputs(tmp_path, 2)


def test_windows_mpi_status_accepts_the_revision_marker_and_bundled_runtime(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    mpi = bin_dir / "mpi"
    mpi.mkdir(parents=True)
    (bin_dir / "getm_cartesian_parallel.exe").write_bytes(b"xx3DWET solver revision 20261102yy")
    (bin_dir / "getm_cartesian_parallel_prev.exe").write_bytes(b"old")
    for name in ("msmpi.dll", "mpiexec.exe", "smpd.exe"):
        (mpi / name).write_bytes(b"x")
    monkeypatch.setattr("mpi_runner._packaged_model_root", lambda: tmp_path)
    status = windows_mpi_status()
    assert status["revision_current"] is True
    assert status["runtime_ready"] is True
    assert status["size"] == len(b"xx3DWET solver revision 20261102yy")
    assert status["backup"].endswith("getm_cartesian_parallel_prev.exe")
    assert "当前版本" in status["message"]
    if os.name != "nt":
        assert "Wine" in status["message"]
        assert status["host_can_launch"] is False


def test_windows_mpi_status_skips_a_solver_without_the_revision(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    (bin_dir / "mpi").mkdir(parents=True)
    (bin_dir / "getm_cartesian_parallel.exe").write_bytes(b"old solver")
    monkeypatch.setattr("mpi_runner._packaged_model_root", lambda: tmp_path)
    status = windows_mpi_status()
    assert status["revision_current"] is False
    assert "不是当前源码" in status["message"]


def test_exit_zero_with_rank_stdout_fatal_never_calls_merger(tmp_path):
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "getm.exe"
    launcher.touch(); solver.touch()

    class Process:
        args = [str(launcher), "-n", "2", str(solver)]
        returncode = 0
        def poll(self): return 0
        def wait(self, *args, **kwargs): return 0

    run = MpiRun(launcher=launcher, solver=solver, n=2, case=tmp_path,
                 merger=lambda *_: pytest.fail("rank fatal must block merge"),
                 feature_enabled=True, popen=lambda *a, **k: Process())
    run.start()
    (tmp_path / "GETM.0001.stdout").write_text("FATAL GETM ERROR: rank 1\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match=r"MPI solver failure detected despite MPI launcher exit 0.*GETM\.0001\.stdout"):
        run.finish()
