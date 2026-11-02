"""Configure the serial GETM NetCDF restart protocol used by this build."""
import json
import os
from pathlib import Path
import shutil
import re
from datetime import datetime, timedelta

import netCDF4 as nc
import numpy as np
import yaml


def _temporal_memory_info(case, dataset, grid_shape):
    """Check memory before staging; native code also validates expression identity."""
    path=case/'fabm.yaml'
    document=yaml.safe_load(path.read_text(encoding='utf-8-sig')) if path.exists() else {}
    instances=(document or {}).get('instances',{})
    known_memory=any(isinstance(item,dict) and item.get('model') in
                     {'wet/phytoplankton','wet/macrophytes'} for item in instances.values())
    message='光照时间均值历史缺失或不兼容，请重新冷启动生成检查点 / Missing or incompatible temporal history; create a new cold-run checkpoint'
    if 'fabm_memory_version' not in dataset.ncattrs():
        if known_memory:raise ValueError(message)
        return {}
    try:
        version=dataset.fabm_memory_version
        count=dataset.fabm_memory_count
        if version!=2 or count!=int(count) or not 0<=count<=10000 or (known_memory and count==0):
            raise ValueError(message)
        if dataset.fabm_memory_timebase!='GETM Julian-day seconds':raise ValueError(message)
        nx,ny,nz=grid_shape
        for index in range(1,int(count)+1):
            prefix=f'fabm_memory_{index:04d}'
            history=dataset[prefix+'_history']
            n=history.n;kind=history.kind
            if n!=int(n) or n<1 or kind not in (1,2) or not str(history.expression):raise ValueError(message)
            if not np.isfinite(history.period) or history.period<=0 or not np.isfinite(history.expression_missing_value):raise ValueError(message)
            if history.shape!=(int(n)+3,nz-1 if kind==1 else 1,ny,nx):raise ValueError(message)
            for suffix in ('history','last','next','oldest','valid'):
                var=dataset[prefix+'_'+suffix]
                if suffix!='history' and var.shape!=(ny,nx):raise ValueError(message)
                values=np.ma.asarray(var[:])
                if np.ma.getmaskarray(values).any() or not np.isfinite(np.asarray(values)).all():raise ValueError(message)
            oldest=np.asarray(dataset[prefix+'_oldest'][:])
            valid=np.asarray(dataset[prefix+'_valid'][:])
            if not np.all((oldest==-1)|((oldest>=1)&(oldest<=n)&(oldest==np.floor(oldest)))):raise ValueError(message)
            if not np.all((valid==0)|(valid==1)):raise ValueError(message)
            last=np.asarray(dataset[prefix+'_last'][:]);future=np.asarray(dataset[prefix+'_next'][:])
            if np.any((oldest>0)&(future<=last)):raise ValueError(message)
        diagnostic_count=dataset.fabm_diagnostic_memory_count
        if diagnostic_count!=int(diagnostic_count) or not 0<=diagnostic_count<=10000:raise ValueError(message)
        known_onset=any(isinstance(item,dict) and item.get('model')=='wet/macrophytes' for item in instances.values())
        if known_onset and diagnostic_count==0:raise ValueError(message)
        if diagnostic_count:
            data=dataset['fabm_diagnostic_memory']
            values=np.ma.asarray(data[:])
            if data.shape!=(int(diagnostic_count),nz-1,ny,nx) or np.ma.getmaskarray(values).any() or not np.isfinite(np.asarray(values)).all():raise ValueError(message)
            names=[data.getncattr(f'name_{i:04d}') for i in range(1,int(diagnostic_count)+1)]
            if len(set(names))!=diagnostic_count or not all(names):raise ValueError(message)
        return {'temporal_memory_count':int(count),'temporal_memory_version':int(version),
                'diagnostic_memory_count':int(diagnostic_count)}
    except (AttributeError,KeyError,TypeError,OverflowError,IndexError) as exc:
        raise ValueError(message) from exc


def restart_settings(case, config):
    case=Path(case)
    sidecar=case/'.studio-hotstart.json'
    try:
        selected=json.loads(sidecar.read_text(encoding='utf-8')).get('file','')
    except (OSError,ValueError,AttributeError):
        selected=''
    io=config.get('io_spec',{})
    return dict(enabled=bool(config.get('param',{}).get('hotstart',False)),
                file=selected or config.get('param',{}).get('hotstart_file',''),
                save=int(io.get('hotout(1)',-1))>=0,
                native_input=str(Path(str(io.get('out_dir','.')))/'restart.in'),
                native_output=str(Path(str(io.get('out_dir','.')))/'restart.out'))


def prepare_restart(case, config, *, enabled, filename='', save=True):
    """Validate before any mutation; stage restart.in and return its timestamp.

    Restart input is restricted to the active case so another project cannot be
    overwritten by a typo. GETM ignores a user-selected filename: it always reads
    out_dir/restart.in in serial mode. The Studio selection belongs in a sidecar.
    """
    case=Path(case).resolve()
    if not isinstance(enabled,bool) or not isinstance(save,bool):
        raise ValueError('启动和保存检查点选项必须是布尔值')
    if config.get('param',{}).get('parallel',False):
        raise ValueError('当前界面仅支持串行重启文件 / Serial restart only')
    io=config.get('io_spec',{})
    directory=(case/str(io.get('out_dir','.'))).resolve()
    if not directory.is_relative_to(case):
        raise ValueError('重启目录必须位于当前案例内 / Restart directory outside case')
    info={}
    source=None
    sidecar=case/'.studio-hotstart.json'
    try:
        saved=json.loads(sidecar.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        saved={}
    fabm_path=case/'getm_fabm.inp'
    fabm_text=fabm_path.read_text(encoding='utf-8') if fabm_path.exists() else None
    method_match=re.search(r'(?im)^\s*fabm_init_method\s*=\s*(\d+)',fabm_text or '')
    cold_method=saved.get('cold_fabm_init_method',int(method_match[1]) if method_match else 1)
    if enabled:
        if not isinstance(filename,str) or not filename.strip():
            raise ValueError('请选择有效重启文件 / Select a restart file')
        source=(case/filename).resolve()
        if not source.is_relative_to(case) or not source.is_file():
            raise ValueError('重启文件不存在或不在当前案例内 / Invalid restart path')
        try:
            with nc.Dataset(source) as ds, nc.Dataset(case/str(config.get('domain',{}).get('bathymetry','bathymetry.nc'))) as grid:
                required={'julianday','secondsofday','timestep','loop','xax','yax','zax','z','U','V'}
                if not required.issubset(ds.variables):
                    raise ValueError('不是 GETM 重启文件 / Not a GETM checkpoint')
                if fabm_text is not None and 'fabm_pel' not in ds.variables:
                    raise ValueError('缺少 FABM 生态重启状态 / Missing FABM restart state')
                bathy=grid['bathymetry']
                expected=(bathy.shape[-1],bathy.shape[-2],int(config.get('domain',{}).get('kdum',10))+1)
                actual=tuple(len(ds.dimensions[k]) for k in ('xax','yax','zax'))
                if actual!=expected:
                    raise ValueError('重启文件的网格或层数不匹配 / Restart grid mismatch')
                memory_info=_temporal_memory_info(case,ds,expected) if fabm_text is not None else {}
                for axis,key in [('xax',bathy.dimensions[-1]),('yax',bathy.dimensions[-2])]:
                    if key in grid.variables and not np.allclose(ds[axis][:],grid[key][:],rtol=1e-10,atol=1e-8):
                        raise ValueError('重启文件的网格坐标不匹配 / Restart grid coordinates mismatch')
                if int(config.get('param',{}).get('runtype',4))>=2 and 'T' not in ds.variables:
                    raise ValueError('缺少三维重启状态 / Missing 3D restart state')
                jd=int(ds['julianday'][...]);seconds=int(ds['secondsofday'][...])
                if not 0<=seconds<86400:
                    raise ValueError('重启时间无效 / Invalid restart time')
                # GETM julian_day.F90 uses the integer civil Julian day number.
                timestamp=datetime.fromordinal(jd-1721425)+timedelta(seconds=seconds)
                stop=datetime.strptime(config['time']['stop'],'%Y-%m-%d %H:%M:%S')
                if timestamp>=stop:
                    raise ValueError('运行结束时间必须晚于检查点 / stop must follow checkpoint')
                info={'time':timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                      'timestep':float(ds['timestep'][...]),'file':str(source.relative_to(case))}
                info.update(memory_info)
        except (OSError,KeyError,OverflowError) as exc:
            raise ValueError(f'重启文件读取失败 / Cannot read checkpoint: {exc}') from exc
    if source is not None:
        directory.mkdir(parents=True,exist_ok=True)
        destination=directory/'restart.in'
        if source!=destination:
            staging=directory/'.studio-restart.tmp'
            shutil.copy2(source,staging)
            if destination.exists():
                # Keep the previous input available for recovery.
                shutil.copy2(destination,directory/'restart.in.previous')
            os.replace(staging,destination)
    config.setdefault('param',{}).pop('hotstart_file',None)
    config['param']['hotstart']=enabled
    config.setdefault('io_spec',{}).update(hotin_fmt=2,hotout_fmt=2)
    # Indexed namelist assignment is accepted natively and avoids quoted arrays.
    config['io_spec'].pop('hotout',None)
    config['io_spec']['hotout(1)']=0 if save else -1
    if fabm_text is not None:
        # GETM otherwise overwrites checkpoint ecology with fabm.yaml defaults.
        method=0 if enabled else (cold_method or 1)
        if method_match:
            fabm_text=re.sub(r'(?im)^(\s*fabm_init_method\s*=\s*)\d+',lambda m:m[1]+str(method),fabm_text)
        else:
            fabm_text=fabm_text.replace('&getm_fabm_nml',f'&getm_fabm_nml\n fabm_init_method = {method},')
        fabm_path.write_text(fabm_text,encoding='utf-8')
    if enabled:
        config.setdefault('time',{})['start']=info['time']
        config['param']['use_epoch']=False
    sidecar.write_text(json.dumps({'file':filename,'cold_fabm_init_method':cold_method},ensure_ascii=False),encoding='utf-8')
    return info
