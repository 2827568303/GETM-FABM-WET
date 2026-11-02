p='regall.py'; s=open(p,encoding='utf-8').read()
s=s.replace("""for line in open(DUMP, encoding='utf-8', errors='replace'):
    line = line.strip()""","""raw = open(DUMP, 'rb').read()
if raw[:2] in (b'\\xff\\xfe', b'\\xfe\\xff'):
    text = raw.decode('utf-16', errors='replace')
else:
    text = raw.decode('utf-8', errors='replace')
for line in text.splitlines():
    line = line.strip()""")
open(p,'w',encoding='utf-8').write(s)
print('fixed')
