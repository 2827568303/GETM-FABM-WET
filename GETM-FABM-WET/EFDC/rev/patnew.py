import pefile, re
p=r"C:\EFDC84_LIC\vb6\MSCOMCTL.OCX"
d=bytearray(open(p,'rb').read())
pe=pefile.PE(data=bytes(d))
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
def find(pat):
    return [m.start() for m in re.finditer(pat, bytes(d))]
# GetLicInfo pattern
pat1=re.compile(rb'\xA1....[\x5E\x56]', re.S)
hits=[]
for m in re.finditer(rb'\xA1(.{4})(.{0,24})', bytes(d)):
    tail=m.group(2)
    if tail[:5]==b'\x5e\x8b\x4c\x24\x08' and tail[5:8]==b'\x89\x41\x04': hits.append(m.start())
print('GetLicInfo candidates:', [hex(x) for x in hits])
pat2=[m.start() for m in re.finditer(rb'\x85\xC0\x59\x75\x0B\xB8\x12\x01\x04\x80', bytes(d))]
print('CreateInstanceLic candidates:', [hex(x) for x in pat2])
