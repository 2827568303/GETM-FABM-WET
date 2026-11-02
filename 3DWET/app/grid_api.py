"""Shared, revision-checked bathymetry editor for browser and desktop clients."""
import copy
import hashlib
import json
import math
import os
import shutil
import uuid
from pathlib import Path

import netCDF4 as nc
from netcdf_io import open_dataset
import numpy as np
from flask import jsonify, request
from lake_points_api import POINT_FILES, read_points, point_command, prepare_point_files


def register_grid_routes(app, context):
    sessions = {}

    def active():
        if not context.active_case_path:
            raise ValueError('请先打开一个案例')
        return Path(context.active_case_path).resolve()

    def fingerprint(path):
        # Size and mtime miss an in-place NetCDF rewrite that lands in the
        # same timestamp (common on a 1-second clock). Hash the bytes too.
        if not path.exists():
            return None
        stat = path.stat()
        digest = hashlib.blake2s()
        with path.open('rb') as handle:
            if stat.st_size <= 8 * 1024 * 1024:
                for block in iter(lambda: handle.read(1024 * 1024), b''):
                    digest.update(block)
            else:
                digest.update(handle.read(256 * 1024))
                tail = min(256 * 1024, stat.st_size)
                handle.seek(max(0, stat.st_size - tail))
                digest.update(handle.read(tail))
        return (stat.st_mtime_ns, stat.st_size, digest.digest())

    def load(path):
        config = context.parse_getm_inp(path / 'getm.inp') if (path / 'getm.inp').exists() else {}
        name = str(config.get('domain', {}).get('bathymetry', 'bathymetry.nc')).strip("'\"")
        file = (path / name).resolve()
        if not file.is_relative_to(path):
            raise ValueError('地形文件必须位于案例目录内')
        if not file.exists():
            raise ValueError('未找到地形文件，请先完成前处理')
        with open_dataset(file) as ds:
            a = np.ma.filled(ds['bathymetry'][:], -10).astype(float)
            if a.ndim != 2 or a.size > 2000000:
                raise ValueError('交互编辑支持二维地形，最多200万网格')
            a[~np.isfinite(a)] = -10
        river_file = path / 'riverinfo.dat'
        rivers = []
        if river_file.exists():
            lines = river_file.read_text(encoding='utf-8-sig').splitlines()
            for line in lines[1:1 + int(lines[0])]:
                parts = line.split()
                if len(parts) < 3:
                    raise ValueError('riverinfo.dat 河流记录不完整')
                rivers.append(dict(i=int(parts[0]), j=int(parts[1]), name=parts[2], tail=parts[3:], original_name=parts[2], kind='signed'))
        if (path / 'rivers_setup.json').exists():
            meta = json.loads((path / 'rivers_setup.json').read_text(encoding='utf-8-sig'))
            kinds = {r['name'].casefold(): r.get('kind') for r in meta.get('rivers', [])}
            known = {r['name'].casefold() for r in rivers}
            for mark in meta.get('rivers', []):
                if mark['name'].casefold() not in known:
                    rivers.append(dict(i=int(mark['i']), j=int(mark['j']), name=mark['name'], tail=['-1', '-1'], original_name=mark['name'], kind='signed'))
                    known.add(mark['name'].casefold())
            for river in rivers:
                kind = kinds.get(river['name'].casefold())
                if kind in ('inflow', 'outflow', 'signed'): river['kind'] = kind
        if (path / 'rivers.nc').exists():
            with open_dataset(path / 'rivers.nc') as ds:
                for river in rivers:
                    if river['name'] in ds.variables:
                        values = np.ma.compressed(ds[river['name']][:])
                        if river['kind'] == 'signed':
                            if values.size and np.all(values >= 0): river['kind'] = 'inflow'
                            elif values.size and np.all(values <= 0): river['kind'] = 'outflow'
        draft_fingerprints = {str(file): fingerprint(file) for file in (path / 'river_drafts').glob('*.json')}
        return dict(file=file, river_file=river_file, fingerprint=fingerprint(file),
                    river_fingerprint=fingerprint(river_file), config_fingerprint=fingerprint(path / 'getm.inp'),
                    depth=a, initial_depth=a.copy(), rivers=rivers,
                    points=read_points(path), point_fingerprints={name: fingerprint(path / name) for name in POINT_FILES}, draft_fingerprints=draft_fingerprints,
                    undo=[], redo=[], revision=0, dirty=False)

    def snapshot(s):
        return s['depth'].copy(), copy.deepcopy(s['rivers']), copy.deepcopy(s['points'])

    def payload(path, s):
        water = s['depth'][s['depth'] > 0]
        return dict(case_path=str(path), depth=s['depth'].tolist(), rivers=s['rivers'], points=s['points'],
                    calibration_candidates=getattr(context, 'calibration_points', []),
                    nx=s['depth'].shape[1], ny=s['depth'].shape[0], revision=s['revision'],
                    dirty=s['dirty'], can_undo=bool(s['undo']), can_redo=bool(s['redo']),
                    water_cells=int(water.size), max_depth=float(water.max()) if water.size else 0)

    @app.get('/api/grid/editor')
    def editor():
        with context._NC_LOCK:
            try:
                path = active()
                if context._case_in_use(path):
                    return jsonify(error='模型计算中，请结束运行后编辑网格'), 409
                key = str(path)
                if key not in sessions:
                    sessions[key] = load(path)
                return jsonify(payload(path, sessions[key]))
            except (ValueError, TypeError, OSError, KeyError) as e:
                return jsonify(error=str(e)), 400

    @app.post('/api/grid/edit')
    def edit():
        with context._NC_LOCK:
            try:
                path = active()
                d = request.get_json() or {}
                if d.get('case_path') != str(path) or context._case_in_use(path):
                    return jsonify(error='案例已切换或正在计算，请重新加载'), 409
                s = sessions.get(str(path))
                if s is None or d.get('revision') != s['revision']:
                    return jsonify(error='网格已被其他窗口修改，请重新加载'), 409
                action = d.get('action')
                if action == 'reload':
                    fresh = load(path)
                    fresh['revision'] = s['revision'] + 1
                    sessions[str(path)] = fresh
                    return jsonify(payload(path, fresh))
                if (fingerprint(s['file']) != s['fingerprint'] or
                        fingerprint(s['river_file']) != s['river_fingerprint'] or
                        fingerprint(path / 'getm.inp') != s['config_fingerprint'] or
                        any(fingerprint(path / name) != stamp for name, stamp in s['point_fingerprints'].items()) or
                        {str(file): fingerprint(file) for file in (path / 'river_drafts').glob('*.json')} != s['draft_fingerprints']):
                    return jsonify(error='磁盘文件已改变，请放弃编辑并重新加载，避免覆盖外部修改'), 409
                backup = None
                if action in ('undo', 'redo'):
                    src, dst = (s['undo'], s['redo']) if action == 'undo' else (s['redo'], s['undo'])
                    if src:
                        dst.append(snapshot(s))
                        s['depth'], s['rivers'], s['points'] = src.pop()
                        s['dirty'] = True
                elif action == 'save':
                    if any(not (1 <= r['i'] <= s['depth'].shape[1] and
                                1 <= r['j'] <= s['depth'].shape[0] and
                                s['depth'][r['j']-1, r['i']-1] > 0) for r in s['rivers'] + s['points']):
                        raise ValueError('所有点位必须位于有效水格，请移动点位或恢复水深')
                    backup_dir = path / 'backups' / ('grid-' + uuid.uuid4().hex[:12])
                    backup_dir.mkdir(parents=True)
                    temp = s['file'].with_name(s['file'].name + '.' + uuid.uuid4().hex + '.tmp')
                    replacements = {}
                    originals = {}
                    try:
                        replacements = prepare_point_files(path, s, backup_dir)
                        replacements[s['file']] = temp
                        for target in list(replacements) + [s['river_file']]:
                            saved = backup_dir / ('original-' + str(len(originals)) + '-' + target.name)
                            originals[target] = saved if target.exists() else None
                            if target.exists(): shutil.copy2(target, saved)
                        shutil.copy2(s['file'], backup_dir / s['file'].name)
                        if s['river_file'].exists(): shutil.copy2(s['river_file'], backup_dir / 'riverinfo.dat')
                        shutil.copy2(s['file'], temp)
                        with open_dataset(temp, 'r+') as ds:
                            original = ds['bathymetry'][:]
                            changed = s['depth'] != s['initial_depth']
                            original[changed] = s['depth'][changed]
                            ds['bathymetry'][:] = original
                        if s['rivers'] or s['river_file'].exists():
                            rows = [str(len(s['rivers']))] + [
                                ' '.join([str(r['i']), str(r['j']), r['name'], *r['tail']]) for r in s['rivers']]
                            river_temp = backup_dir / 'riverinfo.new'
                            river_temp.write_text('\n'.join(rows) + '\n', encoding='utf-8')
                            replacements[s['river_file']] = river_temp
                        for target, prepared in replacements.items():
                            if prepared is None: target.unlink(missing_ok=True)
                            else: os.replace(prepared, target)
                    except Exception:
                        for target, saved in originals.items():
                            if saved is not None: shutil.copy2(saved, target)
                            else: target.unlink(missing_ok=True)
                        raise
                    finally:
                        temp.unlink(missing_ok=True)
                    s['fingerprint'] = fingerprint(s['file'])
                    s['river_fingerprint'] = fingerprint(s['river_file'])
                    s['point_fingerprints'] = {name: fingerprint(path / name) for name in POINT_FILES}
                    s['draft_fingerprints'] = {str(file): fingerprint(file) for file in (path / 'river_drafts').glob('*.json')}
                    renamed = {r.get('original_name'): r['name'] for r in s['rivers']}
                    for history in s['undo'] + s['redo']:
                        for river in history[1]:
                            river['original_name'] = renamed.get(river.get('original_name'), river.get('original_name'))
                    for r in s['rivers']: r['original_name'] = r['name']
                    s['initial_depth'] = s['depth'].copy()
                    s['dirty'] = False
                    backup = str(backup_dir)
                elif action in ('point', 'point_delete', 'river_add', 'river_update', 'river_delete'):
                    collection, index, item = point_command(s, d, getattr(context, 'calibration_points', []))
                    s['undo'].append(snapshot(s))
                    s['undo'] = s['undo'][-max(1, min(50, 64000000 // s['depth'].nbytes)):]
                    s['redo'].clear()
                    if item is None: collection.pop(index)
                    elif index is None: collection.append(item)
                    else: collection[index] = item
                    s['dirty'] = True
                elif action in ('depth', 'land', 'smooth', 'river'):
                    cells = d.get('cells', [])
                    if not isinstance(cells, list) or not cells or len(cells) > s['depth'].size:
                        raise ValueError('请选择有效网格')
                    ny, nx = s['depth'].shape
                    for cell in cells:
                        if (not isinstance(cell, list) or len(cell) != 2 or
                                any(type(v) is not int for v in cell) or
                                not (0 <= cell[0] < nx and 0 <= cell[1] < ny)):
                            raise ValueError('网格索引超出范围')
                    if action == 'depth':
                        value = float(d.get('value'))
                        if not math.isfinite(value) or value <= 0:
                            raise ValueError('水深必须是有限正数')
                    if action == 'river':
                        if len(cells) != 1: raise ValueError('移动点位必须选择一个水格')
                        index = d.get('river_index')
                        if type(index) is not int or not 0 <= index < len(s['rivers']):
                            raise ValueError('请选择现有河流点；新增河流请使用输入数据页面')
                        i, j = cells[0]
                        if s['depth'][j, i] <= 0:
                            raise ValueError('河流点必须位于水格')
                    s['undo'].append(snapshot(s))
                    # Bound memory to roughly 64 MB even for large grids.
                    s['undo'] = s['undo'][-max(1, min(50, 64000000 // s['depth'].nbytes)):]
                    s['redo'].clear()
                    original = s['depth'].copy()
                    for i, j in cells:
                        if action == 'depth': s['depth'][j, i] = value
                        elif action == 'land': s['depth'][j, i] = -10
                        elif action == 'smooth' and original[j, i] > 0:
                            region = original[max(0,j-1):j+2, max(0,i-1):i+2]
                            water = region[region > 0]
                            s['depth'][j, i] = float(water.mean())
                    if action == 'river':
                        s['rivers'][index].update(i=cells[0][0]+1, j=cells[0][1]+1)
                    s['dirty'] = True
                else:
                    raise ValueError('未知网格操作')
                s['revision'] += 1
                result = payload(path, s)
                if backup: result['backup'] = backup
                return jsonify(result)
            except (ValueError, TypeError, OSError, KeyError) as e:
                return jsonify(error=str(e)), 400
