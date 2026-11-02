'use strict';
function send2(s) { send(s); }
function gs(p) {
    try {
        var b = new Uint8Array(p.readByteArray(16));
        function h(x) { return ('0' + x.toString(16)).slice(-2); }
        var d1 = (b[3] << 24 | b[2] << 16 | b[1] << 8 | b[0]) >>> 0, d2 = (b[5] << 8 | b[4]), d3 = (b[7] << 8 | b[6]), s = '';
        for (var i = 8; i < 16; i++) s += h(b[i]);
        return ('00000000' + d1.toString(16)).slice(-8) + '-' + ('0000' + d2.toString(16)).slice(-4) + '-' +
            ('0000' + d3.toString(16)).slice(-4) + '-' + s.substr(0, 4) + '-' + s.substr(4);
    } catch (e) { return ''; }
}
function rstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }

var FILES = [
    'TABCTL32.OCX', 'MSCOMCTL.OCX', 'COMCTL32.OCX', 'MSCOMCT2.OCX', 'MSFLXGRD.OCX', 'MSHFLXGD.OCX',
    'COMDLG32.OCX', 'RICHTX32.OCX', 'MSMASK32.OCX', 'MSINET.OCX', 'MSWINSCK.OCX', 'MSCOMM32.OCX',
    'MSMAPI32.OCX', 'MSCHRT20.OCX', 'MSADODC.OCX', 'MSDATLST.OCX', 'MSDatGrd.ocx', 'MSDatRep.ocx',
    'COMCT232.OCX', 'COMCT332.OCX', 'MCI32.OCX', 'PICCLP32.OCX', 'SYSINFO.OCX', 'DBLIST32.OCX', 'WBCLSDSR.OCX'
];
var DIR = 'C:\\EFDC84_LIC\\vb6\\';

setTimeout(function () {
    var oa = Process.findModuleByName('oleaut32.dll') || Module.load('oleaut32.dll');
    var LoadTypeLib = new NativeFunction(oa.findExportByName('LoadTypeLib'), 'uint', ['pointer', 'pointer']);
    FILES.forEach(function (fn) {
        var path = DIR + fn;
        try {
            var p = Memory.alloc(600); p.writeUtf16String(path);
            var out = Memory.alloc(4);
            var hr = LoadTypeLib(p, out);
            if (hr !== 0) { send2('INFO|' + fn + '|LOADFAIL|0x' + (hr >>> 0).toString(16)); return; }
            var tl = out.readPointer(); var vt = tl.readPointer();
            var GetLibAttr = new NativeFunction(vt.add(28).readPointer(), 'uint', ['pointer', 'pointer']);
            var la = Memory.alloc(4);
            var libGuid = '', ver = '';
            if (GetLibAttr(tl, la) === 0) {
                var a = la.readPointer(); var b = new Uint8Array(a.readByteArray(32));
                libGuid = gs(a);
                ver = (b[24] | (b[25] << 8)) + '.' + (b[26] | (b[27] << 8));
            }
            send2('INFO|' + fn + '|LIB|' + libGuid + '|' + ver);
            var GetCount = new NativeFunction(vt.add(12).readPointer(), 'uint', ['pointer']);
            var GetTI = new NativeFunction(vt.add(16).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
            var GetTIT = new NativeFunction(vt.add(20).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
            var n = GetCount(tl);
            for (var i = 0; i < n; i++) {
                var kind = Memory.alloc(4);
                if (GetTIT(tl, i, kind) !== 0) continue;
                if (kind.readU32() !== 5) continue;
                var ti = Memory.alloc(4);
                if (GetTI(tl, i, ti) !== 0) continue;
                var info = ti.readPointer(); var ivt = info.readPointer();
                var GetTypeAttr = new NativeFunction(ivt.add(12).readPointer(), 'uint', ['pointer', 'pointer']);
                var GetDoc = new NativeFunction(ivt.add(48).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
                var RelTA = new NativeFunction(ivt.add(76).readPointer(), 'void', ['pointer', 'pointer']);
                var ta = Memory.alloc(4);
                if (GetTypeAttr(info, ta) !== 0) continue;
                var attr = ta.readPointer();
                var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), cx = Memory.alloc(4);
                var name = '';
                if (GetDoc(info, -1, nm, doc, hf, cx) === 0) name = rstr(nm.readPointer());
                send2('CLS|' + fn + '|' + gs(attr) + '|' + name);
                RelTA(info, attr);
            }
        } catch (e) { send2('ERR|' + fn + '|' + e); }
    });
    send2('DONE');
}, 400);
send2('loaded');
