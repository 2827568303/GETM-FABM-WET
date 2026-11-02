p='patch.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""PATCHES = {""","""NOP5 = b'\\x90'*5
SKIPFORM = (0x81C5AC, jmp(0x81C5AC, 0x81CDA0), b'\\xba\\xa4\\x54\\x4f\\x00')
PATCHES = {
    'form_nop1': [SKIPFORM, (0x828F84, NOP5, b'\\xe8\\x67\\x6a\\xff\\xff')],
    'form_nop2': [SKIPFORM, (0x828F89, NOP5, b'\\xe8\\x32\\x1d\\xd4\\x00')],
    'form_nop12': [SKIPFORM, (0x828F84, NOP5, b'\\xe8\\x67\\x6a\\xff\\xff'), (0x828F89, NOP5, b'\\xe8\\x32\\x1d\\xd4\\x00')],
    'form_jump40': [SKIPFORM, (0x828F84, jmp(0x828F84, 0x829040) + b'\\x90'*0, b'\\xe8\\x67\\x6a\\xff\\xff')],
    'form_jump8e': [SKIPFORM, (0x828F84, jmp(0x828F84, 0x828F8E), b'\\xe8\\x67\\x6a\\xff\\xff')],""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
