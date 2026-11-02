import re, sys, pefile, json, os
path = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe = pefile.PE(path, fast_load=True)
data = open(path,'rb').read()
secs = [(s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData, s.Name.rstrip(b'\x00').decode('latin1')) for s in pe.sections]
base = pe.OPTIONAL_HEADER.ImageBase
def off2va(off):
    for va, vsz, praw, rsz, name in secs:
        if praw <= off < praw+rsz:
            return base+va+(off-praw), name
    return None, None
rows=[]
for m in re.finditer(rb'(?:[\x20-\x7e]\x00){3,}', data):
    s = m.group().decode('utf-16le','ignore')
    va,sec = off2va(m.start())
    if va: rows.append((va,'U',sec,s))
for m in re.finditer(rb'[\x20-\x7e]{4,}', data):
    s = m.group().decode('latin1')
    va,sec = off2va(m.start())
    if va: rows.append((va,'A',sec,s))
rows.sort()
print("total strings", len(rows))
kw = re.compile(r'(bmp|jpg|jpeg|gif|\.ico|wmf|emf|png|licen|dsi_|EEMS|activ|Act_Lic|feature|Feature|demo|Demo|expir|Expir|\.ini|\.mdb|picture|Picture|logo|Logo)', re.I)
with open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\strings_kw.txt",'w',encoding='utf-8') as f:
    for va,t,sec,s in rows:
        if kw.search(s):
            f.write(f"{va:08X} {t} {sec:6s} {s}\n")
with open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\strings_all.txt",'w',encoding='utf-8') as f:
    for va,t,sec,s in rows:
        f.write(f"{va:08X} {t} {sec:6s} {s}\n")
print("wrote files")
for s in pe.sections:
    print(s.Name.rstrip(b'\x00').decode('latin1'), hex(s.VirtualAddress+base), hex(s.Misc_VirtualSize), hex(s.PointerToRawData), hex(s.SizeOfRawData), 'chars' if s.Characteristics & 0x20000000 else '')
print('ImageBase', hex(base), 'Entry', hex(base+pe.OPTIONAL_HEADER.AddressOfEntryPoint))
