"""Compile real WET burial branch statements for deterministic regression checks."""
import os
from pathlib import Path
import re
import subprocess
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "build/native-toolchain/ucrt64/bin/gfortran.exe"
TMP_ROOT = Path(r"D:\codex_tmp")
BURIAL = Path(os.environ.get("WET_BURIAL_SOURCE", ROOT / "3DWET/src/wet/src/burial.F90"))


def _branch_humus_assignments(source: str, start: str, end: str) -> str:
    body = source.split(start, 1)[1].split(end, 1)[0]
    statements = []
    for line in body.splitlines():
        code = line.split("!", 1)[0].strip()
        if re.match(r"t[dpnc]BurHum\s*=", code, re.IGNORECASE):
            statements.append(code)
    return "\n".join(statements)


def test_burial_humus_fluxes_are_defined_in_both_turnover_branches():
    source = BURIAL.read_bytes().decode("latin-1")
    bottom = source.split("subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)", 1)[1]
    positive = _branch_humus_assignments(
        bottom, "if (vDeltaS >= 0.0_rk) then", "else",
    )
    negative = _branch_humus_assignments(bottom, "else", "endif")

    positive_lhs = {line.split("=", 1)[0].strip().lower() for line in positive.splitlines()}
    negative_lhs = {line.split("=", 1)[0].strip().lower() for line in negative.splitlines()}
    expected = {"tdburhum", "tpburhum", "tnburhum", "tcburhum"}
    assert positive_lhs == expected, "positive turnover must explicitly define all four humus fluxes"
    assert negative_lhs == expected, "negative turnover must retain the four existing humus fluxes"

    if not COMPILER.is_file():
        pytest.skip("Portable Fortran compiler unavailable")
    if not TMP_ROOT.is_dir():
        pytest.skip(r"D:\codex_tmp is required for Fortran test artifacts")

    harness = f"""program probe
use, intrinsic :: ieee_arithmetic, only: ieee_value, ieee_quiet_nan, ieee_is_finite
implicit none
integer, parameter :: rk=8
real(rk) :: vDeltaS,tDBurOM,tDBurHum,tPBurHum,tNBurHum,tCBurHum
real(rk) :: tDBurPOM(2),pom_state_tendency,deep_humus_tendency
logical :: alias
integer :: branch,alias_case
do branch=1,2
 do alias_case=1,2
  alias=(alias_case==1)
  if (branch==1) then
   vDeltaS=1.0_rk
   tDBurOM=2.0_rk
   tDBurPOM=[0.65_rk,1.35_rk]
  else
   vDeltaS=-1.0_rk
   tDBurOM=-2.0_rk
   tDBurPOM=0.0_rk
  endif
  tDBurHum=ieee_value(0.0_rk,ieee_quiet_nan)
  tPBurHum=ieee_value(0.0_rk,ieee_quiet_nan)
  tNBurHum=ieee_value(0.0_rk,ieee_quiet_nan)
  tCBurHum=ieee_value(0.0_rk,ieee_quiet_nan)
  if (vDeltaS >= 0.0_rk) then
{positive}
  else
{negative}
  endif
  if (.not. all(ieee_is_finite([tDBurHum,tPBurHum,tNBurHum,tCBurHum]))) stop 9
  if (branch==1) then
   if (any([tDBurHum,tPBurHum,tNBurHum,tCBurHum] /= 0.0_rk)) stop 1
   pom_state_tendency=-tDBurPOM(2)
   deep_humus_tendency=tDBurHum
   if (alias) pom_state_tendency=pom_state_tendency+deep_humus_tendency
   if (abs(pom_state_tendency+1.35_rk)>1.0e-12_rk) stop 2
   if (alias .and. abs(deep_humus_tendency)>1.0e-12_rk) stop 3
   if (.not. alias .and. abs(deep_humus_tendency)>1.0e-12_rk) stop 4
  else
   if (abs(tDBurHum+2.0_rk)>1.0e-12_rk) stop 5
   if (abs(tPBurHum+0.002_rk)>1.0e-12_rk) stop 6
   if (abs(tNBurHum+0.02_rk)>1.0e-12_rk) stop 7
   if (abs(tCBurHum+1.0_rk)>1.0e-12_rk) stop 8
  endif
 enddo
enddo
print *, 'PASS burial humus flux branches and alias mappings'
end program
"""
    with tempfile.TemporaryDirectory(prefix="wet_burial_", dir=TMP_ROOT) as tmp:
        directory = Path(tmp)
        program = directory / "burial_probe.f90"
        executable = directory / "burial_probe.exe"
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
        assert "PASS burial humus flux branches and alias mappings" in result.stdout
