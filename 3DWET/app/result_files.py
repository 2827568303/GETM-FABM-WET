"""Conservative case-local result inventory and reversible cleanup.

The caller supplies its model/calibration busy state and the shared NetCDF lock.
No output is removed automatically. Trash never leaves the selected case.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from contextlib import nullcontext
import hashlib
import json
import os
import re
import stat
import threading
import uuid
from flask import jsonify, request

_LOGS = {'model_run.log', 'run.log', 'visualize_run.log'}
_PROTECTED = re.compile(r'(meteo|bathy|topo|mask|initial|init[_.-]|input|forcing|river|boundary|hotstart|grid|config)', re.I)
_ARCHIVE = re.compile(r'(?:run|archive)[_-][a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}\Z')
_TOKEN = re.compile(r'[0-9a-f]{32}\Z')


class ResultError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _safe(case, path):
    """Reject every symlink/junction/reparse component, including the case."""
    path = Path(path)
    try:
        path.relative_to(case)
    except ValueError:
        raise ResultError('路径超出当前案例。')
    # Check ancestors too: resolve() alone would silently accept a junction.
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ResultError('不允许操作符号链接或重解析点。')
    if not path.resolve().is_relative_to(case.resolve()):
        raise ResultError('路径超出当前案例。')
    return path


def _relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ResultError('无效的相对路径。')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ResultError('无效的相对路径。')
    return p


def _allowed(value):
    p = _relative(value)
    parts = p.parts
    if len(parts) == 1:
        pass
    elif len(parts) == 2 and parts[0] == 'output':
        pass
    elif len(parts) == 3 and parts[0] == 'output' and _ARCHIVE.fullmatch(parts[1]):
        pass
    else:
        return False
    name = parts[-1]
    if _PROTECTED.search(name):
        return False
    return name in _LOGS or name in ('output.nc', 'restart.nc') or name.endswith(('.2d.nc', '.3d.nc'))


def _signature(path):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode):
        raise ResultError('只允许操作普通结果文件。')
    return [s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_dev, s.st_ino]


def _inventory(case):
    _safe(case, case)
    files = []
    dirs = [case]
    output = case / 'output'
    try:
        _safe(case, output)
        if output.is_dir():
            dirs.append(output)
            for p in output.iterdir():
                if p.is_dir() and _ARCHIVE.fullmatch(p.name):
                    try:
                        _safe(case, p)
                        dirs.append(p)
                    except ResultError:
                        pass
    except ResultError:
        pass
    for directory in dirs:
        for path in directory.iterdir():
            rel = path.relative_to(case).as_posix()
            if not _allowed(rel):
                continue
            try:
                _safe(case, path)
                sig = _signature(path)
            except (OSError, ResultError):
                continue
            files.append(dict(relative_path=rel, absolute_path=str(path), size=sig[0],
                              modified=datetime.fromtimestamp(sig[1] / 1e9, timezone.utc).isoformat(),
                              modified_ns=sig[1], kind='日志' if path.name in _LOGS else ('重启' if path.name == 'restart.nc' else '结果'),
                              duplicate_group=None, _signature=sig))
    files.sort(key=lambda f: f['relative_path'])
    revision = _digest([str(case), [[f['relative_path'], f['_signature']] for f in files]])
    for item in files:
        item['revision'] = revision
    return files, revision


def _public(files):
    return [{k: v for k, v in f.items() if not k.startswith('_')} for f in files]


def _manifests(case):
    root = _safe(case, case / '.studio-trash')
    manifests = []
    if not root.exists():
        return manifests
    if not root.is_dir():
        raise ResultError('回收区路径不是目录。')
    for directory in sorted(root.iterdir()):
        if not _TOKEN.fullmatch(directory.name):
            continue
        _safe(case, directory)
        manifest = _safe(case, directory / 'manifest.json')
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding='utf-8'))
            if data.get('case_path') != str(case) or data.get('token') != directory.name:
                raise ValueError()
            for item in data['files']:
                if not _allowed(item['relative_path']):
                    raise ValueError()
                stored = _safe(case, directory / 'files' / item['relative_path'])
                if stored.exists():
                    if _signature(stored) != item['signature']:
                        # rename changes ctime on some systems; content identity uses size/mtime/inode.
                        actual = _signature(stored)
                        if actual[:2] + actual[3:] != item['signature'][:2] + item['signature'][3:]:
                            raise ValueError()
                    item['stored_path'] = str(stored)
                else:
                    raise ValueError()
        except (ValueError, KeyError, TypeError, OSError):
            raise ResultError('回收区记录已改变，请检查后再操作。', 409)
        manifests.append(data)
    return manifests


def _trash_info(manifests):
    files = [f for m in manifests for f in m['files']]
    latest = max(manifests, key=lambda m: m['created'], default=None)
    return dict(count=len(files), bytes=sum(f['size'] for f in files),
                latest_token=latest['token'] if latest else None,
                revision=_digest([[m['token'], [[f['relative_path'], f['signature']] for f in m['files']]] for m in manifests]))


def _write_manifest(directory, data):
    temporary = directory / 'manifest.tmp'
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(directory / 'manifest.json')


def _prune(case, directory):
    """Remove empty known trash directories only; never recursively delete contents."""
    _safe(case, directory)
    parents = set()
    for p in directory.rglob('*'):
        _safe(case, p)
        if p.is_dir():
            parents.add(p)
    for p in sorted(parents, key=lambda p: len(p.parts), reverse=True):
        try:
            p.rmdir()
        except OSError:
            pass
    try:
        directory.rmdir()
    except OSError:
        pass


def register_result_file_routes(app, context):
    """context() returns {case_path, busy, lock}; busy covers run AND calibration."""
    local_lock = threading.RLock()

    def invoke(operation, mutation=False, shared_lock=True):
        try:
            ctx = context()
            lock = (ctx.get('lock') or nullcontext()) if shared_lock else nullcontext()
            with local_lock, lock:
                ctx = context()  # refresh busy/case after waiting for shared lock
                if not ctx.get('case_path'):
                    raise ResultError('请先选择案例。', 400)
                case = Path(os.path.abspath(ctx['case_path']))
                _safe(case, case)
                if not case.is_dir():
                    raise ResultError('案例目录不存在。', 404)
                if mutation and ctx.get('busy'):
                    raise ResultError('模型或率定运行中，不能清理、恢复或清空结果。', 409)
                data = request.get_json(silent=True) or {}
                if not isinstance(data, dict):
                    raise ResultError('请求格式无效。')
                return jsonify(operation(case, ctx, data))
        except ResultError as exc:
            return jsonify(error=str(exc)), exc.status
        except OSError as exc:
            return jsonify(error='文件正在使用或无法访问：' + str(exc)), 409

    def listing(case, ctx, data):
        files, revision = _inventory(case)
        # An unsafe trash path must not hide otherwise readable output locations.
        try:
            trash = _trash_info(_manifests(case))
        except ResultError as exc:
            trash = dict(count=0, bytes=0, latest_token=None, revision=None, error=str(exc))
        return dict(case_path=str(case), output_path=str(case / 'output'),
                    run_output_path=str(case), busy=bool(ctx.get('busy')), revision=revision,
                    files=_public(files), trash=trash)

    def checked(case, data):
        files, revision = _inventory(case)
        if data.get('revision') != revision:
            raise ResultError('结果清单已改变，请刷新后重新选择。', 409)
        return files, revision

    def duplicates(case, ctx, data):
        files, revision = checked(case, data)
        by_size = {}
        for f in files:
            by_size.setdefault(f['size'], []).append(f)
        buckets = {}
        for candidates in by_size.values():
            if len(candidates) < 2:
                continue
            for f in candidates:
                path = _safe(case, case / f['relative_path'])
                if _signature(path) != f['_signature']:
                    raise ResultError('扫描期间文件改变，请稍后重试。', 409)
                digest = hashlib.sha256()
                with path.open('rb') as stream:
                    before = os.fstat(stream.fileno())
                    if [before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_dev, before.st_ino] != f['_signature']:
                        raise ResultError('扫描期间文件改变，请稍后重试。', 409)
                    while True:
                        block = stream.read(1024 * 1024)
                        if not block:
                            break
                        digest.update(block)
                buckets.setdefault(digest.hexdigest(), []).append(f)
        if _inventory(case)[1] != revision:
            raise ResultError('扫描期间文件改变，请稍后重试。', 409)
        groups, selected = [], []
        for digest, members in buckets.items():
            if len(members) < 2:
                continue
            members.sort(key=lambda f: (-f['modified_ns'], f['relative_path']))
            paths = [f['relative_path'] for f in members]
            for f in members:
                f['duplicate_group'] = digest
            groups.append(dict(id=digest, keep=paths[0], paths=paths))
            selected.extend(paths[1:])
        return dict(revision=revision, groups=groups, duplicate_paths=selected, files=_public(files))

    def cleanup(case, ctx, data):
        files, revision = checked(case, data)
        paths = data.get('paths')
        if not isinstance(paths, list) or not paths or len(paths) != len(set(str(p) for p in paths)):
            raise ResultError('请选择不重复的结果文件。')
        index = {f['relative_path']: f for f in files}
        selected = []
        for rel in paths:
            if not _allowed(rel) or rel not in index:
                raise ResultError('只允许清理清单中的模型生成结果。')
            path = _safe(case, case / rel)
            if _signature(path) != index[rel]['_signature']:
                raise ResultError('文件已改变，请刷新。', 409)
            selected.append((path, index[rel]))
        _manifests(case)  # validate trash before any mutation
        token = uuid.uuid4().hex
        directory = _safe(case, case / '.studio-trash' / token)
        directory.mkdir(parents=True)
        manifest = dict(token=token, case_path=str(case), created=datetime.now(timezone.utc).isoformat(), files=[
            dict(relative_path=f['relative_path'], size=f['size'], signature=f['_signature']) for _, f in selected])
        _write_manifest(directory, manifest)  # durable recovery record precedes first move
        moved = []
        try:
            for source, f in selected:
                _safe(case, source)
                if _signature(source) != f['_signature']:
                    raise ResultError('文件已改变，清理已撤回。', 409)
                dest = _safe(case, directory / 'files' / f['relative_path'])
                dest.parent.mkdir(parents=True, exist_ok=True)
                source.rename(dest)
                moved.append((source, dest))
        except (OSError, ResultError):
            for source, dest in reversed(moved):
                if source.exists():
                    raise ResultError('回退目标已存在，请保留回收区并检查案例。', 409)
                dest.rename(source)
            (directory / 'manifest.json').unlink()
            _prune(case, directory)
            raise
        return dict(ok=True, token=token, count=len(selected), bytes=sum(f['size'] for _, f in selected))

    def restore(case, ctx, data):
        manifests = _manifests(case)
        token = data.get('token') or _trash_info(manifests)['latest_token']
        manifest = next((m for m in manifests if m['token'] == token), None)
        if manifest is None:
            raise ResultError('没有可恢复的清理记录。', 404)
        moves = []
        for f in manifest['files']:
            target = _safe(case, case / f['relative_path'])
            if target.exists():
                raise ResultError('恢复位置已有文件，请先处理冲突：' + f['relative_path'], 409)
            moves.append((Path(f['stored_path']), target))
        moved = []
        try:
            for source, target in moves:
                _safe(case, source); _safe(case, target)
                if target.exists():
                    raise ResultError('恢复位置已有文件。', 409)
                target.parent.mkdir(parents=True, exist_ok=True)
                source.rename(target)
                moved.append((source, target))
        except (OSError, ResultError):
            for source, target in reversed(moved):
                target.rename(source)
            raise
        directory = case / '.studio-trash' / manifest['token']
        (directory / 'manifest.json').unlink()
        _prune(case, directory)
        return dict(ok=True, count=len(moves))

    def empty(case, ctx, data):
        manifests = _manifests(case)
        info = _trash_info(manifests)
        if data.get('revision') != info['revision']:
            raise ResultError('回收区已改变，请刷新后重新确认。', 409)
        # Fully validate all entries before unlinking any file.
        for manifest in manifests:
            for f in manifest['files']:
                _safe(case, Path(f['stored_path']))
        for manifest in manifests:
            directory = case / '.studio-trash' / manifest['token']
            for f in manifest['files']:
                _safe(case, Path(f['stored_path'])).unlink()
            (directory / 'manifest.json').unlink()
            _prune(case, directory)
        return dict(ok=True, count=info['count'], bytes=info['bytes'])

    app.add_url_rule('/api/results/files', 'result_files_list', lambda: invoke(listing), methods=['GET'])
    for suffix, operation in [('duplicates', duplicates), ('cleanup', cleanup), ('restore', restore), ('empty-trash', empty)]:
        shared_lock = suffix != 'duplicates'
        app.add_url_rule('/api/results/files/' + suffix, 'result_files_' + suffix,
                         lambda operation=operation, shared_lock=shared_lock: invoke(
                             operation, mutation=True, shared_lock=shared_lock), methods=['POST'])
