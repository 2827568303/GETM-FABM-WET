import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
# 1) restore original branch
o=off(0x45400); print('branch:', d[o:o+6].hex())
d[o:o+6]=bytes.fromhex('0f844cd50000')
# 2) validator -> always true
o=off(0x45437); print('validator prologue:', d[o:o+8].hex())
d[o:o+8]=bytes.fromhex('b80100000' + '0' + 'c20400'.replace('c20400','c20400'))
