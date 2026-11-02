import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
d=open(p,'rb').read()
txt=d.decode('utf-16le','ignore')
parts=[]
for m in re.finditer(r'[ -~]{3,}', txt):
    s=m.group()
    if s not in parts: parts.append(s)
print('total utf16 strings:', len(parts))
kw=('demo','lic','usage','activ','feature','email','user','pass','product','url','http','error','please','enter','-')
sel=[s for s in parts if any(k in s.lower() for k in kw)]
print('keyword hits:', len(sel))
for s in sel[:80]:
    print('  ',s)
