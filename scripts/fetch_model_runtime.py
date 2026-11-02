"""Fetch the solver's DLL closure from MSYS2 UCRT64, without installing MSYS2.

Requires pefile and zstandard. Package SHA256 values are verified against the
official HTTPS repository database. This is checksum verification, not GPG
signature verification. Only regular DLL/license files are extracted.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

import pefile
import zstandard

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / '3DWET' / 'bin' / 'runtime'
EXE = ROOT / '3DWET' / 'bin' / 'getm_cartesian.exe'
# The geolocated mirror endpoint can redirect to unavailable mirrors. This is
# MSYS2's official central repository, serving the same package database.
REPO = 'https://repo.msys2.org/mingw/ucrt64/'


def download(url):
    print('Download', url, flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def archive(data):
    stream = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data))
    return tarfile.open(fileobj=stream, mode='r|')


def fields(text):
    result = {}
    key = None
    for line in text.splitlines():
        if line.startswith('%') and line.endswith('%'):
            key = line.strip('%')
            result[key] = []
        elif line and key:
            result[key].append(line)
    return result


def safe_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError(f'Unsafe archive path: {name}')
    return path


def imports(path):
    with pefile.PE(str(path), fast_load=True) as pe:
        pe.parse_data_directories(directories=[1, 13])
        return {entry.dll.decode('ascii').lower(): [item.name.decode('ascii') if item.name else item.ordinal
                                                  for item in entry.imports]
                for directory in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT')
                for entry in getattr(pe, directory, [])}


def exports(path):
    with pefile.PE(str(path), fast_load=True) as pe:
        pe.parse_data_directories(directories=[0])
        entries = getattr(getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None), 'symbols', [])
        return {symbol.name.decode('ascii') if symbol.name else symbol.ordinal for symbol in entries}


def system_dll(name):
    return name.startswith(('api-ms-win-', 'ext-ms-win-')) or (
        Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32' / name).is_file()


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    database = download(REPO + 'ucrt64.files')
    records = {}
    dll_owners = {}
    with archive(database) as tar:
        for member in tar:
            path = safe_path(member.name)
            if not member.isfile() or path.name not in ('desc', 'files'):
                continue
            record = records.setdefault(path.parts[0], {})
            record.update(fields(tar.extractfile(member).read().decode()))
    for record in records.values():
        for name in record.get('FILES', []):
            path = safe_path(name)
            if len(path.parts) == 3 and path.parts[:2] == ('ucrt64', 'bin') and path.suffix.lower() == '.dll':
                dll_owners[path.name.lower()] = record

    manifest = {'repository': REPO, 'preferred_mirror': 'https://mirror.msys2.org/mingw/ucrt64/',
                'database_sha256': hashlib.sha256(database).hexdigest(),
                'verification': 'Package SHA256 checked against official HTTPS repository metadata; GPG signatures not verified.',
                'solver_sha256': hashlib.sha256(EXE.read_bytes()).hexdigest(),
                'packages': [], 'dlls': {}, 'system_dlls': [], 'missing_symbols': []}
    fetched = set()
    pending = [EXE]
    visited = set()
    while pending:
        binary = pending.pop()
        if binary.name.lower() in visited:
            continue
        visited.add(binary.name.lower())
        for name, symbols in imports(binary).items():
            if system_dll(name):
                manifest['system_dlls'].append(name)
                continue
            package = dll_owners.get(name)
            if package is None:
                raise RuntimeError(f'No MSYS2 package provides {name}, imported by {binary.name}')
            filename = package['FILENAME'][0]
            if filename not in fetched:
                data = download(REPO + filename)
                digest = hashlib.sha256(data).hexdigest()
                if digest != package['SHA256SUM'][0]:
                    raise ValueError(f'Package checksum mismatch: {filename}')
                entry = {'name': package['NAME'][0], 'version': package['VERSION'][0],
                         'url': REPO + filename, 'sha256': digest,
                         'metadata_url': 'https://packages.msys2.org/packages/' + package['NAME'][0],
                         'license_identifiers': package.get('LICENSE', []), 'license_files': []}
                with archive(data) as tar:
                    for member in tar:
                        path = safe_path(member.name)
                        if not member.isfile():
                            continue
                        is_dll = len(path.parts) == 3 and path.parts[:2] == ('ucrt64', 'bin') and path.suffix.lower() == '.dll'
                        is_license = path.parts[:3] == ('ucrt64', 'share', 'licenses')
                        if not (is_dll or is_license):
                            continue
                        destination = TARGET / (path.name if is_dll else Path('licenses', *path.parts[3:]))
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        content = tar.extractfile(member).read()
                        destination.write_bytes(content)
                        relative = destination.relative_to(TARGET).as_posix()
                        if is_dll:
                            manifest['dlls'][path.name.lower()] = {'file': relative, 'package': entry['name'],
                                                                  'sha256': hashlib.sha256(content).hexdigest()}
                        else:
                            entry['license_files'].append(relative)
                manifest['packages'].append(entry)
                fetched.add(filename)
            dll = TARGET / manifest['dlls'][name]['file']
            available = exports(dll)
            missing = [symbol for symbol in symbols if symbol not in available]
            if missing:
                manifest['missing_symbols'].append({'importer': binary.name, 'dll': name, 'symbols': missing})
            pending.append(dll)
    # Keep only DLLs reachable from the solver; packages can contain unrelated tools.
    for name, entry in list(manifest['dlls'].items()):
        if name not in visited:
            (TARGET / entry['file']).unlink()
            del manifest['dlls'][name]
    manifest['system_dlls'] = sorted(set(manifest['system_dlls']))
    manifest['dll_closure_complete'] = True
    (TARGET / 'runtime-sources.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'packages': len(fetched), 'dlls': len(manifest['dlls']),
                      'missing_symbols': manifest['missing_symbols']}, indent=2))
    return 1 if manifest['missing_symbols'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
