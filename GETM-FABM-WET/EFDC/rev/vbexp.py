import pefile, re
p = r"C:\Windows\SysWOW64\MSVBVM60.DLL"
pe = pefile.PE(p, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
names=[]
for e in pe.DIRECTORY_ENTRY_EXPORT.symbols:
    if e.name: names.append(e.name.decode())
print("base", hex(pe.OPTIONAL_HEADER.ImageBase), "exports", len(names))
print("--- containing Pic/Err/Hres/Pict ---")
for n in names:
    if re.search(r'(pic|Pic|err|Err|hres|Hres|Var|Obj)', n): print(n)
print("--- rtc* ---")
print(", ".join([n for n in names if n.startswith('rtc')]))
print("--- vba* sample ---")
print(", ".join([n for n in names if n.startswith('__vba')][:200]))
