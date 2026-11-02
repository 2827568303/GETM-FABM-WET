import pefile
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=open(p,'rb').read()
pe=pefile.PE(p)
base=pe.OPTIONAL_HEADER.ImageBase
def rva_of(o):
    for s in pe.sections:
        if s.PointerToRawData<=o<s.PointerToRawData+s.SizeOfRawData:
            return s.VirtualAddress+(o-s.PointerToRawData)
    return None
old_pro='558bec83ec0c538b5d08568b750c5733'
pat=bytes.fromhex(old_pro)
print('pattern len',len(pat))
idx=0; hits=[]
while True:
    i=d.find(pat, idx)
    if i<0: break
    hits.append(i); idx=i+1
print('hits:', [hex(x)+' rva='+hex(rva_of(x) or 0) for x in hits][:10])
