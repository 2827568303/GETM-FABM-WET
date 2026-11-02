p='regtrace.js'; s=open(p,encoding='utf-8').read()
s=s.replace("""        var h = Module.load('C:\\\\EFDC84_LIC\\\\mscomctl.ocx');""","""        send2('--- loading OCX now ---');
        var h = Module.load('C:\\\\EFDC84_LIC\\\\mscomctl.ocx');
        send2('--- loaded ---');""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
