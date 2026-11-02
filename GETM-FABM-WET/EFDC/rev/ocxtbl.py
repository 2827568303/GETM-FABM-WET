import pefile, uuid, struct
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase
d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
tbl_rva=0x2eb3c
o=off(tbl_rva)
print('table head:', d[o:o+64].hex())
# search whole file for the ImageList CLSID bytes
for s in ('2C247F23-8591-11D1-B16A-00C0F0283628','66833FE6-8583-11D1-B16A-00C0F0283628'):
    b=uuid.UUID('{'+s+'}').bytes_le
    idx=[]; i=d.find(b)
    while i>=0 and len(idx)<5:
        idx.append(i); i=d.find(b,i+1)
    print(s,'found at file offsets',[hex(x) for x in idx], 'VA', [hex(base+(x-0x1000)) for x in idx][:5])
