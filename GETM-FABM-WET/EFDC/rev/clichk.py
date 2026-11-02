import struct, os
for name in ('DSILIC0.dll','DSILIC1.dll','EFDC_LIC.exe'):
    p=os.path.join(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4", name)
    d=open(p,'rb').read()
    pe=struct.unpack_from('<I', d, 0x3C)[0]
    coff=pe+4
    nsec=struct.unpack_from('<H', d, coff+2)[0]
    optsz=struct.unpack_from('<H', d, coff+16)[0]
    opt=coff+20
    magic=struct.unpack_from('<H', d, opt)[0]
    plus = magic==0x20b
    dd=opt+(0x70 if plus else 0x60)
    cli_rva, cli_size = struct.unpack_from('<II', d, dd+14*8)
    machine=struct.unpack_from('<H', d, coff)[0]
    print(f'{name:14s} size={len(d):9d} machine={machine:#06x} magic={magic:#06x} CLI_rva={cli_rva:#x} size={cli_size}')
