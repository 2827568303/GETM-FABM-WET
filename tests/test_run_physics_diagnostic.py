import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "3DWET" / "app"))
from run_metrics import RunMetrics


def _tracker():
    tracker = RunMetrics()
    tracker.start({"nsteps": 200}, now=10)
    return tracker


def test_snapshot_exposes_valid_solver_physics_diagnostic():
    tracker = _tracker()
    # Field order and spellings match GETM's serial integration diagnostic.
    tracker.observe(
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 "
        "sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 "
        "z_surface_m=1.25 H_static_m=4.5 D_total_m=5.75\n",
        now=11,
        source="solver_log",
    )

    snapshot = tracker.snapshot("running", now=12)
    assert snapshot["physics_diagnostic"] == {
        "status": "available",
        "source": "solver_log",
        "kind": "center_wet_T",
        "completed_step": 100,
        "sim_time": "2001-02-03T04:05:06",
        "global_i": 12,
        "global_j": 8,
        "z_surface_m": 1.25,
        "H_static_m": 4.5,
        "D_total_m": 5.75,
    }
    assert snapshot["current_step"] == 100
    assert snapshot["progress"] == 50


def test_snapshot_rejects_non_finite_or_inconsistent_solver_diagnostics():
    invalid_records = (
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 "
        "sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 "
        "z_surface_m=NaN H_static_m=4.5 D_total_m=5.75\n",
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=100 "
        "sim_time=2001-02-03T04:05:06 global_i=12 global_j=8 "
        "z_surface_m=1 H_static_m=4.5 D_total_m=99\n",
    )
    for record in invalid_records:
        tracker = _tracker()
        tracker.observe(record, now=11, source="solver_log")

        snapshot = tracker.snapshot("running", now=12)
        assert snapshot["physics_diagnostic"] is None
        assert snapshot["current_step"] is None
        assert snapshot["progress"] is None


def test_snapshot_preserves_solver_unavailable_reason_without_claiming_progress():
    tracker = _tracker()
    # GETM emits this form when no wet cell can be sampled.
    tracker.observe(
        "GETM_PHYSICS_DIAG status=unavailable reason=no_wet_cell completed_step=100\n",
        now=11,
        source="solver_log",
    )

    snapshot = tracker.snapshot("running", now=12)
    assert snapshot["physics_diagnostic"] == {
        "status": "unavailable",
        "source": "solver_log",
        "reason": "no_wet_cell",
        "completed_step": 100,
    }
    assert snapshot["current_step"] is None
    assert snapshot["progress"] is None
