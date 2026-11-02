import pefile
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p, fast_load=True); d=open(p,'rb').read()
s=[x for x in pe.sections if x.Name.rstrip(b'\x00')==b'.text'][0]
start=s.PointerToRawData; vsz=s.Misc_VirtualSize; raw=s.SizeOfRawData
i=start; run=0; rs=0; found=[]
while i<start+min(vsz,raw):
    if d[i]==0:
        if run==0: rs=i
        run+=1
    else:
        if run>=48:
            found.append((rs,run))
        run=0
    i+=1
print('runs>=48:', len(found))
for rs,ln in found[:20]:
    va=s.VirtualAddress+(rs-start)
    print(f'  rva {va:#08x} len {ln}  before={d[rs-8:rs].hex()} after={d[rs+ln:rs+ln+8].hex()}')
