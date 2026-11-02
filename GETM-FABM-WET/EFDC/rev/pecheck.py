import pefile, warnings
warnings.simplefilter('always')
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(p)
print('warnings:', [str(w) for w in pe.get_warnings()][:20])
print('SizeOfImage', hex(pe.OPTIONAL_HEADER.SizeOfImage))
print('SizeOfHeaders', hex(pe.OPTIONAL_HEADER.SizeOfHeaders))
print('CheckSum', hex(pe.OPTIONAL_HEADER.CheckSum), 'computed', hex(pe.generate_checksum()))
print('DllCharacteristics', hex(pe.OPTIONAL_HEADER.DllCharacteristics))
print('sections:')
for s in pe.sections:
    print(' ', s.Name.rstrip(b'\x00').decode(), 'VA', hex(s.VirtualAddress), 'VS', hex(s.Misc_VirtualSize), 'Raw', hex(s.PointerToRawData), hex(s.SizeOfRawData))
try:
    print('rsrc entries:', len(pe.DIRECTORY_ENTRY_RESOURCE.entries))
    types={}
    for e in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        types[e.id if e.id is not None else e.name] = len(e.directory.entries) if e.directory else 0
    print('rsrc types:', types)
except Exception as ex:
    print('rsrc parse error:', ex)
