"""Compare model computation and duplicate output cost on untouched case copies."""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
import netCDF4
import numpy as np
from output_paths import output_path, require_outside_c

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'3DWET/app'))
from solver_runtime import solver_environment,log_has_solver_failure


def main():
    work=output_path('build','performance-benchmark-v2')
    work.mkdir(exist_ok=False)
    source=require_outside_c(output_path('cases','Theoretical lake'), 'Source case path')
    exe=ROOT/'3DWET/bin/getm_cartesian.exe'
    sources=['temp','z','D','hn','abiotic_water_sO2W','abiotic_water_sNO3W',
             'abiotic_water_sNH4W','abiotic_water_sPO4W','cyanobacteria_sDW',
             'diatoms_sDW','greens_sDW','inorganic_carbon_sDICW','methane_sCH4W']
    report=[]
    for name,dt,focused in [('full-output',2,False),('focused-output',2,True),('larger-step-comparison',10,True)]:
        case=work/name;case.mkdir()
        for path in source.iterdir():
            if path.is_file() and (path.suffix.lower() in ('.inp','.yaml','.nml') or path.name in
                                  {'bathymetry.nc','fabm_init.nc','meteo.nc','meteo_input.txt','riverinfo.dat','rivers.nc'}):
                shutil.copy2(path,case/path.name)
        path=case/'getm.inp';text=path.read_text(encoding='utf-8')
        for key,value in [('timestep',str(dt)),('stop',"'2020-01-01 00:20:00'"),
                          ('step_2d',str(int(600/dt))),('step_3d',str(int(600/dt))),
                          ('sync_2d','1'),('sync_3d','1'),('check_cfl','.true.'),
                          ('save_3d','.false.' if focused else '.true.')]:
            text=re.sub(r'(?m)^(\s*'+key+r'\s*=\s*)[^\r\n!]+',lambda m:m[1]+value,text)
        path.write_text(text,encoding='utf-8')
        (case/'output.yaml').write_text('output:\n   time_unit: second\n   time_step: 600\n   sync_interval: 1\n   variables:\n'+
                                      ''.join('      - source: '+s+'\n' for s in sources if focused)+
                                      ('' if focused else '      - source: *\n'),encoding='utf-8')
        begin=time.perf_counter()
        with (case/'model_run.log').open('wb') as log:
            process=subprocess.run([str(exe)],cwd=case,env=solver_environment(exe),stdout=subprocess.DEVNULL,
                                   stderr=log,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        elapsed=time.perf_counter()-begin
        log=(case/'model_run.log').read_text(encoding='utf-8',errors='replace')
        item=dict(name=name,timestep=dt,seconds=elapsed,exit_code=process.returncode,
                  output_bytes=sum(p.stat().st_size for p in case.glob('*.nc') if p.name.startswith(('output','THEORETICAL'))),
                  native_timers=[line.strip() for line in log.splitlines() if re.match(r'\s*(getm_fabm|output_manager_save|TIMERS SUM)\s',line)])
        item['passed']=process.returncode==0 and not log_has_solver_failure(log)
        if item['passed']:
            with netCDF4.Dataset(case/'output.nc') as ds:
                item['variables']=len(ds.variables)
                item['records']=len(ds.dimensions['time'])
                item['nonfinite']=[k for k,v in ds.variables.items() if np.issubdtype(v.dtype,np.number) and
                                   not np.isfinite(np.ma.asarray(v[:]).compressed()).all()]
                item['passed']=not item['nonfinite'] and item['records']>0
        report.append(item)
        print(json.dumps(item,ensure_ascii=False),flush=True)
    (work/'benchmark.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
