# -*- coding: utf-8 -*-
"""Make the demo sign-in automatic: pre-set email/password and 'remember password'
in %PUBLIC%\\DSI\\EEMS8.3\\EEMS.ini, so the app skips the login box on start.

python -X utf8 seed_login.py [email] [password]
"""
import os
import sys

PUBLIC = os.environ.get("PUBLIC") or r"C:\Users\Public"
INI = os.path.join(PUBLIC, "DSI", "EEMS8.3", "EEMS.ini")
EMAIL = sys.argv[1] if len(sys.argv) > 1 else "zhang.san8888@gmail.com"
PWD = sys.argv[2] if len(sys.argv) > 2 else "Efdc2026!"

KEYS = {
    "demo_email": EMAIL,
    "demo_password": PWD,
    "demo_rememberpassword": "True",
}


def main():
    os.makedirs(os.path.dirname(INI), exist_ok=True)
    text = ""
    if os.path.isfile(INI):
        try:
            text = open(INI, "rb").read().decode("latin-1")
        except Exception:
            text = ""

    lines = text.splitlines()
    have = {}
    out = []
    for ln in lines:
        k = ln.split("=", 1)[0].strip() if "=" in ln else ""
        if k in KEYS:
            if k not in have:
                have[k] = True
                out.append("%s=%s" % (k, KEYS[k]))
            continue
        out.append(ln)

    if not any(l.strip().startswith("[LicenseInfo]") for l in out):
        out.insert(0, "[LicenseInfo]")
    for k, v in KEYS.items():
        if k not in have:
            out.append("%s=%s" % (k, v))

    data = "\r\n".join(out).rstrip() + "\r\n"
    try:
        open(INI, "wb").write(data.encode("latin-1"))
        print("login seeded: %s (remember password = True)" % INI)
    except PermissionError:
        print("login seed skipped: %s is locked by a running EFDC (fine)" % INI)
    except Exception as e:
        print("login seed skipped: %s" % e)


if __name__ == "__main__":
    main()
