import re
d=open('eems1183_setup.exe','rb').read()
pats=[b'demoUrl',b'eemsdemo',b'wp-json',b'timeUrl',b'proxyUrl',b'licensing',b'eems-analytics',b'DSILIC',b'ENCRYPT_KEY']
for p in pats:
    idx=[m.start() for m in re.finditer(re.escape(p), d)]
    print(f'{p.decode():16s} count={len(idx)} first={[hex(i) for i in idx[:4]]}')
    if idx:
        i=idx[0]
        print('   ctx:', d[max(0,i-100):i+150])
