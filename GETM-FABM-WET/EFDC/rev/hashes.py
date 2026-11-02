import hashlib
for p in (r"C:\EFDC84_LIC\mscomctl.ocx", r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx"):
    print(hashlib.sha256(open(p,'rb').read()).hexdigest()[:16], p)
