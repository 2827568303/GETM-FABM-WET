import re
d=open('eems1183_setup.exe','rb').read()
for p in (b'add key', b'applicationSettings', b'Flexnet.Wrapper.Properties', b'DefaultFeatureVersion', b'configuration>', b'ClientSettingsProvider'):
    idx=[m.start() for m in re.finditer(re.escape(p), d)]
    print(f'{p.decode():28s} count={len(idx)} {[hex(i) for i in idx[:4]]}')
    if idx:
        i=idx[0]; print('   ', d[max(0,i-120):i+200])
