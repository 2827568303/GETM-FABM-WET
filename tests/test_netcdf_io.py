import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))
import netcdf_io
from netcdf_io import open_dataset


def test_non_ascii_case_path_read_write_append(tmp_path):
    folder = tmp_path / '耦合湖泊示例'
    folder.mkdir()
    path = folder / 'bathymetry.nc'
    with open_dataset(path, 'w') as ds:
        ds.createDimension('x', 2)
        ds.createVariable('depth', 'f4', ('x',))[:] = [1, 2]
    with open_dataset(path, 'r+') as ds:
        ds.variables['depth'][1] = 4
    with open_dataset(path) as ds:
        np.testing.assert_array_equal(ds.variables['depth'][:], [1, 4])


def test_acp_check_rejects_unencodable_windows_path(monkeypatch):
    monkeypatch.setattr(netcdf_io.os, 'name', 'nt')
    monkeypatch.setattr(netcdf_io, 'filename_encoding', lambda: 'ascii')
    assert netcdf_io.path_is_acp_compatible(r'D:\cases\NativeTest')
    assert not netcdf_io.path_is_acp_compatible('D:\\测试\\3DWET\\case')


def test_open_dataset_passes_code_page_encoding(monkeypatch):
    seen = {}

    class Fake:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_dataset(path, mode='r', **kwargs):
        seen['path'] = path
        seen['encoding'] = kwargs.get('encoding')
        return Fake()

    monkeypatch.setattr(netcdf_io.netCDF4, 'Dataset', fake_dataset)
    monkeypatch.setattr(netcdf_io, 'filename_encoding', lambda: 'cp936')
    monkeypatch.setattr(netcdf_io, 'native_equivalent', lambda path: path)
    open_dataset('THEORETICAL_LAKE.2d.0000.nc')
    assert seen['encoding'] == 'cp936'
    assert seen['path'].endswith('THEORETICAL_LAKE.2d.0000.nc')


def test_solver_cwd_uses_ascii_junction_when_path_is_not_acp(monkeypatch, tmp_path):
    target = tmp_path / '测试'
    target.mkdir()
    monkeypatch.setattr(netcdf_io.os, 'name', 'nt')
    monkeypatch.setattr(netcdf_io, 'path_is_acp_compatible', lambda path: False)
    link = tmp_path / 'j-ascii'
    monkeypatch.setattr(netcdf_io, '_ascii_junction', lambda path: link)
    cwd, created = netcdf_io.prepare_solver_cwd(target)
    assert cwd == str(link)
    assert created == link
    removed = []
    monkeypatch.setattr(netcdf_io.os, 'rmdir', lambda path: removed.append(path))
    netcdf_io.release_solver_cwd(link)
    assert [Path(path).name for path in removed] == ['j-ascii']
