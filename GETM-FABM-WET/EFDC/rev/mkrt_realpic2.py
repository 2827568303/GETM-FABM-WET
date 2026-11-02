import struct
import pefile

SRC = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\MSVBVM60_realshape.dll"
CAVE_RVA = 0x105600          # tail padding of .text (VSize ends 0x1055D4)
IID_RVA = CAVE_RVA + 0x80
SITE_RVA = 0x1D761
RET_RVA = 0x1D769            # pop ebp; ret 0x20
IAT_CREATEBITMAP = 0x1810
IAT_OLECREATEPIC = 0x19FC

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d))


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


o = rva2off(SITE_RVA)
assert d[o:o + 8] == bytes.fromhex('85c00f8ce7830600'), d[o:o + 8].hex()

code = bytearray()
ev = code.extend

ev(b'\xe8\x00\x00\x00\x00')                          # call $+5
ev(b'\x5b')                                          # pop ebx
ev(b'\x81\xeb' + struct.pack('<I', CAVE_RVA + 5))    # sub ebx, imm32  -> ebx = module base

for v in (0, 1, 1, 1, 1):                            # CreateBitmap(1,1,1,1,NULL)
    ev(b'\x6a' + bytes([v]))
ev(b'\xff\x93' + struct.pack('<I', IAT_CREATEBITMAP))  # call [ebx+CreateBitmap]
ev(b'\x83\xc4\x14')                                  # add esp,0x14

ev(b'\x83\xec\x10')                                  # sub esp,0x10
ev(b'\xc7\x04\x24' + struct.pack('<I', 0x10))        # mov dword[esp],0x10
ev(b'\xc7\x44\x24\x04' + struct.pack('<I', 1))       # mov dword[esp+4],1
ev(b'\x89\x44\x24\x08')                              # mov [esp+8],eax
ev(b'\xc7\x44\x24\x0c' + struct.pack('<I', 0))       # mov dword[esp+0xc],0

ev(b'\x8b\x4d\x18')                                  # mov ecx,[ebp+0x18]
ev(b'\x51')                                          # push ecx
ev(b'\x6a\x01')                                      # push 1 (fOwn)
ev(b'\x8d\x83' + struct.pack('<I', IID_RVA))         # lea eax,[ebx+IID]
ev(b'\x50')                                          # push eax
ev(b'\x8d\x44\x24\x0c')                              # lea eax,[esp+0xC]
ev(b'\x50')                                          # push eax
ev(b'\xff\x93' + struct.pack('<I', IAT_OLECREATEPIC))  # call [ebx+OleCreatePictureIndirect]
ev(b'\x83\xc4\x20')                                  # add esp,0x20
ev(b'\x31\xc0')                                      # xor eax,eax
rel = RET_RVA - (CAVE_RVA + len(code) + 5)
ev(b'\xe9' + struct.pack('<i', rel))                 # jmp 0x1D769

print('stub length', len(code))
assert len(code) <= 0x80

co = rva2off(CAVE_RVA)
d[co:co + len(code)] = code

iid = bytes.fromhex('8109f87b32bf1a108bbb00aa00300cab')  # IID_IPictureDisp
io = rva2off(IID_RVA)
d[io:io + 16] = iid

# patch site -> jmp cave
rel = CAVE_RVA - (SITE_RVA + 5)
d[o:o + 5] = b'\xe9' + struct.pack('<i', rel)
d[o + 5:o + 8] = b'\x90\x90\x90'

open(OUT, 'wb').write(bytes(d))
print('written', OUT)

