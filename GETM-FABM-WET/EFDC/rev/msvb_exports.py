import pefile
pe = pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL")
print("ImageBase", hex(pe.OPTIONAL_HEADER.ImageBase))
exps = [(e.address, e.name.decode() if e.name else '?') for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]
exps.sort()
def name_for(rva):
    best=None; bd=1e9
    for a,n in exps:
        if a <= rva and rva-a < bd: bd=rva-a; best=(a,n)
    return best
for rva in [0x384a7, 0x3847f, 0x38566, 0x891fa, 0x89b93, 0x89396, 0x1d761, 0x1d872, 0x10713c, 0x1146d0, 0x40fc0, 0x427c2, 0x42801, 0x3bd82, 0x10067, 0x2d961, 0x30145, 0xee366, 0xb7da4, 0xb2b23]:
    a,n = name_for(rva)
    print(f"0x{rva:06x} -> {n} (export@0x{a:06x}, +{rva-a:#x})")
