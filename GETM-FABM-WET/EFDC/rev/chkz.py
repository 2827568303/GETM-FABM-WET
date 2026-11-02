for f in ('innoextract.zip','vb6rtlib.exe'):
    d=open(f,'rb').read()
    print(f, len(d), d[:16].hex(), d[:16])
