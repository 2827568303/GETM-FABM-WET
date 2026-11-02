import pefile
src=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx"
dst=r"C:\EFDC84_LIC\mscomctl.ocx"
d=bytearray(open(src,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o1=off(0x82162); print('GetLicInfo before:', d[o1:o1+5].hex()); assert d[o1:o1+5]==bytes.fromhex('a1c8ed6227')
d[o1:o1+5]=bytes.fromhex('b801000000')
o2=off(0x8221B); print('CreateInstanceLic before:', d[o2:o2+2].hex()); assert d[o2:o2+2]==bytes.fromhex('750b')
d[o2:o2+2]=bytes.fromhex('eb0b')
open(dst,'wb').write(bytes(d))
print('patched: GetLicInfo always licensed; CreateInstanceLic forced')
