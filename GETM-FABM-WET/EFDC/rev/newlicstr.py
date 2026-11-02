import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EEMS125\x86\EFDC_LIC.exe"
d=open(p,'rb').read()
print('size',len(d))
# utf16 strings
txt=d.decode('utf-16le','ignore')
strs=[]
for m in re.finditer(r'[ -~]{4,}', txt):
    s=m.group()
    if s not in strs: strs.append(s)
kw=('http','licen','demo','feature','checkout','url','.lic','error','usage','product','email','activ')
sel=[s for s in strs if any(k in s.lower() for k in kw)]
print('keyword strings:', len(sel))
for s in sel[:60]: print('  ',s)
print('--- ascii urls ---')
for m in re.finditer(rb'https?://[ -~]{4,80}', d):
    print('  ', m.group().decode('latin1'))
