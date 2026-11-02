import pefile
pe=pefile.PE(r"C:\Windows\SysWOW64\MSVBVM60.DLL", fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
ex=sorted([(e.address,e.name.decode() if e.name else f'ord{e.ordinal}') for e in pe.DIRECTORY_ENTRY_EXPORT.symbols])
import bisect
target=0xe306b
prev=[x for x in ex if x[0]<=target][-4:]
nxt=[x for x in ex if x[0]>target][:4]
print('near 0xe306b:', [(hex(a),n) for a,n in prev+nxt])
# which exports are exactly in 0xe2000-0xe4000
print([ (hex(a),n) for a,n in ex if 0xe2000<=a<=0xe4000])
print('near 0x7f155:', [(hex(a),n) for a,n in [x for x in ex if x[0]<=0x7f155][-4:]+[x for x in ex if x[0]>0x7f155][:4]])
