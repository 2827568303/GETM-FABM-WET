"""Static 3D geometry is reused only for the same case/source revisions."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_static_geometry_key_invalidates_on_case_source_or_sampling_change(tmp_path):
    from scientific_geometry import static_3d_geometry_key

    case_a = tmp_path / 'case-a'
    case_b = tmp_path / 'case-b'
    case_a.mkdir(); case_b.mkdir()
    output = case_a / 'output.nc'
    bathymetry = case_a / 'bathymetry.nc'
    output.write_bytes(b'coordinates version one')
    bathymetry.write_bytes(b'static depth version one')

    key = static_3d_geometry_key(case_a, output, bathymetry, (14, 21), (2, 3), 8)
    assert static_3d_geometry_key(case_a, output, bathymetry, (14, 21), (2, 3), 8) == key
    assert static_3d_geometry_key(case_b, output, bathymetry, (14, 21), (2, 3), 8) != key
    assert static_3d_geometry_key(case_a, output, bathymetry, (14, 21), (1, 3), 8) != key

    bathymetry.write_bytes(b'static depth version two, changed')
    assert static_3d_geometry_key(case_a, output, bathymetry, (14, 21), (2, 3), 8) != key
    bathymetry.write_bytes(b'static depth version one')
    output.write_bytes(b'coordinates version two, changed')
    assert static_3d_geometry_key(case_a, output, bathymetry, (14, 21), (2, 3), 8) != key


def test_static_geometry_lru_builds_once_and_obeys_capacity():
    from scientific_geometry import Static3DGeometryCache

    cache = Static3DGeometryCache(max_entries=2)
    builds = []
    builder = lambda value: lambda: builds.append(value) or {'value': value}
    first = cache.get_or_build(('case-a', 'revision-1'), builder('first'))
    again = cache.get_or_build(('case-a', 'revision-1'), builder('unused'))
    assert again is first and builds == ['first']
    cache.get_or_build(('case-a', 'revision-2'), builder('changed bathymetry'))
    cache.get_or_build(('case-b', 'revision-1'), builder('other case'))
    assert builds == ['first', 'changed bathymetry', 'other case']
    assert cache.info() == {'entries': 2, 'max_entries': 2, 'hits': 1, 'misses': 3}
