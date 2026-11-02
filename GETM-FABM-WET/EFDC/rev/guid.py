import struct
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
d=open(p,'rb').read()
# RVA 0x4f48 -> file offset
import pefile
pe=pefile.PE(p)
for rva in (0x4f48,0x4f38,0x2d08,0x9ab00,0x9b080):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.Misc_VirtualSize:
            o=s.PointerToRawData+(rva-s.VirtualAddress)
            b=d[o:o+16]
            g=struct.unpack('<IHH8s',b)
            print(f"rva {rva:#06x}: {b.hex()}  guid={g[0]:08X}-{g[1]:04X}-{g[2]:04X}-{g[3].hex()}")
            break
import uuid
print('IPictureDisp', uuid.UUID('{7BF80981-BF32-101A-8BBB-00AA00300CAB}').bytes_le.hex())
print('IPicture    ', uuid.UUID('{7BF80980-BF32-101A-8BBB-00AA00300CAB}').bytes_le.hex())
