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
    send2('hooked ' + modName + '!' + fn + ' @ ' + a);
}
var ole32 = Process.findModuleByName('ole32.dll');
var CreateStreamOnHGlobal = new NativeFunction(ole32.findExportByName('CreateStreamOnHGlobal'), 'uint', ['pointer', 'int', 'pointer']);
var oleaut = Process.findModuleByName('oleaut32.dll');
var OleLoadPictureEx = new NativeFunction(oleaut.findExportByName('OleLoadPictureEx'), 'uint',
    ['pointer', 'int', 'int', 'pointer', 'int', 'int', 'int', 'pointer']);

function vts(p) { return p.readPointer(); }
function mkRead(p) { return new NativeFunction(vts(p).add(3 * 4).readPointer(), 'uint', ['pointer', 'pointer', 'uint', 'pointer']); }
function mkWrite(p) { return new NativeFunction(vts(p).add(4 * 4).readPointer(), 'uint', ['pointer', 'pointer', 'uint', 'pointer']); }
function mkSeek(p) { return new NativeFunction(vts(p).add(5 * 4).readPointer(), 'uint', ['pointer', 'int64', 'uint', 'pointer']); }
function mkStat(p) { return new NativeFunction(vts(p).add(12 * 4).readPointer(), 'uint', ['pointer', 'pointer', 'int']); }

hook('oleaut32.dll', 'OleLoadPictureEx', function (args) {
    var pStm = args[0], size = args[1].toInt32();
    var info = '[' + t() + '] OLEEX in stm=' + pStm + ' size=' + size;
    try {
        var Seek = mkSeek(pStm);
        var pos = Memory.alloc(8);
        Seek(pStm, 0, 1, pos);
        info += ' pos=' + pos.readS64();
        Seek(pStm, 0, 0, pos);
        // Stat
        var st = Memory.alloc(80);
        var hr = mkStat(pStm)(pStm, st, 1);   // STATFLAG_NONAME
        info += ' statHr=0x' + (hr >>> 0).toString(16) + ' type=' + st.add(4).readU32() +
            ' cbSize=' + st.add(8).readS64();
        // copy data into a fresh stream and nested-call
        var buf = Memory.alloc(size + 16);
        var nread = Memory.alloc(4);
        mkRead(pStm)(pStm, buf, size, nread);
        Seek(pStm, 0, 0, pos);
        var pNew = Memory.alloc(4);
        var hr2 = CreateStreamOnHGlobal(ptr(0), 1, pNew);
        var stm2 = pNew.readPointer();
        var nw = Memory.alloc(4);
        mkWrite(stm2)(stm2, buf, nread.readU32(), nw);
        mkSeek(stm2)(stm2, 0, 0, pos);
        var ppv = Memory.alloc(4);
        var hr3 = OleLoadPictureEx(stm2, nread.readU32(), 0, args[3], 0, 0, 0, ppv);
        info += ' nread=' + nread.readU32() + ' freshRet=0x' + (hr3 >>> 0).toString(16) + ' pic=' + ppv.readPointer();
    } catch (e) { info += ' err=' + e; }
    send2(info);
}, function (ret) {
    send2('[' + t() + ']   -> OLEEX ret=0x' + (ret.toInt32() >>> 0).toString(16));
});

send2('script loaded');
