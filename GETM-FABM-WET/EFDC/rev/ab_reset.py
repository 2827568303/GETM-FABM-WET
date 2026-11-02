src=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
s=open(src,'rb').read(); d=bytearray(open(exe,'rb').read())
sites=[0x81CA1F,0x81D3E0,0x81D4D5,0x81D4D7,0x81D51B,0x81D689,0x81D991,0x83CAB3,0x822450]
for va in sites:
    o=va-0x400000
    d[o:o+6]=s[o:o+6]
print('restored all sites from backup')
# now apply ONLY P1: skip the FNO check
o=0x81CA1F-0x400000
print('81CA1F orig:', s[o:o+5].hex())
d[o:o+5]=bytes.fromhex('9090909090')
open(exe,'wb').write(bytes(d))
print('applied P1 only (NOP the FNO check call)')
