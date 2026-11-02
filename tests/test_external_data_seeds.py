"""Each acceptance round needs independently generated, reproducible inputs."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import verify_external_workflow as external_workflow
from verify_external_workflow import generate_external_data
import hashlib
import json
import shapefile
import numpy as np
import netCDF4 as nc
import pytest


def test_external_synthetic_manifest_identifies_generated_meteo_position(tmp_path):
    source = tmp_path / 'external_data'
    manifest = generate_external_data(source, seed=11005)
    assert manifest.get('meteo_source_position') == {
        'latitude': 29.8,
        'longitude': 117.0,
        'crs': 'EPSG:4326',
        'geometry_crs': 'EPSG:32650',
        'geometry_center_projected_m': [500000.0, 3300000.0],
    }


class MeteoSaveProbe:
    def __init__(self, case_path, source, *, confirm=False):
        self.case_path = case_path
        self.source = source
        self.confirm = confirm
        self.calls = []
        self.draft = None

    def call(self, path, data=None, *, files=None, form=None):
        self.calls.append({'path': path, 'data': data, 'files': files, 'form': form})
        if path == '/api/input/meteo/upload':
            self.draft = {
                'exists': True,
                'dates': [f'2020-01-0{i}' for i in range(1, 9)],
                'source': {
                    'latitude': float(form['source_lat']),
                    'longitude': float(form['source_lon']),
                    'sha256': hashlib.sha256((self.source / 'meteo.csv').read_bytes()).hexdigest(),
                },
            }
            return {'success': True}
        if path == '/api/input/meteo/draft':
            return self.draft
        if path == '/api/input/meteo/save':
            if self.confirm:
                return {'success': False, 'requires_confirmation': True,
                        'confirmation_token': 'confirmation-required'}
            with nc.Dataset(self.case_path / 'meteo.nc', 'w') as ds:
                ds.createDimension('time', 8)
                ds.createVariable('time', 'f8', ('time',))[:] = np.arange(8)
                ds.createVariable('t2', 'f4', ('time',))[:] = np.full(8, 15)
            provenance = {
                'source': self.draft['source'],
                'source_period': {'start': self.draft['dates'][0],
                                  'end': self.draft['dates'][-1], 'rows': 8},
                'spatial': {'position_known': True, 'confirmed': False},
            }
            (self.case_path / 'meteo_provenance.json').write_text(
                json.dumps(provenance), encoding='utf-8')
            return {'success': True, 'n_times': 8,
                    'provenance_file': 'meteo_provenance.json',
                    'spatial': provenance['spatial']}
        raise AssertionError(f'Unexpected API request: {path}')


def test_external_meteo_upload_requires_saved_file_and_matching_provenance(tmp_path):
    source = tmp_path / 'external_data'
    manifest = generate_external_data(source, seed=11007)
    case_path = tmp_path / 'case'
    case_path.mkdir()
    probe = MeteoSaveProbe(case_path, source)

    assert callable(getattr(external_workflow, 'save_generated_meteo', None)), (
        'external workflow must validate the meteo save contract')
    saved = external_workflow.save_generated_meteo(probe, source, case_path, manifest)

    upload = next(call for call in probe.calls if call['path'] == '/api/input/meteo/upload')
    assert upload['form'] == {'source_lat': '29.8', 'source_lon': '117'}
    save = next(call for call in probe.calls if call['path'] == '/api/input/meteo/save')
    assert save['data'] == {'source_lat': 29.8, 'source_lon': 117.0}
    assert saved['source_sha256'] == manifest['sha256']['meteo.csv']
    assert saved['n_times'] == 8
    assert saved['provenance']['spatial']['position_known'] is True
    assert saved['provenance']['source']['latitude'] == 29.8
    assert saved['provenance']['source']['longitude'] == 117.0
    assert (case_path / 'meteo.nc').is_file()


def test_external_meteo_harness_rejects_confirmation_response_even_when_http_200(tmp_path):
    source = tmp_path / 'external_data'
    manifest = generate_external_data(source, seed=11008)
    case_path = tmp_path / 'case'
    case_path.mkdir()
    probe = MeteoSaveProbe(case_path, source, confirm=True)

    assert callable(getattr(external_workflow, 'save_generated_meteo', None)), (
        'external workflow must inspect meteo save JSON instead of HTTP status alone')
    with pytest.raises(ValueError, match='requires confirmation'):
        external_workflow.save_generated_meteo(probe, source, case_path, manifest)


def test_different_seeds_change_geometry_depth_and_drivers(tmp_path):
    a=generate_external_data(tmp_path/'a',seed=11001)
    b=generate_external_data(tmp_path/'b',seed=11002)
    again=generate_external_data(tmp_path/'again',seed=11001)
    assert a['sha256']==again['sha256']
    for filename in ('boundary.shp','depth_points.shp','depth.csv','meteo.csv','inflow.csv'):
        assert a['sha256'][filename]!=b['sha256'][filename],filename


def test_polygon_depth_zones_cover_lake_without_overlap(tmp_path):
    manifest = generate_external_data(tmp_path/'polygon', seed=11003)
    zones = manifest['depth_zones']
    assert len(zones) == 5
    with shapefile.Reader(str(tmp_path/'polygon'/'depth_polygons')) as reader:
        assert reader.shapeType == shapefile.POLYGON
        assert len(reader) == len(zones)
        for shape, record, zone in zip(reader.shapes(), reader.records(), zones):
            np.testing.assert_allclose(shape.bbox, zone['bbox'])
            assert record['depth'] == zone['depth']
    with shapefile.Reader(str(tmp_path/'polygon'/'boundary')) as reader:
        west, south, east, north = reader.bbox
    assert zones[0]['bbox'][0] < west
    assert zones[-1]['bbox'][2] > east
    for left, right in zip(zones, zones[1:]):
        assert left['bbox'][2] == right['bbox'][0]
    assert all(z['bbox'][1] < south and z['bbox'][3] > north for z in zones)
    again = generate_external_data(tmp_path/'again', seed=11003)
    other = generate_external_data(tmp_path/'other', seed=11004)
    assert manifest['sha256']['depth_polygons.shp'] == again['sha256']['depth_polygons.shp']
    assert manifest['sha256']['depth_polygons.shp'] != other['sha256']['depth_polygons.shp']
