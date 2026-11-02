import re
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
pats=[rb'EE_[A-Z0-9_]{2,24}', rb'EEMS_[A-Z0-9_]{2,24}', rb'EFDC_[A-Z0-9_]{2,24}']
seen=set()
for p in pats:
    for m in re.finditer(p,d):
        s=m.group().decode('latin1')
        if s not in seen:
            seen.add(s)
print('feature-like strings:', len(seen))
for s in sorted(seen)[:60]:
    print('  ',s)
