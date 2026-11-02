'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function mod(a) { try { var m = Process.findModuleByAddress(a); if (m) return m.name + '+0x' + a.sub(m.base).toString(16); } catch (e) { } return String(a); }

var BMP = null;
function makeBmp() {
    // 16x16 24bpp BMP
    var w = 16, h = 16, row = (w * 3 + 3) & ~3;
    var size = 14 + 40 + row * h;
    var b = new Uint8Array(size);
    b[0] = 0x42; b[1] = 0x4D;
    var dv = new DataView(b.buffer);
    dv.setUint32(2, size, true); dv.setUint32(10, 54, true);
    dv.setUint32(14, 40, true); dv.setInt32(18, w, true); dv.setInt32(22, h, true);
    dv.setUint16(26, 1, true); dv.setUint16(28, 24, true); dv.setUint32(34, row * h, true);
    for (var i = 54; i < size; i += 3) { b[i] = 0x20; b[i + 1] = 0x80; b[i + 2] = 0x40; }
    return b;
}

function runTest(tag) {
    try {
        var ole32 = Process.findModuleByName('ole32.dll');
        var oleaut = Process.findModuleByName('oleaut32.dll');
        function N(m, n, r, a) { return new NativeFunction(m.findExportByName(n), r, a); }
        var CreateStream = N(ole32, 'CreateStreamOnHGlobal', 'uint', ['pointer', 'int', 'pointer']);
        var OleLoadPictureEx = N(oleaut, 'OleLoadPictureEx', 'uint', ['pointer', 'int', 'uint', 'pointer', 'uint', 'uint', 'uint', 'pointer']);
        var data = makeBmp();
        var mem = Memory.alloc(data.length); mem.writeByteArray(data);
        var p = Memory.alloc(4);
        var hr0 = CreateStream(ptr(0), 1, p);
        var stm = p.readPointer();
        var out = tag + ' (' + t() + ') createHr=0x' + (hr0 >>> 0).toString(16) + ' stm=' + stm;
        if (stm.isNull()) { send2(out + ' NULL STREAM'); return; }
        var vt = stm.readPointer();
        var W = new NativeFunction(vt.add(16).readPointer(), 'uint', ['pointer', 'pointer', 'uint', 'pointer']);
        var S = new NativeFunction(vt.add(20).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']);
        var St = new NativeFunction(vt.add(48).readPointer(), 'uint', ['pointer', 'pointer', 'int']);
        var n = Memory.alloc(4), pos = Memory.alloc(8), st = Memory.alloc(80);
        var hw = W(stm, mem, data.length, n);
        var hs = S(stm, 0, 0, pos);
        var hst = St(stm, st, 1);
        out += ' writeHr=0x' + (hw >>> 0).toString(16) + ' n=' + n.readU32() + ' seekHr=0x' + (hs >>> 0).toString(16) +
            ' statHr=0x' + (hst >>> 0).toString(16) + ' cb=' + st.add(8).readS64();
        var iid = Memory.alloc(16);
        iid.writeByteArray(new Uint8Array([0x80, 0x09, 0xf8, 0x7b, 0x32, 0xbf, 0x1a, 0x10, 0x8b, 0xbb, 0x00, 0xaa, 0x00, 0x30, 0x0c, 0xab]));
        var pp = Memory.alloc(4);
        var hr = OleLoadPictureEx(stm, data.length, 0, iid, 0, 0, 0, pp);
        out += ' loadHr=0x' + (hr >>> 0).toString(16) + ' pic=' + pp.readPointer();
        send2(out);
    } catch (e) { send2(tag + ' err ' + e); }
}

// 1) on a frida timer thread
setTimeout(function () {
    try {
        var ole32 = Process.findModuleByName('ole32.dll');
        if (ole32) { var OI = new NativeFunction(ole32.findExportByName('OleInitialize'), 'int', ['pointer']); OI(ptr(0)); }
    } catch (e) { }
    runTest('timer');
}, 900);

// 2) on the app main thread, inside its own OleLoadPictureEx call
try {
    var oleautm = Process.findModuleByName('oleaut32.dll');
    if (oleautm) {
        Interceptor.attach(oleautm.findExportByName('OleLoadPictureEx'), function () {
            send2('[main-thread] app called OleLoadPictureEx from ' + mod(this.returnAddress));
            runTest('main');
        });
    }
} catch (e) { send2('hook err ' + e); }
send2('loaded');
