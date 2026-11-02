import struct
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read(); base=0x400000
def rd(va,n):
    o=va-base
    return d[o:o+n] if 0<=o and o+n<=len(d) else None
for (ptr,ln) in ((0x625214,0x4c),(0x6BC744,0x9c),(0x4EDE2D70 & 0xffffffff,0)):
    if ln:
        b=rd(ptr,ln*2)
        try: print(hex(ptr), 'utf16:', b.decode('utf-16le','ignore')[:120])
        except: pass
        b2=rd(ptr,ln)
        print(hex(ptr), 'ascii:', b2.split(b'\x00')[0][:120])
