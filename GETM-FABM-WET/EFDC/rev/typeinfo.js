'use strict';
function send2(s) { send(s); }
function rstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }
var IID_IDispatch = [0x00, 0x04, 0x02, 0x00, 0, 0, 0, 0, 0xC0, 0, 0, 0, 0, 0, 0, 0x46];

setTimeout(function () {
    try {
        var obj = ptr(0x16249b0).readPointer();
        send2('obj=' + obj);
        if (obj.isNull()) return;
        var vt = obj.readPointer();
        var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
        var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
        var pp = Memory.alloc(4);
        var hr = QI(obj, iid, pp);
        send2('QI(IDispatch) hr=0x' + (hr >>> 0).toString(16));
        if ((hr >>> 0) !== 0) return;
        var disp = pp.readPointer();
        var dvt = disp.readPointer();
        var GetTypeInfo = new NativeFunction(dvt.add(16).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
        var ti = Memory.alloc(4);
        var h2 = GetTypeInfo(disp, 0, ti);
        send2('GetTypeInfo hr=0x' + (h2 >>> 0).toString(16));
        if ((h2 >>> 0) !== 0) return;
        var info = ti.readPointer();
        var ivt = info.readPointer();
        var GetTypeAttr = new NativeFunction(ivt.add(12).readPointer(), 'uint', ['pointer', 'pointer']);
        var GetFuncDesc = new NativeFunction(ivt.add(20).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
        var GetDoc = new NativeFunction(ivt.add(44).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
        var ReleaseFuncDesc = new NativeFunction(ivt.add(76).readPointer(), 'void', ['pointer', 'pointer']);
        var pa = Memory.alloc(4);
        if ((GetTypeAttr(info, pa) >>> 0) !== 0) { send2('GetTypeAttr failed'); return; }
        var attr = pa.readPointer();
        var cFuncs = attr.add(0x30).readU32();
        send2('cFuncs=' + cFuncs);
        var out = [];
        for (var i = 0; i < cFuncs; i++) {
            var fd = Memory.alloc(4);
            if ((GetFuncDesc(info, i, fd) >>> 0) !== 0) continue;
            var fdesc = fd.readPointer();
            var memid = fdesc.readInt32();
            var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), cx = Memory.alloc(4);
            var name = '';
            if ((GetDoc(info, memid, nm, doc, hf, cx) >>> 0) === 0) name = rstr(nm.readPointer());
            if (i >= 0x80) out.push(i + ':' + memid + ':' + name);
            ReleaseFuncDesc(info, fdesc);
        }
        send2('funcs[>=128]: ' + out.join(' | '));
    } catch (e) { send2('ERR ' + e); }
}, 6000);
send2('loaded');
