import pefile
for f in ('github_mscomctl.ocx','github_mscomct2.ocx'):
    try:
        pe=pefile.PE(f, fast_load=True)
        print(f, 'machine', hex(pe.FILE_HEADER.Machine))
    except Exception as e:
        print(f,'ERR',e)
