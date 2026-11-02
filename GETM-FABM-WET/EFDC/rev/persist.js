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
function guidBytes(s) {
    var m = s.replace(/[{}]/g, '').split('-'); var b = new Uint8Array(16);
    var d1 = parseInt(m[0], 16), d2 = parseInt(m[1], 16), d3 = parseInt(m[2], 16);
    b[0] = d1 & 255; b[1] = (d1 >> 8) & 255; b[2] = (d1 >> 16) & 255; b[3] = (d1 >>> 24) & 255;
    b[4] = d2 & 255; b[5] = (d2 >> 8) & 255; b[6] = d3 & 255; b[7] = (d3 >> 8) & 255;
    for (var i = 0; i < 4; i++) b[8 + i] = parseInt(m[3].substr(i * 2, 2), 16);
    for (var i = 0; i < 8; i++) b[12 + i] = parseInt(m[4].substr(i * 2, 2), 16);
    return b;
}
var IMAGELIST = '2c247f23-8591-11d1-b16a-00c0f0283628';
var IID_IUnknown = '{00000000-0000-0000-C000-000000000046}';
var IID_IPersistStream = '{00000109-0000-0000-C000-000000000046}';
var done = false;

setTimeout(function () {
    var ole32 = Process.findModuleByName('ole32.dll');
    Interceptor.attach(ole32.findExportByName('CoGetClassObject'), {
        onEnter: function (a) { this.c = gs(a[0]); this.ppv = a[4]; },
        onLeave: function (r) {
            if (this.c !== IMAGELIST || (r.toInt32() >>> 0) !== 0 || done) return;
            done = true;
            try {
                var cf = this.ppv.readPointer();
                var cvt = cf.readPointer();
                var CreateInstanceLic = new NativeFunction(cvt.add(28).readPointer(), 'uint',
                    ['pointer', 'pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
                var riid = Memory.alloc(16); riid.writeByteArray(guidBytes(IID_IUnknown));
                var pp = Memory.alloc(4);
                var hr = CreateInstanceLic(cf, ptr(0), ptr(0), riid, ptr(0), pp);
                var obj = pp.readPointer();
                send2('CreateInstanceLic(IID_IUnknown) hr=0x' + (hr >>> 0).toString(16) + ' obj=' + obj);
                if (obj.isNull()) return;
                var ovt = obj.readPointer();
                var QI = new NativeFunction(ovt.add(0).readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
                var psIid = Memory.alloc(16); psIid.writeByteArray(guidBytes(IID_IPersistStream));
                var pps = Memory.alloc(4);
                var hr2 = QI(obj, psIid, pps);
                var ps = pps.readPointer();
                send2('QI(IPersistStream) hr=0x' + (hr2 >>> 0).toString(16) + ' ps=' + ps);
                if (ps.isNull()) return;
                var pvt = ps.readPointer();
                var load = pvt.add(5 * 4).readPointer();
                var save = pvt.add(6 * 4).readPointer();
                send2('IPersistStream::Load=' + load + ' Save=' + save);
                send2('LOADRVA ' + load.sub(Process.findModuleByName('mscomctl.ocx').base).toString(16));
            } catch (e) { send2('ERR ' + e); }
        }
    });
    send2('hooked');
}, 300);
send2('loaded');

