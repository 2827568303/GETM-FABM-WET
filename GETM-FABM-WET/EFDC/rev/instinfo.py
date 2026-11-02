import pefile
pe=pefile.PE('eems1183_setup.exe', fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
if hasattr(pe,'VS_VERSIONINFO'):
    for fi in pe.FileInfo:
        for f in fi:
            if hasattr(f,'StringTable'):
                for st in f.StringTable:
                    for k,v in st.entries.items():
                        print(k.decode(errors='ignore'), '=', v.decode(errors='ignore'))
print('--- sections ---')
for s in pe.sections:
    print(s.Name.rstrip(b'\x00').decode(errors='ignore'), hex(s.PointerToRawData), hex(s.SizeOfRawData))
print('--- imports (dlls) ---')
pe2=pefile.PE('eems1183_setup.exe')
for e in pe2.DIRECTORY_ENTRY_IMPORT:
    print(e.dll.decode())
