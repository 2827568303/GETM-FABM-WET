"""Core-count selection has no ceiling and remembers a measured choice."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "3DWET" / "app"))

import core_plan
from solver_runtime import recommended_openmp_threads, solver_environment


def test_core_count_has_no_upper_bound():
    assert core_plan.parse_core_count(1) == 1
    assert core_plan.parse_core_count("100000") == 100000
    assert core_plan.parse_core_count(" 32 ") == 32
    for bad in (0, -1, True, False, 1.5, "1.5", "", None, "32 cores"):
        with pytest.raises(ValueError):
            core_plan.parse_core_count(bad)


def test_small_lake_guess_does_not_grow_with_a_large_machine():
    dianchi_32 = recommended_openmp_threads(32, wet_columns=1150)
    dianchi_128 = recommended_openmp_threads(128, wet_columns=1150)
    assert dianchi_32 == dianchi_128 == 3
    assert dianchi_32 <= 4
    assert recommended_openmp_threads(8) == 7
    assert recommended_openmp_threads(2, wet_columns=1150) == 2


def test_benchmark_counts_include_the_whole_machine():
    assert core_plan.benchmark_thread_counts(32) == [1, 2, 4, 8, 16, 32]
    assert core_plan.benchmark_thread_counts(3) == [1, 2, 3]
    assert core_plan.benchmark_thread_counts(4) == [1, 2, 4]
    assert max(core_plan.benchmark_thread_counts(256)) == 256


def test_fingerprint_changes_when_the_machine_changes():
    base = {"logical": 4, "physical": 4, "sockets": 1, "numa_nodes": 1,
            "system": "Linux", "machine": "vm", "mpi_launcher": "",
            "srun": "", "parallel_solver": ""}
    other = dict(base, logical=32)
    assert core_plan.hardware_fingerprint(base) != core_plan.hardware_fingerprint(other)


def test_cache_roundtrip_is_keyed_by_machine_grid_and_exe(tmp_path, monkeypatch):
    cache = tmp_path / "core_calibration.json"
    monkeypatch.setenv("WET_CORE_CACHE", str(cache))
    hardware = {"logical": 4, "physical": 4, "sockets": 1, "numa_nodes": 1,
                "system": "Linux", "machine": "vm", "mpi_launcher": "",
                "srun": "", "parallel_solver": ""}
    grid = {"nx": 41, "ny": 67, "layers": 10, "wet_columns": 1150}
    exe = tmp_path / "getm_cartesian"
    exe.write_bytes(b"exe")
    choice = {"mode": "threads", "threads": 2, "ranks": 1, "cores": 2,
              "source": "measured", "steps_per_second": 80.0}
    data = {"entries": {core_plan.cache_key(hardware, grid, exe): {"choice": choice}}}
    core_plan.save_cache(data)
    loaded = core_plan.lookup_choice(hardware, grid, exe)
    assert loaded["cores"] == 2
    assert loaded["source"] == "measured"
    assert json.loads(cache.read_text(encoding="utf-8"))["entries"]


def test_choose_fastest_breaks_ties_toward_fewer_cores():
    results = [
        {"ok": True, "threads": 4, "ranks": 1, "steps_per_second": 10},
        {"ok": True, "threads": 2, "ranks": 1, "steps_per_second": 10},
        {"ok": False, "threads": 1, "ranks": 1, "steps_per_second": 100},
    ]
    choice = core_plan.choose_fastest(results)
    assert choice["threads"] == 2
    assert choice["cores"] == 2
    assert core_plan.choose_fastest([{"ok": False}]) is None


def test_integration_rate_uses_the_progress_lines():
    log = "noise\n00:00:01.000 n=         100\n00:00:03.000 n=         300\n"
    assert core_plan.integration_rate(log) == pytest.approx(100)
    assert core_plan.integration_rate("00:00:01.000 n=         100\n") is None


def test_auto_uses_the_cache_and_mpi_needs_a_launcher(tmp_path, monkeypatch):
    monkeypatch.setenv("WET_CORE_CACHE", str(tmp_path / "cache.json"))
    hardware = {"logical": 32, "physical": 16, "sockets": 2, "numa_nodes": 2,
                "system": "Linux", "machine": "hpc", "mpi_launcher": "",
                "srun": "", "parallel_solver": "", "mpi_available": False}
    grid = {"nx": 41, "ny": 67, "layers": 10, "wet_columns": 1150}
    exe = tmp_path / "solver"
    exe.write_bytes(b"x")
    plan = core_plan.resolve_plan(hardware, grid, exe, mode="auto")
    assert plan["source"] == "heuristic"
    assert plan["threads"] == 3
    assert plan["ranks"] == 1
    with pytest.raises(ValueError):
        core_plan.resolve_plan(hardware, grid, exe, requested_cores=128, mode="mpi")
    explicit = core_plan.resolve_plan(hardware, grid, exe, requested_cores=100000, mode="threads")
    assert explicit["threads"] == 100000
    hybrid = core_plan.resolve_plan(hardware, grid, exe, requested_cores=16, mode="hybrid")
    assert hybrid["mode"] == "threads"
    assert "没有 MPI" in hybrid["note"]
    hardware["mpi_available"] = True
    hardware["srun"] = "/usr/bin/srun"
    split = core_plan.resolve_plan(hardware, grid, exe, requested_cores=16, mode="hybrid")
    assert split["mode"] == "hybrid"
    assert split["threads"] * split["ranks"] == 16


def test_explicit_thread_count_reaches_a_parallel_executable():
    env = solver_environment(
        Path("/tmp/getm_cartesian_parallel.exe"), {"PATH": "/usr/bin"}, threads=4)
    assert env["OMP_NUM_THREADS"] == "4"
    assert env["OMP_WAIT_POLICY"] == "PASSIVE"


def test_case_copy_keeps_bathymetry_and_drops_results(tmp_path):
    source = tmp_path / "case"
    source.mkdir()
    (source / "getm.inp").write_text("start = '2023-01-01 00:00:00'\n", encoding="utf-8")
    (source / "bathymetry.nc").write_bytes(b"bathy")
    (source / "output.nc").write_bytes(b"result")
    (source / "LAKE.3d.nc").write_bytes(b"field")
    nested = source / "forcing"
    nested.mkdir()
    (nested / "note.txt").write_text("keep", encoding="utf-8")
    dest = tmp_path / "copy"
    core_plan._copy_case(source, dest)
    assert (dest / "bathymetry.nc").read_bytes() == b"bathy"
    assert (dest / "getm.inp").is_file()
    assert (dest / "forcing" / "note.txt").read_text(encoding="utf-8") == "keep"
    assert not (dest / "output.nc").exists()
    assert not (dest / "LAKE.3d.nc").exists()
