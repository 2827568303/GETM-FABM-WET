"""Use the Windows filesystem code page expected by the native NetCDF DLL."""
import os

import netCDF4


def filename_encoding():
    if os.name == 'nt':
        import ctypes
        codepage = ctypes.windll.kernel32.GetACP()
        return 'utf-8' if codepage == 65001 else f'cp{codepage}'
    return 'utf-8'


def open_dataset(path, mode='r', **kwargs):
    kwargs.setdefault('encoding', filename_encoding())
    return netCDF4.Dataset(str(path), mode, **kwargs)
