from pathlib import Path
import json
import hashlib
import subprocess
import sys

import pytest
import netCDF4 as nc
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import server


def test_observation_preview_apply_and_reload_are_case_scoped(tmp_path, monkeypatch):
    case_a, case_b = tmp_path / 'case-a', tmp_path / 'case-b'
    case_a.mkdir(); case_b.mkdir()
    source = tmp_path / 'observations.csv'
    source.write_text('time,value,depth_m,unit,variable,lake_id,station_id,point_id\n'
                      '2020-01-01,4,2,degC,T,L,S,P1\n', encoding='utf-8')
    monkeypatch.setattr(server, 'active_case_path', case_a)
    monkeypatch.setattr(server, 'run_status', 'idle')
    monkeypatch.setattr(server, 'run_thread', None)
    client = server.app.test_client()
    body = {'files': [str(source)], 'mappings': {}, 'max_time_gap_hours': 3}
    preview = client.post('/api/calibration/observations/preview', json=body)
    assert preview.status_code == 200, preview.json
    assert not (case_a / 'calibration' / 'observations.json').exists()
    applied = client.post('/api/calibration/observations/apply', json={'preview': preview.json, 'mappings': {}})
    assert applied.status_code == 200, applied.json
    assert client.get('/api/calibration/observations').json['records'][0]['point_id'] == 'P1'
    monkeypatch.setattr(server, 'active_case_path', case_b)
    assert client.get('/api/calibration/observations').json['records'] == []
    assert not (case_b / 'calibration').exists()


def test_observation_apply_refuses_while_case_is_busy(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    source = tmp_path / 'observations.csv'
    source.write_text('time,value,depth_m,unit,variable\n2020-01-01,4,2,degC,T\n')
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_results_context', lambda: {'busy': True})
    client = server.app.test_client()
    preview = client.post('/api/calibration/observations/preview', json={'files': [str(source)], 'max_time_gap_hours': 2})
    response = client.post('/api/calibration/observations/apply', json={'preview': preview.json})
    assert response.status_code == 409
    assert not (case / 'calibration' / 'observations.json').exists()


def test_observation_preview_requires_explicit_positive_time_gap(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    source = tmp_path / 'observations.csv'
    source.write_text('time,value,depth_m,unit,variable,lake_id,station_id\n2020-01-01,4,2,degC,T,L,S\n')
    monkeypatch.setattr(server, 'active_case_path', case)
    client = server.app.test_client()
    assert client.post('/api/calibration/observations/preview', json={'files': [str(source)]}).status_code == 400
    assert client.post('/api/calibration/observations/preview', json={
        'files': [str(source)], 'max_time_gap_hours': 0}).status_code == 400


def test_wide_csv_preview_preserves_explicit_header_value_and_constant_depth_mapping(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    source = tmp_path / 'official-profile.csv'
    raw = (''.join(f'metadata line {line}\n' for line in range(1, 70)) +
           'TIMESTAMP,TW_-1.0m,TW_-2.0m\n2024-06-01T12:00:00,17.25,16.80\n').encode()
    source.write_bytes(raw)
    mapping = {
        'header_row': 70, 'time_column': 'TIMESTAMP', 'value_column': 'TW_-1.0m',
        'depth_m_mode': 'constant', 'depth_m_constant': 1.0,
        'unit': 'degC', 'variable': 'temp',
    }
    mappings = {'__version__': 'observation-ui-v3', str(source): mapping}
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_results_context', lambda: {'busy': False})
    response = server.app.test_client().post('/api/calibration/observations/preview', json={
        'files': [str(source)], 'mappings': mappings, 'max_time_gap_hours': 3})

    assert response.status_code == 200, response.json
    entry = response.json['files'][0]
    assert entry['mapping'] == mapping
    assert len(entry['records']) == 1
    record = entry['records'][0]
    assert (record['value'], record['depth_m'], record['source_line']) == (17.25, 1.0, 71)
    assert record['source_row'] == {
        'TIMESTAMP': '2024-06-01T12:00:00', 'TW_-1.0m': '17.25', 'TW_-2.0m': '16.80'}
    from observation_store import ObservationStore
    store = ObservationStore(case.parent)
    signed_payload = {key: value for key, value in response.json.items() if key != 'preview_signature'}
    assert response.json['preview_signature'] == store._sign(signed_payload)
    assert source.read_bytes() == raw


def test_obs_preview_apply_preserves_per_file_model_mapping_and_diagnostics(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    source_dir = tmp_path / 'official'; source_dir.mkdir()
    sources = {
        'TEMP.obs': '2020-01-01 00:00 1 10.2\n',
        'DO.obs': '2020-01-01 00:00 1 8.4\nbad row\n',
        'CHLA.obs': '2020-01-01 00:00 1 2.3\n',
    }
    paths = []
    for name, content in sources.items():
        path = source_dir / name
        path.write_text(content, encoding='utf-8')
        paths.append(str(path))
    mappings = {'__version__': 'observation-ui-v2'}
    for path, variable, unit in zip(paths,
            ['temp', 'abiotic_water_sO2W', 'wet_chla_calculator_result'],
            ['degC', 'mg/L', 'ug/L']):
        mappings[path] = {'variable': variable, 'unit': unit,
                          'lake_id': 'Ravn', 'station_id': 'Ravn'}
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_results_context', lambda: {'busy': False})
    client = server.app.test_client()

    response = client.post('/api/calibration/observations/preview', json={
        'files': paths, 'mappings': mappings, 'max_time_gap_hours': 2})
    assert response.status_code == 200, response.json
    preview = response.json
    assert [entry['mapping'] for entry in preview['files']] == [mappings[path] for path in paths]
    assert [entry['records'][0]['variable'] for entry in preview['files']] == [
        'temp', 'abiotic_water_sO2W', 'wet_chla_calculator_result']
    assert [entry['records'][0]['unit'] for entry in preview['files']] == ['degC', 'mg/L', 'ug/L']
    assert all(entry['records'][0]['lake_id'] == entry['records'][0]['station_id'] == 'Ravn'
               for entry in preview['files'])
    assert preview['files'][1]['diagnostics'] == [
        {'source_file': 'DO.obs', 'source_line': 2, 'reason': 'expected_four_columns'}]

    applied = client.post('/api/calibration/observations/apply', json={
        'preview': preview, 'mappings': mappings})
    assert applied.status_code == 200, applied.json
    records = {record['source_file']: record for record in applied.json['records']}
    assert {name: record['variable'] for name, record in records.items()} == {
        'TEMP.obs': 'temp', 'DO.obs': 'abiotic_water_sO2W',
        'CHLA.obs': 'wet_chla_calculator_result'}
    assert [item for item in applied.json['diagnostics'] if item.get('source_file') == 'DO.obs'] == [
        {'source_file': 'DO.obs', 'source_line': 2, 'reason': 'expected_four_columns'}]


def test_observation_preview_signature_survives_browser_json_round_trip(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    source = tmp_path / 'observations.csv'
    source.write_text('time,value,depth_m,unit,variable,lake_id,station_id\n'
                      '2020-01-01,4,2,degC,T,L,S\n', encoding='utf-8')
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_results_context', lambda: {'busy': False})
    client = server.app.test_client()
    preview_response = client.post('/api/calibration/observations/preview', json={
        'files': [str(source)], 'mappings': {}, 'max_time_gap_hours': 1})
    assert preview_response.status_code == 200, preview_response.json

    # The browser parses the preview and serializes it again before Apply.
    browser_payload = subprocess.run(
        ['node', '-e', 'let s="";process.stdin.setEncoding("utf8");process.stdin.on("data",c=>s+=c);'
         'process.stdin.on("end",()=>process.stdout.write(JSON.stringify(JSON.parse(s))))'],
        input=json.dumps({'preview': preview_response.json, 'mappings': {}}, ensure_ascii=False),
        text=True, capture_output=True, check=True)
    tampered = json.loads(browser_payload.stdout)
    tampered['preview']['files'][0]['records'][0]['value'] = 5
    rejected = client.post('/api/calibration/observations/apply', json=tampered)
    assert rejected.status_code == 400
    assert 'modified' in rejected.json['error']

    response = client.post('/api/calibration/observations/apply',
                           data=browser_payload.stdout, content_type='application/json')
    assert response.status_code == 200, response.json
    assert len(response.json['records']) == 1


def test_native_observation_series_uses_each_time_hn_and_zc_without_downsampling(tmp_path):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.coordinate_crs = 'EPSG:25832'
        for name, size in [('time', 2), ('sigma', 2), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01 00:00:00'; clock[:] = [0, 1]
        sigma = ds.createVariable('sigma', 'f8', ('sigma',)); sigma[:] = [-.75, -.25]
        temp = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x')); temp.units = 'degC'
        temp[:, :, 0, 0] = [[0, 10], [12, 18]]
        hn = ds.createVariable('hn', 'f8', temp.dimensions); hn.units = 'm'
        hn[:, :, 0, 0] = [[3, 9], [4, 10]]
        zc = ds.createVariable('zc', 'f8', temp.dimensions); zc.units = 'm'
        # zc carries elevations at the centres implied by each native hn record.
        zc[:, :, 0, 0] = [[-10.5, -4.5], [-10, -4]]
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy.units = 'm'; bathy[:] = 12
        for name, dim, val in [('xc', 'x', 10), ('yc', 'y', 20)]:
            coord = ds.createVariable(name, 'f8', (dim,)); coord.units = 'm'; coord[:] = [val]
    target = {'point_id': 'P', 'lake_id': 'L', 'station_id': 'S', 'i': 0, 'j': 0,
              'x_m': 10, 'y_m': 20, 'coordinate_crs': 'EPSG:25832', 'spatial_mapping': 'verified'}
    result = server._native_observation_model(path, 'temp', target)
    assert result['times'] == ['2020-01-01 00:00:00', '2020-01-01 01:00:00']
    assert result['center_depth'] == [[10.5, 4.5], [12.0, 6.0]]
    assert result['values'] == [[0.0, 10.0], [12.0, 18.0]]
    assert result['spatial_mapping'] == 'verified'


def test_native_observation_series_accepts_explicit_ui_cell_without_fabricating_crs(tmp_path):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 1), ('y', 1), ('x', 2)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        sigma = ds.createVariable('sigma', 'f8', ('sigma',)); sigma[:] = [-.5]
        temp = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x')); temp.units = 'degC'; temp[:] = 4
        hn = ds.createVariable('hn', 'f8', temp.dimensions); hn.units = 'm'; hn[:] = 10
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy.units = 'm'; bathy[:] = [[10, 10]]
        for name, dim, values in [('xc', 'x', [10, 20]), ('yc', 'y', [30])]:
            coord = ds.createVariable(name, 'f8', (dim,)); coord.units = 'm'; coord[:] = values
    target = {'point_id': 'obs-A', 'lake_id': 'Lake-X', 'station_id': 'Station-A', 'i': 1, 'j': 0,
              'x_m': 20, 'y_m': 30, 'spatial_mapping': 'explicit_cell',
              'mapping_source': 'gridstudio_explicit_cell'}
    result = server._native_observation_model(path, 'temp', target)
    assert result['point_id'] == 'obs-A'
    assert result['spatial_mapping'] == 'explicit_cell'
    assert result['mapping_source'] == 'gridstudio_explicit_cell'
    assert 'coordinate_crs' not in result
    with pytest.raises(ValueError, match='does not match verified station mapping'):
        server._native_observation_model(path, 'temp', {**target, 'x_m': 19})
    from observation_matching import pair_observations
    pairs, diagnostics = pair_observations([{'point_id': 'obs-A', 'lake_id': 'Lake-X', 'station_id': 'Station-A',
        'variable': 'temp', 'time': '2020-01-01 00:00:00', 'depth_m': 5, 'unit': 'degC', 'value': 3,
        'quality': [], 'quality_flags': []}], result, max_time_gap_hours=1)
    assert not diagnostics
    assert pairs[0]['sim'] == 4


def test_comparison_uses_imported_observations_and_native_pairer(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'effective_calibration_points', lambda ctx: [
        {'id': 'P', 'variables': ['temp'], 'i': 0, 'j': 0, 'lake_id': 'L',
         'station_id': 'S', 'point_id': 'P', 'x_m': 1, 'y_m': 2,
         'coordinate_crs': 'EPSG:25832', 'spatial_mapping': 'verified'}])
    monkeypatch.setattr(server, 'find_output_files', lambda *a, **k: {'3d': 'unused.nc', '2d': None})
    monkeypatch.setattr(server, 'get_timeseries', lambda *a, **k: pytest.fail('legacy downsampled series must not score'))
    monkeypatch.setattr(server, '_native_observation_model', lambda *a: {
        'times': ['2020-01-01 00:00:00'], 'values': [[1]], 'center_depth': [[2]],
        'variable': 'temp', 'unit': 'degC', 'lake_id': 'L', 'station_id': 'S',
        'point_id': 'P', 'spatial_mapping': 'verified', 'geometry_source': 'hn+zc', 'downsampled': False})
    from observation_store import ObservationStore
    ObservationStore(case.parent).save('case', {
        'version': 1, 'case_id': 'case', 'max_time_gap_hours': 1,
        'records': [{'point_id': 'P', 'lake_id': 'L', 'station_id': 'S', 'variable': 'temp',
                     'time': '2020-01-01 00:00:00', 'depth_m': 2, 'unit': 'degC',
                     'value': 4, 'quality': [], 'quality_flags': []}], 'diagnostics': [], 'manifest': []})
    response = server.app.test_client().get('/api/calibration/comparison?point_id=P&variable=temp')
    assert response.status_code == 200, response.json
    assert response.json['scatter_pairs'][0]['obs'] == 4
    assert response.json['scatter_pairs'][0]['sim'] == 1
    assert response.json['geometry_source'] == 'hn+zc'
    assert response.json['downsampled'] is False


def test_comparison_uses_persisted_ui_cell_and_matches_observation_point_identity(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('y', 1); ds.createDimension('x', 2)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [10, 20]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [30]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[10, 10]]
    (case / 'lake_points.json').write_text(json.dumps({'points': [{
        'id': 'local', 'calibration_id': 'cal-1', 'i': 2, 'j': 1, 'lake_id': 'Lake-X',
        'station_id': 'Station-A', 'observation_point_id': 'obs-A'}]}))
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, 'calibration_points', [{'id': 'cal-1', 'name': 'Station A',
        'i': 0, 'j': 0, 'variables': ['temp']}])
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    output = tmp_path / 'output.nc'
    with nc.Dataset(output, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 1), ('y', 1), ('x', 2)]: ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        sigma = ds.createVariable('sigma', 'f8', ('sigma',)); sigma[:] = [-.5]
        temp = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x')); temp.units = 'degC'; temp[:] = 4
        hn = ds.createVariable('hn', 'f8', temp.dimensions); hn.units = 'm'; hn[:] = 10
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[10, 10]]
        for name, dim, values in [('xc', 'x', [10, 20]), ('yc', 'y', [30])]:
            coord = ds.createVariable(name, 'f8', (dim,)); coord.units = 'm'; coord[:] = values
    monkeypatch.setattr(server, 'find_output_files', lambda *a, **k: {'3d': str(output), '2d': None})
    from observation_store import ObservationStore
    ObservationStore(case.parent).save('case', {'max_time_gap_hours': 1, 'records': [{
        'point_id': 'obs-A', 'lake_id': 'Lake-X', 'station_id': 'Station-A', 'variable': 'temp',
        'time': '2020-01-01 00:00:00', 'depth_m': 5, 'unit': 'degC', 'value': 3,
        'quality': [], 'quality_flags': []}], 'manifest': []})
    response = server.app.test_client().get('/api/calibration/comparison?point_id=cal-1&variable=temp')
    assert response.status_code == 200, response.json
    assert response.json['scatter_pairs'] == [{'time': '2020-01-01 00:00:00', 'obs': 3.0, 'sim': 4.0, 'source_line': None}]
    assert response.json['simulated']['point_id'] == 'obs-A'
    assert response.json['simulated']['spatial_mapping'] == 'explicit_cell'


def test_official_ravn_gotm_replay_reads_explicit_column_native_geometry():
    path = Path(__file__).resolve().parents[1] / 'build' / 'ravn-official-replay-20261017-attempt01' / 'Default' / 'output.nc'
    if not path.exists():
        pytest.skip('official Ravn replay fixture is unavailable')
    target = {'point_id': 'Ravn-column', 'lake_id': 'Ravn', 'representativeness': 'column'}
    result = server._native_observation_model(path, 'temp', target)
    assert len(result['times']) == 5844
    assert len(result['values']) == len(result['center_depth']) == 5844
    assert len(result['center_depth'][0]) == 32
    assert result['center_depth'][0][0] == pytest.approx(31.5)
    assert result['center_depth'][0][-1] == pytest.approx(0.5)
    assert result['representativeness'] == 'column'
    assert result['downsampled'] is False
    from observation_matching import pair_observations
    observation = {'point_id': 'Ravn-column', 'lake_id': 'Ravn', 'station_id': 'official-station',
                  'variable': 'temp', 'time': result['times'][0], 'depth_m': 31.5,
                  'unit': result['unit'], 'value': 4.0, 'quality': [], 'quality_flags': []}
    pairs, diagnostics = pair_observations([observation], result, max_time_gap_hours=1)
    assert len(pairs) == 1, diagnostics
    assert pairs[0]['sim'] == pytest.approx(result['values'][0][0])


def test_native_observation_model_exposes_attested_mass_basis_provenance(tmp_path):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.title = 'QWET'
        ds.comment = 'file created by the GOTM output_manager'
        ds.wet_native_metadata_source = 'wet_ravn_gotm_943d3c4'
        for name, size in [('time', 1), ('z', 1), ('lat', 1), ('lon', 1)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        h = ds.createVariable('h', 'f8', ('time', 'z', 'lat', 'lon')); h.units = 'm'; h[:] = 10
        z = ds.createVariable('z', 'f8', ('time', 'z', 'lat', 'lon')); z.units = 'm'; z[:] = -5
        oxygen = ds.createVariable('abiotic_water_sO2W', 'f8', ('time', 'z', 'lat', 'lon'))
        oxygen.units = 'g/m3'; oxygen[:] = 8
    target = {'point_id': 'Ravn-column', 'lake_id': 'Ravn', 'representativeness': 'column'}
    result = server._native_observation_model(path, 'abiotic_water_sO2W', target)
    assert result['mass_basis'] == 'O2'
    assert result['unit'] == 'gO2/m3'
    assert result['mass_basis_source'] == 'wet_ravn_gotm_943d3c4'
    assert result['mass_basis_provenance']['source_file'] == '3DWET/src/wet/src/abiotic_water.F90'


def test_native_observation_model_accepts_hash_bound_sidecar_and_rejects_stale_sidecar(tmp_path):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.title = 'QWET'; ds.comment = 'file created by the GOTM output_manager'
        for name, size in [('time', 1), ('z', 1), ('lat', 1), ('lon', 1)]: ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        h = ds.createVariable('h', 'f8', ('time', 'z', 'lat', 'lon')); h.units = 'm'; h[:] = 10
        z = ds.createVariable('z', 'f8', ('time', 'z', 'lat', 'lon')); z.units = 'm'; z[:] = -5
        oxygen = ds.createVariable('abiotic_water_sO2W', 'f8', ('time', 'z', 'lat', 'lon'))
        oxygen.units = 'g/m3'; oxygen[:] = 8
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    sidecar = path.with_name('native_variable_metadata.json')
    sidecar.write_text(json.dumps({'producer': 'wet_ravn_gotm_943d3c4', 'output_sha256': digest}), encoding='utf-8')
    target = {'point_id': 'Ravn-column', 'lake_id': 'Ravn', 'representativeness': 'column'}
    result = server._native_observation_model(path, 'abiotic_water_sO2W', target)
    assert result['mass_basis'] == 'O2'
    sidecar.write_text(json.dumps({'producer': 'wet_ravn_gotm_943d3c4', 'output_sha256': '0' * 64}), encoding='utf-8')
    result = server._native_observation_model(path, 'abiotic_water_sO2W', target)
    assert result.get('mass_basis') is None


def test_native_observation_model_does_not_assume_basis_for_unattested_netcdf(tmp_path):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.title = 'QWET'
        ds.comment = 'file created by the GOTM output_manager'
        for name, size in [('time', 1), ('z', 1), ('lat', 1), ('lon', 1)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        h = ds.createVariable('h', 'f8', ('time', 'z', 'lat', 'lon')); h.units = 'm'; h[:] = 10
        z = ds.createVariable('z', 'f8', ('time', 'z', 'lat', 'lon')); z.units = 'm'; z[:] = -5
        oxygen = ds.createVariable('abiotic_water_sO2W', 'f8', ('time', 'z', 'lat', 'lon'))
        oxygen.units = 'g/m3'; oxygen[:] = 8
    result = server._native_observation_model(path, 'abiotic_water_sO2W', {
        'point_id': 'Ravn-column', 'lake_id': 'Ravn', 'representativeness': 'column'})
    assert result.get('mass_basis') is None
    assert result['unit'] == 'g/m3'


def test_result_inventory_reports_single_column_geometry(tmp_path, monkeypatch):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 2), ('z', 3), ('lat', 1), ('lon', 1)]: ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0, 1]
        z = ds.createVariable('z', 'f8', ('z',)); z[:] = [-.8, -.5, -.2]
        temp = ds.createVariable('temp', 'f8', ('time', 'z', 'lat', 'lon')); temp.units = 'degC'; temp[:] = 5
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'find_output_files', lambda *a, **k: {'3d': str(path), '2d': None})
    server._result_inventory_cache.clear()
    response = server.app.test_client().get('/api/results/variables')
    assert response.status_code == 200
    assert response.json['geometry_3d']['horizontal_shape'] == [1, 1]
    assert response.json['geometry_3d']['single_column'] is True
    map_response = server.app.test_client().get('/api/results/2d?var=temp&time=0&level=0')
    assert map_response.status_code == 422
    assert map_response.json['reason'] == 'single_column_geometry'


def test_official_ravn_result_apis_preserve_real_column_geometry(monkeypatch):
    case = Path(__file__).resolve().parents[1] / 'build' / 'real-use-validation-20261020' / 'ravn_official_workflow' / 'baseline_run'
    if not (case / 'output.nc').exists():
        pytest.skip('official Ravn baseline fixture is unavailable')
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    client = server.app.test_client()
    inventory = client.get('/api/results/variables')
    assert inventory.status_code == 200
    assert inventory.json['geometry_3d']['single_column'] is True
    assert client.get('/api/results/2d?var=temp&time=100&level=0').status_code == 422
    profile = client.get('/api/results/profile?var=temp&time=100&i=0&j=0')
    timeseries = client.get('/api/results/timeseries?var=temp&i=0&j=0&tstride=1')
    assert profile.status_code == 200 and len(profile.json['profile']) == 32
    assert timeseries.status_code == 200 and len(timeseries.json['times']) == 5844
    column = client.get('/api/results/3d_surface?var=temp&time=100')
    assert column.status_code == 200
    assert column.json['geometry_mode'] == 'single_column'
    assert column.json['shape'] == [32, 1, 1]
    assert len(column.json['column_depth_m']) == 32
    assert column.json['depth_source'] == 'GOTM native h+z'


def test_per_layer_timeseries_includes_native_depth_centers_aligned_to_series(tmp_path, monkeypatch):
    path = tmp_path / 'output.nc'
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 2), ('sigma', 2), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0, 1]
        sigma = ds.createVariable('sigma', 'f8', ('sigma',)); sigma[:] = [-.75, -.25]
        var = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x')); var.units = 'degC'
        var[:, :, 0, 0] = [[1, 2], [3, 4]]
        hn = ds.createVariable('hn', 'f8', var.dimensions); hn.units = 'm'
        hn[:, :, 0, 0] = [[3, 9], [4, 10]]
        zc = ds.createVariable('zc', 'f8', var.dimensions); zc.units = 'm'
        zc[:, :, 0, 0] = [[-10.5, -4.5], [-10, -4]]
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy.units = 'm'; bathy[:] = 12
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'find_output_files', lambda *a, **k: {'3d': str(path), '2d': None})
    response = server.app.test_client().get(
        '/api/results/timeseries?var=temp&i=0&j=0&per_layer=1&tstride=1')
    assert response.status_code == 200, response.json
    result = response.json
    assert result['layer_center_depth_m'] == [[10.5, 12.0], [4.5, 6.0]]
    assert result['layer_center_depth_source'] == 'hn+zc'
    assert result['layer_center_depth_aggregation'] == 'exact selected model cell'
    assert len(result['times']) == len(result['series'][0]) == 2


def test_per_layer_timeseries_uses_case_bathymetry_when_output_omits_it(tmp_path, monkeypatch):
    case = tmp_path / 'case'; case.mkdir()
    path = tmp_path / 'output.nc'
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 2); ds.createDimension('y', 1)
        x = ds.createVariable('x', 'f8', ('x',)); x[:] = [10, 20]
        y = ds.createVariable('y', 'f8', ('y',)); y[:] = [30]
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy.units = 'm'; bathy[:] = [[99, 12]]
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', 1), ('sigma', 2), ('yc', 1), ('xc', 2)]:
            ds.createDimension(name, size)
        clock = ds.createVariable('time', 'f8', ('time',)); clock.units = 'hours since 2020-01-01'; clock[:] = [0]
        sigma = ds.createVariable('sigma', 'f8', ('sigma',)); sigma[:] = [-.75, -.25]
        x = ds.createVariable('xc', 'f8', ('xc',)); x[:] = [10, 20]
        y = ds.createVariable('yc', 'f8', ('yc',)); y[:] = [30]
        var = ds.createVariable('temp', 'f8', ('time', 'sigma', 'yc', 'xc')); var.units = 'degC'
        var[0, :, 0, :] = [[1, 2], [3, 4]]
        hn = ds.createVariable('hn', 'f8', var.dimensions); hn.units = 'm'
        hn[0, :, 0, :] = [[3, 3], [9, 9]]
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'find_output_files', lambda *a, **k: {'3d': str(path), '2d': None})
    response = server.app.test_client().get(
        '/api/results/timeseries?var=temp&i=1&j=0&per_layer=1&tstride=1')
    assert response.status_code == 200, response.json
    assert response.json['layer_center_depth_m'] == [[10.5], [4.5]]
    assert response.json['layer_center_depth_source'] == 'hn'
