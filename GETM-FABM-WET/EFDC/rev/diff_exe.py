import sys, struct
A = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
B = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
a = open(A,'rb').read()
b = open(B,'rb').read()
print('sizes', len(a), len(b))
n = min(len(a), len(b))
runs = []
i = 0
while i < n:
    if a[i] != b[i]:
        j = i
        while j < n and a[j] != b[j]:
            j += 1
        runs.append((i, j))
        i = j
    else:
        i += 1
print('diff runs:', len(runs))
for (s, e) in runs:
    print(f'file_off 0x{s:08X}-0x{e-1:08X} ({e-s} B)  orig={a[s:e].hex()} cur={b[s:e].hex()}')

# PE section map so we can translate VA -> file offset
try:
    e_lfanew = struct.unpack_from('<I', a, 0x3C)[0]
    nsec = struct.unpack_from('<H', a, e_lfanew+6)[0]
    opt = e_lfanew+24
    image_base = struct.unpack_from('<I', a, opt+28)[0]
    print('image_base', hex(image_base), 'sections', nsec)
    secs = []
    so = opt + struct.unpack_from('<H', a, e_lfanew+20)[0]
    for k in range(nsec):
        off = so + 40*k
        name = a[off:off+8].rstrip(b'\x00').decode('latin1')
        vsize, vaddr, rawsize, rawptr = struct.unpack_from('<IIII', a, off+8)
        secs.append((name, vaddr, vsize, rawptr, rawsize))
        print(f'  {name:8s} RVA=0x{vaddr:08X} VSize=0x{vsize:08X} RawPtr=0x{rawptr:08X} RawSize=0x{rawsize:08X}')
    def va2off(va):
        rva = va - image_base
        for (name, vaddr, vsize, rawptr, rawsize) in secs:
            if vaddr <= rva < vaddr + max(vsize, rawsize):
                return rawptr + (rva - vaddr)
        return None
    print('--- diff runs mapped to VA ---')
    for (s, e) in runs:
        va = None
        for (name, vaddr, vsize, rawptr, rawsize) in secs:
            if rawptr <= s < rawptr + rawsize:
                va = image_base + vaddr + (s - rawptr)
                break
        print(f'  off 0x{s:08X} -> VA {hex(va) if va else "?"}  orig={a[s:e].hex()} cur={b[s:e].hex()}')
except Exception as ex:
    print('pe parse err', ex)
