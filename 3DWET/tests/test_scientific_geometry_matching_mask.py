import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))

from scientific_geometry import matching_input_dry_mask


class TrackedVariable:
    """NetCDF-like array that records reads and rejects whole-grid reads."""

    def __init__(self, values, units='', *, reject_whole_grid=False):
        self.values = np.ma.asarray(values)
        self.shape = self.values.shape
        self.units = units
        self.reads = []
        self.reject_whole_grid = reject_whole_grid

    def __getitem__(self, key):
        self.reads.append(key)
        if self.reject_whole_grid and key == (slice(None), slice(None)):
            raise AssertionError('bathymetry must be read in row blocks')
        return self.values[key]


def datasets(output_depth, input_depth, *, output_units='m', input_units='m',
             output_x=(1, 2, 3), input_x=(1, 2, 3), output_y=None, input_y=None):
    output_depth, input_depth = np.ma.asarray(output_depth), np.ma.asarray(input_depth)
    rows, cols = output_depth.shape
    if output_y is None:
        output_y = input_y = tuple(range(rows))
    output = TrackedVariable(output_depth, output_units, reject_whole_grid=True)
    reference = TrackedVariable(input_depth, input_units, reject_whole_grid=True)
    out = SimpleNamespace(variables={
        'bathymetry': output,
        'xc': TrackedVariable(output_x, 'm'), 'yc': TrackedVariable(output_y, 'm'),
    })
    grid = SimpleNamespace(variables={
        'bathymetry': reference,
        'x': TrackedVariable(input_x, 'm'), 'y': TrackedVariable(input_y, 'm'),
    })
    return out, grid, output, reference


def test_compares_every_native_cell_across_row_block_boundary_and_returns_slice():
    wet = np.full((130, 3), 5.0)
    source = wet.copy()
    # Same narrow dry channel in both files, crossing the 128-row block edge.
    wet[127:130, 1] = source[127:130, 1] = -4
    out, grid, output, reference = datasets(source, wet)

    result = matching_input_dry_mask(out, grid, wet.shape, slice(126, 130), slice(1, 3))

    expected = np.zeros((4, 2), dtype=bool)
    expected[:, 0] = [False, True, True, True]
    np.testing.assert_array_equal(result, expected)
    assert output.reads == reference.reads
    assert len(output.reads) >= 2
    assert all(isinstance(key, tuple) and isinstance(key[0], slice)
               and key[0].stop - key[0].start <= 128 for key in output.reads)


def test_rejects_single_cell_wet_topology_mismatch_in_later_block():
    source = np.full((130, 3), 5.0)
    reference = source.copy()
    reference[128, 1] = -2  # A one-cell narrow channel must not be sampled away.
    out, grid, *_ = datasets(source, reference)

    assert matching_input_dry_mask(out, grid, source.shape) is None


@pytest.mark.parametrize('bad_value', [np.nan, np.inf])
def test_invalid_values_in_both_grids_do_not_become_dry(bad_value):
    source = np.full((130, 3), 5.0)
    reference = source.copy()
    source[128, 1] = bad_value
    reference[128, 1] = bad_value
    out, grid, *_ = datasets(source, reference)

    result = matching_input_dry_mask(out, grid, source.shape)
    assert result is not None
    assert not result[128, 1]


def test_masked_values_in_both_grids_do_not_become_dry():
    source = np.ma.array(np.full((130, 3), 5.0), mask=False)
    reference = np.ma.array(np.full((130, 3), 5.0), mask=False)
    source[128, 1] = np.ma.masked
    reference[128, 1] = np.ma.masked
    out, grid, *_ = datasets(source, reference)

    result = matching_input_dry_mask(out, grid, source.shape)
    assert result is not None
    assert not result[128, 1]


def test_finite_input_dry_cell_can_fill_masked_output():
    source = np.ma.array(np.full((130, 3), 5.0), mask=False)
    reference = np.full((130, 3), 5.0)
    source[128, 1] = np.ma.masked
    reference[128, 1] = -7
    out, grid, *_ = datasets(source, reference)

    result = matching_input_dry_mask(out, grid, source.shape)

    assert result is not None
    assert result[128, 1]


@pytest.mark.parametrize('delta, expected', [(1.000009e-6, True), (1.02e-6, False)])
def test_wet_depth_comparison_keeps_existing_allclose_tolerance(delta, expected):
    source = np.full((130, 3), 1.0)
    reference = source.copy()
    reference[129, 2] += delta
    out, grid, *_ = datasets(source, reference)

    result = matching_input_dry_mask(out, grid, source.shape)

    assert (result is not None) is expected


def test_all_dry_grid_has_no_wet_identity_proof():
    source = np.full((130, 3), -2.0)
    reference = np.full((130, 3), -9.0)
    out, grid, *_ = datasets(source, reference)

    assert matching_input_dry_mask(out, grid, source.shape) is None


def test_matching_static_grid_returns_reference_dry_mask():
    source = np.full((130, 3), 5.0)
    reference = source.copy()
    source[0, 0] = reference[0, 0] = 0
    source[129, 2] = reference[129, 2] = -1
    reference[0, 0] = 0
    reference[129, 2] = -3
    out, grid, *_ = datasets(source, reference)

    result = matching_input_dry_mask(out, grid, source.shape)

    expected = np.zeros(source.shape, dtype=bool)
    expected[0, 0] = expected[129, 2] = True
    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize('output_units,input_units,axes_match', [
    ('ft', 'm', True), ('m', 'cm', True), ('m', 'm', False),
])
def test_rejects_unverified_units_or_axes(output_units, input_units, axes_match):
    source = np.full((130, 3), 5.0)
    out, grid, *_ = datasets(source, source, output_units=output_units,
                              input_units=input_units,
                              output_x=(1, 2, 3) if axes_match else (1, 2, 4))

    assert matching_input_dry_mask(out, grid, source.shape) is None

