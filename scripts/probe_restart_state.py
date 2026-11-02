"""Compare checkpoint to a zero-step hot restart, without advancing integration."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime,timedelta
import netCDF4 as nc
import numpy as np
from verify_builtin_cases import ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--case',default='NativeTest')
    parser.add_argument('--unbuffered',action='store_true',help='Use the application Fortran logging environment')
    parser.add_argument('--advance-seconds',type=int,default=0)
    parser.add_argument('--solver',type=Path,default=ROOT/'3DWET/bin/getm_cartesian.exe')
    args=parser.parse_args();work=args.work.resolve();source=args.source.resolve()
    if work.exists():raise SystemExit('Use a fresh directory')
    work.mkdir(parents=True);case=work/'case'
    shutil.copytree(source/'3DWET/case'/args.case,case,ignore=shutil.ignore_patterns('output','*.log','restart.out','restart.in.previous'))
    shutil.copy2(source/'midpoint-restart.out',case/'restart.in')
    inp=case/'getm.inp';text=inp.read_text(encoding='utf-8-sig')
    start=re.search(r"(?m)^\s*start\s*=\s*'([^']+)'",text)[1]
    stop=(datetime.strptime(start,'%Y-%m-%d %H:%M:%S')+timedelta(seconds=args.advance_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    text=re.sub(r"(?m)^(\s*stop\s*=).*",lambda m:m[1]+repr(stop),text)
    inp.write_text(text,encoding='utf-8')
    env=os.environ.copy();env['PATH']=str(ROOT/'3DWET/bin/runtime')+os.pathsep+env['PATH']
    if args.unbuffered:
        env['GFORTRAN_UNBUFFERED_PRECONNECTED']='y'
        env['GFORTRAN_UNBUFFERED_ALL']='y'
    with (work/'native.log').open('w',encoding='utf-8') as log:
        result=subprocess.run([str(args.solver.resolve())],cwd=case,env=env,
                              stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL if args.unbuffered else log,
                              stderr=log if args.unbuffered else subprocess.STDOUT,timeout=120)
    reference=case/'restart.in'
    if args.advance_seconds:
        cold=work/'continuous'
        shutil.copytree(source/'3DWET/case/ContinuousReference',cold,ignore=shutil.ignore_patterns('output','*.log','restart.out'))
        cold_inp=cold/'getm.inp'
        cold_inp.write_text(re.sub(r"(?m)^(\s*stop\s*=).*",lambda m:m[1]+repr(stop),cold_inp.read_text(encoding='utf-8-sig')),encoding='utf-8')
        with (work/'continuous.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(args.solver.resolve())],cwd=cold,env=env,
                           stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL if args.unbuffered else log,
                           stderr=log if args.unbuffered else subprocess.STDOUT,timeout=120,check=True)
        reference=cold/'restart.out'
    report={'returncode':result.returncode,'advance_seconds':args.advance_seconds,'differences':{}}
    with nc.Dataset(reference) as before,nc.Dataset(case/'restart.out') as after:
        for name in before.variables:
            a=np.asarray(before[name][...]);b=np.asarray(after[name][...])
            error=float(np.max(np.abs(a-b)))
            if error:report['differences'][name]={'max_absolute_error':error,'index':list(map(int,np.unravel_index(np.argmax(np.abs(a-b)),a.shape))) if a.shape else []}
    (work/'probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
