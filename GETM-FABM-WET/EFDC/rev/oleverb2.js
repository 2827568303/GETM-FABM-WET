'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
var done = false;
var IID_IOleObject = [0x12, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46];

function doShow() {
    try {
        var obj = ptr(0x16249b0).readPointer();
        send2('[' + t() + '] form obj=' + obj);
        if (obj.isNull()) return;
        var vt = obj.readPointer();
        var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
        var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IOleObject));
        var pp = Memory.alloc(4);
        var hr = QI(obj, iid, pp);
        send2('[' + t() + '] QI(IOleObject) hr=0x' + (hr >>> 0).toString(16) + ' p=' + pp.readPointer());
        if ((hr >>> 0) !== 0) return;
        var oo = pp.readPointer();
        var ovt = oo.readPointer();
        var DoVerb = new NativeFunction(ovt.add(11 * 4).readPointer(), 'uint',
            ['pointer', 'int', 'pointer', 'pointer', 'uint', 'pointer', 'pointer']);
        var hr2 = DoVerb(oo, -1, ptr(0), ptr(0), 0, ptr(0), ptr(0));
        send2('[' + t() + '] DoVerb(SHOW) hr=0x' + (hr2 >>> 0).toString(16));
    } catch (e) { send2('doShow ERR ' + e); }
}

setTimeout(function () {
    var u = Process.findModuleByName('user32.dll');
    var funcs = ['PeekMessageW', 'PeekMessageA', 'DispatchMessageW', 'DispatchMessageA'];
    funcs.forEach(function (fn) {
        var p = u.findExportByName(fn);
        if (!p) return;
        try {
            Interceptor.attach(p, {
                onEnter: function () {
                    if (!done && (Date.now() - T0) > 5500) { done = true; doShow(); }
                }
            });
            send2('hooked ' + fn);
        } catch (e) { send2('fail ' + fn); }
    });
}, 150);
send2('loaded');
