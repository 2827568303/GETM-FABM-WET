"""Result controls must bind each variable to its actual output calendar."""
import sys
from pathlib import Path

import netCDF4 as nc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_inventory_keeps_source_axis_and_physical_layer_count(tmp_path, monkeypatch):
    import server
    path = tmp_path / 'native.3d.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.model = 'GETM'
        for name, size in [('time', 3), ('sigma', 4), ('y', 1), ('x', 1)]:
            ds.createDimension(name, size)
        t = ds.createVariable('time', 'f8', ('time',)); t.units = 'seconds since 2026-12-31 23:00:00'; t[:] = [0, 1800, 5400]
        ds.createVariable('sigma', 'f8', ('sigma',))[:] = [-1, -.67, -.33, 0]
        v = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'), fill_value=-9999)
        v[:] = 12; v[:, 0] = -9999
    monkeypatch.setattr(server, 'active_case_path', tmp_path)
    metadata = server.get_variable_list(path)[0]
    assert metadata['ntimesteps'] == 3
    assert metadata['nlev'] == 3
    assert metadata['time_axis'] == str(path.resolve())
    response = server.app.test_client().get('/api/results/variables').json
    assert response['time_axes'][metadata['time_axis']] == [
        '2026-12-31 23:00:00', '2026-12-31 23:30:00', '2027-01-01 00:30:00']


def test_time_labels_do_not_truncate_real_output(tmp_path):
    import server
    path = tmp_path / 'long.nc'
    with nc.Dataset(path, 'w') as ds:
        ds.createDimension('time', 2002)
        t = ds.createVariable('time', 'f8', ('time',)); t.units = 'hours since 2026-01-01'; t[:] = range(2002)
    labels = server._nc_time_labels(path)
    assert len(labels) == 2002
    assert labels[1] == '2026-01-01 01:00:00'
