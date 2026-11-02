"""Ecological output must remain visible beside optional legacy hydro files."""
import ast
from collections import OrderedDict
from pathlib import Path
import threading
import netCDF4 as nc


def load_function():
    path = Path(__file__).resolve().parents[1] / '3DWET/app/server.py'
    function = next(n for n in ast.parse(path.read_text(encoding='utf-8')).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'find_output_files')
    def time_len(path):
        with nc.Dataset(path) as ds:
            return len(ds.dimensions['time'])
    scope = dict(Path=Path, _nc_time_len=time_len, nc_open=nc.Dataset, nc=nc,
                 _output_selection_cache=OrderedDict(),
                 _output_selection_cache_lock=threading.RLock())
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), scope)
    return scope['find_output_files']


def output(path, variables, records=2, start=0):
    path.parent.mkdir(parents=True, exist_ok=True)
    with nc.Dataset(path, 'w') as ds:
        ds.createDimension('time', records)
        time = ds.createVariable('time', 'f8', ('time',))
        time.units = 'hours since 2020-01-01 00:00:00'
        if records:
            time[:] = [start + index for index in range(records)]
        for name in variables:
            variable = ds.createVariable(name, 'f4', ('time',))
            if records:
                variable[:] = 1


def test_primary_ecology_is_preferred_but_legacy_velocity_accessible(tmp_path):
    primary = tmp_path / 'output/output.nc'
    legacy = tmp_path / 'output/lake.3d.nc'
    output(primary, ['temp', 'fish_sDW'])
    output(legacy, ['temp', 'uu'])
    find = load_function()
    assert find(tmp_path)['3d'] == primary
    assert find(tmp_path, 'fish_sDW')['3d'] == primary
    assert find(tmp_path, 'uu')['3d'] == legacy


def test_empty_root_cannot_hide_archived_data(tmp_path):
    output(tmp_path / 'output.nc', ['temp'], 0)
    archive = tmp_path / 'output/output.nc'
    output(archive, ['temp'])
    assert load_function()(tmp_path)['3d'] == archive


def test_newer_named_run_supersedes_stale_legacy_output(tmp_path):
    stale = tmp_path / 'output.nc'
    current_2d = tmp_path / 'ERKEN_METEO_PROXY_5D.2d.nc'
    current_3d = tmp_path / 'ERKEN_METEO_PROXY_5D.3d.nc'
    output(stale, ['temp', 'legacy_only'], records=20, start=0)
    output(current_2d, ['waterlevel'], records=120, start=0)
    output(current_3d, ['temp', 'oxygen'], records=120, start=0)

    find = load_function()
    assert find(tmp_path)['3d'] == current_3d
    assert find(tmp_path)['2d'] == current_2d
    assert find(tmp_path, 'temp')['3d'] == current_3d
    assert find(tmp_path, 'legacy_only')['3d'] == stale
