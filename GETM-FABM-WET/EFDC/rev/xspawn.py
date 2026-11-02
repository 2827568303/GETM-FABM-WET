import os, sys, time, threading
import frida

BASE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC"
EXE = os.path.join(BASE, "EFDC 商业版8.4", "EFDC_Explorer8.4.exe")
js_file = sys.argv[1] if len(sys.argv) > 1 else None
JS = open(js_file, encoding='utf-8').read() if js_file else "send('trivial ready');"

def step(msg):
    print('[%6.2f] %s' % (time.time() - T0, msg), flush=True)

T0 = time.time()
step('spawning')
pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
step('spawned pid=%d' % pid)
session = frida.attach(pid)
step('attached')
script = session.create_script(JS)
script.on('message', lambda m, d: step('msg %s' % (m.get('payload') if m.get('type') == 'send' else m)))
step('loading script')
script.load()
step('script loaded')
frida.resume(pid)
step('resumed')
time.sleep(8)
step('done sleeping')
