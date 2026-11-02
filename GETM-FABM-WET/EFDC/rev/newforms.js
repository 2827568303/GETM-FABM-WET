'use strict';
function send2(s) { send(s); }
var exeBase = null;
var FORMV = null;

setTimeout(function () {
    try {
        var m = Process.findModuleByName('EFDC_Explorer8.4.exe');
        exeBase = m.base;
        FORMV = exeBase.add(0x123C1F4);
        send2('exe base=' + exeBase + ' formVtable=' + FORMV);
        var mb = Process.findModuleByName('MSVBVM60.DLL');
        Interceptor.attach(mb.findExportByName('__vbaNew2'), {
            onEnter: function (a) { this.info = a[0]; this.out = a[1]; },
            onLeave: function (r) {
                try {
                    var hr = r.toInt32() >>> 0;
                    var obj = this.out.readPointer();
                    if (obj.isNull()) { send2('New2 info=' + this.info + ' -> null hr=0x' + hr.toString(16)); return; }
                    var vt = obj.readPointer();
                    var isForm = vt.equals(FORMV);
                    send2('New2 info=' + this.info + ' obj=' + obj + ' vt=' + vt + (isForm ? '  *** FORM ***' : ''));
                } catch (e) { send2('New2 hook err ' + e); }
            }
        });
        send2('hooked New2');
    } catch (e) { send2('ERR ' + e); }
}, 200);
send2('loaded');
