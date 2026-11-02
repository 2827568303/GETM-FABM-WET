"""Lossless result compression must preserve the classic NetCDF schema and data."""
import hashlib
import ast
import sys
import threading
from pathlib import Path

import netCDF4
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "3DWET" / "app"))


def _fixture(path):
    with netCDF4.Dataset(path, "w", format="NETCDF3_CLASSIC") as ds:
        ds.createDimension("time", None)
        ds.createDimension("sigma", 3)
        ds.createDimension("yc", 100)
        ds.createDimension("xc", 100)
        ds.title = "Dianchi lossless fixture"
        ds.history = "keep exact metadata"
        time = ds.createVariable("time", "f8", ("time",))
        time[:] = [86400.0]
        time.units = "seconds since 2020-01-01 00:00:00"
        ds.createVariable("lonc", "f4", ("yc", "xc"))[:] = np.broadcast_to(
            np.arange(100, dtype="f4"), (100, 100))
        state = ds.createVariable("temp", "f4", ("time", "sigma", "yc", "xc"), fill_value=-9999.0)
        state.long_name = "water temperature"
        state.units = "degree_Celsius"
        values = np.full((1, 3, 100, 100), 20, dtype="f4")
        values[0, 1, 50, 50] = -9999.0
        state[:] = values
        ds.createVariable("surface", "f4", ("time", "yc", "xc"))[:] = values[:, -1]
        ds.createVariable("scalar", "i4").assignValue(7)


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_compress_netcdf_preserves_every_attribute_dimension_and_value(tmp_path):
    from netcdf_compression import compress_netcdf_file

    path = tmp_path / "output.nc"
    _fixture(path)
    with netCDF4.Dataset(path) as before:
        before_globals = {name: before.getncattr(name) for name in before.ncattrs()}
        before_dims = {name: (len(dim), dim.isunlimited()) for name, dim in before.dimensions.items()}
        before_vars = {
            name: (var.dimensions, var.shape, str(var.dtype),
                   {attr: var.getncattr(attr) for attr in var.ncattrs()},
                   np.ma.asarray(var[:]) if var.ndim else np.ma.asarray(var[...]))
            for name, var in before.variables.items()
        }

    result = compress_netcdf_file(path)

    assert result["status"] == "compressed"
    assert result["compressed_bytes"] < result["original_bytes"]
    with netCDF4.Dataset(path) as after:
        assert after.data_model == "NETCDF4_CLASSIC"
        assert {name: after.getncattr(name) for name in after.ncattrs()} == before_globals
        assert {name: (len(dim), dim.isunlimited()) for name, dim in after.dimensions.items()} == before_dims
        assert list(after.variables) == list(before_vars)
        for name, (dims, shape, dtype, attrs, values) in before_vars.items():
            var = after.variables[name]
            assert (var.dimensions, var.shape, str(var.dtype)) == (dims, shape, dtype)
            assert {attr: var.getncattr(attr) for attr in var.ncattrs()} == attrs
            actual = np.ma.asarray(var[:] if var.ndim else var[...])
            np.testing.assert_array_equal(np.ma.getmaskarray(actual), np.ma.getmaskarray(values))
            np.testing.assert_array_equal(actual.filled(0), values.filled(0))
            if var.ndim:
                assert var.filters()["zlib"] is True
                assert var.chunking() is not None


def test_failed_compression_keeps_source_bytes_and_removes_temporary_file(tmp_path, monkeypatch):
    import netcdf_compression as module

    path = tmp_path / "output.nc"
    _fixture(path)
    original = _digest(path)
    real_dataset = module.Dataset

    def fail_target(filename, mode="r", **kwargs):
        if mode == "w":
            raise OSError("simulated target write failure")
        return real_dataset(filename, mode, **kwargs)

    monkeypatch.setattr(module, "Dataset", fail_target)
    result = module.compress_netcdf_file(path)

    assert result["status"] == "failed"
    assert _digest(path) == original
    assert list(tmp_path.iterdir()) == [path]


def test_cancelled_compression_keeps_source_bytes_and_cleans_staging_file(tmp_path):
    from netcdf_compression import compress_netcdf_file

    path = tmp_path / "output.nc"
    _fixture(path)
    original = _digest(path)

    result = compress_netcdf_file(path, cancelled=lambda: True)

    assert result["status"] == "cancelled"
    assert _digest(path) == original
    assert list(tmp_path.iterdir()) == [path]


def test_spatial_chunks_keep_small_grids_together_and_bound_large_chunks():
    from netcdf_compression import compression_chunksizes

    small = compression_chunksizes(("time", "sigma", "yc", "xc"), (20, 10, 82, 41), "f4")
    assert small == (4, 2, 82, 41)
    large = compression_chunksizes(("time", "sigma", "yc", "xc"), (100, 10, 3000, 4000), "f4")
    assert large[0] == 4 and large[1] == 2
    assert large[2] <= 128 and large[3] <= 128
    assert np.prod(large) * np.dtype("f4").itemsize <= 1024 * 1024


def test_compression_bounds_each_chunked_variable_cache_but_skips_classic(tmp_path):
    import netcdf_compression as module

    path = tmp_path / "chunk_cache_probe.nc"
    with netCDF4.Dataset(path, "w", format="NETCDF4_CLASSIC") as ds:
        ds.createDimension("time", 2)
        ds.createDimension("x", 4)
        chunked = ds.createVariable("chunked", "f4", ("time", "x"),
                                    chunksizes=(1, 4), zlib=True)
        module._limit_variable_chunk_cache(chunked)
        assert chunked.get_var_chunk_cache() == (128 * 1024, 1009, 0.75)

    classic_path = tmp_path / "classic_probe.nc"
    with netCDF4.Dataset(classic_path, "w", format="NETCDF3_CLASSIC") as ds:
        ds.createDimension("x", 4)
        contiguous = ds.createVariable("contiguous", "f4", ("x",))
        assert module._limit_variable_chunk_cache(contiguous) is None


def test_completed_getm_results_are_opt_in_and_restart_files_are_excluded(tmp_path):
    source = ROOT / "3DWET" / "app" / "server.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_compress_completed_getm_outputs")
    scope = {
        "Path": Path,
        "run_config": {"compress_results": False},
        "run_status": "running",
        "_NC_LOCK": threading.RLock(),
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), scope)
    output = tmp_path / "output.nc"
    three_d = tmp_path / "run.3d.nc"
    restart = tmp_path / "restart.nc"
    _fixture(output)
    _fixture(three_d)
    restart.write_bytes(b"keep restart byte-for-byte")
    original_output = _digest(output)
    logs = []

    assert scope["_compress_completed_getm_outputs"](tmp_path, logs)
    assert _digest(output) == original_output
    assert restart.read_bytes() == b"keep restart byte-for-byte"

    scope["run_config"]["compress_results"] = True
    assert scope["_compress_completed_getm_outputs"](tmp_path, logs)
    with netCDF4.Dataset(output) as ds:
        assert ds.data_model == "NETCDF4_CLASSIC"
    with netCDF4.Dataset(three_d) as ds:
        assert ds.data_model == "NETCDF4_CLASSIC"
    assert restart.read_bytes() == b"keep restart byte-for-byte"
    assert any("核验通过" in line for line in logs)


def test_native_vertical_slot_cache_keeps_all_result_variables(tmp_path):
    from result_layers import _padding_cache, physical_vertical_grid

    path = tmp_path / "large_inventory.nc"
    with netCDF4.Dataset(path, "w") as ds:
        ds.model = "GETM"
        for name, size in (("time", 1), ("sigma", 3), ("yc", 1), ("xc", 1)):
            ds.createDimension(name, size)
        ds.createVariable("sigma", "f4", ("sigma",))[:] = [-1, -0.5, 0]
        names = [f"field{i:03d}" for i in range(140)]
        for name in names:
            var = ds.createVariable(name, "f4", ("time", "sigma", "yc", "xc"), fill_value=-9999)
            var[:] = 1
            var[:, 0, :, :] = -9999
        for name in names:
            assert physical_vertical_grid(ds, ds[name])[0] == 1

    assert len(_padding_cache) >= 140


def test_run_control_enables_compression_by_default_but_can_be_disabled():
    template = (ROOT / "3DWET" / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    client = (ROOT / "3DWET" / "app" / "static" / "js" / "app.js").read_text(encoding="utf-8")
    server = (ROOT / "3DWET" / "app" / "server.py").read_text(encoding="utf-8")
    checkbox = next(line for line in template.splitlines() if 'id="compress-run-results"' in line)
    assert 'type="checkbox"' in checkbox and " checked" in checkbox
    assert "compress_results:compressResults" in client
    assert 'run_request.get("compress_results", True)' in server
