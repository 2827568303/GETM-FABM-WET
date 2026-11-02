import hashlib
import sys
from pathlib import Path

import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET' / 'app'))
from gotm_working_copy import create_working_copy, validate_working_copy, validate_gotm_output


def make_gotm(source):
    (source / 'gotm.yaml').write_text('config: reference', encoding='utf-8')
    (source / 'fabm.yaml').write_text('instances: {}', encoding='utf-8')
    (source / 'input.dat').write_text('native input', encoding='utf-8')
    (source / 'notes.txt').write_text('do not copy arbitrary extras', encoding='utf-8')
    (source / 'gotm_release.exe').write_bytes(b'MZofficial release binary')
    (source / 'debug.exe').write_bytes(b'debug binary')
    with nc.Dataset(source / 'output.nc', 'w') as ds:
        ds.createDimension('time', 2)
        ds.createDimension('z', 2)
        ds.createDimension('lat', 1)
        ds.createDimension('lon', 1)
        t = ds.createVariable('time', 'f8', ('time',))
        t.units = 'days since 2000-01-01 00:00:00'
        t[:] = [0, 1]
        ds.comment = 'GOTM native single column output'
        for name, dims, values in [('h', ('time','z','lat','lon'), [[[[-10]], [[-2]]], [[[-10]], [[-2]]]]),
                                   ('z', ('time','z','lat','lon'), [[[[-8]], [[-1]]], [[[-8]], [[-1]]]]),
                                   ('temp', ('time','z','lat','lon'), [[[[10]], [[9]]], [[[11]], [[8]]]])]:
            ds.createVariable(name, 'f8', dims)[:] = values


def test_working_copy_is_allowlisted_signed_and_source_unchanged(tmp_path):
    src, dst = tmp_path / 'reference', tmp_path / 'copy'
    src.mkdir(); dst.mkdir()
    make_gotm(src)
    before = {p.relative_to(src).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in src.rglob('*') if p.is_file()}
    create_working_copy(src, dst, b'test-secret')
    assert validate_working_copy(dst, b'test-secret')
    assert (dst / 'output.nc').is_file() and (dst / 'gotm_release.exe').is_file()
    assert not (dst / 'debug.exe').exists() and not (dst / 'notes.txt').exists()
    after = {p.relative_to(src).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in src.rglob('*') if p.is_file()}
    assert before == after


def test_tampered_manifest_or_files_are_not_trusted(tmp_path):
    src, dst = tmp_path / 'reference', tmp_path / 'copy'
    src.mkdir(); dst.mkdir(); make_gotm(src)
    create_working_copy(src, dst, b'test-secret')
    (dst / 'gotm_release.exe').write_bytes(b'user executable')
    assert not validate_working_copy(dst, b'test-secret')
    assert not validate_working_copy(dst, b'wrong-secret')


def test_output_must_be_fresh_single_column_finite_and_cover_time(tmp_path):
    make_gotm(tmp_path)
    report = validate_gotm_output(tmp_path, nc.Dataset, started_at=0, expected_range=None)
    assert report['ready'], report
    assert report['time_range'] == ['2000-01-01 00:00:00', '2000-01-02 00:00:00']
    (tmp_path / 'output.nc').unlink()
    assert not validate_gotm_output(tmp_path, nc.Dataset, started_at=0)['ready']


def test_gotm_output_rejects_nonfinite_native_field(tmp_path):
    make_gotm(tmp_path)
    with nc.Dataset(tmp_path / 'output.nc', 'a') as ds:
        ds.variables['temp'][-1, 0, 0, 0] = np.nan
    report = validate_gotm_output(tmp_path, nc.Dataset, started_at=0)
    assert not report['ready'] and report['bad_variables']


def test_gotm_output_rejects_incomplete_expected_time_range(tmp_path):
    make_gotm(tmp_path)
    report = validate_gotm_output(tmp_path, nc.Dataset, started_at=0,
                                 expected_range=['1999-01-01 00:00:00', '2000-01-03 00:00:00'])
    assert not report['ready'] and any('cover' in error for error in report['errors'])


def test_gotm_output_accepts_interface_and_column_fields(tmp_path):
    make_gotm(tmp_path)
    with nc.Dataset(tmp_path / 'output.nc', 'a') as ds:
        ds.createDimension('zi', 3)
        interface = ds.createVariable('tke', 'f8', ('time', 'zi', 'lat', 'lon'))
        interface[:] = 1.
        column = ds.createVariable('airtemp', 'f8', ('time', 'lat', 'lon'))
        column[:] = 2.
    report = validate_gotm_output(tmp_path, nc.Dataset, started_at=0)
    assert report['ready'], report


def test_gotm_output_rejects_non_singleton_horizontal_dimensions(tmp_path):
    make_gotm(tmp_path)
    with nc.Dataset(tmp_path / 'output.nc', 'a') as ds:
        # A new horizontal dimension cannot be mistaken for the vertical axis.
        ds.createDimension('x', 2)
        field = ds.createVariable('horizontal_field', 'f8', ('time', 'z', 'x'))
        field[:] = 1.
    report = validate_gotm_output(tmp_path, nc.Dataset, started_at=0)
    assert not report['ready'] and any('horizontal' in error.lower() or 'dimension' in error.lower()
                                        for error in report['errors'])


def test_reject_source_with_path_escape(tmp_path):
    src, dst = tmp_path / 'reference', tmp_path / 'copy'
    src.mkdir(); dst.mkdir(); make_gotm(src)

