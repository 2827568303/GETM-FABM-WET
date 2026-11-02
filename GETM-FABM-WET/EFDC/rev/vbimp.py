import pefile
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p)
print("ImageBase",hex(pe.OPTIONAL_HEADER.ImageBase))
for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name and e.name.decode() in ('rtcMsgBox','__vbaError','__vbaHresultCheckObj','__vbaOnError','ThunRTMain','rtcLoadPicture','__vbaStrCopy','__vbaVarMove','__vbaLateIdCall','__vbaLateIdCallLd','__vbaObjSet','__vbaEnd','__vbaExceptHandler','rtcErrObj','__vbaVarLateMemSt','__vbaFreeObj','__vbaFreeStr','__vbaStrVarMove'):
        print(f"{e.name.decode():24s} RVA={e.address:#x}")
print("--- imports mentioning Picture/Ole ---")
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll=entry.dll.decode()
    for imp in entry.imports:
        n=(imp.name or b'').decode(errors='ignore')
        if 'Pic' in n or 'Pic' in n or 'Ole' in n:
            print(f"{dll:20s} {n:32s} {imp.address:#x}")
