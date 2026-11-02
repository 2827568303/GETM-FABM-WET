import re
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
for pat in (b'Form_Load', b'Form_Resize', b'frmEFDC_Explorer', b'Show', b'Command1', b'__vbaVarPow', b'Sub Main', b'InitParameters'):
    n=d.count(pat)
    i=d.find(pat)
    print(f'{pat!r:24} count={n:6d} first={hex(i) if i>=0 else None}')
# look at surroundings of __vbaVarPow
i=d.find(b'__vbaVarPow')
if i>=0:
    print('--- context around __vbaVarPow ---')
    print(d[i-200:i+300])
