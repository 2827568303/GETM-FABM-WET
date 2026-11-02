import re
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
for pat in [b'l\x00t\x00', b'lt\x00\x00\xbe\x0c\x00\x00']:
    offs=[m.start() for m in re.finditer(re.escape(pat),d)]
    print(pat, len(offs), [hex(0x400000+o) for o in offs[:10]])
# offsets of the exact head
head=bytes.fromhex('6c740000be0c00000000010001002020000001001800')
offs=[m.start() for m in re.finditer(re.escape(head),d)]
print('exact head hits', [hex(0x400000+o) for o in offs])
