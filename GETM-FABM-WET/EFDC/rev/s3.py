lines=[l.rstrip() for l in open('strings_all.txt',encoding='utf-8')]
for l in lines:
    va=int(l[:8],16)
    if 0x4EDD00<=va<=0x4EE000: print(l)
