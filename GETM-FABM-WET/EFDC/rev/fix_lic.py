import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o=off(0x45400)
print('current:', d[o:o+6].hex())
assert d[o:o+6]==bytes.fromhex('e94cd5000090'), d[o:o+6].hex()
d[o:o+6]=bytes.fromhex('909090909090')   # always fall through to CreateInstance
open(p,'wb').write(bytes(d))
print('patched: CreateInstanceLic always creates (no license path)')
