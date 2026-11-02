exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
seg=d[0xe4060:0xe44a0]
txt=seg.decode('latin1')
import re
parts=re.findall(r'[ -~]{3,}', txt)
print(' | '.join(parts[:120]))
