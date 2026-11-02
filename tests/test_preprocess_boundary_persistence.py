"""Uploaded lake boundaries remain available to the display after case save."""
import json
import io
import sys
from pathlib import Path

import pytest
import netCDF4 as nc
import numpy as np
import shapefile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
import server


def test_boundary_upload_keeps_exact_source_vertices_and_crs_provenance(tmp_path, monkeypatch):
    # This API is independent of the active case; isolate it from prior tests
    # that may leave a read-only or C: case selected in the process globals.
    monkeypatch.setattr(server, 'active_case_path', None)
    base = tmp_path / 'shore'
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYGON)
    writer.field('id', 'N')
    vertices = [[12.0, 55.0], [12.0, 55.1], [12.1, 55.1], [12.1, 55.0], [12.0, 55.0]]
    writer.poly([vertices]); writer.record(1); writer.close()
    (tmp_path / 'shore.prj').write_text(
        'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],'
        'PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]]', encoding='utf-8')
    uploads = [(io.BytesIO((tmp_path / f'shore{suffix}').read_bytes()), f'shore{suffix}')
               for suffix in ('.shp', '.shx', '.dbf', '.prj')]
    response = server.app.test_client().post('/api/preprocess/boundary/upload',
        data={'files': uploads, 'crs_preset': 'auto'}, content_type='multipart/form-data')
    assert response.status_code == 200
    cached = server._preprocess_cache['boundary'][response.get_json()['boundary_id']]
    assert cached['source_polygons'][0]['outer'] == vertices
    assert cached['source_crs']['wkt'].startswith('GEOGCS["GCS_WGS_1984"')
    assert cached['source_crs_selection'] == {'preset': 'auto', 'epsg': None}
    assert cached['source_files'] == ['shore.dbf', 'shore.prj', 'shore.shp', 'shore.shx']
    assert cached['polygons'][0]['outer'] != cached['source_polygons'][0]['outer']


def test_preprocess_save_persists_source_and_projected_boundary(monkeypatch, tmp_path):
    case_root = tmp_path / 'cases'
    monkeypatch.setattr(server, 'CASE_DIR', case_root)
    monkeypatch.setattr(server, 'active_case', None)
    monkeypatch.setattr(server, 'active_case_path', None)
    monkeypatch.setattr(server, '_write_bathymetry_nc_standalone', lambda *_args, **_kwargs: None)
    boundary_id, grid_id = 'bnd-test', 'grid-test'
    source_groups = [{'outer': [[12.0, 55.0], [12.1, 55.0], [12.1, 55.1]], 'holes': []}]
    projected_groups = [{'outer': [[690000.0, 6090000.0], [696000.0, 6090000.0], [696000.0, 6100000.0]], 'holes': []}]
    monkeypatch.setitem(server._preprocess_cache['boundary'], boundary_id, {
        'coords': projected_groups[0]['outer'], 'rings': [projected_groups[0]['outer']],
        'polygons': projected_groups, 'source_polygons': source_groups,
        'source_crs': {'crs_type': 'geographic', 'wkt': 'GEOGCRS["WGS 84"]'},
        'crs_info': {'crs_type': 'utm', 'utm_zone': 33, 'central_meridian': 15.0},
        'source_files': ['lake.shp', 'lake.shx', 'lake.dbf', 'lake.prj'],
    })
    monkeypatch.setitem(server._preprocess_cache['grid'], grid_id, {
        'boundary_id': boundary_id, 'depth_array': [[4.0]], 'nx': 1, 'ny': 1,
        'dx': 100.0, 'dy': 100.0, 'x0': 689950.0, 'y0': 6089950.0,
        'n_water': 1, 'crs_info': {'crs_type': 'utm'},
    })

    response = server.app.test_client().post('/api/preprocess/save', json={
        'case_name': 'BoundaryLake', 'grid_id': grid_id,
    })
    assert response.status_code == 200
    saved = json.loads((case_root / 'BoundaryLake' / 'rivers_setup.json').read_text(encoding='utf-8'))
    boundary = saved['boundary_geometry']
    assert boundary['source_polygons'] == source_groups
    assert boundary['source_crs']['wkt'] == 'GEOGCRS["WGS 84"]'
    assert boundary['projected_polygons'] == projected_groups
    assert boundary['projected_crs']['utm_zone'] == 33
    assert boundary['provenance']['files'] == ['lake.shp', 'lake.shx', 'lake.dbf', 'lake.prj']


def test_geo_grid_exposes_only_saved_projected_boundary_and_has_no_fake_fallback(tmp_path, monkeypatch):
    case = tmp_path / 'case'
    case.mkdir()
    (case / 'rivers_setup.json').write_text(json.dumps({
        'boundary_geometry': {
            'source_polygons': [{'outer': [[1, 2], [3, 4]], 'holes': []}],
            'projected_polygons': [{'outer': [[500.25, 600.5], [501.75, 600.5], [501.75, 601.25]], 'holes': []}],
            'source_crs': {'crs_type': 'projected', 'wkt': 'PROJCRS["test"]'},
            'projected_crs': {'crs_type': 'projected'},
        }
    }), encoding='utf-8')
    monkeypatch.setattr(server, 'active_case_path', case)
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 3); ds.createDimension('y', 3)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [500.25, 501.0, 501.75]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [600.5, 601.0, 601.5]
        bathy = ds.createVariable('bathymetry', 'f8', ('y', 'x')); bathy[:] = np.ones((3, 3)) * 4
        lon = ds.createVariable('lonc', 'f8', ('y', 'x')); lon[:] = np.ones((3, 3)) * 12
        lat = ds.createVariable('latc', 'f8', ('y', 'x')); lat[:] = np.ones((3, 3)) * 55
    payload = server.app.test_client().get('/api/geo/grid').get_json()
    # The map/3D payload exposes only the genuine projected coordinates.
    assert payload['authoritative_boundary']['projected_polygons'][0]['outer'][0] == [500.25, 600.5]
    assert payload['authoritative_boundary']['source_crs']['wkt'] == 'PROJCRS["test"]'
    assert len(payload['authoritative_boundary']['provenance']['identity']) == 64
    assert server._load_saved_boundary_geometry(case)['projected_polygons'][0]['outer'][0] == [500.25, 600.5]
    (case / 'rivers_setup.json').write_text('{}', encoding='utf-8')
    assert server._load_saved_boundary_geometry(case) is None


def test_scientific_geo_grid_exposes_saved_projected_boundary(tmp_path, monkeypatch):
    case = tmp_path / 'scientific-case'
    case.mkdir()
    (case / 'rivers_setup.json').write_text(json.dumps({
        'boundary_geometry': {
            'coordinate_space': 'bathymetry_projected_grid_coordinates',
            'projected_polygons': [{
                'outer': [[500.0, 600.0], [501.0, 600.0], [501.0, 601.0]],
                'holes': [],
            }],
            'source_crs': {'wkt': 'PROJCRS["test"]'},
            'projected_crs': {'epsg': 32633},
            'provenance': {'source': 'uploaded-boundary-shapefile'},
        }
    }), encoding='utf-8')
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('x', 2); ds.createDimension('y', 2)
        x = ds.createVariable('x', 'f8', ('x',)); x.units = 'm'; x[:] = [500.0, 501.0]
        y = ds.createVariable('y', 'f8', ('y',)); y.units = 'm'; y[:] = [600.0, 601.0]
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = np.ones((2, 2)) * 4
    monkeypatch.setattr(server, 'active_case_path', case)

    response = server.app.test_client().get('/api/geo/grid?display=scientific')

    assert response.status_code == 200
    boundary = response.json['authoritative_boundary']
    assert boundary['projected_polygons'][0]['outer'][0] == [500.0, 600.0]
    assert boundary['coordinate_space'] == 'bathymetry_projected_grid_coordinates'
    assert boundary['source_crs']['wkt'] == 'PROJCRS["test"]'
    assert boundary['provenance']['source'] == 'uploaded-boundary-shapefile'
    assert len(boundary['provenance']['identity']) == 64


def test_saved_source_polygons_are_adapted_only_with_exact_projected_crs_and_coordinate_space(tmp_path):
    case = tmp_path / 'source-polygons-case'
    case.mkdir()
    wkt = 'PROJCS["case projected coordinates",UNIT["metre",1]]'
    groups = [{
        'outer': [[10.0, 20.0], [12.0, 20.0], [12.0, 22.0], [10.0, 20.0]],
        'holes': [[[10.5, 20.5], [10.75, 20.5], [10.5, 20.75]]],
    }]
    geometry = {
        'schema_version': 1,
        'coordinate_space': 'bathymetry_projected_grid_coordinates',
        'source_polygons': groups,
        'projected_crs': {'wkt': wkt},
        'provenance': {'source': 'recovered-local-upload-cache',
                       'status': 'proxy-display-geometry-not-scientifically-validated'},
    }
    setup = {'boundary_wkt': wkt, 'boundary_geometry': geometry}
    setup_path = case / 'rivers_setup.json'
    setup_path.write_text(json.dumps(setup), encoding='utf-8')

    loaded = server._load_saved_boundary_geometry(case)

    assert loaded['projected_polygons'] == groups
    assert loaded['projected_polygons'][0]['outer'] == geometry['source_polygons'][0]['outer']
    assert loaded['projected_polygons'][0]['holes'] == geometry['source_polygons'][0]['holes']
    assert loaded['provenance'] == geometry['provenance']
    assert 'projected_polygons' not in geometry
    assert json.loads(setup_path.read_text(encoding='utf-8')) == setup


@pytest.mark.parametrize('change', [
    {'coordinate_space': None},
    {'coordinate_space': 'geographic'},
    {'projected_crs': None},
    {'projected_crs': {'wkt': None}},
    {'projected_crs': {'wkt': 'PROJCS["different projection"]'}},
    {'source_polygons': [{'outer': [[10, 20], [11, 21]], 'holes': []}]},
    {'source_polygons': [{'outer': [[10, 20], [11, 20], [11, float('nan')]], 'holes': []}]},
    {'source_polygons': [{'outer': [[10, 20], [10, 20], [10, 20]], 'holes': []}]},
    {'source_polygons': [{'outer': [[10, 20], [11, 20], [11, True]], 'holes': []}]},
])
def test_saved_source_polygons_are_rejected_without_exact_coordinate_and_crs_proof(tmp_path, change):
    case = tmp_path / 'invalid-source-polygons-case'
    case.mkdir()
    wkt = 'PROJCS["case projected coordinates",UNIT["metre",1]]'
    geometry = {
        'coordinate_space': 'bathymetry_projected_grid_coordinates',
        'source_polygons': [{'outer': [[10, 20], [12, 20], [12, 22]], 'holes': []}],
        'projected_crs': {'wkt': wkt},
        'provenance': {'status': 'proxy-display-geometry-not-scientifically-validated'},
    }
    geometry.update(change)
    (case / 'rivers_setup.json').write_text(json.dumps({
        'boundary_wkt': wkt, 'boundary_geometry': geometry,
    }), encoding='utf-8')
    assert server._load_saved_boundary_geometry(case) is None
