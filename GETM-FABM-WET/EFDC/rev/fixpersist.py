p='persist.js'; s=open(p,encoding='utf-8').read()
s=s.replace("""                var CreateInstanceLic = new NativeFunction(cvt.add(28).readPointer(), 'uint',
                    ['pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
                var riid = Memory.alloc(16); riid.writeByteArray(guidBytes(IID_IUnknown));
                var pp = Memory.alloc(4);
                var lic = Memory.alloc(4); lic.writePointer(ptr(0));
                var hr = CreateInstanceLic(cf, ptr(0), riid, lic, pp);""","""                var CreateInstanceLic = new NativeFunction(cvt.add(28).readPointer(), 'uint',
                    ['pointer', 'pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
                var riid = Memory.alloc(16); riid.writeByteArray(guidBytes(IID_IUnknown));
                var pp = Memory.alloc(4);
                var hr = CreateInstanceLic(cf, ptr(0), ptr(0), riid, ptr(0), pp);""")
open(p,'w',encoding='utf-8').write(s)
print('fixed')
