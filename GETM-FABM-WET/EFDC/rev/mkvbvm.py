import pefile, struct, os, shutil, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
DST = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.DLL"
HRES_RVA = 0x427c2          # __vbaHresultCheckObj
ERR481 = 0x800A01E1

d = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(d), fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
exps = {e.name.decode(): e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name} if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') else {}
if not exps:
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    exps = {e.name.decode(): e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    raise ValueError(hex(rva))


cave_rva = exps['rtcAppleScript']
eo = rva2off(HRES_RVA)
co = rva2off(cave_rva)
orig6 = bytes(d[eo:eo + 6])
print('entry bytes:', orig6.hex(), 'cave rva', hex(cave_rva))

stub = bytearray()
stub += b'\x81\x7c\x24\x04' + struct.pack('<I', ERR481)     # cmp dword [esp+4], 0x800A01E1
stub += b'\x75\x05'                                          # jne +5
stub += b'\x31\xc0'                                          # xor eax,eax
stub += b'\xc2\x10\x00'                                      # ret 0x10
stub += orig6                                                 # original entry bytes
jmp_back_at = len(stub)
stub += b'\xe9\x00\x00\x00\x00'
# patch rel32 for the jump back
rel = (base + HRES_RVA + 6) - (base + cave_rva + len(stub))
struct.pack_into('<i', stub, jmp_back_at + 1, rel)
d[co:co + len(stub)] = stub
# patch entry
rel2 = (base + cave_rva) - (base + HRES_RVA + 5)
d[eo:eo + 5] = b'\xe9' + struct.pack('<i', rel2)
open(DST, 'wb').write(bytes(d))
print('wrote', DST, os.path.getsize(DST), 'stub', len(stub), 'bytes')
print('stub hex:', stub.hex())
