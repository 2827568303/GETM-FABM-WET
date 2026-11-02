'use strict';
function send2(s) { send(s); }
setTimeout(function () {
    try {
        var advapi = Process.findModuleByName('advapi32.dll');
        if (!advapi) advapi = Module.load('advapi32.dll');
        var RegOpenKeyExW = new NativeFunction(advapi.findExportByName('RegOpenKeyExW'), 'uint', ['pointer', 'pointer', 'uint', 'uint', 'pointer']);
        var RegOverridePredefKey = new NativeFunction(advapi.findExportByName('RegOverridePredefKey'), 'uint', ['pointer', 'pointer']);
        var RegCloseKey = new NativeFunction(advapi.findExportByName('RegCloseKey'), 'uint', ['pointer']);
        var HKCU = ptr(0x80000001);
        var HKCR = ptr(0x80000000);
        var sub = Memory.alloc(128); sub.writeUtf16String('Software\\Classes');
        var phk = Memory.alloc(4);
        var hr = RegOpenKeyExW(HKCU, sub, 0, 0x000F003F, phk);
        send2('RegOpenKeyExW HKCU\\Software\\Classes hr=0x' + (hr >>> 0).toString(16) + ' key=' + phk.readPointer());
        var hkey = phk.readPointer();
        var hr2 = RegOverridePredefKey(HKCR, hkey);
        send2('RegOverridePredefKey(HKCR->HKCU\\Software\\Classes) hr=0x' + (hr2 >>> 0).toString(16));

        var files = [
            'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\mscomctl.ocx',
            'C:\\Users\\23801\\Desktop\\GETM-FABM-WET-260928\\GETM-FABM-WET\\EFDC\\EFDC 商业版8.4\\comctl32.ocx'
        ];
        files.forEach(function (f) {
            try {
                var h = Module.load(f);
                var reg = new NativeFunction(h.findExportByName('DllRegisterServer'), 'uint', []);
                var r = reg();
                send2('DllRegisterServer ' + f.split('\\').pop() + ' -> 0x' + (r >>> 0).toString(16));
            } catch (e) { send2('load/reg FAIL ' + f + ' : ' + e); }
        });

        var hr3 = RegOverridePredefKey(HKCR, ptr(0));
        send2('restore override hr=0x' + (hr3 >>> 0).toString(16));
        RegCloseKey(hkey);
    } catch (e) { send2('ERR ' + e); }
}, 600);
send2('loaded');
