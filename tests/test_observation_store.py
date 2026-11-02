from pathlib import Path
import sys

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_case_isolation_preview_hash_apply_and_restore(tmp_path):
    from observation_store import ObservationStore
    store = ObservationStore(tmp_path)
    f = tmp_path / 'input.csv'
    f.write_text('time,value,depth_m,unit,variable,lake_id,station_id\n2020-01-01,2,1,degC,T,L,S\n')
    preview = store.preview('case-a', [f])
    assert preview['files'][0]['sha256']
    store.apply('case-a', preview, {})
    assert store.load('case-a')['records'][0]['lake_id'] == 'L'
    store.save('case-b', {'records': []})
    assert store.load('case-b')['records'] == []
    assert store.load('case-a')['records']
    store.save('case-a', {'records': [{'time': '2020-01-02', 'value': 3}]})
    assert store.load('case-a')['records'][0]['value'] == 3
    f.write_text(f.read_text() + '\n')
    with pytest.raises(ValueError, match='changed'):
        store.apply('case-a', preview, {})
    store.restore('case-a')
    assert store.load('case-a')['records']


def test_store_rejects_missing_case_and_path_escape(tmp_path):
    from observation_store import ObservationStore
    store = ObservationStore(tmp_path / 'root')
    with pytest.raises(ValueError, match='case'):
        store.save('', {'records': []})
    outside = tmp_path / 'outside.csv'
    outside.write_text('')
    assert store.preview('Lake Luoma', [outside])['case_id'] == 'Lake Luoma'
    assert not (tmp_path / 'root' / 'Lake Luoma').exists()


def test_preview_signs_mapping_and_records_and_cross_file_conflicts_are_isolated(tmp_path):
    from observation_store import ObservationStore
    storage = tmp_path / 'store'
    selected = tmp_path / 'selected'; selected.mkdir()
    a = selected / 'a.csv'; b = selected / 'b.csv'
    header = 'time,value,depth_m,unit,variable,lake_id,station_id\n'
    a.write_text(header + '2020-01-01,1,2,degC,T,L,S\n')
    b.write_text(header + '2020-01-01,3,2,degC,T,L,S\n')
    store = ObservationStore(storage)
    maps = {'a.csv': {'lake_id': 'L'}, 'b.csv': {'lake_id': 'L'}, '__version__': 'm1'}
    preview = store.preview('Lake Luoma', [a, b], maps)
    tampered = dict(preview); tampered['files'] = [dict(preview['files'][0], records=[]), preview['files'][1]]
    with pytest.raises(ValueError, match='modified'):
        store.apply('Lake Luoma', tampered, maps)
    changed_maps = {'a.csv': {'lake_id': 'OTHER'}, 'b.csv': {'lake_id': 'L'}, '__version__': 'm2'}
    with pytest.raises(ValueError, match='mapping changed'):
        store.apply('Lake Luoma', preview, changed_maps)
    applied = store.apply('Lake Luoma', preview, maps)
    assert applied['records'] == []
    assert any(d['reason'] == 'conflicting_duplicate' for d in applied['diagnostics'])


def test_load_does_not_create_case_and_calibration_symlink_is_rejected(tmp_path):
    from observation_store import ObservationStore
    store = ObservationStore(tmp_path / 'root')
    assert store.load('absent')['records'] == []
    assert not (tmp_path / 'root' / 'absent').exists()
    outside = tmp_path / 'outside'; outside.mkdir()
    case = tmp_path / 'root' / 'case'; case.mkdir()
    try:
        (case / 'calibration').symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip('directory symlinks unavailable on this Windows configuration')
    with pytest.raises(ValueError, match='escapes'):
        store.save('case', {'records': []})


def test_expired_preview_is_rejected_before_writing(tmp_path):
    from observation_store import ObservationStore
    f = tmp_path / 'input.csv'
    f.write_text('time,value,depth_m,unit,variable\n2020-01-01,1,1,degC,T\n')
    store = ObservationStore(tmp_path / 'store', preview_ttl_seconds=-1)
    preview = store.preview('case', [f])
    with pytest.raises(ValueError, match='expired'):
        store.apply('case', preview)
    assert store.load('case')['records'] == []


def test_signed_json_numbers_are_browser_stable_but_strings_remain_distinct():
    from observation_store import ObservationStore
    canonical = ObservationStore._canonical
    assert canonical({'gap': 1.0}) == canonical({'gap': 1})
    assert canonical({'value': 1e-7}) == canonical({'value': 0.0000001})
    assert canonical({'value': -0.0}) == canonical({'value': 0})
    assert canonical({'value': 1}) != canonical({'value': '1'})
    assert canonical({'value': True}) != canonical({'value': 1})
