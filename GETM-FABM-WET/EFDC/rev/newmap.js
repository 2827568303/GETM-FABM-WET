'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function rstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }
var IID_IDispatch = [0x00, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46];
var seen = {};

function nameOf(obj) {
    try {
        var vt = obj.readPointer();
        var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
        var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
        var pp = Memory.alloc(4);
        if ((QI(obj, iid, pp) >>> 0) !== 0) return '';
        var disp = pp.readPointer();
        if (disp.isNull()) return '';
        var dvt = disp.readPointer();
        var GetTI = new NativeFunction(dvt.add(16).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
        var ti = Memory.alloc(4);
        if ((GetTI(disp, 0, ti) >>> 0) !== 0) return '';
        var info = ti.readPointer();
        if (info.isNull()) return '';
        var ivt = info.readPointer();
        var GetDoc = new NativeFunction(ivt.add(48).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
        var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), cx = Memory.alloc(4);
        if ((GetDoc(info, -1, nm, doc, hf, cx) >>> 0) !== 0) return '';
        return rstr(nm.readPointer());
    } catch (e) { return '<err ' + e + '>'; }
}

setTimeout(function () {
    var mb = Process.findModuleByName('msvbvm60.dll');
    var New2 = new NativeFunction(mb.findExportByName('__vbaNew2'), 'uint', ['pointer', 'pointer']);
    Interceptor.attach(mb.findExportByName('__vbaNew2'), {
        onEnter: function (a) { this.info = a[0]; this.out = a[1]; },
        onLeave: function (r) {
            try {
                var obj = this.out.readPointer();
                if (obj.isNull()) return;
                var key = this.info.toString();
                if (seen[key]) return;
                seen[key] = 1;
                var nm = nameOf(obj);
                send2('[' + t() + '] New2 info=' + this.info + ' name=' + JSON.stringify(nm));
            } catch (e) { send2('hook err ' + e); }
        }
    });
    send2('hooked New2');
}, 150);
send2('loaded');
