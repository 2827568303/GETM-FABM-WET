import re
d=open('eems1183_setup.exe','rb').read()
print('--- names table around 0x3af000 ---')
print(d[0x3af000:0x3af200])
print('--- xml headers ---')
idx=[m.start() for m in re.finditer(rb'<\?xml', d)]
print('count',len(idx),[hex(i) for i in idx[:8]])
for i in idx[:3]:
    print(hex(i), d[i:i+200])
print('--- PE test: MZ headers count ---')
idx=[m.start() for m in re.finditer(rb'MZ\x90\x00', d)]
print('MZ count', len(idx), [hex(i) for i in idx[:10]])
