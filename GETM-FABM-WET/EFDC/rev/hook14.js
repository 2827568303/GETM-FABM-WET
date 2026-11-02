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
    send2('hooked ' + modName + '!' + fn);
}
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
function astr(p) { try { return p.isNull() ? '' : p.readAnsiString(); } catch (e) { return '<bad>'; } }

hook('user32.dll', 'CreateWindowExW', function (args) {
    var cls = wstr(args[1]), name = wstr(args[2]);
    send2('[' + t() + '] CreateWindowExW cls=' + JSON.stringify(cls) + ' name=' + JSON.stringify(name) +
        ' style=0x' + args[3].toInt32().toString(16));
}, function (ret) { send2('[' + t() + ']   -> hwnd=' + ret); });

hook('user32.dll', 'CreateWindowExA', function (args) {
    var cls = astr(args[1]), name = astr(args[2]);
    send2('[' + t() + '] CreateWindowExA cls=' + JSON.stringify(cls) + ' name=' + JSON.stringify(name) +
        ' style=0x' + args[3].toInt32().toString(16));
}, function (ret) { send2('[' + t() + ']   -> hwnd=' + ret); });

hook('user32.dll', 'ShowWindow', function (args) {
    send2('[' + t() + '] ShowWindow hwnd=' + args[0] + ' cmd=' + args[1].toInt32());
}, null);

hook('oleaut32.dll', 'OleLoadPictureEx', function (args) {
    send2('[' + t() + '] OleLoadPictureEx size=' + args[1].toInt32());
}, function (ret) { send2('[' + t() + ']   -> hr=0x' + (ret.toInt32() >>> 0).toString(16)); });

send2('script loaded');
