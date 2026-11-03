"""Focused correctness checks for bounded MPI NetCDF output assembly."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from netCDF4 import Dataset

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "merge_getm_rank_outputs", ROOT / "3DWET/scripts/merge_getm_rank_outputs.py"
)
MERGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MERGER)


def _write_fixture(folder, *, conflict=False, mask_conflict=False, schema_conflict=False, missing=False):
    ref_path = folder / "reference.nc"
    yy, xx = np.mgrid[:3, :4]
    with Dataset(ref_path, "w") as ds:
        ds.createDimension("yc", 3)
        ds.createDimension("xc", 4)
        lon = ds.createVariable("lonc", "f8", ("yc", "xc"))
        lat = ds.createVariable("latc", "f8", ("yc", "xc"))
        lon[:] = xx + 100
        lat[:] = yy + 20
    shards = []
    blocks = [(0, 3), (2, 4)]
    if missing:
        blocks = [(0, 1), (2, 4)]
    t = np.arange(19, dtype="f8")
    for rank, (x0, x1) in enumerate(blocks):
        path = folder / f"rank{rank}.nc"
        shards.append(path)
        with Dataset(path, "w") as ds:
            ds.createDimension("time", None)
            ds.createDimension("yc", 3)
            ds.createDimension("xc", x1 - x0)
            ds.createDimension("sigma", 2)
            ds.setncattr("title", "fixture")
            time = ds.createVariable("time", "f8", ("time",))
            time.units = "seconds since start"
            time[:] = t
            ycoord = ds.createVariable("yc", "i4", ("yc",))
            ycoord[:] = np.arange(3)
            xcoord = ds.createVariable("xc", "i4", ("xc",))
            xcoord[:] = np.arange(x0, x1)
            lon = ds.createVariable("lonc", "f8", ("yc", "xc"))
            lat = ds.createVariable("latc", "f8", ("yc", "xc"))
            lon[:] = np.broadcast_to(np.arange(x0, x1) + 100, (3, x1 - x0))
            lat[:] = np.broadcast_to(np.arange(3)[:, None] + 20, (3, x1 - x0))
            state_type = "f8" if schema_conflict and rank == 1 else "f4"
            state = ds.createVariable("state", state_type, ("time", "yc", "xc"), fill_value=-9999)
            state.units = "test"
            vals = np.broadcast_to(t[:, None, None] + np.arange(3)[None, :, None] * 10 + np.arange(x0, x1)[None, None, :], (19, 3, x1 - x0)).copy()
            if conflict and rank == 1:
                vals[:, :, 0] += 2
            if mask_conflict and rank == 1:
                vals = np.ma.array(vals, mask=np.zeros(vals.shape, dtype=bool))
                vals.mask[:, :, 0] = True
            state[:] = vals
            field3 = ds.createVariable("field3", "f4", ("time", "sigma", "yc", "xc"), fill_value=-9999)
            field3[:] = np.broadcast_to(vals[:, None, :, :], (19, 2, 3, x1 - x0))
            ordered = ds.createVariable("ordered", "f4", ("yc", "time", "xc", "sigma"), fill_value=-9999)
            ordered[:] = np.broadcast_to(vals.transpose(1, 0, 2)[..., None], (3, 19, x1 - x0, 2))
            ds.createVariable("ioff", "i4").assignValue(1)
    return ref_path, shards


def test_merger_streams_time_chunks_and_preserves_schema_and_values(tmp_path):
    reference, shards = _write_fixture(tmp_path)
    dest = tmp_path / "merged.nc"
    MERGER.merge_rank_outputs(shards, reference, dest, time_chunk_records=8,
                              max_chunk_bytes=512)
    with Dataset(dest) as ds:
        assert ds.dimensions["time"].isunlimited()
        assert ds.dimensions["xc"].size == 4
        assert ds.getncattr("title") == "fixture"
        assert ds["state"].units == "test"
        expected = np.arange(19)[:, None, None] + np.arange(3)[None, :, None] * 10 + np.arange(4)[None, None, :]
        np.testing.assert_array_equal(ds["state"][:], expected.astype("f4"))
        np.testing.assert_array_equal(ds["field3"][:], np.broadcast_to(expected[:, None], (19, 2, 3, 4)))
        np.testing.assert_array_equal(ds["ordered"][:], np.broadcast_to(expected.transpose(1, 0, 2)[..., None], (3, 19, 4, 2)))
        assert ds["ioff"].getValue() == 0


def test_chunk_plan_reduces_time_records_to_fit_budget():
    time_axis, records, cells, bytes_per_cell = MERGER._chunk_plan(
        ("time", "sigma", "yc", "xc"), (10000, 2, 3, 4), "f4",
        4, 3, 8, 2500)
    assert time_axis == 0
    assert records == 2
    assert records * 3 * 4 * bytes_per_cell <= 2500
    assert records <= 8
    _, records, cells, bytes_per_cell = MERGER._chunk_plan(
        ("time", "sigma", "yc", "xc"), (10000, 2, 3000, 4000), "f4",
        4000, 3000, 8, 1024 * 1024)
    assert records == 1
    assert cells * bytes_per_cell <= 1024 * 1024
    for y0, y1, x0, x1 in MERGER._spatial_tiles(4000, 3000, cells):
        assert (y1-y0) * (x1-x0) * bytes_per_cell <= 1024 * 1024


def test_merger_applies_adaptive_temporal_chunks(tmp_path):
    reference, shards = _write_fixture(tmp_path)
    dest = tmp_path / "merged_adaptive.nc"
    MERGER.merge_rank_outputs(shards, reference, dest, time_chunk_records=8,
                              max_chunk_bytes=2500)
    expected = np.arange(19)[:, None, None] + np.arange(3)[None, :, None] * 10 + np.arange(4)[None, None, :]
    with Dataset(dest) as ds:
        np.testing.assert_array_equal(ds["state"][:], expected.astype("f4"))
        np.testing.assert_array_equal(ds["ordered"][:], np.broadcast_to(expected.transpose(1, 0, 2)[..., None], (3, 19, 4, 2)))


def test_merger_rejects_conflicting_overlap_without_publishing(tmp_path):
    reference, shards = _write_fixture(tmp_path, conflict=True)
    dest = tmp_path / "bad.nc"
    with pytest.raises(ValueError, match="Conflicting overlap values"):
        MERGER.merge_rank_outputs(shards, reference, dest, time_chunk_records=3,
                                  max_chunk_bytes=128)
    assert not dest.exists()
    assert not list(tmp_path.glob(".bad.nc.*.tmp"))


def test_merger_rejects_overlap_mask_conflict_without_publishing(tmp_path):
    reference, shards = _write_fixture(tmp_path, mask_conflict=True)
    dest = tmp_path / "bad_mask.nc"
    with pytest.raises(ValueError, match="Conflicting overlap masks"):
        MERGER.merge_rank_outputs(shards, reference, dest, time_chunk_records=3,
                                  max_chunk_bytes=128)
    assert not dest.exists()
    assert not list(tmp_path.glob(".bad_mask.nc.*.tmp"))


def test_merger_rejects_rank_schema_mismatch(tmp_path):
    reference, shards = _write_fixture(tmp_path, schema_conflict=True)
    with pytest.raises(ValueError, match="Variable schema mismatch"):
        MERGER.merge_rank_outputs(shards, reference, tmp_path / "schema.nc")


def test_merger_rejects_incomplete_global_coverage(tmp_path):
    reference, shards = _write_fixture(tmp_path, missing=True)
    with pytest.raises(ValueError, match="Incomplete coverage"):
        MERGER.merge_rank_outputs(shards, reference, tmp_path / "missing.nc")


def test_merger_places_cartesian_shards_on_bathymetry_xy(tmp_path):
    reference = tmp_path / "bathymetry.nc"
    with Dataset(reference, "w") as ds:
        ds.createDimension("x", 4)
        ds.createDimension("y", 3)
        ds.createVariable("x", "f8", ("x",))[:] = np.arange(4) * 10.0
        ds.createVariable("y", "f8", ("y",))[:] = np.arange(3) * 5.0
        # Present, but not the axes the Cartesian shards carry.
        ds.createVariable("lonc", "f8", ("y", "x"))[:] = 100.0
        ds.createVariable("latc", "f8", ("y", "x"))[:] = 20.0
    shards = []
    for rank, (x0, x1) in enumerate(((0, 2), (2, 4))):
        path = tmp_path / f"output.{rank:04d}.nc"
        shards.append(path)
        with Dataset(path, "w") as ds:
            ds.createDimension("time", None)
            ds.createDimension("yc", 3)
            ds.createDimension("xc", x1 - x0)
            ds.createVariable("time", "f8", ("time",))[:] = [0.0]
            ds.createVariable("yc", "f8", ("yc",))[:] = np.arange(3) * 5.0
            ds.createVariable("xc", "f8", ("xc",))[:] = np.arange(x0, x1) * 10.0
            temp = ds.createVariable("temp", "f4", ("time", "yc", "xc"), fill_value=-9999)
            temp[:] = np.arange(x0, x1)[None, None, :] + np.arange(3)[None, :, None]
    dest = tmp_path / "output.nc"
    MERGER.merge_rank_outputs(shards, reference, dest)
    with Dataset(dest) as ds:
        assert ds.dimensions["xc"].size == 4
        assert ds.dimensions["yc"].size == 3
        expected = np.arange(4)[None, None, :] + np.arange(3)[None, :, None]
        np.testing.assert_array_equal(ds["temp"][:], expected.astype("f4"))
        np.testing.assert_array_equal(ds["xc"][:], np.arange(4) * 10.0)


def test_merger_still_requires_lonlat_without_cartesian_axes(tmp_path):
    reference = tmp_path / "reference.nc"
    shard = tmp_path / "output.0000.nc"
    with Dataset(reference, "w") as ds:
        ds.createDimension("yc", 1)
        ds.createDimension("xc", 1)
        ds.createVariable("lonc", "f8", ("yc", "xc"))[:] = 1
        ds.createVariable("latc", "f8", ("yc", "xc"))[:] = 2
    with Dataset(shard, "w") as ds:
        ds.createDimension("time", None)
        ds.createDimension("yc", 1)
        ds.createDimension("xc", 1)
        ds.createVariable("temp", "f4", ("time", "yc", "xc"))[:] = 1
    with pytest.raises(ValueError, match="Shards require lonc and latc"):
        MERGER.merge_rank_outputs([shard], reference, tmp_path / "merged.nc")
