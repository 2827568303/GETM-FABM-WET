import winreg, os, sys, re
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

DUMP = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\ocxdump.txt"
DIR = r"C:\EFDC84_LIC\vb6"

libs = {}   # file -> (libguid, version)
cls = []    # (file, clsid, name)

raw = open(DUMP, 'rb').read()
if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
    text = raw.decode('utf-16', errors='replace')
else:
    text = raw.decode('utf-8', errors='replace')
for line in text.splitlines():
    line = line.strip()
    if line.startswith('INFO|'):
        p = line.split('|')
        if len(p) >= 5 and p[2] == 'LIB':
            libs[p[1]] = (p[3].upper(), p[4])
    elif line.startswith('CLS|'):
        p = line.split('|')
        if len(p) >= 4:
            cls.append((p[1], p[2].upper(), p[3]))

print('libs', len(libs), 'classes', len(cls))


def setval(root, path, name, value):
    try:
        k = winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(k)
    except Exception as e:
        print('WARN', path, name, e)


def setdword(root, path, name, value):
    try:
        k = winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(k)
    except Exception as e:
        print('WARN', path, name, e)


ROOTS = [winreg.HKEY_CURRENT_USER]
VIEWS = ['Software\\Classes\\', 'Software\\Classes\\WOW6432Node\\']

count = 0
for f, (lib, ver) in libs.items():
    path = os.path.join(DIR, f)
    for view in VIEWS:
        # TypeLib registration
        tl = view + 'TypeLib\\{%s}\\%s' % (lib, ver)
        setval(winreg.HKEY_CURRENT_USER, tl + '\\0\\win32', '', path)
        setval(winreg.HKEY_CURRENT_USER, tl + '\\HELPDIR', '', DIR)
        setdword(winreg.HKEY_CURRENT_USER, tl, 'FLAGS', 2)

for f, g, name in cls:
    lib, ver = libs.get(f, ('', ''))
    path = os.path.join(DIR, f)
    for view in VIEWS:
        base = view + 'CLSID\\{%s}' % g
        setval(winreg.HKEY_CURRENT_USER, base, '', name)
        setval(winreg.HKEY_CURRENT_USER, base + '\\InprocServer32', '', path)
        setval(winreg.HKEY_CURRENT_USER, base + '\\InprocServer32', 'ThreadingModel', 'Apartment')
        setval(winreg.HKEY_CURRENT_USER, base + '\\TypeLib', '', '{%s}' % lib)
        setval(winreg.HKEY_CURRENT_USER, base + '\\TypeLib', 'Version', ver)
        setval(winreg.HKEY_CURRENT_USER, base + '\\ProgID', '', '')
        winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, base + '\\Control', 0, winreg.KEY_WRITE)
        count += 1
print('registered classes:', count)
