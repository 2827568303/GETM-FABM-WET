import pefile, struct, uuid
p=r"C:\EFDC84_LIC\mscomctl.ocx"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
base_rva=0xAEB38
print('count word at table:', struct.unpack_from('<H', d, off(base_rva))[0])
for i in range(0,12):
    rva=base_rva+4+i*8
    o=off(rva)
    if o is None: break
    ptr,flag=struct.unpack_from('<II', d, o)
    s=''
    if 0x27580000<=ptr<0x27600000:
        pr=ptr-base; po=off(pr)
        if po:
            g=d[po:po+16]
            try: s=str(uuid.UUID(bytes_le=g))
            except Exception: s=g.hex()
    print(f'entry {i}: ptr={ptr:#x} flag={flag:#x} guid={s}')
