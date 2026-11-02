lines=[l.rstrip() for l in open('strings_all.txt',encoding='utf-8')]
for l in lines:
    va=int(l[:8],16)
    if 0x518300<=va<=0x518500: print(l)
