import pefile, struct, os, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SRC = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
DST = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.DLL"

data = bytearray(open(SRC, 'rb').read())
pe = pefile.PE(data=bytes(data), fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
fa = pe.OPTIONAL_HEADER.FileAlignment
sa = pe.OPTIONAL_HEADER.SectionAlignment
e_lfanew = pe.DOS_HEADER.e_lfanew
nsec = pe.FILE_HEADER.NumberOfSections
sizeof_headers = pe.OPTIONAL_HEADER.SizeOfHeaders
last_hdr_end = e_lfanew + 0x18 + nsec * 0x28
print(f'sections={nsec} headers={sizeof_headers:#x} last_hdr_end={last_hdr_end:#x} fa={fa:#x} sa={sa:#x} image={pe.OPTIONAL_HEADER.SizeOfImage:#x}')
assert last_hdr_end + 0x28 <= sizeof_headers, 'no room for a new section header'

# new section
new_va = (pe.OPTIONAL_HEADER.SizeOfImage + sa - 1) & ~(sa - 1)
new_raw = (len(data) + fa - 1) & ~(fa - 1)
cave = bytearray(0x1000)
# stub A: picture fallback (16 bytes)
stubA = bytearray(b'\x85\xc0' + b'\x79\x08' + b'\x8b\x4d\x24' + b'\x83\x21\x00' + b'\x33\xc0' + b'\x5d' + b'\xc2\x20\x00')
cave[0:len(stubA)] = stubA
# stub B: swallow VB error 481 (at cave+0x100)
stubB_off = 0x100
hres = 0x427C2
orig6 = bytes(data[hres: hres + 6]) if False else None


def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + s.SizeOfRawData:
            return s.PointerToRawData + (rva - s.VirtualAddress)
    raise ValueError(hex(rva))


eo = rva2off(hres)
orig6 = bytes(data[eo:eo + 6])
sb = bytearray()
sb += b'\x81\x7c\x24\x04' + struct.pack('<I', 0x800A01E1)
sb += b'\x75\x05'
sb += b'\x31\xc0'
sb += b'\xc2\x10\x00'
sb += orig6
jmp_at = len(sb)
sb += b'\xe9\x00\x00\x00\x00'
struct.pack_into('<i', sb, jmp_at + 1, (base + hres + 6) - (base + new_va + stubB_off + len(sb)))
cave[stubB_off:stubB_off + len(sb)] = sb

# append cave raw data
if len(data) < new_raw:
    data.extend(b'\x00' * (new_raw - len(data)))
data.extend(cave)

# new section header
name = b'.cave\x00\x00\x00'
hdr = struct.pack('<8sIIIIIIHHI', name, 0x1000, new_va, 0x1000, new_raw, 0, 0, 0, 0, 0x60000020)
hdr_off = last_hdr_end
data[hdr_off:hdr_off + 0x28] = hdr

# update headers
struct.pack_into('<H', data, e_lfanew + 0x6, nsec + 1)
struct.pack_into('<I', data, e_lfanew + 0x18 + 0x38, new_va + 0x1000)   # SizeOfImage
# SizeOfCode
size_of_code = struct.unpack_from('<I', data, e_lfanew + 0x18 + 0x04)[0]
struct.pack_into('<I', data, e_lfanew + 0x18 + 0x04, size_of_code + 0x1000)

# patch 1: jmp to cave stubA
rel = (base + new_va) - (base + 0x1D761 + 5)
data[rva2off(0x1D761):rva2off(0x1D761) + 5] = b'\xe9' + struct.pack('<i', rel)
# patch 2: jmp to cave stubB
rel2 = (base + new_va + stubB_off) - (base + hres + 5)
data[rva2off(hres):rva2off(hres) + 5] = b'\xe9' + struct.pack('<i', rel2)

open(DST, 'wb').write(bytes(data))
print('new section VA', hex(base + new_va), 'raw', hex(new_raw), 'size', len(data))
pe2 = pefile.PE(DST, fast_load=True)
print('verify sections', len(pe2.sections), 'last', pe2.sections[-1].Name, hex(pe2.sections[-1].VirtualAddress))
