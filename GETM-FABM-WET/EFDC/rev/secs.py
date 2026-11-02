import pefile
pe=pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL")
for s in pe.sections:
    n=s.Name.rstrip(b'\x00').decode(errors='ignore')
    print(f'{n:10s} VA={s.VirtualAddress:#08x} VSize={s.Misc_VirtualSize:#08x} RawSize={s.SizeOfRawData:#08x} RawPtr={s.PointerToRawData:#08x} chars={s.Characteristics:#x}')
d=open(r"C:\Windows\SysWOW64\MSVBVM60.DLL",'rb').read()
print('file size', len(d))
# check tail of each section raw data for zeros
for s in pe.sections:
    n=s.Name.rstrip(b'\x00').decode(errors='ignore')
    start=s.PointerToRawData; end=start+s.SizeOfRawData
    tail=d[end-0x100:end]
    print(n,'tail zeros:', tail.count(0), '/', len(tail))
