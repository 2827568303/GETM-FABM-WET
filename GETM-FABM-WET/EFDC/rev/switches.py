import re
exe=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
d=open(exe,'rb').read()
# find ASCII strings starting with / or - of length>=3
cands=set()
for m in re.finditer(rb'[/-][A-Za-z][A-Za-z0-9_]{2,20}', d):
    s=m.group().decode('latin1')
    cands.add(s)
print('switch-like strings:', len(cands))
print(sorted(cands)[:80])
