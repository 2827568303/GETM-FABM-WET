'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
var done = false;

setTimeout(function () {
    var u = Process.findModuleByName('user32.dll');
    var names = ['DispatchMessageW', 'DispatchMessageA', 'PeekMessageW', 'GetMessageW'];
    names.forEach(function (n) {
        var p = u.findExportByName(n);
        if (!p) return;
        try {
            Interceptor.attach(p, {
                onEnter: function () {
                    if (done || (Date.now() - T0) < 6000) return;
                    done = true;
                    try {
                        var obj = ptr(0x16249b0).readPointer();
                        send2('[' + t() + '] main-thread: obj=' + obj);
                        if (obj.isNull()) return;
                        var vt = obj.readPointer();
                        var fn = vt.add(0x94).readPointer();
                        send2('[' + t() + '] slot94=' + fn);
                        var f = new NativeFunction(fn, 'uint', ['pointer', 'int']);
                        var hr = f(obj, -1);
                        send2('[' + t() + '] Visible(-1) hr=0x' + (hr >>> 0).toString(16));
                    } catch (e) { send2('doit ERR ' + e); }
                }
            });
            send2('hooked ' + n);
        } catch (e) { send2('hook fail ' + n + ' ' + e); }
    });
}, 150);
send2('loaded');
