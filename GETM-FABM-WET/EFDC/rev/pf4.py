p='patch.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""PATCHES = {""","""P1 = [
    (0x81CA1F, NOP5, b'\\xe8\\xbc\\x09\\x00\\x00'),
    (0x822450, b'\\xb0\\x01\\xc2\\x10\\x00', b'\\x55\\x8b\\xec\\x83\\xec'),
]
PATCHES = {
    'P1': P1,
    'P1_form': P1 + [(0x81C5AC, jmp(0x81C5AC, 0x81CD9B), b'\\xba\\xa4\\x54\\x4f\\x00')],""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
