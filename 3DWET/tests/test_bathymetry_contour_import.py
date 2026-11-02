import io
import sys
from pathlib import Path

import numpy as np
import shapefile
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))

@pytest.fixture(autouse=True)
def isolate_preprocess_server_case_state(monkeypatch):
    import server

    # These uploads are independent preprocessing requests. A selected C-drive
    # case from another test must not make the global write guard reject them.
    monkeypatch.setattr(server, 'active_case_path', None)
    monkeypatch.setattr(server, 'active_case_read_only', None)
    monkeypatch.setattr(server, 'active_case_kind_path', None)
    monkeypatch.setattr(server, '_preprocess_cache', {
        'boundary': {}, 'bathymetry': {}, 'grid': {},
    })


def _contour_files(tmp_path):
    base = tmp_path / 'erken_contours'
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYLINE)
    writer.field('OBJECTID', 'N', decimal=0)
    writer.field('CONTOUR', 'N', decimal=2)
    writer.line([[(-10, 0), (0, 0), (10, 0)]])
    writer.record(1, 5.0)
    writer.line([[(-10, 10), (0, 10), (10, 10)]])
    writer.record(2, 10.0)
    writer.close()
    return [(f'{base.name}{suffix}', (tmp_path / f'{base.name}{suffix}').read_bytes())
            for suffix in ('.shp', '.shx', '.dbf')]


def _upload(client, files, depth_field=''):
    data = {'files': [(io.BytesIO(content), name) for name, content in files]}
    if depth_field:
        data['depth_field'] = depth_field
    return client.post('/api/preprocess/bathymetry/upload', data=data,
                       content_type='multipart/form-data')


def _multipart_boundary_files(tmp_path):
    base = tmp_path / 'lake_multipart'
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYGON)
    writer.field('NAME', 'C')

    def ring(x0, y0, x1, y1, clockwise):
        points = [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]
        if not clockwise:
            points = list(reversed(points))
        return points

    # ESRI shapefile convention: exterior rings clockwise, holes counterclockwise.
    writer.poly([
        ring(18.500, 59.800, 18.510, 59.810, True),  # small island, intentionally first
        ring(18.500, 59.800, 18.600, 59.900, True),  # main lake exterior
        ring(18.540, 59.840, 18.560, 59.860, False),  # one dry hole
    ])
    writer.record('Erken')
    writer.close()
    return [(f'{base.name}{suffix}', (tmp_path / f'{base.name}{suffix}').read_bytes())
            for suffix in ('.shp', '.shx', '.dbf')]


def test_boundary_upload_keeps_all_exteriors_and_excludes_holes(tmp_path, monkeypatch):
    import server

    monkeypatch.setattr(server, '_preprocess_cache', {
        'boundary': {}, 'bathymetry': {}, 'grid': {},
    })
    data = {'crs_preset': 'epsg', 'crs_epsg': '4326',
            'files': [(io.BytesIO(content), name)
                      for name, content in _multipart_boundary_files(tmp_path)]}
    client = server.app.test_client()
    response = client.post('/api/preprocess/boundary/upload', data=data,
                           content_type='multipart/form-data')

    assert response.status_code == 200
    boundary_id = response.json['boundary_id']
    boundary = server._preprocess_cache['boundary'][boundary_id]
    assert len(boundary['polygons']) == 2
    assert sum(len(poly['holes']) for poly in boundary['polygons']) == 1
    assert len(response.json['holes_preview']) == 1

    grid = client.post('/api/preprocess/grid/generate', json={
        'boundary_id': boundary_id, 'dx': 500, 'dy': 500,
    })
    assert grid.status_code == 200
    assert grid.json['n_water_cells'] > 0
    assert grid.json['n_water_cells'] < grid.json['n_total_cells']


def test_geographic_boundary_uses_exact_utm_projection():
    import crs_utils
    import server

    coords = [(18.55, 59.85), (18.56, 59.86)]
    projected, info = server._convert_boundary_to_utm(coords, {
        'crs_type': 'geographic', 'utm_zone': 34,
    })
    transformer = crs_utils.make_transformer(
        crs_utils.WGS84, crs_utils.utm_crs(34))
    expected = [transformer.transform(*point) for point in coords]

    assert np.allclose(projected, expected, atol=0.01)
    assert info['crs_type'] == 'utm'


def test_polyline_import_requires_explicit_depth_field_and_never_guesses_objectid(tmp_path, monkeypatch):
    import server

    monkeypatch.setattr(server, '_preprocess_cache', {
        'boundary': {}, 'bathymetry': {}, 'grid': {},
    })
    response = _upload(server.app.test_client(), _contour_files(tmp_path))

    assert response.status_code == 400
    assert response.json['fields'] == ['OBJECTID', 'CONTOUR']
    assert not server._preprocess_cache['bathymetry']


def test_polyline_contours_are_sampled_and_interpolated_with_selected_field(tmp_path, monkeypatch):
    import server

    monkeypatch.setattr(server, '_preprocess_cache', {
        'boundary': {}, 'bathymetry': {}, 'grid': {},
    })
    client = server.app.test_client()
    response = _upload(client, _contour_files(tmp_path), 'CONTOUR')

    assert response.status_code == 200
    uploaded = response.json
    assert uploaded['geom_type'] == 'contour'
    assert uploaded['depth_field'] == 'CONTOUR'
    assert uploaded['source_crs']
    assert uploaded['n_features'] == 2
    assert uploaded['depth_range'] == [5.0, 10.0]
    assert uploaded['n_sample_points'] == 4
    assert len(uploaded['preview_points']) == 4
    assert all(depth in (5.0, 10.0) for depth in uploaded['preview_point_depths'])

    server._preprocess_cache['grid']['test-grid'] = {
        'nx': 3, 'ny': 3, 'mask': np.ones((3, 3), dtype=bool),
        'xc': np.array([-5.0, 0.0, 5.0]), 'yc': np.array([2.5, 5.0, 7.5]),
        'dx': 5.0, 'dy': 2.5,
    }
    interpolated = client.post('/api/preprocess/bathymetry/interpolate', json={
        'grid_id': 'test-grid', 'bathy_id': uploaded['bathy_id'], 'method': 'linear',
    })

    assert interpolated.status_code == 200
    result = interpolated.json
    assert result['n_water_cells'] == 9
    assert result['n_bathy_sample_points'] > uploaded['n_sample_points']
    assert result['depth_min'] >= 5.0
    assert result['depth_max'] <= 10.0
    assert result['depth_array'][1][1] == 7.5


def test_multipart_contour_preserves_separate_line_parts(tmp_path, monkeypatch):
    import server

    monkeypatch.setattr(server, '_preprocess_cache', {
        'boundary': {}, 'bathymetry': {}, 'grid': {},
    })
    base = tmp_path / 'disjoint_contours'
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYLINE)
    writer.field('CONTOUR', 'N', decimal=1)
    writer.line([
        [(-20, 0), (-10, 0), (0, 0)],
        [(100, 10), (110, 10), (120, 10)],
    ])
    writer.record(7.5)
    writer.close()
    files = [(f'{base.name}{suffix}', (tmp_path / f'{base.name}{suffix}').read_bytes())
             for suffix in ('.shp', '.shx', '.dbf')]

    response = _upload(server.app.test_client(), files, 'CONTOUR')

    assert response.status_code == 200
    assert len(response.json['preview_lines']) == 2
    first, second = response.json['preview_lines']
    assert max(point[0] for point in first) < min(point[0] for point in second)
    assert response.json['preview_line_depths'] == [7.5, 7.5]
