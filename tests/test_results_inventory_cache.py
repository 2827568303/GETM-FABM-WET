"""The result inventory should reuse a revision-identical NetCDF summary."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_inventory_reuses_repeated_reads_and_invalidates_case_and_output_revisions(tmp_path, monkeypatch):
    import server

    case_a = tmp_path / 'case-a'; case_a.mkdir()
    case_b = tmp_path / 'case-b'; case_b.mkdir()
    a2d, a3d = case_a / 'result.2d.nc', case_a / 'result.3d.nc'
    b2d, b3d = case_b / 'result.2d.nc', case_b / 'result.3d.nc'
    for path in (a2d, a3d, b2d, b3d): path.write_bytes(path.name.encode())

    reads = []
    def find_outputs(case, _variable=None):
        return {'2d': case / 'result.2d.nc', '3d': case / 'result.3d.nc', 'legacy3d': None}
    def variable_list(path):
        reads.append(('variables', Path(path).resolve()))
        return [{'name': 'temp', 'time_axis': str(Path(path).resolve())}]
    def timesteps(path):
        reads.append(('timesteps', Path(path).resolve()))
        return 2
    def labels(path, max_items=None):
        reads.append(('labels', Path(path).resolve()))
        return ['t0', 't1']
    def geometry(path):
        reads.append(('geometry', Path(path).resolve()))
        return {'horizontal_shape': [1, 2], 'path': str(Path(path).resolve())}

    monkeypatch.setattr(server, 'find_output_files', find_outputs)
    monkeypatch.setattr(server, 'get_variable_list', variable_list)
    monkeypatch.setattr(server, 'get_ntimesteps', timesteps)
    monkeypatch.setattr(server, '_nc_time_labels', labels)
    # These cache tests exercise inventory invalidation, not NetCDF parsing.
    # The files above are deliberately tiny revision markers, not NetCDF files.
    monkeypatch.setattr(server, '_result_horizontal_geometry', geometry)
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'active_case_path', case_a)
    client = server.app.test_client()

    first = client.get('/api/results/variables').get_json()
    reads_after_first = len(reads)
    repeated = client.get('/api/results/variables').get_json()
    assert repeated == first
    assert len(reads) == reads_after_first, 'same case and file revisions should reuse the inventory'

    a3d.write_bytes(b'rebuilt output, new revision')
    changed_output = client.get('/api/results/variables').get_json()
    assert changed_output == first
    assert len(reads) > reads_after_first, 'changed output file revision must rebuild the inventory'
    reads_after_revision = len(reads)

    monkeypatch.setattr(server, 'active_case_path', case_b)
    changed_case = client.get('/api/results/variables').get_json()
    assert changed_case['2d'][0]['time_axis'] == str(b2d.resolve())
    assert len(reads) > reads_after_revision, 'case identity must prevent cross-case inventory reuse'


def test_inventory_cache_bounds_entries_and_invalidates_when_missing_output_appears(tmp_path):
    from result_inventory_cache import ResultInventoryCache, inventory_key

    case = tmp_path / 'case'; case.mkdir()
    output = case / 'late-output.3d.nc'
    files = {'2d': None, '3d': output, 'legacy3d': None}
    before = inventory_key(case, files)
    cache = ResultInventoryCache(max_entries=2)
    cache.put(before, {'3d': []})
    assert cache.get(before) == {'3d': []}
    output.write_bytes(b'created')
    after = inventory_key(case, files)
    assert after != before
    cache.put(after, {'3d': [1]})
    cache.put(('third',), {'3d': [2]})
    assert cache.info()['entries'] == 2
    assert cache.info()['max_entries'] == 2
    assert cache.get(before) is None, 'the least recently used entry should be evicted'


def test_inventory_built_during_case_switch_is_not_cached(tmp_path, monkeypatch):
    """A cold inventory must not be retained under the case captured before a switch."""
    import server

    case_a = tmp_path / 'case-a'; case_a.mkdir()
    case_b = tmp_path / 'case-b'; case_b.mkdir()
    outputs = {}
    for case in (case_a, case_b):
        outputs[case] = {kind: case / f'result.{kind}.nc' for kind in ('2d', '3d')}
        for path in outputs[case].values():
            path.write_bytes(case.name.encode())

    reads = []
    switched = False
    def find_outputs(case, _variable=None):
        case = Path(case).resolve()
        return {'2d': outputs[case]['2d'], '3d': outputs[case]['3d'], 'legacy3d': None}
    def variable_list(path):
        nonlocal switched
        reads.append(Path(path).resolve())
        annotation_case = Path(server.active_case_path).name
        if not switched:
            switched = True
            server.active_case_path = case_b
        return [{'name': 'temp', 'annotated_case': annotation_case,
                 'time_axis': str(Path(path).resolve())}]

    monkeypatch.setattr(server, 'find_output_files', find_outputs)
    monkeypatch.setattr(server, 'get_variable_list', variable_list)
    monkeypatch.setattr(server, 'get_ntimesteps', lambda _path: 1)
    monkeypatch.setattr(server, '_nc_time_labels', lambda _path, max_items=None: ['t0'])
    # Keep this focused on inventory cache races; outputs are revision markers.
    monkeypatch.setattr(server, '_result_horizontal_geometry', lambda path: {'path': str(path)})
    monkeypatch.setattr(server, '_output_locked', lambda: False)
    monkeypatch.setattr(server, 'active_case_path', case_a)
    server._result_inventory_cache.clear()
    client = server.app.test_client()

    client.get('/api/results/variables')
    reads_after_race = len(reads)
    assert reads_after_race > 0

    # Return to A: the raced response must not be found under A's inventory key.
    monkeypatch.setattr(server, 'active_case_path', case_a)
    rebuilt = client.get('/api/results/variables').get_json()
    assert len(reads) > reads_after_race, 'inventory built across a case switch must not be cached'
    assert all(item['annotated_case'] == case_a.name for item in rebuilt['2d'] + rebuilt['3d'])


def test_current_case_endpoint_exposes_persisted_backend_case_without_mutating_it(tmp_path, monkeypatch):
    import server

    case = tmp_path / 'restored-case'; case.mkdir()
    marker = tmp_path / 'case-state.json'
    marker.write_text('unchanged', encoding='utf-8')
    monkeypatch.setattr(server, 'active_case', case.name)
    monkeypatch.setattr(server, 'active_case_path', case)
    monkeypatch.setattr(server, '_active_case_generation', 7)
    monkeypatch.setattr(server, '_LAST_CASE_FILE', marker)

    response = server.app.test_client().get('/api/case/current')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['case_name'] == case.name
    assert payload['case_path'] == str(case.resolve())
    assert payload['case_generation'] == 7
    assert payload['read_only'] is False
    assert payload['case_type'] == 'getm'
    assert payload['native_time_range'] is None
    assert payload['native_column_variables'] is None
    assert marker.read_text(encoding='utf-8') == 'unchanged'
