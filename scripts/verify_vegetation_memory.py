"""Controlled native restart with different vegetation onset dates by column."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
from urllib.request import build_opener,ProxyHandler
import netCDF4 as nc
import numpy as np
from verify_builtin_cases import ROOT,prepare_model,wait_for_service,run_case
from verify_external_workflow import APIProbe

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--model-source',type=Path,required=True)
    parser.add_argument('--solver',type=Path,required=True)
    args=parser.parse_args();work=args.work.resolve()
    if work.exists():raise SystemExit('Use a fresh directory')
    name='Imported Random Lake';prepare_model(work,[name],args.model_source,keep_defaults=True)
    import shutil
    shutil.copy2(args.solver,work/'3DWET/bin/getm_cartesian.exe')
    case=work/'3DWET/case'/name
    inp=case/'getm.inp';text=inp.read_text(encoding='utf-8-sig')
    for key,value in [('start',"'2020-05-01 00:00:00'"),('stop',"'2020-05-01 00:10:00'")]:
        text=re.sub(r'(?im)^(\s*'+key+r'\s*=\s*)[^\r\n!]+',lambda m:m[1]+value,text)
    inp.write_text(text,encoding='utf-8')
    for filename in ['meteo.nc','rivers.nc']:
        with nc.Dataset(case/filename,'a') as ds:ds['time'].units='seconds since 2020-05-01 00:00:00'
    env=dict(os.environ,WET_MODEL_ROOT=str(work/'3DWET'))
    log=(work/'service.log').open('w',encoding='utf-8')
    process=subprocess.Popen([sys.executable,str(ROOT/'3DWET/app/launcher.py'),'--web','--no-open','--port','0'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    report=dict(passed=False,scope='Controlled column-memory checkpoint data; not a full workflow or scientific field validation')
    try:
        url=wait_for_service(work,process,120);probe=APIProbe(build_opener(ProxyHandler({})),url)
        probe.call('/api/case/load',{'case_name':name})
        probe.call('/api/config/hotstart',dict(enabled=False,save=True))
        report['cold']=run_case(probe.opener,url,name,case,120,verify_features=False)
        assert report['cold']['passed'] and report['cold']['run']['status']=='completed'
        with nc.Dataset(case/'bathymetry.nc') as grid:wet=np.ma.filled(grid['bathymetry'][:]>0,False)
        values=np.where(np.indices(wet.shape)[1]%2==0,110.,120.)
        with nc.Dataset(case/'restart.out','a') as checkpoint:
            assert int(checkpoint['secondsofday'][...])==600
            assert checkpoint.fabm_memory_version==2
            var=checkpoint['fabm_diagnostic_memory']
            names=[var.getncattr(f'name_{i:04d}') for i in range(1,checkpoint.fabm_diagnostic_memory_count+1)]
            index=names.index('macrophytes_aDayInitVeg')
            data=np.asarray(var[:]);data[index]=np.broadcast_to(values,data[index].shape)
            data[index,:,~wet]=-1.;var[:]=data
            report['checkpoint_fields']=names
        shutil.copy2(case/'restart.out',work/'controlled-onset-checkpoint.out')
        settings=probe.call('/api/config/time');settings['stop']='2020-05-01 00:20:00'
        probe.call('/api/config/time',settings)
        report['resume_settings']=probe.call('/api/config/hotstart',dict(enabled=True,file='restart.out',save=True))
        report['warm']=run_case(probe.opener,url,name,case,120,verify_features=False)
        assert report['warm']['passed'] and report['warm']['run']['status']=='completed'
        with nc.Dataset(case/'restart.out') as checkpoint:
            from datetime import date
            assert int(checkpoint['julianday'][...])==date(2020,5,1).toordinal()+1721425
            report['final_seconds_of_day']=int(checkpoint['secondsofday'][...])
            assert report['final_seconds_of_day']==1200,'Checkpoint clock did not advance through the warm run'
            actual=np.asarray(checkpoint['fabm_diagnostic_memory'][index])
            expected=np.broadcast_to(values,actual.shape)
            error=float(np.max(np.abs(actual[:,wet]-expected[:,wet])))
            report['onset_max_error']=error
            assert error==0,'Vegetation onset dates were overwritten across columns or restart'
        legacy=next((case/'output').glob('*.3d.nc'))
        with nc.Dataset(legacy) as output:
            roots=np.ma.asarray(output['macrophytes_bfRootVeg_PV'][-1,1])
            means={str(date):float(np.ma.mean(roots[wet&(values==date)])) for date in [110.,120.]}
            report['root_fraction_by_onset']=means
            assert all(np.isfinite(list(means.values()))) and abs(means['110.0']-means['120.0'])>1e-5,means
        report['passed']=True
    except Exception as error:report['error']=f'{type(error).__name__}: {error}'
    finally:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=30)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        log.close();(work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({key:report[key] for key in ['passed','error','onset_max_error','root_fraction_by_onset'] if key in report},ensure_ascii=False))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
