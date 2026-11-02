import re
p=r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\strings_all.txt"
rows=[]
for line in open(p,encoding='utf-8'):
    va=int(line[:8],16)
    if 0x5E7800 <= va <= 0x5E8300:
        rows.append(line.rstrip())
print("=== strings 0x5E7800-0x5E8300 ===")
for r in rows: print(r)
