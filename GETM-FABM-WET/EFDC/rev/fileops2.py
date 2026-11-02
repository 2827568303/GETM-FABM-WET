import re
app=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(app,'rb').read(); base=0x400000
def va(o): return base+(o-0x1000)
pairs={0x4014F8:'FileOpen',0x401374:'KillFiles',0x401550:'FileCopy',0x401490:'MakeDir',0x40121C:'NameFile',
       0x401508:'FileLength',0x4013E0:'FileLocation',0x4011FC:'WriteFile',0x4013D4:'FileSeek',0x40134C:'FileClose',
       0x40118C:'FreeVarList',0x401144:'__vbaI4Str'}
for addr,name in pairs.items():
    if name in ('FreeVarList','__vbaI4Str'): continue
    pat=bytes([0xFF,0x15])+addr.to_bytes(4,'little')
    vas=[va(m.start()) for m in re.finditer(re.escape(pat),d)]
    sel=[v for v in vas if 0x818000<=v<=0x840000]
    print(f"{name:14s} in license region:", ' '.join(f'{v:08X}' for v in sel))
