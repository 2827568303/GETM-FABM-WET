import sys
import types
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP))
import mpi_tuning  # noqa: E402


@pytest.mark.parametrize(("repetitions", "expected_order"), [
    (1, [1, 2, 4]),
    (2, [1, 2, 4, 4, 2, 1]),
])
def test_mpi_trials_reverse_candidate_order_by_repetition_round(
        tmp_path, monkeypatch, repetitions, expected_order):
    source = tmp_path / "source"
    source.mkdir()
    (source / "getm.inp").write_text(
        "start = '2000-01-01 00:00:00'\nstop = '2000-01-02 00:00:00'\ntimestep = 60\n",
        encoding="utf-8",
    )
    order = []

    class Runner:
        def __init__(self, *, n, **kwargs):
            self.n = n
            self.process = None

        def start(self):
            order.append(self.n)
            self.process = types.SimpleNamespace(poll=lambda: 0)

        def finish(self):
            return ["merged.nc"]

    monkeypatch.setattr(mpi_tuning, "choose_tuning_candidates", lambda *a, **k: [1, 2, 4])
    monkeypatch.setattr(mpi_tuning, "minimum_trial_duration", lambda *_: 1)
    def prepare_trial(*args, **kwargs):
        trial = tmp_path / "trial"
        trial.mkdir()
        (trial / "getm.inp").write_text(
            "start = '2000-01-01 00:00:00'\nstop = '2000-01-02 00:00:00'\ntimestep = 60\n",
            encoding="utf-8",
        )
        return trial

    monkeypatch.setitem(sys.modules, "mpi_runner", types.SimpleNamespace(
        MpiRun=Runner,
        prepare_mpi_case=prepare_trial,
        merge_case_rank_outputs=lambda *_: ["merged.nc"],
    ))
    monkeypatch.setitem(sys.modules, "run_output_health", types.SimpleNamespace(
        validate_current_run_outputs=lambda *a, **k: {"ready": True, "errors": []},
    ))
    monkeypatch.setitem(sys.modules, "netCDF4", types.SimpleNamespace(Dataset=object))

    result = mpi_tuning.benchmark_mpi_case(
        source, launcher="mpi", solver="solver", runtime_dirs=[],
        allowed_processes=[1, 2, 4], physical_cores=4, repetitions=repetitions,
    )

    assert order == expected_order
    assert result["repetitions"] == repetitions
    assert all(len(samples) == repetitions for samples in result["measurements"].values())


def test_mpi_tuning_ui_requests_two_trials_and_labels_simulated_duration():
    source = (APP / "static" / "js" / "app.js").read_text(encoding="utf-8")

    assert "duration_seconds:10800,repetitions:2" in source
    assert "覆盖至少 ${trialHours} 小时的模拟时段" in source
