exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
for va,n in ((0x81CA1F,5),(0x81D4D5,2),(0x81D4D7,5),(0x81D51B,5),(0x81D689,5),(0x81D991,6),(0x83CAB3,5),(0x156ABA8,6),(0x822450,5)):
    o=va-0x400000
    print(f'{va:#08x}: {d[o:o+n].hex()}')
import os
print('MSVBVM60 in app dir:', os.path.exists(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\MSVBVM60.dll"))
