import sys, struct, shutil, os, hashlib
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
BASE = 0x400000
# file offset == RVA for this exe (.text RVA 0x1000 == raw 0x1000)


def off(va):
    return va - BASE


def read(va, n):
    with open(EXE, 'rb') as f:
        f.seek(off(va))
        return f.read(n)


def write(va, data):
    with open(EXE, 'r+b') as f:
        f.seek(off(va))
        f.write(data)


def rel32(va, target):
    return struct.pack('<i', target - (va + 5))


def apply(patches, dry=False):
    ok = True
    for va, data, expect in patches:
        cur = read(va, len(expect))
        if cur != expect:
            print(f'MISMATCH at {va:#x}: expected {expect.hex()} got {cur.hex()}')
            ok = False
            continue
        if not dry:
            write(va, data)
        print(f'patch {va:#08x}: {expect.hex()} -> {data.hex()}')
    return ok


def jmp(va, target):
    return b'\xe9' + rel32(va, target)


NOP5 = b'\x90'*5
SKIPFORM = (0x81C5AC, jmp(0x81C5AC, 0x81CDA0), b'\xba\xa4\x54\x4f\x00')
P1 = [
    (0x81CA1F, NOP5, b'\xe8\xbc\x09\x00\x00'),
    (0x822450, b'\xb0\x01\xc2\x10\x00', b'\x55\x8b\xec\x83\xec'),
]
PATCHES = {
    'P1': P1,
    'P1_form': P1 + [(0x81C5AC, jmp(0x81C5AC, 0x81CD9B), b'\xba\xa4\x54\x4f\x00')],
    'form_nop1': [SKIPFORM, (0x828F84, NOP5, b'\xe8\x67\x6a\xff\xff')],
    'form_nop2': [SKIPFORM, (0x828F89, NOP5, b'\xe8\x32\x1d\xd4\x00')],
    'form_nop12': [SKIPFORM, (0x828F84, NOP5, b'\xe8\x67\x6a\xff\xff'), (0x828F89, NOP5, b'\xe8\x32\x1d\xd4\x00')],
    'form_jump40': [SKIPFORM, (0x828F84, jmp(0x828F84, 0x829040) + b'\x90'*0, b'\xe8\x67\x6a\xff\xff')],
    'form_jump8e': [SKIPFORM, (0x828F84, jmp(0x828F84, 0x828F8E), b'\xe8\x67\x6a\xff\xff')],
    'skip_to_form': [
        (0x81C5AC, jmp(0x81C5AC, 0x81CDA0), b'\xba\xa4\x54\x4f\x00'),
    ],
    'skip_to_end': [
        (0x81C5AC, jmp(0x81C5AC, 0x81CDA5), b'\xba\xa4\x54\x4f\x00'),
    ],
    'skip_license': [
        # at 0x81C5AC (start of body, after prologue/early-exit) jump to success path 0x81CD9B
        (0x81C5AC, jmp(0x81C5AC, 0x81CD9B), b'\xba\xa4\x54\x4f\x00'),
    ],
    'bypass_fno_only': [
        (0x81CA1F, b'\x90' * 5, b'\xe8\xbc\x09\x00\x00'),
    ],
}

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'restore':
        src = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\_backup_EFDC84_orig\EFDC_Explorer8.4.exe"
        shutil.copy2(src, EXE)
        print('restored from backup')
    elif cmd == 'hash':
        print(hashlib.sha256(open(EXE, 'rb').read()).hexdigest())
    else:
        name = cmd
        apply(PATCHES[name])
        print('applied', name)
