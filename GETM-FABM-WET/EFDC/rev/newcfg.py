import re
d=open('eems1251_setup.exe','rb').read()
print('size', len(d))
for p in (b'demoUrl', b'eemsdemo', b'wp-json', b'timeUrl', b'proxyUrl', b'add key', b'applicationSettings', b'Flexnet.Wrapper.Properties', b'DSILIC0.dll.config'):
    idx=[m.start() for m in re.finditer(re.escape(p), d)]
    print(f'{p.decode():28s} count={len(idx)} {[hex(i) for i in idx[:4]]}')
    if idx:
        i=idx[0]; print('   ', d[max(0,i-80):i+220])
