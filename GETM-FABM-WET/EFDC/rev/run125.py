import subprocess, time, os, sys
e = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EEMS125\EFDC+Explorer.exe"
p = subprocess.Popen([e], cwd=os.path.dirname(e))
t0 = time.time()
while time.time() - t0 < 12:
    if p.poll() is not None:
        print('exited code', hex(p.returncode & 0xffffffff), 'after', round(time.time()-t0, 2), 's')
        break
    time.sleep(0.2)
else:
    print('still running after 12s, pid', p.pid)
    try:
        p.terminate()
    except Exception:
        pass
