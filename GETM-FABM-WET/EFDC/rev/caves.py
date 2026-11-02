import pefile
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p, fast_load=True); d=open(p,'rb').read()
s=[x for x in pe.sections if x.Name.rstrip(b'\x00')==b'.text'][0]
print('Va',hex(s.VirtualAddress),'VS',hex(s.Misc_VirtualSize),'raw',hex(s.PointerToRawData),hex(s.SizeOfRawData),'flags',hex(s.Characteristics))
o=s.PointerToRawData+0xE000
print('bytes at rva 0xE000:', d[o:o+32].hex())
for rva in (0x104d00,0x104e00,0x104f00,0x104f80):
    o=s.PointerToRawData+(rva-s.VirtualAddress)
    print(hex(rva), d[o:o+32].hex())
print('SizeOfImage', hex(pe.OPTIONAL_HEADER.SizeOfImage))
