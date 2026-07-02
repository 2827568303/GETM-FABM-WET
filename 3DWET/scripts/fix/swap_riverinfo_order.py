# riverinfo.dat 格式：尝试 j i 顺序而不是 i j
with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\riverinfo.dat', 'w') as f:
    f.write('5\n')
    f.write('35 5 DAYUN -1 -1\n')      # j=35, i=5
    f.write('49 12 YIHE -1 -1\n')       # j=49, i=12
    f.write('3 23 LUONAN -1 -1\n')      # j=3, i=23
    f.write('13 35 ZHANGSHAN -1 -1\n')  # j=13, i=35
    f.write('26 39 YANGHE -1 -1\n')     # j=26, i=39
print('已修改 riverinfo.dat: j i 顺序（0-indexed）')
