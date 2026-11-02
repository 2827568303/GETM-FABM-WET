import pefile, struct
from capstone import *
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p)
data=open(p,'rb').read()
base=pe.OPTIONAL_HEADER.ImageBase
secs=[(base+s.VirtualAddress, s.PointerToRawData, s.Misc_VirtualSize, s.Name.rstrip(b"\x00").decode()) for s in pe.sections]
def va2off(va):
    for vs,pr,sz,n in secs:
        if vs<=va<vs+sz: return pr+(va-vs)
    return None
targets={'OleLoadPicture':0x66001a50,'OleCreatePictureIndirect':0x660019fc}
md=Cs(CS_ARCH_X86,CS_MODE_32)
for name,iat in targets.items():
    pat=struct.pack('<I',iat)
    offs=[i for i in range(len(data)) if data.startswith(pat,i)]
    print(f"=== {name} iat={iat:#x} refs={len(offs)}")
    for o in offs[:12]:
        # find section + va
        va=None
        for vs,pr,sz,n in secs:
            if pr<=o<pr+sz: va=vs+(o-pr); sec=n
        if va is None: continue
        start=max(va-40,0)
        o2=va2off(start)
        print(f"  ref at VA {va:#x} ({sec})")
        code=data[o2:o2+70]
        for i in md.disasm(code,start):
            mark='  <== IAT' if i.address==va else ''
            print(f"    {i.address:08x}: {i.bytes.hex():<18} {i.mnemonic} {i.op_str}{mark}")
