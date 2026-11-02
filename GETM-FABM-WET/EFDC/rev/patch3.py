p='patch.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""PATCHES = {
    'skip_license': [""","""PATCHES = {
    'skip_to_form': [
        (0x81C5AC, jmp(0x81C5AC, 0x81CDA0), b'\\xba\\xa4\\x54\\x4f\\x00'),
    ],
    'skip_to_end': [
        (0x81C5AC, jmp(0x81C5AC, 0x81CDA5), b'\\xba\\xa4\\x54\\x4f\\x00'),
    ],
    'skip_license': [""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
