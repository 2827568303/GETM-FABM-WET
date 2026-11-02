import frida, time, os, io, sys

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
OUT = os.path.join(REV, "slot_trials.txt")

slots = [int(x, 16) for x in sys.argv[1:]] or [0x310, 0x10, 0x18, 0xA4, 0x54, 0x20]
PIC = open(os.path.join(REV, "diag51.js"), encoding="utf-8").read()
BODY = open(os.path.join(REV, "diag66.js"), encoding="utf-8").read()

f = io.open(OUT, "w", encoding="utf-8")
for slot in slots:
    f.write("\n===== SLOT 0x%X =====\n" % slot)
    f.flush()
    js = "var SLOT = 0x%X;\n" % slot + PIC + "\n" + BODY
    pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
    sess = frida.attach(pid)
    sc = sess.create_script(js)
    sc.on("message", lambda m, d: (f.write(str(m.get("payload") or m.get("description")) + "\n"), f.flush()))
    try:
        sc.load()
    except Exception as e:
        f.write("load err %s\n" % e)
    frida.resume(pid)
    time.sleep(9)
    try:
        os.kill(pid, 9)
    except Exception:
        pass
    time.sleep(0.4)

f.close()
print("done")
