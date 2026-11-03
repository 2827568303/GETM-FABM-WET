"""Windows folder and file dialogs on a dedicated STA thread.

The in-window path is pywebview's WebView2 file dialog. This module is the
HTTP fallback used when that bridge is absent. Shell dialogs and WinForms
require an STA (CoInitializeEx COINIT_APARTMENTTHREADED). Calling them on a
waitress worker thread is a real Windows failure: the dialog never appears,
or the process faults. User cancel is HRESULT 0x800704C7 / winerror 1223.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
import threading

DIALOG_TITLE = '3DWET 选择文件夹'
FILE_DIALOG_TITLE = '3DWET 选择文件'
COINIT_APARTMENTTHREADED = 2
BIF_RETURNONLYFSDIRS = 0x0001
BIF_NEWDIALOGSTYLE = 0x0040
BFFM_INITIALIZED = 1
BFFM_SETSELECTIONW = 0x467
WM_SETTEXT = 0x000C
OFN_EXPLORER = 0x00080000
OFN_FILEMUSTEXIST = 0x00001000
OFN_PATHMUSTEXIST = 0x00000800
OFN_ALLOWMULTISELECT = 0x00000200
OFN_NOCHANGEDIR = 0x00000008
WS_OVERLAPPEDWINDOW = 0x00CF0000


class DialogResult:
    def __init__(self):
        self.path = ''
        self.paths = []
        self.error = ''
        self.engine = ''
        self.cancelled = False


def parse_picker_payload(text):
    """Accept the JSON written by the dialog helper, or a bare path."""
    raw = (text or '').strip()
    if not raw:
        return {'path': '', 'paths': [], 'error': '', 'engine': '',
                'cancelled': True, 'done': True}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {'path': raw, 'paths': [raw], 'error': '', 'engine': 'text',
                'cancelled': False, 'done': True}
    if not isinstance(data, dict):
        return {'path': '', 'paths': [], 'error': '文件夹选择结果不是 JSON 对象',
                'engine': 'none', 'cancelled': True, 'done': True}
    path = str(data.get('path') or '')
    paths = data.get('paths')
    if not isinstance(paths, list):
        paths = [path] if path else []
    paths = [str(item) for item in paths if str(item)]
    if path and path not in paths:
        paths.insert(0, path)
    if not path and paths:
        path = paths[0]
    cancelled = data.get('cancelled')
    if cancelled is None:
        cancelled = not path and not data.get('error')
    return {'path': path, 'paths': paths, 'error': str(data.get('error') or ''),
            'engine': str(data.get('engine') or ''), 'cancelled': bool(cancelled),
            'done': True}


def result_payload(result):
    path = result.path or ''
    paths = list(result.paths or [])
    if path and path not in paths:
        paths.insert(0, path)
    return {'path': path, 'paths': paths, 'error': result.error or '',
            'engine': result.engine or '', 'cancelled': bool(result.cancelled),
            'done': True}


def _run_sta(function):
    if os.name != 'nt':
        result = DialogResult()
        result.error = '当前系统没有 Windows 文件夹对话框'
        result.engine = 'none'
        result.cancelled = True
        return result
    box = {}

    def run():
        ole32 = ctypes.windll.ole32
        ole32.CoInitializeEx.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        ole32.CoInitializeEx.restype = ctypes.c_long
        hr = ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
        try:
            box['result'] = function()
        except Exception as exc:
            failed = DialogResult()
            failed.error = str(exc)
            failed.engine = 'none'
            box['result'] = failed
        finally:
            # S_OK and S_FALSE both need CoUninitialize. RPC_E_CHANGED_MODE does not.
            if hr in (0, 1):
                ole32.CoUninitialize()

    thread = threading.Thread(target=run, name='3dwet-sta-dialog', daemon=True)
    thread.start()
    thread.join()
    return box.get('result') or DialogResult()


class BROWSEINFOW(ctypes.Structure):
    _fields_ = [
        ('hwndOwner', wintypes.HWND),
        ('pidlRoot', ctypes.c_void_p),
        ('pszDisplayName', ctypes.c_wchar_p),
        ('lpszTitle', ctypes.c_wchar_p),
        ('ulFlags', wintypes.UINT),
        ('lpfn', ctypes.c_void_p),
        ('lParam', wintypes.LPARAM),
        ('iImage', ctypes.c_int),
    ]


class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [
        ('lStructSize', wintypes.DWORD),
        ('hwndOwner', wintypes.HWND),
        ('hInstance', wintypes.HINSTANCE),
        ('lpstrFilter', ctypes.c_wchar_p),
        ('lpstrCustomFilter', ctypes.c_wchar_p),
        ('nMaxCustFilter', wintypes.DWORD),
        ('nFilterIndex', wintypes.DWORD),
        ('lpstrFile', ctypes.c_wchar_p),
        ('nMaxFile', wintypes.DWORD),
        ('lpstrFileTitle', ctypes.c_wchar_p),
        ('nMaxFileTitle', wintypes.DWORD),
        ('lpstrInitialDir', ctypes.c_wchar_p),
        ('lpstrTitle', ctypes.c_wchar_p),
        ('Flags', wintypes.DWORD),
        ('nFileOffset', wintypes.WORD),
        ('nFileExtension', wintypes.WORD),
        ('lpstrDefExt', ctypes.c_wchar_p),
        ('lCustData', ctypes.c_void_p),
        ('lpfnHook', ctypes.c_void_p),
        ('lpTemplateName', ctypes.c_wchar_p),
        ('pvReserved', ctypes.c_void_p),
        ('dwReserved', wintypes.DWORD),
        ('FlagsEx', wintypes.DWORD),
    ]


def _owner_window(title):
    user32 = ctypes.windll.user32
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD, ctypes.c_wchar_p, ctypes.c_wchar_p, wintypes.DWORD,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, ctypes.c_void_p]
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.SetWindowTextW.argtypes = [wintypes.HWND, ctypes.c_wchar_p]
    user32.SetWindowTextW.restype = wintypes.BOOL
    # A real titled window. Wine and xdotool can see it, and the folder dialog
    # is owned by it so it stays in the foreground on a Windows STA thread.
    hwnd = user32.CreateWindowExW(
        0, 'Static', title, WS_OVERLAPPEDWINDOW | 0x10000000,
        80, 80, 420, 80, None, None, None, None)
    if hwnd:
        user32.SetWindowTextW(hwnd, title)
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL
        user32.ShowWindow(hwnd, 5)
    return hwnd


def _destroy_window(hwnd):
    if not hwnd:
        return
    user32 = ctypes.windll.user32
    user32.DestroyWindow.argtypes = [wintypes.HWND]
    user32.DestroyWindow.restype = wintypes.BOOL
    user32.DestroyWindow(hwnd)


def _browse_folder(start, title, modern):
    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32
    user32 = ctypes.windll.user32
    shell32.SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFOW)]
    shell32.SHBrowseForFolderW.restype = ctypes.c_void_p
    shell32.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    shell32.SHGetPathFromIDListW.restype = wintypes.BOOL
    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.SendMessageW.restype = wintypes.LPARAM
    user32.SetWindowTextW.argtypes = [wintypes.HWND, ctypes.c_wchar_p]
    display = ctypes.create_unicode_buffer(32768)
    title_buf = ctypes.create_unicode_buffer(title or DIALOG_TITLE)
    start_buf = ctypes.create_unicode_buffer(start or '')
    owner = _owner_window(title or DIALOG_TITLE)
    callback_type = ctypes.WINFUNCTYPE(
        ctypes.c_int, wintypes.HWND, ctypes.c_uint, wintypes.LPARAM, wintypes.LPARAM)

    def callback(hwnd, msg, _lparam, _data):
        if msg == BFFM_INITIALIZED:
            user32.SetWindowTextW(hwnd, title or DIALOG_TITLE)
            if start:
                user32.SendMessageW(hwnd, BFFM_SETSELECTIONW, 1, ctypes.cast(start_buf, ctypes.c_void_p))
        return 0

    callback_ref = callback_type(callback)
    info = BROWSEINFOW()
    info.hwndOwner = owner
    info.pszDisplayName = ctypes.cast(display, ctypes.c_wchar_p)
    info.lpszTitle = ctypes.cast(title_buf, ctypes.c_wchar_p)
    info.ulFlags = BIF_RETURNONLYFSDIRS | (BIF_NEWDIALOGSTYLE if modern else 0)
    info.lpfn = ctypes.cast(callback_ref, ctypes.c_void_p)
    result = DialogResult()
    result.engine = 'shbrowse'
    try:
        pidl = shell32.SHBrowseForFolderW(ctypes.byref(info))
        if not pidl:
            result.cancelled = True
            return result
        path_buf = ctypes.create_unicode_buffer(32768)
        ok = shell32.SHGetPathFromIDListW(pidl, path_buf)
        ole32.CoTaskMemFree(pidl)
        if not ok:
            result.error = '无法读取所选文件夹'
            result.cancelled = False
            return result
        result.path = path_buf.value
        result.paths = [result.path] if result.path else []
        result.cancelled = not result.path
        return result
    finally:
        _destroy_window(owner)
        # Keep the callback alive until the dialog returns.
        del callback_ref


def _choose_directory_sta(start, title):
    try:
        return _browse_folder(start, title, modern=True)
    except Exception as modern_error:
        try:
            return _browse_folder(start, title, modern=False)
        except Exception as legacy_error:
            failed = DialogResult()
            failed.engine = 'shbrowse'
            failed.error = f'{modern_error}; {legacy_error}'
            return failed


def choose_directory(start='', title=DIALOG_TITLE):
    return _run_sta(lambda: _choose_directory_sta(start or '', title or DIALOG_TITLE))


def _choose_files_sta(start, title, multi):
    comdlg32 = ctypes.windll.comdlg32
    comdlg32.GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]
    comdlg32.GetOpenFileNameW.restype = wintypes.BOOL
    comdlg32.CommDlgExtendedError.argtypes = []
    comdlg32.CommDlgExtendedError.restype = wintypes.DWORD
    buf = ctypes.create_unicode_buffer(32768)
    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    ofn.lpstrFilter = '所有文件\0*.*\0'
    ofn.lpstrFile = ctypes.cast(buf, ctypes.c_wchar_p)
    ofn.nMaxFile = 32768
    ofn.lpstrInitialDir = start if start and os.path.isdir(start) else None
    ofn.lpstrTitle = title or FILE_DIALOG_TITLE
    ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR
    if multi:
        ofn.Flags |= OFN_ALLOWMULTISELECT
    result = DialogResult()
    result.engine = 'getopenfilename'
    if not comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        err = int(comdlg32.CommDlgExtendedError())
        if err == 0:
            result.cancelled = True
        else:
            result.error = f'打开文件对话框失败（{err}）'
        return result
    raw = ctypes.wstring_at(ctypes.addressof(buf), 32767)
    items = [item for item in raw.split('\0') if item]
    if len(items) <= 1:
        result.path = items[0] if items else ''
        result.paths = [result.path] if result.path else []
    else:
        from pathlib import Path
        result.paths = [str(Path(items[0]) / name) for name in items[1:]]
        result.path = result.paths[0] if result.paths else ''
    result.cancelled = not result.paths
    return result


def choose_files(start='', title=FILE_DIALOG_TITLE, multi=True):
    return _run_sta(lambda: _choose_files_sta(start or '', title, multi))
