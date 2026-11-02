'use strict';
function send2(s) { send(s); }
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
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
var IMAGELIST = '2c247f23-8591-11d1-b16a-00c0f0283628';
var done = false;
setTimeout(function () {
    var ole32 = Process.findModuleByName('ole32.dll');
    var mod = Process.findModuleByName('mscomctl.ocx');
    Interceptor.attach(ole32.findExportByName('CoGetClassObject'), {
        onEnter: function (a) { this.c = gs(a[0]); this.ppv = a[4]; },
        onLeave: function (r) {
            if (this.c !== IMAGELIST || (r.toInt32() >>> 0) !== 0 || done) return;
            try {
                var cf = this.ppv.readPointer();
                var cvt = cf.readPointer();
                var CIL = new NativeFunction(cvt.add(28).readPointer(), 'uint',
                    ['pointer', 'pointer', 'pointer', 'pointer', 'pointer', 'pointer']);
                var riid = Memory.alloc(16);
                riid.writeByteArray(new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0xC0, 0, 0, 0, 0, 0, 0, 0x46]));
                var pp = Memory.alloc(4);
                var hr = CIL(cf, ptr(0), ptr(0), riid, ptr(0), pp);
                var obj = pp.readPointer();
                send2('CreateInstanceLic hr=0x' + (hr >>> 0).toString(16) + ' obj=' + obj);
                if (obj.isNull()) return;
                var ovt = obj.readPointer();
                var QI = new NativeFunction(ovt.add(0).readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
                var cands = [
                  ['IPersistStreamInit', [0x80,0x23,0xD5,0x7F,0x07,0x4E,0x1B,0x10,0xAE,0x2D,0x08,0x00,0x2B,0x2E,0xC7,0x13], 5],
                  ['IPersistPropertyBag', [0x60,0x4F,0xD8,0x37,0xCB,0x42,0xCE,0x11,0x81,0x35,0x00,0xAA,0x00,0x4B,0xB8,0x51], 5],
                  ['IPersistStream', [0x09,0x01,0,0,0,0,0,0,0xC0,0,0,0,0,0,0,0x46], 5],
                  ['IPersistStorage', [0x0A,0x01,0,0,0,0,0,0,0xC0,0,0,0,0,0,0,0x46], 6]
                ];
                var ps = ptr(0), loadIdx = 5, which = '';
                for (var ci = 0; ci < cands.length; ci++) {
                  var ii = Memory.alloc(16); ii.writeByteArray(new Uint8Array(cands[ci][1]));
                  var p2 = Memory.alloc(4);
                  var h2 = QI(obj, ii, p2);
                  send2('QI(' + cands[ci][0] + ') hr=0x' + (h2 >>> 0).toString(16) + ' p=' + p2.readPointer());
                  if ((h2 >>> 0) === 0) { ps = p2.readPointer(); loadIdx = cands[ci][2]; which = cands[ci][0]; break; }
                }
                if (ps.isNull()) return;
                done = true;
                var pvt = ps.readPointer();
                var load = pvt.add(loadIdx * 4).readPointer();
                var lm = Process.findModuleByAddress(load); send2('using ' + which + ' load=' + load + ' mod=' + (lm ? lm.name : '?') + ' rva=' + (lm ? load.sub(lm.base).toString(16) : '?'));
                Interceptor.attach(load, {
                    onEnter: function (a) { this.s = a[1]; },
                    onLeave: function (r3) { send2('IPersistStream::Load hr=0x' + ((r3.toInt32() >>> 0).toString(16))); }
                });
                send2('hooked Load');
            } catch (e) { send2('ERR ' + e); }
        }
    });
    send2('hooked CoGetClassObject');
}, 300);
send2('loaded');
