import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from run_metrics import RunMetrics


def test_getm_progress_uses_last_completed_step_and_only_completed_reaches_100_percent():
    metrics = RunMetrics()
    metrics.start({"nsteps": 400}, now=0)

    metrics.observe("12:00:00.000 n=400\n", now=10)
    running = metrics.snapshot("running", now=10)

    assert running["current_step"] == 399
    assert running["progress"] == 99.75
    assert running["steps_per_second"] is None
    assert running["eta_seconds"] is None
    assert metrics.snapshot("completed", now=10)["progress"] == 100


def test_eta_and_rate_remain_stable_between_solver_step_observations():
    metrics = RunMetrics()
    metrics.start({"nsteps": 400}, now=0)
    metrics.observe("n=100\n", now=10)
    metrics.observe("n=200\n", now=20)

    observed = metrics.snapshot("running", now=20)
    polled_later = metrics.snapshot("running", now=30)

    assert observed["current_step"] == 199
    assert observed["steps_per_second"] == 10
    assert observed["eta_seconds"] == 201 / 10
    assert polled_later["steps_per_second"] == observed["steps_per_second"]
    assert polled_later["eta_seconds"] == observed["eta_seconds"]


def test_unknown_progress_stays_unknown_for_engines_without_getm_step_records():
    metrics = RunMetrics()
    metrics.start({"engine": "official_gotm_reference_working_copy"}, now=0)

    status = metrics.snapshot("running", now=10)

    assert status["current_step"] is None
    assert status["total_steps"] is None
    assert status["progress"] is None
    assert status["steps_per_second"] is None
    assert status["eta_seconds"] is None


def test_gotm_does_not_interpret_an_unrelated_n_record_as_getm_progress():
    metrics = RunMetrics()
    metrics.start({"engine": "official_gotm_reference_working_copy", "nsteps": 400}, now=0)
    metrics.observe("n=400\n", now=10)

    status = metrics.snapshot("running", now=10)

    assert status["current_step"] is None
    assert status["progress"] is None


def test_available_solver_physics_diagnostic_reports_completed_step_without_getm_offset():
    metrics = RunMetrics()
    metrics.start({"nsteps": 10}, now=0)
    metrics.observe(
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=10 "
        "sim_time=2020-01-01T00:00:50 global_i=22 global_j=9 "
        "z_surface_m=0.0 H_static_m=13.0 D_total_m=13.0\n",
        now=5,
    )

    status = metrics.snapshot("running", now=5)

    assert status["current_step"] == 10
    assert status["progress"] == 99.9
    assert status["eta_seconds"] is None


def test_unavailable_or_incomplete_physics_diagnostics_do_not_claim_progress():
    for line in (
        "GETM_PHYSICS_DIAG status=unavailable kind=center_wet_T completed_step=10\n",
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=10 sim_time=unknown\n",
    ):
        metrics = RunMetrics()
        metrics.start({"nsteps": 10}, now=0)
        metrics.observe(line, now=5)
        assert metrics.snapshot("running", now=5)["current_step"] is None


def test_mpi_uses_complete_rank_zero_diagnostic_as_completed_step_and_keeps_n_progress():
    metrics = RunMetrics()
    metrics.start({"nsteps": 400, "solver_mode": "MPI (4 ranks)"}, now=0)
    metrics.observe(
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=10 "
        "sim_time=2020-01-01T00:00:50 global_i=22 global_j=9 "
        "owner_rank=1 z_surface_m=0.0 H_static_m=13.0 D_total_m=13.0\n",
        now=5, source="rank0_stderr",
    )
    assert metrics.snapshot("running", now=5)["current_step"] == 10
    assert metrics.snapshot("running", now=5)["progress"] == 2.5
    metrics.observe("n=20\n", now=6, source="rank0_stderr")
    assert metrics.snapshot("running", now=6)["current_step"] == 19


def test_mpi_physics_diagnostic_requires_complete_owner_and_available_record():
    for line in (
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=10 "
        "sim_time=2020-01-01T00:00:50 global_i=22 global_j=9 "
        "z_surface_m=0.0 H_static_m=13.0 D_total_m=13.0\n",
        "GETM_PHYSICS_DIAG status=unsupported reason=mpi_hotstart_unverified\n",
        "GETM_PHYSICS_DIAG status=unavailable reason=no_wet_cell completed_step=10\n",
    ):
        metrics = RunMetrics()
        metrics.start({"nsteps": 400, "solver_mode": "MPI (2 ranks)"}, now=0)
        metrics.observe(line, now=5, source="rank0_stderr")
        assert metrics.snapshot("running", now=5)["current_step"] is None


def test_mpi_short_run_diagnostic_is_already_a_completed_step():
    metrics = RunMetrics()
    metrics.start({"nsteps": 3, "solver_mode": "MPI (2 ranks)"}, now=0)
    metrics.observe(
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=1 "
        "sim_time=2020-01-01T00:00:30 global_i=5 global_j=2 owner_rank=0 "
        "z_surface_m=0.0 H_static_m=4.0 D_total_m=4.0\n",
        now=2, source="rank0_stderr",
    )
    status = metrics.snapshot("running", now=2)
    assert status["current_step"] == 1
    assert status["progress"] == 100 / 3
    assert status["eta_seconds"] is None


def test_latest_mpi_physics_diagnostic_survives_log_flood_and_finished_status():
    metrics = RunMetrics()
    metrics.start({"nsteps": 101, "solver_mode": "MPI (4 ranks)"}, now=0)
    latest = (
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=101 "
        "sim_time=2020-01-01T00:50:30 global_i=5 global_j=2 owner_rank=0 "
        "z_surface_m=3.06548886E-005 H_static_m=4.35605397E+000 "
        "D_total_m=4.35608462E+000\n"
    )
    metrics.observe(latest, now=10, source="rank0_stderr")
    # This mirrors run_logs clipping after high-volume MPI stderr has been
    # consumed; the latest point is stored separately from that bounded list.
    metrics.observe("ordinary solver message\n" * 6000, now=11, source="rank0_stderr")

    diagnostic = metrics.snapshot("completed", now=12)["physics_diagnostic"]
    assert diagnostic == {
        "status": "available",
        "source": "rank0_stderr",
        "kind": "center_wet_T",
        "completed_step": 101,
        "sim_time": "2020-01-01T00:50:30",
        "global_i": 5,
        "global_j": 2,
        "owner_rank": 0,
        "z_surface_m": 3.06548886e-5,
        "H_static_m": 4.35605397,
        "D_total_m": 4.35608462,
    }


def test_mpi_physics_diagnostic_accepts_only_rank_zero_source_and_resets_on_new_run():
    metrics = RunMetrics()
    metrics.start({"nsteps": 10, "solver_mode": "MPI (2 ranks)"}, now=0)
    line = (
        "GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=1 "
        "sim_time=2020-01-01T00:00:30 global_i=5 global_j=2 owner_rank=1 "
        "z_surface_m=0.0 H_static_m=4.0 D_total_m=4.0\n"
    )
    metrics.observe(line, now=1, source="rank1_stderr")
    assert metrics.snapshot("running", now=1)["physics_diagnostic"] is None

    metrics.observe(line, now=2, source="rank0_stderr")
    assert metrics.snapshot("failed", now=2)["physics_diagnostic"]["owner_rank"] == 1
    metrics.start({"nsteps": 5, "solver_mode": "MPI (2 ranks)"}, now=3)
    assert metrics.snapshot("running", now=4)["physics_diagnostic"] is None


def test_mpi_unavailable_and_unsupported_physics_statuses_are_retained_without_values():
    metrics = RunMetrics()
    metrics.start({"nsteps": 10, "solver_mode": "MPI (2 ranks)"}, now=0)
    metrics.observe(
        "GETM_PHYSICS_DIAG status=unavailable reason=no_wet_cell completed_step=1\n",
        now=1, source="rank0_stderr",
    )
    assert metrics.snapshot("running", now=1)["physics_diagnostic"] == {
        "status": "unavailable", "source": "rank0_stderr", "reason": "no_wet_cell",
        "completed_step": 1,
    }
    metrics.observe(
        "GETM_PHYSICS_DIAG status=unsupported reason=mpi_hotstart_unverified\n",
        now=2, source="rank0_stderr",
    )
    assert metrics.snapshot("running", now=2)["physics_diagnostic"] == {
        "status": "unsupported", "source": "rank0_stderr",
        "reason": "mpi_hotstart_unverified",
    }

