from pathlib import Path
import hashlib
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_official_obs_preserves_full_semantics_and_marks_outliers(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'TEMP.obs'
    raw = b'2006-07-11 10:30:00 -14 72\n1975-10-26 00:00:00 -99 1.2\n'
    path.write_bytes(raw)
    result = parse_observations(path, {'lake_id': 'ravn', 'variable': 'TEMP', 'unit': 'degC', 'review_depth_max': 32.65})
    a, b = sorted(result['records'], key=lambda r: r['source_line'])
    assert a['time'] == '2006-07-11 10:30:00' and a['time_basis'] == 'source_naive'
    assert a['depth_m'] == 14 and a['source_line'] == 1 and a['source_sha256'] == hashlib.sha256(raw).hexdigest()
    assert a['source_depth'] == '-14' and a['source_value'] == '72'
    assert a['value'] == 72 and 'physical_range_review' in a['quality']
    assert b['depth_m'] == 99 and 'depth_outside_review_range' in b['quality']


def test_obs_requires_explicit_variable_and_unit_instead_of_filename_inference(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'TEMP.obs'
    path.write_text('2006-07-11 10:30:00 -14 12.5\n', encoding='utf-8')
    missing = parse_observations(path)
    assert missing['records'] == []
    assert missing['diagnostics'][0]['reason'] == 'explicit_variable_mapping_required'
    missing_unit = parse_observations(path, {'variable': 'temp'})
    assert missing_unit['records'] == []
    assert missing_unit['diagnostics'][0]['reason'] == 'explicit_unit_mapping_required'


def test_csv_and_xlsx_keep_metadata_and_report_bad_rows(tmp_path):
    from observations import parse_observations
    csv = tmp_path / 'x.csv'
    csv.write_text('time,value,depth_m,unit,variable,lake_id,station_id,quality\n2020-01-01,2,10,mg/L,DO,L1,S1,ok\n2020-01-02,NaN,0,mg/L,DO,L1,S1,ok\nbad,1,0,mg/L,DO,L1,S1,ok\n', encoding='utf-8')
    result = parse_observations(csv)
    assert result['records'][0]['station_id'] == 'S1' and result['records'][0]['depth_m'] == 10
    assert [d['source_line'] for d in result['diagnostics']] == [3, 4]
    assert all(d['reason'] for d in result['diagnostics'])


def test_csv_custom_observation_point_column_is_preserved_for_calibration_pairing(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'obs.csv'
    path.write_text('when,value,depth,point\n2020-01-01,2,5,field-station-7\n', encoding='utf-8')
    result = parse_observations(path, {'time_column': 'when', 'depth_m_column': 'depth',
                                       'point_id_column': 'point', 'unit': 'degC', 'variable': 'temp'})
    assert result['records'][0]['point_id'] == 'field-station-7'


def test_wide_csv_supports_explicit_late_header_value_column_and_constant_depth(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'official-profile.csv'
    preamble = ''.join(f'metadata line {line}\n' for line in range(1, 70))
    raw = (preamble + 'TIMESTAMP,TW_-1.0m,TW_-2.0m\n'
           '2024-06-01T12:00:00,17.25,16.80\n').encode('utf-8')
    path.write_bytes(raw)

    result = parse_observations(path, {
        'header_row': 70,
        'time_column': 'TIMESTAMP',
        'value_column': 'TW_-1.0m',
        'depth_m_mode': 'constant',
        'depth_m_constant': 1.0,
        'unit': 'degC',
        'variable': 'temp',
    })

    assert len(result['records']) == 1
    record = result['records'][0]
    assert (record['time'], record['time_basis'], record['value'], record['depth_m']) == (
        '2024-06-01 12:00:00', 'source_naive', 17.25, 1.0)
    assert (record['unit'], record['variable'], record['source_line']) == ('degC', 'temp', 71)
    assert record['source_value'] == '17.25'
    assert record['source_row'] == {
        'TIMESTAMP': '2024-06-01T12:00:00', 'TW_-1.0m': '17.25', 'TW_-2.0m': '16.80'}
    assert record['sources'][0]['source_line'] == 71
    assert path.read_bytes() == raw


def test_duplicate_conflict_detection_is_full_key(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'x.csv'
    path.write_text('time,value,depth_m,unit,variable,lake_id,station_id\n2020-01-01,1,2,mg/L,DO,L,S\n2020-01-01,1,2,mg/L,DO,L,S\n2020-01-01,3,3,mg/L,DO,L,S\n2020-01-01,4,3,mg/L,DO,L,S\n', encoding='utf-8')
    result = parse_observations(path)
    assert len(result['records']) == 1
    assert len(result['records'][0]['sources']) == 2
    assert any(d['reason'] == 'conflicting_duplicate' for d in result['diagnostics'])


def test_xlsx_retains_columns_and_nonfinite_rows_are_rejected(tmp_path):
    from openpyxl import Workbook
    from observations import parse_observations
    path = tmp_path / 'x.xlsx'
    book = Workbook(); sheet = book.active
    sheet.append(['time', 'value', 'depth_m', 'unit', 'variable', 'lake_id', 'station_id', 'quality'])
    sheet.append(['2020-01-01 12:00', 4, 7, 'ug/L', 'CHLA', 'L', 'S', 'estimated'])
    sheet.append(['2020-01-02', 'NaN', 0, 'ug/L', 'CHLA', 'L', 'S', 'bad'])
    book.save(path)
    result = parse_observations(path)
    assert result['records'][0]['depth_m'] == 7
    assert result['records'][0]['quality'] == ['estimated']
    assert any(d['reason'] == 'non_finite_value' for d in result['diagnostics'])


def test_csv_negative_depth_needs_explicit_sign_mapping_and_review_limit(tmp_path):
    from observations import parse_observations
    path = tmp_path / 'z.csv'
    path.write_text('time,value,depth_m,unit,variable\n2020-01-01,1,-99,mg/L,PO4\n', encoding='utf-8')
    rejected = parse_observations(path)
    assert not rejected['records']
    assert rejected['diagnostics'][0]['reason'] == 'negative_depth_requires_downward_sign_mapping'
    accepted = parse_observations(path, {'depth_sign': 'negative_down', 'review_depth_max': 32.0})
    assert accepted['records'][0]['depth_m'] == 99
    assert 'depth_outside_review_range' in accepted['records'][0]['quality']
    assert accepted['diagnostics'][0]['reason'] == 'quality_review'


def test_duplicate_fold_unions_quality_flags_independent_of_input_order():
    from observations import merge_observation_records
    good = {'lake_id': 'L', 'station_id': 'S', 'variable': 'T', 'time': '2020-01-01',
            'depth_m': 2, 'value': 4, 'unit': 'degC', 'quality': [], 'quality_flags': [],
            'sources': [{'source_line': 1}]}
    suspect = {**good, 'quality': ['physical_range_review'],
               'quality_flags': ['physical_range_review'], 'sources': [{'source_line': 2}]}
    a, _ = merge_observation_records([good, suspect])
    b, _ = merge_observation_records([suspect, good])
    assert a[0]['quality_flags'] == b[0]['quality_flags'] == ['physical_range_review']
    assert a[0]['quality'] == b[0]['quality'] == ['physical_range_review']
    assert a[0]['sources'] == b[0]['sources'] == [{'source_line': 1}, {'source_line': 2}]
