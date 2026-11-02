exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=bytearray(open(exe,'rb').read())
o=0x156ABA8-0x400000
print('before:', d[o:o+6].hex())
assert d[o:o+6]==bytes.fromhex('ff90b8010000'), d[o:o+6].hex()
rel=0x156AC43-(0x156ABA8+5)
import struct
d[o:o+6]=b'\xe9'+struct.pack('<i',rel)+b'\x90'
open(exe,'wb').write(bytes(d))
print('patched: jump to 0x156AC43 (create activation form), rel=',hex(rel & 0xffffffff))
