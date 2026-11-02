"""Sampled display topology must be derived from every native bathymetry cell."""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '3DWET/app'))


def test_narrow_native_dry_cell_invalidates_the_whole_sampled_face_and_keeps_edges():
    from scientific_geometry import sampled_display_topology

    depth = np.full((3, 17), 4.0)
    depth[1, 1] = 0.0
    topology = sampled_display_topology(depth, [0, 1, 2], [0, 8, 16])

    assert topology['source_shape'] == [3, 17]
    assert topology['x_indices'] == [0, 8, 16]
    assert topology['y_indices'] == [0, 1, 2]
    assert topology['cell_status'] == [
        ['wet', 'wet', 'wet'],
        ['mixed', 'wet', 'wet'],
        ['wet', 'wet', 'wet'],
    ]
    assert topology['wet_mask'] == [[True] * 3, [False, True, True], [True] * 3]
    assert topology['land_mask'] == [[False] * 3 for _ in range(3)]
    assert topology['x_edges'] == [-0.5, 7.5, 15.5, 16.5]
    assert 'full_wet_mask' not in topology
    assert 'full_dry_mask' not in topology
    assert 'full_known_mask' not in topology
    assert topology['mask_cells_examined'] == 3 * 17
    assert topology['grid_hash'].startswith('sha256:')


def test_only_fully_dry_sample_blocks_become_land_and_wet_dry_interfaces_become_walls():
    from scientific_geometry import sampled_display_topology

    depth = np.full((2, 17), 4.0)
    depth[:, 8:] = 0.0
    topology = sampled_display_topology(depth, [0, 1], [0, 8, 16])

    assert topology['cell_status'] == [['wet', 'dry', 'dry'], ['wet', 'dry', 'dry']]
    assert topology['land_mask'] == [[False, True, True], [False, True, True]]
    assert topology['wall_sides'][0][0] == [False, True, False, False]
    assert topology['wall_sides'][0][1] == [False, False, False, False]


def test_unknown_native_cells_never_prove_a_wet_or_land_display_face():
    from scientific_geometry import sampled_display_topology

    depth = np.ma.array(np.full((2, 4), 5.0), mask=False)
    depth.mask[0, 1] = True
    depth[1, 1] = 0.0
    topology = sampled_display_topology(depth, [0, 1], [0, 2])

    assert topology['cell_status'][0] == ['unknown', 'wet']
    assert topology['wet_mask'][0] == [False, True]
    assert topology['land_mask'][0] == [False, False]
    assert 'full_known_mask' not in topology
    assert topology['cell_status'][0][0] == 'unknown'
    assert 'grid_hash' in topology


def test_million_cell_native_mask_does_not_expand_into_json_boolean_matrices():
    from scientific_geometry import sampled_display_topology
    import json

    depth = np.full((1000, 1000), 12.0)
    topology = sampled_display_topology(depth, range(0, 1000, 40), range(0, 1000, 40))
    assert topology['source_shape'] == [1000, 1000]
    assert not any(key.startswith('full_') for key in topology)
    assert topology['mask_cells_examined'] == 1_000_000
    assert len(json.dumps(topology, separators=(',', ':'))) < 100_000
