import struct, pefile
app=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(app,'rb').read(); base=0x400000
def rd(va,n=4): return d[0x1000+(va-base):0x1000+(va-base)+n]
for tbl in (0x402208,0x402240,0x402268,0x402278):
    print(f"=== table {tbl:#x} ===")
    for i in range(0,0x60,4):
        v=struct.unpack('<I', rd(tbl+i))[0]
        print(f"  +{i:02x}: {v:#010x}")
