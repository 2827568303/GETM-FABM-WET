p='mkrt_realpic.py'; s=open(p,encoding='utf-8').read()
old="""cave_rva = None
for sec in pe.sections:"""
new="""cave_rva = 0x105600   # tail padding of .text (VSize ends at 0x1055D4), executable & unused
for sec in pe.sections:
    if False:"""
s=s.replace(old,new,1)
# remove the search loop body by leaving it unreachable; simpler: cut everything up to assert
import re
s=re.sub(r"cave_rva = 0x105600.*?\nassert cave_rva", "cave_rva = 0x105600\nassert cave_rva", s, flags=re.S)
open(p,'w',encoding='utf-8').write(s)
print(s[:1200])
