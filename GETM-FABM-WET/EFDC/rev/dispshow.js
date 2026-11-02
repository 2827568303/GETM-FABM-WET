'use strict';
function send2(s) { send(s); }
var T0 = Date.now();
function t() { return ((Date.now() - T0) / 1000).toFixed(2); }
var IID_IDispatch = [0x00, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46];

function invokeShow(obj, name) {
    try {
        var vt = obj.readPointer();
        var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
        var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
        var pp = Memory.alloc(4);
        if ((QI(obj, iid, pp) >>> 0) !== 0) { send2('QI(IDispatch) failed for ' + name); return; }
        var disp = pp.readPointer();
        var dvt = disp.readPointer();
        var GetIDsOfNames = new NativeFunction(dvt.add(20).readPointer(), 'uint',
            ['pointer', 'pointer', 'pointer', 'uint', 'uint', 'pointer']);
        var Invoke = new NativeFunction(dvt.add(24).readPointer(), 'uint',
            ['pointer', 'int', 'pointer', 'uint', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);

        var nameBuf = Memory.allocUtf16String('Show');
        var names = Memory.alloc(Process.pointerSize);
        names.writePointer(nameBuf);
        var dispid = Memory.alloc(4);
        var nilIid = Memory.alloc(16);
        var hr = GetIDsOfNames(disp, nilIid, names, 1, 0, dispid);
        send2(name + ': GetIDsOfNames("Show") hr=0x' + (hr >>> 0).toString(16) + ' dispid=' + dispid.readInt32());
        if ((hr >>> 0) !== 0) return;

        // DISPPARAMS: no args
        var params = Memory.alloc(24);
        params.writePointer(ptr(0)); // rgvarg
        params.add(8).writePointer(ptr(0)); // rgdispidNamedArgs
        params.add(16).writeInt32(0); // cArgs
        params.add(20).writeInt32(0); // cNamedArgs
        var res = Memory.alloc(16);
        var hr2 = Invoke(disp, dispid.readInt32(), nilIid, 1 /*METHOD*/, 1 /*PROPERTYGET? use 1*/, params, res, ptr(0), ptr(0));
        send2(name + ': Invoke(Show) hr=0x' + (hr2 >>> 0).toString(16));
    } catch (e) { send2(name + ' ERR ' + e); }
}

setTimeout(function () {
    try {
        var obj = ptr(0x16249b0).readPointer();
        send2('[' + t() + '] title form obj=' + obj);
        if (!obj.isNull()) invokeShow(obj, 'titleform');
    } catch (e) { send2('ERR ' + e); }
}, 6000);
send2('loaded');

