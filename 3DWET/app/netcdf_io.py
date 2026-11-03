"""Open NetCDF files the way the Windows NetCDF DLL can actually see them.

Python 3 paths are Unicode. The netCDF C library on Windows opens the
filename with the ANSI code page (GetACP), unless the process code page is
UTF-8. A path such as ``D:\\测试\\...\\THEORETICAL_LAKE.2d.0000.nc`` therefore
raises ``[Errno 2]`` from ``Dataset(path)`` even when the file is on disk.
``open_dataset`` passes that code page. When the path cannot be encoded in
the code page at all, an ASCII directory junction under
``%SYSTEMROOT%\\Temp\\3DWET-links`` is the path handed to NetCDF and to
``mpiexec`` as its working directory. The junction is removed with
``os.rmdir`` so the real case directory is left in place.
"""
from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from pathlib import Path
import subprocess
import threading

import netCDF4


NETCDF_LOCK = threading.RLock()
_JUNCTIONS = {}


def filename_encoding():
    if os.name == 'nt':
        import ctypes
        codepage = ctypes.windll.kernel32.GetACP()
        return 'utf-8' if codepage == 65001 else f'cp{codepage}'
    return 'utf-8'


def path_is_acp_compatible(path):
    """True when the native NetCDF DLL can encode this path."""
    if os.name != 'nt':
        return True
    encoding = filename_encoding()
    if encoding == 'utf-8':
        return True
    try:
        os.fspath(path).encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


def _junction_root():
    system = os.environ.get('SYSTEMROOT') or os.environ.get('WINDIR') or r'C:\Windows'
    root = Path(system) / 'Temp' / '3DWET-links'
    root.mkdir(parents=True, exist_ok=True)
    return root


def _ascii_junction(target):
    """Create an ASCII junction pointing at ``target``. Never copies files."""
    target = Path(target).resolve()
    key = os.path.normcase(str(target))
    cached = _JUNCTIONS.get(key)
    if cached is not None and cached.exists():
        return cached
    digest = hashlib.sha1(str(target).encode('utf-8')).hexdigest()[:16]
    link = _junction_root() / f'j{digest}'
    if not link.exists():
        completed = subprocess.run(
            ['cmd.exe', '/d', '/c', 'mklink', '/J', os.fspath(link), os.fspath(target)],
            capture_output=True, text=True, encoding='utf-8', errors='replace', check=False)
        if not link.exists():
            detail = (completed.stderr or completed.stdout or '').strip()
            raise OSError(f'无法为非 ANSI 路径创建目录联接: {target}: {detail}')
    _JUNCTIONS[key] = link
    return link


def native_equivalent(path):
    """Return a path the native NetCDF DLL can open."""
    path = Path(path)
    if os.name != 'nt' or path_is_acp_compatible(path):
        return path
    parent = path if path.is_dir() else path.parent
    link = _ascii_junction(parent)
    if path.is_dir():
        return link
    return link / path.name


def prepare_solver_cwd(case):
    """Working directory for mpiexec. Second value is a junction to remove."""
    case = Path(case)
    if os.name != 'nt' or path_is_acp_compatible(case):
        return os.fspath(case), None
    link = _ascii_junction(case)
    return os.fspath(link), link


def release_solver_cwd(link):
    """Remove a junction created for the solver. Does not delete the target."""
    if not link:
        return
    link = Path(link)
    try:
        if os.name == 'nt' or link.is_symlink():
            os.rmdir(link)
    except OSError:
        return
    stale = [key for key, value in _JUNCTIONS.items() if value == link]
    for key in stale:
        _JUNCTIONS.pop(key, None)


def open_dataset(path, mode='r', **kwargs):
    kwargs.setdefault('encoding', filename_encoding())
    native = native_equivalent(path)
    return netCDF4.Dataset(os.fspath(native), mode, **kwargs)


@contextmanager
def locked_dataset(path, mode='r', **kwargs):
    """Hold the process-wide NetCDF lock for one open dataset."""
    with NETCDF_LOCK:
        dataset = open_dataset(path, mode, **kwargs)
        try:
            yield dataset
        finally:
            dataset.close()
