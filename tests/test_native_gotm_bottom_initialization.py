"""Compile the production GOTM initialization for the bottom flux buffer."""
import os
from pathlib import Path
import subprocess
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "3DWET/src/gotm/src/fabm/gotm_fabm.F90"
COMPILER = ROOT / "build/native-toolchain/ucrt64/bin/gfortran.exe"
TMP_ROOT = Path(r"D:\codex_tmp")


def test_startup_bottom_flux_buffer_is_zero_before_fabm_callback():
    source = SOURCE.read_bytes().decode("latin-1")
    routine = source.split("subroutine start_gotm_fabm(nlev, field_manager)", 1)[1]
    initialization = routine.split("#if 0", 1)[0].split("rhs = _ZERO_", 1)[1]
    initialization = "rhs = _ZERO_" + initialization
    statements = []
    for line in initialization.splitlines():
        code = line.split("!", 1)[0].strip()
        if code:
            statements.append(code.replace("_ZERO_", "0.0_rk"))
    assert "bottom_flux = 0.0_rk" in statements, (
        "start_gotm_fabm must initialize bottom_flux before calling fabm_do_bottom"
    )
    executable_source = "\n".join(statements)
    harness = f"""program probe
use, intrinsic :: ieee_arithmetic, only: ieee_is_finite, ieee_value, ieee_quiet_nan
implicit none
integer, parameter :: rk=8
real(rk) :: rhs(3),bottom_flux(4)
rhs=ieee_value(0.0_rk,ieee_quiet_nan)
bottom_flux=ieee_value(0.0_rk,ieee_quiet_nan)
{executable_source}
if (any(rhs/=0.0_rk)) stop 1
if (any(bottom_flux/=0.0_rk)) stop 2
call fabm_do_bottom(bottom_flux)
if (any(bottom_flux/=[1.0_rk,2.0_rk,3.0_rk,4.0_rk])) stop 3
print *, 'PASS startup bottom_flux initialized before callback'
contains
subroutine fabm_do_bottom(flux)
 real(rk), intent(inout) :: flux(:)
 if (any(.not.ieee_is_finite(flux))) stop 4
 if (any(flux/=0.0_rk)) stop 5
 flux=[1.0_rk,2.0_rk,3.0_rk,4.0_rk]
end subroutine
end program
"""
    if not COMPILER.is_file():
        pytest.skip("Portable Fortran compiler unavailable")
    if not TMP_ROOT.is_dir():
        pytest.skip(r"D:\codex_tmp is required for Fortran test artifacts")
    with tempfile.TemporaryDirectory(prefix="gotm_bottom_init_", dir=TMP_ROOT) as temp:
        directory = Path(temp)
        program = directory / "gotm_bottom_init_probe.f90"
        executable = directory / "gotm_bottom_init_probe.exe"
        program.write_text(harness, encoding="ascii")
        env = dict(os.environ, PATH=str(COMPILER.parent) + os.pathsep + os.environ.get("PATH", ""))
        built = subprocess.run(
            [str(COMPILER), "-ffree-line-length-none", "-fcheck=all", "-finit-real=snan",
             "-ffpe-trap=invalid,zero,overflow", str(program), "-o", str(executable)],
            cwd=directory, env=env, capture_output=True, text=True,
        )
        assert built.returncode == 0, built.stdout + built.stderr
        result = subprocess.run([str(executable)], cwd=directory, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
