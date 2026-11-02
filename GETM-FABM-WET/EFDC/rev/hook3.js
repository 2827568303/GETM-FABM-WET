'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function mod(addr) {
    try {
        var m = Process.findModuleByAddress(addr);
        if (m) return m.name + '+0x' + addr.sub(m.base).toString(16);
    } catch (e) { }
    return String(addr);
}
function send2(s) { send(s); }
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}
function wstr(p) { try { return p.isNull() ? '<null>' : p.readUtf16String(); } catch (e) { return '<bad>'; } }

var exeInfo = null;
function scanStack(ctx, nFrames) {
    var out = [];
    try {
        var exe = Process.enumerateModules()[0];
        var esp = ctx.esp;
        for (var i = 0; i < 0x400; i += 4) {
            var v;
            try { v = esp.add(i).readPointer(); } catch (e) { break; }
            var x = v.toInt32() >>> 0;
            if (x >= 0x400000 && x < 0x166b000) out.push('exe+0x' + (x - 0x400000).toString(16));
            if (out.length >= (nFrames || 8)) break;
        }
    } catch (e) { out.push('<scan err ' + e + '>'); }
    return out.join(',');
}

function peekStream(pStm) {
    try {
        var vt = pStm.readPointer();
        var Read = new NativeFunction(vt.add(0xC).readPointer(), 'uint', ['pointer', 'pointer', 'uint', 'pointer']);
        var Seek = new NativeFunction(vt.add(0x14).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']);
        var buf = Memory.alloc(96);
        var nread = Memory.alloc(4);
        var hr = Read(pStm, buf, 64, nread);
        var n = nread.readU32();
        var bytes = buf.readByteArray(n);
        Seek(pStm, 0, 0, ptr(0));
        var arr = new Uint8Array(bytes);
        var hex = '';
        for (var i = 0; i < Math.min(arr.length, 24); i++) hex += ('0' + arr[i].toString(16)).slice(-2);
        return 'hr=0x' + (hr >>> 0).toString(16) + ' n=' + n + ' head=' + hex;
    } catch (e) { return 'peek err ' + e; }
}

['OleLoadPictureEx', 'OleLoadPicture'].forEach(function (fn) {
    hook('oleaut32.dll', fn, function (args) {
        var s = '[' + t() + '] ' + fn + ' stm=' + args[0] + ' size=' + args[1].toInt32() + ' runmode=' + args[2].toInt32();
        s += ' | ' + peekStream(args[0]);
        s += ' | stack=' + scanStack(this.context, 10);
        send2(s);
    }, function (ret) { send2('[' + t() + ']   -> ' + fn + ' ret=0x' + (ret.toInt32() >>> 0).toString(16)); });
});

hook('msvbvm60.dll', '__vbaHresultCheckObj', function (args) {
    var hr = args[0].toInt32();
    if (hr < 0) send2('[' + t() + '] HRFAIL hr=0x' + (hr >>> 0).toString(16) + ' off=0x' + args[3].toInt32().toString(16) +
        ' stack=' + scanStack(this.context, 8));
}, null);

hook('msvbvm60.dll', 'rtcMsgBox', function (args) {
    send2('[' + t() + '] rtcMsgBox text=' + JSON.stringify(wstr(args[0])) +
        ' stack=' + scanStack(this.context, 8));
}, null);

send2('script loaded');
