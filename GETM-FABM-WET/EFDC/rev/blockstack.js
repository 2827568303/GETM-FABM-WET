'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function sym(a) {
    try { var m = Process.findModuleByAddress(a); if (m) return m.name + '+0x' + a.sub(m.base).toString(16); } catch (e) { }
    return a.toString();
}
var reported = {};

setTimeout(function () {
    var mods = [['ntdll.dll', ['NtWaitForSingleObject', 'NtUserWaitMessage', 'NtUserGetMessage', 'NtUserPeekMessage', 'NtDelayExecution']],
    ['user32.dll', ['MsgWaitForMultipleObjects', 'MsgWaitForMultipleObjectsEx', 'WaitMessage', 'GetMessageW', 'GetMessageA']],
    ['kernel32.dll', ['WaitForSingleObject', 'WaitForSingleObjectEx', 'Sleep']]];
    mods.forEach(function (pair) {
        var m = Process.findModuleByName(pair[0]);
        if (!m) return;
        pair[1].forEach(function (fn) {
            var p = m.findExportByName(fn);
            if (!p) return;
            try {
                Interceptor.attach(p, {
                    onEnter: function () {
                        if ((Date.now() - T0) < 4000) return;
                        var key = fn;
                        if (reported[key]) return;
                        reported[key] = 1;
                        var bt = Thread.backtrace(this.context, Backtracer.FUZZY).map(sym).join(' <- ');
                        send2('[' + t() + '] BLOCKED in ' + fn + ' : ' + bt);
                    }
                });
            } catch (e) { }
        });
    });
    send2('hooks ready');
}, 150);
send2('loaded');
