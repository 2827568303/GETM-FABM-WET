import frida, time, sys
try:
    pid = frida.spawn([r"C:\Windows\System32\notepad.exe"])
    print("spawned", pid)
    s = frida.attach(pid)
    print("attached")
    sc = s.create_script("send('hi from js')")
    sc.on('message', lambda m, d: print("msg", m))
    sc.load()
    frida.resume(pid)
    print("resumed")
    time.sleep(1.5)
    frida.kill(pid)
    print("killed OK")
except Exception as e:
    print("FRIDA ERR", e)
