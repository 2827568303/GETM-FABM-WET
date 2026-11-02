'use strict';
function send2(s) { send(s); }
var IID_IPictureDisp = [0x81, 0x09, 0xF8, 0x7B, 0x32, 0xBF, 0x1A, 0x10, 0x8B, 0xBB, 0x00, 0xAA, 0x00, 0x30, 0x0C, 0xAB];

setTimeout(function () {
    try {
        var oleaut = Process.findModuleByName('oleaut32.dll');
        var orig = oleaut.findExportByName('OleLoadPictureEx');
        var gdi = Process.findModuleByName('gdi32.dll');
        var CreateBitmap = new NativeFunction(gdi.findExportByName('CreateBitmap'), 'pointer',
            ['int', 'int', 'uint', 'uint', 'pointer']);
        var OleCreate = new NativeFunction(oleaut.findExportByName('OleCreatePictureIndirect'), 'uint',
            ['pointer', 'pointer', 'int', 'pointer']);
        var iidBuf = Memory.alloc(16);
        iidBuf.writeByteArray(new Uint8Array(IID_IPictureDisp));

        var shim = new NativeCallback(function (pStm, lSize, fRun, cx, cy, flags, ppv) {
            try {
                if (ppv.isNull()) return 0x80004003;
                var hbmp = CreateBitmap(2, 2, 1, 1, ptr(0));
                var desc = Memory.alloc(16);
                desc.writeU32(16);
                desc.add(4).writeU32(1);            // PICTYPE_BITMAP
                desc.add(8).writePointer(hbmp);
                desc.add(12).writePointer(ptr(0));
                var hr = OleCreate(desc, iidBuf, 1, ppv);
                send2('shim OleLoadPictureEx -> OleCreatePictureIndirect hr=0x' + (hr >>> 0).toString(16));
                return 0;
            } catch (e) { send2('shim ERR ' + e); return 0x80004005; }
        }, 'int', ['pointer', 'int', 'int', 'uint', 'uint', 'uint', 'pointer']);

        Interceptor.replace(orig, shim);
        send2('replaced OleLoadPictureEx at ' + orig);
    } catch (e) { send2('ERR ' + e); }
}, 200);
send2('loaded');
