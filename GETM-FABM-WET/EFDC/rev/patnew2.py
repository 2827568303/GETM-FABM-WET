import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o1=off(0x81324); print('GetLicInfo:', d[o1:o1+5].hex()); assert d[o1:o1+5]==bytes.fromhex('a150e06227')
d[o1:o1+5]=bytes.fromhex('b801000000')
o2=off(0x45400); print('LicBranch:', d[o2:o2+6].hex()); assert d[o2:o2+6]==bytes.fromhex('0f844cd50000')
d[o2:o2+6]=bytes.fromhex('e94cd5000090')
open(p,'wb').write(bytes(d))
print('patched license checks in vb6\\MSCOMCTL.OCX')
