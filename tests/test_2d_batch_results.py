"""The 2D playback batch endpoint returns bounded frames from one result read."""
import sys
import threading
from collections import Counter
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
import server
REAL_FIND_OUTPUT_FILES = server.find_output_files


@pytest.fixture
def batch_client(tmp_path, monkeypatch):
    case = tmp_path / 'case'
    case.mkdir()
    output = case / 'case.3d.nc'
    with nc.Dataset(output, 'w') as ds:
        for dim, size in [('time', 6), ('sigma', 2), ('sigma_one', 1), ('y', 2), ('x', 3)]:
            ds.createDimension(dim, size)
        time = ds.createVariable('time', 'f8', ('time',))
        time.units = 'hours since 2020-01-01 00:00:00'
        time[:] = [0, 1, 2, 3, 4, 5]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = 5
        temp = ds.createVariable('temp', 'f8', ('time', 'sigma', 'y', 'x'))
        temp[:] = np.stack([np.full((2, 2, 3), value) for value in range(10, 16)])
        surface = ds.createVariable('surface_temp', 'f8', ('time', 'y', 'x'))
        surface[:] = np.stack([np.full((2, 3), value) for value in range(20, 26)])
        single = ds.createVariable('single_layer', 'f8', ('time', 'sigma_one', 'y', 'x'))
        single[:] = np.stack([np.full((1, 2, 3), value) for value in range(30, 36)])

    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_active_case_generation', 12, raising=False)
    monkeypatch.setattr(server, 'run_status', 'idle')
    monkeypatch.setattr(server, 'find_output_files', lambda *_args: {'3d': output, '2d': None})
    opened = []
    original_nc_open = server.nc_open

    class CountedOpen:
        def __init__(self, path, mode='r'):
            self.path = path
            self.mode = mode

        def __enter__(self):
            self._ctx = original_nc_open(self.path, self.mode)
            ds = self._ctx.__enter__()
            opened.append(str(Path(self.path).resolve()))
            return ds

        def __exit__(self, *args):
            return self._ctx.__exit__(*args)

    monkeypatch.setattr(server, 'nc_open', lambda path, mode='r': CountedOpen(path, mode))
    with server._result_horizontal_geometry_cache_lock:
        server._result_horizontal_geometry_cache.clear()
    return server.app.test_client(), opened


def test_batch_reads_two_frames_once_and_returns_server_case_identity(batch_client):
    client, opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [1, 2], 'level': 1,
        'include_bathymetry': False, 'case_revision': 4, 'output_revision': 8,
    })
    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload['frames']) == {'1', '2'}
    assert payload['frames']['1']['mean'] == pytest.approx(11)
    assert payload['frames']['2']['mean'] == pytest.approx(12)
    assert payload['frames']['1']['shape'] == [2, 3]
    assert payload['case_path'].endswith('case')
    assert payload['case_generation'] == 12
    assert (
        'case_revision' not in payload and 'output_revision' not in payload
    ), 'the server must not echo client revisions as if they were validated identities'
    assert payload['result_revision']
    assert len(opened) == 1, 'single-column metadata is derived during the frame read'
    client.post('/api/results/2d_batch', json={'var': 'temp', 'times': [0, 1],
                                               'expected_case_path': payload['case_path']})
    assert len(opened) == 2, 'each batch uses one Dataset open even before geometry cache warmup'


@pytest.mark.parametrize('times', [[], [1, 2, 0, 3, 4], [1, 1], [-1], [6], [0, 1, 2, 3, 4]])
def test_batch_rejects_empty_duplicate_oversized_or_out_of_range_times(batch_client, times):
    client, _opened = batch_client
    response = client.post('/api/results/2d_batch', json={'var': 'temp', 'times': times})
    assert response.status_code == 400
    assert response.get_json().get('error')


def test_batch_reads_four_frames_with_one_dataset_open(batch_client):
    client, opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [1, 2, 3, 4], 'level': 1,
        'include_bathymetry': False,
    })
    assert response.status_code == 200
    frames = response.get_json()['frames']
    assert list(frames) == ['1', '2', '3', '4']
    assert [frames[str(time)]['mean'] for time in range(1, 5)] == pytest.approx([11, 12, 13, 14])
    assert len(opened) == 1, 'the four-frame batch should read all slices through one Dataset open'


def test_cold_batch_route_opens_single_candidate_once_for_discovery_and_once_for_frames(
        batch_client, monkeypatch):
    client, opened = batch_client
    monkeypatch.setattr(server, 'find_output_files', REAL_FIND_OUTPUT_FILES)
    with server._output_selection_cache_lock:
        server._output_selection_cache.clear()
    opened.clear()

    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [1, 2, 3, 4], 'level': 1,
        'include_bathymetry': False,
    })
    assert response.status_code == 200
    frames = response.get_json()['frames']
    assert [frames[str(time)]['mean'] for time in range(1, 5)] == pytest.approx([11, 12, 13, 14])
    assert len(opened) == 2, 'cold discovery opens the sole candidate once, then reads all frames once'

    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [3, 4], 'level': 1,
        'include_bathymetry': False,
    })
    assert response.status_code == 200
    frames = response.get_json()['frames']
    assert [frames[str(time)]['mean'] for time in (3, 4)] == pytest.approx([13, 14])
    assert len(opened) == 3, 'warm file selection cache should leave only the frame Dataset open'


@pytest.mark.parametrize('candidate_count', [2, 3, 4])
def test_cold_batch_route_opens_each_real_candidate_once_then_selected_file_for_frames(
        batch_client, monkeypatch, candidate_count):
    client, opened = batch_client
    case = Path(server.active_case_path)
    candidates = [case / 'case.3d.nc']
    monkeypatch.setattr(server, 'find_output_files', REAL_FIND_OUTPUT_FILES)
    for rank in range(1, candidate_count):
        suffix = '2d' if candidate_count == 4 and rank == candidate_count - 1 else '3d'
        path = case / f'candidate_{rank:02d}.{suffix}.nc'
        with nc.Dataset(path, 'w') as ds:
            ds.createDimension('time', 6)
            ds.createDimension('y', 2)
            ds.createDimension('x', 3)
            if suffix == '3d':
                ds.createDimension('sigma', 2)
                dims = ('time', 'sigma', 'y', 'x')
                values = np.stack([
                    np.full((2, 2, 3), rank * 100 + frame)
                    for frame in range(6)
                ])
            else:
                dims = ('time', 'y', 'x')
                values = np.stack([
                    np.full((2, 3), rank * 100 + frame)
                    for frame in range(6)
                ])
            time = ds.createVariable('time', 'f8', ('time',))
            time.units = 'hours since 2020-01-01 00:00:00'
            time[:] = np.arange(6) + rank * 10
            ds.createVariable('temp', 'f8', dims)[:] = values
        candidates.append(path)

    with server._output_selection_cache_lock:
        server._output_selection_cache.clear()
    opened.clear()
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [1, 2, 3, 4], 'level': 0,
        'include_bathymetry': False,
    })
    assert response.status_code == 200
    frames = response.get_json()['frames']
    expected_rank = candidate_count - 1
    assert frames['1']['mean'] == pytest.approx(expected_rank * 100 + 1), (
        'the latest native time axis should continue to select the owning output file'
    )

    resolved_candidates = [str(path.resolve()) for path in candidates]
    counts = Counter(opened)
    assert set(counts) == set(resolved_candidates)
    selected = str(candidates[-1].resolve())
    assert counts[selected] == 2, 'selected candidate opens once for discovery and once for frame slices'
    assert all(counts[path] == 1 for path in resolved_candidates if path != selected), (
        'each non-selected candidate should be opened exactly once during cold discovery'
    )


def test_batch_reports_missing_variable_without_partial_frames(batch_client):
    client, _opened = batch_client
    response = client.post('/api/results/2d_batch', json={'var': 'missing', 'times': [1, 2]})
    assert response.status_code == 404
    assert response.get_json().get('error')


def test_batch_refuses_reads_while_active_result_is_locked(batch_client, monkeypatch, tmp_path):
    client, opened = batch_client
    monkeypatch.setattr(server, 'run_status', 'running')
    monkeypatch.setattr(server, 'run_case_path', server.active_case_path)
    response = client.post('/api/results/2d_batch', json={'var': 'temp', 'times': [1, 2]})
    assert response.status_code == 409
    assert response.get_json().get('error')
    assert opened == []


def test_batch_rejects_client_case_path_mismatch_before_opening_output(batch_client, tmp_path):
    client, opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [0, 1], 'level': 0,
        'expected_case_path': str(tmp_path / 'another-case'),
    })
    assert response.status_code == 409
    assert opened == []


def test_batch_rejects_stale_server_case_generation_before_opening_output(batch_client):
    client, opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [0, 1], 'level': 0,
        'expected_case_path': str(server.active_case_path),
        'expected_case_generation': 11,
    })
    assert response.status_code == 409
    assert opened == []


@pytest.mark.parametrize('var,level', [('temp', -1), ('temp', 2),
                                       ('surface_temp', -1), ('surface_temp', 1),
                                       ('single_layer', -1), ('single_layer', 1)])
def test_batch_rejects_vertical_layers_outside_actual_variable_range(batch_client, var, level):
    client, _opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': var, 'times': [0, 1], 'level': level,
    })
    assert response.status_code == 400
    assert response.get_json().get('error')


@pytest.mark.parametrize('var,level,expected', [('temp', 0, 10), ('temp', 1, 10),
                                                ('surface_temp', 0, 20), ('single_layer', 0, 30)])
def test_batch_accepts_valid_boundaries_for_multilayer_and_single_layer_fields(batch_client, var, level, expected):
    client, _opened = batch_client
    response = client.post('/api/results/2d_batch', json={
        'var': var, 'times': [0, 1], 'level': level,
    })
    assert response.status_code == 200
    assert response.get_json()['frames']['0']['mean'] == pytest.approx(expected)


def test_batch_rejects_when_active_case_changes_during_file_read(batch_client, monkeypatch, tmp_path):
    client, _opened = batch_client
    old_case = server.active_case_path
    other_case = tmp_path / 'other-case'
    other_case.mkdir()
    original_read = server.get_2d_fields

    def switch_case_after_read(*args, **kwargs):
        result = original_read(*args, **kwargs)
        server.active_case_path = other_case
        server._active_case_generation += 1
        return result

    monkeypatch.setattr(server, 'get_2d_fields', switch_case_after_read)
    response = client.post('/api/results/2d_batch', json={
        'var': 'temp', 'times': [0, 1], 'level': 0,
        'expected_case_path': str(old_case), 'case_revision': 999, 'output_revision': 999,
    })
    assert response.status_code == 409
    assert response.get_json().get('error')
