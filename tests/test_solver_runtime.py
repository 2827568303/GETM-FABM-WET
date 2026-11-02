import os
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from solver_runtime import solver_environment, inspect_runtime, explain_exit_code, log_has_solver_failure


def test_bundled_runtime_precedes_system_path(tmp_path):
    exe = tmp_path / 'getm_cartesian.exe'
    exe.write_bytes(b'not-an-exe')
    runtime = tmp_path / 'runtime'; runtime.mkdir()
    env = solver_environment(exe, {'PATH': 'system-path', 'OTHER': 'keep'})
    assert env['PATH'].split(os.pathsep)[0] == str(runtime)
    assert env['OTHER'] == 'keep'
    assert env['GFORTRAN_UNBUFFERED_ALL'] == 'y'


def test_missing_runtime_has_specific_diagnostic(tmp_path):
    exe = tmp_path / 'getm_cartesian.exe'; exe.write_bytes(b'x')
    r = inspect_runtime(exe)
    assert r['ready'] is False
    assert 'libgfortran-5.dll' in r['missing']
    assert 'libnetcdff-7.dll' in r['missing']
    assert 'DLL' in explain_exit_code(3221225781)


@pytest.mark.skipif(os.name != 'nt', reason='Windows PE loader probe needs the native DLL loader and getm_cartesian.exe')
def test_loader_probe_enters_model_without_case_writes():
    exe = Path(__file__).resolve().parents[1] / '3DWET/bin/getm_cartesian.exe'
    r = inspect_runtime(exe, probe=True)
    assert r['ready'], r
    assert r['loader_verified'], r


def test_success_log_with_disabled_nan_checks_is_not_failure():
    assert not log_has_solver_failure('sealevel_check=0 --> NaN checks disabled\ngetm: Completed on 20261008')


def test_real_numerical_and_fortran_errors_are_failures():
    for text in ('STOP 1', 'FATAL GETM ERROR', 'IEEE_INVALID_FLAG', 'NaN detected in water level',
                 'out-of-bound values encountered', 'value is NaN',
                 ' Error: state variable           25  is zero and has negative derivative!'):
        assert log_has_solver_failure(text), text


def test_solver_configuration_description_is_not_failure():
    text = 'out-of-bound values result in termination of program\ngetm: Completed on 20261009'
    assert not log_has_solver_failure(text)
