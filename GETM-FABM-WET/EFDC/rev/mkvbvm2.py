import pefile, struct, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
DST = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.DLL"

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d), fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
base = pe.OPTIONAL_HEADER.ImageBase
exps = {e.name.decode(): e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    raise ValueError(hex(rva))


# ---------- patch 1: LoadPicture failure -> return S_OK with NULL picture ----------
LOADPIC_RVA = 0x1D740           # wrapper: push 8 args; call [OleLoadPictureEx]; test eax,eax; jl err
CHECK_RVA = 0x1D761             # 'test eax,eax' / 'jl 0x66085b50'
cave1 = exps['rtcAppleScript']

cave = bytearray()
cave += b'\x85\xc0'             # test eax,eax
cave += b'\x79\x08'             # jns +8
cave += b'\x8b\x4d\x24'         # mov ecx,[ebp+0x24]   (ppvObj)
cave += b'\x83\x21\x00'         # and dword [ecx],0
cave += b'\x33\xc0'             # xor eax,eax
cave += b'\x5d'                 # pop ebp
cave += b'\xc2\x20\x00'         # ret 0x20
co = rva2off(cave1)
d[co:co + len(cave)] = cave
# patch: jmp cave
eo = rva2off(CHECK_RVA)
rel = (base + cave1) - (base + CHECK_RVA + 5)
d[eo:eo + 5] = b'\xe9' + struct.pack('<i', rel)
print('cave1 @', hex(base + cave1), 'jmp from', hex(base + CHECK_RVA), 'rel', hex(rel & 0xffffffff))

# ---------- patch 2: swallow VB error 481 in __vbaHresultCheckObj ----------
HRES_RVA = 0x427C2
cave2 = exps['rtcMacId']
orig6 = bytes(d[rva2off(HRES_RVA):rva2off(HRES_RVA) + 6])
stub = bytearray()
stub += b'\x81\x7c\x24\x04' + struct.pack('<I', 0x800A01E1)   # cmp dword [esp+4], 481
stub += b'\x75\x05'                                          # jne +5
stub += b'\x31\xc0'                                          # xor eax,eax
stub += b'\xc2\x10\x00'                                      # ret 0x10
stub += orig6
jmp_at = len(stub)
stub += b'\xe9\x00\x00\x00\x00'
struct.pack_into('<i', stub, jmp_at + 1, (base + HRES_RVA + 6) - (base + cave2 + len(stub)))
c2o = rva2off(cave2)
d[c2o:c2o + len(stub)] = stub
eo2 = rva2off(HRES_RVA)
d[eo2:eo2 + 5] = b'\xe9' + struct.pack('<i', (base + cave2) - (base + HRES_RVA + 5))
print('cave2 @', hex(base + cave2), 'stub len', len(stub))

open(DST, 'wb').write(bytes(d))
print('wrote', DST, os.path.getsize(DST))

