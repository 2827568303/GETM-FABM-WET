import re, json
res={}
for name in ('mscomctl.ocx','comctl32.ocx'):
    d=open('vb6cab2\\'+name,'rb').read()
    s=d.decode('latin1')
    g=set(m.upper() for m in re.findall(r'\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}', s))
    # utf-16
    s2=d.decode('utf-16le','ignore')
    g |= set(m.upper() for m in re.findall(r'\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}', s2))
    res[name]=sorted(g)
    print(name, len(g))
    for x in res[name][:40]: print('   ', x)
json.dump(res, open('ocx_guids.json','w'), indent=1)
