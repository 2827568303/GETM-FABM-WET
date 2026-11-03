import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import case_scan


def test_scan_finds_markers_and_skips_lone_fabm(tmp_path):
    home = tmp_path / 'home'
    documents = home / 'Documents'
    lake = documents / '湖泊' / 'Dianchi'
    lake.mkdir(parents=True)
    (lake / 'getm.inp').write_text('&getm_nml\n/\n', encoding='utf-8')
    dat_case = documents / 'old'
    dat_case.mkdir()
    (dat_case / 'getm.dat').write_text('getm', encoding='ascii')
    gotm = documents / 'column'
    gotm.mkdir()
    (gotm / 'gotm.yaml').write_text('gotm: {}\n', encoding='utf-8')
    (gotm / 'output.nc').write_bytes(b'not-read')
    lone = documents / 'notes'
    lone.mkdir()
    (lone / 'fabm.yaml').write_text('instances: {}\n', encoding='utf-8')
    (documents / '.hidden-case').mkdir()
    ((documents / '.hidden-case') / 'getm.inp').write_text('x', encoding='ascii')

    roots, _drives = case_scan.default_roots([], home=home, local_app_data=None)
    found = case_scan.scan_once(roots, [], max_seconds=5)['found']
    paths = {item['path'] for item in found}
    assert str(lake) in paths
    assert str(dat_case) in paths
    assert str(gotm) in paths
    assert str(lone) not in paths
    assert all('.hidden-case' not in item['path'] for item in found)


def test_scan_can_be_cancelled(tmp_path):
    import threading
    root = tmp_path / 'Documents'
    root.mkdir()
    cancel = threading.Event()
    cancel.set()
    result = case_scan.scan_once([root], [], cancel=cancel, max_seconds=5)
    assert result['cancelled'] is True
