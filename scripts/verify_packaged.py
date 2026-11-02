"""Exercise a frozen app and native coupled solver in a disposable model copy."""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler

import netCDF4
import numpy as np
from verify_builtin_cases import prepare_model, wait_for_service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('program', type=Path)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--case', default='StudioDemo')
    args = parser.parse_args()
    program = args.program.resolve()
    work = args.work.resolve()
    if work.exists():
        raise SystemExit('Use a fresh --work directory; existing data will never be removed.')
    work.mkdir(parents=True)
    model = work / '3DWET'
    # Copy only canonical inputs. Installed model trees contain service leases,
    # user selections and old results, which must not enter an isolated test.
    prepare_model(work, [args.case], program.parent / '3DWET', 1200, 2, 60, True)
    case_root = work / 'case-storage'
    state_root = work / 'case-state'
    env = dict(os.environ, WET_MODEL_ROOT=str(model),
               WET_CASE_DIR=str(case_root), WET_CASE_STATE_DIR=str(state_root),
               PATH=str(Path(os.environ['SystemRoot']) / 'System32'),
               PYTHONHOME=str(work / 'no-system-python'))
    report = {'program': str(program), 'model_root': str(model), 'standalone_environment': True}
    process = subprocess.Popen([str(program), '--web', '--no-open', '--port', '0'], env=env)
    opener = build_opener(ProxyHandler({}))
    url = None
    try:
        url = wait_for_service(work, process, state_root=state_root, model_root=model)

        def api(path, data=None):
            request = Request(url + path, data=json.dumps(data).encode() if data is not None else None,
                              headers={'Content-Type': 'application/json'})
            with opener.open(request, timeout=30) as response:
                return json.load(response)

        report['health'] = api('/api/system/health')
        assert Path(report['health']['model_root']).resolve() == model
        with opener.open(url) as response:
            assert 'class="studio-hero"' not in response.read().decode()
        assert api('/api/case/load', {'case_name': args.case})['success']
        report['case'] = args.case
        report['ecology_modules'] = len(api('/api/ecology/network')['nodes'])
        geometry = api('/api/geo/grid')
        assert geometry['nx'] > 0 and geometry['ny'] > 0
        report['preflight'] = api('/api/run/check')
        assert report['preflight']['ok'], report['preflight']
        assert api('/api/run/start', {})['success']
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            status = api('/api/run/status')
            if status['status'] != 'running':
                break
            time.sleep(.2)
        report['run'] = status
        assert status['status'] == 'completed', status
        report['outputs'] = {}
        for path in (model / 'case' / args.case).rglob('*.nc'):
            if path.name not in ('output.nc', 'THEORETICAL_LAKE.2d.nc', 'THEORETICAL_LAKE.3d.nc'):
                continue
            with netCDF4.Dataset(path) as dataset:
                assert len(dataset.dimensions['time']) > 0
                bad = []
                for name, variable in dataset.variables.items():
                    if np.issubdtype(variable.dtype, np.number):
                        values = np.ma.asarray(variable[:]).compressed()
                        if values.size and not np.isfinite(values).all():
                            bad.append(name)
                assert not bad, (path, bad)
                report['outputs'][path.name] = {'time_records': len(dataset.dimensions['time']),
                                              'variables': len(dataset.variables), 'nonfinite': bad}
        assert 'output.nc' in report['outputs']
        volume = api('/api/results/3d_surface?var=temp')
        assert volume['bottom'] and len(volume['xc']) == volume['shape'][2]
        assert volume['min'] is not None and np.isfinite(volume['min'])
        report['render_geometry'] = {'shape': volume['shape'], 'has_bathymetry': True, 'has_coordinates': True}
        dashboard = api('/api/dashboard/summary')
        assert {'temp', 'u', 'v'} <= set(dashboard), dashboard.keys()
        assert ('z' in dashboard or 'elev' in dashboard), dashboard.keys()
        assert 'abiotic_water_sO2W' in dashboard, dashboard.keys()
        report['dashboard_key_fields'] = sorted(set(dashboard) & {
            'temp', 'z', 'elev', 'u', 'v', 'abiotic_water_sO2W',
            'abiotic_water_sNO3W', 'abiotic_water_sNH4W', 'abiotic_water_sPO4W',
            'wet_chla', 'wet_chla_calculator_result'})
        report['passed'] = True
    except Exception as error:
        report.update(passed=False, error=str(error))
        raise
    finally:
        # This private service cannot serve another user; finish any run before stopping it.
        if url and process.poll() is None:
            try:
                with opener.open(Request(url + '/api/run/stop', data=b'{}',
                                 headers={'Content-Type': 'application/json'}), timeout=15):
                    pass
            except Exception:
                pass
        process.terminate()
        process.wait(timeout=20)
        (work / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k != 'run'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
