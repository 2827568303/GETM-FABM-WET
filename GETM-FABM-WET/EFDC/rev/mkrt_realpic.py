import struct, sys
import pefile

SRC = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\MSVBVM60_realshape.dll"
BASE = 0x66000000

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d))


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


# patch site: 0x1D761, 8 bytes free before `pop ebp; ret 0x20` at 0x1D769
o = rva2off(0x1D761)
print('site bytes:', d[o:o + 8].hex())
assert d[o:o + 8] == bytes.fromhex('85c00f8ce7830600'), d[o:o + 8].hex()

# find a zero-filled cave (>= 0x80 bytes) in .text / ENGINE
cave_rva = 0x105600
assert cave_rva, 'no cave'
cave_va = BASE + cave_rva
iid_va = cave_va + 0x80           # IID placed after code
ret_va = BASE + 0x1D769           # pop ebp; ret 0x20

code = bytearray()
def emit(b):
    code.extend(b)

# CreateBitmap(1,1,1,1,NULL)
emit(b'\x6a\x00')                                  # push 0        (lpBits)
emit(b'\x6a\x01')                                  # push 1        (nBitCount)
emit(b'\x6a\x01')                                  # push 1        (nPlanes)
emit(b'\x6a\x01')                                  # push 1        (nHeight)
emit(b'\x6a\x01')                                  # push 1        (nWidth)
emit(b'\xff\x15' + struct.pack('<I', BASE + 0x1810))  # call [CreateBitmap]
emit(b'\x83\xc4\x14')                              # add esp, 0x14

# PICTDESC {cbSize=0x10, picType=1, hbmp, hpal=0}
emit(b'\x83\xec\x10')                              # sub esp, 0x10
emit(b'\xc7\x04\x24' + struct.pack('<I', 0x10))    # mov dword [esp], 0x10
emit(b'\xc7\x44\x24\x04' + struct.pack('<I', 1))   # mov dword [esp+4], 1
emit(b'\x89\x44\x24\x08')                          # mov [esp+8], eax
emit(b'\xc7\x44\x24\x0c' + struct.pack('<I', 0))   # mov dword [esp+0xc], 0

# OleCreatePictureIndirect(&desc, &IID_IPictureDisp, TRUE, ppvObj)
emit(b'\x8b\x4d\x18')                              # mov ecx, [ebp+0x18]  (ppvObj)
emit(b'\x51')                                      # push ecx
emit(b'\x6a\x01')                                  # push 1 (fOwn)
emit(b'\x68' + struct.pack('<I', iid_va))          # push &IID
emit(b'\x8d\x44\x24\x0c')                          # lea eax, [esp+0xC]
emit(b'\x50')                                      # push eax
emit(b'\xff\x15' + struct.pack('<I', BASE + 0x19FC))  # call [OleCreatePictureIndirect]
emit(b'\x83\xc4\x20')                              # add esp, 0x20

emit(b'\x31\xc0')                                  # xor eax,eax
# jmp ret_va
rel = ret_va - (cave_va + len(code) + 5)
emit(b'\xe9' + struct.pack('<i', rel))

print('stub length', len(code), 'max 0x80')
assert len(code) <= 0x80

co = rva2off(cave_rva)
d[co:co + len(code)] = code

# IID_IPictureDisp {7BF80981-BF32-101A-8BBB-00AA00300CAB}
iid = bytes.fromhex('8109f87b32bf1a108bbb00aa00300cab')
io = rva2off(cave_rva + 0x80)
d[io:io + 16] = iid

# patch the site: jmp cave
rel = cave_va - (BASE + 0x1D761 + 5)
d[o:o + 5] = b'\xe9' + struct.pack('<i', rel)
d[o + 5:o + 8] = b'\x90\x90\x90'

open(OUT, 'wb').write(bytes(d))
print('written', OUT)
