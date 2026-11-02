"""Surface/bottom contrast and Patankar log filtering."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from result_layers import surface_bottom_contrast
from solver_runtime import prepare_solver_log_chunk, recommended_openmp_threads, solver_environment


def test_surface_and_bottom_differ_when_the_column_is_stratified():
    bottom = np.array([[1.0, 2.0], [np.nan, 3.0]])
    surface = np.array([[5.0, 2.5], [np.nan, 9.0]])
    report = surface_bottom_contrast(bottom, surface, bottom_index=0, surface_index=9)
    assert report['n_wet'] == 3
    assert report['bottom_index'] == 0 and report['surface_index'] == 9
    assert report['surface_mean'] > report['bottom_mean']
    assert report['max_abs_diff'] == 6.0
    assert report['well_mixed'] is False


def test_well_mixed_shallow_column_is_reported_not_hidden():
    bottom = np.full((2, 2), 15.0)
    surface = np.full((2, 2), 15.001)
    report = surface_bottom_contrast(bottom, surface, bottom_index=1, surface_index=10)
    assert report['mean_abs_diff'] < 0.01
    assert report['well_mixed'] is True


def test_patankar_flood_keeps_progress_and_the_first_warnings():
    text = '12:00:00.000 n=         100\n' + ('Warning: small pi=1e-8 in Extended Modified Patankar slows down system!\n' * 50)
    filtered, dropped = prepare_solver_log_chunk(text)
    assert dropped == 50
    assert 'n=         100' in filtered
    assert filtered.count('small pi=') == 3
    assert '省略 Patankar' in filtered


def test_openmp_threads_leave_a_core_for_the_interface_and_mpi_stays_serial():
    assert recommended_openmp_threads(8) == 7
    assert recommended_openmp_threads(2) == 2
    env = solver_environment(Path('/tmp/getm_cartesian_parallel.exe'), {'PATH': '/usr/bin'})
    assert env['OMP_NUM_THREADS'] == '1'
