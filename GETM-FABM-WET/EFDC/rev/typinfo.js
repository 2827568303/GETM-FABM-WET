'use strict';
function send2(s) { send(s); }
function guidStr(p) {
    var b = new Uint8Array(p.readByteArray(16));
    function h(x) { return ('0' + x.toString(16)).slice(-2); }
    var d1 = (b[3] << 24 | b[2] << 16 | b[1] << 8 | b[0]) >>> 0;
    var d2 = (b[5] << 8 | b[4]);
    var d3 = (b[7] << 8 | b[6]);
    var s = '';
    for (var i = 8; i < 16; i++) s += h(b[i]);
    return ('00000000' + d1.toString(16)).slice(-8) + '-' + ('0000' + d2.toString(16)).slice(-4) + '-' +
        ('0000' + d3.toString(16)).slice(-4) + '-' + s.substring(0, 4) + '-' + s.substring(4);
}
function readStr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }

setTimeout(function () {
    try {
        var oleaut = Process.findModuleByName('oleaut32.dll');
        if (!oleaut) oleaut = Module.load('oleaut32.dll');
        var LoadTypeLib = new NativeFunction(oleaut.findExportByName('LoadTypeLib'), 'uint', ['pointer', 'pointer']);
        var files = [
            'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\mscomctl.ocx',
            'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\comctl32.ocx'
        ];
        files.forEach(function (f) {
            var p = Memory.alloc(520); p.writeUtf16String(f);
            var out = Memory.alloc(4);
            var hr = LoadTypeLib(p, out);
            send2('=== ' + f.split('\\').pop() + ' LoadTypeLib hr=0x' + (hr >>> 0).toString(16) + ' tl=' + out.readPointer());
            if (hr !== 0) return;
            var tl = out.readPointer();
            var vt = tl.readPointer();
            function fn(off, ret, args) { return new NativeFunction(vt.add(off).readPointer(), ret, args); }
            var GetCount = fn(12, 'uint', ['pointer']);
            var GetTypeInfo = fn(16, 'uint', ['pointer', 'uint', 'pointer']);
            var GetTypeInfoType = fn(20, 'uint', ['pointer', 'uint', 'pointer']);
            var GetLibAttr = fn(28, 'uint', ['pointer', 'pointer']);
            var GetLibDoc = fn(36, 'uint', ['pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
            var libattr = Memory.alloc(4);
            if (GetLibAttr(tl, libattr) === 0) {
                var la = libattr.readPointer();
                var b = new Uint8Array(la.readByteArray(32));
                var major = b[24] | (b[25] << 8), minor = b[26] | (b[27] << 8);
                send2('LIBGUID ' + guidStr(la) + ' version=' + major + '.' + minor);
            }
            var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), ctx = Memory.alloc(4);
            if (GetLibDoc(tl, ptr(0), nm, doc, ctx) === 0) send2('LIBNAME ' + JSON.stringify(readStr(nm.readPointer())));
            var n = GetCount(tl);
            send2('TYPECOUNT ' + n);
            for (var i = 0; i < n; i++) {
                var kind = Memory.alloc(4);
                if (GetTypeInfoType(tl, i, kind) !== 0) continue;
                var ti = Memory.alloc(4);
                if (GetTypeInfo(tl, i, ti) !== 0) continue;
                var info = ti.readPointer();
                var ivt = info.readPointer();
                var GetTypeAttr = new NativeFunction(ivt.add(12).readPointer(), 'uint', ['pointer', 'pointer']);
                var GetDoc = new NativeFunction(ivt.add(48).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
                var ReleaseTypeAttr = new NativeFunction(ivt.add(76).readPointer(), 'void', ['pointer', 'pointer']);
                var ta = Memory.alloc(4);
                if (GetTypeAttr(info, ta) !== 0) continue;
                var attr = ta.readPointer();
                var typekind = attr.add(36).readU32();
                var tname = Memory.alloc(4);
                GetDoc(info, -1, tname, doc, ctx, ptr(0));
                send2('TYPE ' + i + ' kind=' + typekind + ' clsid=' + guidStr(attr) + ' name=' + JSON.stringify(readStr(tname.readPointer())));
                ReleaseTypeAttr(info, attr);
            }
        });
    } catch (e) { send2('ERR ' + e); }
}, 600);
send2('loaded');
