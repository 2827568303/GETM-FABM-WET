import pefile
pe=pefile.PE('eems1251_setup.exe', fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
for e in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    nm = e.name if e.name else pefile.RESOURCE_TYPE.get(e.struct.Id, e.struct.Id)
    if str(nm) in ('24','RT_MANIFEST'):
        for d1 in e.directory.entries:
            for l in d1.directory.entries:
                data=pe.get_data(l.data.struct.OffsetToData, l.data.struct.Size)
                txt=data.decode('utf-8','ignore')
                print(txt[:1200])
                print('---')
                print('requireAdministrator:', 'requireAdministrator' in txt)
                print('asInvoker:', 'asInvoker' in txt)
