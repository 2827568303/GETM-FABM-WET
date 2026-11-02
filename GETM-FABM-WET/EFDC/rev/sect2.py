import pefile
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
pe=pefile.PE(p); base=pe.OPTIONAL_HEADER.ImageBase
for s in pe.sections:
    n=s.Name.rstrip(b'\x00').decode(errors='ignore')
    print(f'{n:10s} VA={base+s.VirtualAddress:#010x} VSize={s.Misc_VirtualSize:#08x} RawPtr={s.PointerToRawData:#08x} RawSize={s.SizeOfRawData:#08x}')
def where(va):
    r=va-base
    for s in pe.sections:
        if s.VirtualAddress<=r<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.Name.rstrip(b'\x00').decode(errors='ignore'), r-s.VirtualAddress
    return None,None
for va in (0x4C16308,0x4D16A28,0x4F6E470,0x4F7127C):
    print(hex(va),'->',where(va))
