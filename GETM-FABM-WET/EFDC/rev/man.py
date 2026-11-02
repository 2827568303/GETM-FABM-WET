import pefile
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(exe)
if hasattr(pe,'DIRECTORY_ENTRY_RESOURCE'):
    for e in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        name=e.name if e.name else pefile.RESOURCE_TYPE.get(e.struct.Id, e.struct.Id)
        if str(name) in ('24','RT_MANIFEST','MANIFEST'):
            for d in e.directory.entries:
                for l in d.directory.entries:
                    data=pe.get_data(l.data.struct.OffsetToData, l.data.struct.Size)
                    print('--- manifest ---')
                    print(data.decode('utf-8','ignore')[:2000])
else:
    print('no resources')
