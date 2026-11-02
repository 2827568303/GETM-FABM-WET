p='fr.py'; s=open(p,encoding='utf-8').read()
s=s.replace("SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hook.js')","SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[3] if len(sys.argv) > 3 else 'hook.js')")
open(p,'w',encoding='utf-8').write(s)
print('ok')
