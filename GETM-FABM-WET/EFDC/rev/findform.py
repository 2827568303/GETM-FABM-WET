import re, struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
def va(o): return base+o
for name_va,label in [(0x4E4DD0,'frmEFDC_Explorer'),(0x4E4970,'frmEFDC_Explorer_TitleForm'),(0x4E4090,'frmAct_License_Validation')]:
    pats=[struct.pack('<I',name_va)]
    print(f"=== {label} @ {name_va:#x} ===")
    for pat in pats:
        offs=[m.start() for m in re.finditer(re.escape(pat),d)]
        print('  ptr refs:', [hex(va(o)) for o in offs][:20])
        for o in offs[:6]:
            # dump surrounding dwords to identify descriptor
            s=max(0,o-16); ctx=[struct.unpack('<I',d[i:i+4])[0] for i in range(s,min(len(d)-3,o+32),4)]
            print('   ctx at', hex(va(o)), [hex(x) for x in ctx])
