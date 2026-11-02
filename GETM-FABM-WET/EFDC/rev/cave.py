import pefile, struct, shutil, os, hashlib
src=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d=bytearray(open(src,'rb').read())
pe=pefile.PE(data=bytes(d), fast_load=True)
text=[s for s in pe.sections if s.Name.rstrip(b'\x00')==b'.text'][0]
print('.text', hex(text.VirtualAddress), hex(text.Misc_VirtualSize), 'raw', hex(text.PointerToRawData), hex(text.SizeOfRawData), 'flags', hex(text.Characteristics))
start=text.PointerToRawData; end=start+text.SizeOfRawData
need=32
runs=[]
i=start; run=0; rs=0
while i<end:
    if d[i]==0:
        if run==0: rs=i
        run+=1
        if run>=need:
            runs.append(rs); i+=need; run=0
    else:
        run=0
    i+=1
print('zero runs >=32:', len(runs), [hex(r) for r in runs[:10]])
