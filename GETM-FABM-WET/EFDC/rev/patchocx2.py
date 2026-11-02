import pefile
src=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx"
dst=r"C:\EFDC84_LIC\mscomctl.ocx"
d=bytearray(open(src,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
rva=0x8221B
o=off(rva)
print('before:', d[o:o+2].hex())
assert d[o:o+2]==bytes.fromhex('750b'), d[o:o+2].hex()
d[o:o+2]=bytes.fromhex('eb0b')
open(dst,'wb').write(bytes(d))
print('patched CreateInstanceLic license check at RVA 0x8221B: 75 0B -> EB 0B')
