import pefile
P = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe = pefile.PE(P, fast_load=False)
want = 0x661196cc
print('=== imports of MSVBVM60 ===')
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode()
    for imp in entry.imports:
        if imp.address and abs(imp.address - want) < 0x40:
            print('  %s!%s  at 0x%X (delta %d)' % (dll, (imp.name or b'').decode(), imp.address, imp.address - want))
print()
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode()
    for imp in entry.imports:
        if imp.address == want:
            print('EXACT: %s!%s' % (dll, (imp.name or b'').decode()))
