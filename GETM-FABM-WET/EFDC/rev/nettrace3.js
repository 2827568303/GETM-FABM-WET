'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
var done = {};
function tryHook(mod, fn, cb) {
    var key = mod + '!' + fn;
    if (done[key]) return;
    var m = Process.findModuleByName(mod);
    if (!m) return;
    var p = m.findExportByName(fn);
    if (!p) return;
    try { Interceptor.attach(p, cb); done[key] = 1; send2('hooked ' + key); } catch (e) { done[key] = 1; }
}
var iv = setInterval(function () {
    tryHook('winhttp.dll', 'WinHttpReadData', {
        onEnter: function (a) { this.buf = a[1]; this.n = a[2].toInt32(); },
        onLeave: function (r) {
            var got = 0;
            try { got = this.buf.add(0).readU32(); } catch (e) { }
            var cnt = 0;
            try { cnt = ptr(this.buf).readU32(); } catch (e) { }
            var s = '';
            try { s = this.buf.readAnsiString(); } catch (e) { s = '<unreadable>'; }
            send2('[' + t() + '] WinHttpReadData want=' + this.n + ' -> hr=' + r + ' data=' + JSON.stringify(s));
        }
    });
    tryHook('winhttp.dll', 'WinHttpQueryHeaders', {
        onEnter: function (a) { this.buf = a[3]; this.lenp = a[4]; },
        onLeave: function (r) {
            var s = '';
            try { s = this.buf.readUtf16String(); } catch (e) { try { s = this.buf.readAnsiString(); } catch (e2) { s = '?'; } }
            send2('[' + t() + '] WinHttpQueryHeaders -> hr=' + r + ' val=' + JSON.stringify(s));
        }
    });
    tryHook('winhttp.dll', 'WinHttpQueryDataAvailable', {
        onEnter: function (a) { this.p = a[1]; },
        onLeave: function (r) { var n = 0; try { n = this.p.readU32(); } catch (e) { } send2('[' + t() + '] WinHttpQueryDataAvailable hr=' + r + ' n=' + n); }
    });
}, 200);
setTimeout(function () { clearInterval(iv); }, 14000);
send2('loaded');
