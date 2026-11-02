from pathlib import Path
import sys

import numpy as np
import pytest
from netCDF4 import Dataset

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from merge_getm_rank_outputs import merge_rank_outputs  # noqa: E402


def _reference(path):
    with Dataset(path, "w") as ds:
        ds.createDimension("yc", 3)
        ds.createDimension("xc", 2)
        lon = ds.createVariable("lonc", "f8", ("yc", "xc"))
        lat = ds.createVariable("latc", "f8", ("yc", "xc"))
        lon[:] = np.tile([10.0, 11.0], (3, 1))
        lat[:] = np.tile(np.arange(20.0, 23.0)[:, None], (1, 2))


def _rank(path, joff, *, ntime=1, mask_overlap=False, bad_yc=False,
          bad_field_dtype=False):
    nrow = 2
    with Dataset(path, "w") as ds:
        ds.createDimension("yc", nrow)
        ds.createDimension("xc", 2)
        ds.createDimension("time", ntime)
        lon = ds.createVariable("lonc", "f8", ("yc", "xc"))
        lat = ds.createVariable("latc", "f8", ("yc", "xc"))
        lon[:] = np.tile([10.0, 11.0], (nrow, 1))
        lat[:] = np.tile(np.arange(20.0 + joff, 22.0 + joff)[:, None], (1, 2))
        x = ds.createVariable("xc", "f8", ("xc",))
        y = ds.createVariable("yc", "f8", ("yc",))
        x[:] = [10.0, 11.0]
        y[:] = np.arange(20.0 + joff, 22.0 + joff)
        if bad_yc and joff:
            y[0] += 0.25
        time = ds.createVariable("time", "f8", ("time",))
        time[:] = np.arange(ntime)
        values = np.ones((ntime, nrow, 2), dtype="f4")
        mask = np.zeros(values.shape, dtype=bool)
        if mask_overlap and joff:
            mask[:, 0, 0] = True
        dtype = "f8" if bad_field_dtype else "f4"
        field = ds.createVariable("field", dtype, ("time", "yc", "xc"), fill_value=-999.0)
        field[:] = np.ma.array(values, mask=mask)


def _fixture(tmp_path, *, rank1_ntime=1, mask_overlap=False, bad_yc=False,
             bad_field_dtype=False):
    ref = tmp_path / "bathymetry.nc"
    _reference(ref)
    rank0, rank1 = tmp_path / "run.0000.nc", tmp_path / "run.0001.nc"
    _rank(rank0, 0)
    _rank(rank1, 1, ntime=rank1_ntime, mask_overlap=mask_overlap, bad_yc=bad_yc,
          bad_field_dtype=bad_field_dtype)
    return ref, [rank0, rank1]


def test_rejects_spatial_schema_with_different_time_extent_and_cleans_partial(tmp_path):
    ref, shards = _fixture(tmp_path, rank1_ntime=2)
    destination = tmp_path / "merged.nc"
    with pytest.raises(ValueError, match="Variable schema mismatch: time"):
        merge_rank_outputs(shards, ref, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".merged.nc.*.tmp"))


def test_rejects_field_dtype_schema_mismatch_and_cleans_partial(tmp_path):
    ref, shards = _fixture(tmp_path, bad_field_dtype=True)
    destination = tmp_path / "merged.nc"
    with pytest.raises(ValueError, match="Variable schema mismatch: field"):
        merge_rank_outputs(shards, ref, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".merged.nc.*.tmp"))


def test_rejects_mask_conflict_in_halo_overlap_and_cleans_partial(tmp_path):
    ref, shards = _fixture(tmp_path, mask_overlap=True)
    destination = tmp_path / "merged.nc"
    with pytest.raises(ValueError, match="overlap masks for field"):
        merge_rank_outputs(shards, ref, destination)
    assert not destination.exists()
    assert not list(tmp_path.glob(".merged.nc.*.tmp"))


def test_rejects_conflicting_one_dimensional_y_coordinate_overlap(tmp_path):
    ref, shards = _fixture(tmp_path, bad_yc=True)
    destination = tmp_path / "merged.nc"
    with pytest.raises(ValueError, match="overlap coordinate yc"):
        merge_rank_outputs(shards, ref, destination)
    assert not destination.exists()


def test_merges_consistent_overlap_and_normalizes_partition_offset(tmp_path):
    ref, shards = _fixture(tmp_path)
    destination = tmp_path / "merged.nc"
    merge_rank_outputs(shards, ref, destination)
    with Dataset(destination) as merged:
        assert merged.variables["field"].shape == (1, 3, 2)
        np.testing.assert_array_equal(merged.variables["yc"][:], [20.0, 21.0, 22.0])
        np.testing.assert_array_equal(merged.variables["field"][:], 1.0)
