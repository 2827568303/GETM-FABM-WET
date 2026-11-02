import pefile
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p)
for e in pe.DIRECTORY_ENTRY_IMPORT:
    dll=e.dll.decode()
    names=[(i.name or b'').decode(errors='ignore') for i in e.imports]
    show=[n for n in names if n.startswith('Reg') or 'Registry' in n or n.startswith('Rtl')]
    print(dll, len(names), '| reg-ish:', show)
