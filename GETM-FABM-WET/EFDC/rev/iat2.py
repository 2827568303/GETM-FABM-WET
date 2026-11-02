import pefile
pe=pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL")
targets={0x661196CC,0x660019FC,0x66001810,0x66001A50}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    dn=e.dll.decode()
    for imp in e.imports:
        if imp.address in targets:
            print(f'{dn}!{(imp.name or b"").decode(errors="ignore")}  IAT={imp.address:#x}')
print('---- all oleaut32 imports around ----')
for e in pe.DIRECTORY_ENTRY_IMPORT:
    if e.dll.decode().lower()!='oleaut32.dll': continue
    for imp in e.imports:
        n=(imp.name or b'').decode(errors='ignore')
        if 'Picture' in n or 'Pict' in n:
            print(f'{n} IAT={imp.address:#x}')
