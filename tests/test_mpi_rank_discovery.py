import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / '3DWET' / 'app'
sys.path.insert(0, str(APP))
from mpi_runner import merge_case_rank_outputs


def test_missing_rank_family_names_the_work_directory(tmp_path):
    case = tmp_path / '测试' / '.NativeTest.mpi-6ktd_g8l'
    case.mkdir(parents=True)
    (case / 'bathymetry.nc').write_bytes(b'not a netcdf')
    (case / 'notes.txt').write_text('kept', encoding='utf-8')
    with pytest.raises(RuntimeError, match='notes.txt') as caught:
        merge_case_rank_outputs(case, 2)
    assert 'THEORETICAL_LAKE' not in str(caught.value) or 'Directory names' in str(caught.value)
    assert '.NativeTest.mpi-6ktd_g8l' in str(caught.value)


def test_existing_shard_is_opened_with_code_page_helper(tmp_path, monkeypatch):
    case = tmp_path / '测试'
    case.mkdir()
    (case / 'bathymetry.nc').write_bytes(b'x')
    shard = case / 'THEORETICAL_LAKE.2d.0000.nc'
    shard.write_bytes(b'x')
    opened = []

    def fake_open(path, mode='r', **kwargs):
        opened.append(Path(path).name)
        raise FileNotFoundError(2, 'No such file or directory', str(path))

    monkeypatch.setattr('netcdf_io.open_dataset', fake_open)
    with pytest.raises(RuntimeError, match='系统代码页'):
        merge_case_rank_outputs(case, 1)
    assert opened == ['THEORETICAL_LAKE.2d.0000.nc']
