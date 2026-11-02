"""Deterministic external-data import/build/native-run and result API integration.

Run with .venv/Scripts/python.exe scripts/verify_external_workflow.py --work build/external-check
Use --skip-run to exercise preprocessing without launching the solver. All writes
are inside a fresh --work tree. Reports distinguish tested, failed, and untested
features; API coverage does not establish scientific accuracy or UI rendering.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, ProxyHandler, build_opener
import uuid
import zipfile

import netCDF4 as nc
import numpy as np
import shapefile

from verify_builtin_cases import (ROOT, MODEL_SOURCE, INPUT_NAMES, api,
                                  prepare_model, run_case, wait_for_service,
                                  isolated_launcher_environment as _isolated_launcher_environment)


class APIProbe:
    def __init__(self, opener, url):
        self.opener, self.url, self.calls = opener, url, []

    def call(self, path, data=None, *, method=None, files=None, form=None, expected=200):
        method = method or ('POST' if data is not None or files else 'GET')
        headers, body = {}, None
        if files:
            boundary = '----WETVerify' + uuid.uuid4().hex
            chunks = []
            for key, value in (form or {}).items():
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
            for field, file in files:
                chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{file.name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode())
                chunks.extend([file.read_bytes(), b'\r\n'])
            chunks.append(f'--{boundary}--\r\n'.encode())
            body = b''.join(chunks)
            headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        elif data is not None:
            body = json.dumps(data, allow_nan=False).encode()
            headers['Content-Type'] = 'application/json'
        item = dict(method=method, path=path, passed=False)
        self.calls.append(item)
        try:
            request = Request(self.url + path, data=body, headers=headers, method=method)
            try:
                response = self.opener.open(request, timeout=120)
            except HTTPError as error:
                response = error
            with response:
                item['http_status'] = response.code
                raw = response.read()
            parsed = json.loads(raw)
            if item['http_status'] != expected:
                raise ValueError(f'{method} {path}: HTTP {item["http_status"]}: {parsed}')
            if expected == 200 and isinstance(parsed, dict) and parsed.get('error'):
                raise ValueError(f'{path}: {parsed["error"]}')
            item.update(passed=True, response_bytes=len(raw))
            return parsed
        except Exception as error:
            item['error'] = str(error)
            raise


def finite_numbers(value):
    if isinstance(value, dict):
        return [v for item in value.values() for v in finite_numbers(item)]
    if isinstance(value, (list, tuple)):
        return [v for item in value for v in finite_numbers(item)]
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        if not math.isfinite(value):
            raise ValueError('Nonfinite number in API payload')
        return [value]
    return []


def require_values(payload, key):
    values = finite_numbers(payload.get(key))
    if not values:
        raise ValueError(f'API {key} contains no finite numeric values')
    return len(values)


def verify_result_features(probe, case_path):
    """Exercise each results route; compare slices and point series to NetCDF."""
    features, failures = {}, []

    def check(label, fn):
        try:
            details = fn()
            features[label] = dict(status='passed', details=details)
            return details
        except Exception as error:
            failures.append(label)
            features[label] = dict(status='failed', error=str(error))
            return None

    inventory = probe.call('/api/results/variables')
    items = inventory.get('3d', [])
    if not items or inventory.get('timesteps_3d', 0) < 2:
        raise ValueError('Results inventory lacks nonempty 3D output')
    nt = inventory['timesteps_3d']
    features['inventory'] = dict(status='passed', variables=len(items), timesteps=nt,
                                 labels=inventory.get('time_labels_3d'))
    # Match the server's current file selection exactly, then cross-check raw
    # numerical values. Never infer success merely from an HTTP 200.
    paths = [case_path / 'output.nc', case_path / 'output' / 'output.nc']
    for folder in (case_path, case_path / 'output'):
        paths.extend(sorted(folder.glob('*.3d.nc')))
    chosen = None
    for path in paths:
        if path.exists():
            with nc.Dataset(path) as ds:
                if len(ds.dimensions.get('time', [])):
                    chosen = path
                    break
    if chosen is None:
        raise ValueError('No readable 3D result NetCDF')
    with nc.Dataset(case_path / 'bathymetry.nc') as bathy:
        wet = np.ma.filled(bathy['bathymetry'][:] > 0, False)
    cells = np.argwhere(wet)
    j, i = map(int, cells[len(cells) // 2])
    ny, nx = wet.shape
    with nc.Dataset(chosen) as ds:
        # Every offered spatial variable must return a usable 2D slice.
        # Numeric comparison covers bottom/surface, first/final temperature.
        fields = [item for item in items if item['ndim'] in (3, 4)]
        for item in fields:
            variable = item['name']
            if variable in ds.variables and np.ma.getmaskarray(ds[variable][-1]).all():
                features['slice:' + variable] = dict(status='not_applicable', reason='Optional diagnostic is entirely masked in this configuration; no numerical field exists.')
                continue
            def slice_check(variable=variable):
                result = probe.call('/api/results/2d?' + urlencode(dict(var=variable, time=nt-1, level=0)))
                count = require_values(result, 'data')
                if result['shape'] != [ny, nx]:
                    raise ValueError(f'{variable}: incorrect slice shape {result["shape"]}')
                return dict(values=count)
            check('slice:' + variable, slice_check)

        def reference_checks():
            for t in (0, nt-1):
                for level in (0, ds['temp'].shape[1]-1):
                    result = probe.call('/api/results/2d?' + urlencode(dict(var='temp', time=t, level=level)))
                    actual = np.asarray(result['data'], dtype=float)
                    expected = np.ma.filled(ds['temp'][t, level], np.nan)
                    np.testing.assert_allclose(actual[wet], expected[wet], rtol=1e-6, atol=1e-7)
            cell = probe.call('/api/results/timeseries_cell?' + urlencode(dict(var='temp', i=i, j=j, layer=-1)))
            np.testing.assert_allclose(cell['values'], ds['temp'][:, -1, j, i], rtol=1e-6, atol=1e-7)
            profile = probe.call('/api/results/profile?' + urlencode(dict(var='temp', i=i, j=j, time=nt-1)))
            np.testing.assert_allclose(profile['profile'], ds['temp'][-1, :, j, i], rtol=1e-6, atol=1e-7)
            return dict(reference_file=str(chosen), point=[i, j], checked='first/final and bottom/surface slices, every point time, final profile')
        check('numeric_reference', reference_checks)

        def volume_checks():
            for quality in (16, 22, 30):
                result = probe.call('/api/results/3d_surface?' + urlencode(dict(var='temp', time=nt-1, target=quality)))
                require_values(result, 'data')
                if not result.get('bottom') or not result.get('sigma'):
                    raise ValueError('Missing volume bathymetry/sigma geometry')
                data = np.asarray(result['data'], dtype=float)
                bottom = np.asarray(result['bottom'], dtype=float)
                if data.shape != tuple(result['shape']) or bottom.shape != data.shape[1:]:
                    raise ValueError('Volume geometry dimensions mismatch')
                if np.isfinite(data[:, ~np.isfinite(bottom)]).any():
                    raise ValueError('Volume has visible data over land')
            return dict(qualities=[16, 22, 30])
        check('3d_volume_geometry', volume_checks)
        for representative in ['JuFish_sD', 'AdFish_sD', 'PiscFish_sD',
                               'methane_sCH4W', 'inorganic_carbon_sDICW',
                               'abiotic_water_sO2W', 'cyanobacteria_sDW']:
            if representative not in ds.variables:
                features['state_views:' + representative] = dict(status='not_applicable', reason='Model state is not in this case output subscription.')
                continue
            def state_views(variable=representative):
                volume = probe.call('/api/results/3d_surface?' + urlencode(dict(var=variable,time=nt-1,target=16)))
                require_values(volume,'data')
                layers = probe.call('/api/results/timeseries?' + urlencode(dict(var=variable,i=i,j=j,per_layer=1)))
                require_values(layers,'series')
                profile = probe.call('/api/results/profile?' + urlencode(dict(var=variable,i=i,j=j,time=nt-1)))
                require_values(profile,'profile')
                series = probe.call('/api/results/timeseries_cell?' + urlencode(dict(var=variable,i=i,j=j,layer=-1)))
                np.testing.assert_allclose(series['values'], ds[variable][:,-1,j,i], rtol=1e-6, atol=1e-7)
                return dict(views=['volume','vertical_heatmap','profile','point_timeseries'])
            check('state_views:' + representative, state_views)

    checks = [
        ('lake_average', '/api/results/timeseries?var=temp&lake_avg=1', None, 'values'),
        ('point_timeseries', f'/api/results/timeseries?var=temp&i={i}&j={j}', None, 'values'),
        ('region_timeseries', '/api/results/timeseries?' + urlencode(dict(var='temp', region=f'0,{nx},0,{ny}')), None, 'values'),
        ('layer_timeseries', '/api/results/timeseries?var=temp&lake_avg=1&per_layer=1', None, 'series'),
        ('polygon_timeseries', '/api/results/timeseries_polygon', dict(var='temp', polygon=[[0,0],[nx,0],[nx,ny],[0,ny]], layer=-1), 'values'),
        ('geographic_field', f'/api/geo/field?var=temp&time={nt-1}&level=0', None, 'values'),
        ('state_dashboard', '/api/results/state_vars_surface', None, None),
        ('dashboard', '/api/dashboard/summary', None, None),
    ]
    for label, path, body, key in checks:
        def generic(path=path, body=body, key=key):
            response = probe.call(path, body)
            count = require_values(response, key) if key else len(finite_numbers(response))
            if count == 0:
                raise ValueError('Empty result payload')
            return dict(numeric_values=count)
        check(label, generic)
    for label, path in [('network', '/api/ecology/network'), ('points', '/api/calibration/points'),
                        ('grid', '/api/geo/grid'), ('grid_editor', '/api/grid/editor')]:
        check(label, lambda path=path: {'response_type': type(probe.call(path)).__name__})
    features['exports'] = dict(status='not_exercised', reason='CSV/canvas/3D exports run in the browser; there is no HTTP export route. UI/download verification is required separately.')
    features['rendering_controls'] = dict(status='not_exercised', reason='Orbit, cut planes, animation, network drag, chart clicks and image export require browser interaction. API checks validate their data only.')
    return dict(passed=not failures, failed=failures, features=features,
                visible_variables=[item['name'] for item in items])


def route_inventory(app_dir):
    routes = set()
    for file in app_dir.glob('*.py'):
        if file.name.startswith('_'):
            continue
        tree = ast.parse(file.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr not in ('get', 'post', 'delete', 'route'):
                continue
            if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str) or not node.args[0].value.startswith('/api/'):
                continue
            methods = [node.func.attr.upper()] if node.func.attr != 'route' else ['GET']
            for keyword in node.keywords:
                if keyword.arg == 'methods':
                    methods = ast.literal_eval(keyword.value)
            routes.update((method, node.args[0].value) for method in methods)
    return sorted(routes)


def coverage_report(probe):
    tested = {}
    for call in probe.calls:
        tested.setdefault((call['method'], urlsplit(call['path']).path), []).append(call)
    report = []
    for method, path in route_inventory(ROOT / '3DWET' / 'app'):
        calls = tested.get((method, path), [])
        reason = 'Outside this external import/build/result integration scenario; not claimed tested.'
        status = 'not_exercised'
        if calls:
            status = 'passed' if all(c['passed'] for c in calls) else 'failed'
            reason = f'{len(calls)} HTTP requests'
        elif '/system/pick_folder' in path or path == '/api/system/explore':
            status, reason = 'not_applicable', 'Interactive OS picker/Explorer is excluded from headless API validation.'
        elif '/calibration/auto/' in path:
            status, reason = 'not_exercised', 'Optimization requires a separate repeated solver/calibration study; this harness checks observed/simulated comparison only.'
        report.append(dict(method=method, path=path, status=status, reason=reason))
    return report


def generate_external_data(folder, seed=20261010):
    folder.mkdir(parents=True)
    rng = np.random.default_rng(seed)
    cx, cy = 500000., 3300000.
    a, b = rng.uniform(400.,500.), rng.uniform(260.,340.)
    angle = np.linspace(0, 2*np.pi, 121)
    ring = [(cx+a*np.cos(t)*(1+.04*np.sin(3*t)), cy+b*np.sin(t)) for t in angle]
    with shapefile.Writer(str(folder / 'boundary'), shapeType=shapefile.POLYGON) as writer:
        writer.field('name', 'C', size=40)
        writer.poly([ring])
        writer.record('Deterministic external lake')
    # DBF otherwise embeds today's date, breaking deterministic source hashes.
    dbf = folder / 'boundary.dbf'
    content = bytearray(dbf.read_bytes())
    content[1:4] = bytes((120, 1, 1))
    dbf.write_bytes(content)
    # WKT from a fixed EPSG rather than guessed projected coordinates.
    from pyproj import CRS
    (folder / 'boundary.prj').write_text(CRS.from_epsg(32650).to_wkt(version='WKT1_ESRI'), encoding='utf-8')
    samples = []
    while len(samples) < 250:
        u, v = rng.uniform(-.95, .95, size=2)
        if u*u+v*v < .95:
            depth = 2 + 7*(1-u*u-v*v) + rng.uniform(-.15,.15)
            samples.append((cx+a*u, cy+b*v, depth))
    bathy = 'x,y,depth\n' + '\n'.join(f'{x:.6f},{y:.6f},{d:.6f}' for x,y,d in samples) + '\n'
    (folder / 'depth.csv').write_text(bathy, encoding='utf-8')
    with shapefile.Writer(str(folder/'depth_points'), shapeType=shapefile.POINT) as writer:
        writer.field('depth','N',decimal=6,size=14)
        for x,y,d in samples:
            writer.point(x,y)
            writer.record(d)
    depth_dbf = folder/'depth_points.dbf'
    content = bytearray(depth_dbf.read_bytes())
    content[1:4] = bytes((120,1,1))
    depth_dbf.write_bytes(content)
    shutil.copy2(folder/'boundary.prj',folder/'depth_points.prj')
    # Non-overlapping measured depth zones cover the entire shore. Their known
    # bounds allow an independent cell-by-cell oracle after polygon interpolation.
    edges = np.linspace(cx-1.1*a, cx+1.1*a, 6)
    zones = []
    with shapefile.Writer(str(folder/'depth_polygons'), shapeType=shapefile.POLYGON) as writer:
        writer.field('depth','N',decimal=6,size=14)
        for k, depth in enumerate((3.,5.,7.,5.,3.)):
            west,east = float(edges[k]),float(edges[k+1])
            south,north = cy-1.1*b,cy+1.1*b
            writer.poly([[(west,south),(west,north),(east,north),(east,south),(west,south)]])
            writer.record(depth)
            zones.append(dict(bbox=[west,south,east,north],depth=depth))
    polygon_dbf = folder/'depth_polygons.dbf'
    content = bytearray(polygon_dbf.read_bytes())
    content[1:4] = bytes((120,1,1))
    polygon_dbf.write_bytes(content)
    shutil.copy2(folder/'boundary.prj',folder/'depth_polygons.prj')
    (folder/'hypsograph.dat').write_text('0 0\n2 70000\n5 210000\n9 420000\n',encoding='utf-8')
    start = datetime(2020,1,1)
    meteo, inflow, outflow = ['date,u10,v10,slp,t2,rh,tcc,precip,evap'], ['date,Q,temp,nh4,no3,po4'], ['date,Q,temp,nh4,no3,po4']
    for day in range(8):
        date = (start+timedelta(days=day)).strftime('%Y-DOY%j')
        meteo.append(f'{date},{rng.uniform(.6,1.5):.5f},{rng.uniform(-.4,.5):.5f},{rng.uniform(1010,1018):.5f},{rng.uniform(14,18):.5f},{rng.uniform(.65,.85):.5f},{rng.uniform(.2,.6):.5f},{rng.uniform(0,2):.5f},{rng.uniform(.2,1):.5f}')
        q = rng.uniform(.15,.3)
        inflow.append(f'{date},{q:.6f},15.5,0.03,0.3,0.015')
        outflow.append(f'{date},{-q:.6f},15.5,0.03,0.3,0.015')
    for name, rows in [('meteo.csv',meteo),('inflow.csv',inflow),('outflow.csv',outflow)]:
        (folder/name).write_text('\n'.join(rows)+'\n', encoding='utf-8')
    manifest = dict(seed=seed, description='Synthetic realistic test data; not observations',
                    samples=len(samples), boundary_vertices=len(ring), days=8,
                    semi_axes_m=[float(a),float(b)],depth_zones=zones,
                    meteo_source_position=dict(latitude=29.8,longitude=117.0,crs='EPSG:4326',
                                               geometry_crs='EPSG:32650',
                                               geometry_center_projected_m=[500000.0,3300000.0]),
                    sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()})
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest


def save_generated_meteo(probe, source, case_path, manifest):
    """Upload the synthetic station's known position and verify persisted forcing.

    HTTP 200 is not sufficient: the meteo API intentionally returns HTTP 200
    with ``success=false`` when a spatial warning needs user confirmation.
    This generated source is colocated with its known projected lake centre, so
    the explicit WGS84 source coordinates should avoid that confirmation path.
    """
    position = manifest.get('meteo_source_position') or {}
    latitude, longitude = position.get('latitude'), position.get('longitude')
    if position.get('geometry_crs') != 'EPSG:32650' or (latitude, longitude) != (29.8, 117.0):
        raise ValueError(f'Generated meteo source position is missing/invalid: {position}')
    meteo_csv = Path(source) / 'meteo.csv'
    expected_sha = hashlib.sha256(meteo_csv.read_bytes()).hexdigest()
    if manifest.get('sha256', {}).get('meteo.csv') != expected_sha:
        raise ValueError('Generated meteo source hash differs from its manifest')

    uploaded = probe.call('/api/input/meteo/upload', files=[('file', meteo_csv)],
                          form={'source_lat': f'{latitude:g}',
                                'source_lon': f'{longitude:g}'})
    if uploaded.get('success') is not True:
        raise ValueError(f'Meteo upload did not report success: {uploaded}')
    draft = probe.call('/api/input/meteo/draft')
    if not draft.get('exists') or len(draft.get('dates', [])) != manifest['days']:
        raise ValueError(f'Meteo draft does not contain all generated records: {draft}')
    draft_source = draft.get('source') or {}
    if (not np.isclose(float(draft_source.get('latitude', np.nan)), latitude) or
            not np.isclose(float(draft_source.get('longitude', np.nan)), longitude)):
        raise ValueError(f'Meteo draft lost the known source coordinates: {draft_source}')
    if draft_source.get('sha256') != expected_sha:
        raise ValueError('Meteo draft source hash does not match the generated CSV')

    saved = probe.call('/api/input/meteo/save',
                       {'source_lat': latitude, 'source_lon': longitude})
    if saved.get('success') is not True:
        if saved.get('requires_confirmation'):
            warning = saved.get('warning', {})
            raise ValueError(f'Meteo save requires confirmation: {warning}')
        raise ValueError(f'Meteo save did not report success: {saved}')
    if saved.get('requires_confirmation'):
        raise ValueError(f'Meteo save unexpectedly still requires confirmation: {saved}')
    spatial = saved.get('spatial') or {}
    if spatial.get('position_known') is not True:
        raise ValueError(f'Saved meteo provenance does not know source position: {spatial}')

    meteo_path = Path(case_path) / 'meteo.nc'
    if not meteo_path.is_file() or meteo_path.stat().st_size == 0:
        raise ValueError('Meteo save reported success but did not write meteo.nc')
    provenance_name = saved.get('provenance_file')
    if not provenance_name:
        raise ValueError('Meteo save omitted its provenance filename')
    provenance_path = Path(case_path) / provenance_name
    if not provenance_path.is_file():
        raise ValueError(f'Meteo provenance file is missing: {provenance_path}')
    provenance = json.loads(provenance_path.read_text(encoding='utf-8'))
    provenance_source = provenance.get('source') or {}
    if provenance_source.get('sha256') != expected_sha:
        raise ValueError('Saved meteo provenance hash does not match the generated CSV')
    if (not np.isclose(float(provenance_source.get('latitude', np.nan)), latitude) or
            not np.isclose(float(provenance_source.get('longitude', np.nan)), longitude)):
        raise ValueError(f'Saved meteo provenance lost the source coordinates: {provenance_source}')
    if provenance.get('source_period', {}).get('rows') != manifest['days']:
        raise ValueError('Saved meteo provenance has an unexpected source row count')
    with nc.Dataset(meteo_path) as dataset:
        if len(dataset.dimensions.get('time', [])) != saved.get('n_times'):
            raise ValueError('meteo.nc time dimension disagrees with save response')
        if 't2' not in dataset.variables or not np.isfinite(dataset['t2'][:]).all():
            raise ValueError('meteo.nc is missing finite air-temperature forcing')
    return dict(source_position={'latitude': latitude, 'longitude': longitude,
                                 'crs': position['crs']},
                source_sha256=expected_sha, n_times=saved['n_times'],
                netcdf=str(meteo_path), provenance_file=str(provenance_path),
                spatial=spatial, provenance=provenance)


def case_path_from_bathymetry_save(response, expected_name=None):
    """Use the API's persisted bathymetry path to identify selected case storage."""
    if not isinstance(response, dict) or response.get('success') is not True:
        raise ValueError(f'Preprocess save did not report success: {response}')
    raw_path = response.get('path')
    if not raw_path:
        raise ValueError(f'Preprocess save omitted its bathymetry path: {response}')
    bathymetry_path = Path(raw_path).resolve()
    if bathymetry_path.name != 'bathymetry.nc' or not bathymetry_path.is_file():
        raise ValueError(f'Preprocess save bathymetry path is missing or invalid: {bathymetry_path}')
    case_path = bathymetry_path.parent
    if expected_name and case_path.name != expected_name:
        raise ValueError(f'Preprocess save returned unexpected case path: {case_path}')
    return case_path


def external_setup(probe, work, duration_seconds, seed=20261010, bathymetry_kind='point'):
    if bathymetry_kind not in ('point','polygon'):
        raise ValueError('Unknown bathymetry kind')
    source = work / 'external_data'
    manifest = generate_external_data(source, seed=seed)
    name = 'External Seed Lake'
    probe.call('/api/preprocess/case/create', dict(case_name=name))
    boundary = probe.call('/api/preprocess/boundary/upload', files=[('files',p) for p in sorted(source.glob('boundary.*'))])
    bathy = probe.call('/api/preprocess/bathymetry/upload_xyz', files=[('file',source/'depth.csv')], form=dict(crs='projected'))
    shapebathy = probe.call('/api/preprocess/bathymetry/upload', files=[('files',p) for p in sorted(source.glob('depth_points.*'))],form=dict(depth_field='depth'))
    if shapebathy.get('n_features') != manifest['samples']:
        raise ValueError('Shapefile depth upload lost samples')
    curve = probe.call('/api/preprocess/hypsograph',files=[('file',source/'hypsograph.dat')],form=dict(center_lon=117,center_lat=29.8))
    if curve.get('max_depth_m') != 9 or not curve.get('boundary_id') or not curve.get('bathy_id'):
        raise ValueError('Hypsograph conversion incorrect')
    grid = probe.call('/api/preprocess/grid/generate', dict(boundary_id=boundary['boundary_id'], dx=50, dy=50))
    if grid['n_water_cells'] < 50:
        raise ValueError('Generated lake has too few wet cells')
    probe.call('/api/preprocess/bathymetry/interpolate', dict(grid_id=grid['grid_id'], bathy_id=shapebathy['bathy_id'], method='nearest'))
    probe.call('/api/preprocess/bathymetry/interpolate', dict(grid_id=grid['grid_id'], bathy_id=bathy['bathy_id'], method='linear'))
    if bathymetry_kind == 'polygon':
        polygon = probe.call('/api/preprocess/bathymetry/upload',
            files=[('files',p) for p in sorted(source.glob('depth_polygons.*'))],form=dict(depth_field='depth'))
        if polygon.get('n_features') != len(manifest['depth_zones']):
            raise ValueError('Polygon upload lost depth zones')
        interpolated = probe.call('/api/preprocess/bathymetry/interpolate',
            dict(grid_id=grid['grid_id'],bathy_id=polygon['bathy_id'],method='polygon'))
        actual = np.asarray(interpolated['depth_array'],dtype=float)
        mask = np.asarray(grid['mask'],dtype=bool)
        expected = np.full(mask.shape,np.nan)
        for j,i in np.argwhere(mask):
            x = grid['x0']+(i+.5)*grid['dx']
            y = grid['y0']+(j+.5)*grid['dy']
            matches = [z for z in manifest['depth_zones'] if z['bbox'][0]<=x<z['bbox'][2] and z['bbox'][1]<=y<z['bbox'][3]]
            if len(matches)!=1:raise ValueError(f'Uncovered/overlapping cell {i},{j}')
            expected[j,i]=matches[0]['depth']
        np.testing.assert_allclose(actual[mask],expected[mask],rtol=0,atol=1e-9)
        if len(np.unique(actual[mask]))!=3:raise ValueError('Polygon depth zones collapsed')
        manifest['polygon_verification']=dict(cells=int(mask.sum()),depths=np.unique(actual[mask]).tolist(),max_abs_error=float(np.max(np.abs(actual[mask]-expected[mask]))))
    preview = probe.call('/api/preprocess/preview?' + urlencode(dict(
        boundary_id=boundary['boundary_id'], grid_id=grid['grid_id'])))
    if preview['grid']['nx'] != grid['nx'] or preview['grid']['ny'] != grid['ny']:
        raise ValueError('Preview grid dimensions differ from generated grid')
    if len(preview['boundary']['coords']) < 3 or not np.isfinite(
            np.asarray(preview['grid']['depth_array'])[np.asarray(grid['mask'], dtype=bool)]).all():
        raise ValueError('Boundary/depth preview contains invalid lake data')
    mask = np.asarray(grid['mask'], dtype=bool)
    # Choose connected cells, away from isolated corners, in one-based river coordinates.
    cells = [(j,i) for j,i in np.argwhere(mask) if 0<j<mask.shape[0]-1 and 0<i<mask.shape[1]-1 and mask[j-1:j+2,i-1:i+2].all()]
    j0,i0 = cells[len(cells)//3]
    j1,i1 = cells[2*len(cells)//3]
    rivers = [dict(name='SEED_IN',i=int(i0)+1,j=int(j0)+1,kind='inflow'), dict(name='SEED_OUT',i=int(i1)+1,j=int(j1)+1,kind='outflow')]
    saved_case = probe.call('/api/preprocess/save', dict(case_name=name,grid_id=grid['grid_id'],rivers=rivers))
    case_path = case_path_from_bathymetry_save(saved_case, expected_name=name)
    if bathymetry_kind == 'polygon':
        with nc.Dataset(case_path/'bathymetry.nc') as saved:
            np.testing.assert_allclose(saved['bathymetry'][:][mask],expected[mask],rtol=0,atol=1e-9)
    manifest['meteo_save'] = save_generated_meteo(probe, source,
                                                   case_path,
                                                   manifest)
    for river, file in [('SEED_IN','inflow.csv'),('SEED_OUT','outflow.csv')]:
        probe.call('/api/input/rivers/upload', files=[('file',source/file)], form=dict(river_name=river))
    probe.call('/api/input/rivers/save', {})
    for name_ in ('SEED_IN','SEED_OUT'):
        values = probe.call('/api/input/rivers/series?' + urlencode(dict(name=name_)))
        require_values(values['series']['flow'], 'values')
    stop = datetime(2020,1,1)+timedelta(seconds=duration_seconds)
    built = probe.call('/api/case/build', dict(preset='mesotrophic',start='2020-01-01 00:00:00',stop=str(stop),timestep=2,nlev=6,engines=dict(eco=True,fish=True,ghg=True)))
    if not built.get('success'):
        raise ValueError('Case build unsuccessful')
    import yaml
    model_config = yaml.safe_load((case_path/'fabm.yaml').read_text(encoding='utf-8'))
    models = [instance.get('model') for instance in model_config.get('instances', {}).values()]
    if models.count('wet/fish') < 3 or 'wet/methane' not in models or 'wet/inorganic_carbon' not in models:
        raise ValueError(f'Builder did not honor requested fish/GHG modules: {models}; warnings={built.get("warnings")}')
    initial_temp = 15.0 + float(np.random.default_rng(manifest['seed']+1).uniform(-.5,.5))
    initial = probe.call('/api/case/init_conditions', dict(hydro=dict(elev_const=0,temp_const=initial_temp),water_quality={'abiotic_water.sO2W':8.5,'abiotic_water.sNH4W':.03,'abiotic_water.sNO3W':.3,'abiotic_water.sPO4W':.015}))
    if initial.get('warnings'):
        raise ValueError(f'Initial conditions warnings: {initial["warnings"]}')
    probe.call('/api/case/init_conditions')
    probe.call('/api/config/output', dict(time_unit='second',time_step=60,sync_interval=1,preset='all'))
    # This directory is a genuine external complete project; the subsequent
    # import uses the app's copy/provenance API instead of directly registering it.
    external_project = source/'complete_case'
    external_project.mkdir()
    for path in case_path.iterdir():
        if path.is_file() and (path.name in INPUT_NAMES or path.suffix in ('.inp','.nml','.yaml','.json')):
            shutil.copy2(path, external_project/path.name)
    imported = probe.call('/api/projects/import', dict(source_path=str(external_project),name='Imported Random Lake'))
    if not imported.get('success'):
        raise ValueError('External import did not succeed')
    copied = imported.get('manifest', {}).get('files', [])
    if not copied or any(item.get('source_sha256') != item.get('copied_sha256') for item in copied):
        raise ValueError('Import provenance hashes absent or unequal')
    imported_path = Path(imported['case_path'])
    if not imported_path.is_dir():
        raise ValueError(f'Imported case path does not exist: {imported_path}')
    missing_imports = [filename for filename in ('bathymetry.nc','meteo.nc','output.yaml')
                       if not (imported_path/filename).is_file()]
    if missing_imports:
        raise ValueError(f'Imported case is missing run inputs: {missing_imports} in {imported_path}')
    probe.call('/api/case/load', dict(case_name=imported_path.name))
    manifest.update(initial_temp=initial_temp, import_files=len(copied), imported_case=str(imported_path),bathymetry_kind=bathymetry_kind)
    (source/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    return imported_path, manifest


def exercise_repair(probe, case_path):
    # Deliberately corrupt cadence only in this isolated generated case, require
    # revision-guarded repair and its real backup, then recheck.
    output = case_path/'output.yaml'
    original = output.read_text(encoding='utf-8')
    output.write_text(original.replace('sync_interval: 1','sync_interval: 0'), encoding='utf-8')
    check = probe.call('/api/run/check')
    repairs = [c.get('repair') for c in check.get('checks', []) if c.get('repair')]
    if not repairs:
        raise ValueError('Zero sync interval did not offer a repair')
    candidates = [r for r in repairs if 'sync' in str(r)]
    if not candidates:
        raise ValueError(f'No output sync repair offered: {repairs}')
    repair = candidates[0]
    action = repair.get('id', repair.get('action')) if isinstance(repair,dict) else repair
    result = probe.call('/api/run/repair', dict(case_path=check['case_path'],revision=check['revision'],action=action))
    if not result.get('success') or not Path(result['backup']).is_file():
        raise ValueError('Repair did not create backup')
    if 'sync_interval: 0' in output.read_text(encoding='utf-8'):
        raise ValueError('Repair left output disabled')
    return result


def export_inputs(work, destination):
    """Package synthetic source files and a complete importable input project."""
    work, destination = Path(work), Path(destination)
    source = work/'external_data'
    manifest = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    if not (source/'complete_case'/'getm.inp').is_file():
        raise ValueError('Verified complete external input project is missing')
    readme = f"""# 外部合成湖泊输入样例

固定随机种子：{manifest['seed']}。这是用于软件与数值稳定性检查的合成数据，不是实测资料，也未做科学校准或长期预测验证。

湖界和水深点采用 WGS84 / UTM 50N (EPSG:32650)，中心约 (500000, 3300000) m；湖泊半长轴{manifest.get("semi_axes_m",[450,300])[0]:.2f} m、半短轴{manifest.get("semi_axes_m",[450,300])[1]:.2f} m。网格50×50 m，250个随机水深点，水深向下为正，约2–9 m。boundary.*必须整体上传；depth.csv包含x,y,depth。depth_points.*是同一批深度点的可选Shapefile表达；depth_polygons.*为覆盖湖界的五个独立测深分区（3/5/7/5/3 m），可选择polygon插值；本案例实际使用的类型见manifest.json的bathymetry_kind。hypsograph.dat是独立的深度面积格式测试样例，不代表主湖的实际面积曲线。

气象和河流CSV日期使用 YYYY-DOYDDD（例如2020-DOY001），共8天。气象单位：u10/v10 m/s；slp hPa；t2 ℃；rh/tcc为0–1；precip/evap mm/day（程序将蒸发转为负水通量）。河流Q m³/s，正值入湖、负值出湖；temp ℃，nh4/no3/po4 g/m³。入流、出流采用相同流量大小，方向相反。

导入方法：解压后，在3DWET Studio“导入项目”中选择 complete_case 文件夹并填写新案例名；载入后先进行运行体检，再运行。complete_case已包含bathymetry.nc、气象/河流NetCDF、生态配置/初值、20分钟演示的getm.inp和output.yaml。可独立用“新建案例→上传boundary.*→生成50m网格→上传depth.csv或depth_points.*→插值→上传气象及两条河流CSV→构建案例”重建。手工放置河流点时应选择连通水格；格点元数据位于complete_case/rivers_setup.json。

完整案例演示起止为2020-01-01 00:00:00至00:20:00，步长2s、6层，每60s输出。包括水动力、生态、三个鱼类模型及无机碳/甲烷模块。水位为相对bathymetry基准的0m。更长模拟需要重新检查输入覆盖、CFL、生态参数及稳定性。

manifest.json记录源文件SHA-256。complete_case中的源输入保持完整；本压缩包不包含运行结果、日志或临时缓存。导入时程序另外生成import_manifest.json，记录逐文件复制前后SHA-256。\n"""
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('README.md',readme)
        for path in sorted(source.rglob('*')):
            if path.is_file() and 'output' not in path.relative_to(source).parts and path.suffix.lower() not in ('.log',):
                archive.write(path,path.relative_to(source).as_posix())
    return dict(path=str(destination.resolve()),bytes=destination.stat().st_size,
                sha256=hashlib.sha256(destination.read_bytes()).hexdigest())


def isolated_launcher_environment(work, environ=None):
    """Keep launcher case and state storage inside this acceptance work tree."""
    return _isolated_launcher_environment(work,environ)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',required=True,type=Path)
    parser.add_argument('--model-source',type=Path,default=MODEL_SOURCE)
    parser.add_argument('--launcher',type=Path,default=ROOT/'3DWET'/'app'/'launcher.py')
    parser.add_argument('--solver',type=Path,help='Candidate solver copied only into this isolated work tree')
    parser.add_argument('--hold',action='store_true',help='Keep a successful case available for browser acceptance until work/stop exists')
    parser.add_argument('--duration-seconds',type=int,default=1200)
    parser.add_argument('--seed',type=int,default=20261010,
                        help='Reproducible independent boundary, depth and driver data')
    parser.add_argument('--bathymetry-kind',choices=('point','polygon'),default='point')
    parser.add_argument('--timeout',type=float,default=600)
    parser.add_argument('--skip-run',action='store_true')
    parser.add_argument('--export-inputs',type=Path,
                        help='On successful native/result validation, write this inputs-only ZIP')
    args = parser.parse_args()
    if args.duration_seconds<1200 or args.duration_seconds%60:
        parser.error('Duration must be >=1200 seconds and divisible by 60')
    work=args.work.resolve()
    if work.exists():
        parser.error('--work must be a fresh directory; nothing is deleted')
    work.mkdir(parents=True)
    # Case builder needs the Luoma scientific templates in its own model root.
    prepare_model(work,['Lake Luoma'],args.model_source.resolve(),args.duration_seconds)
    if args.solver:shutil.copy2(args.solver,work/'3DWET/bin/getm_cartesian.exe')
    env,model_root,state_root=isolated_launcher_environment(work)
    stdout=(work/'launcher.stdout.log').open('w',encoding='utf-8')
    stderr=(work/'launcher.stderr.log').open('w',encoding='utf-8')
    launcher=args.launcher.resolve()
    command=([sys.executable,str(launcher)] if launcher.suffix=='.py' else [str(launcher)])+['--web','--no-open','--port','0']
    process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
    opener=build_opener(ProxyHandler({}))
    probe=None
    report=dict(passed=False,duration_seconds=args.duration_seconds,
                scope='Deterministic synthetic integration scenario; not observational, scientific-accuracy, annual stability, or complete browser UX validation.')
    try:
        url=wait_for_service(work,process,state_root=state_root,model_root=model_root)
        report['url']=url
        probe=APIProbe(opener,url)
        report['health']=probe.call('/api/system/health')
        probe.call('/api/system/diagnostics')
        case_path,report['data']=external_setup(probe,work,args.duration_seconds,seed=args.seed,bathymetry_kind=args.bathymetry_kind)
        report['repair']=exercise_repair(probe,case_path)
        report['preflight']=probe.call('/api/run/check')
        if not report['preflight'].get('ok'):
            raise ValueError(f'Preflight blocked: {report["preflight"]}')
        if args.skip_run:
            report.update(passed=True,run=dict(status='not_exercised',reason='--skip-run requested'))
        else:
            report['run']=run_case(opener,url,case_path.name,case_path,args.timeout,verify_features=False)
            report['result_features']=verify_result_features(probe,case_path)
            report['passed']=report['result_features']['passed']
            names=report['result_features']['visible_variables']
            if not all(any(name.startswith(prefix) for name in names) for prefix in ('JuFish_','AdFish_','PiscFish_','methane_','inorganic_carbon_')):
                raise ValueError('Expected fish/GHG families absent from native results')
            if report['passed'] and args.export_inputs:
                report['input_archive']=export_inputs(work,args.export_inputs)
            if report['passed'] and args.hold:
                (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps({'browser_acceptance_url':url,'work':str(work)},ensure_ascii=False),flush=True)
                while process.poll() is None and not (work/'stop').exists():time.sleep(1)
    except Exception as error:
        report['error']=f'{type(error).__name__}: {error}'
    finally:
        if probe:
            report['api_calls']=probe.calls
            report['route_coverage']=coverage_report(probe)
            try:
                probe.call('/api/run/stop',{})
            except Exception:
                pass
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        stdout.close()
        stderr.close()
        (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:report[k] for k in ('passed','error','data') if k in report},ensure_ascii=False,indent=2))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
