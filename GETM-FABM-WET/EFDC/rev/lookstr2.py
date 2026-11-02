s=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
for t in (0x506378,0x590d34,0x4d5204,0x6197b0,0x4e940c,0x4e9288):
    o=t-0x400000
    raw=s[o:o+120]
    print(f"{t:#08x} raw: {raw[:60]!r}")
    try: print('   ascii:', raw.split(b'\x00')[0])
    except Exception as e: print(e)
