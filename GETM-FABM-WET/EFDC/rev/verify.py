import pefile
pe=pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL", fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
d=open(r"C:\Windows\SysWOW64\MSVBVM60.DLL",'rb').read()
def off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+s.SizeOfRawData:
            return s.PointerToRawData+(rva-s.VirtualAddress)
for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name and e.name.decode() in ('rtcAppleScript','rtcMacId','rtcLoadPicture'):
        o=off(e.address)
        print(e.name.decode(), hex(e.address), d[o:o+16].hex())
print('at 0x1d740:', d[off(0x1d740):off(0x1d740)+0x30].hex())
print('at 0x1d761:', d[off(0x1d761):off(0x1d761)+8].hex())
