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
    } catch (e) { return '?'; }
}
function rstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }

var INFOS = [0x4a3088, 0x4a49fc, 0x4a6468, 0x4a7fa0, 0x4a9b28, 0x4ab718, 0x4ad328, 0x4aefd0,
    0x4b0e20, 0x4b2cb0, 0x4b6bbc, 0x4b8e44, 0x4bb150, 0x4bd5e8, 0x4c24ac, 0x4c7378, 0x4cd0dc, 0x4d5204];

setTimeout(function () {
    var mb = Process.findModuleByName('msvbvm60.dll');
    var New2 = new NativeFunction(mb.findExportByName('__vbaNew2'), 'uint', ['pointer', 'pointer']);
    var IID_IDispatch = [0x00, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46];
    INFOS.forEach(function (ci) {
        try {
            var out = Memory.alloc(16); out.writeU64(0); out.writeU64(0);
            var hr = New2(ptr(ci), out);
            var obj = out.readPointer();
            var name = '';
            if (!obj.isNull()) {
                var vt = obj.readPointer();
                var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
                var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
                var pp = Memory.alloc(4);
                var qhr = QI(obj, iid, pp);
                if ((qhr >>> 0) === 0) {
                    var disp = pp.readPointer();
                    var dvt = disp.readPointer();
                    var GetTI = new NativeFunction(dvt.add(16).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
                    var ti = Memory.alloc(4);
                    var thr = GetTI(disp, 0, ti);
                    if ((thr >>> 0) === 0) {
                        var info = ti.readPointer();
                        var ivt = info.readPointer();
                        var GetDoc = new NativeFunction(ivt.add(48).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
                        var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), cx = Memory.alloc(4);
                        if ((GetDoc(info, -1, nm, doc, hf, cx) >>> 0) === 0) name = rstr(nm.readPointer());
                    }
                }
            }
            send2('CI ' + ci.toString(16) + ' hr=0x' + (hr >>> 0).toString(16) + ' obj=' + obj + ' name=' + JSON.stringify(name));
        } catch (e) { send2('CI ' + ci.toString(16) + ' ERR ' + e); }
    });
    send2('DONE');
}, 6000);
send2('loaded');

