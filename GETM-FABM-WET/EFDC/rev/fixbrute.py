p='brute_forms.py'; s=open(p,encoding='utf-8').read()
s=s.replace('''def patch(ci):
    d = bytearray(open(EXE, "rb").read())
    o = SITE - 0x400000
    d[o:o+5] = b"\\x68" + ci.to_bytes(4, "little")
    open(EXE, "wb").write(bytes(d))''','''def patch(ci):
    for _ in range(30):
        try:
            subprocess.run(["taskkill","/F","/IM","EFDC_Explorer8.4.exe"], capture_output=True)
            time.sleep(0.3)
            d = bytearray(open(EXE, "rb").read())
            o = SITE - 0x400000
            d[o:o+5] = b"\\x68" + ci.to_bytes(4, "little")
            open(EXE, "wb").write(bytes(d))
            return
        except PermissionError:
            time.sleep(0.5)
    raise RuntimeError("cannot write exe")''')
open(p,'w',encoding='utf-8').write(s)
print('patched script')
