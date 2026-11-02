import subprocess
import sys
from pathlib import Path

import pytest


APP = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP))
from mpi_runner import MpiRun  # noqa: E402
import mpi_runner  # noqa: E402
import server  # noqa: E402


class FinishedProcess:
    def __init__(self, returncode):
        self.returncode = returncode
        self.args = ["mpiexec", "-n", "2", "solver"]

    def wait(self):
        return self.returncode

    def poll(self):
        return self.returncode


def make_runner(tmp_path):
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "solver.exe"
    launcher.touch()
    solver.touch()
    case = tmp_path / "case"
    case.mkdir()
    return MpiRun(launcher=launcher, solver=solver, n=2, case=case,
                  cpu_count=2, merger=lambda *_: ["merged.nc"],
                  feature_enabled=True), case


def test_nonzero_launcher_exit_preserves_solver_failure_diagnostic(tmp_path):
    runner, case = make_runner(tmp_path)
    runner.process = FinishedProcess(1)
    (case / "model_run.log").write_text("mpiexec exited\n")
    (case / "LAKE.0001.stderr").write_text(
        "STOP 1\nFATAL ERROR: invalid time step\n")

    with pytest.raises(RuntimeError) as error:
        runner.finish()

    assert "solver failure" in str(error.value).lower()
    assert "exit code 1" in str(error.value).lower()
    assert "LAKE.0001.stderr" in str(error.value)
    assert "FATAL ERROR: invalid time step" in str(error.value)


def test_nonzero_launcher_exit_without_solver_diagnostic_stays_process_error(tmp_path):
    runner, case = make_runner(tmp_path)
    runner.process = FinishedProcess(2)
    (case / "model_run.log").write_text("mpiexec failed to start rank 1\n")

    with pytest.raises(subprocess.CalledProcessError, match="exit status 2") as error:
        runner.finish()

    assert error.value.returncode == 2


def test_zero_launcher_exit_still_rejects_solver_failure(tmp_path):
    runner, case = make_runner(tmp_path)
    runner.process = FinishedProcess(0)
    (case / "model_run.log").write_text("FATAL ERROR: invalid time step\n")

    with pytest.raises(RuntimeError, match="MPI solver failure detected"):
        runner.finish()


def run_thread_with_exit(tmp_path, monkeypatch, *, code, launcher_log, rank_stderr=None):
    original_case = tmp_path / "original"
    original_case.mkdir()
    isolated_case = tmp_path / "isolated"
    launcher = tmp_path / "mpiexec.exe"
    solver = tmp_path / "solver.exe"
    launcher.touch()
    solver.touch()
    monkeypatch.setattr(mpi_runner, "prepare_mpi_case", lambda *_args, **_kwargs: isolated_case)

    def start(run):
        run.case.mkdir(parents=True, exist_ok=True)
        (run.case / "model_run.log").write_text(launcher_log, encoding="utf-8")
        if rank_stderr is not None:
            (run.case / "LAKE.0001.stderr").write_text(rank_stderr, encoding="utf-8")
        run.process = FinishedProcess(code)
        return run.process

    monkeypatch.setattr(MpiRun, "start", start)
    monkeypatch.setattr(server, "run_status", "running")
    monkeypatch.setattr(server, "run_logs", [])
    monkeypatch.setattr(server, "run_case_path", None)
    monkeypatch.setattr(server, "run_process", None)
    monkeypatch.setattr(server, "run_config", {"solver_mode": "MPI (2 ranks)", "phase": "solving"})
    monkeypatch.setattr(server.run_metrics, "finish", lambda: None)

    server.run_mpi_model_thread(original_case, launcher, solver, 2)
    return original_case, server.run_logs


def test_mpi_thread_keeps_rank_fatal_diagnostic_when_launcher_fails(tmp_path, monkeypatch):
    original_case, logs = run_thread_with_exit(
        tmp_path,
        monkeypatch,
        code=1,
        launcher_log="mpiexec exited\n",
        rank_stderr="STOP 1\nFATAL ERROR: invalid time step\n",
    )

    assert server.run_status == "failed"
    assert any("MPI solver failure detected" in line for line in logs)
    assert any("LAKE.0001.stderr" in line and "FATAL ERROR: invalid time step" in line
               for line in logs)
    assert "FATAL ERROR: invalid time step" in (
        original_case / "mpi-LAKE.0001.stderr"
    ).read_text(encoding="utf-8")


def test_mpi_thread_keeps_plain_launcher_failure_as_process_error(tmp_path, monkeypatch):
    original_case, logs = run_thread_with_exit(
        tmp_path,
        monkeypatch,
        code=2,
        launcher_log="mpiexec failed to start rank 1\n",
    )

    assert server.run_status == "failed"
    assert any("exit status 2" in line for line in logs)
    assert "mpiexec failed to start rank 1" in (
        original_case / "model_run.mpi.log"
    ).read_text(encoding="utf-8")


def test_failed_mpi_run_keeps_partial_output_and_names_rank(tmp_path, monkeypatch):
    original_case = tmp_path / "Dianchi2023"
    original_case.mkdir()
    isolated_case = tmp_path / ".Dianchi2023.mpi-dead"
    isolated_case.mkdir()
    (isolated_case / "getm.inp").write_text(
        "&time\n timestep = 15.0\n start = '2023-01-01 00:00:00'\n/\n",
        encoding="utf-8")
    (isolated_case / "LAKE_DIANCHI_WET.0006.stdout").write_text(
        " Non-finite value of FABM state variable abiotic_water_sPO4W\n",
        encoding="utf-8")
    (isolated_case / "LAKE_DIANCHI_WET.0006.stderr").write_text(
        "2023-08-10 00:00:00: saving 2D ....\n    02:05:53.472 n=     1275000\n",
        encoding="utf-8")
    (isolated_case / "model_run.log").write_text(
        "n=1275000\nSTOP 1\nProcess name: [prterun-host-1,6]\nExit code:    1\n",
        encoding="utf-8")
    (isolated_case / "LAKE_DIANCHI_WET.2d.0006.nc").write_bytes(b"rank6-partial")
    (isolated_case / "LAKE_DIANCHI_WET.2d.0000.nc").write_bytes(b"rank0-partial")
    launcher = tmp_path / "mpiexec"
    solver = tmp_path / "solver"
    launcher.touch()
    solver.touch()
    monkeypatch.setattr(mpi_runner, "prepare_mpi_case", lambda *_args, **_kwargs: isolated_case)

    def start(run):
        run.process = FinishedProcess(1)
        return run.process

    monkeypatch.setattr(MpiRun, "start", start)
    monkeypatch.setattr(server, "run_status", "running")
    monkeypatch.setattr(server, "run_logs", [])
    monkeypatch.setattr(server, "run_case_path", None)
    monkeypatch.setattr(server, "run_process", None)
    monkeypatch.setattr(server, "run_config", {"solver_mode": "MPI (8 ranks)", "phase": "solving"})
    monkeypatch.setattr(server.run_metrics, "finish", lambda: None)

    server.run_mpi_model_thread(original_case, launcher, solver, 8)

    assert server.run_status == "failed"
    text = "\n".join(server.run_logs)
    assert "abiotic_water_sPO4W" in text
    assert "rank 6" in text
    assert "2023-08-10 08:30:00" in text
    assert "n=1275000" in text
    assert (original_case / "output" / "LAKE_DIANCHI_WET.2d.0006.nc").read_bytes() == b"rank6-partial"
    assert (original_case / "output" / "LAKE_DIANCHI_WET.2d.0000.nc").read_bytes() == b"rank0-partial"
    assert "失败前的输出已保存到 output/" in text


def test_nonfinite_before_first_step_is_not_retried_as_serial(tmp_path, monkeypatch):
    original_case = tmp_path / "lake"
    original_case.mkdir()
    isolated_case = tmp_path / "work"
    isolated_case.mkdir()
    (isolated_case / "getm.inp").write_text(
        "&time\n timestep = 15.0\n start = '2023-08-01 00:00:00'\n/\n",
        encoding="utf-8")
    (isolated_case / "LAKE.0006.stdout").write_text(
        "2023-08-01 00:00:00: integrating\n"
        "Non-finite value of FABM state variable abiotic_water_sPO4W\n",
        encoding="utf-8")
    (isolated_case / "model_run.log").write_text(
        "STOP 1\nProcess name: [prterun-host-1,6]\n",
        encoding="utf-8")
    (isolated_case / "LAKE.2d.0006.nc").write_bytes(b"partial")
    launcher = tmp_path / "mpiexec"
    solver = tmp_path / "solver"
    launcher.touch()
    solver.touch()
    monkeypatch.setattr(mpi_runner, "prepare_mpi_case", lambda *_a, **_k: isolated_case)

    def start(run):
        run.process = FinishedProcess(1)
        return run.process

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("serial fallback must not hide a diagnosed FABM failure")

    monkeypatch.setattr(MpiRun, "start", start)
    monkeypatch.setattr(server, "run_model_thread", fail_if_called)
    monkeypatch.setattr(server, "run_status", "running")
    monkeypatch.setattr(server, "run_logs", [])
    monkeypatch.setattr(server, "run_case_path", None)
    monkeypatch.setattr(server, "run_process", None)
    monkeypatch.setattr(server, "run_config", {"solver_mode": "MPI (8 ranks)", "phase": "solving"})
    monkeypatch.setattr(server.run_metrics, "finish", lambda: None)

    server.run_mpi_model_thread(original_case, launcher, solver, 8)

    assert server.run_status == "failed"
    text = "\n".join(server.run_logs)
    assert "abiotic_water_sPO4W" in text
    assert "rank 6" in text
    assert "2023-08-01 00:00:00" in text
    assert (original_case / "output" / "LAKE.2d.0006.nc").read_bytes() == b"partial"
