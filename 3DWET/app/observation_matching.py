"""Strict time/depth matching shared by plots and objective functions."""
from datetime import datetime
from bisect import bisect_left
import math
import numpy as np


def _clock(value):
    if isinstance(value, datetime):
        return value
    text = str(value).strip().replace('Z', '+00:00')
    return datetime.fromisoformat(text)


def _unit(value):
    text = str(value or '').strip().lower().replace('μ', 'u').replace('µ', 'u').replace(' ', '')
    aliases = {'c': 'degc', 'celsius': 'degc', 'degree_celsius': 'degc', 'degrees_celsius': 'degc',
               'mg/l': 'mg/l', 'g/m3': 'g/m3', 'g/m^3': 'g/m3',
               'gn/m3': 'gn/m3', 'gn/m^3': 'gn/m3',
               'gp/m3': 'gp/m3', 'gp/m^3': 'gp/m3',
               'go2/m3': 'go2/m3', 'go2/m^3': 'go2/m3',
               'gdw/m3': 'gdw/m3', 'gdw/m^3': 'gdw/m3',
               'ug/l': 'ug/l', 'mg/m3': 'mg/m3', 'mg/m^3': 'mg/m3'}
    return aliases.get(text, text)


def _convert(value, source, target, mass_basis=None):
    a, b = _unit(source), _unit(target)
    # Dry-weight concentration is valid for variables registered by FABM with
    # gDW/m3 (for example diatoms_sDW). It is comparable only to itself;
    # never infer a carbon, nitrogen, phosphorus, or wet-mass conversion.
    known = {'degc', 'mg/l', 'g/m3', 'gn/m3', 'gp/m3', 'go2/m3', 'gdw/m3', 'ug/l', 'mg/m3'}
    if a not in known or b not in known:
        raise ValueError('unknown_or_missing_unit')
    if a == b:
        return value, 1.0
    # Generic g/m3 is compatible with a basis-qualified concentration only
    # after pair_observations has confirmed the same explicit O2/N/P basis.
    # Never use the generic label to infer which element the observation holds.
    basis_units = {'N': 'gn/m3', 'P': 'gp/m3', 'O2': 'go2/m3'}
    expected = basis_units.get(str(mass_basis or '').strip().upper())
    if expected and (a, b) in {('g/m3', expected), (expected, 'g/m3')}:
        return value, 1.0
    factors = {('mg/l', 'g/m3'): 1.0, ('g/m3', 'mg/l'): 1.0,
               ('mg/l', 'gn/m3'): 1.0, ('gn/m3', 'mg/l'): 1.0,
               ('mg/l', 'gp/m3'): 1.0, ('gp/m3', 'mg/l'): 1.0,
               ('mg/l', 'go2/m3'): 1.0, ('go2/m3', 'mg/l'): 1.0,
               ('ug/l', 'mg/m3'): 1.0, ('mg/m3', 'ug/l'): 1.0}
    if (a, b) not in factors:
        raise ValueError('incompatible_or_unknown_unit')
    factor = factors[(a, b)]
    return value * factor, factor


def _series(values, depths, index):
    v = np.asarray(values, dtype=float)
    z = np.asarray(depths, dtype=float)
    # A preselected station column may be [depth], [1, depth], or [depth,1].
    v = np.squeeze(v)
    z = np.squeeze(z)
    if v.ndim == 0:
        v = v.reshape(1)
    if z.ndim == 0:
        z = z.reshape(1)
    if v.ndim > 1 or z.ndim > 1 or v.size != z.size:
        raise ValueError('model values and center_depth must describe one selected column')
    if not np.isfinite(v).all() or not np.isfinite(z).all() or np.any(z < 0):
        raise ValueError('invalid_model_values_or_geometry')
    order = np.argsort(z)
    z, v = z[order], v[order]
    if len(z) > 1 and np.any(np.diff(z) <= 0):
        raise ValueError('duplicate_or_invalid_layer_centers')
    return z, v


def _model_time_index(model):
    """Parse and validate the model clock once per pairing operation."""
    clocks = [_clock(t) for t in model.get('times', [])]
    if len(clocks) != len(model.get('values', [])) or len(clocks) != len(model.get('center_depth', [])):
        raise ValueError('model time/value/geometry lengths differ')
    if not clocks:
        raise LookupError('no_time_overlap')
    strictly_increasing = all((clocks[i+1]-clocks[i]).total_seconds() > 0
                              for i in range(len(clocks)-1))
    return clocks, strictly_increasing


def _at_time_index(clocks, when, strictly_increasing=True):
    if not clocks:
        raise LookupError('no_time_overlap')
    if (clocks[0].tzinfo is None) != (when.tzinfo is None):
        raise ValueError('time_basis_mismatch')
    if not strictly_increasing:
        raise ValueError('model_times_not_strictly_increasing')
    if when < clocks[0] or when > clocks[-1]:
        raise LookupError('no_time_overlap')
    # Equivalent to the prior first t >= when scan, with O(log n) lookup.
    right = bisect_left(clocks, when)
    left = max(0, right-1)
    if clocks[right] == when:
        left = right
    nearest_gap = min((when-clocks[left]).total_seconds(),
                      (clocks[right]-when).total_seconds()) / 3600
    return left, right, 0.0 if right == left else (when-clocks[left]).total_seconds()/(clocks[right]-clocks[left]).total_seconds(), nearest_gap


def _at_time(model, when):
    """Compatibility wrapper for callers that resolve one timestamp."""
    clocks, strictly_increasing = _model_time_index(model)
    return _at_time_index(clocks, when, strictly_increasing)


def pair_observations(observations, model, max_time_gap_hours=None):
    """Pair each input row at its true time and depth; return pairs and exclusions.

    ``model`` must hold native ``times``, ``values`` and physical
    ``center_depth`` for exactly one resolved column. ``max_time_gap_hours``
    limits the observation's distance to its nearest bracketing native model
    timestamp; values between samples are linearly interpolated. Identity and scientific
    metadata are mandatory. A column-wide reference uses explicit
    ``representativeness='column'`` (e.g. official GOTM).
    """
    pairs, diagnostics, used = [], [], set()
    try:
        max_gap = float(max_time_gap_hours)
    except (TypeError, ValueError):
        max_gap = float('nan')
    if not math.isfinite(max_gap) or max_gap <= 0:
        return [], [{'reason': 'explicit_positive_max_time_gap_required'}]
    if model.get('calendar', 'standard') not in {'standard', 'gregorian', 'proleptic_gregorian'}:
        return [], [{'reason': 'incompatible_calendar'}]
    try:
        model_clocks, model_times_increasing = _model_time_index(model)
        model_time_error = None
    except (ValueError, LookupError) as exc:
        model_clocks = []
        model_times_increasing = False
        model_time_error = exc
    for index, obs in enumerate(observations):
        try:
            if obs.get('quality_flags') or any(str(q).lower() not in {'ok', 'good', 'valid', 'accepted'}
                                               for q in (obs.get('quality') or [])):
                raise LookupError('observation_quality_review')
            if obs.get('lake_id') is None or model.get('lake_id') != obs.get('lake_id'):
                raise LookupError('lake_mismatch')
            rep = model.get('representativeness')
            if model.get('station_id') is None:
                if rep != 'column':
                    raise LookupError('unknown_station')
            elif obs.get('station_id') != model.get('station_id'):
                raise LookupError('station_mismatch')
            elif (model.get('spatial_mapping') != 'verified' and not
                  (model.get('spatial_mapping') == 'explicit_cell' and
                   model.get('mapping_source') == 'gridstudio_explicit_cell')):
                raise LookupError('unknown_station_coordinates')
            if not obs.get('variable') or obs.get('variable') != model.get('variable'):
                raise LookupError('variable_mismatch')
            obs_basis = str(obs.get('mass_basis') or '').strip().upper()
            model_basis = str(model.get('mass_basis') or '').strip().upper()
            if obs_basis or model_basis:
                if not obs_basis and model_basis:
                    raise LookupError('mass_basis_requires_explicit_' + model_basis)
                if obs_basis and not model_basis:
                    raise LookupError('mass_basis_metadata_missing')
                if obs_basis != model_basis:
                    raise LookupError('mass_basis_conflict')
            raw_value = float(obs['value'])
            if not math.isfinite(raw_value):
                raise LookupError('non_finite_observation_value')
            converted, factor = _convert(raw_value, obs.get('unit'), model.get('unit'),
                                         mass_basis=model_basis if model_basis == obs_basis else None)
            depth = float(obs['depth_m'])
            if not math.isfinite(depth) or depth < 0:
                raise LookupError('invalid_observation_depth')
            when = _clock(obs['time'])
            if model_time_error is not None:
                raise model_time_error
            lo, hi, tw, gap = _at_time_index(model_clocks, when, model_times_increasing)
            if gap > max_gap:
                raise LookupError('time_gap_exceeds_limit')
            z0, v0 = _series(model['values'][lo], model['center_depth'][lo], lo)
            z1, v1 = (z0, v0) if hi == lo else _series(model['values'][hi], model['center_depth'][hi], hi)
            if depth < z0[0] or depth > z0[-1] or depth < z1[0] or depth > z1[-1]:
                raise LookupError('depth_outside_model_centers')
            def depth_interp(z, values):
                if len(z) == 1:
                    if not math.isclose(depth, z[0], abs_tol=1e-9):
                        raise LookupError('depth_outside_model_centers')
                    return float(values[0]), 0, 0, 0.0
                upper = min(max(int(np.searchsorted(z, depth, side='right')), 1), len(z)-1)
                lower = upper-1
                weight = (depth-z[lower])/(z[upper]-z[lower])
                return float(values[lower]*(1-weight)+values[upper]*weight), lower, upper, float(weight)
            a0, j0, k0, dw0 = depth_interp(z0, v0)
            a1, j1, k1, dw1 = (a0, j0, k0, dw0) if hi == lo else depth_interp(z1, v1)
            if len(z0) == 1:
                if not math.isclose(depth, z0[0], abs_tol=1e-9):
                    raise LookupError('depth_outside_model_centers')
            pair_key = ((obs.get('source_sha256'), obs.get('source_line')) if obs.get('source_sha256')
                        else (obs.get('lake_id'), obs.get('station_id'), obs.get('variable'), obs.get('time'),
                              obs.get('depth_m'), obs.get('value')))
            if pair_key in used:
                raise LookupError('observation_reused')
            used.add(pair_key)
            pairs.append({'observation': obs, 'observation_index': index,
                          'sim': float(a0*(1-tw)+a1*tw), 'obs': float(converted),
                          'model_times': [model['times'][lo], model['times'][hi]],
                          'time_weight': float(tw), 'depth_weight': float((1-tw)*dw0+tw*dw1),
                          'depth_layers': [[j0, k0], [j1, k1]],
                          'depth_weights': [dw0, dw1],
                          'unit_factor': float(factor), 'unit_from': obs.get('unit'), 'unit_to': model.get('unit'),
                          'observation_mass_basis': obs_basis or None,
                          'model_mass_basis': model_basis or None,
                          'model_mass_basis_source': model.get('mass_basis_source'),
                          'value_weights': [float((1-tw)*(1-dw0)), float((1-tw)*dw0), float(tw*(1-dw1)), float(tw*dw1)]})
        except LookupError as exc:
            diagnostics.append({'observation_index': index, 'source_line': obs.get('source_line'), 'reason': str(exc)})
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            diagnostics.append({'observation_index': index, 'source_line': obs.get('source_line'), 'reason': str(exc) or 'invalid_record'})
    if not pairs and not diagnostics and observations:
        diagnostics.append({'reason': 'no_time_overlap'})
    return pairs, diagnostics
