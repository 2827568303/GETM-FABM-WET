from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parents[1] / "3DWET" / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from mpi_tuning import (choose_tuning_candidates, minimum_trial_duration,
                        rank_count_from_measurements)


def test_tuning_candidates_cover_single_balanced_and_physical_core_limits():
    assert choose_tuning_candidates(
        allowed_processes=list(range(1, 33)), physical_cores=16
    ) == [1, 4, 8, 16, 32]
    assert choose_tuning_candidates(
        allowed_processes=list(range(1, 33)), physical_cores=16,
        logical_cores=32
    ) == [1, 4, 8, 16, 32]


def test_tuning_candidates_are_filtered_by_grid_decomposition():
    assert choose_tuning_candidates(
        allowed_processes=[1, 2, 4, 8, 12, 16, 24, 32], physical_cores=16
    ) == [1, 4, 8, 16, 32]
    assert choose_tuning_candidates(
        allowed_processes=[1, 2, 4, 8, 12, 16, 24, 32], physical_cores=16,
        logical_cores=16
    ) == [1, 4, 8, 16]
    assert choose_tuning_candidates([1, 2, 4], physical_cores=16) == [1, 2, 4]
    assert choose_tuning_candidates([25, 28], physical_cores=24,
                                   logical_cores=32) == [25, 28]
    assert choose_tuning_candidates([], physical_cores=24) == []


def test_tuning_selects_fastest_measured_rank_count_and_breaks_near_ties_small():
    measurements = {
        1: [102.0, 100.0, 101.0],
        8: [38.0, 36.0, 37.0],
        16: [35.0, 34.0, 35.0],
        32: [47.0, 46.0, 48.0],
    }
    assert rank_count_from_measurements(measurements) == 16
    assert rank_count_from_measurements({8: [100, 102], 16: [99, 103]}) == 8


def test_tuning_ignores_failed_invalid_or_empty_trials():
    assert rank_count_from_measurements({
        1: [100.0, None], 4: [float("nan")], 8: [42.0, 44.0], 16: []
    }) == 8
    assert rank_count_from_measurements({1: [None], 2: []}) is None


def test_daily_output_requires_one_day_plus_model_step_margin(tmp_path):
    (tmp_path / "getm.inp").write_text(" timestep = 25\n", encoding="utf-8")
    (tmp_path / "output.yaml").write_text(
        "output:\n   time_unit: day\n   time_step: 1\n", encoding="utf-8")
    assert minimum_trial_duration(tmp_path) == 86460


def test_native_output_interval_extends_daily_trial_to_first_2d_and_3d_record(tmp_path):
    (tmp_path / "getm.inp").write_text(
        " timestep = 25\n save_2d = .true.\n step_2d = 8640\n"
        " save_3d = .true.\n step_3d = 8640\n", encoding="utf-8")
    (tmp_path / "output.yaml").write_text(
        "output:\n   time_unit: day\n   time_step: 1\n", encoding="utf-8")
    assert minimum_trial_duration(tmp_path) == 216060
