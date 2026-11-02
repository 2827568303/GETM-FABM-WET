"""Repeat an isolated Lake Luoma pressure-gradient regression with a candidate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET/app'))
from solver_runtime import solver_environment, log_has_solver_failure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--repeat', type=int, default=20)
    args = parser.parse_args()
    exe = args.exe.resolve()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    env = solver_environment(ROOT / '3DWET/bin/getm_cartesian.exe')
    env.pop('HDF5_USE_FILE_LOCKING', None)
    records = []
    for index in range(args.repeat):
        case = work / f'run-{index:02}'
        case.mkdir()
        source = ROOT / 'build/root-cause-probe-20261010/run-0'
        for path in source.iterdir():
            if path.suffix in ('.inp', '.yaml', '.nml') or path.name in (
                    'bathymetry.nc', 'fabm_init.nc', 'meteo.nc', 'rivers.nc', 'riverinfo.dat', 'meteo_input.txt'):
                shutil.copy2(path, case / path.name)
        with (case / 'native.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([str(exe)], cwd=case, env=env, stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=subprocess.STDOUT, timeout=120)
        log = (case / 'native.log').read_text(encoding='utf-8', errors='replace')
        passed = result.returncode == 0 and not log_has_solver_failure(log)
        records.append({'repeat': index + 1, 'exit_code': result.returncode, 'passed': passed})
        print(records[-1], flush=True)
    report = {'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
              'hdf5_locking_override': False, 'runs': records,
              'passed': all(r['passed'] for r in records)}
    (work / 'verification.json').write_text(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
