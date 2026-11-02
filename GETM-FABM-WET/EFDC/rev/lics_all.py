import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
d=open(p,'rb').read()
print('size',len(d))
parts=[]
for m in re.finditer(rb'[ -~]{4,}', d):
    s=m.group().decode('latin1')
    parts.append((m.start(), s))
print('strings:', len(parts))
for off,s in parts[:200]:
    print(f'{off:06x} {s}')
