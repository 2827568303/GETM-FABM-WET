"""Loss-aware readers for scientific observation files.

Records deliberately keep source-naive clocks naive. Unknown metadata stays
unknown; import mapping is explicit and never inferred from a lake name.
"""
from collections import defaultdict
from datetime import date, datetime
import csv
import hashlib
import math
from pathlib import Path
from model_dates import parse_ordinal_date


FIELDS = ('time', 'value', 'depth_m', 'unit', 'variable', 'lake_id',
          'station_id', 'point_id', 'quality', 'source_file', 'source_line', 'source_sha256')


def _time(value):
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime(value.year, value.month, value.day)
    else:
        text = str(value or '').strip()
        if not text:
            raise ValueError('missing_time')
        dt = parse_ordinal_date(text)
        if dt is None:
            try:
                dt = datetime.fromisoformat(text.replace('Z', '+00:00'))
            except ValueError as exc:
                raise ValueError('invalid_time') from exc
    return dt.isoformat(sep=' ', timespec='microseconds' if dt.microsecond else 'seconds'), (
        'source_naive' if dt.tzinfo is None else 'source_offset')


def _number(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('invalid_' + name) from exc
    if not math.isfinite(result):
        raise ValueError('non_finite_' + name)
    return result


def _json_source(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _json_source(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_source(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def _header_row(mapping):
    value = mapping.get('header_row', 1)
    if isinstance(value, bool):
        raise ValueError('header_row_must_be_positive_integer')
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('header_row_must_be_positive_integer') from exc
    if parsed < 1 or str(value).strip() not in {str(parsed), f'{parsed}.0'}:
        raise ValueError('header_row_must_be_positive_integer')
    return parsed


def _rows(path, mapping=None):
    mapping = mapping or {}
    header_row = _header_row(mapping)
    suffix = path.suffix.lower()
    if suffix == '.obs':
        text = path.read_text(encoding='utf-8-sig')
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 4:
                yield line_no, None, 'expected_four_columns'
                continue
            yield line_no, {'time': parts[0] + ' ' + parts[1], 'source_time': parts[0] + ' ' + parts[1],
                            'source_depth': parts[2], 'depth_m': parts[2], 'value': parts[3],
                            'source_value': parts[3], 'source_row': line}, None
        return
    if suffix == '.csv':
        with path.open('r', encoding='utf-8-sig', newline='') as stream:
            for _ in range(header_row - 1):
                if stream.readline() == '':
                    raise ValueError('header_row_out_of_range')
            reader = csv.reader(stream)
            headers = next(reader, None)
            if not headers:
                return
            cursor = header_row
            while True:
                try:
                    values = next(reader)
                except StopIteration:
                    break
                line_no = cursor + 1
                cursor = header_row - 1 + reader.line_num
                row = dict(zip(headers, values))
                if len(values) > len(headers):
                    row[None] = values[len(headers):]
                for name in headers[len(values):]:
                    row[name] = None
                row['source_row'] = dict(row)
                yield line_no, row, None
        return
    if suffix in ('.xlsx', '.xlsm'):
        from openpyxl import load_workbook
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = book.active
            if header_row > sheet.max_row:
                raise ValueError('header_row_out_of_range')
            iterator = sheet.iter_rows(min_row=header_row, values_only=True)
            headers = next(iterator, ())
            names = [str(v).strip() if v is not None else '' for v in headers]
            for line_no, values in enumerate(iterator, header_row + 1):
                row = dict(zip(names, values))
                row['source_row'] = dict(row)
                yield line_no, row, None
        finally:
            book.close()
        return
    raise ValueError('unsupported_observation_format')


def parse_observations(path, mapping=None):
    """Return ``{records, diagnostics, source_sha256, row_count}``.

    mapping may define canonical fields (including ``time_column`` and
    ``value_column`` etc.). Diagnostics include original physical source lines.
    Conflicting duplicate keys are excluded from usable records and represented
    in diagnostics with all alternatives; exact duplicate rows fold with sources.
    """
    path = Path(path)
    mapping = dict(mapping or {})
    header_row = _header_row(mapping)
    depth_mode = mapping.get('depth_m_mode', 'column')
    if depth_mode not in {'column', 'constant'}:
        raise ValueError('depth_m_mode_must_be_column_or_constant')
    if depth_mode == 'constant' and str(mapping.get('depth_m_column', '')).strip():
        raise ValueError('constant_depth_requires_empty_depth_column')
    constant_depth = _number(mapping.get('depth_m_constant'), 'depth') if depth_mode == 'constant' else None
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    diagnostics, staged, row_count = [], [], 0
    def get(row, name, default=None):
        col = mapping.get(name + '_column', name)
        value = row.get(col, default) if isinstance(row, dict) else default
        if value in (None, ''):
            value = mapping.get(name, default)
        return value

    for line_no, row, row_error in _rows(path, mapping):
        row_count += 1
        if row_error:
            diagnostics.append({'source_file': path.name, 'source_line': line_no, 'reason': row_error})
            continue
        try:
            stamp, basis = _time(get(row, 'time'))
            value = _number(get(row, 'value'), 'value')
            depth_raw = constant_depth if depth_mode == 'constant' else get(row, 'depth_m')
            depth_value = _number(depth_raw, 'depth') if depth_raw not in (None, '') else None
            depth_sign = mapping.get('depth_sign', 'negative_down' if path.suffix.lower() == '.obs' else 'positive_down')
            if depth_sign not in {'positive_down', 'negative_down'}:
                raise ValueError('depth_sign_must_be_explicit')
            if depth_value is not None and depth_value < 0 and depth_sign != 'negative_down':
                raise ValueError('negative_depth_requires_downward_sign_mapping')
            depth = abs(depth_value) if depth_value is not None and depth_sign == 'negative_down' else depth_value
            quality_value = get(row, 'quality', '')
            quality = [q.strip() for q in str(quality_value).replace(';', ',').split(',') if q.strip()]
            quality_flags = [q for q in quality if q.lower() not in {'ok', 'good', 'valid', 'accepted'}]
            variable = get(row, 'variable')
            unit = get(row, 'unit')
            if path.suffix.lower() == '.obs' and not variable:
                raise ValueError('explicit_variable_mapping_required')
            if path.suffix.lower() == '.obs' and not unit:
                raise ValueError('explicit_unit_mapping_required')
            review_max = mapping.get('review_depth_max')
            if depth is not None and review_max is not None and depth > float(review_max):
                quality.append('depth_outside_review_range'); quality_flags.append('depth_outside_review_range')
            if path.suffix.lower() == '.obs':
                if str(variable).upper() == 'TEMP' and abs(value) > 40:
                    quality.append('physical_range_review'); quality_flags.append('physical_range_review')
            record = {'time': stamp, 'time_basis': basis, 'value': value, 'depth_m': depth,
                      'unit': unit, 'variable': variable,
                      'mass_basis': get(row, 'mass_basis'),
                      'lake_id': get(row, 'lake_id'), 'station_id': get(row, 'station_id'),
                      'point_id': get(row, 'point_id'),
                      'quality': sorted(set(quality)), 'quality_flags': sorted(set(quality_flags)), 'source_file': path.name,
                      'source_line': line_no, 'source_sha256': digest,
                      'source_time': _json_source(get(row, 'source_time', get(row, 'time'))),
                      'source_depth': _json_source(get(row, 'source_depth', depth_raw)),
                      'source_value': _json_source(get(row, 'source_value', get(row, 'value'))),
                      'source_row': _json_source(get(row, 'source_row', row)),
                      'sources': [{'source_file': path.name, 'source_line': line_no, 'source_sha256': digest}]}
            staged.append(record)
            if record['quality_flags']:
                diagnostics.append({'source_file': path.name, 'source_line': line_no,
                                    'reason': 'quality_review', 'quality': record['quality'],
                                    'quality_flags': record['quality_flags']})
        except (ValueError, TypeError) as exc:
            diagnostics.append({'source_file': path.name, 'source_line': line_no,
                                'reason': str(exc) or 'invalid_row'})

    records, duplicate_diagnostics = merge_observation_records(staged)
    diagnostics.extend(duplicate_diagnostics)
    diagnostics.sort(key=lambda d: str(d.get('source_line')))
    return {'records': records, 'diagnostics': diagnostics, 'source_sha256': digest,
            'source_file': path.name, 'row_count': row_count}


def merge_observation_records(records):
    """Fold identical full-key records and quarantine conflicting variants."""
    groups = defaultdict(list)
    for record in records:
        key = tuple(record.get(k) for k in ('lake_id', 'station_id', 'variable', 'time', 'depth_m'))
        if record.get('lake_id') is None:
            key += (record.get('source_sha256'), record.get('source_line'))
        groups[key].append(record)
    folded, diagnostics = [], []
    for key, group in groups.items():
        distinct = {(r.get('value'), r.get('unit'), r.get('mass_basis')) for r in group}
        if len(distinct) > 1:
            diagnostics.append({'source_file': group[0].get('source_file'),
                                'source_line': [r.get('source_line') for r in group],
                                'reason': 'conflicting_duplicate', 'key': list(key),
                                'alternatives': [{'value': r.get('value'), 'unit': r.get('unit'),
                                                 'mass_basis': r.get('mass_basis'), 'sources': r.get('sources', [])}
                                                for r in group]})
            continue
        first = dict(group[0])
        if len(group) > 1:
            first['sources'] = sorted(
                [source for r in group for source in r.get('sources', [])],
                key=lambda source: (str(source.get('source_file', '')),
                                    str(source.get('source_sha256', '')),
                                    source.get('source_line', 0)))
            for field in ('quality', 'quality_flags'):
                union = set()
                for record in group:
                    value = record.get(field) or []
                    union.update(value if isinstance(value, (list, tuple, set)) else [str(value)])
                first[field] = sorted(union)
            first['duplicate_count'] = len(group)
        folded.append(first)
    folded.sort(key=lambda r: (r.get('time') or '', r.get('source_line') or 0))
    return folded, diagnostics
