import re, struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
cands={'frmEFDC_Explorer':[0x4DF888,0x4DF880],'TitleForm':[0x4DED9C,0x4DED94,0x4DEDA0],'LicenseValidation':[0x4DD92C,0x4DD924]}
for label,vas in cands.items():
    print('===',label)
    for v in vas:
        pat=struct.pack('<I',v)
        offs=[m.start() for m in re.finditer(re.escape(pat),d)]
        sel=[base+o for o in offs if 0x401000<=(base+o)<0x1620000]
        print(f'  refs to {v:#x}:', [hex(x) for x in sel][:12])
