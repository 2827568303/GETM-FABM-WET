import re, struct
d=open('eems1251_setup.exe','rb').read()
for p in (b'DSILIC', b'lmgract', b'FNP_Act', b'EFDC_Explorer', b'.dll', b'EFDC_LIC', b'license'):
    idx=[m.start() for m in re.finditer(re.escape(p), d)]
    print(f'{p.decode():16s} count={len(idx)} {[hex(i) for i in idx[:5]]}')
# PE parse
pe=struct.unpack_from('<I',d,0x3C)[0]
coff=pe+4; nsec=struct.unpack_from('<H',d,coff+2)[0]; optsz=struct.unpack_from('<H',d,coff+16)[0]
opt=coff+20; magic=struct.unpack_from('<H',d,opt)[0]; plus=magic==0x20b
dd=opt+(0x70 if plus else 0x60)
res_rva,res_sz=struct.unpack_from('<II',d,dd+2*8)
print(f'nsec={nsec} res_rva={res_rva:#x} size={res_sz}')
sections=[]
so=opt+optsz
for i in range(nsec):
    o=so+i*40
    nm=d[o:o+8].rstrip(b'\x00').decode(errors='ignore')
    vs,va,rs,ra=struct.unpack_from('<IIII',d,o+8)
    sections.append((nm,va,vs,ra,rs)); 
print('end of sections raw:', hex(max(ra+rs for _,_,_,ra,rs in sections)))
for s in sections: print(' ',s[0], hex(s[1]),hex(s[2]),hex(s[3]),hex(s[4]))
