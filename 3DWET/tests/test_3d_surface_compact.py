import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'app'))

import server


def test_waterbody_compact_payload_keeps_render_inputs_and_summary_only():
    payload = {
        'shape': [1, 2, 2],
        'data': [[[1.0, None], [2.0, 3.0]]],
        'min': 1.0,
        'max': 3.0,
        'water_depth': [[4.0, 4.0], [4.0, 4.0]],
        'elevation': [[[1.0, None], [2.0, 3.0]]],
        'valid_geometry': [[True, False], [True, True]],
        'surface_synchronized': [[False, False], [True, True]],
        'depth': [[[1.0, None], [2.0, 3.0]]],
        'surface_elevation': [[0.0, None], [0.0, 0.0]],
        'barotropic_surface_elevation': [[0.0, None], [0.0, 0.0]],
        'surface_difference': [[0.0, None], [0.0, 0.0]],
    }

    compact = server.compact_3d_waterbody_payload(payload)

    assert compact['surface_sync_mismatch'] is True
    assert compact['data'] == payload['data']
    assert compact['min'] == payload['min'] and compact['max'] == payload['max']
    assert compact['water_depth'] == payload['water_depth']
    assert compact['elevation'] == payload['elevation']
    assert compact['valid_geometry'] == payload['valid_geometry']
    assert compact['depth'] == payload['depth']
    assert not ({'surface_synchronized', 'surface_elevation',
                 'barotropic_surface_elevation', 'surface_difference'} & compact.keys())


def test_waterbody_compact_payload_preserves_selected_layer_center_depth_exactly():
    depth = [[[0.03448, 0.76337]]]
    payload = {'shape': [1, 1, 2], 'layer_indices': [9], 'sigma': [0.0],
               'depth': depth, 'bottom': [[0.68940, 15.26806]]}

    compact = server.compact_3d_waterbody_payload(payload)

    assert compact['depth'] == depth
    assert compact['depth'][0][0][0] < compact['bottom'][0][0]


def test_waterbody_compact_payload_ignores_sync_mismatch_outside_valid_geometry():
    payload = {
        'valid_geometry': [[False, True]],
        'surface_synchronized': [[False, True]],
    }

    compact = server.compact_3d_waterbody_payload(payload)

    assert compact['surface_sync_mismatch'] is False
