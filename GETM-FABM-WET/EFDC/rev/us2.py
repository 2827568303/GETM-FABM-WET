import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
d=open(p,'rb').read()
base=0x9840; size=27152
seg=d[base:base+size]
print('first bytes:', seg[:32].hex())
# decode utf16le and split
txt=seg.decode('utf-16le','ignore')
parts=re.findall(r'[ -~]{4,}', txt)
seen=[]
for s in parts:
    if s not in seen: seen.append(s)
print('candidate strings:', len(seen))
for s in seen[:120]:
    print('  ', s)
