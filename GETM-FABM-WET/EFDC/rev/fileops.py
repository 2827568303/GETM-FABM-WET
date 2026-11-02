import re, pefile
app=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(app,'rb').read()
pe=pefile.PE(app, fast_load=True)
s=pe.sections[0]
text_va=0x400000+s.VirtualAddress; praw=s.PointerToRawData; vsz=s.Misc_VirtualSize
def off2va(o): return text_va+(o-praw)
filethunks={
 0x4014F8:'__vbaFileOpen',0x401374:'rtcKillFiles',0x401550:'rtcFileCopy',0x401490:'rtcMakeDir',
 0x401494:'rtcRemoveDir',0x40121C:'__vbaNameFile',0x401508:'rtcFileLength',0x4013E0:'rtcFileLocation',
 0x4011FC:'__vbaWriteFile',0x401440:'__vbaInputFile',0x4013D4:'rtcFileSeek',0x40134C:'__vbaFileClose',
 0x40128C:'__vbaFileCloseAll',0x401674:'rtcSetFileAttr',0x401574:'rtcGetFileAttr',0x401468:'rtcRound',
}
hits={}
for addr,name in filethunks.items():
    pat=bytes([0xFF,0x15])+addr.to_bytes(4,'little')
    offs=[m.start() for m in re.finditer(re.escape(pat),d)]
    hits[name]=[off2va(o) for o in offs]
for name,vas in hits.items():
    print(f"{name:20s} {len(vas):4d} ", ' '.join(f'{v:08X}' for v in vas[:24]))
