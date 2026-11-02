import ctypes, ctypes.wintypes as wt, os, subprocess, sys, time
import frida

EXE = r"C:\EFDC84_RUN\EFDC_Explorer8.4.pristine.exe"
REV = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev"
INI = r"C:\Users\Public\DSI\EFDC_Explorer8.0\EFDC_Explorer.ini"
LOG = r"C:\Users\Public\DSI\EEMS8.4\ee_activation.log"
OUT = os.path.join(REV, "feat_variants.txt")

TEMPLATE = """[LicenseInfo]
IsActivated=True
FeatureName={feat}
ProdNameVersion=EFDC_Explorer8.4
LicType=PERPETUAL
IsDongle=False
ActivationID=A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47
FulfillmentID=14AC1ACA-EFD2-4C01-A1DD-4397B7F19715
FulfillDate=2020-01-01
ExpirationDate=2030-01-01
VersionDate=2030-01-01
LastDate=2030-01-01
TotalCopies=100
RemainingCopies=100
UniqueId=FB5BE307-6E85-410A-9265-B9389E71E38D
LicenseFile=C:\\Users\\Public\\DSI\\EEMS8.4\\license.lic
IsReportUsage=False
"""

JS = open(os.path.join(REV, "diag51.js"), encoding="utf-8").read()
variants = sys.argv[1:] or ["EE_MULTI_TRIAL_8_4", "EEMS_MULTI_TRIAL", "PND_EE_MULTI_TRIAL_20160225", "EE_MULTI_TRIAL_8_0"]

lines = []
for feat in variants:
    open(INI, "w", encoding="utf-8").write(TEMPLATE.format(feat=feat))
    start = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    pid = frida.spawn(EXE, cwd=os.path.dirname(EXE))
    sess = frida.attach(pid)
    sc = sess.create_script(JS)
    sc.load()
    frida.resume(pid)
    time.sleep(13)
    tail = ""
    try:
        with open(LOG, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
        tail = "\n".join([l for l in data[start:].splitlines() if l.strip()][-4:])
    except Exception as e:
        tail = "log err %s" % e
    lines.append("=== %s\n%s" % (feat, tail))
    try:
        os.kill(pid, 9)
    except Exception:
        pass
    time.sleep(0.5)

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))

