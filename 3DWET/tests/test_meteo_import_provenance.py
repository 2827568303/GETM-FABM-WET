import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import netCDF4
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))


def _case(tmp_path, monkeypatch, station=(59.83917, 18.629333)):
    import server

    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    lat = station[0] if station else 30.0
    lon = station[1] if station else 117.0
    with netCDF4.Dataset(tmp_path / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('y', 2)
        ds.createDimension('x', 3)
        ds.createVariable('lonc', 'f8', ('y', 'x'))[:] = np.array([[lon - .005, lon, lon + .005]] * 2)
        ds.createVariable('latc', 'f8', ('y', 'x'))[:] = np.array([[lat - .005] * 3, [lat + .005] * 3])
    return server, server.app.test_client()


def _upload(client, *, lat='', lon='', source_url='', license_name=''):
    raw = b'date,u10,v10,slp,t2,rh,tcc,precip,evap\n2020-01-01,2,1,1013,8,70,50,0,1\n2020-01-02,3,2,1012,9,75,40,1,1\n'
    response = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'Erken weather.csv'),
        'source_lat': lat, 'source_lon': lon,
        'source_url': source_url, 'license': license_name,
    }, content_type='multipart/form-data')
    return raw, response


def test_near_station_saves_and_records_original_source(tmp_path, monkeypatch):
    server, client = _case(tmp_path, monkeypatch)
    raw, uploaded = _upload(client, lat='59.83917', lon='18.629333',
                            source_url='https://example.test/erken-weather', license_name='CC BY 4.0')
    assert uploaded.status_code == 200
    draft = client.get('/api/input/meteo/draft').json
    rows = [dict(date=draft['dates'][i], **{key: draft[key][i] for key in
             ('u10', 'v10', 'slp', 't2', 'rh', 'tcc', 'precip', 'evap')}) for i in range(2)]
    saved = client.post('/api/input/meteo/save', json={
        'rows': rows, 'source_lat': '59.83917', 'source_lon': '18.629333',
        'source_url': 'https://example.test/erken-weather', 'license': 'CC BY 4.0',
    }).json
    assert saved['success'] is True
    stored = tmp_path / draft['source']['stored_file']
    assert stored.is_file() and stored.read_bytes() == raw
    provenance = json.loads((tmp_path / 'meteo_provenance.json').read_text(encoding='utf-8'))
    assert provenance['source']['original_filename'] == 'Erken weather.csv'
    assert provenance['source']['sha256'] == hashlib.sha256(raw).hexdigest()
    assert provenance['source']['source_url'] == 'https://example.test/erken-weather'
    assert provenance['source']['license'] == 'CC BY 4.0'
    assert provenance['spatial']['mode'] == 'single_station_uniform_broadcast'
    assert provenance['spatial']['distance_km'] < 1
    assert provenance['source_period'] == {'start': '2020-01-01', 'end': '2020-01-02', 'rows': 2}
    assert provenance['columns']['t2'] == 't2'
    assert 'precip: mm/day to m/s' in provenance['conversions']
    assert provenance['defaults_applied'] == {}
    inputs = client.get('/api/case/inputs').json['files']
    assert any(item['name'] == 'meteo_provenance.json' and item['exists'] for item in inputs)
    with netCDF4.Dataset(tmp_path / 'meteo.nc') as ds:
        assert np.all(ds.variables['t2'][0] == ds.variables['t2'][0, 0, 0])


def test_far_station_requires_confirmation_without_writing_meteo(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch, station=(29.83075, 117.00015))
    _upload(client, lat='59.83917', lon='18.629333')
    warning = client.post('/api/input/meteo/save', json={}).json
    assert warning['requires_confirmation'] is True
    assert warning['warning']['distance_km'] > 25
    assert warning['warning']['grid_center']
    assert not (tmp_path / 'meteo.nc').exists()
    saved = client.post('/api/input/meteo/save', json={
        'confirmation_token': warning['confirmation_token']}).json
    assert saved['success'] is True
    assert saved['spatial']['distance_km'] > 25


def test_unknown_station_requires_explicit_confirmation(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch, station=None)
    _upload(client)
    warning = client.post('/api/input/meteo/save', json={}).json
    assert warning['requires_confirmation'] is True
    assert warning['warning']['position_known'] is False
    assert warning['warning']['message'] == '位置未知，仍可广播'
    assert not (tmp_path / 'meteo.nc').exists()
    assert client.post('/api/input/meteo/save', json={
        'confirmation_token': warning['confirmation_token']}).json['success'] is True


def test_legacy_rows_payload_still_saves_after_confirmation(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch, station=(30.0, 117.0))
    rows = [dict(date='2020-01-01', u10=2, v10=1, slp=1013, t2=8,
                 rh=.7, tcc=.5, precip=0, evap=0),
            dict(date='2020-01-02', u10=2, v10=1, slp=1013, t2=9,
                 rh=.7, tcc=.5, precip=0, evap=0)]
    warning = client.post('/api/input/meteo/save', json={'rows': rows}).json
    assert warning['requires_confirmation'] is True
    saved = client.post('/api/input/meteo/save', json={
        'rows': rows, 'confirmation_token': warning['confirmation_token']}).json
    assert saved['success'] is True
    assert (tmp_path / 'meteo.nc').is_file()
    provenance = json.loads((tmp_path / 'meteo_provenance.json').read_text(encoding='utf-8'))
    assert provenance['source']['sha256'] is None
    assert provenance['source']['original_filename'] is None


def test_duplicate_upload_names_are_preserved_without_overwrite(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw1, first = _upload(client, lat='59.83917', lon='18.629333')
    assert first.status_code == 200
    first_path = tmp_path / first.json['source']['stored_file']
    raw2 = raw1.replace(b'2,1,1013,8', b'9,1,1013,8', 1)
    second = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw2), 'Erken weather.csv'),
        'source_lat': '59.83917', 'source_lon': '18.629333',
    }, content_type='multipart/form-data')
    assert second.status_code == 200
    second_path = tmp_path / second.json['source']['stored_file']
    assert first_path != second_path
    assert first_path.read_bytes() == raw1
    assert second_path.read_bytes() == raw2


def test_hourly_upload_preserves_timestamps_and_writes_continuous_model_offsets(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    (tmp_path / 'getm.inp').write_text(
        "&time\n start = '2020-01-01 00:00:00'\n/\n", encoding='utf-8')
    start = datetime(2020, 1, 1, 1)
    rows = ['date,u10,v10,slp,t2,rh,tcc,precip,evap']
    for index in range(24):
        timestamp = (start + timedelta(hours=index)).strftime('%Y-%m-%d %H:%M:%S')
        rows.append(f'{timestamp},2,1,1013,8,70,50,0,1')
    response = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(('\n'.join(rows) + '\n').encode('utf-8')), 'hourly.csv'),
        'source_lat': '59.83917', 'source_lon': '18.629333',
    }, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.json['n_rows'] == 24
    draft = client.get('/api/input/meteo/draft').json
    expected_dates = [(start + timedelta(hours=index)).strftime('%Y-%m-%d %H:%M:%S')
                      for index in range(24)]
    assert draft['dates'] == expected_dates

    saved = client.post('/api/input/meteo/save', json={})
    assert saved.status_code == 200 and saved.json['success'] is True
    with netCDF4.Dataset(tmp_path / 'meteo.nc') as ds:
        time = ds.variables['time'][:]
        assert ds.variables['time'].units == 'seconds since 2020-01-01 00:00:00'
        np.testing.assert_array_equal(time, np.arange(1, 25) * 3600)
        np.testing.assert_array_equal(np.diff(time), np.full(23, 3600))
        assert len(ds.dimensions['time']) == 24


def test_daily_save_extension_keeps_time_and_forcing_lengths_aligned(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    (tmp_path / 'getm.inp').write_text(
        "&time\n start = '2020-01-01 00:00:00'\n stop = '2020-01-02 00:00:00'\n/\n",
        encoding='utf-8')
    _upload(client, lat='59.83917', lon='18.629333')

    saved = client.post('/api/input/meteo/save', json={})

    assert saved.status_code == 200 and saved.json['success'] is True
    assert saved.json['extended_days'] == 1
    with netCDF4.Dataset(tmp_path / 'meteo.nc') as ds:
        assert len(ds.dimensions['time']) == 3
        np.testing.assert_array_equal(ds.variables['time'][:], [0, 86400, 172800])
        assert ds.variables['t2'].shape[0] == 3


@pytest.mark.parametrize('dates', [
    ['2020-01-01 00:00:00', '2020-01-01 00:00:00'],
    ['2020-01-01 02:00:00', '2020-01-01 01:00:00'],
])
def test_meteo_save_rejects_duplicate_or_descending_timestamps_without_overwriting(
        tmp_path, monkeypatch, dates):
    _, client = _case(tmp_path, monkeypatch)
    original = b'preserve existing forcing on invalid save'
    (tmp_path / 'meteo.nc').write_bytes(original)
    rows = [dict(date=date, u10=2, v10=1, slp=1013, t2=8,
                 rh=.7, tcc=.5, precip=0, evap=0) for date in dates]

    response = client.post('/api/input/meteo/save', json={
        'rows': rows, 'source_lat': '59.83917', 'source_lon': '18.629333',
    })

    assert response.status_code == 400
    assert response.json['success'] is False
    assert '严格递增' in response.json['error']
    assert (tmp_path / 'meteo.nc').read_bytes() == original


def test_meteo_ui_explains_uniform_broadcast_and_source_metadata_fields():
    root = Path(__file__).parents[1] / 'app'
    html = (root / 'templates' / 'index.html').read_text(encoding='utf-8')
    script = (root / 'static' / 'js' / 'app.js').read_text(encoding='utf-8')
    assert 'meteo-source-lat' in html and 'meteo-source-lon' in html
    assert 'meteo-source-url' in html and 'meteo-source-license' in html
    assert '空间均匀广播到全格点' in html
    assert 'confirmation_token' in script and 'grid_center' in script
    assert 'meteo.nc:swr' in html and '启用 GETM 实测短波路径' in html
    assert "res.shortwave_mode === 'measured_swr'" in script


def test_prognos_malma_schema_converts_wind_rain_and_measured_shortwave(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'TMSTAMP,SW_Rad_Avg,Air_Temp_AS_Avg,RelHumidity_Avg,Vapor_Pressure_Avg,'
        'MeanWS,WindDir,Rain_Total,AirPressure_hPa_Avg,Total molnmängd\n'
        '2017-06-29 10:00,400,18,65,10,5,90,0.2,1008,60\n'
        '2017-06-29 11:00,500,19,62,11,10,180,0.4,1007,55\n'
    ).encode('utf-8')
    response = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'ErkenMalmaIslanMetData.csv'),
        'source_lat': '59.83909', 'source_lon': '18.629558',
        'source_url': 'https://www.hydroshare.org/resource/2dead0d54fe74ee7943e89ae4159aab1/',
        'license': 'CC BY 4.0',
    }, content_type='multipart/form-data')

    assert response.status_code == 200, response.json
    draft = client.get('/api/input/meteo/draft').json
    assert draft['u10'][0] == pytest.approx(-5.0)
    assert draft['v10'][0] == pytest.approx(0.0, abs=1e-12)
    assert draft['u10'][1] == pytest.approx(0.0, abs=1e-12)
    assert draft['v10'][1] == pytest.approx(10.0)
    assert draft['precip'][0] == pytest.approx(0.2)
    assert draft['meteo_source_mask'] == [
        {'source_primary': 'Malma observation'}, {'source_primary': 'Malma observation'}]
    assert draft['shortwave_mode'] == 'measured_swr'
    assert draft['swr'] == [400.0, 500.0]
    assert draft['tcc'] == pytest.approx([0.60, 0.55])
    assert draft['effective_cloud_source'] == ['observed cloud for longwave'] * 2
    assert draft['source']['time_standard'] == 'UTC+01:00 fixed standard time'
    assert 'precip: hourly accumulation mm to m/s' in draft['conversions']
    assert 'swr: measured incoming shortwave W m-2' in draft['conversions']
    (tmp_path / 'getm.inp').write_text('&meteo\n calc_met = .true.\n/\n', encoding='utf-8')
    saved = client.post('/api/input/meteo/save', json={})
    assert saved.status_code == 200 and saved.json['success'] is True
    with netCDF4.Dataset(tmp_path / 'meteo.nc') as ds:
        np.testing.assert_allclose(ds.variables['precip'][:, 0, 0], np.array([0.2, 0.4]) / 3_600_000.0)
        assert ds.variables['tcc'].shape[0] == 2
        np.testing.assert_allclose(ds.variables['swr'][:, 0, 0], [400, 500])
        assert ds.variables['swr'].units == 'W m-2'
    inp = (tmp_path / 'getm.inp').read_text(encoding='utf-8')
    assert 'use_measured_swr = .true.' in inp
    provenance = json.loads((tmp_path / 'meteo_provenance.json').read_text(encoding='utf-8'))
    assert provenance['source']['time_standard'] == 'UTC+01:00 fixed standard time'
    assert provenance['effective_cloud_source'] == ['observed cloud for longwave'] * 2
    assert provenance['shortwave_mode'] == 'measured_swr'


def test_swr_csv_without_cloud_uses_labeled_proxy_and_direct_mode(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'TMSTAMP,SW_Rad_Avg,Air_Temp_AS_Avg,RelHumidity_Avg,Vapor_Pressure_Avg,'
        'MeanWS,WindDir,Rain_Total,AirPressure_hPa_Avg\n'
        '2017-06-29 10:00,0,18,65,10,5,90,0.2,1008\n'
        '2017-06-29 11:00,600,19,62,11,10,180,0.4,1007\n'
    ).encode('utf-8')
    uploaded = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'swr.csv'), 'source_lat': '59.83909',
        'source_lon': '18.629558',
    }, content_type='multipart/form-data')
    assert uploaded.status_code == 200, uploaded.json
    draft = client.get('/api/input/meteo/draft').json
    assert draft['shortwave_mode'] == 'measured_swr'
    assert draft['swr'] == [0.0, 600.0]
    assert draft['tcc'] == [0.5, 0.5]
    assert draft['effective_cloud_source'] == ['fixed proxy for longwave'] * 2


@pytest.mark.parametrize('bad_swr', ['-1', 'NaN', 'inf'])
def test_measured_swr_rejects_nonfinite_or_negative_csv_values(tmp_path, monkeypatch, bad_swr):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'TMSTAMP,SW_Rad_Avg,Air_Temp_AS_Avg,MeanWS,WindDir,Rain_Total,AirPressure_hPa_Avg\n'
        f'2017-06-29 10:00,{bad_swr},18,5,90,0.2,1008\n'
        '2017-06-29 11:00,500,19,10,180,0.4,1007\n'
    ).encode('utf-8')
    response = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'invalid-swr.csv'), 'source_lat': '59.83909',
        'source_lon': '18.629558',
    }, content_type='multipart/form-data')
    assert response.status_code == 400
    assert '有限且非负' in response.json['error']
    assert not (tmp_path / 'meteo_draft.json').exists()


def test_meteo_upload_rejects_unresolved_gaps_in_supplied_forcing(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'TMSTAMP,SW_Rad_Avg,Air_Temp_AS_Avg,RelHumidity_Avg,Vapor_Pressure_Avg,'
        'MeanWS,WindDir,Rain_Total,AirPressure_hPa_Avg,Total molnmängd\n'
        '2017-06-29 10:00,400,18,65,10,5,90,0.2,1008,60\n'
        '2017-06-29 11:00,500,19,62,11,,180,0.4,1007,55\n'
    ).encode('utf-8')
    response = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'ErkenMalmaIslanMetData.csv'),
        'source_lat': '59.83909', 'source_lon': '18.629558',
    }, content_type='multipart/form-data')

    assert response.status_code == 400
    assert 'MeanWS' in response.json['error']
    assert not (tmp_path / 'meteo_draft.json').exists()


def test_meteo_source_columns_are_retained_as_per_hour_provenance(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'date,u10,v10,slp,t2,rh,tcc,precip,evap,source_wind,source_cloud\n'
        '2017-06-29 10:00,1,2,1008,18,65,0.6,0,0,Malma observation,Svanberga observation\n'
        '2017-06-29 11:00,2,3,1007,19,62,0.55,0,0,ERA5 reanalysis fill,Svanberga observation\n'
    ).encode('utf-8')
    uploaded = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'merged.csv'), 'source_lat': '59.83909',
        'source_lon': '18.629558',
    }, content_type='multipart/form-data')

    assert uploaded.status_code == 200, uploaded.json
    assert uploaded.json['forcing_source_counts'] == {
        'source_wind': {'ERA5 reanalysis fill': 1, 'Malma observation': 1},
        'source_cloud': {'Svanberga observation': 2},
    }
    draft = client.get('/api/input/meteo/draft').json
    assert draft['meteo_source_mask'][1] == {
        'source_wind': 'ERA5 reanalysis fill', 'source_cloud': 'Svanberga observation'}
    assert uploaded.json['unmapped_cols'] == []


def test_mixed_percent_cloud_and_inverted_cloud_share_fraction_units(tmp_path, monkeypatch):
    _, client = _case(tmp_path, monkeypatch)
    raw = (
        'TMSTAMP,SW_Rad_Avg,Air_Temp_AS_Avg,MeanWS,WindDir,Rain_Total,'
        'AirPressure_hPa_Avg,Total molnmängd\n'
        '2017-06-29 00:00,0,15,2,90,0,1010,60\n'
        '2017-06-29 10:00,400,18,5,90,0,1008,55\n'
    ).encode('utf-8')
    uploaded = client.post('/api/input/meteo/upload', data={
        'file': (io.BytesIO(raw), 'mixed-cloud.csv'),
        'source_lat': '59.83909', 'source_lon': '18.629558',
    }, content_type='multipart/form-data')
    assert uploaded.status_code == 200, uploaded.json
    draft = client.get('/api/input/meteo/draft').json
    assert draft['tcc'][0] == pytest.approx(.60)
    assert 0 <= draft['tcc'][1] <= 1
    assert max(draft['tcc']) <= 1
