import pefile, re
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase
d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
iat={}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        n=(imp.name or b'').decode(errors='ignore')
        if 'Picture' in n or 'Icon' in n:
            iat[n]=imp.address
            print(f'{e.dll.decode():12s} {n:24s} IAT={imp.address:#x}')
        if n in ('OleLoadPicture','OleLoadPictureEx','OleLoadPicturePath','OleIconToCursor','OleCreatePictureIndirect'):
            iat[n]=imp.address
for n,va in iat.items():
    pat=bytes([0xFF,0x15])+va.to_bytes(4,'little')
    offs=[m.start() for m in re.finditer(re.escape(pat),d)]
    print(f'call sites for {n}: {len(offs)}', [hex(base+(o-0x1000)) for o in offs][:10])
