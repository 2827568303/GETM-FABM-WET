p='loadhook.js'; s=open(p,encoding='utf-8').read()
s=s.replace("send2('using ' + which + ' load rva=' + load.sub(mod.base).toString(16));","var lm = Process.findModuleByAddress(load); send2('using ' + which + ' load=' + load + ' mod=' + (lm ? lm.name : '?') + ' rva=' + (lm ? load.sub(lm.base).toString(16) : '?'));")
open(p,'w',encoding='utf-8').write(s)
print('ok')
