import pefile
pe=pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL")
names=[(e.address,(e.name or b'').decode()) for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name]
for a,n in sorted(names):
    if any(k in n for k in ('Show','Form','Modal','DoEvents','Load','Zombie')):
        print(f'{a:#08x} {n}')
