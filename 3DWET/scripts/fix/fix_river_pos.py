# 把河流位置改到边界上
with open(r'c:\Users\dinod\Desktop\GETM-FABM-WET\test_case\riverinfo.dat', 'w') as f:
    f.write('1\n')
    f.write('1 3 TEST_RIV -1 -1\n')  # 西边界
print('已修改河流位置到西边界')
