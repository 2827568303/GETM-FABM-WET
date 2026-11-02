import pefile, re
pe=pefile.PE('eems1183_setup.exe', fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
found=False
if hasattr(pe,'DIRECTORY_ENTRY_RESOURCE'):
    for e in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        nm = e.name if e.name else pefile.RESOURCE_TYPE.get(e.struct.Id, e.struct.Id)
        if str(nm) in ('24','RT_MANIFEST'):
            for d in e.directory.entries:
                for l in d.directory.entries:
                    data=pe.get_data(l.data.struct.OffsetToData, l.data.struct.Size)
                    print(data.decode('utf-8','ignore')[:1500])
                    found=True
print('manifest found:', found)
