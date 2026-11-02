import pefile
p=r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe=pefile.PE(p)
want=('CreateBitmap','CreateCompatibleBitmap','CreateDIBSection','OleCreatePictureIndirect','OleLoadPicture','OleLoadPictureEx','LoadIconW','GetDC','CreateCompatibleDC','DeleteObject','SelectObject')
for e in pe.DIRECTORY_ENTRY_IMPORT:
    dn=e.dll.decode()
    for imp in e.imports:
        n=(imp.name or b'').decode(errors='ignore')
        if n in want:
            print(f'{dn}!{n}  IAT={imp.address:#x}')
