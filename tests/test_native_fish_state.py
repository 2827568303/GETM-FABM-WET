"""Execute the real fish check_state with bounds checks and untouched sentinels."""
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def compile_probe(source, destination):
    model = ROOT / '3DWET'
    tool_bin = ROOT / 'build/native-toolchain/ucrt64/bin'
    if not tool_bin.exists():
        tool_bin = Path(r'C:\Users\23801\.codex\toolchains\msys64\ucrt64\bin')
    compiler = tool_bin / 'gfortran.exe'
    if not compiler.exists():
        pytest.skip('Portable native Fortran compiler is unavailable')
    destination.mkdir(parents=True, exist_ok=True)
    includes = [destination, model/'src/fabm/src/drivers/gotm',
                model/'src/fabm/include',model/'build-win/fabm/modules',
                model/'build/fabm/modules', model/'build/fabm/models/wet',
                model/'build-win/fabm/models/wet',model/'install-win/fabm/include']
    if not any((path/'wet_utility.mod').exists() for path in includes):
        pytest.skip('WET dependency module wet_utility.mod is unavailable; native fish probe cannot compile')
    env = dict(os.environ, PATH=str(tool_bin)+os.pathsep+os.environ['PATH'])
    flags = ['-O0','-g','-fcheck=all','-fbacktrace','-ffree-line-length-none',
             *(f'-I{p}' for p in includes)]
    obj = destination/'fish.F90.obj'
    subprocess.run([str(compiler),*flags,'-cpp','-c',str(source),'-o',str(obj)],
                   cwd=destination,env=env,check=True,capture_output=True)
    exe = destination/'fish_probe.exe'
    subprocess.run([str(compiler),*flags,str(ROOT/'tests/native_fish_state_probe.f90'),
                    str(obj),str(model/'install-win/fabm/lib/libfabm.a'),'-o',str(exe)],
                   cwd=destination,env=env,check=True,capture_output=True)
    return subprocess.run([str(exe)],cwd=destination,env=env,
                          capture_output=True,text=True,timeout=30)


def test_optional_fish_state_and_diagnostics_do_not_corrupt_other_variables(tmp_path):
    result = compile_probe(ROOT/'3DWET/src/wet/src/fish.F90',tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '32 combinations' in ' '.join(result.stdout.split())
