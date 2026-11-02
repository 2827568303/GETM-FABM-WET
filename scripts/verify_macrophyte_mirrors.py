"""Compare native cold initialization on the previously failing input dataset.

Diagnostic evidence only: reusing this dataset does not count as a full round.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

import netCDF4 as nc
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '3DWET/app'))
from solver_runtime import log_has_solver_failure, solver_environment


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    report = {'passed': False, 'scope': 'Same-input native diagnostic, not a full round', 'runs': {}}
    try:
        for label, exe in [('old', ROOT / '3DWET/bin/getm_cartesian.exe'),
                           ('candidate', args.candidate.resolve())]:
            folder = work / label
            folder.mkdir()
            for item in args.case.iterdir():
                if item.is_file() and item.name not in ('output.nc',) and item.suffix not in ('.log',) and not item.name.endswith(('.2d.nc', '.3d.nc')):
                    shutil.copy2(item, folder / item.name)
            inp = folder / 'getm.inp'
            inp.write_text(inp.read_text(encoding='utf-8-sig').replace('save_initial = .false.', 'save_initial = .true.'), encoding='utf-8')
            # Both programs use exactly the shipped runtime, not a compiler PATH.
            env = solver_environment(ROOT / '3DWET/bin/getm_cartesian.exe')
            started = time.monotonic()
            with (folder / 'native.log').open('w', encoding='utf-8') as stream:
                proc = subprocess.run([str(exe)], cwd=folder, env=env, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=120)
            log = (folder / 'native.log').read_text(encoding='utf-8', errors='replace')
            result = dict(elapsed_seconds=time.monotonic()-started, returncode=proc.returncode,
                          sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
                          negative_derivative_count=log.count('is zero and has negative derivative!'),
                          small_pi_zero_count=len(re.findall(r'small pi=\s*0\.0+(?:[DE][+-]?\d+)?\s', log, re.I)),
                          small_pi_warning_count=log.count('small pi='),
                          solver_failure=log_has_solver_failure(log),
                          completed='getm: Completed on' in log)
            with nc.Dataset(folder / 'output.nc') as ds:
                states = {}
                for pool, suffix in [('macrophytes',''), ('zoobenthos',''), ('bivalves',''),
                                     ('POM','S'), ('DOM','S'), ('humus','S'),
                                     ('cyanobacteria','S'), ('diatoms','S'), ('greens','S')]:
                    for element in 'DNPC':
                        name = pool + '_s' + element + suffix
                        if name not in ds.variables or name + '_PV' not in ds.variables:
                            continue
                        bottom = np.ma.asarray(ds[name][:])
                        pelagic = np.ma.asarray(ds[name + '_PV'][:, 0])
                        states[pool + '_' + element] = dict(initial_mirror_error=float(np.ma.max(np.ma.abs(bottom[0]-pelagic[0]))),
                                              benthic_change=float(np.ma.max(np.ma.abs(bottom[-1]-bottom[0]))),
                                              finite=bool(np.isfinite(bottom.compressed()).all() and np.isfinite(pelagic.compressed()).all()))
                result['states'] = states
                result['records'] = len(ds['time'])
                result['initial_time'] = float(ds['time'][0])
            report['runs'][label] = result
        old = report['runs']['old']; new = report['runs']['candidate']
        assert old['negative_derivative_count'] > 0 and old['solver_failure'], old
        assert new['returncode'] == 0 and new['completed'] and not new['solver_failure'], new
        assert new['negative_derivative_count'] == 0, new
        assert new['small_pi_warning_count'] == 0, new
        assert all(s['finite'] and s['initial_mirror_error'] == 0 for s in new['states'].values()), new
        assert new['states']['macrophytes_D']['benthic_change'] > 0, new
        assert new['states']['DOM_C']['benthic_change'] > 0, new
        report['passed'] = True
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
    (work / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
