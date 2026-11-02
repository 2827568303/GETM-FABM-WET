import pefile
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def s(va,n=64):
    o=va-base
    b=d[o:o+n]
    t=b.split(b'\x00')[0]
    try: return t.decode('latin1')
    except: return repr(t)
for va in (0x4E5338,0x4E92DC,0x4E5390,0x4E9334,0x4E93E0,0x4E9384,0x4E545C,0x4F96D0,0x4F9760):
    print(hex(va), '->', repr(s(va)))
