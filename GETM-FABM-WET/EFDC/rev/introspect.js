'use strict';
function emit(s) { send(s); }
function rstr(p) { try { return p.isNull() ? '' : p.readUtf16String(); } catch (e) { return ''; } }
var IID_IDispatch = [0x00, 0x04, 0x02, 0x00, 0, 0, 0, 0, 0xC0, 0, 0, 0, 0, 0, 0, 0x46];
var IID_IPictureDisp = [0x81, 0x09, 0xF8, 0x7B, 0x32, 0xBF, 0x1A, 0x10, 0x8B, 0xBB, 0x00, 0xAA, 0x00, 0x30, 0x0C, 0xAB];
var done = false;

setTimeout(function () {
    try {
        var oa = Process.findModuleByName('oleaut32.dll');
        var gdi = Process.findModuleByName('gdi32.dll');
        var CreateBitmap = new NativeFunction(gdi.findExportByName('CreateBitmap'), 'pointer', ['int', 'int', 'uint', 'uint', 'pointer']);
        var OleCreate = new NativeFunction(oa.findExportByName('OleCreatePictureIndirect'), 'uint', ['pointer', 'pointer', 'int', 'pointer']);
        var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IPictureDisp));
        Interceptor.attach(oa.findExportByName('OleLoadPictureEx'), {
            onEnter: function (a) { this.ppv = a[7]; },
            onLeave: function (r) {
                if ((r.toInt32() >>> 0) === 0) return;
                try {
                    var hbmp = CreateBitmap(2, 2, 1, 1, ptr(0));
                    var desc = Memory.alloc(16); desc.writeU32(16); desc.add(4).writeU32(1); desc.add(8).writePointer(hbmp); desc.add(12).writePointer(ptr(0));
                    if ((OleCreate(desc, iid, 1, this.ppv) >>> 0) === 0) r.replace(ptr(0));
                } catch (e) { }
            }
        });
    } catch (e) { }

    // hook the 0x2B0 call site: on main thread, introspect the form object
    try {
        Interceptor.attach(ptr(0x156AE23), {
            onEnter: function () {
                if (done) return;
                done = true;
                try {
                    var obj = this.context.esi;
                    emit('form obj = ' + obj);
                    var vt = obj.readPointer();
                    var QI = new NativeFunction(vt.readPointer(), 'uint', ['pointer', 'pointer', 'pointer']);
                    var iid = Memory.alloc(16); iid.writeByteArray(new Uint8Array(IID_IDispatch));
                    var pp = Memory.alloc(4);
                    var hr = QI(obj, iid, pp);
                    emit('QI(IDispatch) hr=0x' + (hr >>> 0).toString(16));
                    if ((hr >>> 0) !== 0) return;
                    var disp = pp.readPointer();
                    var dvt = disp.readPointer();
                    var GetTypeInfo = new NativeFunction(dvt.add(16).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
                    var ti = Memory.alloc(4);
                    var h2 = GetTypeInfo(disp, 0, ti);
                    emit('GetTypeInfo hr=0x' + (h2 >>> 0).toString(16));
                    if ((h2 >>> 0) !== 0) return;
                    var info = ti.readPointer();
                    var ivt = info.readPointer();
                    var GetTypeAttr = new NativeFunction(ivt.add(12).readPointer(), 'uint', ['pointer', 'pointer']);
                    var GetFuncDesc = new NativeFunction(ivt.add(20).readPointer(), 'uint', ['pointer', 'uint', 'pointer']);
                    var GetDoc = new NativeFunction(ivt.add(44).readPointer(), 'uint', ['pointer', 'int', 'pointer', 'pointer', 'pointer', 'pointer']);
                    var pa = Memory.alloc(4);
                    if ((GetTypeAttr(info, pa) >>> 0) !== 0) { emit('GetTypeAttr fail'); return; }
                    var attr = pa.readPointer();
                    var cFuncs = attr.add(0x30).readU32();
                    emit('cFuncs = ' + cFuncs);
                    var lines = [];
                    for (var i = 0; i < cFuncs; i++) {
                        var fd = Memory.alloc(4);
                        if ((GetFuncDesc(info, i, fd) >>> 0) !== 0) continue;
                        var f = fd.readPointer();
                        var memid = f.readInt32();
                        var nm = Memory.alloc(4), doc = Memory.alloc(4), hf = Memory.alloc(4), cx = Memory.alloc(4);
                        var name = '';
                        if ((GetDoc(info, memid, nm, doc, hf, cx) >>> 0) === 0) name = rstr(nm.readPointer());
                        lines.push(i + ':' + memid + ':' + name);
                    }
                    emit('FUNCS ' + lines.join(' | '));
                } catch (e) { emit('introspect ERR ' + e); }
            }
        });
        emit('hooked 0x156AE23');
    } catch (e) { emit('hook ERR ' + e); }
}, 200);
emit('loaded');
