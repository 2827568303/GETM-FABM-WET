"""Copy source projects and edit scalar namelists without rewriting formatting."""
import hashlib
import json
import math
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import jsonify, request


_INPUT_SUFFIXES = {'.inp', '.nml', '.yaml', '.yml', '.json', '.nc', '.txt',
                   '.dat', '.csv', '.tsv', '.asc', '.shp', '.shx', '.dbf',
                   '.prj', '.cpg', '.qpj', '.tif', '.tiff', '.grd'}
_EXCLUDED_DIRS = {'out', 'output', 'outputs', 'results', 'logs', 'log', 'backup',
                  'backups', 'cache', '__pycache__', 'node_modules', 'venv'}
_INTEGER = re.compile(r'[+-]?\d+\Z')
_REAL = re.compile(r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[edED][+-]?\d+)?\Z')
_STRING = re.compile(r"(?:'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\")\Z")
_ASSIGNMENT = re.compile(r'^(\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*)(.*)$')
_YAML_FIELD = re.compile(r'^\s*([^:#][^:]*?)\s*:\s*(.*?)\s*$')
_PATH_SUFFIXES = ('file', 'filename', 'filepath', 'path', 'directory', 'dir')


def _digest(content):
    return hashlib.sha256(content).hexdigest()


def _comment_start(line):
    """Find a Fortran comment while respecting quoted strings and doubled quotes."""
    quote = None
    i = 0
    while i < len(line):
        char = line[i]
        if quote:
            if char == quote:
                if i + 1 < len(line) and line[i + 1] == quote:
                    i += 2
                    continue
                quote = None
        elif char in "'\"":
            quote = char
        elif char == '!':
            return i
        i += 1
    return len(line)


def _scalar_type(value):
    if _INTEGER.fullmatch(value):
        return 'integer'
    if _REAL.fullmatch(value):
        return 'real'
    if value.lower() in ('.true.', '.false.'):
        return 'logical'
    if _STRING.fullmatch(value):
        return 'string'
    return None


def _parse_scalars(content):
    text = content.decode('utf-8')
    lines = text.splitlines(keepends=True)
    group = None
    parameters = []
    unsupported = 0
    for index, line in enumerate(lines):
        plain = line[:_comment_start(line)]
        stripped = plain.strip().lstrip('\ufeff')
        if stripped.startswith('&'):
            group = stripped[1:].strip().lower()
            continue
        if stripped in ('/', '&end'):
            group = None
            continue
        if not group or not stripped:
            continue
        assignment = _ASSIGNMENT.match(plain)
        if not assignment:
            if '=' in plain:
                unsupported += 1
            continue
        value = assignment[3].strip()
        if value.endswith(','):
            value = value[:-1].rstrip()
        kind = _scalar_type(value)
        if kind is None:
            unsupported += 1
            continue
        start = len(assignment[1])
        parameters.append(dict(group=group, key=assignment[2].lower(),
                               value=value, type=kind, line=index + 1,
                               _start=start, _end=start + len(value)))
    # Duplicate assignments cannot be mapped to a unique editable scalar.
    counts = {}
    for item in parameters:
        key = (item['group'], item['key'])
        counts[key] = counts.get(key, 0) + 1
    unique = [p for p in parameters if counts[(p['group'], p['key'])] == 1]
    return lines, unique, unsupported + len(parameters) - len(unique)


def _safe_source_file(path):
    name = path.name.lower()
    if name.startswith('.') or path.suffix.lower() not in _INPUT_SUFFIXES:
        return False
    if re.search(r'(?:secret|credential|password|token|(?:private|api)[_-]?key)', name):
        return False
    if re.search(r'(?:\.2d\.nc|\.3d\.nc|\.bak(?:\.|$)|\.log(?:\.|$)|backup)', name):
        return False
    if name in ('output.nc', 'restart.nc', 'import_manifest.json'):
        return False
    return not name.startswith(('history', 'restart', 'hotstart'))


def _is_path_field(key):
    normalized = str(key).strip().lower().replace('-', '_').replace(' ', '_')
    return any(normalized == suffix or normalized.endswith('_' + suffix) or normalized.endswith(suffix)
               for suffix in _PATH_SUFFIXES) or normalized.startswith(('path_', 'file_'))


def _decode_quoted(value):
    value = value.strip().rstrip(',').strip()
    if not _STRING.fullmatch(value):
        return None
    quote = value[0]
    return value[1:-1].replace(quote + quote, quote)


def _yaml_scalar(value):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            decoded = json.loads(value)
            return decoded if isinstance(decoded, str) else None
        except (ValueError, TypeError):
            return None
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1].replace("''", "'")
    if not value or value.lower() in ('null', '~', 'true', 'false'):
        return None
    if value[0] in '[{&*!|>':
        return None
    return value


def _path_references(path, content):
    suffix = path.suffix.lower()
    references = []
    if suffix in ('.inp', '.nml'):
        group = None
        for line_number, line in enumerate(content.decode('utf-8-sig').splitlines(), 1):
            plain = line[:_comment_start(line)].strip()
            if plain.startswith('&'):
                group = plain[1:].strip().lower()
                continue
            if plain in ('/', '&end'):
                group = None
                continue
            assignment = _ASSIGNMENT.match(line[:_comment_start(line)]) if group else None
            if not assignment or not _is_path_field(assignment[2]):
                continue
            value = _decode_quoted(assignment[3])
            if value is not None:
                references.append(dict(key=assignment[2], value=value, line=line_number))
    elif suffix == '.json':
        try:
            data = json.loads(content.decode('utf-8-sig'))
        except (ValueError, UnicodeError):
            return references

        def visit(value, prefix=''):
            if isinstance(value, dict):
                for key, child in value.items():
                    name = f'{prefix}.{key}' if prefix else str(key)
                    if _is_path_field(key) and isinstance(child, str):
                        references.append(dict(key=name, value=child, line=None))
                    else:
                        visit(child, name)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, f'{prefix}[{index}]')
        visit(data)
    elif suffix in ('.yaml', '.yml'):
        for line_number, line in enumerate(content.decode('utf-8-sig').splitlines(), 1):
            plain = line.strip()
            if not plain or plain.startswith('#'):
                continue
            match = _YAML_FIELD.match(line.split('#', 1)[0])
            if not match or not _is_path_field(match[1]):
                continue
            value = _yaml_scalar(match[2])
            if value is not None:
                references.append(dict(key=match[1].strip(), value=value, line=line_number))
    return references


def _path_reference_audit(source, target, copied_paths):
    source, target = source.resolve(), target.resolve()
    copied_paths = set(copied_paths)
    references = []
    counts = dict(copied=0, missing=0, absolute_source=0, absolute_external=0, outside_project=0)
    scanned_files = 0
    for config in sorted(source.rglob('*')):
        if not config.is_file() or config.is_symlink() or config.suffix.lower() not in ('.inp', '.nml', '.json', '.yaml', '.yml'):
            continue
        if not config.resolve().is_relative_to(source):
            continue
        relative_config = config.relative_to(source).as_posix()
        scanned_files += 1
        try:
            found = _path_references(config, config.read_bytes())
        except (OSError, UnicodeError):
            continue
        for item in found:
            value = item['value'].strip()
            # Environment substitutions, URL references, and globs need application-specific resolution.
            if not value or '://' in value or any(mark in value for mark in ('$(', '${', '%', '*', '?')):
                continue
            candidate = Path(value).expanduser()
            if candidate.is_absolute():
                resolved = candidate.resolve()
                if not resolved.is_relative_to(source):
                    status, relative_target = 'absolute_external', None
                else:
                    relative_target = resolved.relative_to(source).as_posix()
                    status = 'absolute_source'
            else:
                resolved = (source / candidate).resolve()
                if not resolved.is_relative_to(source):
                    status, relative_target = 'outside_project', None
                else:
                    relative_target = resolved.relative_to(source).as_posix()
                    status = 'copied' if relative_target in copied_paths else 'missing'
            counts[status] += 1
            record = dict(file=relative_config, key=item['key'], value=value, line=item['line'], status=status)
            if status == 'copied':
                record['target_relative_path'] = Path(relative_target).as_posix()
            references.append(record)
    return dict(scanned_files=scanned_files, counts=counts, references=references)


def register_project_routes(app, context):
    def active():
        if not context.active_case_path:
            raise ValueError('请先打开一个案例')
        return Path(context.active_case_path).resolve()

    def config_file(case, name):
        if not isinstance(name, str) or Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('配置文件名无效')
        if name not in ('getm.inp', 'getm_fabm.inp') and not name.lower().endswith('.nml'):
            raise ValueError('仅支持 GETM/GOTM namelist 文件')
        path = case / name
        if path.is_symlink() or path.resolve().parent != case:
            raise ValueError('配置文件必须位于案例目录内')
        if not path.is_file():
            raise ValueError('未找到配置文件，请先完成前处理')
        return path

    def payload(case, path, content):
        _, parameters, unsupported = _parse_scalars(content)
        visible = [{k: v for k, v in p.items() if not k.startswith('_')} for p in parameters]
        files = sorted(p.name for p in case.iterdir()
                       if p.is_file() and not p.is_symlink()
                       and (p.name in ('getm.inp', 'getm_fabm.inp') or p.suffix.lower() == '.nml'))
        return dict(case_path=str(case), file=path.name, revision=_digest(content),
                    parameters=visible, uneditable_lines=unsupported, files=files)

    @app.post('/api/projects/import')
    def import_project():
        with context._NC_LOCK:
            target = None
            created = False
            try:
                data = request.get_json(silent=True)
                if not isinstance(data, dict):
                    raise ValueError('请求必须为 JSON 对象')
                name = data.get('name', '')
                if (not isinstance(name, str) or not name.strip() or name != name.strip()
                        or name in ('.', '..') or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
                        or name.endswith(('.', ' '))
                        or re.fullmatch(r'(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', name, re.I)):
                    raise ValueError('请输入有效的案例名称')
                source_value = data.get('source_path')
                if not isinstance(source_value, str) or not source_value:
                    raise ValueError('请选择源项目目录')
                raw_source = Path(source_value).expanduser()
                if raw_source.is_symlink():
                    raise ValueError('不支持链接目录')
                source = raw_source.resolve()
                if source.is_file() and source.name == 'project.json':
                    source = source.parent
                if not source.is_dir() or not any((source / f).is_file() for f in ('getm.inp', 'bathymetry.nc', 'project.json')):
                    raise ValueError('源目录须包含 getm.inp、bathymetry.nc 或 project.json')
                if context.run_status == 'running':
                    return jsonify(error='模型运行中，请结束运行后导入'), 409
                root = Path(context.CASE_DIR).resolve()
                target = root / name
                if target.exists() or target.is_symlink():
                    raise ValueError('案例名称已存在')
                if target.resolve().parent != root or target.is_relative_to(source):
                    raise ValueError('导入目录不能位于源目录内部')
                target.mkdir(parents=True)
                created = True
                files = []
                skipped = []
                for directory, dirs, names in os.walk(source, followlinks=False):
                    base = Path(directory)
                    dirs[:] = [d for d in dirs if not d.startswith('.')
                               and d.lower() not in _EXCLUDED_DIRS and not (base / d).is_symlink()]
                    for filename in names:
                        original = base / filename
                        relative = original.relative_to(source)
                        if original.is_symlink() or not original.is_file() or not _safe_source_file(original):
                            skipped.append(relative.as_posix())
                            continue
                        if not original.resolve().is_relative_to(source):
                            raise ValueError('源项目包含目录外的文件')
                        destination = target / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        content = original.read_bytes()
                        destination.write_bytes(content)
                        files.append(dict(path=relative.as_posix(), source_sha256=_digest(content),
                                          copied_sha256=_digest(destination.read_bytes()), size=len(content)))
                if not files:
                    raise ValueError('源目录没有可导入的模型输入文件')
                needs = not (target / 'getm.inp').is_file() or not (target / 'bathymetry.nc').is_file()
                path_audit = _path_reference_audit(source, target, (item['path'] for item in files))
                manifest = dict(source_path=str(source), imported_at=datetime.now(timezone.utc).isoformat(),
                                needs_preprocessing=needs, files=files, skipped_files=skipped,
                                path_reference_audit=path_audit)
                (target / 'import_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
                return jsonify(success=True, case_path=str(target), case_name=name,
                               needs_preprocessing=needs, manifest=manifest)
            except (ValueError, OSError, UnicodeError) as exc:
                if created:
                    shutil.rmtree(target)
                return jsonify(error=str(exc)), 400

    @app.get('/api/physics/config')
    def get_physics_config():
        with context._NC_LOCK:
            try:
                case = active()
                path = config_file(case, request.args.get('file', 'getm.inp'))
                return jsonify(payload(case, path, path.read_bytes()))
            except (ValueError, OSError, UnicodeError) as exc:
                return jsonify(error=str(exc)), 400

    @app.post('/api/physics/config')
    def save_physics_config():
        with context._NC_LOCK:
            temporary = None
            try:
                data = request.get_json(silent=True)
                if not isinstance(data, dict):
                    raise ValueError('请求必须为 JSON 对象')
                case = active()
                if context.run_status == 'running':
                    return jsonify(error='模型运行中，请结束运行后编辑'), 409
                if data.get('case_path') != str(case):
                    return jsonify(error='当前案例已变化，请重新加载配置'), 409
                path = config_file(case, data.get('file', 'getm.inp'))
                original = path.read_bytes()
                if data.get('revision') != _digest(original):
                    return jsonify(error='配置已变化，请重新加载后再保存'), 409
                lines, parameters, _ = _parse_scalars(original)
                lookup = {(p['group'], p['key']): p for p in parameters}
                changes = data.get('changes')
                if not isinstance(changes, list):
                    raise ValueError('changes 必须为列表')
                seen = set()
                for change in changes:
                    if not isinstance(change, dict):
                        raise ValueError('参数修改格式无效')
                    key = (change.get('group'), change.get('key'))
                    if key not in lookup or key in seen:
                        raise ValueError('参数不可编辑或重复')
                    seen.add(key)
                    parameter = lookup[key]
                    value = change.get('value')
                    if not isinstance(value, str) or any(c in value for c in '\r\n\x00'):
                        raise ValueError('参数值必须为单行字符串')
                    value = value.strip()
                    kind = _scalar_type(value)
                    expected = parameter['type']
                    if kind != expected and not (expected == 'real' and kind == 'integer'):
                        raise ValueError('参数值类型不匹配')
                    if expected == 'real' and not math.isfinite(float(re.sub('[dD]', 'e', value))):
                        raise ValueError('参数值必须为有限数值')
                    index = parameter['line'] - 1
                    lines[index] = lines[index][:parameter['_start']] + value + lines[index][parameter['_end']:]
                updated = ''.join(lines).encode('utf-8')
                if updated == original:
                    return jsonify(success=True, **payload(case, path, original), backup=None)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '-' + uuid.uuid4().hex[:8]
                backups = case / 'backups'
                if backups.is_symlink() or backups.resolve().parent != case:
                    raise ValueError('备份目录必须位于案例内')
                backups.mkdir(exist_ok=True)
                backup = backups / (path.name + '.' + stamp + '.bak')
                backup.write_bytes(original)
                temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
                temporary.write_bytes(updated)
                parser = getattr(context, 'parse_getm_inp', None)
                cached = parser(temporary) if path.name == 'getm.inp' and parser else None
                os.replace(temporary, path)
                if cached is not None:
                    context.cached_getm_config = cached
                return jsonify(success=True, **payload(case, path, updated), backup=str(backup))
            except (ValueError, OSError, UnicodeError, TypeError, OverflowError) as exc:
                return jsonify(error=str(exc)), 400
            finally:
                if temporary is not None and temporary.exists():
                    temporary.unlink()
