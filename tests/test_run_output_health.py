import importlib
import os
import sys
import time
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))


def validate(case, **kwargs):
    assert importlib.util.find_spec('run_output_health'), 'Output health validation is missing'
    return importlib.import_module('run_output_health').validate_current_run_outputs(case, nc.Dataset, **kwargs)


def bathymetry(case):
    with nc.Dataset(case / 'bathymetry.nc', 'w') as ds:
        ds.createDimension('y', 2)
        ds.createDimension('x', 3)
        ds.createVariable('bathymetry', 'f8', ('y', 'x'))[:] = [[-10, 1, 2], [-10, 1, 2]]


def output(path, records=2, bad=None, allmasked=None, mask_land=True):
    with nc.Dataset(path, 'w') as ds:
        for name, size in [('time', None), ('level', 2), ('lat', 2), ('lon', 3)]:
            ds.createDimension(name, size)
        ds.createVariable('time', 'f8', ('time',))[:] = np.arange(records)
        for name in ['z', 'D', 'hn', 'temp', 'ecology']:
            dimensions = ('time', 'lat', 'lon') if name in ('z', 'D') else ('time', 'level', 'lat', 'lon')
            variable = ds.createVariable(name, 'f8', dimensions, fill_value=-9999.)
            shape = tuple(records if d == 'time' else len(ds.dimensions[d]) for d in dimensions)
            data = np.ones(shape)
            if mask_land:
                data[..., 0] = -9999.
            if records and name == bad:
                data[-1, ..., 1] = np.nan
            if name == allmasked:
                data[...] = -9999.
                # Finite land values must not hide a completely masked wet field.
                data[..., 0] = 1.
            variable[:] = data


def test_successful_exit_nan_outputs_are_rejected(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc', bad='temp')
    report = validate(tmp_path)
    assert report['ready'] is False
    assert any(v['variable'] == 'temp' and 'nonfinite' in v['reason'] for v in report['bad_variables'])


def test_finite_water_with_masked_land_is_healthy(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc')
    report = validate(tmp_path)
    assert report['ready'], report
    assert report['files'][0]['records'] == 2
    assert report['bytes_read'] > 0


@pytest.mark.parametrize('field', ['z', 'temp', 'hn', 'D'])
def test_fully_masked_critical_wet_field_is_rejected(tmp_path, field):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc', allmasked=field)
    report = validate(tmp_path)
    assert not report['ready']
    assert any(v['variable'] == field and 'wet' in v['reason'] for v in report['bad_variables'])


def test_fully_masked_optional_diagnostic_is_allowed(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc')
    with nc.Dataset(tmp_path / 'output.nc', 'a') as ds:
        for name in ('optional_diagnostic', 'elev'):
            diagnostic = ds.createVariable(name, 'f8', ('time', 'lat', 'lon'), fill_value=-9999.)
            diagnostic[:] = -9999.
    assert validate(tmp_path)['ready']


def test_all_emitted_numeric_variables_reject_nonfinite_values(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc', bad='ecology')
    report = validate(tmp_path)
    assert not report['ready']
    assert any(v['variable'] == 'ecology' for v in report['bad_variables'])


def test_archive_only_is_not_current_output(tmp_path):
    (tmp_path / 'output').mkdir()
    output(tmp_path / 'output' / 'output.nc')
    report = validate(tmp_path)
    assert not report['ready'] and report['errors']
    assert report['files'] == []


def test_empty_primary_rejected_but_empty_legacy_shell_skipped_with_valid_primary(tmp_path):
    output(tmp_path / 'output.nc', records=0)
    assert not validate(tmp_path)['ready']
    output(tmp_path / 'output.nc')
    output(tmp_path / 'lake.2d.nc', records=0)
    report = validate(tmp_path)
    assert report['ready'], report
    assert any(s['file'] == 'lake.2d.nc' for s in report['skipped'])


def test_no_primary_accepts_valid_legacy_pair(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'lake.2d.nc')
    output(tmp_path / 'lake.3d.nc')
    report = validate(tmp_path)
    assert report['ready'], report
    assert len(report['files']) == 2


def test_old_root_file_cannot_mask_missing_current_output(tmp_path):
    output(tmp_path / 'output.nc')
    old = time.time() - 120
    os.utime(tmp_path / 'output.nc', (old, old))
    report = validate(tmp_path, started_at=time.time())
    assert not report['ready'] and report['files'] == []


@pytest.mark.parametrize('offset_ns, expected', [(0, True), (-1000, False), (1000, True)])
def test_file_clock_and_process_clock_use_the_same_float_conversion(tmp_path, offset_ns, expected):
    # Captured Windows FILETIME tick: stat.st_mtime rounded one ULP below
    # time.time(), although the integer timestamps represented the same tick.
    tick = 1791789053221176500
    output(tmp_path / 'output.nc')
    stamp = tick + offset_ns
    os.utime(tmp_path / 'output.nc', ns=(stamp, stamp))
    report = validate(tmp_path, started_at=tick / 1e9)
    assert report['ready'] is expected, report


def test_scan_latest_record_only_and_enforces_chunk_bound(tmp_path):
    bathymetry(tmp_path)
    output(tmp_path / 'output.nc', records=100, bad='temp')
    with nc.Dataset(tmp_path / 'output.nc', 'a') as ds:
        ds.variables['temp'][-1] = 1.
        ds.variables['temp'][0] = np.nan
    report = validate(tmp_path, max_chunk_elements=3)
    assert report['ready'], report
    assert report['max_chunk_elements_read'] <= 3
    # One record and small repeated wet-mask tiles, never 100-record histories.
    assert report['bytes_read'] < 3000


def test_corrupt_current_file_reports_failure(tmp_path):
    (tmp_path / 'output.nc').write_bytes(b'not netcdf')
    report = validate(tmp_path)
    assert not report['ready'] and report['errors']


def test_dimension_names_align_transposed_critical_fields(tmp_path):
    bathymetry(tmp_path)
    with nc.Dataset(tmp_path / 'output.nc', 'w') as ds:
        for name, size in [('time', 1), ('x', 3), ('y', 2), ('level', 2)]:
            ds.createDimension(name, size)
        ds.createVariable('time', 'f8', ('time',))[:] = 0
        field = ds.createVariable('temp', 'f8', ('time', 'x', 'y', 'level'), fill_value=-9999.)
        values = np.full((1, 3, 2, 2), -9999.)
        values[:, 0] = 1.  # All wet values masked despite finite land values.
        field[:] = values
    assert not validate(tmp_path, max_chunk_elements=3)['ready']
