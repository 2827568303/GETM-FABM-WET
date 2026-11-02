import struct
d=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe",'rb').read()
base=0x400000
for target,name in ((0x16249b0,'titleform global'),(0x16249a8,'titleform global-8'),(0x1623b78,'another form global')):
    pat=struct.pack('<I',target)
    offs=[]; i=d.find(pat)
    while i>=0:
        offs.append(base+i); i=d.find(pat,i+1)
    print(name, hex(target), 'refs:', len(offs))
    print('  ', [hex(x) for x in offs][:24])
