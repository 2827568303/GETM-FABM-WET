p='logredir2.js'; s=open(p,encoding='utf-8').read()
s=s.replace("function send(s2) { }\n","").replace("function send2(s) { }\n","")
open(p,'w',encoding='utf-8').write(s)
print('fixed')
