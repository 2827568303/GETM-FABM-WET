'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function mod(a) { try { var m = Process.findModuleByAddress(a); if (m) return m.name + '+0x' + a.sub(m.base).toString(16); } catch (e) { } return String(a); }
function astr(p) { try { return p.isNull() ? '' : p.readAnsiString(); } catch (e) { return '?'; } }
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '?'; } }
function hookExp(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! missing ' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
}
setTimeout(function () {
    try {
        hookExp('user32.dll', 'CreateWindowExA', function (a) {
            var cls = astr(a[1]);
            if (/ThunderRT6Form|ThunderRT6MDI/.test(cls)) send2('[' + t() + '] FormWindow cls=' + cls + ' name=' + JSON.stringify(astr(a[2])));
        }, null);
        hookExp('user32.dll', 'CreateWindowExW', function (a) {
            var cls = wstr(a[1]);
            if (/ThunderRT6Form|ThunderRT6MDI/.test(cls)) send2('[' + t() + '] FormWindowW cls=' + cls + ' name=' + JSON.stringify(wstr(a[2])));
        }, null);
        var mb = Process.findModuleByName('msvbvm60.dll');
        if (mb) {
            var n2 = mb.findExportByName('__vbaNew2');
            if (n2) Interceptor.attach(n2, {
                onEnter: function (a) { send2('[' + t() + '] New2 info=' + a[0] + ' from=' + mod(this.returnAddress)); },
                onLeave: function (r) { }
            });
            var nw = mb.findExportByName('__vbaNew');
            if (nw) Interceptor.attach(nw, {
                onEnter: function (a) { send2('[' + t() + '] New info=' + a[0] + ' from=' + mod(this.returnAddress)); }
            });
        }
        send2('hooked windows/New');
    } catch (e) { send2('ERR ' + e); }
}, 200);
send2('loaded');
