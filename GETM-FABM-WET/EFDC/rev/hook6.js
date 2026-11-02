'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}

var SEEKERS = {};
function seeker(pStm) {
    var key = pStm.toString();
    if (!SEEKERS[key]) {
        var vt = pStm.readPointer();
        SEEKERS[key] = {
            Seek: new NativeFunction(vt.add(0x14).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']),
            pos: Memory.alloc(8)
        };
    }
    return SEEKERS[key];
}

hook('oleaut32.dll', 'OleLoadPictureEx', function (args) {
    var s = seeker(args[0]);
    var hr0 = s.Seek(args[0], 0, 1, s.pos);
    var before = s.pos.readS64();
    var hr = s.Seek(args[0], 0, 0, s.pos);   // SEEK_SET 0
    send2('[' + t() + '] OLEEX size=' + args[1].toInt32() + ' posBefore=' + before + ' seekHr=0x' + (hr >>> 0).toString(16));
}, function (ret) {
    send2('[' + t() + ']   -> OLEEX ret=0x' + (ret.toInt32() >>> 0).toString(16));
});

send2('script loaded');
