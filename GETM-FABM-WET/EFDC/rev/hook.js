'use strict';
function mod(addr) {
    try {
        var m = Process.findModuleByAddress(addr);
        if (m) return m.name + '+0x' + addr.sub(m.base).toString(16);
    } catch (e) { }
    return String(addr);
}
function log(s) { send(s); }

function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { log('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { log('!! export missing ' + modName + '!' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    log('hooked ' + modName + '!' + fn + ' @ ' + a);
}

var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(3); }

function safeStr(ptr, wide) {
    try {
        if (ptr.isNull()) return '<null>';
        if (wide) return ptr.readUtf16String();
        return ptr.readAnsiString();
    } catch (e) { return '<bad>'; }
}

hook('kernel32.dll', 'CreateFileW', function (args) {
    var p = safeStr(args[0], true);
    if (/\.(bmp|ico|jpg|jpeg|png|gif|emf|wmf|lic|ini|mdb|xml|dat)$/i.test(p) || /DSI|EEMS|EFDC/i.test(p)) {
        log('[' + t() + '] CreateFileW ' + JSON.stringify(p) + ' from ' + mod(this.returnAddress));
    }
}, null);

hook('kernel32.dll', 'CreateFileA', function (args) {
    var p = safeStr(args[0], false);
    if (/\.(bmp|ico|jpg|jpeg|png|gif|emf|wmf|lic|ini|mdb|xml|dat)$/i.test(p) || /DSI|EEMS|EFDC/i.test(p)) {
        log('[' + t() + '] CreateFileA ' + JSON.stringify(p) + ' from ' + mod(this.returnAddress));
    }
}, null);

['OleLoadPicture', 'OleLoadPicturePath', 'OleLoadPictureFile', 'OleLoadPictureEx'].forEach(function (fn) {
    hook('oleaut32.dll', fn, function (args) {
        var extra = '';
        if (fn === 'OleLoadPicturePath') extra = ' path=' + JSON.stringify(safeStr(args[0], true));
        log('[' + t() + '] ' + fn + extra + ' from ' + mod(this.returnAddress));
    }, null);
});

hook('msvbvm60.dll', '__vbaHresultCheckObj', function (args) {
    var hr = args[0].toInt32();
    if (hr < 0) {
        log('[' + t() + '] HresultCheckObj hr=0x' + (hr >>> 0).toString(16) + ' from ' + mod(this.returnAddress) +
            ' src=' + mod(args[2]) + ' off=0x' + args[3].toInt32().toString(16));
    }
}, null);

hook('msvbvm60.dll', 'rtcMsgBox', function (args) {
    log('[' + t() + '] rtcMsgBox text=' + JSON.stringify(safeStr(args[0], true)) + ' title=' + JSON.stringify(safeStr(args[2], true)) + ' from ' + mod(this.returnAddress));
}, null);

hook('user32.dll', 'MessageBoxIndirectA', function (args) {
    log('[' + t() + '] MessageBoxIndirectA from ' + mod(this.returnAddress));
}, null);

log('script loaded');
