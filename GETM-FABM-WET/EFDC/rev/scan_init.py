import re, struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
pat=bytes([0xFF,0x15,0x14,0x15,0x40,0x00])
sites=[base+m.start() for m in re.finditer(re.escape(pat),d)]
init=[s for s in sites if 0x1010cf0<=s<0x1040000]
lic=[s for s in sites if 0x81c4c0<=s<0x8200000]
print('New2 in InitParameters range:', len(init), [hex(x) for x in init][:10])
print('New2 in license range:', len(lic), [hex(x) for x in lic][:10])
# also check functions called from Sub Main
pat2=bytes([0xFF,0x15,0x6c,0x15,0x40,0x00])
print('total New2 sites', len(sites))
