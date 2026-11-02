import struct, pefile
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); d=open(p,'rb').read()
# find import entry for IAT 0x401188
target=0x401188
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        if imp.address==target:
            print('0x401188 ->', e.dll.decode(), (imp.name or b'').decode(errors='ignore'), imp.hint)
for t2 in (0x401280,0x40129c,0x401514,0x4016a0,0x401188):
    found=False
    for e in pe.DIRECTORY_ENTRY_IMPORT:
        for imp in e.imports:
            if imp.address==t2:
                print(hex(t2),'->', e.dll.decode(), (imp.name or b'').decode(errors='ignore'))
                found=True
    if not found: print(hex(t2),'-> (not in import table)')
