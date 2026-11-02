d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
for va in (0x81CA1F,0x822450,0x81C5AC):
    print(hex(va), d[va-0x400000:va-0x400000+6].hex())
