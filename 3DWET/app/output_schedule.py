"""Last scheduled output time for the GETM/Flexout settings in a trial case."""
from datetime import datetime, timedelta
import math
from pathlib import Path
import re
import yaml


def last_output_time(case_path, filename, namelist, model_stop):
    def scalar(key):
        match=re.search(r'(?im)^\s*'+key+r'\s*=\s*([^!\r\n]+)',namelist)
        return match[1].strip().strip(',').strip("'\"") if match else None
    def date(value):
        if isinstance(value,datetime):return value
        return datetime.strptime(str(value),'%Y-%m-%d %H:%M:%S')
    def number(value):return float(str(value).replace('D','e').replace('d','e'))
    start_value=scalar('start')
    if not start_value:return model_stop
    model_start=date(start_value)
    timestep=number(scalar('timestep') or 0)
    duration=(model_stop-model_start).total_seconds()
    if duration<0:raise ValueError('模型结束时间早于开始时间')
    # GETM timefmt=2 uses Fortran NINT, not floor/ceil, for its final step.
    native_last=math.floor(duration/timestep+0.5) if timestep>0 else None
    if timestep>0 and scalar('timefmt') in ('1','3') and scalar('nlast') is not None:
        native_last=int(number(scalar('nlast')))
    def at_step(n,flexout=True):
        seconds=n*timestep
        if not flexout:return model_start+timedelta(seconds=seconds)
        whole=math.floor(seconds)
        # update_time truncates seconds then NINT-rounds the fractional part;
        # timedelta(float seconds) instead uses ties-to-even at half a microsecond.
        start_seconds=model_start.hour*3600+model_start.minute*60+model_start.second
        microseconds=math.floor(((seconds+start_seconds)-(whole+start_seconds))*1000000+0.5)
        # GETM currently clamps this fraction after assigning secondsofday.
        # Match the actual clock it passes to Flexout, including that ordering.
        if microseconds>=999990:microseconds=0
        return model_start+timedelta(seconds=whole,microseconds=microseconds)
    def on_step(stamp):
        if timestep<=0:return stamp
        n=math.ceil((stamp-model_start).total_seconds()/timestep-1e-10)
        return at_step(n)
    if filename.endswith(('.2d.nc','.3d.nc')):
        step=scalar('step_3d' if filename.endswith('.3d.nc') else 'step_2d')
        if step is None or timestep<=0:return model_stop
        step=number(step)
        if not math.isfinite(step) or step<=0 or step!=int(step):raise ValueError('输出步数必须为正整数')
        last_step=(native_last//int(step))*int(step)
        first=int(number(scalar('first_3d' if filename.endswith('.3d.nc') else 'first_2d') or 1))
        if last_step<first:raise ValueError('输出窗口内没有计划输出')
        return at_step(last_step,flexout=False)
    else:
        path=Path(case_path)/'output.yaml'
        if not path.is_file():return model_stop
        # Flexout treats source: * as a literal wildcard; standard YAML treats
        # it as an alias. Quote only that scalar before reading the configuration.
        text=re.sub(r'(?m)(\bsource:\s*)\*(\s*(?:#.*)?)$',r"\1'*'\2",path.read_text(encoding='utf-8-sig'))
        groups=yaml.safe_load(text) or {}
        settings=groups.get(Path(filename).stem,{})
        if not isinstance(settings,dict):raise ValueError('输出设置必须为对象')
        unit=str(settings.get('time_unit','day')).lower()
        step=number(settings.get('time_step',1))
        anchor=date(settings['time_start']) if settings.get('time_start') else model_start
        # Flexout defaults last_julian to huge(1); GETM's requested stop is not
        # an implicit file window. NINT may integrate its last step past it.
        explicit_stop=date(settings['time_stop']) if settings.get('time_stop') else None
        stop=explicit_stop or (at_step(native_last) if timestep>0 else model_stop)
        factors={'second':1,'seconds':1,'minute':60,'minutes':60,'hour':3600,'hours':3600,'day':86400,'days':86400,'dt':timestep}
        cadence=step*factors[unit] if unit in factors else None
    if stop<max(anchor,model_start):raise ValueError('输出窗口内没有模型时间步')
    limit=stop
    if timestep>0:
        # Flexout compares integer secondsofday, excluding microseconds. A step
        # at stop+.785733 is in the stop-second; stop+1 is outside the window.
        window_last=math.ceil(((explicit_stop-model_start).total_seconds()+1)/timestep-1e-10)-1 if explicit_stop else native_last
        eligible_last=min(native_last,window_last)
        limit=at_step(eligible_last)
    if unit in ('month','year'):
        if step<1 or step!=int(step):raise ValueError('日历输出周期必须为正整数')
        current=anchor;last=None
        while current<=limit:
            actual=on_step(current)
            if current>=model_start and actual<=limit:last=actual
            months=current.year*12+current.month-1+int(step)*(12 if unit=='year' else 1)
            current=datetime(months//12,months%12+1,1,current.hour,current.minute,current.second)+timedelta(days=current.day-1)
        if last is None:raise ValueError('输出窗口内没有计划输出')
        return last
    if cadence is None:raise ValueError(f'不支持的输出周期单位: {unit}')
    if not math.isfinite(cadence) or cadence<=0:raise ValueError('输出周期必须大于零')
    if unit=='dt' and timestep>0:
        if step!=int(step):raise ValueError('输出步数必须为正整数')
        # type_file.first_index defaults to 0. save_initial controls whether
        # n=0 is emitted, not the cadence of later dt records.
        first=max(0 if (scalar('save_initial') or '.false.').lower()=='.true.' else 1,
                  math.ceil((anchor-model_start).total_seconds()/timestep-1e-10))
        last=(eligible_last//int(step))*int(step)
        if last<first:raise ValueError('输出窗口内没有计划输出')
        return at_step(last)
    count=math.floor((limit-anchor).total_seconds()/cadence+1e-10)
    scheduled=anchor+timedelta(seconds=count*cadence)
    # Flexout saves on the first eligible model step reaching the schedule.
    actual=on_step(scheduled)
    if actual>limit:
        actual=on_step(scheduled-timedelta(seconds=cadence))
    if actual<max(anchor,model_start):raise ValueError('输出窗口内没有计划输出')
    return actual
