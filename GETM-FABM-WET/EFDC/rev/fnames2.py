import pefile
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase; d=open(p,'rb').read()
def u16(va,n=80):
    o=va-base
    b=d[o:o+n]
    try: return b.decode('utf-16le','ignore').split('\x00')[0]
    except: return '?'
for va in (0x4E5338,0x4E92DC,0x4E5390,0x4E9334,0x4E93E0,0x4E9384,0x4E545C,0x4E545C+2,0x4F96D0,0x4F9760,0x4E93E0+2):
    print(hex(va), '->', repr(u16(va)))
