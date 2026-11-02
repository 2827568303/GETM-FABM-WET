import re, sys, pefile
from capstone import *
path = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe = pefile.PE(path, fast_load=True)
data = open(path,'rb').read()
base = pe.OPTIONAL_HEADER.ImageBase
secs=[]
for s in pe.sections:
    secs.append((base+s.VirtualAddress, base+s.VirtualAddress+s.Misc_VirtualSize, s.PointerToRawData, s.Misc_VirtualSize, s.Name.rstrip(b'\x00').decode('latin1')))
def va2off(va):
    for vs,ve,praw,vsz,name in secs:
        if vs <= va < ve:
            return praw + (va-vs)
    return None
# build string map: VA -> text (utf16 & ascii), only for .text .data .rsrc
strs={}
for m in re.finditer(rb'(?:[\x20-\x7e]\x00){4,}', data):
    va = None
    for vs,ve,praw,vsz,name in secs:
        if praw <= m.start() < praw+vsz:
            va = vs + (m.start()-praw); break
    if va: strs.setdefault(va, m.group().decode('utf-16le','ignore'))
for m in re.finditer(rb'[\x20-\x7e]{5,}', data):
    va = None
    for vs,ve,praw,vsz,name in secs:
        if praw <= m.start() < praw+vsz:
            va = vs + (m.start()-praw); break
    if va: strs.setdefault(va, m.group().decode('latin1'))
start=int(sys.argv[1],16); end=int(sys.argv[2],16)
off=va2off(start); size=end-start
md=Cs(CS_ARCH_X86, CS_MODE_32); md.detail=True
code=data[off:off+size]
out=[]
for i in md.disasm(code, start):
    ann=''
    m=i.mnemonic; op=i.op_str
    if m=='call' or m=='jmp':
        if op.startswith('dword ptr [0x') :
            tgt=int(op.split('[')[1].split(']')[0],16)
            ann=f'   ; thunk {tgt:08X}'
    for val in re.findall(r'0x([0-9a-f]{5,8})', op):
        v=int(val,16)
        if v in strs and m in ('push','mov','cmp','lea'):
            s=strs[v].replace('\n',' ')[:110]
            ann += f'   ; "{s}"'
    out.append(f"{i.address:08X}: {i.bytes.hex():<20} {m:<8} {op}{ann}")
print("\n".join(out))
