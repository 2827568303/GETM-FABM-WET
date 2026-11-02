import pefile
for p in (r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\mscomctl.ocx",
          r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\vb6cab2\comctl32.ocx"):
    pe=pefile.PE(p, fast_load=True)
    print(p.split('\\')[-1], 'machine', hex(pe.FILE_HEADER.Machine), 'size', __import__('os').path.getsize(p))
