'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '?'; } }
function astr(p) { try { return p.isNull() ? '' : p.readAnsiString(); } catch (e) { return '?'; } }
function hookExp(mod, fn, cb) {
    var m = Process.findModuleByName(mod);
    if (!m) { send2('!! no ' + mod); return; }
    var p = m.findExportByName(fn);
    if (!p) { send2('!! no ' + fn); return; }
    try { Interceptor.attach(p, cb); send2('hooked ' + mod + '!' + fn); } catch (e) { send2('fail ' + fn + ' ' + e); }
}
setTimeout(function () {
    hookExp('winhttp.dll', 'WinHttpOpenRequest', {
        onEnter: function (a) {
            send2('[' + t() + '] WinHttpOpenRequest verb=' + JSON.stringify(wstr(a[1])) + ' path=' + JSON.stringify(wstr(a[2])));
        }, onLeave: function (r) { send2('[' + t() + ']  -> req=' + r); }
    });
    hookExp('winhttp.dll', 'WinHttpConnect', {
        onEnter: function (a) { send2('[' + t() + '] WinHttpConnect host=' + JSON.stringify(wstr(a[1])) + ' port=' + a[2].toInt32()); }
    });
    hookExp('winhttp.dll', 'WinHttpSendRequest', { onEnter: function () { send2('[' + t() + '] WinHttpSendRequest'); } });
    hookExp('winhttp.dll', 'WinHttpReceiveResponse', { onEnter: function () { send2('[' + t() + '] WinHttpReceiveResponse'); } });
    ['InternetOpenUrlA', 'InternetOpenUrlW', 'HttpOpenRequestA', 'HttpOpenRequestW', 'InternetConnectA', 'InternetConnectW'].forEach(function (fn) {
        hookExp('wininet.dll', fn, {
            onEnter: function (a) {
                var s = /W$/.test(fn) ? wstr(a[1]) : astr(a[1]);
                send2('[' + t() + '] ' + fn + ' ' + JSON.stringify(s));
            }
        });
    });
    send2('--- hooks ready ---');
}, 150);
send2('loaded');
