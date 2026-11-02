import pefile
targets = {
 r"C:\Windows\SysWOW64\oleaut32.dll": ['OleLoadPicture','OleLoadPictureEx','OleLoadPicturePath','OleLoadPictureFile','OleCreatePictureIndirect'],
 r"C:\Windows\SysWOW64\user32.dll": ['MessageBoxA','MessageBoxW','MessageBoxIndirectA','MessageBoxIndirectW'],
 r"C:\Windows\SysWOW64\msvbvm60.dll": ['rtcMsgBox','__vbaError','__vbaHresultCheckObj','__vbaOnError','__vbaExceptHandler','__vbaEnd','__vbaLateIdCall','__vbaLateIdCallLd','__vbaVarLateMemSt','__vbaObjSet','__vbaObjSetAddref','__vbaStrCopy'],
}
for path,names in targets.items():
    pe=pefile.PE(path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    m={e.name.decode(): e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
    print(path.split('\\')[-1], "base", hex(pe.OPTIONAL_HEADER.ImageBase))
    for n in names:
        print("   ", n, hex(m[n]) if n in m else "MISSING")
