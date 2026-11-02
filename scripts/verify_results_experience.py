"""Actual solver results, Chinese variable guides and reversible file management."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import netCDF4
import numpy as np
from openpyxl import Workbook
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

from verify_builtin_cases import (ROOT, prepare_model, wait_for_service, run_case,
                                  isolated_launcher_environment)
from verify_external_workflow import APIProbe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--model-source', type=Path, default=ROOT/'3DWET')
    parser.add_argument('--case', default='NativeTest',
                        help='Input case in model-source, including independently generated cases')
    parser.add_argument('--launcher', type=Path, default=ROOT/'3DWET/app/launcher.py')
    parser.add_argument('--hold', action='store_true')
    args = parser.parse_args()
    work = args.work.resolve()
    if work.exists():
        raise SystemExit('Use a fresh verification directory')
    prepare_model(work, [args.case], args.model_source, duration_seconds=1200, output_interval=600)
    case = work/'3DWET/case'/args.case
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in case.iterdir() if p.is_file()}
    report = {'passed':False, 'scope':'Short native integration; does not establish scientific accuracy.'}
    report['source_case'] = str((args.model_source/'case'/args.case).resolve())
    report['solver_sha256'] = hashlib.sha256((work/'3DWET/bin/getm_cartesian.exe').read_bytes()).hexdigest()
    stdout = (work/'service.log').open('w',encoding='utf-8')
    env,model_root,state_root = isolated_launcher_environment(work)
    process = subprocess.Popen(([sys.executable,str(args.launcher)] if args.launcher.suffix=='.py' else [str(args.launcher)]) +
        ['--web','--no-open','--port','0'],cwd=ROOT,env=env,stdout=stdout,stderr=subprocess.STDOUT)
    url = None
    try:
        url = wait_for_service(work,process,state_root=state_root,model_root=model_root)
        report['url'] = url
        probe = APIProbe(build_opener(ProxyHandler({})),url)
        report['native'] = run_case(probe.opener,url,case.name,case,300,verify_features=False)
        inventory = probe.call('/api/results/variables')
        items = list({v['name']:v for v in inventory.get('2d',[])+inventory.get('3d',[])}.values())
        assert items and all(v.get('zh_name') and v.get('meaning') and v.get('reference') for v in items)
        assert all(v.get('en_name') and v.get('meaning_en') and v['reference'].get('source_en') for v in items)
        report['english_metadata'] = 'passed'
        report['variables'] = items
        temp = next(v for v in items if v['name']=='temp')
        custom = probe.call('/api/results/reference',dict(name='temp',units=temp['units'],lower=12,upper=22))
        assert custom['variable']['reference']['kind']=='custom'
        reset = probe.call('/api/results/reference',dict(name='temp',units=temp['units'],reset=True))
        assert reset['variable']['reference']['kind']!='custom'
        field = probe.call('/api/results/2d?var=temp&time=0&level=0')
        assert field['zh_name']==temp['zh_name'] and field['data']
        averaged = probe.call('/api/results/2d?var=temp&time=0&aggregation=depth_mean')
        assert averaged['aggregation'] == 'depth_weighted_mean'
        assert averaged['weight_source'] == 'hn'
        with netCDF4.Dataset(case/'output/output.nc') as ds:
            values = np.asarray(np.ma.filled(ds['temp'][0], np.nan), dtype=np.float64)
            thickness = np.asarray(np.ma.filled(ds['hn'][0], np.nan), dtype=np.float64)
            valid = np.isfinite(values) & np.isfinite(thickness) & (thickness > 0)
            weights = np.where(valid, thickness, 0)
            denominator = weights.sum(axis=0)
            expected_mean = np.full(denominator.shape, np.nan)
            np.divide((np.where(valid, values, 0)*weights).sum(axis=0), denominator,
                      out=expected_mean, where=denominator > 0)
        actual_mean = np.asarray(averaged['data'], dtype=float)
        np.testing.assert_allclose(actual_mean[np.isfinite(actual_mean)],
                                   expected_mean[np.isfinite(actual_mean)], rtol=1e-12)
        report['depth_mean_actual_solver'] = {'passed': True, 'weight_source': averaged['weight_source']}
        j, i = np.argwhere(np.isfinite(actual_mean))[0]
        point = probe.call('/api/calibration/points', dict(name='XLSX verification',
                            i=int(i), j=int(j), variables=['temp']))['point']
        book = Workbook()
        book.active.append(['time', 'value', 'variable'])
        book.active.append(['2020-01-01 00:00:00', float(actual_mean[j, i]), 'temp'])
        xlsx = work/'observations.xlsx'
        book.save(xlsx)
        report['xlsx_upload'] = probe.call('/api/calibration/upload', files=[('file', xlsx)],
                                          form={'point_id': point['id'], 'variable': 'temp'})
        probe.call('/api/calibration/points?'+urlencode({'id':point['id']}), method='DELETE')
        volume = probe.call('/api/results/3d_surface?var=temp&target=16')
        assert volume['long_name']==temp['zh_name'] and volume['bottom']
        # A disposable metadata variant exercises actual external unit handling
        # through the frozen HTTP service. Restore it before the file checks.
        output_nc = case/'output/output.nc'
        with netCDF4.Dataset(output_nc,'r+') as ds:
            oxygen = ds['abiotic_water_sO2W']
            original_unit = oxygen.units
            oxygen.units = 'mgO2/L'
        try:
            custom = probe.call('/api/results/reference',dict(name='abiotic_water_sO2W',units='mgO2/L',value=7))
            assert custom['variable']['reference']['kind']=='custom'
            assert custom['variable']['reference']['value']==7
            probe.call('/api/results/reference',dict(name='abiotic_water_sO2W',units='g/m3',value=7),expected=400)
            probe.call('/api/results/reference',dict(name='abiotic_water_sO2W',units='mgO2/L',reset=True))
            report['external_unit_reference'] = 'passed'
        finally:
            with netCDF4.Dataset(output_nc,'r+') as ds:
                ds['abiotic_water_sO2W'].units = original_unit
        files = probe.call('/api/results/files')
        assert Path(files['case_path'])==case and files['files']
        # Duplicate only a tiny recognized log, never copy a multi-GB model field.
        output = case/'output'
        output.mkdir(exist_ok=True)
        (output/'visualize_run.log').write_text('verification duplicate\n',encoding='utf-8')
        archive = output/'archive_verification'
        archive.mkdir()
        shutil.copy2(output/'visualize_run.log',archive/'visualize_run.log')
        files = probe.call('/api/results/files')
        duplicates = probe.call('/api/results/files/duplicates',{'revision':files['revision']})
        assert duplicates['duplicate_paths']
        chosen = [p for p in duplicates['duplicate_paths'] if p.endswith('visualize_run.log')]
        assert len(chosen)==1
        cleaned = probe.call('/api/results/files/cleanup',dict(paths=chosen,revision=files['revision']))
        assert not (case/chosen[0]).exists()
        probe.call('/api/results/files/restore',{})
        assert (case/chosen[0]).exists()
        files = probe.call('/api/results/files')
        probe.call('/api/results/files/cleanup',dict(paths=chosen,revision=files['revision']))
        files = probe.call('/api/results/files')
        probe.call('/api/results/files/empty-trash',{'revision':files['trash']['revision']})
        assert probe.call('/api/results/files')['trash']['count']==0
        assert all(hashlib.sha256((case/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
        report['files'] = probe.call('/api/results/files')
        report['api_calls'] = probe.calls
        report['passed'] = True
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'passed':True,'variables':len(items),'url':url},ensure_ascii=False),flush=True)
        if args.hold:
            while not (work/'stop').exists():
                time.sleep(.5)
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        process.terminate()
        process.wait(timeout=30)
        stdout.close()


if __name__=='__main__':
    main()
