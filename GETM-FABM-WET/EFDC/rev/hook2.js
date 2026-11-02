'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function mod(addr) {
    try {
        var m = Process.findModuleByAddress(addr);
        if (m) return m.name + '+0x' + addr.sub(m.base).toString(16);
    } catch (e) { }
    return String(addr);
}
function bt(ctx, n) {
    try {
        return Thread.backtrace(ctx, Backtracer.ACCURATE).slice(0, n || 6).map(mod).join(' <- ');
    } catch (e) { return '<bt err>'; }
}
function send2(s) { send(s); }
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}
function wstr(p) { try { return p.isNull() ? '<null>' : p.readUtf16String(); } catch (e) { return '<bad>'; } }

hook('kernel32.dll', 'CreateFileW', function (args) {
    var p = wstr(args[0]);
    if (/ee_activation\.log/i.test(p)) return;
    if (/\.(bmp|ico|jpg|jpeg|png|gif|emf|wmf|lic|ini|mdb|xml)$/i.test(p) || /DSI|EEMS|EFDC/i.test(p))
        send2('[' + t() + '] CreateFileW ' + JSON.stringify(p));
}, null);

['OleLoadPicture', 'OleLoadPicturePath', 'OleLoadPictureFile', 'OleLoadPictureEx'].forEach(function (fn) {
    hook('oleaut32.dll', fn, function (args) {
        var extra = fn === 'OleLoadPicturePath' ? ' path=' + JSON.stringify(wstr(args[0])) : '';
        send2('[' + t() + '] ' + fn + extra + ' bt=' + bt(this.context, 6));
    }, function (ret) { send2('[' + t() + ']   -> ' + fn + ' ret=0x' + (ret.toInt32() >>> 0).toString(16)); });
});

hook('msvbvm60.dll', '__vbaHresultCheckObj', function (args) {
    var hr = args[0].toInt32();
    if (hr < 0) send2('[' + t() + '] HRFAIL hr=0x' + (hr >>> 0).toString(16) + ' off=0x' + args[3].toInt32().toString(16) +
        ' bt=' + bt(this.context, 5));
}, null);

hook('msvbvm60.dll', '__vbaError', function (args) {
    send2('[' + t() + '] __vbaError args=' + args.slice(0, 4).map(function (a) { return '0x' + a.toString(16); }).join(',') +
        ' bt=' + bt(this.context, 5));
}, null);

hook('msvbvm60.dll', 'rtcMsgBox', function (args) {
    send2('[' + t() + '] rtcMsgBox text=' + JSON.stringify(wstr(args[0])) + ' title=' + JSON.stringify(wstr(args[2])) + ' bt=' + bt(this.context, 5));
}, null);

send2('script loaded');
