from datetime import datetime
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'3DWET/app'))
from output_schedule import last_output_time


@pytest.mark.parametrize('unit,step,start,stop,expected',[
    ('month',1,'2020-01-01 00:00:00','2020-03-15 00:00:00','2020-03-01 00:00:00'),
    ('year',1,'2020-01-01 00:00:00','2022-06-15 00:00:00','2022-01-01 00:00:00'),
    ('second',7,'2020-01-01 00:00:00','2020-01-01 00:00:22','2020-01-01 00:00:22'),
    ('dt',7,'2020-01-01 00:00:00','2020-01-01 00:20:00','2020-01-01 00:19:50'),
])
def test_schedules_calendar_and_model_step_rounding(tmp_path,unit,step,start,stop,expected):
    (tmp_path/'output.yaml').write_text(f'output:\n time_unit: {unit}\n time_step: {step}\n variables:\n  - source: *\n')
    text=f" start = '{start}'\n stop = '{stop}'\n timestep = 2.\n save_initial = .true.\n"
    result=last_output_time(tmp_path,'output.nc',text,datetime.fromisoformat(stop))
    assert result==datetime.fromisoformat(expected)


@pytest.mark.parametrize('settings',[
    'time_unit: second\n time_step: 0',
    'time_unit: unknown\n time_step: 1',
    'time_unit: month\n time_step: 1.5',
    'time_unit: second\n time_start: 2020-01-02 00:00:00',
])
def test_invalid_output_schedule_cannot_pass_integrity(tmp_path,settings):
    (tmp_path/'output.yaml').write_text('output:\n '+settings+'\n')
    with pytest.raises(ValueError):
        last_output_time(tmp_path,'output.nc',"start = '2020-01-01 00:00:00'\ntimestep = 2.\n",datetime(2020,1,1,0,20))


def test_fractional_native_final_step_can_save_the_last_flexout_schedule(tmp_path):
    # Real diagnostic run: dt=1.9060091, 630 completed integration steps,
    # output.nc has its twentieth record at 1200.785733 seconds.
    (tmp_path/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n variables:\n  - source: *\n')
    text="start = '2020-01-01 00:00:00'\nstop = '2020-01-01 00:20:00'\ntimestep = 1.9060091\n"
    result=last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,0,20))
    assert result==datetime(2020,1,1,0,20,0,785733)


@pytest.mark.parametrize('dt,window,expected',[
    (3.1,'','2020-01-01 00:19:00.800000'),
    # Retained native output.nc stores 600.392866 (binary NINT input is below .5).
    (1.9060091,' time_stop: 2020-01-01 00:10:00\n','2020-01-01 00:10:00.392866'),
    (3.1,' time_stop: 2020-01-01 00:10:00\n','2020-01-01 00:09:02.500000'),
])
def test_fractional_schedule_uses_actual_final_step_and_integer_second_window(tmp_path,dt,window,expected):
    (tmp_path/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n'+window)
    text=f"start = '2020-01-01 00:00:00'\ntimestep = {dt}\n"
    assert last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,0,20)) == datetime.fromisoformat(expected)


def test_dt_output_anchor_stays_zero_when_initial_output_is_disabled(tmp_path):
    (tmp_path/'output.yaml').write_text('output:\n time_unit: dt\n time_step: 7\n')
    text="start = '2020-01-01 00:00:00'\ntimestep = 2\nsave_initial = .false.\n"
    # Direct current-exe probe dt1.9/step7 emitted n7..n630; first_index defaults 0.
    assert last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,0,20)) == datetime(2020,1,1,0,19,50)


@pytest.mark.parametrize('window,expected',[
    ('','2020-01-01 00:20:01.700000'),
    (' time_stop: 2020-01-01 00:20:00\n','2020-01-01 00:19:00.700000'),
    (' time_stop: 2020-01-01 00:20:10\n','2020-01-01 00:20:01.700000'),
])
def test_only_explicit_flexout_stop_limits_the_window(tmp_path,window,expected):
    (tmp_path/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n'+window)
    text="start = '2020-01-01 00:00:00'\ntimestep = 6.1\n"
    assert last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,0,20)) == datetime.fromisoformat(expected)


def test_flexout_clock_uses_native_start_second_float_subtraction(tmp_path):
    (tmp_path/'output.yaml').write_text('output:\n time_unit: second\n time_step: 60\n time_stop: 2020-01-01 01:10:00\n')
    text="start = '2020-01-01 01:00:00'\ntimestep = 1.9060091\n"
    assert last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,1,20)) == datetime(2020,1,1,1,10,0,392867)


def test_flexout_near_second_rule_does_not_change_native_ncdf_clock(tmp_path):
    (tmp_path/'output.yaml').write_text('output:\n time_unit: second\n time_step: 1\n')
    text="start = '2020-01-01 00:00:00'\ntimestep = .999999\nstep_2d = 1\n"
    # time.F90 assigns secondsofday before its near-integer microsecond clamp;
    # this actual native rule reports 1.0 for n=2, while native NCDF uses n*dt.
    assert last_output_time(tmp_path,'output.nc',text,datetime(2020,1,1,0,0,2)) == datetime(2020,1,1,0,0,1)
    assert last_output_time(tmp_path,'run.2d.nc',text,datetime(2020,1,1,0,0,2)) == datetime(2020,1,1,0,0,1,999998)
