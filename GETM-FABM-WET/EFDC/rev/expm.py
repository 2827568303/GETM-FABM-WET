import pefile
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\MSVBVM60_picpatch.dll"
pe=pefile.PE(p)
target=0x10707c
best=None
for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.address and e.address<=target:
        if best is None or e.address>best[0]: best=(e.address, e.name, e.ordinal)
print('nearest export below:', hex(best[0]) if best else None, best[1], best[2] if best else '')
# also check the 8 bytes at target
d=open(p,'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData: return s.PointerToRawData+(rva-s.VirtualAddress)
o=off(target)
print('bytes at 0x10707c:', d[o:o+32].hex() if o else None)
# section info
for s in pe.sections:
    print(s.Name.rstrip(b'\x00').decode(), hex(s.VirtualAddress), hex(s.VirtualAddress+s.Misc_VirtualSize))
