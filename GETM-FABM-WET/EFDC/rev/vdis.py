import sys, struct, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

PRISTINE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
pe = pefile.PE(PRISTINE, fast_load=False)
IB = pe.OPTIONAL_HEADER.ImageBase
secs = [(s.Name.rstrip(b'\x00').decode(), IB + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

iat = {}
try:
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode()
        for imp in entry.imports:
            if imp.address:
                iat[imp.address] = (dll, (imp.name or b'').decode('latin1'))
except Exception as e:
    print('iat err', e)

data = open(PRISTINE, 'rb').read()

def va2off(va):
    for (n, base, vsize, rawptr, rawsize) in secs:
        if base <= va < base + max(vsize, rawsize):
            return rawptr + (va - base)
    return None

def read(va, n):
    o = va2off(va)
    if o is None:
        return None
    return data[o:o+n]

def thunk(va):
    """VB6 import thunk: FF 25 xx xx xx xx  -> resolve import name"""
    b = read(va, 6)
    if b and len(b) == 6 and b[0] == 0xFF and b[1] == 0x25:
        slot = struct.unpack('<I', b[2:6])[0]
        # slot may already be the IAT address
        for cand in (slot, va2offback(slot) if False else slot):
            pass
        d = iat.get(slot)
        if not d:
            # VB6 thunks often point to a 'pointer table' inside the exe
            v = read(slot, 4)
            if v:
                p = struct.unpack('<I', v)[0]
                d = iat.get(p)
        if d:
            return '%s!%s' % d
        return 'thunk->0x%X' % slot
    return None

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

def dis(va_start, count=40):
    off = va2off(va_start)
    code = data[off:off + count * 8]
    print('--- disasm VA 0x%X (off 0x%X) ---' % (va_start, off))
    for ins in md.disasm(code, va_start):
        extra = ''
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            pass
        if ins.mnemonic == 'call' and ins.op_str.startswith('dword ptr [0x'):
            t = int(ins.op_str.split('[')[1].split(']')[0], 16)
            b = read(t, 6)
            if b and b[0] == 0xFF and b[1] == 0x25:
                nm = thunk(t)
                if nm:
                    extra = '   ; => ' + nm
            else:
                v = read(t, 4)
                if v:
                    extra = '   ; slot=0x%X' % struct.unpack('<I', v)[0]
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            t = int(ins.op_str, 16)
            nm = thunk(t)
            if nm:
                extra = '   ; => ' + nm
        print('  0x%08X  %-24s %-8s %-24s%s' % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, extra))

if __name__ == '__main__':
    for a in sys.argv[1:]:
        va, cnt = (a.split(':') + ['40'])[:2]
        dis(int(va, 16), int(cnt))
