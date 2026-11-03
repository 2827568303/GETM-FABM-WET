"""Companion 3D outputs contribute variables to the result inventory."""
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_inventory_merges_companion_variables_and_invalidates_on_companion_revision(
        tmp_path, monkeypatch):
    import server

    case = tmp_path / 'erken'; case.mkdir()
    preferred = case / 'output.nc'
    companion = case / 'ERKEN_USER_WORKFLOW_2026_WET.3d.nc'
    from test_output_selection import output
    output(preferred, ['temp'])
    output(companion, ['temp', 'greens_cohort2_sDW'])

    def find_outputs(_case, _variable=None):
        return {'2d': None, '3d': preferred, 'legacy3d': preferred,
                '3d_candidates': [preferred, companion]}

    reads = []
    def variable_list(path):
        path = Path(path).resolve()
        reads.append(path)
        if path == preferred.resolve():
            return [{'name': 'temp', 'time_axis': str(path)},
                    {'name': 'greens_sDW', 'time_axis': str(path)}]
        return [{'name': 'temp', 'time_axis': str(path)},
                {'name': 'greens_cohort2_sDW', 'time_axis': str(path)}]

    labels_read = []
    def labels(path, max_items=None):
        path = Path(path).resolve()
        labels_read.append(path)
        return ['preferred-t0'] if path == preferred.resolve() else ['companion-t0', 'companion-t1']

    monkeypatch.setattr(server, 'find_output_files', find_outputs)
    monkeypatch.setattr(server, 'get_variable_list', variable_list)
    monkeypatch.setattr(server, 'get_ntimesteps', lambda _path: 1)
    monkeypatch.setattr(server, '_nc_time_labels', labels)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'active_case_path', case)
    server._result_inventory_cache.clear()
    client = server.app.test_client()

    first = client.get('/api/results/variables').get_json()
    by_name = {item['name']: item for item in first['3d']}
    assert by_name['temp']['time_axis'] == str(preferred.resolve())
    assert by_name['greens_cohort2_sDW']['time_axis'] == str(companion.resolve())
    assert first['time_axes'][str(companion.resolve())] == ['companion-t0', 'companion-t1']

    reads_before_revision = len(reads)
    # An in-place touch can land on the same timestamp. Advance the revision
    # explicitly so the inventory must observe the companion change.
    revised_ns = companion.stat().st_mtime_ns + 1_000_000_000
    os.utime(companion, ns=(revised_ns, revised_ns))
    revised = client.get('/api/results/variables').get_json()
    assert 'greens_cohort2_sDW' in {item['name'] for item in revised['3d']}
    assert len(reads) > reads_before_revision, 'companion revision must invalidate inventory cache'


def test_find_output_files_preserves_preferred_source_and_exposes_valid_companions(tmp_path):
    import netCDF4 as nc
    from test_output_selection import load_function, output

    preferred = tmp_path / 'output/output.nc'
    companion = tmp_path / 'output/ERKEN_USER_WORKFLOW_2026_WET.3d.nc'
    output(preferred, ['temp'])
    output(companion, ['temp', 'greens_cohort2_sDW'])

    files = load_function()(tmp_path)
    assert files['3d'] == preferred
    assert files['3d_candidates'] == [preferred, companion]
