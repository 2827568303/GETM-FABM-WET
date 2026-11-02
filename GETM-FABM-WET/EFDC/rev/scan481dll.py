import re, pefile
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d=open(p,'rb').read()
pe=pefile.PE(p, fast_load=True)
base=pe.OPTIONAL_HEADER.ImageBase
secs=[(s.VirtualAddress,s.PointerToRawData,s.Misc_VirtualSize,s.Name.rstrip(b"\x00").decode()) for s in pe.sections]
def off2va(o):
    for va,pr,sz,n in secs:
        if pr<=o<pr+sz: return base+va+(o-pr),n
    return None,None
pats={
 'push 0x1E1': rb'\x68\xe1\x01\x00\x00',
 'mov eax,0x1E1': rb'\xb8\xe1\x01\x00\x00',
 'mov ecx,0x1E1': rb'\xb9\xe1\x01\x00\x00',
 'mov edx,0x1E1': rb'\xba\xe1\x01\x00\x00',
 'mov [ebp-x],0x1E1': rb'\xc7\x45.\xe1\x01\x00\x00',
 'moffs': rb'\xa3.\x2a\x66',
}
for name,pat in pats.items():
    offs=[m.start() for m in re.finditer(pat,d,re.S)]
    res=[]
    for o in offs:
        va,sec=off2va(o)
        if va: res.append((va,sec))
    print(name, len(res), [f"{v:#x}({s})" for v,s in res[:20]])
