import sys, time, os
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import frida

EXE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[3] if len(sys.argv) > 3 else 'hook.js')

src = open(SCRIPT, encoding='utf-8').read()
dev = frida.get_local_device()
print('spawning', EXE)
pid = dev.spawn([EXE], cwd=os.path.dirname(EXE))
print('pid', pid)
sess = dev.attach(pid)
script = sess.create_script(src)
lines = []


def on_message(msg, data):
    if msg['type'] == 'send':
        print(msg['payload'], flush=True)
        lines.append(str(msg['payload']))
    else:
        print('ERR', msg, flush=True)


script.on('message', on_message)
script.load()
dev.resume(pid)
t0 = time.time()
try:
    while time.time() - t0 < DUR:
        time.sleep(0.2)
        try:
            procs = dev.enumerate_processes()
            if not any(p.pid == pid for p in procs):
                print('process gone after %.2fs' % (time.time() - t0))
                break
        except Exception:
            pass
finally:
    try:
        dev.kill(pid)
    except Exception as e:
        print('kill:', e)
    print('done')
