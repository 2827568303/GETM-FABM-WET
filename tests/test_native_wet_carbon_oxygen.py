"""Compile production-derived WET oxygen and benthic-carbon calculations."""
import os
from pathlib import Path
import subprocess
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "build/native-toolchain/ucrt64/bin/gfortran.exe"
TMP_ROOT = Path(r"D:\codex_tmp")
OM_POOL = ROOT / "3DWET/src/wet/src/om_pool.F90"
ZOOBENTHOS = ROOT / "3DWET/src/wet/src/zoobenthos.F90"


def _production_code_between(source: str, start: str, end: str) -> str:
    """Extract actual Fortran statements from a production source block."""
    body = start + source.split(start, 1)[1].split(end, 1)[0]
    statements = []
    for line in body.splitlines():
        code = line.split("!", 1)[0].strip()
        if code:
            statements.append(code)
    return "\n".join(statements)


def _compile_and_run(directory: Path, source: str) -> None:
    program = directory / "wet_carbon_oxygen_probe.f90"
    executable = directory / "wet_carbon_oxygen_probe.exe"
    program.write_text(source, encoding="ascii")
    env = dict(os.environ, PATH=str(COMPILER.parent) + os.pathsep + os.environ.get("PATH", ""))
    built = subprocess.run(
        [str(COMPILER), "-ffree-line-length-none", "-fcheck=all", "-finit-real=snan",
         "-ffpe-trap=invalid,zero,overflow", str(program), "-o", str(executable)],
        cwd=directory, env=env, capture_output=True, text=True,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    result = subprocess.run([str(executable)], cwd=directory, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def _temporary_directory():
    if not COMPILER.is_file():
        pytest.skip("Portable Fortran compiler unavailable")
    if not TMP_ROOT.is_dir():
        pytest.skip(r"D:\codex_tmp is required for Fortran test artifacts")
    return tempfile.TemporaryDirectory(prefix="wet_carbon_oxygen_", dir=TMP_ROOT)


def test_refractory_mineralization_uses_registered_oxic_sediment_fraction():
    source = OM_POOL.read_bytes().decode("latin-1")
    bottom = source.split("subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)", 1)[1]
    calculation = _production_code_between(bottom, "if (self%lRefrpool) then", "else")
    macro = "_GET_HORIZONTAL_(self%id_afOxySed,afOxySed)"
    assert macro in calculation, "lRefrpool must fetch its registered afOxySed dependency"
    calculation = calculation.replace(macro, "afOxySed=horizontal_values(self%id_afOxySed)")
    harness = f"""program probe
use, intrinsic :: ieee_arithmetic, only: ieee_value, ieee_quiet_nan
implicit none
integer, parameter :: rk=8
real(rk) :: horizontal_values(3),sDS,sNS,sPS,sCS,uFunTmMinS,afOxySed,tDMin,tNMin,tPMin,tCMin
integer :: sample
type type_model
 logical :: lRefrpool
 integer :: id_afOxySed
 real(rk) :: kDMinS,kNMinS,kPMinS
end type
type(type_model) :: self
self%lRefrpool=.true.
self%kDMinS=0.1_rk; self%kNMinS=0.2_rk; self%kPMinS=0.3_rk
sDS=4.0_rk; sNS=5.0_rk; sPS=6.0_rk; sCS=8.0_rk; uFunTmMinS=2.0_rk
horizontal_values=[0.0_rk,0.25_rk,0.9_rk]
do sample=2,3
 self%id_afOxySed=sample
 afOxySed=ieee_value(0.0_rk,ieee_quiet_nan)
 tDMin=0.0_rk; tNMin=0.0_rk; tPMin=0.0_rk; tCMin=0.0_rk
 {calculation}
 end if
 if (abs(afOxySed-horizontal_values(self%id_afOxySed))>1e-12_rk) stop 1
 if (abs(tDMin-self%kDMinS*uFunTmMinS*sDS*horizontal_values(self%id_afOxySed))>1e-12_rk) stop 2
 if (abs(tNMin-self%kNMinS*uFunTmMinS*sNS*horizontal_values(self%id_afOxySed))>1e-12_rk) stop 3
 if (abs(tPMin-self%kPMinS*uFunTmMinS*sPS*horizontal_values(self%id_afOxySed))>1e-12_rk) stop 4
 if (abs(tCMin-self%kDMinS*uFunTmMinS*sCS*horizontal_values(self%id_afOxySed))>1e-12_rk) stop 5
end do
print *, 'PASS lRefrpool horizontal oxygen coupling'
end program
"""
    with _temporary_directory() as directory:
        _compile_and_run(Path(directory), harness)


def test_benthic_carbon_particulate_and_dissolved_fluxes_conserve_total():
    source = ZOOBENTHOS.read_bytes().decode("latin-1")
    body = source.split("tCBentTOMS = tCEgesBent + tCMortBent", 1)[1]
    body = "tCBentTOMS = tCEgesBent + tCMortBent" + body.split("! 6.2.5 silica", 1)[0]
    lines = []
    for line in body.splitlines():
        code = line.split("!", 1)[0].strip()
        if code and any(name in code for name in ("tCBentTOMS =", "tCBentTPOMS =", "tCBentPOMS =", "tCBentDOMS =")):
            lines.append(code.replace("self%fBentDOMS", "fBentDOMS"))
    calculation = "\n".join(lines)
    assert "tCBentTPOMS = tCBentTOMS" in calculation
    assert "tCBentDOMS = tCBentTOMS" in calculation
    harness = f"""program probe
use, intrinsic :: ieee_arithmetic, only: ieee_value, ieee_quiet_nan
implicit none
integer, parameter :: rk=8
real(rk) :: tCEgesBent,tCMortBent,tCBentTOMS,tCBentTPOMS,tCBentPOMS,tCBentDOMS
real(rk) :: fractions(5),expected_total,fBentDOMS
integer :: i
fractions=[0.0_rk,0.1_rk,0.35_rk,0.9_rk,1.0_rk]
tCEgesBent=1.25_rk; tCMortBent=0.75_rk; expected_total=tCEgesBent+tCMortBent
do i=1,size(fractions)
 fBentDOMS=fractions(i)
 tCBentTPOMS=ieee_value(0.0_rk,ieee_quiet_nan)
 tCBentPOMS=ieee_value(0.0_rk,ieee_quiet_nan)
 tCBentDOMS=ieee_value(0.0_rk,ieee_quiet_nan)
 {calculation}
 if (abs(tCBentPOMS+tCBentDOMS-tCBentTOMS)>1e-12_rk) stop 1
 if (abs(tCBentTPOMS-tCBentPOMS)>1e-12_rk) stop 2
 if (abs(tCBentPOMS-expected_total*(1.0_rk-fractions(i)))>1e-12_rk) stop 3
 if (abs(tCBentDOMS-expected_total*fractions(i))>1e-12_rk) stop 4
end do
print *, 'PASS benthic carbon partition conservation'
end program
"""
    with _temporary_directory() as directory:
        _compile_and_run(Path(directory), harness)
