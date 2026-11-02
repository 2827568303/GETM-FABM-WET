import pefile
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
pe=pefile.PE(exe)
def rva_of(o):
    for s in pe.sections:
        if s.PointerToRawData<=o<s.PointerToRawData+s.SizeOfRawData:
            return base + s.VirtualAddress + (o - s.PointerToRawData)
    return None
for off in (0xea330, 0xe45b0, 0x115e60, 0xe50c3):
    va=rva_of(off)
    print('=== off',hex(off),'VA',hex(va) if va else None)
    seg=d[off-64:off+96]
    print(repr(seg))
