'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s, d) { send(s, d); }
function wstr(p) { try { return p.isNull() ? '<null>' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
function scanStack(ctx, n) {
    var out = [];
    try {
        var esp = ctx.esp;
        for (var i = 0; i < 0x500; i += 4) {
            var v = esp.add(i).readPointer();
            var x = v.toInt32() >>> 0;
            if (x >= 0x400000 && x < 0x166b000) out.push('exe+0x' + (x - 0x400000).toString(16));
            if (out.length >= (n || 8)) break;
        }
    } catch (e) { }
    return out.join(',');
}
var dumpN = 0;
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}

hook('oleaut32.dll', 'OleLoadPictureEx', function (args) {
    var pStm = args[0], size = args[1].toInt32();
    var info = '[' + t() + '] OleLoadPictureEx stm=' + pStm + ' size=' + size + ' stack=' + scanStack(this.context, 10);
    try {
        var vt = pStm.readPointer();
        var Read = new NativeFunction(vt.add(0xC).readPointer(), 'uint', ['pointer', 'pointer', 'uint', 'pointer']);
        var Seek = new NativeFunction(vt.add(0x14).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']);
        var buf = Memory.alloc(size > 0 && size < 200000 ? size : 4096);
        var nread = Memory.alloc(4);
        var hr = Read(pStm, buf, size > 0 && size < 200000 ? size : 4096, nread);
        var n = nread.readU32();
        Seek(pStm, 0, 0, ptr(0));
        info += ' readHr=0x' + (hr >>> 0).toString(16) + ' n=' + n;
        send2(info, buf.readByteArray(n));
    } catch (e) {
        send2(info + ' peek err ' + e);
    }
}, function (ret) {
    send2('[' + t() + ']   -> OleLoadPictureEx ret=0x' + (ret.toInt32() >>> 0).toString(16));
});

hook('msvbvm60.dll', 'rtcMsgBox', function (args) {
    // try deref as BSTR* and as BSTR
    var a0 = args[0];
    var cands = [];
    try { cands.push('d0=' + JSON.stringify(wstr(a0))); } catch (e) { }
    try { cands.push('dd0=' + JSON.stringify(wstr(a0.readPointer()))); } catch (e) { }
    send2('[' + t() + '] rtcMsgBox ' + cands.join(' | ') + ' stack=' + scanStack(this.context, 6));
}, null);

send2('script loaded');
