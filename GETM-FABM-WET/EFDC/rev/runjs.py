import frida, time, os, io, sys

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
OUT = os.path.join(REV, "fileopen_out.txt")
JS = open(os.path.join(REV, sys.argv[1] if len(sys.argv) > 1 else "diag48.js"), encoding="utf-8").read()

f = io.open(OUT, "w", encoding="utf-8")


def on_msg(m, d):
    txt = m.get("payload") or m.get("description")
    f.write(str(txt) + "\n")
    f.flush()


pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
s = frida.attach(pid)
sc = s.create_script(JS)
sc.on("message", on_msg)
sc.load()
frida.resume(pid)
f.write("pid %d\n" % pid)
f.flush()
time.sleep(8)
try:
    os.kill(pid, 9)
except Exception:
    pass
f.close()
print("done")
