# -*- coding: utf-8 -*-
"""Register the Sheridan Threed controls (THREED32.OCX) per-user (HKCU), no admin needed."""
import os
import sys
import winreg

DIR = r"C:\EFDC84_LIC\vb6"
FILE = "THREED32.OCX"
PATH = os.path.join(DIR, FILE)
LIB = "{0BA686C6-F7D3-101A-993E-0000C0EF6F5E}"
LIBVER = "1.0"
CLASSES = [
    ("SSCheck", "{0BA686AA-F7D3-101A-993E-0000C0EF6F5E}"),
    ("SSFrame", "{0BA686AF-F7D3-101A-993E-0000C0EF6F5E}"),
    ("SSCommand", "{0BA686B4-F7D3-101A-993E-0000C0EF6F5E}"),
    ("SSPanel", "{0BA686B9-F7D3-101A-993E-0000C0EF6F5E}"),
    ("SSOption", "{0BA686BE-F7D3-101A-993E-0000C0EF6F5E}"),
    ("SSRibbon", "{0BA686C3-F7D3-101A-993E-0000C0EF6F5E}"),
]
ROOTS = ["Software\\Classes\\", "Software\\Classes\\WOW6432Node\\"]


def sv(base, name, value):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(k)


def dword(base, name, value):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, value)
    winreg.CloseKey(k)


def empty(base):
    k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE)
    winreg.CloseKey(k)


n = 0
for root in ROOTS:
    tl = root + "TypeLib\\%s\\%s" % (LIB, LIBVER)
    sv(tl + "\\0\\win32", "", PATH)
    sv(tl + "\\HELPDIR", "", DIR)
    dword(tl, "FLAGS", 2)
    for name, clsid in CLASSES:
        progid = "Threed." + name
        base = root + "CLSID\\" + clsid
        sv(base, "", progid)
        sv(base + "\\InprocServer32", "", PATH)
        sv(base + "\\InprocServer32", "ThreadingModel", "Apartment")
        sv(base + "\\TypeLib", "", LIB)
        sv(base + "\\TypeLib", "Version", LIBVER)
        sv(base + "\\Version", "", LIBVER)
        sv(base + "\\ProgID", "", progid)
        sv(base + "\\MiscStatus", "", "0")
        sv(base + "\\MiscStatus\\1", "", "0")
        empty(base + "\\Control")
        sv(root + progid + "\\CLSID", "", clsid)
        n += 1
print("registered %d class entries under HKCU" % n)
