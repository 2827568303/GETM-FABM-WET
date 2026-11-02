'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function scanStack(ctx, n) {
    var out = [];
    try {
        for (var i = 0; i < 0x400; i += 4) {
            var x = ctx.esp.add(i).readPointer().toInt32() >>> 0;
            if (x >= 0x400000 && x < 0x166b000) out.push('exe+0x' + (x - 0x400000).toString(16));
            if (out.length >= (n || 6)) break;
        }
    } catch (e) { }
    return out.join(',');
}
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}

hook('oleaut32.dll', 'OleLoadPictureEx', function (args) {
    var pStm = args[0];
    var info = '[' + t() + '] OLEEX stm=' + pStm + ' size=' + args[1].toInt32() +
        ' runmode=' + args[2].toInt32() + ' riid=' + args[3] +
        ' x=' + args[4].toInt32() + ' y=' + args[5].toInt32() + ' flags=0x' + args[6].toInt32().toString(16) +
        ' ppv=' + args[7];
    try {
        var vt = pStm.readPointer();
        var Seek = new NativeFunction(vt.add(0x14).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']);
        var pos = Memory.alloc(8);
        var hr = Seek(pStm, 0, 1, pos);   // SEEK_CUR
        info += ' seekCurHr=0x' + (hr >>> 0).toString(16) + ' pos=' + pos.readS64();
    } catch (e) { info += ' seekerr=' + e; }
    info += ' stack=' + scanStack(this.context, 8);
    send2(info);
}, function (ret) {
    send2('[' + t() + ']   -> OLEEX ret=0x' + (ret.toInt32() >>> 0).toString(16));
});

send2('script loaded');
