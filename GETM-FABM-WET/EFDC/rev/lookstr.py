targets=[0x49102c,0x4e9580,0x48fe70,0x4fcf1c,0x4fd380,0x4fd3e8,0x402d20,0x402268,0x4eef28,0x4ebf98]
lines=[l.rstrip() for l in open('strings_all.txt',encoding='utf-8')]
d={int(l[:8],16):l for l in lines}
for t in targets:
    print(f"{t:#08x}: {d.get(t,'(not a string boundary)')}")
# also dump raw utf16 at those addresses from the exe
s=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
for t in targets:
    o=t-0x400000
    raw=s[o:o+80]
    print(f"{t:#08x} raw: {raw[:40]!r}")
