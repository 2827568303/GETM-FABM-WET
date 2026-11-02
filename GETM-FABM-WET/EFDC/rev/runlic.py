import frida, os, time
EXE=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_LIC.exe"
JS=open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\lictrace2.js",encoding='utf-8').read()
pid=frida.spawn(EXE, cwd=os.path.dirname(EXE))
s=frida.attach(pid); sc=s.create_script(JS)
sc.on('message', lambda m,d: print('[js]', m.get('payload') if m.get('type')=='send' else m))
sc.load(); frida.resume(pid)
time.sleep(6)
try: frida.kill(pid)
except: pass
