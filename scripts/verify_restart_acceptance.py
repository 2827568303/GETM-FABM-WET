"""Actual API cold/checkpoint/resume consistency; isolated NativeTest copies."""
import argparse
from datetime import datetime,timedelta
import json
import hashlib
import re
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.request import build_opener, ProxyHandler
import netCDF4 as nc
import numpy as np
from verify_builtin_cases import (ROOT, prepare_model, wait_for_service, run_case,
                                  isolated_launcher_environment)
from verify_external_workflow import APIProbe


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--model-source',type=Path,default=ROOT/'3DWET')
    parser.add_argument('--case',default='NativeTest')
    parser.add_argument('--checkpoint-seconds',type=int,default=600)
    parser.add_argument('--solver',type=Path,help='Isolated candidate executable; never replaces the shipped solver')
    parser.add_argument('--checkpoint-every-steps',type=int,default=0,help='Also exercise repeated native checkpoint writes')
    parser.add_argument('--timeout',type=float,default=120,help='Per native run limit; longer memory-window diagnostics may opt in')
    args=parser.parse_args();work=args.work.resolve()
    if work.exists():raise SystemExit('Use a fresh verification directory')
    prepare_model(work,[args.case],args.model_source,keep_defaults=True)
    if args.solver:shutil.copy2(args.solver,work/'3DWET/bin/getm_cartesian.exe')
    case=work/'3DWET/case'/args.case
    continuous=case.with_name('ContinuousReference');shutil.copytree(case,continuous)
    text=(case/'getm.inp').read_text(encoding='utf-8-sig')
    start=datetime.strptime(re.search(r"(?im)^\s*start\s*=\s*['\"]([^'\"]+)",text)[1],'%Y-%m-%d %H:%M:%S')
    stop=datetime.strptime(re.search(r"(?im)^\s*stop\s*=\s*['\"]([^'\"]+)",text)[1],'%Y-%m-%d %H:%M:%S')
    if not 0<args.checkpoint_seconds<(stop-start).total_seconds():
        raise ValueError('Checkpoint must be inside the actual case time window')
    midpoint=(start+timedelta(seconds=args.checkpoint_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    env,model_root,state_root=isolated_launcher_environment(work)
    log=(work/'service.log').open('w',encoding='utf-8')
    process=subprocess.Popen([sys.executable,str(ROOT/'3DWET/app/launcher.py'),'--web','--no-open','--port','0'],
                             cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    report={'passed':False,'checkpoint_seconds':args.checkpoint_seconds,'duration_seconds':(stop-start).total_seconds(),
            'scope':'Native continuous versus segmented restart over the source case time window; not a five-workflow round.'}
    report['solver_sha256']=hashlib.sha256((work/'3DWET/bin/getm_cartesian.exe').read_bytes()).hexdigest()
    report['source_case']=str((args.model_source/'case'/args.case).resolve())
    probe=None
    def periodic_checkpoint(path):
        if args.checkpoint_every_steps<=0:return
        inp=path/'getm.inp';text=inp.read_text(encoding='utf-8-sig')
        text=re.sub(r'(?m)^(\s*hotout\(1\)\s*=\s*)0\s*$',
                    lambda m:m[1]+str(args.checkpoint_every_steps)+'\n   hotout(2) = 2147483647\n   hotout(3) = '+str(args.checkpoint_every_steps),text)
        inp.write_text(text,encoding='utf-8')
    try:
        url=wait_for_service(work,process,120,state_root=state_root,model_root=model_root);probe=APIProbe(build_opener(ProxyHandler({})),url)
        probe.call('/api/case/load',{'case_name':continuous.name})
        probe.call('/api/config/hotstart',dict(enabled=False,save=True))
        periodic_checkpoint(continuous)
        report['continuous']=run_case(probe.opener,url,continuous.name,continuous,args.timeout,verify_features=False)
        with nc.Dataset(continuous/'restart.out') as checkpoint:
            report['temporal_memory']={}
            for name,var in checkpoint.variables.items():
                if not name.startswith('fabm_memory_') or not name.endswith('_history'):continue
                period=re.search(r'(\d+)_s_mean_',var.expression)
                assert period and float(var.period)==float(period[1]),'Physical-second memory period mismatch: '+name
                report['temporal_memory'][name]={'expression':var.expression,'period_seconds':float(var.period),
                                               'samples':int(var.n),'shape':list(var.shape)}
        probe.call('/api/case/load',{'case_name':case.name})
        time=probe.call('/api/config/time');time['stop']=midpoint
        probe.call('/api/config/time',time)
        probe.call('/api/config/hotstart',dict(enabled=False,save=True))
        periodic_checkpoint(case)
        report['first_half']=run_case(probe.opener,url,case.name,case,args.timeout,verify_features=False)
        checkpoint=case/'restart.out';assert checkpoint.is_file()
        shutil.copy2(checkpoint,work/'midpoint-restart.out')
        time['stop']=stop.strftime('%Y-%m-%d %H:%M:%S');probe.call('/api/config/time',time)
        report['resume_settings']=probe.call('/api/config/hotstart',dict(enabled=True,file='restart.out',save=True))
        assert report['resume_settings']['checkpoint']['time']==midpoint
        report['second_half']=run_case(probe.opener,url,case.name,case,args.timeout,verify_features=False)
        comparisons={}
        with nc.Dataset(continuous/'restart.out') as a,nc.Dataset(case/'restart.out') as b:
            for name in ['T','z','U','V','uu','vv','hn','fabm_pel','fabm_ben']:
                left=np.asarray(a[name][:]);right=np.asarray(b[name][:])
                assert np.isfinite(left).all() and np.isfinite(right).all(),name
                error=float(np.max(np.abs(left-right)))
                comparisons[name]={'shape':list(left.shape),'max_absolute_error':error,
                                   'passed':bool(np.allclose(left,right,rtol=1e-9,atol=1e-10))}
            for name in a.variables:
                if not (name.startswith('fabm_memory_') or name=='fabm_diagnostic_memory'):continue
                left=np.asarray(a[name][:]);right=np.asarray(b[name][:])
                assert np.isfinite(left).all() and np.isfinite(right).all(),name
                comparisons[name]={'shape':list(left.shape),'max_absolute_error':float(np.max(np.abs(left-right))),
                                   'passed':bool(np.allclose(left,right,rtol=1e-9,atol=1e-10))}
        report['comparisons']=comparisons
        assert all(v['passed'] for v in comparisons.values()),comparisons
        report['passed']=True
    except Exception as error:report['error']=f'{type(error).__name__}: {error}'
    finally:
        if probe:report['api_calls']=probe.calls
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=30)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        log.close()
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:report[k] for k in ['passed','error','comparisons'] if k in report},ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
