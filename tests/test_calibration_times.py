"""Actual fractional native clocks must survive result extraction and pairing."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

import netCDF4 as nc
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import server


def test_seven_microsecond_observations_match_the_exact_native_times():
    times = ['2020-01-01 00:01:00.992291', '2020-01-01 00:04:00.157147',
             '2020-01-01 00:07:01.228011', '2020-01-01 00:10:00.392866',
             '2020-01-01 00:13:01.463731', '2020-01-01 00:16:00.628586',
             '2020-01-01 00:20:00.785733']
    obs = [dict(time=t, value=10+i) for i,t in enumerate(times)]
    pairs, _ = server._pair_obs_sim(obs, dict(times=times, values=list(range(11,18))), max_lag_hours=0)
    assert len(pairs) == 7
    assert [p['sim']-p['obs'] for p in pairs] == [1]*7


@pytest.mark.parametrize('value', [
    '2020-01-01T00:20:00.785733Z', '2020-01-01T08:20:00.785733+08:00',
    '2019-12-31T19:20:00.785733-05:00', '2020-DOY001 00:20:00.785733',
    datetime(2020,1,1,8,20,0,785733,tzinfo=timezone(timedelta(hours=8))),
])
def test_timezones_and_ordinal_microseconds_share_the_model_utc_clock(value):
    assert server._parse_iso_time(value) == datetime(2020,1,1,0,20,0,785733)


def test_native_timeseries_retains_microseconds(tmp_path):
    path = tmp_path/'output.nc'
    with nc.Dataset(path,'w') as ds:
        for name,size in [('time',2),('level',1),('y',1),('x',1)]:
            ds.createDimension(name,size)
        clock = ds.createVariable('time','f8',('time',))
        clock.units = 'seconds since 2020-01-01 00:00:00'
        clock[:] = [60.992291,1200.785733]
        ds.createVariable('temp','f8',('time','level','y','x'))[:] = 17.6
    result = server.get_timeseries(path,'temp',i=0,j=0)
    assert result['times'] == ['2020-01-01 00:01:00.992291','2020-01-01 00:20:00.785733']
    pairs,_ = server._pair_obs_sim([dict(time=t,value=17.6) for t in result['times']],result,max_lag_hours=0)
    assert len(pairs) == 2


@pytest.mark.parametrize('bad',['2023-02-29 00:00:00.123456','2020-DOY367','bad'])
def test_invalid_calendar_times_remain_invalid(bad):
    assert server._parse_iso_time(bad) is None


@pytest.mark.parametrize('fraction',['1','12','1234','12345'])
def test_short_fractional_timestamps_from_trimmed_cf_labels(fraction):
    expected=datetime(2020,1,1,0,0,0,int(fraction.ljust(6,'0')))
    assert server._parse_iso_time('2020-01-01 00:00:00.'+fraction) == expected
    assert server._parse_iso_time('2020-DOY001 00:00:00.'+fraction) == expected
