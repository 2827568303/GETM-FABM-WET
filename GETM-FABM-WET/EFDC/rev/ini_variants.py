import ctypes, ctypes.wintypes as wt, subprocess, os, time, io

EXE = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\EFDC 商业版8.4\EFDC_Explorer8.4.exe"
INI = r"C:\Users\Public\DSI\EEMS8.3\EEMS.ini"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\ini_variants.txt"
LIC = r"C:\Users\Public\DSI\EEMS8.4\license.lic"

u32 = ctypes.WinDLL("user32", use_last_error=True)
u32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u32.GetParent.argtypes = [wt.HWND]
u32.GetParent.restype = wt.HWND
E = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def cls(h):
    b = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, b, 256); return b.value


def txt(h):
    b = ctypes.create_unicode_buffer(1024); u32.GetWindowTextW(h, b, 1024); return b.value


TEMPLATE = """[LicenseInfo]
IsActivated=True
FeatureName={feature}
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
LicenseFile={lic}
IsReportUsage=False
"""

variants = ["EE_MULTI_TRIAL_8_4", "EEMS_MULTI_TRIAL", "EEMS_MULTI_TRIAL_8_4", "EE_MULTI_TRIAL_8_0", "PND_EE_MULTI_TRIAL_20160225"]
lines = []

for feat in variants:
    open(INI, "w", encoding="utf-8").write(TEMPLATE.format(feature=feat, lic=LIC))
    proc = subprocess.Popen([EXE], cwd=os.path.dirname(EXE))
    time.sleep(9)
    found = []

    def cb(h, l):
        p = wt.DWORD(0); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == proc.pid:
            c = cls(h)
            if c in ("#32770", "ThunderRT6FormDC", "ThunderRT6MDIForm", "ThunderRT6Form"):
                kids = []
                if c == "#32770":
                    def cb2(ch, l2):
                        t = txt(ch)
                        if t:
                            kids.append(t)
                        return True
                    u32.EnumChildWindows(h, E(cb2), 0)
                found.append("%s|%s|%s" % (c, txt(h), " / ".join(kids)))
        return True
    u32.EnumWindows(E(cb), 0)
    alive = proc.poll() is None
    lines.append("variant %-30s alive=%-5s windows=%s" % (feat, alive, found if found else "<none>"))
    subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
    time.sleep(0.5)

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
