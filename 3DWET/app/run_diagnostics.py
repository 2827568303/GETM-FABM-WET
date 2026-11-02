"""Read-only run diagnostics and narrowly scoped, revision-guarded repairs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import math
import os
from pathlib import Path
import re
import tempfile
import uuid

import netCDF4 as nc
import numpy as np
from flask import jsonify, make_response, request

from project_api import _parse_scalars

# Known GETM logical fields only: a quoted title such as '.true.' is a string.
_LOGICAL_FIELDS = {
    'param': 'dryrun parallel hotstart use_epoch save_initial',
    'domain': 'f_plane check_cfl',
    'meteo': 'metforcing on_grid calc_met',
    'm3d': 'calc_temp calc_salt bdy3d bdy3d_tmrlx',
    'io_spec': 'save_metrics save_masks save_2d save_3d save_vel destag save_strho save_s save_t save_rho save_rad save_turb save_tke save_eps save_num save_nuh save_ss_nn save_taub save_meteo save_numerical_analyses',
    'getm_fabm': 'fabm',
    'diagnostics': 'diagnostics',
}


def quoted_logicals(original):
    _, parameters, _ = _parse_scalars(original)
    return [p for p in parameters
            if p['key'] in _LOGICAL_FIELDS.get(p['group'], '').split()
            and re.fullmatch(r"(['\"])\.(?:true|false)\.\1",p['value'],re.I)]


def _date(value):
    value = str(value or '').strip("'\"")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def forcing_coverage_details(case_path, config, context):
    """Inspect only time coordinates; never append or rewrite forcing records.

    GETM's input reader needs a record beyond stop for interpolation. Keep the
    existing application's one-day guard, but require the user to supply it.
    CF time units are interpreted by netCDF4, including hours and days.
    """
    time_cfg = config.get('time', {}) or {}
    stop, start = _date(time_cfg.get('stop')), _date(time_cfg.get('start'))
    if stop is None:
        return []
    details = []
    for filename in ('meteo.nc', 'rivers.nc'):
        path = Path(case_path) / filename
        if not path.exists():
            continue
        try:
            with context.nc_open(path) as ds:
                variable = ds.variables.get('time')
                if variable is None or len(variable) == 0:
                    raise ValueError('无时间步数据')
                values = np.ma.asarray(variable[:], dtype='f8')
                if (np.ma.is_masked(values) or values.ndim != 1 or not np.isfinite(values).all()
                        or (len(values) > 1 and not (np.diff(values) > 0).all())):
                    raise ValueError('时间轴须为有限、严格递增的一维序列')
                calendar = getattr(variable, 'calendar', 'standard')
                if calendar not in ('standard', 'gregorian', 'proleptic_gregorian'):
                    raise ValueError(f'不支持与公历模拟时段比较的 calendar={calendar}')
                dates = nc.num2date(values[[0, -1]], getattr(variable, 'units', ''),
                                   calendar=calendar, only_use_cftime_datetimes=False,
                                   only_use_python_datetimes=True)
                first = datetime(dates[0].year, dates[0].month, dates[0].day,
                                 dates[0].hour, dates[0].minute, dates[0].second)
                last = datetime(dates[1].year, dates[1].month, dates[1].day,
                                dates[1].hour, dates[1].minute, dates[1].second)
        except (OSError, ValueError, TypeError, OverflowError, RuntimeError) as exc:
            raise ValueError(f'{filename}: {exc}') from exc
        needed = stop + timedelta(days=1)
        if last < needed or (start is not None and first > start):
            details.append(dict(file=filename, first=first, last=last, needed=needed,
                                start_missing=start is not None and first > start,
                                end_missing=last < needed,
                                safe_stop=last - timedelta(days=1)))
    return details


def inspect_forcing_coverage(case_path, config, context):
    warnings = []
    for item in forcing_coverage_details(case_path, config, context):
        reason = []
        if item['start_missing']:
            reason.append(f"首条记录 {item['first']:%Y-%m-%d %H:%M} 晚于模拟开始")
        if item['end_missing']:
            reason.append(f"截止 {item['last']:%Y-%m-%d %H:%M}，需要覆盖至 {item['needed']:%Y-%m-%d %H:%M}")
        warnings.append(f"{item['file']}：" + '；'.join(reason) + '。请补充真实驱动数据或调整模拟时段；检查未改写数据。')
    return warnings


def case_revision(case):
    """Hash editable configuration and forcing/grid identity without reading large grids."""
    digest = hashlib.sha256()
    for name in ('getm.inp', 'output.yaml', 'fabm.yaml', 'getm_fabm.inp',
                 'bathymetry.nc', 'meteo.nc', 'rivers.nc'):
        path = case / name
        digest.update(name.encode())
        if path.exists():
            if path.is_symlink() or not path.is_file() or path.resolve().parent != case:
                raise ValueError(f'{name} 必须是案例目录内的普通文件')
            if name.endswith('.nc'):
                stat = path.stat()
                digest.update(f'{stat.st_size}:{stat.st_mtime_ns}'.encode())
            else:
                digest.update(path.read_bytes())
        else:
            digest.update(b'<missing>')
    return digest.hexdigest()


def _replace_scalar(original, group, key, value):
    lines, parameters, _ = _parse_scalars(original)
    parameter = next((p for p in parameters if p['group'] == group and p['key'] == key), None)
    if parameter is None:
        raise ValueError(f'{group}.{key} 未找到唯一可安全编辑的配置项，请定位后手动修改')
    index = parameter['line'] - 1
    lines[index] = lines[index][:parameter['_start']] + value + lines[index][parameter['_end']:]
    return ''.join(lines).encode('utf-8')


def _source_entries(text):
    """Only the final variables block is rewritten; reject ambiguous layouts."""
    blocks = list(re.finditer(r'^([ \t]*)variables\s*:\s*\r?$', text, re.M))
    if len(blocks) != 1:
        raise ValueError('output.yaml 需要唯一 variables 列表，请手动编辑复杂输出配置')
    block = blocks[0]
    tail = text[block.end():]
    source_pattern = re.compile(r'^([ \t]*)-\s*source\s*:\s*([^\r\n]+)', re.M)
    matches = list(source_pattern.finditer(tail))
    if not matches:
        raise ValueError('未找到可安全编辑的输出订阅')
    indent = len(block[1])
    item_indent = len(matches[0][1])
    if item_indent <= indent:
        raise ValueError('variables 列表缩进不一致，请手动编辑复杂输出配置')

    # Locate the first sibling key after the list. Keep it and its adjacent
    # comments/blank lines as an opaque suffix so only subscription entries
    # are rewritten. Refuse unexpected structures between the list and that
    # sibling instead of guessing their ownership.
    lines = tail.splitlines(keepends=True)
    offsets = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    first_source = matches[0].start()
    boundary_line = None
    for line_index, line in enumerate(lines):
        line_start = offsets[line_index]
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if line_start < first_source:
            raise ValueError('variables 列表前包含其他结构，请手动编辑复杂输出配置')
        line_indent = len(line) - len(line.lstrip(' \t'))
        if line_indent <= indent:
            boundary_line = line_index
            break
        if line_indent <= item_indent and not source_pattern.match(line):
            raise ValueError('variables 列表包含无法安全定位的结构，请手动编辑复杂输出配置')
    suffix_start = len(tail)
    if boundary_line is not None:
        suffix_start = offsets[boundary_line]
        # Comments and blank lines immediately before a sibling belong to the
        # untouched trailing configuration, not the last subscription item.
        previous = boundary_line - 1
        while previous >= 0 and (not lines[previous].strip() or lines[previous].lstrip().startswith('#')):
            suffix_start = offsets[previous]
            previous -= 1
    else:
        # Preserve trailing comments/spacing even when the list reaches EOF.
        previous = len(lines) - 1
        while previous >= 0 and (not lines[previous].strip() or lines[previous].lstrip().startswith('#')):
            suffix_start = offsets[previous]
            previous -= 1

    matches = [match for match in matches if match.start() < suffix_start]
    if not matches:
        raise ValueError('未找到可安全编辑的输出订阅')
    if any(len(match[1]) != item_indent for match in matches):
        raise ValueError('variables 列表缩进不一致，请手动编辑复杂输出配置')
    entries = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else suffix_start
        raw = match[2].strip()
        if ' #' in raw:
            raw = raw.split(' #', 1)[0].rstrip()
        entries.append((raw.strip("'\""), tail[match.start():end]))
    return text[:block.end()], matches[0][1], entries, tail[suffix_start:]


_REPAIRS = {
    'unquote_logicals': ('getm.inp', '修复逻辑值引号并保留原值'),
    'enable_cfl': ('getm.inp', '启用 CFL 检查'),
    'conservative_timestep': ('getm.inp', '采用保守时间步长（最多 2 秒）'),
    'fix_sync_interval': ('output.yaml', '设 sync_interval 为 1'),
    'remove_unregistered_sources': ('output.yaml', '移除未注册订阅'),
    'standard_output': ('output.yaml', '采用当前案例的标准输出订阅'),
    'resolve_output_sources': ('output.yaml', '转换为求解器支持的变量名称'),
    'shorten_stop_to_coverage': ('getm.inp', '将结束时间缩短到真实驱动覆盖范围'),
}


def _updated_config(case, action, context, original):
    if action == 'unquote_logicals':
        fields=quoted_logicals(original)
        if not fields:
            raise ValueError('没有可修复的带引号逻辑值')
        for field in fields:
            original=_replace_scalar(original,field['group'],field['key'],field['value'][1:-1])
        return original
    if action == 'enable_cfl':
        return _replace_scalar(original, 'domain', 'check_cfl', '.true.')
    if action == 'conservative_timestep':
        config = context.parse_getm_inp(case / 'getm.inp')
        maximum, _ = context._cfl_max_timestep(case)
        current = (config.get('time', {}) or {}).get('timestep')
        try:
            current = float(current)
        except (TypeError, ValueError):
            current = None
        if maximum is None or not math.isfinite(float(maximum)) or maximum <= 0:
            raise ValueError('无法估计 CFL 上限，请手动检查网格与时间步长')
        recommended = min(2., float(maximum) * .8)
        if current is not None and math.isfinite(current) and 0 < current <= maximum:
            raise ValueError('当前时间步长已通过 CFL 检查，请保留并检查短时运行结果')
        return _replace_scalar(original, 'time', 'timestep', f'{recommended:.8g}')
    if action == 'shorten_stop_to_coverage':
        config = context.parse_getm_inp(case / 'getm.inp')
        details = forcing_coverage_details(case, config, context)
        start = _date((config.get('time', {}) or {}).get('start'))
        stop = _date((config.get('time', {}) or {}).get('stop'))
        if not details or any(d['start_missing'] for d in details):
            raise ValueError('无法只靠缩短结束时间补足驱动覆盖，请补充真实数据')
        safe_stop = min(d['safe_stop'] for d in details)
        if start is None or stop is None or not start < safe_stop < stop:
            raise ValueError('现有驱动数据不足以形成有效模拟时段，请补充真实数据')
        return _replace_scalar(original, 'time', 'stop', f"'{safe_stop:%Y-%m-%d %H:%M:%S}'")
    text = original.decode('utf-8')
    if action == 'fix_sync_interval':
        matches = list(re.finditer(r'^(\s*sync_interval\s*:\s*)([-+0-9.eE]+)', text, re.M))
        if len(matches) != 1:
            raise ValueError('未找到唯一 sync_interval 配置项，请定位后手动修改')
        match = matches[0]
        value = float(match[2])
        if math.isfinite(value) and value >= 1:
            raise ValueError('sync_interval 已有效，无需修复')
        return (text[:match.start(2)] + '1' + text[match.end(2):]).encode('utf-8')
    head, indent, entries, suffix = _source_entries(text)
    newline = '\r\n' if '\r\n' in text else '\n'
    if action == 'resolve_output_sources':
        sources = context._resolve_output_sources(case, [source for source, _ in entries], context)
        body = ''.join(f'{indent}- source: {source}{newline}' for source in sources)
        return (head + newline + body + suffix).encode('utf-8')
    if action == 'remove_unregistered_sources':
        invalid = set(context._OUTPUT_UNREGISTERED)
        kept = [entry for source, entry in entries if source not in invalid]
        if len(kept) == len(entries):
            raise ValueError('订阅中没有已知的未注册变量')
        if not kept:
            raise ValueError('移除后没有输出变量，请使用标准输出订阅或手动选择')
        body = ''.join(kept)
    elif action == 'standard_output':
        sources = context._preset_sources(case, 'standard')
        if not sources or '*' in sources or any(s in context._OUTPUT_UNREGISTERED for s in sources):
            raise ValueError('当前案例没有可靠的标准输出订阅，请手动选择')
        body = ''.join(f'{indent}- source: {source}{newline}' for source in dict.fromkeys(sources))
    else:
        raise ValueError('不支持此修复动作')
    return (head + newline + body + suffix).encode('utf-8')


def _check_action(check, case, context):
    title, detail = str(check.get('title', '')), str(check.get('detail', ''))
    source, page, control, selector, repair, code = 'getm.inp', 'time', 'time-dt', None, None, 'configuration'
    if '逻辑值引号' in title:
        code, page, control, repair = 'quoted-logicals', 'projecttools', 'physics-rows', 'unquote_logicals'
    elif 'check_cfl' in title:
        code, page, control, selector, repair = 'cfl-disabled', 'projecttools', 'physics-rows', '[aria-label="domain.check_cfl"]', 'enable_cfl'
    elif '步长无效' in title or '步长超过' in title:
        code, repair = 'timestep-invalid' if '无效' in title else 'timestep-cfl', 'conservative_timestep'
    elif 'CFL 无法' in title:
        code, source, page, control = 'cfl-unavailable', 'bathymetry.nc', 'preprocess', 'pp-grid-canvas'
    elif '水位基准' in title:
        code, page, control = 'elevation-datum', 'initial', 'ic-elev'
    elif '地形' in title:
        code, source, page, control = 'bathymetry', 'bathymetry.nc', 'preprocess', 'pp-grid-canvas'
    elif 'getm.inp' in title:
        code, page, control = 'missing-namelist', 'input', 'build-dt'
    elif 'sync_interval' in title:
        code, source, control, repair = 'output-sync', 'output.yaml', 'output-sync-interval', 'fix_sync_interval'
    elif '未注册变量' in title:
        code, source, control, repair = 'output-unregistered', 'output.yaml', 'output-modules', 'remove_unregistered_sources'
    elif '订阅需要转换' in title:
        code, source, control, repair = 'output-legacy', 'output.yaml', 'output-modules', 'resolve_output_sources'
    elif '订阅无效' in title:
        code, source, control, repair = 'output-invalid', 'output.yaml', 'output-modules', 'standard_output'
    elif '全部变量' in title:
        code, source, control, repair = 'output-all', 'output.yaml', 'output-modules', 'standard_output'
    elif 'output.yaml' in title or '输出体积' in title or '磁盘空间' in title:
        code, source, control = 'output-settings' if '磁盘' not in title else 'disk-space', 'output.yaml', 'output-modules'
    elif '驱动' in title:
        source = 'rivers.nc' if 'rivers.nc' in detail else 'meteo.nc'
        code, page, control = 'forcing-' + source.split('.')[0], 'input', 'river-add-name' if source == 'rivers.nc' else 'meteo-csv-file'
        if '覆盖' in title:
            try:
                config = context.parse_getm_inp(case / 'getm.inp')
                details = forcing_coverage_details(case, config, context)
                start = _date((config.get('time', {}) or {}).get('start'))
                stop = _date((config.get('time', {}) or {}).get('stop'))
                if details and start and stop and not any(d['start_missing'] for d in details) and start < min(d['safe_stop'] for d in details) < stop:
                    repair = 'shorten_stop_to_coverage'
            except ValueError:
                pass
    elif '空壳' in title:
        match = re.search(r'([^\s/\\]+\.nc)', detail)
        source = match[1] if match else 'output.nc'
        code, page, control = 'empty-output-' + source, 'input', 'input-files-table'
    target = dict(page=page, control=control, file=source)
    if selector:
        target['selector'] = selector
    check.update(id=code, source_file=source, target=target,
                 actions=[dict(type='locate', label='定位设置', **target)])
    if repair and check.get('level') in ('warn', 'error'):
        filename, label = _REPAIRS[repair]
        check['repair'] = dict(id=repair, label=label, file=filename)
        check['actions'].append(dict(type='repair', **check['repair']))
    return check


def register_run_diagnostic_routes(app, context):
    """Wrap the legacy read-only checker; register after /api/run/check exists.

    Integration must replace the legacy _ensure_forcing_coverage call with
    inspect_forcing_coverage(..., context). Never monkeypatch shared globals.
    """
    original_check = app.view_functions['run_check']

    def checked():
        with context._NC_LOCK:
            try:
                response = make_response(original_check())
                data = response.get_json()
                if response.status_code != 200 or not isinstance(data, dict) or not context.active_case_path:
                    return response
                case = Path(context.active_case_path).resolve()
                if (case/'getm.inp').is_file():
                    fields=quoted_logicals((case/'getm.inp').read_bytes())
                    if fields:
                        data.setdefault('checks',[]).append(dict(level='error',title='逻辑值引号无效',
                            detail='GETM 逻辑值不能带引号：'+', '.join(p['group']+'.'+p['key'] for p in fields),
                            fix='只移除已知逻辑配置项的引号，保留真假值、注释和其他配置。'))
                        data['blocking']=int(data.get('blocking',0))+1
                        data['ok']=False
                seen = {}
                for check in data.get('checks', []):
                    _check_action(check, case, context)
                    code = check['id']
                    seen[code] = seen.get(code, 0) + 1
                    if seen[code] > 1:
                        check['id'] = f'{code}-{seen[code]}'
                data.update(case_path=str(case), revision=case_revision(case),
                            n_warn=sum(c.get('level') == 'warn' for c in data.get('checks', [])))
                return jsonify(data)
            except (ValueError, OSError, UnicodeError) as exc:
                return jsonify(error=str(exc)), 400

    app.view_functions['run_check'] = checked

    @app.post('/api/run/repair')
    def repair_run_configuration():
        with context._NC_LOCK:
            temporary = None
            backup = None
            try:
                data = request.get_json(silent=True)
                if not isinstance(data, dict):
                    raise ValueError('请求必须为 JSON 对象')
                if not context.active_case_path:
                    return jsonify(error='请先加载案例'), 409
                case = Path(context.active_case_path).resolve()
                if context.run_status == 'running':
                    return jsonify(error='模型运行中，请结束运行后修复'), 409
                if data.get('case_path') != str(case):
                    return jsonify(error='当前案例已变化，请重新体检'), 409
                if data.get('revision') != case_revision(case):
                    return jsonify(error='配置或输入文件已变化，请重新体检'), 409
                action = data.get('action')
                if not isinstance(action, str) or action not in _REPAIRS:
                    raise ValueError('不支持此修复动作，请定位后手动编辑')
                filename, _ = _REPAIRS[action]
                path = case / filename
                if path.is_symlink() or path.resolve().parent != case or not path.is_file():
                    raise ValueError('未找到案例目录内的配置文件，请定位后手动编辑')
                original = path.read_bytes()
                updated = _updated_config(case, action, context, original)
                if updated == original:
                    raise ValueError('配置已满足此修复，无需修改')
                directory = case / 'backups'
                if directory.is_symlink() or directory.resolve().parent != case:
                    raise ValueError('备份目录必须位于案例目录内')
                directory.mkdir(exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '-' + uuid.uuid4().hex[:8]
                backup = directory / (filename + '.' + stamp + '.bak')
                with backup.open('xb') as stream:
                    stream.write(original)
                    stream.flush()
                    os.fsync(stream.fileno())
                descriptor, tmp = tempfile.mkstemp(prefix='.' + filename + '-', suffix='.tmp', dir=case)
                temporary = Path(tmp)
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(updated)
                    stream.flush()
                    os.fsync(stream.fileno())
                cached = context.parse_getm_inp(temporary) if filename == 'getm.inp' else None
                # Also reject external editors or legacy case switches that do
                # not yet participate in the shared runtime lock.
                if (not context.active_case_path or Path(context.active_case_path).resolve() != case
                        or context.run_status == 'running' or data['revision'] != case_revision(case)):
                    return jsonify(error='案例、配置或运行状态已变化，请重新体检', backup=str(backup)), 409
                os.replace(temporary, path)
                if cached is not None:
                    context.cached_getm_config = cached
                return jsonify(success=True, action=action, file=filename, backup=str(backup),
                               case_path=str(case), revision=case_revision(case))
            except (ValueError, OSError, UnicodeError, TypeError, OverflowError) as exc:
                return jsonify(error=str(exc), backup=str(backup) if backup else None), 400
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
