import pefile
d=open(r"C:\Windows\SysWOW64\MSVBVM60.DLL",'rb').read()
base=0x66000000
for rs in (0x2ab9a,0x2abda,0x30854,0x68068,0x680b8,0x9283b,0x7a000 if False else 0x9287b):
    print(hex(rs), 'before:', d[rs-16:rs].hex(), 'after32:', d[rs:rs+8].hex(), 'VA', hex(base+ (rs-0x1000) + 0x1000))
