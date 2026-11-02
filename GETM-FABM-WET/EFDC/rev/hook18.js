'use strict';
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
function send2(s) { send(s); }
function hook(modName, fn, onEnter, onLeave) {
    var m = Process.findModuleByName(modName);
    if (!m) { send2('!! module missing ' + modName); return; }
    var a = m.findExportByName(fn);
    if (!a) { send2('!! export missing ' + fn); return; }
    Interceptor.attach(a, { onEnter: onEnter, onLeave: onLeave });
    send2('hooked ' + modName + '!' + fn);
}

send2('modules with gdi: ' + Process.enumerateModules().filter(function (m) { return /gdi/i.test(m.name); }).map(function (m) { return m.name + '@' + m.base; }).join(','));

['GdipLoadImageFromStream', 'GdipCreateBitmapFromStream', 'GdipCreateBitmapFromStreamICM', 'GdipCreateBitmapFromScan0',
 'GdipCreateBitmapFromFile', 'GdipStartup', 'GdiplusStartup'].forEach(function (fn) {
    var m = Process.findModuleByName('gdiplus.dll');
    if (!m) return;
    if (!m.findExportByName(fn)) { send2('no export ' + fn); return; }
    hook('gdiplus.dll', fn, function (args) { send2('[' + t() + '] gdiplus!' + fn); },
        function (ret) { send2('[' + t() + ']   -> ' + fn + ' ret=0x' + (ret.toInt32() >>> 0).toString(16)); });
});

try {
    var g = Process.findModuleByName('gdiplus.dll');
    if (g) {
        var GdiplusStartup = new NativeFunction(g.findExportByName('GdiplusStartup'), 'uint', ['pointer', 'pointer', 'pointer']);
        var tok = Memory.alloc(4);
        var inp = Memory.alloc(16); inp.writeU32(1); inp.add(4).writeU32(0); inp.add(8).writePointer(ptr(0)); inp.add(12).writeU32(0);
        var hr = GdiplusStartup(tok, inp, ptr(0));
        send2('[' + t() + '] self GdiplusStartup ret=0x' + (hr >>> 0).toString(16) + ' token=' + tok.readU32());
    } else send2('gdiplus not loaded');
} catch (e) { send2('startup err ' + e); }

send2('loaded');
