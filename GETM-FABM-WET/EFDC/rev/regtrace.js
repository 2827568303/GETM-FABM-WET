'use strict';
function send2(s) { send(s); }
function wstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return '<bad>'; } }
function astr(p) { try { return p.isNull() ? '' : p.readAnsiString(); } catch (e) { return '<bad>'; } }
function hkeyName(h) {
    var v = h.toInt32() >>> 0;
    if (v === 0x80000000) return 'HKCR';
    if (v === 0x80000001) return 'HKCU';
    if (v === 0x80000002) return 'HKLM';
    if (v === 0x80000003) return 'HKU';
    return 'H:' + v.toString(16);
}

setTimeout(function () {
    try {
        var adv = Process.findModuleByName('advapi32.dll') || Module.load('advapi32.dll');
        ['RegOpenKeyExW', 'RegOpenKeyW', 'RegOpenKeyExA', 'RegOpenKeyA'].forEach(function (fn) {
            var p = adv.findExportByName(fn);
            if (!p) return;
            var wide = /W$/.test(fn);
            Interceptor.attach(p, {
                onEnter: function (a) {
                    send2('REG ' + fn + ' ' + hkeyName(a[0]) + '\\' + (wide ? wstr(a[1]) : astr(a[1])));
                }
            });
        });
        ['RegQueryValueExW', 'RegQueryValueExA'].forEach(function (fn) {
            var p = adv.findExportByName(fn);
            if (!p) return;
            var wide = /W$/.test(fn);
            Interceptor.attach(p, {
                onEnter: function (a) { send2('REGQ ' + fn + ' ' + (wide ? wstr(a[1]) : astr(a[1]))); }
            });
        });
        send2('--- loading OCX now ---');
        var h = Module.load('C:\\EFDC84_LIC\\mscomctl.ocx');
        send2('--- loaded ---');
        var dgco = new NativeFunction(h.findExportByName('DllGetClassObject'), 'uint', ['pointer', 'pointer', 'pointer']);
        function guid(s) {
            var m = s.replace(/[{}]/g, '').split('-'); var b = new Uint8Array(16);
            var d1 = parseInt(m[0], 16), d2 = parseInt(m[1], 16), d3 = parseInt(m[2], 16);
            b[0] = d1 & 255; b[1] = (d1 >> 8) & 255; b[2] = (d1 >> 16) & 255; b[3] = (d1 >>> 24) & 255;
            b[4] = d2 & 255; b[5] = (d2 >> 8) & 255; b[6] = d3 & 255; b[7] = (d3 >> 8) & 255;
            for (var i = 0; i < 4; i++) b[8 + i] = parseInt(m[3].substr(i * 2, 2), 16);
            for (var i = 0; i < 8; i++) b[12 + i] = parseInt(m[4].substr(i * 2, 2), 16);
            return b;
        }
        var c = Memory.alloc(16); c.writeByteArray(guid('{2C247F23-8591-11D1-B16A-00C0F0283628}'));
        var iid = Memory.alloc(16); iid.writeByteArray(guid('{00000001-0000-0000-C000-000000000046}'));
        var pp = Memory.alloc(4);
        send2('--- calling DllGetClassObject ---');
        var hr = dgco(c, iid, pp);
        send2('RESULT hr=0x' + (hr >>> 0).toString(16) + ' cf=' + pp.readPointer());
    } catch (e) { send2('ERR ' + e); }
}, 600);
send2('loaded');
