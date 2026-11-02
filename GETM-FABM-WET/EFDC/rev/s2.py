p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\strings_all.txt"
for line in open(p,encoding='utf-8'):
    va=int(line[:8],16)
    if 0x4EBB00<=va<=0x4EBF00: print(line.rstrip())
